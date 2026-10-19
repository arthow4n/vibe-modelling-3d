"""Force/energy screen for stronger bearing bands and a smaller .6mm bite."""
from dataclasses import replace
import json
import sys
import numpy as np
from physical_analysis import Region, SurfaceForce, QuestionStudy
from physical_analysis.evidence import retain_run
from execution.batch import ScriptTask, run as batch
from short_lap_refinement_study import question as previous_question
from short_lap_study import OUT, ROOT
from short_lap_report import segments, guide_screen
from short_lap_design import sample
import short_lap_reinforced as design
from short_lap_refinement import bump
from closure_research_pull import required_retraction, profile_retraction, spring_path
from closure_research_checks import hashes

INPUTS = ('short_lap_reinforced.py','short_lap_reinforced_study.py','short_lap_refinement.py',
    'short_lap_design.py','short_lap_study.py','short_lap_refinement_study.py','short_lap_report.py',
    'closure_research_design.py','m1_design.py','closure_research_flex.py',
    'closure_research_pull.py','overlap_exploration.py','overlap_diagonal.py')


def question(member):
    q = previous_question(member)
    p = design.build(design.SELECTED_OVERLAP)
    d = p['dimensions']
    z = d.latch_z
    if member == 'body':
        r = d.sleeve_width/2+d.detent
        pad = Region((r,-5,z-.25),(r,5,z+.25))
        part,force = sample(p)['body'],(-1,0,0)
    elif member == 'cap':
        r = d.width/2-d.wall
        pad = Region((r,-5.3,z-3.2),(r,5.3,z-1))
        part,force = p['cap'],(1,0,0)
    else:
        raise ValueError(member)
    return replace(q,name='reinforced_'+member,part=part,
                   forces=(SurfaceForce(pad,force),),observations={'pad':pad})


def solve(member):
    folder,compact = OUT/'native'/('reinforced_'+member),OUT/'flex'/('reinforced_'+member)
    if folder.exists() or compact.exists():
        raise ValueError('Existing study; read evidence or choose a fresh destination')
    result = QuestionStudy(question(member),
        decision='Resolve 30mm reinforced prototype radial compliance to 10%; compare 8–18N pull and >=3.5N ideal energy threshold, not printed qualification',
        metrics=('max_displacement_mm',),relative_tolerance=.10,mesh_levels=1).run(folder)
    for label in ('baseline','mesh_sensitivity_1'):
        if (folder/label/'result.json').exists():
            retain_run(folder/label,compact/label)
    (compact/'study_result.json').write_text((folder/'study_result.json').read_text())
    print('reinforced',member,result.status,flush=True)


def report():
    members = {}
    for member in ('body','cap'):
        records = []
        for label,mesh in (('baseline',2.5),('mesh_sensitivity_1',1.75)):
            folder = OUT/'flex'/('reinforced_'+member)/label
            answer = replace(question(member),mesh_size_mm=mesh).read_evidence(folder)
            assert answer.completed
            r = json.loads((folder/'result.json').read_text())
            assert r['metrics']['question']['numerical_evidence_adequate']
            records.append(r)
        values = [abs(r['metrics']['observations']['pad']['mean_mm'][0]) for r in records]
        change = abs(values[1]-values[0])/values[1]
        assert change < .10
        r = records[1]
        assert r['metrics']['max_force_balance_relative'] < .01
        members[member] = dict(compliance_mm_N=values[1],mesh_relative_change=change,
            peak_strain_at_1N=r['metrics']['question']['peak_strain'],
            input_sha256=r['provenance']['input_sha256'],loads=r['provenance']['loads'],
            mesh=r['provenance']['mesh'],balance=r['metrics']['max_force_balance_relative'])
    p = design.build(design.SELECTED_OVERLAP)
    d = p['dimensions']
    tooth = bump(d.sleeve_width/2,d,pocket=False).val().rotate((0,0,0),(0,0,1),-90)
    tooth_profile,receiver = segments(tooth,d),segments(p['cap'].val(),d)
    total = sum(r['compliance_mm_N'] for r in members.values())
    assert all(profile_retraction(tooth_profile,receiver,s,.6) == 0 for s in np.linspace(0,6,49))
    paths,scenarios = {},[]
    for gap in (-.15,0.,.15):
        travel = np.linspace(0,6,481)
        delta = [profile_retraction(tooth_profile,receiver,s,gap) for s in travel]
        path = spring_path(travel,delta,total,2)
        coarse = spring_path(travel[::2],delta[::2],total,2)
        path['peak_step_change'] = abs(path['peak_force_N']-coarse['peak_force_N'])/path['peak_force_N']
        path['energy_step_change'] = abs(path['undamped_seated_release_force_N']-coarse['undamped_seated_release_force_N'])/path['undamped_seated_release_force_N']
        assert path['peak_step_change'] < .10 and path['energy_step_change'] < .10
        witnesses = []
        for s in (0.,.5,1.,2.,3.,6.):
            direct = required_retraction(p['cap'].val(),tooth,s,0,gap)
            planar = profile_retraction(tooth_profile,receiver,s,gap)
            assert abs(direct-planar) < .001
            witnesses.append(dict(travel_mm=s,CAD_retraction_mm=direct,profile_retraction_mm=planar))
        path.update(travel_mm=travel.tolist(),retraction_mm=delta,CAD_witnesses=witnesses)
        paths[str(gap)] = path
        for E in (900,1200,1800):
            for catches in (1,2):
                scale = E/1200*catches/2
                scenarios.append(dict(E_MPa=E,extra_radial_gap_mm=gap,catches=catches,
                    peak_force_N=path['peak_force_N']*scale,
                    undamped_release_threshold_N=path['undamped_seated_release_force_N']*scale))
    guide = guide_screen(p)
    play = max([r['roof_center_lateral_motion_mm'] for axis in ('x','y') for r in guide[axis]]+
               [guide['diagonal']['roof_center_lateral_motion_mm']])
    radial_force = max(paths['0.0']['retraction_mm'])/total
    data = dict(scope=__doc__+' Uncalibrated elastic proxy; not safe payload, printed holding or impact qualification.',
        source_sha256=hashes(INPUTS),overlap_mm=d.lap,members=members,paths=paths,scenarios=scenarios,
        guide=guide,missing_bite_zero_barrier=True,
        nominal_scaled_peak_strain={m:r['peak_strain_at_1N']*radial_force for m,r in members.items()},
        provisional_screens=dict(nominal_centered_pull_8_to_18N=8 <= paths['0.0']['peak_force_N'] <= 18,
                                 nominal_energy_threshold_above_3_5N=paths['0.0']['undamped_seated_release_force_N'] >= 3.5,
                                 rigid_roof_motion_below_1mm=play < 1.))
    (OUT/'reinforced.json').write_text(json.dumps(data,indent=2)+'\n')
    print('reinforced nominal',paths['0.0']['peak_force_N'],paths['0.0']['undamped_seated_release_force_N'],flush=True)


if __name__ == '__main__':
    if sys.argv[1:] == ['batch']:
        results = batch([ScriptTask('reinforced_'+m,ROOT/'short_lap_reinforced_study.py',('solve',m),threads=1,
            outputs=(OUT/'native'/('reinforced_'+m),OUT/'flex'/('reinforced_'+m))) for m in ('body','cap')],max_concurrent=2)
        print(json.dumps(results),flush=True)
        if any(r['exit_code'] for r in results.values()):
            raise RuntimeError('Inspect failed reinforced study')
    elif len(sys.argv) == 3 and sys.argv[1] == 'solve':
        solve(sys.argv[2])
    elif not sys.argv[1:]:
        report()
    else:
        raise SystemExit('Use batch, solve body|cap, or no arguments to report')
