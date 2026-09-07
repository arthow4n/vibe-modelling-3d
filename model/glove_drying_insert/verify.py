import sys, json
from pathlib import Path
sys.path.insert(0,str(Path(globals().get('__file__','/home/hevar/git/vibe-modelling-3d/model/glove_drying_insert/verify.py')).resolve().parent))
import glove_drying_insert as m
import importlib
importlib.reload(m)
parts=m.print_parts()
report={'parts':[{'solids':len(p.solids().vals()),'valid':p.val().isValid(),'volume':p.val().Volume()} for p in parts]}
report['motion']=[]
for angle in (0,3,6,11,15,25,45):
    a,b,p=m.assembled(angle,False)
    report['motion'].append({'angle':angle,'frame_collision':a.intersect(b).val().Volume(),'axle_collision':a.intersect(p).val().Volume()+b.intersect(p).val().Volume()})
a,b,p,s=m.assembled()
report['spreader_collision']=[s.intersect(f).val().Volume() for f in (a,b)]
report['spreader_pullout_collision']=[s.translate((0,-2,0)).intersect(f).val().Volume() for f in (a,b)]
# Conservative circular bore: compressed barb cross-section must pass without
# the two arms touching each other. This establishes room, not elastic stress.
barbs=m.axle().intersect(m.box(1,20,10,(m.HINGE_HALF_WIDTH+1.5,0,0)))
upper=barbs.intersect(m.box(100,10,10,(0,5,0))).translate((0,-.5,0))
lower=barbs.intersect(m.box(100,10,10,(0,-5,0))).translate((0,.5,0))
bore=m.cq.Workplane('YZ',origin=(-50,0,1.7)).circle(m.BORE_RADIUS).extrude(100)
report['compressed_barb_outside_bore']=upper.union(lower).cut(bore).val().Volume()
assert report['compressed_barb_outside_bore']<1e-6
report['pin_pullout_collision']=p.translate((-2,0,0)).intersect(a).val().Volume()
report['brace_compression_collision']=sum(s.intersect(f).val().Volume() for f in m.placed_frames(m.OPEN_HALF_ANGLE-1))
(m.HERE/'notes/geometry_checks.json').write_text(json.dumps(report,indent=2))
assert all(d['valid'] and d['solids']==1 for d in report['parts'])
assert all(d['frame_collision']<1e-6 and d['axle_collision']<1e-6 for d in report['motion'])
assert max(report['spreader_collision'])<1e-6
assert min(report['spreader_pullout_collision'])>0
assert report['pin_pullout_collision']>0 and report['brace_compression_collision']>0
# One meaningful larger fit setting; hardware remains unchanged.
saved=(m.FRAME_LENGTH,m.CUFF_WIDTH,m.PALM_WIDTH)
m.FRAME_LENGTH,m.CUFF_WIDTH,m.PALM_WIDTH=135.,68.,48.
variant=m.print_parts()
va,vb,vp,vs=m.assembled()
report['larger_variant']={'length':135,'width':68,'valid':all(v.val().isValid() and len(v.solids().vals())==1 for v in variant),
    'frame_collision':va.intersect(vb).val().Volume(),'spreader_collision':sum(vs.intersect(f).val().Volume() for f in (va,vb))}
assert report['larger_variant']['valid'] and report['larger_variant']['spreader_collision']<1e-6
m.FRAME_LENGTH,m.CUFF_WIDTH,m.PALM_WIDTH=saved
import hashlib
report['source_sha256']=hashlib.sha256((m.HERE/'glove_drying_insert.py').read_bytes()).hexdigest()
(m.HERE/'notes/geometry_checks.json').write_text(json.dumps(report,indent=2))
result=m.compound(parts)
