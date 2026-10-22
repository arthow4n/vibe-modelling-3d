"""Review delivered screw core and local wheel/core toolpaths from native receipts."""
import json,hashlib
from pathlib import Path
from collections import defaultdict
from math import hypot
from statistics import median
from physical_analysis.manufacturing import orca_linear_paths,section_coverage
import cadquery as cq
from rotary_conical_design import screw_print_pose


def main():
    root=Path(__file__).resolve().parent;n=root/'notes/rotary_case'
    reports={k:json.loads((n/(v+'_review.json')).read_text()) for k,v in [('wheel','wheel'),('screw','screw'),('full','print')]}
    paths={}
    for k,r in reports.items():
     g=Path(r['slice']['kept_run_directory'])/'plate_1.gcode'
     paths[k]=list(orca_linear_paths(g))

    # The user-reported empty-thread failure justifies a targeted delivered STEP core check.
    step=cq.importers.importStep(str(root/'rotary_conical_screw.step'))
    core=screw_print_pose(cq.Workplane('XY',origin=(0,0,4.2)).circle(2.28).extrude(6.39))
    missing=core.cut(step).val().Volume();assert missing<1e-5,missing
    negative=cq.importers.importStep(str(root/'rotary_refinement_axle.step'))
    witness=cq.Workplane('XY',origin=(0,0,5.)).circle(1.5).extrude(4.)
    old_missing=witness.cut(negative).val().Volume();assert old_missing>28
    sections=[]
    for z in (4.6,5.,6.,8.,10.8):
     c=section_coverage(paths['screw'],x_mm=135,z_mm=z,span_mm=(132.8,137.2))
     assert c['uncovered_width_mm']<.1,(z,c)
     sections.append(dict(z_mm=z,coverage=c))
    # Review actual inner perimeter progression through the wheel's former flat roof.
    rings=defaultdict(list)
    for x,y,nx,ny,z,w,role in paths['wheel']:
     if role!='Outer wall' or z>2.4:continue
     radius=hypot((x+nx)/2-135,(y+ny)/2-135)
     if 4.<radius<6.7:rings[round(z,4)].append((radius,w))
    progression=[dict(z_mm=z,median_radius_mm=median(q[0] for q in v),median_width_mm=median(q[1] for q in v)) for z,v in sorted(rings.items())]
    for a,b in zip(progression,progression[1:]):
     drop=a['median_radius_mm']-b['median_radius_mm']
     overlap=(a['median_width_mm']+b['median_width_mm'])/2-drop
     assert overlap>0,(a,b,overlap)
     b['overlap_with_previous_ring_mm']=overlap
    assert len(progression)>=10
    # Include both support roles in the full layout; standalone parts should have none.
    groups=defaultdict(list)
    for p in paths['full']:
     if not p[-1].startswith('Support'):continue
     x=(p[0]+p[2])/2;y=(p[1]+p[3])/2
     region='wheel' if y>160 else 'cap' if x>160 else 'body'
     groups[region,p[-1]].append(p)
    records={};outside=True
    for (region,role),rows in groups.items():
     low=min(min(q[1],q[3])-q[5]/2 for q in rows);high=max(max(q[1],q[3])+q[5]/2 for q in rows)
     assert region!='wheel','New wheel should not generate full-layout supports'
     safe=high<78.95 if region=='body' else low>127.65
     outside &= safe
     records[region+' / '+role]=dict(segments=len(rows),z_mm=[min(q[4] for q in rows),max(q[4] for q in rows)],deposited_y_extent_mm=[low,high],outside_storage=safe)
    assert outside
    support=dict(slice_input_sha256=reports['full']['slice']['input_sha256'],reviewed_roles=sorted({role for _,role in groups}),all_support_outside_storage=outside,regions=records,centering_translation_xy_mm=[85.,103.35],interpretation='Full layout has accessible body exterior bore and cap keeper supports only; new wheel has no supports. All recorded support paths plus half extrusion width remain outside storage. Remove before assembly.')
    (n/'support_review.json').write_text(json.dumps(support,indent=2)+'\n')
    inputs=('rotary_conical_print_checks.py','rotary_conical_design.py','../../physical_analysis/manufacturing.py')
    out=dict(source_sha256={name:hashlib.sha256((root/name).read_bytes()).hexdigest() for name in inputs},exported_thread_missing_core_mm3=missing,old_hollow_negative_control_missing_mm3=old_missing,
     solid_core_sections=sections,uncovered_width_limit_mm=.1,wheel_inner_perimeter_progression=progression,
     scope='Targeted exported screw thread core and 100% sliced fill; actual wheel inner perimeter replaces the former abrupt recess roof. Path widths are approximations, not calibrated polymer or print finish.',
     slice_inputs={k:r['slice']['input_sha256'] for k,r in reports.items()})
    (n/'conical_print_paths.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(dict(core_missing=missing,core_sections=len(sections),wheel_layers=len(progression),support_regions=list(records))))


if __name__=='__main__':main()
