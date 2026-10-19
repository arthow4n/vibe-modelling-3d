"""Compare new wall-compliance evidence, CAD ramp paths and guide-only rocking."""
from dataclasses import replace
import json
import math
import sys
from types import SimpleNamespace
import numpy as np
import cadquery as cq
import short_lap_design as design
from short_lap_study import question, OUT
from closure_research_checks import hashes
from closure_research_pull import profile_retraction, required_retraction, spring_path
from overlap_exploration import onset, peel
from overlap_diagonal import first_contact, pose as diagonal_pose
import m1_design as base

INPUTS = ('m1_design.py','closure_research_design.py','short_lap_design.py',
          'short_lap_study.py','short_lap_report.py','closure_research_flex.py',
          'closure_research_pull.py','overlap_exploration.py','overlap_diagonal.py')


def segments(shape, d):
    result = []
    for edge in cq.Workplane('XZ').add(shape).section().val().Edges():
        a,b = edge.startPoint().toTuple(),edge.endPoint().toTuple()
        if min(a[0],b[0]) > d.sleeve_width/2-1 and min(a[2],b[2]) < d.latch_z+3 and max(a[2],b[2]) > d.latch_z-8:
            if edge.geomType() != 'LINE':
                raise ValueError('Curved contact needs a different clearance model')
            result.append(((a[0],a[2]),(b[0],b[2])))
    if not result:
        raise ValueError('Missing contact profile')
    return result


def compliance(lap, member):
    records = []
    for level,mesh in (('baseline',2.5),('mesh_sensitivity_1',1.75)):
        folder = OUT/'flex'/f'{lap:g}_{member}'/level
        answer = replace(question(lap,member),mesh_size_mm=mesh).read_evidence(folder)
        if not answer.completed:
            raise ValueError(f'Incomplete {lap} {member} {level}')
        data = json.loads((folder/'result.json').read_text())
        assert data['metrics']['question']['numerical_evidence_adequate']
        records.append(data)
    values = [abs(v['metrics']['observations']['pad']['mean_mm'][0]) for v in records]
    change = abs(values[1]-values[0])/values[1]
    assert change < .10, (lap,member,change)
    r = records[1]
    assert r['metrics']['max_force_balance_relative'] < .01
    return dict(compliance_mm_N=values[1],mesh_relative_change=change,
                peak_strain_at_1N=r['metrics']['question']['peak_strain'],
                input_sha256=r['provenance']['input_sha256'],
                loads=r['provenance']['loads'],mesh=r['provenance']['mesh'],
                balance=r['metrics']['max_force_balance_relative'])


def guide_screen(parts):
    d = parts['dimensions']
    rows = {}
    for axis in ('x','y'):
        events = []
        for shift in (0.,d.clearance):
            event = onset(parts['plain_body'].val(),parts['cap'].val(),d,
                          axis=axis,transverse=shift)
            angle = event['angle_deg']
            assert angle is not None
            # Track cap roof center in the actual prescribed rigid pose.
            point = cq.Vertex.makeVertex(0,0,d.length)
            point = peel(point,d,angle,axis=axis,transverse=shift).Center()
            lateral = math.hypot(point.x,point.y)
            events.append(dict(shift_mm=shift,angle_deg=angle,
                               roof_center_lateral_motion_mm=lateral))
        rows[axis] = events
    diagonal = SimpleNamespace(width=d.width,depth=d.depth,seam=d.seam,lap_clearance=d.clearance)
    angle = first_contact(parts['plain_body'].val(),parts['cap'].val(),diagonal)
    point = diagonal_pose(cq.Vertex.makeVertex(0,0,d.length),diagonal,angle).Center()
    rows['diagonal'] = dict(angle_deg=angle,roof_center_lateral_motion_mm=math.hypot(point.x,point.y))
    # The nominal overlap carries a bearing couple; actual contact is narrower
    # and wall flexibility can increase rotation. This is equilibrium, not strength.
    rows['side_load_assumption_N'] = 2.
    rows['seam_moment_Nmm'] = 2*(d.length-d.seam)
    rows['ideal_full_span_bearing_reaction_N'] = rows['seam_moment_Nmm']/d.lap
    rows['scope'] = 'Guide-only rigid prescribed principal and diagonal rocking, snaps omitted; no loaded stiffness, unrestricted peel or impact strength claim'
    return rows


def guides():
    data = dict(source_sha256=hashes(INPUTS),cases={})
    for lap in design.OVERLAPS:
        data['cases'][str(lap)] = guide_screen(design.build(lap))
        print('guide',lap,data['cases'][str(lap)],flush=True)
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/'guides.json').write_text(json.dumps(data,indent=2)+'\n')


def report():
    from closure_research_verification import require_sources
    guide_data = json.loads((OUT/'guides.json').read_text())
    require_sources(guide_data['source_sha256'])
    cases = {}
    for lap in design.OVERLAPS:
        p = design.build(lap)
        d = p['dimensions']
        members = {m:compliance(lap,m) for m in ('body','cap')}
        total_c = sum(v['compliance_mm_N'] for v in members.values())
        tooth = design.research.local_bump(d.sleeve_width/2,d.latch_z,d.bump_width,d.detent).val()
        tooth = tooth.rotate((0,0,0),(0,0,1),-90)
        tooth_profile,cap_profile = segments(tooth,d),segments(p['cap'].val(),d)
        paths = {}
        for gap in (-.15,0.,.15):
            travel = np.linspace(0,6,481)
            delta = np.array([profile_retraction(tooth_profile,cap_profile,s,gap) for s in travel])
            witnesses = []
            for s in (0.,.5,1.,2.,3.,6.):
                actual = required_retraction(p['cap'].val(),tooth,s,0,gap)
                planar = profile_retraction(tooth_profile,cap_profile,s,gap)
                assert abs(actual-planar) < .001,(lap,gap,s,actual,planar)
                witnesses.append(dict(travel_mm=s,CAD_retraction_mm=actual,profile_retraction_mm=planar))
            path = spring_path(travel,delta,total_c,2)
            coarse = spring_path(travel[::2],delta[::2],total_c,2)
            path['peak_step_change'] = abs(path['peak_force_N']-coarse['peak_force_N'])/path['peak_force_N']
            assert path['peak_step_change'] < .10
            path.update(travel_mm=travel.tolist(),retraction_mm=delta.tolist(),CAD_witnesses=witnesses)
            paths[str(gap)] = path
        scenarios = []
        for E in (900,1200,1800):
            for gap,path in paths.items():
                for count in (1,2):
                    scale = E/1200*count/2
                    scenarios.append(dict(E_MPa=E,extra_radial_gap_mm=float(gap),catches=count,
                        peak_force_N=path['peak_force_N']*scale,
                        undamped_release_threshold_N=path['undamped_seated_release_force_N']*scale))
        radial_force = max(paths['0.0']['retraction_mm'])/total_c
        cases[str(lap)] = dict(overlap_mm=lap,members=members,
            radial_compliance_mm_N=total_c,paths=paths,scenarios=scenarios,
            nominal_scaled_peak_strain={m:v['peak_strain_at_1N']*radial_force for m,v in members.items()},
            guide=guide_data['cases'][str(lap)])
        print(lap,'nominal pull N',paths['0.0']['peak_force_N'],
              'energy threshold N',paths['0.0']['undamped_seated_release_force_N'],flush=True)
    result = dict(scope=__doc__+' Uncalibrated elastic comparison; not a payload, printed force, noise or durability rating.',
                  source_sha256=hashes(INPUTS),cases=cases)
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/'comparison.json').write_text(json.dumps(result,indent=2)+'\n')
    return result


if __name__ == '__main__':
    if sys.argv[1:] == ['guides']:
        guides()
    elif not sys.argv[1:]:
        report()
    else:
        raise SystemExit('Use no arguments or guides')
