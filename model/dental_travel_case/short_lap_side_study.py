"""Conditional side-bearing response, not a contact equilibrium or impact solve.

Two opposing 4mm contact bands reproduce a 2N load 90mm above the seam.
Body and cap deform separately under equal/opposite tractions on matching
bearing walls. Existing geometry meshes can be reused by the native API.
"""
from dataclasses import replace
import json
import math
import sys
from physical_analysis import Region, SurfaceForce, QuestionStudy
from physical_analysis.evidence import retain_run
from execution.batch import ScriptTask, run as batch
from short_lap_refinement_study import question as snap_question
from short_lap_study import OUT, ROOT
from short_lap_design import SELECTED_OVERLAP
import short_lap_refinement as design
from closure_research_checks import hashes


def configuration(stage):
    if stage == 'first':
        return snap_question,design,SELECTED_OVERLAP,'side'
    if stage == 'reinforced':
        from short_lap_reinforced_study import question as final_question
        import short_lap_reinforced as final_design
        return final_question,final_design,final_design.SELECTED_OVERLAP,'reinforced_side'
    raise ValueError(stage)


def question(member, axis, *, stage):
    if axis not in ('x','y'):
        raise ValueError(axis)
    factory,builder,overlap,prefix = configuration(stage)
    q = factory(member)
    d = builder.build(overlap)['dimensions']
    index = 0 if axis == 'x' else 1
    radial = (d.sleeve_width if index == 0 else d.sleeve_depth)/2
    if member == 'cap':
        radial += d.clearance
    across = 18 if index == 0 else 28
    lower,upper = d.seam+3,d.seam+d.lap-3
    span = upper-lower
    high = (2*(d.length-d.seam)-2*3)/span
    low = 2-high
    def band(sign,z):
        return (Region((sign*radial,-across,z-2),(sign*radial,across,z+2)) if index == 0
                else Region((-across,sign*radial,z-2),(across,sign*radial,z+2)))
    top,bottom = band(-1,upper),band(1,lower)
    sign = 1 if member == 'body' else -1
    ftop,flow = [0.,0.,0.],[0.,0.,0.]
    ftop[index],flow[index] = sign*high,sign*low
    return replace(q,name=f'{prefix}_{member}_{axis}',
        forces=(SurfaceForce(top,tuple(ftop)),SurfaceForce(bottom,tuple(flow))),
        observations={'top':top,'bottom':bottom})


def solve(member,axis,*,stage):
    prefix = configuration(stage)[3]
    name = f'{prefix}_{member}_{axis}'
    folder,compact = OUT/'native'/name,OUT/'flex'/name
    if folder.exists() or compact.exists():
        raise ValueError('Existing side study; read evidence or choose fresh destination')
    result = QuestionStudy(question(member,axis,stage=stage),
        decision='Screen two principal side-bearing paths at a gentle 2N cap-end load; 10% displacement precision, no loaded-impact qualification',
        metrics=('max_displacement_mm',),relative_tolerance=.10,mesh_levels=1).run(folder)
    for label in ('baseline','mesh_sensitivity_1'):
        if (folder/label/'result.json').exists():
            retain_run(folder/label,compact/label)
    (compact/'study_result.json').write_text((folder/'study_result.json').read_text())
    print(name,result.status,flush=True)


def report(*,stage):
    _,builder,overlap,prefix = configuration(stage)
    d = builder.build(overlap)['dimensions']
    cases = {}
    for axis,index in (('x',0),('y',1)):
        members = {}
        coarse_members = {}
        for member in ('body','cap'):
            records = []
            for label,mesh in (('baseline',2.5),('mesh_sensitivity_1',1.75)):
                folder = OUT/'flex'/f'{prefix}_{member}_{axis}'/label
                answer = replace(question(member,axis,stage=stage),mesh_size_mm=mesh).read_evidence(folder)
                assert answer.completed
                r = json.loads((folder/'result.json').read_text())
                assert r['metrics']['question']['numerical_evidence_adequate']
                records.append(r)
            fine = records[1]
            observations = fine['metrics']['observations']
            sensitivity = {}
            for label in ('top','bottom'):
                values = [r['metrics']['observations'][label]['mean_mm'][index] for r in records]
                sensitivity[label] = abs(values[1]-values[0])/max(abs(values[1]),.001)
            coarse_members[member] = {k:v['mean_mm'][index] for k,v in records[0]['metrics']['observations'].items()}
            members[member] = dict(mean_mm={k:v['mean_mm'][index] for k,v in observations.items()},
                pad_mesh_relative_change=sensitivity,peak_strain=fine['metrics']['question']['peak_strain'],
                input_sha256=fine['provenance']['input_sha256'],loads=fine['provenance']['loads'],
                balance=fine['metrics']['max_force_balance_relative'])
            assert members[member]['balance'] < .01
        relative = {k:members['body']['mean_mm'][k]-members['cap']['mean_mm'][k] for k in ('top','bottom')}
        slope = (relative['top']-relative['bottom'])/(d.lap-6)
        roof = relative['bottom']+slope*(d.length-d.seam-3)
        coarse_relative = {k:coarse_members['body'][k]-coarse_members['cap'][k] for k in ('top','bottom')}
        coarse_slope = (coarse_relative['top']-coarse_relative['bottom'])/(d.lap-6)
        coarse_roof = coarse_relative['bottom']+coarse_slope*(d.length-d.seam-3)
        roof_change = abs(roof-coarse_roof)/max(abs(roof),.01)
        assert roof_change < .10,('Decision quantity: roof motion',axis,roof_change)
        cases[axis] = dict(members=members,relative_bearing_motion_mm=relative,
            estimated_extra_roof_motion_mm=abs(roof),roof_mesh_relative_change=roof_change,
            coarse_estimated_extra_roof_motion_mm=abs(coarse_roof),
            estimated_extra_rotation_deg=abs(math.degrees(math.atan(slope))))
        print('side',axis,cases[axis]['estimated_extra_roof_motion_mm'],flush=True)
    data = dict(scope=__doc__+' Independent linear fixture response and rigid-band extrapolation. Contact redistribution, shell grip, inertia, diagonal loading and material calibration omitted.',
        source_sha256=hashes(('short_lap_side_study.py','short_lap_refinement_study.py',
            'short_lap_refinement.py','short_lap_design.py','closure_research_design.py','m1_design.py',
            'short_lap_reinforced.py','short_lap_reinforced_study.py')),
        load_N=2.,moment_Nmm=180.,overlap_mm=d.lap,cases=cases)
    (OUT/(prefix+'.json')).write_text(json.dumps(data,indent=2)+'\n')


if __name__ == '__main__':
    if sys.argv[1:] in (['batch'],['batch-final']):
        stage = 'first' if sys.argv[1] == 'batch' else 'reinforced'
        prefix = configuration(stage)[3]
        command = 'solve' if stage == 'first' else 'solve-final'
        tasks = [ScriptTask(f'{prefix}_{member}_{axis}',ROOT/'short_lap_side_study.py',
            (command,member,axis),threads=1,
            outputs=(OUT/'native'/f'{prefix}_{member}_{axis}',OUT/'flex'/f'{prefix}_{member}_{axis}'))
            for member in ('body','cap') for axis in ('x','y')]
        results = batch(tasks,max_concurrent=2)
        print(json.dumps(results),flush=True)
        if any(r['exit_code'] for r in results.values()):
            raise RuntimeError('Inspect failed side study')
    elif len(sys.argv) == 4 and sys.argv[1] in ('solve','solve-final'):
        solve(sys.argv[2],sys.argv[3],stage='first' if sys.argv[1] == 'solve' else 'reinforced')
    elif not sys.argv[1:]:
        report(stage='first')
    elif sys.argv[1:] == ['report-final']:
        report(stage='reinforced')
    else:
        raise SystemExit('Use batch, solve body|cap x|y, or no arguments to report')
