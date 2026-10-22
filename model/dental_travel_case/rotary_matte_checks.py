"""Affected interface checks for the two-part matte-PLA repair. Run explicitly."""
import json,hashlib
from pathlib import Path
import cadquery as cq
from rotary_matte_design import matte_case,printed_axle
from rotary_covered_design import covered_case,face_pose
from rotary_refinement_design import rotor_pose
from rotary_refinement_checks import check_parts,clear,material
from rotary_printed_fastener_design import printed_nut,PITCH,ROOT_RADIUS,TIP
def main():
    p=matte_case();old=covered_case();r={}
    r['unchanged']={}
    for name in ('body','cap','rotor','pivot_nut'):
     a,b=p[name],old[name];v=a.cut(b).val().Volume()+b.cut(a).val().Volume();assert v<1e-5,(name,v);r['unchanged'][name]=v
    print('unchanged parts confirmed',flush=True)
    r['full']=check_parts(p,contents=True)
    print('full case checks passed',flush=True)
    rows=[]
    for angle in range(0,91,5):
     c=face_pose(p,angle)
     for name in ('body','cap','pivot_axle','pivot_nut'):rows.append(clear(c,p[name],'Cover turn clears '+name))
     rows.append(clear(c,rotor_pose(p,angle),'Common turn keeps keys in pockets'))
    for lift in (0,1.5,5,30,95):rows.append(clear(face_pose(p,90),p['cap'].translate((0,0,lift)),'Unlocked withdrawal'))
    for distance in (0,.2,.5,1.,1.6,3.,6.):rows.append(clear(p['facecap'].translate((0,-distance,0)),p['rotor'],'Axial key insertion'))
    r['clearances']=rows
    r['key_obstructions']=[]
    for separation in (0.,.7):
     for angle in (-2.,2.):
      v=face_pose(p,angle).translate((0,-separation,0)).intersect(p['rotor']).val().Volume();assert v>1e-5,(separation,angle,v);r['key_obstructions'].append(v)
    for angle in (-2.,2.):
     bare=p['facecap_without_keys'].rotate((0,0,p['dimensions'].pivot),(0,1,p['dimensions'].pivot),angle)
     clear(bare,p['rotor'],'Key-removed negative control')
    spring=p['rotor'].cut(p['rotor_rigid']);r['spring']=[]
    from math import sin,cos,radians
    for angle in range(0,360,30):r['spring'].append(clear(p['facecap'],spring.translate((.35*cos(radians(angle)),0,.35*sin(radians(angle)))),'Translated spring envelope'))
    print('cap motion and coupling passed',flush=True)
    s=printed_axle();n=printed_nut();r['thread_motion']=[]
    for angle in range(-360,1,30):
     moved=s.rotate((0,0,0),(0,0,1),angle).translate((0,0,PITCH*angle/360))
     v=moved.intersect(n).val().Volume();assert v<1e-5,(angle,v);r['thread_motion'].append(v)
    # Withdrawal is negative Z. Positive insertion ends at the body shoulder.
    for shift in (-.5,):
     v=s.translate((0,0,shift)).intersect(n).val().Volume();assert v>.01,(shift,v)
    core=cq.Workplane('XY',origin=(0,0,4.2)).circle(ROOT_RADIUS-.02).extrude(TIP-4.2-.01)
    r['solid_core']=material(s,core,'Solid full thread core')
    print('thread fit and solid core passed',flush=True)
    root=Path(__file__).resolve().parent;names=['rotary_matte_design.py','rotary_matte_repair.py','rotary_matte_checks.py','rotary_covered_design.py','rotary_refinement_checks.py','rotary_printed_fastener_design.py','rotary_conical_design.py']
    r['source_sha256']={name:hashlib.sha256((root/name).read_bytes()).hexdigest() for name in names}
    out=root/'notes/matte_rotary';out.mkdir(exist_ok=True);(out/'cad.json').write_text(json.dumps(r,indent=2)+'\n')


if __name__=='__main__':
    main()
