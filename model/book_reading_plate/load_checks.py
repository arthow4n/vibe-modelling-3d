"""Conditional hand-calculation screen, N/mm/MPa. No FEA or load certification."""
from pathlib import Path
import json, math, hashlib
ROOT=Path(__file__).resolve().parent
s=json.loads((ROOT/'notes/sections.json').read_text())
p=s['parameters']
engagement=s['thread_engagement_interval_mm'][1]-s['thread_engagement_interval_mm'][0]
assert s['source_sha256']['components.py']==hashlib.sha256((ROOT/'components.py').read_bytes()).hexdigest()
g=9.81; book=3; plate=1.6; L=p['width']; handling=2
M_service=book*g*L/4+plate*g*L/8
M=M_service*handling
V=(book+plate)*g/2*handling
T=V*125
spacing=2*p['hole_x']; row_gap=p['inner_height']+p['thickness']-p['back_top_margin']-p['thickness']/2
Fz=.6*M/spacing+.6*T/row_gap+.3*V
transverse=math.hypot(Fz,.3*50)
axial=1.25*Fz+40
K=1.5; normal=7; shear=normal/math.sqrt(3)
checks={}
def check(name,stress,allow=normal):
    checks[name]={'stress_MPa':stress,'allowable_MPa':allow,'margin':allow/stress,'passes':stress<=allow}
for name,data in s['parts'].items():
    stresses=[]
    for sec in data['sections']:
        u=L/2-abs(sec['x_mm'])
        local_moment=handling*(book*g*u/2+(plate*g/L)*u*(L-u)/2)
        stresses.append(K*local_moment/sec['Sy_mm3'])
    check(name+'_net_section_bending',max(stresses))
for name,data in s['parts'].items():
    root_u=L/2-abs(data['root_section']['x_mm'])
    root_moment=handling*(book*g*root_u/2+(plate*g/L)*root_u*(L-root_u)/2)
    check(name+'_lap_root_notch_screen',2.5*root_moment/data['root_section']['Sy_mm3'])
rear_t=p['thickness']/2-p['lap_gap']/2-(p['end_recess']+p['head_rim']+(p['head_diameter']-p['shoulder_diameter'])/2)
check('rear_shoulder_bearing',K*transverse/(p['shoulder_diameter']*rear_t))
check('front_shoulder_bearing',K*transverse/(p['thread_root']*engagement))
d=p['thread_root']; area=math.pi*d*d/4; modulus=math.pi*d**3/32
sigma=K*(axial/area+(transverse*4/2)/modulus)
tau=K*transverse/area
check('screw_combined_von_mises',math.sqrt(sigma*sigma+3*tau*tau))
check('screw_shear',tau,shear)
head_area=math.pi*(p['head_diameter']**2-(p['shoulder_diameter']+p['shoulder_clearance'])**2)/4
# Fan-shaped radial strips have more loaded width at the outer radius.
head_curvature_factor=p['head_diameter']/p['shoulder_diameter']
head_reach=(p['head_diameter']-p['shoulder_diameter'])/2
check('conical_head_strip_bending',K*head_curvature_factor*3*(axial/head_area)*head_reach**2/(p['head_rim']+head_reach)**2)
check('head_neck_net_axial',K*axial/(math.pi*p['shoulder_diameter']**2/4-math.sqrt(3)*p['hex_af']**2/2))
# 45-degree seat: total radial wedge force equals axial force.
seat_height=(p['head_diameter']-p['shoulder_diameter']-p['shoulder_clearance'])/2
seat_mean_radius=(p['head_diameter']+p['shoulder_diameter']+p['shoulder_clearance'])/4
seat_edge_wall=p['overlap_half']-p['hole_x']-(p['head_diameter']+.4)/2
radial_pressure=axial/(2*math.pi*seat_mean_radius*seat_height)
check('countersink_splitting_screen',K*radial_pressure*seat_mean_radius/seat_edge_wall)
check('head_annulus_bearing',K*axial/head_area)
for name,data in s['thread_stripping_surfaces'].items():
    check(name+'_thread_strip',K*axial/data['screening_area_mm2'],shear)
edge=p['overlap_half']-p['hole_x']-(p['shoulder_diameter']+p['shoulder_clearance'])/2
counterbore_reach=(p['head_diameter']+.4-p['shoulder_diameter']-p['shoulder_clearance'])/2
tear_area=2*((edge-counterbore_reach)*(p['thickness']/2-p['lap_gap']/2)+counterbore_reach*rear_t)
check('rear_edge_tearout',K*transverse/tear_area,shear)
check('front_edge_tearout',K*transverse/(2*(p['overlap_half']-p['hole_x']-(p['thread_major']+2*p['thread_clearance'])/2)*(p['thickness']/2-p['lap_gap']/2)),shear)
I=min(v['minimum_Iy_mm4'] for v in s['parts'].values())
rotation=M_service*(2*p['overlap_half'])/(800*I)
play=p['shoulder_clearance']/spacing
# Conservative bearing-spring approximation: deformation length equals bore diameter.
service_force=transverse/handling
bearing_slip=service_force/800*(1/rear_t+1/engagement)
bolt_shear_slip=service_force*4/((800/(2*1.4))*area)
fastener_rotation=2*(bearing_slip+bolt_shear_slip)/spacing
total_rotation=rotation+fastener_rotation+play
# Unit-load integration of the complete simply supported 400 mm L beam.
# Use the weaker single lap throughout overlap: no composite-interface credit.
whole=s['whole_L_section'];check('whole_plate_L_bending',K*M/whole['Sy_mm3'])
E=800;G=E/(2*1.4);steps=2000;dx=(L/2)/steps
beam_sag=0
for i in range(steps):
    u=(i+.5)*dx
    moment=book*g*u/2+(plate*g/L)*u*(L-u)/2
    section_I=I if u>=L/2-p['overlap_half'] else whole['Iy_mm4']
    beam_sag += 2*moment*(u/2)/(E*section_I)*dx
joint_sag=L*(fastener_rotation+play)/4
# Secondary estimate without credit for lip stiffening, for sensitivity to load spreading.
back_I=p['inner_height']*p['thickness']**3/12
back_sag=book*g*L**3/(48*E*back_I)+5*plate*g*L**3/(384*E*back_I)
# Open L-section Saint-Venant torsion, conservative lap halves unbonded.
J_whole=(p['inner_height']+p['inner_lip'])*p['thickness']**3/3
J_lap=(p['inner_height']+p['inner_lip'])*2*(p['thickness']/2-p['lap_gap']/2)**3/3
# Service end torque over each half. A bounding eccentric-grip case, not ordinary lap use.
twist=(T/handling)*((L/2-p['overlap_half'])/J_whole+p['overlap_half']/J_lap)/G
check('whole_L_torsion',K*T*p['thickness']/J_whole, shear)
check('lap_L_torsion',K*T*(p['thickness']/2-p['lap_gap']/2)/J_lap, shear)
# Combined stress screens use the same simultaneous bending/torsion load case.
torsion_stress=K*T*(p['thickness']/2-p['lap_gap']/2)/J_lap
for name in ['rear','front']:
    for mode in ['net_section_bending','lap_root_notch_screen']:
        sigma=checks[name+'_'+mode]['stress_MPa']
        check(name+'_'+mode+'_with_torsion',math.sqrt(sigma*sigma+3*torsion_stress*torsion_stress))
report={'scope' :'Conditional full-plate beam and local joint analytical screens; not FEA or physical validation',
'assumptions':{'book_kg':book,'plate_kg':plate,'span_mm':L,'handling_factor':handling,'geometry_multiplier':K,'normal_allowance_MPa':normal,'shear_allowance_MPa':shear,'effective_E_MPa':800,'row_load_share_envelope':.6,'torsion_offset_mm':125,'prying_factor':1.25,'preload_upper_assumption_N':40,'direct_pull_N':50},
'loads':{'service_moment_Nmm':M_service,'design_moment_Nmm':M,'design_shear_N':V,'design_torsion_Nmm':T,'bolt_transverse_envelope_N':transverse,'bolt_axial_envelope_N':axial},
'checks':checks,'minimum_margin':min(c['margin'] for c in checks.values()),
'full_plate_estimates':{'beam_sag_mm':beam_sag,'joint_fastener_and_clearance_sag_mm':joint_sag,'total_L_beam_sag_mm':beam_sag+joint_sag,'plain_back_beam_sag_without_lip_or_joint_mm':back_sag,'eccentric_grip_section_twist_degree':math.degrees(twist),'scope':'Simple supports across full width; whole L cross-section load sharing. Plain-back sensitivity is a separate model, not added to L result. Torsion neglects restrained warping and fastener compliance; not a validated bound.'},
'stiffness':{'section_elastic_rotation_degree':math.degrees(rotation),'fastener_bearing_rotation_estimate_degree':math.degrees(fastener_rotation),'joint_rotation_including_clearance_estimate_degree':math.degrees(total_rotation),'joint_sag_contribution_including_clearance_mm':L*total_rotation/4,'section_rotation_midspan_sag_mm':L*rotation/4,'unclamped_shoulder_play_bound_degree':math.degrees(play),'scope':'Conservative individual lap section only. Includes simplified fastener/bearing spring estimate and free clearance separately. Excludes full-plate warping, contact nonlinearity and PETG creep; not a certified deflection bound.'},
'source_sha256':{f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in [ROOT/'components.py',ROOT/'measure_structure.py',ROOT/'notes/sections.json',Path(__file__)]}}
(ROOT/'notes/load_checks.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k!='source_sha256'},indent=2))
assert all(c['passes'] for c in checks.values()),'A strength screening check failed'
