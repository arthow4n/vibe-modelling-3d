"""Conditional hand-calculation screen, N/mm/MPa. No FEA or load certification."""
from pathlib import Path
import json, math, hashlib
ROOT=Path(__file__).resolve().parent
s=json.loads((ROOT/'notes/sections.json').read_text())
p=s['full_section']['parameters']
assert s['source_sha256']['joint.py']==hashlib.sha256((ROOT/'joint.py').read_bytes()).hexdigest()
g=9.81; book=3; plate=1.6; L=400; handling=2
M_service=book*g*L/4+plate*g*L/8
M=M_service*handling
V=(book+plate)*g/2*handling
T=V*125
spacing=2*p['hole_x']; row_gap=p['back_hole_y']-5
Fz=.6*M/spacing+.6*T/row_gap+.3*V
transverse=math.hypot(Fz,.3*50)
axial=1.25*Fz+40
K=1.5; normal=7; shear=normal/math.sqrt(3)
checks={}
def check(name,stress,allow=normal):
    checks[name]={'stress_MPa':stress,'allowable_MPa':allow,'margin':allow/stress,'passes':stress<=allow}
for name,data in s['full_section']['parts'].items():
    check(name+'_net_section_bending',K*M/data['minimum_section']['Sy_mm3'])
for name,data in s['full_section']['parts'].items():
    check(name+'_lap_root_notch_screen',2.5*M/data['sections'][0]['Sy_mm3'])
rear_t=p['layer_split']-p['head_recess']-p['head_thickness']
check('rear_shoulder_bearing',K*transverse/(p['shoulder_diameter']*rear_t))
check('front_shoulder_bearing',K*transverse/(p['thread_root']*3.7))
d=p['thread_root']; area=math.pi*d*d/4; modulus=math.pi*d**3/32
sigma=K*(axial/area+(transverse*4/2)/modulus)
tau=K*transverse/area
check('screw_combined_von_mises',math.sqrt(sigma*sigma+3*tau*tau))
check('screw_shear',tau,shear)
head_area=math.pi*(p['head_diameter']**2-p['shoulder_diameter']**2)/4
head_reach=(p['head_diameter']-p['shoulder_diameter'])/2
check('head_annulus_bending',K*3*(axial/head_area)*head_reach**2/p['head_thickness']**2)
check('head_annulus_bearing',K*axial/head_area)
for name,data in s['thread_stripping_surfaces'].items():
    check(name+'_thread_strip',K*axial/data['screening_area_mm2'],shear)
edge=p['overlap_half']-p['hole_x']-(p['shoulder_diameter']+p['shoulder_clearance'])/2
counterbore_reach=(p['head_diameter']+.4-p['shoulder_diameter']-p['shoulder_clearance'])/2
tear_area=2*((edge-counterbore_reach)*p['layer_split']+counterbore_reach*rear_t)
check('rear_edge_tearout',K*transverse/tear_area,shear)
check('front_edge_tearout',K*transverse/(2*(p['overlap_half']-p['hole_x']-(p['thread_major']+2*p['thread_clearance'])/2)*p['layer_split']),shear)
I=min(v['minimum_Iy_mm4'] for v in s['full_section']['parts'].values())
rotation=M_service*(2*p['overlap_half'])/(800*I)
play=p['shoulder_clearance']/spacing
# Conservative bearing-spring approximation: deformation length equals bore diameter.
service_force=transverse/handling
bearing_slip=service_force/800*(1/rear_t+1/3.7)
bolt_shear_slip=service_force*4/((800/(2*1.4))*area)
fastener_rotation=2*(bearing_slip+bolt_shear_slip)/spacing
total_rotation=rotation+fastener_rotation+play
report={'scope':'Conditional conservative analytical screen of full-height joint section; not full-plate FEA or physical validation',
'assumptions':{'book_kg':book,'plate_kg':plate,'span_mm':L,'handling_factor':handling,'geometry_multiplier':K,'normal_allowance_MPa':normal,'shear_allowance_MPa':shear,'effective_E_MPa':800,'row_load_share_envelope':.6,'torsion_offset_mm':125,'prying_factor':1.25,'preload_upper_assumption_N':40,'direct_pull_N':50},
'loads':{'service_moment_Nmm':M_service,'design_moment_Nmm':M,'design_shear_N':V,'design_torsion_Nmm':T,'bolt_transverse_envelope_N':transverse,'bolt_axial_envelope_N':axial},
'checks':checks,'minimum_margin':min(c['margin'] for c in checks.values()),
'stiffness':{'section_elastic_rotation_degree':math.degrees(rotation),'fastener_bearing_rotation_estimate_degree':math.degrees(fastener_rotation),'joint_rotation_including_clearance_estimate_degree':math.degrees(total_rotation),'joint_sag_contribution_including_clearance_mm':L*total_rotation/4,'section_rotation_midspan_sag_mm':L*rotation/4,'unclamped_shoulder_play_bound_degree':math.degrees(play),'scope':'Conservative individual lap section only. Includes simplified fastener/bearing spring estimate and free clearance separately. Excludes full-plate warping, contact nonlinearity and PETG creep; not a certified deflection bound.'},
'source_sha256':{f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in [ROOT/'joint.py',ROOT/'measure.py',ROOT/'notes/sections.json',Path(__file__)]}}
(ROOT/'notes/load_checks.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k!='source_sha256'},indent=2))
assert all(c['passes'] for c in checks.values()),'A strength screening check failed'
