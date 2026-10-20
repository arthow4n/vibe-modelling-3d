"""Actual deformable joint, lateral roof drive with axial motion left free.

Quasi-static peel search for travel-bag knocks, not impact dynamics. Both walls
deform; no independent-snap force estimate is used to declare retention.
"""
from dataclasses import replace
from pathlib import Path
import sys

from physical_analysis import (ContactQuestion, MatingPart, Motion, Region,
                               Support, SurfaceForce, QuestionStudy)
from physical_analysis.evidence import retain_run
from closure_research_flex import MATERIAL
import short_lap_reinforced as design
from short_lap_design import sample
import m1_design as base

ROOT = Path(__file__).resolve().parent
OUT = ROOT/'notes/short_lap'


def question(axis, *, mesh, increment, penalty):
    if axis not in ('x', 'y'):
        raise ValueError(axis)
    parts = design.build(design.SELECTED_OVERLAP)
    d = parts['dimensions']
    patch = Region((-4, -4, d.length), (4, 4, d.length))
    displacement = (8., None, None) if axis == 'x' else (None, 8., None)
    plane = (None, 0., None) if axis == 'x' else (0., None, None)
    observations = {'roof': patch}
    for sign, label in ((-1, 'negative'), (1, 'positive')):
        lo, hi = sorted((sign*(d.width/2-d.wall-.01), sign*(d.width/2+.01)))
        observations['lip_'+label] = Region((lo,-5.3,d.latch_z-3.2),
                                           (hi,5.3,d.latch_z-1))
        observations['rim_'+label] = Region((lo,-5.3,d.seam), (hi,5.3,d.seam+.5))
    contact = Region((-d.width,-d.depth,d.seam-.01),
                     (d.width,d.depth,d.seam+d.lap+6))
    return ContactQuestion(name='short_lap_lateral_'+axis, part=parts['cap'],
        material=MATERIAL, supports=(Support(patch,plane,name='plane'),),
        motion=Motion(displacement,patch,name='lateral'),
        forces=(SurfaceForce(patch,(0.,0.,-.05)),),
        mating_parts=(MatingPart('body',sample(parts)['body'],material=MATERIAL,
            supports=(Support(Region.plane('z',d.seam-16)),),contact_region=contact),),
        contact_region=contact,penalty_N_mm3=penalty,penetration_limit_mm=.03,
        observations=observations,mesh_size_mm=mesh,max_increment=increment)


def solve(axis):
    name = 'lateral_'+axis
    native, compact = OUT/'native'/name, OUT/'flex'/name
    if native.exists() or compact.exists():
        raise ValueError('Existing evidence; do not overwrite')
    study = QuestionStudy(question(axis,mesh=2.5,increment=.02,penalty=20000.),
        decision='Search actual deformable joint for lateral peel with axial roof DOF free; inspect contact and both bites before interpreting force. No dynamic or physical rating.',
        metrics=('question.peak_actuation_force_N',),relative_tolerance=.10)
    result = study.run(native)
    if (native/'baseline'/'result.json').exists():
        retain_run(native/'baseline',compact/'baseline')
    compact.mkdir(parents=True,exist_ok=True)
    (compact/'study_result.json').write_text((native/'study_result.json').read_text())
    print(result.status,flush=True)


def symmetric_question(axis, *, mesh, increment, penalty):
    """Exact half-domain for the centered principal-plane fixture only.

    The cut plane has zero normal displacement on both shells. Force and loaded
    area are halved; drive displacement and full-force interpretation are not.
    This does not represent diagonal or asymmetric luggage contact.
    """
    q = question(axis,mesh=mesh,increment=increment,penalty=penalty)
    normal = 'y' if axis == 'x' else 'x'
    half = (base.box(0,50,210,120,100,140) if normal == 'y'
            else base.box(50,0,210,100,120,140))
    symmetry = Support(Region.plane(normal,0),
        (None,0.,None) if normal == 'y' else (0.,None,None),name='symmetry')
    body = replace(q.mating_parts[0],shape=q.mating_parts[0].shape.intersect(half),
                   supports=(*q.mating_parts[0].supports,symmetry))
    observations = {name:region for name,region in q.observations.items()
                    if normal != 'x' or not name.endswith('_negative')}
    return replace(q,name=q.name+'_half',part=q.part.intersect(half),
        supports=(symmetry,),mating_parts=(body,),
        observations=observations,
        forces=tuple(replace(f,force_N=tuple(v/2 for v in f.force_N)) for f in q.forces))


def solve_half(axis):
    name = 'lateral_half_'+axis
    native, compact = OUT/'native'/name, OUT/'flex'/name
    if native.exists() or compact.exists():
        raise ValueError('Existing evidence; do not overwrite')
    study = QuestionStudy(symmetric_question(axis,mesh=2.5,increment=.02,penalty=20000.),
        decision='Mirror-symmetric centered lateral fixture with free axial DOF. Both shells deform; double lateral reaction for full fixture. Inspect snap passage, not just peak force.',
        metrics=('question.peak_actuation_force_N',),relative_tolerance=.10)
    result = study.run(native)
    if (native/'baseline'/'result.json').exists():
        retain_run(native/'baseline',compact/'baseline')
    compact.mkdir(parents=True,exist_ok=True)
    (compact/'study_result.json').write_text((native/'study_result.json').read_text())
    print(result.status,flush=True)


def seated_question(axis, *, mesh, increment, penalty):
    q = symmetric_question(axis,mesh=mesh,increment=increment,penalty=penalty)
    return replace(q,name=q.name+'_seated',motion=replace(q.motion,
        progress=((0.,0.),(.1,0.),(1.,1.))))


def pickup_question(axis, *, mesh, increment, penalty):
    """Take up measured guide play before the elastic/contact ramp.

    Explicit initial cap placement, not altered manufactured geometry. Its tiny
    CAD-established flank interference must relax during the initial hold.
    """
    q = seated_question(axis,mesh=mesh,increment=increment,penalty=penalty)
    index = 0 if axis == 'x' else 1
    gap = design.build(design.SELECTED_OVERLAP)['dimensions'].clearance
    vector = tuple(gap if i == index else 0. for i in range(3))
    def region(original):
        def shifted(values):
            return tuple(v+vector[i] if v is not None else None for i,v in enumerate(values))
        return Region(shifted(original.lower),shifted(original.upper),original.tolerance_mm)
    return replace(q,name=q.name+'_pickup',part=q.part.translate(vector),
        motion=replace(q.motion,region=region(q.motion.region)),
        forces=tuple(replace(f,region=region(f.region)) for f in q.forces),
        observations={name:region(value) for name,value in q.observations.items()})


def solve_pickup(axis):
    name = 'lateral_pickup_'+axis
    native, compact = OUT/'native'/name, OUT/'flex'/name
    if native.exists() or compact.exists():
        raise ValueError('Existing evidence; do not overwrite')
    q = pickup_question(axis,mesh=2.5,increment=.02,penalty=20000.)
    study = QuestionStudy(q,
        decision='Explicit cap placement takes up nominal 0.1mm guide play, then initial hold resolves any flank preload. Axial DOF remains free. No impact or printed validation.',
        metrics=('question.peak_actuation_force_N',),relative_tolerance=.10)
    result = study.run(native)
    if (native/'baseline'/'result.json').exists():
        retain_run(native/'baseline',compact/'baseline')
    compact.mkdir(parents=True,exist_ok=True)
    (compact/'study_result.json').write_text((native/'study_result.json').read_text())
    print(result.status,flush=True)


def solve_seated(axis):
    name = 'lateral_seated_'+axis
    native, compact = OUT/'native'/name, OUT/'flex'/name
    if native.exists() or compact.exists():
        raise ValueError('Existing evidence; do not overwrite')
    source = OUT/'native'/('lateral_half_'+axis)/'baseline'
    # A valid, identity-guarded mesh may be reused after an interrupted solve;
    # no old displacement/contact prediction is replayed or called complete.
    for old in ('lateral_'+axis,'lateral_half_'+axis):
        raw, archive = OUT/'native'/old/'baseline', OUT/'flex'/old/'baseline'
        if (raw/'result.json').exists() and not archive.exists():
            retain_run(raw,archive)
    q = seated_question(axis,mesh=2.5,increment=.02,penalty=20000.)
    mesh_source = source if (source/'result.json').is_file() else None
    q.run(native/'baseline',mesh_from=mesh_source)
    study = QuestionStudy(q,
        decision='Establish seam seating before lateral drive; axial DOF stays free. Both shells deform. Inspect both bites and numerical quality before drawing a retention conclusion.',
        metrics=('question.peak_actuation_force_N',),relative_tolerance=.10)
    result = study.run(native,evidence={'baseline':native/'baseline'})
    retain_run(native/'baseline',compact/'baseline')
    (compact/'study_result.json').write_text((native/'study_result.json').read_text())
    print(result.status,flush=True)


def targeted_question(axis):
    q = seated_question(axis,mesh=2.5,increment=.1,penalty=20000.)
    drive = (2.,None,None) if axis == 'x' else (None,4.,None)
    return replace(q,name=q.name+'_targeted',motion=replace(q.motion,displacement_mm=drive))


def solve_targeted(axis):
    """Fresh shorter path; reuse X's finalized mesh, mesh Y afresh."""
    q = targeted_question(axis)
    native,compact = OUT/'native'/('lateral_targeted_v2_'+axis),OUT/'flex'/('lateral_targeted_v2_'+axis)
    if native.exists() or compact.exists():
        raise ValueError('Existing evidence; do not overwrite')
    source = OUT/'native'/('lateral_half_'+axis)/'baseline'
    # Abruptly orphaned seated jobs have frozen inputs but no finalized run
    # receipt. Do not manufacture one merely to bypass the mesh-reuse guard.
    answer = q.run(native/'baseline',mesh_from=source if (source/'result.json').exists() else None)
    if not (native/'baseline'/'case.json').exists():
        retain_run(native/'baseline',compact/'baseline')
        print(answer.status,answer.errors,flush=True)
        return
    study = QuestionStudy(q,
        decision='Shorter fresh principal-plane loading path after interrupted long solves. Mesh only reused. Provisional 10N comparison, not an impact rating. Inspect both capture and contact quality.',
        metrics=('question.peak_actuation_force_N',),relative_tolerance=.10)
    result = study.run(native,evidence={'baseline':native/'baseline'})
    retain_run(native/'baseline',compact/'baseline')
    (compact/'study_result.json').write_text((native/'study_result.json').read_text())
    print(result.status,flush=True)


if __name__ == '__main__':
    if len(sys.argv) == 3 and sys.argv[1] == 'solve':
        solve(sys.argv[2])
    elif len(sys.argv) == 3 and sys.argv[1] == 'solve-half':
        solve_half(sys.argv[2])
    elif len(sys.argv) == 3 and sys.argv[1] == 'solve-seated':
        solve_seated(sys.argv[2])
    elif len(sys.argv) == 3 and sys.argv[1] == 'solve-pickup':
        solve_pickup(sys.argv[2])
    elif len(sys.argv) == 3 and sys.argv[1] == 'solve-targeted':
        solve_targeted(sys.argv[2])
    else:
        raise SystemExit('Use solve, solve-half, solve-seated, solve-pickup or solve-targeted, followed by x|y')
