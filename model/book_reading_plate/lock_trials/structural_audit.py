"""Reproducible rejection screen, SI-derived loads and N-mm section mechanics.
Run after measure_structure.py through MCP; this script performs no CAD or exports.
A pass here would still not validate nonlinear contact or unknown printed material.
"""
from pathlib import Path
import json,math,hashlib
ROOT=Path(__file__).resolve().parent
DATA=ROOT/'notes/structural_review'
cad=json.loads((DATA/'cad_sections.json').read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert cad['hashes']['lock_trials.py']==sha(ROOT/'lock_trials.py')
# Explicit design assumptions, not measurements of the user's book/material.
g=9.81; span=400.; book_kg=3.; plate_kg=1.6
handling_factor=2.; K=1.5; strength_reference=14.; material_factor=2.
allow=strength_reference/material_factor; shear_allow=allow/math.sqrt(3)
E=800.; withdrawal_N=50.
M_service=book_kg*g*span/4+plate_kg*g*span/8
M_design=handling_factor*M_service
V_design=handling_factor*(book_kg+plate_kg)*g/2
full_width=238-12 # provisional production rail; deduct whole spring-relief band
report={'status':'REJECT_CURRENT_A_AND_B_FOR_LOADED_PLATE','assumptions':{
 'book_kg':book_kg,'plate_mass_budget_kg':plate_kg,'span_mm':span,
 'book_load':'central point load; plate self-weight uniformly distributed',
 'support':'both outside X edges; back joint carries seam moment, no tensile credit for unjoined lip',
 'handling_load_factor':handling_factor,'geometry_stress_multiplier':K,
 'reference_interlayer_strength_MPa':strength_reference,'reference_basis':'18 minus 4 MPa from Prusament PETG TDS; not a guaranteed lower bound for generic PETG',
 'material_safety_factor':material_factor,'normal_allowable_MPa':allow,
 'shear_allowable_MPa':shear_allow,'effective_modulus_MPa':E,
 'withdrawal_design_N':withdrawal_N,'full_rail_effective_width_mm':full_width,
 'service_deflection_target_mm':2,'joint_rotation_target_degrees':.25,
 'infill':'100% solid material assumed for rejection; 40% is not credited as solid'},
 'loads':{'service_force_N':(book_kg+plate_kg)*g,'service_moment_Nmm':M_service,
          'design_moment_Nmm':M_design,'design_half_reaction_N':V_design,
          'all_mass_central_design_moment_Nmm':handling_factor*(book_kg+plate_kg)*g*span/4},'variants':{}}
for letter in 'AB':
 d=cad[letter];p=d['source_parameters']
 local_width=p['rail_end']-p['rail_start']-(p['leaf_width']+2)
 neck=min(d['rail_sections'].values(),key=lambda s:s['Sy_mm3'])
 sy_per_mm=neck['Sy_mm3']/local_width
 skin=d['receiver_rear_skin_mm'];reach=p['depth']+p['clearance'];lever=p['depth']-1
 results={}
 for fraction in [1.,.5]:
  b=full_width*fraction;sy=sy_per_mm*b
  tongue_nom=M_design/sy
  receiver_force=M_design/lever # opposing contact couple, conservative tip load model
  socket_nom=6*receiver_force*reach/(b*skin**2)
  shear_nom=1.5*V_design/(b*p['neck'])
  # Conditional stiffness before yielding; NOT actual deformation when stress screen fails.
  socket_I=b*skin**3/12
  delta=M_service/lever*reach**3/(3*E*socket_I)
  theta=2*delta/lever
  neck_required=math.sqrt(6*M_design*K/(b*allow))
  skin_required=math.sqrt(6*(M_design/lever)*reach*K/(b*allow))
  results[str(fraction)]={'effective_width_mm':b,'section_modulus_mm3':sy,
   'tongue_nominal_MPa':tongue_nom,'tongue_design_MPa':K*tongue_nom,
   'tongue_margin_allowable_over_demand':allow/(K*tongue_nom),
   'socket_nominal_MPa':socket_nom,'socket_design_MPa':K*socket_nom,
   'socket_margin_allowable_over_demand':allow/(K*socket_nom),
   'transverse_shear_design_MPa':K*shear_nom,'transverse_shear_margin':shear_allow/(K*shear_nom),
   'socket_wall_linear_service_deflection_mm':delta,
   'socket_linear_service_rotation_degrees':math.degrees(theta),
   'stiffness_validity':'reject as excessive compliance indicator; contact/yield invalidates quantitative rotation prediction',
   'minimum_neck_mm_at_current_mass':neck_required,
   'minimum_socket_skin_mm_at_current_mass':skin_required,
   'minimum_total_thickness_mm_at_current_mass':neck_required+(p['head']-p['neck'])+2*(skin_required+p['clearance']),
   'sizing_limits':'Same rail architecture, K and mass held fixed; not a redesigned/approved part.'}
 clip=d['clip_root_section'];clip_lever=p['depth']-1-(p['leaf_root']+1)
 clip_nom=withdrawal_N*clip_lever/clip['Sz_mm3']
 # Available hook overlap is conservative at the wide-head part; geometric edge fillets ignored.
 hook_engagement=(p['thickness']-p['head'])/2-p['clearance']-p['hook_tip']
 hook_area=(p['depth']-1)*hook_engagement
 hook_shear=withdrawal_N/hook_area
 # Sample moment that reproduces production moment per active rail length.
 sample_equiv={str(f):M_design*local_width/(full_width*f) for f in [1.,.5]}
 results['retention']={'root_area_mm2':clip['area_mm2'],'root_section_modulus_mm3':clip['Sz_mm3'],
  'load_lever_mm':clip_lever,'root_nominal_bending_MPa':clip_nom,
  'root_design_bending_MPa':K*clip_nom,'root_margin':allow/(K*clip_nom),
  'side_contact_gap_mm':1.0,
  'tip_load_for_1mm_free_cantilever_deflection_N':3*E*clip['Iz_mm4']/clip_lever**3,
  'stress_at_1mm_free_cantilever_deflection_MPa':(3*E*clip['Iz_mm4']/clip_lever**3)*clip_lever/clip['Sz_mm3'],
  'hook_shear_area_estimate_mm2':hook_area,'hook_shear_design_MPa':K*hook_shear,
  'hook_shear_margin':shear_allow/(K*hook_shear),
  'release_strain_nominal':3*p['leaf_thickness']*p['release']/(2*(p['depth']-p['leaf_root']-3)**2),
  'limits':'Free-cantilever extrapolation ceases to apply after relief-side contact; one-mm contact onset is also screened. Contact distribution, stress concentration and receiver restraint need a nonlinear model for approval.'}
 results['sample_equivalent_design_moment_Nmm']=sample_equiv
 results['prior_sample_screen_Nmm']=100
 # Generous ideal full-width case still fails before penalties: robust rejection.
 assert results['1.0']['tongue_nominal_MPa']>strength_reference
 assert results['1.0']['socket_nominal_MPa']>strength_reference
 assert results['retention']['root_margin']<1
 report['variants'][letter]=results
# Back plate alone, solid rectangle, no stiffness credit for discontinuous lip at seam.
I=250*10**3/12
flat_sag=book_kg*g*span**3/(48*E*I)+5*plate_kg*g*span**3/(384*E*I)
report['plate_stiffness_screen']={'back_only_solid_I_mm4':I,'service_sag_mm':flat_sag,
 'limits':'1D full-width strip, ideal supports. Existing L can stiffen halves but its lip has no tensile joint; point grips and plate load spreading need later 3D analysis.'}
report['infill_conclusion']='Changing infill cannot repair a failure calculated for solid geometry. Printed layer bonding and nominally solid voids can further reduce capacity.'
report['required_next_design']='Replace the thin-neck/skin bending load path; do not issue a new safe claim or print recommendation from this rejection screen.'
report['source_hashes']={p.name:sha(p) for p in [Path(__file__),DATA/'cad_sections.json',ROOT/'lock_trials.py']}
(DATA/'load_audit.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'status':report['status'],'loads':report['loads'],'A':report['variants']['A']['1.0'],'B':report['variants']['B']['1.0'],'retention_A':report['variants']['A']['retention'],'plate':report['plate_stiffness_screen']},indent=2))
