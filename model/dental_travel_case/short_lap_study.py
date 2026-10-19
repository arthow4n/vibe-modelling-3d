"""New wall-compliance evidence for 18/24/30mm laps, never inherited 78mm force.

Compare actual body crops and complete caps with independent 1N radial loads.
Mesh-checked compliance feeds the established frictionless spring/ramp proxy;
full deformable contact, printed force, peel and sound remain unqualified.
"""
from dataclasses import replace
import json
from pathlib import Path
import sys
from physical_analysis import StructuralQuestion, Region, Support, SurfaceForce, QuestionStudy
from physical_analysis.evidence import retain_run
from execution.batch import ScriptTask, run as batch
from closure_research_flex import MATERIAL
import short_lap_design as design

ROOT = Path(__file__).resolve().parent
OUT = ROOT/'notes/short_lap'


def question(overlap, member):
    if member not in ('body','cap'):
        raise ValueError(member)
    parts = design.build(overlap)
    d = parts['dimensions']
    z = d.latch_z
    if member == 'body':
        part = design.sample(parts)['body']
        r = d.sleeve_width/2+d.detent
        pad = Region((r,-5,z-.25),(r,5,z+.25))
        force = (-1,0,0)
        clamp = d.seam-16
    else:
        part = parts['cap']
        r = d.width/2-d.wall
        pad = Region((r,-5.3,z-3.2),(r,5.3,z-1))
        force = (1,0,0)
        clamp = d.length
    return StructuralQuestion(name=f'short_lap_{overlap:g}_{member}', part=part,
        material=MATERIAL, supports=(Support(Region.plane('z',clamp)),),
        forces=(SurfaceForce(pad,force),), observations={'pad':pad},
        mesh_size_mm=2.5, nonlinear=False, max_increment=1.)


def solve(overlap, member):
    folder = OUT/'native'/f'{overlap:g}_{member}'
    compact = OUT/'flex'/f'{overlap:g}_{member}'
    if folder.exists() or compact.exists():
        raise ValueError('Existing study: read identity-checked evidence, do not overwrite')
    study = QuestionStudy(question(overlap,member),
        decision='Choose short overlap with useful snap force scale; resolve radial compliance to 10%, without printed-force or strength qualification',
        metrics=('max_displacement_mm',), relative_tolerance=.10, mesh_levels=1)
    result = study.run(folder)
    print(overlap,member,result.status,flush=True)
    for label in ('baseline','mesh_sensitivity_1'):
        if (folder/label/'result.json').exists():
            retain_run(folder/label,compact/label)
    (compact/'study_result.json').write_text((folder/'study_result.json').read_text())


def run_all():
    tasks = [ScriptTask(f'{lap:g}_{member}', Path(__file__).resolve(),
                       ('solve',str(lap),member),
                       outputs=(OUT/'native'/f'{lap:g}_{member}',OUT/'flex'/f'{lap:g}_{member}'),
                       threads=1)
             for lap in design.OVERLAPS for member in ('body','cap')]
    answers = batch(tasks,max_concurrent=2)
    print(json.dumps(answers),flush=True)
    if any(v['exit_code'] for v in answers.values()):
        raise RuntimeError('Inspect failed short-lap study')


if __name__ == '__main__':
    if sys.argv[1:] == ['batch']:
        run_all()
    elif len(sys.argv) == 4 and sys.argv[1] == 'solve':
        solve(float(sys.argv[2]),sys.argv[3])
    else:
        raise SystemExit('Use batch or solve OVERLAP body|cap')
