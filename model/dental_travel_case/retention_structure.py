"""Actual-CAD structural/contact retention experiments; mm, N, MPa.

Commands are experiments, not product verification. All fixtures and uncalibrated
material assumptions are retained by physical_analysis. No result is a print rating.
"""
import argparse
from pathlib import Path
from physical_analysis import AnalysisCase, Material, Region
from physical_analysis.evidence import retain_run
from m1_design import box
import m1_design

ROOT = Path(__file__).resolve().parent


def material(modulus):
    return Material('PETG effective isotropic hypothesis', modulus, .38,
                    'Uncalibrated sensitivity hypothesis; homogeneous load-bearing CAD, '
                    'not a measured infill/layer model; no calibrated strain acceptance', None)


def design_module(variant):
    if variant=='m1':
        return m1_design
    if variant=='m2b':
        import m2b_design
        return m2b_design
    if variant=='m3':
        import m3_design
        return m3_design
    if variant=='m2':
        import m2_design
        return m2_design
    raise ValueError(variant)


def eccentric_case(*, variant, modulus, mesh, load, receiving_land, mesh_min_size, mesh_curvature_points, root_stub):
    """Axial traction on actual lower hook face; no receiver or holding claim.

    Positive X at the negative-X hook is inward. Loading the original material
    face does not simulate contact migration; this isolates the eccentricity.
    """
    if variant=='m2':
        raise ValueError('Inclined M2A faces need a different load-face selection')
    module=design_module(variant)
    D=module.D
    case = AnalysisCase(variant+'_eccentric', nonlinear=True, max_increment=.05)
    shape=module.tongue(D)
    if receiving_land:
        # Preserve geometry while imprinting the true receiver edge on the
        # underside, so traction does not drift with a box-cut triangle selection.
        outside=box(-(D.width/2-D.receiver_wall)-10,0,D.hook_bottom,20,30,100)
        shape=shape.cut(outside).union(shape.intersect(outside),clean=False)
    case.add_part('catch', shape, material=material(modulus), mesh_size_mm=mesh,
                  mesh_min_size_mm=mesh_min_size,mesh_curvature_points=mesh_curvature_points)
    root=(Region((-50,-20,D.beam_root),(50,20,D.beam_root+1)) if root_stub
          else Region.plane('z',D.beam_root))
    case.fix('catch',root,name='root')
    inner = D.width/2-D.receiver_wall if receiving_land else D.beam_outer
    case.apply_force('catch', Region((-40, -D.hook_width/2-.01, D.hook_bottom),
                                    (-inner, D.hook_width/2+.01, D.hook_bottom)), force_N=(0, 0, load))
    case.observe('catch', Region((-40, -D.hook_width/2-.01, D.hook_bottom),
                                (-D.beam_outer, D.hook_width/2+.01, D.hook_bottom+.1)), name='shoulder')
    return case


def assembly_case(*, variant, modulus, mesh, travel, increment, eccentric, lateral, crop, penalty, mesh_min_size, mesh_curvature_points, grip_style, pickup=False):
    """Both actual shells deform; remote finger-sized grip drives the cap.

    Body butt/crop end is clamped. Only a 6x6 mm end-panel patch has prescribed
    axial travel. Two in-plane components on the same patch model a local hand
    grip; shell everywhere between grip and receiver remains deformable. This
    is a declared gripping condition, not a search over all free-body escapes.
    Lateral travel deliberately challenges rocking; eccentric patch challenges peel.
    """
    parts=design_module(variant).build()
    d = parts['dimensions']
    lower, upper = parts['body'], parts['cap']
    support_z, grip_z = 0., d.length
    if crop:
        from m1_design import box
        support_z, grip_z = d.beam_root-12, d.seam+d.lap+18
        # Keep the artificial cap cut beyond all selected mating surfaces,
        # including the longer M2B guide; M1 crop remains unchanged.
        lower = lower.intersect(box(0,0,(support_z+d.seam+d.lap)/2,100,80,d.seam+d.lap-support_z))
        upper = upper.intersect(box(0,0,(d.seam+grip_z)/2,100,80,grip_z-d.seam))
    initial_lift=d.axial_play if pickup else 0.
    if pickup:
        # CAD-established zero-work free play only; no imposed leaf deformation.
        upper=upper.translate((0,0,initial_lift))
        grip_z+=initial_lift
    case = AnalysisCase('retention_'+variant, nonlinear=True, max_increment=increment)
    for name, shape in (('body',lower),('cap',upper)):
        case.add_part(name, shape, material=material(modulus), mesh_size_mm=mesh,
                      mesh_min_size_mm=mesh_min_size,mesh_curvature_points=mesh_curvature_points)
    case.fix('body', Region.plane('z',support_z), name='body_grip')
    patch = Region((eccentric-3,-3,grip_z),(eccentric+3,3,grip_z))
    if crop:
        patch = Region((-10,-d.depth/2,grip_z),(10,-d.depth/2+d.wall,grip_z))
    if grip_style == 'side':
        patch=Region((eccentric-3,-d.depth/2,grip_z-8),
                     (eccentric+3,-d.depth/2,grip_z-2))
    elif grip_style != 'end':
        raise ValueError(grip_style)
    case.prescribe_motion('cap', patch, displacement_mm=(lateral,0,travel), name='cap_grip')
    case.contact('body',Region((-50,-40,d.seam-1),(50,40,d.seam+d.lap+.1)),
                 'cap',Region((-50,-40,d.seam),(50,40,d.seam+d.lap+12+initial_lift)),
                 penalty_N_mm3=penalty,penetration_limit_mm=.03,
                 discretization='surface_to_surface')
    for side, x in (('negative',-1),('positive',1)):
        lo, hi = sorted((x*(d.beam_outer-.1),x*(d.beam_outer+d.hook_projection+.1)))
        case.observe('body',Region((lo,-d.hook_width/2,d.hook_bottom-.5),
                                  (hi,d.hook_width/2,d.hook_bottom+.5)),name='hook_'+side)
        lo, hi = sorted((x*(d.width/2-d.receiver_wall-.1),x*(d.width/2+.9)))
        case.observe('cap',Region((lo,-d.hook_width/2-1,d.hook_bottom-1+initial_lift),
                                 (hi,d.hook_width/2+1,d.hook_bottom+.5+initial_lift)),name='receiver_'+side)
    for side,x in (('negative',-1),('positive',1)):
        lo,hi=sorted((x*(d.width/2-d.receiver_wall-.1),x*(d.width/2+.9)))
        case.observe('cap',Region((lo,-5,d.seam+initial_lift),(hi,5,d.seam+.5+initial_lift)),name='rim_'+side)
    for name,z in (('cap_rim',d.seam+initial_lift),('guide_top',d.seam+d.lap-.8)):
        case.observe('cap' if name=='cap_rim' else 'body',
                     Region((-50,-40,z-.2),(50,40,z+.2)),name=name)
    return case


def release_question(*, variant, modulus, mesh):
    from physical_analysis import FlexureQuestion,Support,Motion
    module=design_module(variant)
    d=module.D
    length=d.beam_tip-d.beam_root-1
    contact=d.press_z-d.beam_root-1
    press_travel=d.release*2*contact/(3*length-contact)
    return FlexureQuestion(name=variant+'_release',part=module.tongue(d),material=material(modulus),
        supports=(Support(Region((-50,-20,d.beam_root),(50,20,d.beam_root+1)),name='root'),),
        motion=Motion((press_travel,None,None),Region.plane('x',-d.beam_outer-1.2),name='press',
                      progress=((0,0),(.5,1),(1,0))),
        observations={'shoulder':Region((-40,-d.hook_width/2,d.hook_bottom),
                                        (-d.beam_outer,d.hook_width/2,d.hook_bottom+.1)),
                      'tip':Region.plane('z',d.beam_tip)},mesh_size_mm=mesh,max_increment=.025)


def press_force_question(*, variant, modulus, mesh, load):
    """Uniform radial pad traction permits pad rotation (conforming press).

    Contrast with the uniform-displacement flat-press fixture. Neither models
    skin or measures subjective comfort. Force controls the response; no desired
    release travel is forced into this calculation.
    """
    from physical_analysis import StructuralQuestion,Support,SurfaceForce
    module=design_module(variant)
    d=module.D
    front=Region((-d.beam_outer-1.2,-d.beam_width/2,d.press_z-1),
                 (-d.beam_outer-1.2,d.beam_width/2,d.press_z+1))
    return StructuralQuestion(name=variant+'_press_force',part=module.tongue(d),material=material(modulus),
        supports=(Support(Region((-50,-20,d.beam_root),(50,20,d.beam_root+1)),name='root'),),
        forces=(SurfaceForce(front,(load,0,0)),),
        observations={'shoulder':Region((-40,-d.hook_width/2,d.hook_bottom),
                                        (-d.beam_outer,d.hook_width/2,d.hook_bottom+.1)),
                      'tooth':Region((-40,-d.hook_width/2,d.hook_bottom-.1),
                                     (-d.beam_outer+.1,d.hook_width/2,d.beam_tip+.1)),
                      'pad':front,'tip':Region.plane('z',d.beam_tip)},
        mesh_size_mm=mesh,max_increment=.1)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('operation', choices=('eccentric','assembly','release','press_force'))
    p.add_argument('--modulus', type=float, required=True)
    p.add_argument('--mesh', type=float, required=True)
    p.add_argument('--mesh-min-size',type=float)
    p.add_argument('--mesh-curvature-points',type=int)
    p.add_argument('--load', type=float)
    p.add_argument('--receiving-land',action='store_true')
    p.add_argument('--root-stub',action='store_true')
    p.add_argument('--variant', choices=('m1','m2','m2b','m3'),required=True)
    p.add_argument('--travel', type=float)
    p.add_argument('--increment', type=float, default=.02)
    p.add_argument('--eccentric', type=float, default=0)
    p.add_argument('--lateral', type=float, default=0)
    p.add_argument('--crop', action='store_true')
    p.add_argument('--pickup', action='store_true',help='Start cap at nominal first shoulder contact; omit only zero-work axial play')
    p.add_argument('--grip-style',choices=('end','side'),default='end')
    p.add_argument('--penalty', type=float, default=20000)
    p.add_argument('--backend',choices=('calculix','febio'),default='calculix',help='Existing native backend; FEBio only for prescribed-motion assembly cases')
    p.add_argument('--febio-linear-solver',choices=('native','fgmres-ilut'),default='native')
    p.add_argument('--febio-restart',type=int)
    p.add_argument('--ilut-max-fill',type=int)
    p.add_argument('--febio-restart-plugin',type=Path)
    p.add_argument('--linear-solver',choices=('default','iterative_scaling','iterative_cholesky'),default='default')
    p.add_argument('--mesh-from',type=Path)
    p.add_argument('--destination', type=Path, required=True)
    a = p.parse_args()
    if a.backend=='febio' and a.operation!='assembly':
        p.error('FEBio is supported here only for prescribed-motion assembly studies')
    if a.operation in ('release','press_force') and (
            a.linear_solver!='default' or a.mesh_from is not None or
            a.mesh_min_size is not None or a.mesh_curvature_points is not None):
        p.error('Question-based release studies do not expose mesh reuse, curvature controls or linear-solver choice')
    if a.backend!='febio' and (a.febio_linear_solver!='native' or
            a.febio_restart is not None or a.ilut_max_fill is not None or a.febio_restart_plugin is not None):
        p.error('FEBio controls require --backend febio')
    if a.operation in ('release','press_force'):
        if a.operation=='release':
            question=release_question(variant=a.variant,modulus=a.modulus,mesh=a.mesh)
        else:
            if a.load is None:
                p.error('--load required for press_force')
            question=press_force_question(variant=a.variant,modulus=a.modulus,mesh=a.mesh,load=a.load)
        answer=question.run(a.destination.resolve(),numerical=True)
        retain_run(a.destination.resolve(),ROOT/'notes/retention'/a.destination.name)
        print(dict(status=answer.status,metrics=answer.metrics),flush=True)
        return
    if a.operation == 'eccentric':
        if a.load is None:
            p.error('--load required for eccentric')
        case = eccentric_case(variant=a.variant,modulus=a.modulus, mesh=a.mesh, load=a.load, receiving_land=a.receiving_land,root_stub=a.root_stub,
                               mesh_min_size=a.mesh_min_size,mesh_curvature_points=a.mesh_curvature_points)
    else:
        if a.variant is None or a.travel is None:
            p.error('--variant and --travel required for assembly')
        case = assembly_case(variant=a.variant,modulus=a.modulus,mesh=a.mesh,travel=a.travel,
                             increment=a.increment,eccentric=a.eccentric,lateral=a.lateral,
                             crop=a.crop,penalty=a.penalty,
                             mesh_min_size=a.mesh_min_size,mesh_curvature_points=a.mesh_curvature_points,grip_style=a.grip_style,pickup=a.pickup)
    run = a.destination.resolve()
    if a.backend=='febio':
        if a.operation!='assembly' or a.linear_solver!='default':
            p.error('FEBio comparison requires assembly and default linear-solver (native FEBio solver)')
        from physical_analysis.backends.febio import FebioBackend,FgmresILUT
        iterative=None
        if a.febio_linear_solver=='fgmres-ilut':
            if a.febio_restart is None or a.ilut_max_fill is None:
                p.error('FGMRES requires explicit --febio-restart and --ilut-max-fill')
            iterative=FgmresILUT(max_iterations=1000,restart_iterations=a.febio_restart,
                relative_tolerance=1e-8,absolute_tolerance=1e-12,
                max_fill=a.ilut_max_fill,fill_tolerance=1e-5,
                restart_correction_plugin=a.febio_restart_plugin)
        elif a.febio_restart is not None or a.ilut_max_fill is not None or a.febio_restart_plugin is not None:
            p.error('Iterative controls require --febio-linear-solver fgmres-ilut')
        backend=FebioBackend(two_pass=True,linear_solver=iterative)
    else:
        if a.febio_linear_solver!='native' or a.febio_restart is not None or a.ilut_max_fill is not None or a.febio_restart_plugin is not None:
            p.error('FEBio controls require --backend febio')
        from physical_analysis.backends.structural import CalculixBackend
        backend=CalculixBackend(linear_solver=a.linear_solver)
    answer = case.run(run,backend=backend,mesh_from=a.mesh_from)
    print(dict(status=answer.status, completed=answer.completed, metrics=answer.metrics, errors=answer.errors), flush=True)
    retain_run(run, ROOT/'notes/retention'/run.name)


if __name__ == '__main__':
    main()
