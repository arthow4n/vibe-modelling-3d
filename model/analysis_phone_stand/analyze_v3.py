"""Decision-specific full-size printed mechanism fixtures, mm/N/MPa."""
import argparse
import json
import math
from pathlib import Path
import cadquery as cq
import v3_components as d
from physical_analysis import (Material, Region, Support, Motion, SurfaceForce,
    MatingPart, FlexureQuestion, ContactQuestion, StructuralQuestion, ManufacturingAssumption, QuestionStudy)


def material():
    return Material('conditional_solid_PETG',800,.38,
        'Uncalibrated isotropic short-term PETG assumption; no fatigue, creep or layer-bond qualification',.015)


def release_question(mesh=.5):
    # Keep the actual working leaf. The stout root is replaced by its fixed
    # continuation at x=40, avoiding refinement of the unrelated pin bore.
    leaf=cq.Workplane('XY').newObject([d.return_leaf(1).val().copy()]).intersect(d.box(10,d.ROOT_Y+3,18,30,14,4))
    return FlexureQuestion(name='v3_return_leaf',part=leaf,material=material(),
        supports=(Support(Region.plane('x',40)),),
        motion=Motion((0,-d.RELEASE,0),region=Region.plane('x',10),name='press'),
        observations={'end':Region.plane('x',10)},mesh_size_mm=mesh,
        max_increment=.2,
        acceptance={'peak_motion_force_N.press':4},
        manufacturing=ManufacturingAssumption('Actual right working leaf XY flat, solid PETG, .4 nozzle/.2 layers. Stout continuation at x40 restrained and inner end guided; pin/root play and guide friction excluded. Two mirrored leaves double this force.'))


def guide_question(mesh=1.8):
    dog=cq.Workplane('XY').newObject([d.slider().val().copy()]).intersect(d.box(0,10,18,14,18,12))
    case=cq.Workplane('XY').newObject([d.base().val().copy()]).intersect(d.box(0,10,8,17,19,27))
    return ContactQuestion(name='v3_compliant_lock_guide',part=dog,material=material(),
        supports=(Support(Region.plane('y',28)),Support(Region.plane('x',0),(0,None,None),'symmetry')),
        forces=(SurfaceForce(Region((0,20,d.PIVOT_Z+d.LOCK_THICKNESS/2),
                                    (8,23,d.PIVOT_Z+d.LOCK_THICKNESS/2)),(0,0,15)),),
        mesh_size_mm=mesh,max_increment=.25,
        contact_region=Region((-14,14,20.5),(14,28,22.5)),
        mating_parts=(MatingPart('housing',case,material=material(),
            contact_region=Region((-14.5,14,20.5),(14.5,29,23.5)),
            supports=(Support(Region.plane('z',8)),Support(Region.plane('x',0),(0,None,None),'symmetry'))),),
        penalty_N_mm3=4000,penetration_limit_mm=.02,
        acceptance={'max_displacement_mm':.75},
        manufacturing=ManufacturingAssumption('Symmetric half of actual nose, rails and printed housing, both solid PETG. Housing foundation fixed; truncated rail ends fixed. Half of 30 N bounds the worst .3 kg phone plus 2 N normal tap torque at 18 mm radius. Excludes whole hinge, flank wear, desk friction and printed joint play.'))


def pocket_question(mesh=.65):
    strip=d.place_cradle(d.cradle(),60).intersect(d.box(-2,20,19,4,9,15))
    z=d.PIVOT_Z-(d.LOCK_THICKNESS+d.LOCK_GAP)/2
    return StructuralQuestion(name='v3_pocket_web',part=strip,material=material(),
        supports=(Support(Region.plane('y',29)),),
        forces=(SurfaceForce(Region((-2,20,z),(2,23.15,z)),(0,0,7.5)),),
        mesh_size_mm=mesh,max_increment=.25,
        acceptance={'max_displacement_mm':.3},
        manufacturing=ManufacturingAssumption('Actual central 4 mm strip of the indexed rotor at 60 degrees. Uniform 30 N full-width flank load gives 7.5 N here; continuation at Y29 fixed. Solid PETG; excludes nonuniform contact, full cradle, pin compliance and layer anisotropy.'))


def cradle_question(mesh=3):
    weight=d.PHONE_MASS*9.81
    t=math.radians(45)
    normal=weight*math.cos(t)+2
    upper=(weight*math.cos(t)*d.PHONE_HEIGHT/2+2*(d.PHONE_HEIGHT-10))/72
    lower=normal-upper
    forces=[]
    for x in (-37,37):
        forces.extend((
            SurfaceForce(Region((x-6,28,40),(x+6,28,55.5)),(0,-weight*math.sin(t)/2,0)),
            SurfaceForce(Region((x-5,94,40),(x+5,106,40)),(0,0,-upper/2)),
            SurfaceForce(Region((x-6,28,53.8),(x+6,35,53.8)),(0,0,-lower/2))))
    return StructuralQuestion(name='v3_cradle_service',part=d.cradle(),material=material(),
        supports=(Support(Region((-8,-4.15,-4.15),(8,4.15,4.15))),),forces=tuple(forces),
        mesh_size_mm=mesh,max_increment=.25,
        acceptance={'max_displacement_mm':1},
        manufacturing=ManufacturingAssumption('Full production cradle, .3 kg portrait phone at 45 degrees plus 2 N upper-screen press. Phone equilibrium distributes load to ledges, upper back pads and front lips. Pivot-bore neighbourhood fixed, excluding hinge play and rotor-pocket compliance. Side-down solid PETG; printed anisotropy uncalibrated.'))


if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('question',choices=('release','guide','pocket','cradle'))
    p.add_argument('directory',type=Path)
    p.add_argument('--mesh',type=float)
    p.add_argument('--study',action='store_true')
    a=p.parse_args()
    q={'release':release_question,'guide':guide_question,'pocket':pocket_question,'cradle':cradle_question}[a.question](**({'mesh':a.mesh} if a.mesh else {}))
    if a.study:
        metrics=(('question.peak_strain','question.peak_actuation_force_N') if a.question=='release' else
                 ('question.peak_strain','max_strain_by_part.housing','max_displacement_mm') if a.question=='guide' else
                 ('question.peak_strain','max_displacement_mm'))
        r=QuestionStudy(q,'Resolve the 1.5% provisional strain and 8 N two-leaf release / .75 mm guide-deflection screens',
            metrics,relative_tolerance=.2,mesh_levels=0 if a.question=='release' else 1,
            motion_levels=1 if a.question=='release' else 0,
            contact_levels=1 if a.question=='guide' else 0).run(a.directory)
    else:r=q.run(a.directory)
    print(json.dumps({'status':r.status,'errors':r.errors,'question':r.metrics.get('question')}))
