"""Geometric checks for the five-digit revision; evaluate using CadQuery MCP."""
import sys, json, math, importlib, hashlib
from pathlib import Path
HERE=Path(globals().get('__file__','/home/hevar/git/vibe-modelling-3d/model/glove_drying_insert/verify.py')).resolve().parent
sys.path.insert(0,str(HERE))
import glove_drying_insert as m
importlib.reload(m)
parts=m.print_parts()
report={'design':'five-digit folding hand skeleton','parts':[{'solids':len(p.solids().vals()),'valid':p.val().isValid(),'volume':p.val().Volume()} for p in parts]}
(HERE/'notes/geometry_checks.json').write_text(json.dumps(report,indent=2)+'\n')
assert all(d['valid'] and d['solids']==1 for d in report['parts']), "See notes/geometry_checks.json"
report['motion']=[]
for angle in (0,.5,1,1.7,3,5):
    a,b,p=m.assembled(angle,False)
    d={'half_angle':angle,'frame_collision':a.intersect(b).val().Volume(),'axle_collision':sum(f.intersect(p).val().Volume() for f in (a,b))}
    report['motion'].append(d)
    (HERE/'notes/geometry_checks.json').write_text(json.dumps(report,indent=2)+'\n')
    assert d['frame_collision']<1e-6 and d['axle_collision']<1e-6, "See notes/geometry_checks.json"

a,b,p,s=m.assembled()
report['brace_seated_collision']=[s.intersect(f).val().Volume() for f in (a,b)]
report['brace_pullout_contact']=[s.translate((0,-2,0)).intersect(f).val().Volume() for f in (a,b)]
report['brace_closing_contact']=sum(s.intersect(f).val().Volume() for f in m.placed_frames(0))
report['pin_pullout_contact']=p.translate((-2,0,0)).intersect(a).val().Volume()
(HERE/'notes/geometry_checks.json').write_text(json.dumps(report,indent=2)+'\n')
assert max(report['brace_seated_collision'])<1e-6, "See notes/geometry_checks.json"
(HERE/'notes/geometry_checks.json').write_text(json.dumps(report,indent=2)+'\n')
assert min(report['brace_pullout_contact'])>0 and report['brace_closing_contact']>0 and report['pin_pullout_contact']>0, "See notes/geometry_checks.json"
# Physical elastic forces remain untested; check room for the compressed barb.
barbs=m.axle().intersect(m.box(1,20,10,(m.HINGE_HALF_WIDTH+1.5,0,0)))
u=barbs.intersect(m.box(100,10,10,(0,5,0))).translate((0,-.5,0))
l=barbs.intersect(m.box(100,10,10,(0,-5,0))).translate((0,.5,0))
bore=m.cq.Workplane('YZ',origin=(-50,0,1.7)).circle(m.BORE_RADIUS).extrude(100)
report['compressed_barb_outside_bore']=u.union(l).cut(bore).val().Volume()
(HERE/'notes/geometry_checks.json').write_text(json.dumps(report,indent=2)+'\n')
assert report['compressed_barb_outside_bore']<1e-6, "See notes/geometry_checks.json"
# Each branch must reach a distinct finger and contain an empty long-slot probe.
report['digits']={}
t=math.radians(m.OPEN_HALF_ANGLE)
flat=m.frame(True)
for name,(root,tip,width) in m.digit_dimensions().items():
    point=tuple(root[i]+.8*(tip[i]-root[i]) for i in (0,1))
    probe=m.cq.Workplane('XY').center(*point).circle(.8).extrude(m.THICKNESS)
    slot_collision=flat.intersect(probe).val().Volume()
    report['digits'][name]={'root_mm':root,'tip_center_mm':tip,'width_mm':width,'slot_width_mm':width-2*m.FINGER_RAIL,
        'tip_clear_air_gap_mm':2*((m.HINGE_RADIUS-m.THICKNESS)*math.cos(t)+tip[1]*math.sin(t)),
        'slot_probe_collision':slot_collision}
    (HERE/'notes/geometry_checks.json').write_text(json.dumps(report,indent=2)+'\n')
    assert slot_collision<1e-6, "See notes/geometry_checks.json"
# A longer/wider hand and reduced opening check meaningful independent fit edits.
m.HAND_SCALE=1.04;m.FINGER_LENGTH_SCALE=1.05;m.OPEN_HALF_ANGLE=.7
variant=m.print_parts();va,vb,vp,vs=m.assembled()
report['variant']={'hand_scale':1.04,'finger_length_scale':1.05,'half_angle':.7,
    'valid':all(v.val().isValid() and len(v.solids().vals())==1 for v in variant),
    'brace_collision':sum(vs.intersect(f).val().Volume() for f in (va,vb))}
(HERE/'notes/geometry_checks.json').write_text(json.dumps(report,indent=2)+'\n')
assert report['variant']['valid'] and report['variant']['brace_collision']<1e-6, "See notes/geometry_checks.json"
importlib.reload(m)
report['source_sha256']=hashlib.sha256((HERE/'glove_drying_insert.py').read_bytes()).hexdigest()
(HERE/'notes/geometry_checks.json').write_text(json.dumps(report,indent=2)+'\n')
result=m.compound(m.print_parts())
