"""Captured rail trials only; X across seam, Y insertion, Z plate thickness."""
from dataclasses import dataclass,replace,asdict
from pathlib import Path
import hashlib,json
import cadquery as cq
ROOT=Path(__file__).resolve().parent
VARIANTS={'A':'compact_6mm','B':'deep_9mm'}
@dataclass(frozen=True)
class Parameters:
    thickness:float=10
    height:float=52
    left_grip:float=32
    right_grip:float=15
    depth:float=6
    head:float=4
    neck:float=3
    clearance:float=.12
    rail_start:float=6
    rail_end:float=48
    leaf_root:float=-26
    leaf_width:float=10
    leaf_thickness:float=1.6
    leaf_y:float=27
    hook_tip:float=2.1
    release:float=1.3
P=Parameters()
def params(letter):return replace(P,depth=6 if letter=='A' else 9)
def box(x0,x1,y0,y1,z0,z1):
    return cq.Workplane('XY').box(x1-x0,y1-y0,z1-z0).translate(((x0+x1)/2,(y0+y1)/2,(z0+z1)/2))
def profile(p):
    lo=(p.thickness-p.neck)/2; hi=p.thickness-lo
    rise=(p.head-p.neck)/2
    return [(-1,lo),(2,lo),(2+rise,lo-rise),(p.depth,lo-rise),
            (p.depth,hi+rise),(2+rise,hi+rise),(2,hi),(-1,hi)]
def leaf(p,retracted=False):
    lo=(p.thickness-p.leaf_thickness)/2-.5
    beam=box(p.leaf_root-.5,p.depth,p.leaf_y-p.leaf_width/2,p.leaf_y+p.leaf_width/2,lo,lo+p.leaf_thickness).edges('|X').fillet(.3)
    points=[(p.leaf_y-4,lo),(p.leaf_y-4,3.6),(p.leaf_y,p.hook_tip),(p.leaf_y+3,p.hook_tip),(p.leaf_y+3,lo+.1)]
    hook=cq.Workplane('YZ',origin=(1,0,0)).polyline(points).close().extrude(p.depth-1)
    ramp=cq.Workplane('XZ',origin=(0,p.leaf_y+6,0)).polyline([(1,lo),(1,lo+1),(p.depth,lo+1),(p.depth,p.hook_tip),(1+lo-p.hook_tip,p.hook_tip)]).close().extrude(12)
    s=beam.union(hook.intersect(ramp))
    return s.translate((0,0,p.release if retracted else 0))
def parts(letter,retracted=False,labels=True,p=None):
    p=p or params(letter)
    assert p.depth>=5 and p.thickness>p.head+2*p.clearance
    a=box(-p.left_grip,0,0,p.height,0,p.thickness).edges('|X').fillet(1.5).faces('<X').edges().chamfer(.6)
    b=box(0,p.right_grip,0,p.height,0,p.thickness).edges('|X').fillet(1.5).faces('>X').edges().chamfer(.6)
    rail=cq.Workplane('XZ',origin=(0,p.rail_end,0)).polyline(profile(p)).close().extrude(p.rail_end-p.rail_start).edges('|Y').fillet(.2)
    channel=cq.Workplane('XZ',origin=(0,p.height+1,0)).polyline(profile(p)).close().offset2D(p.clearance).extrude(p.height+1-p.rail_start)
    a=a.union(rail)
    relief=box(p.leaf_root,p.depth+1,p.leaf_y-p.leaf_width/2-1,p.leaf_y+p.leaf_width/2+1,1,p.thickness-1)
    a=a.cut(relief).union(leaf(p,retracted))
    pocket=box(1,p.depth+.3,p.leaf_y-4.3,p.leaf_y+3.15,-1,3.6)
    mouth=box(.5,p.depth+.8,p.leaf_y-4.8,p.leaf_y+3.65,-1,.5).edges('|Z').fillet(.45).faces('>Z').edges().chamfer(.3)
    b=b.cut(channel).cut(pocket.union(mouth))
    if labels:
        for x,side in [(-p.left_grip+5,0),(p.right_grip-3,1)]:
            mark=cq.Workplane('XY',origin=(x,10,p.thickness-.4)).text(letter,4,.8)
            if side==0:a=a.cut(mark)
            else:b=b.cut(mark)
    return a,b

def bed(s):
    bb=s.val().BoundingBox();return s.translate((-bb.xmin,-bb.ymin,-bb.zmin))
def layout(a,b):
    a=bed(a.rotate((0,0,0),(0,1,0),-90))
    b=bed(b.rotate((0,0,0),(0,1,0),90)).translate((22,0,0))
    return cq.Compound.makeCompound([a.val(),b.val()])
def overlap(a,b):return a.val().intersect(b.val()).Volume()
def run():
    report={}
    for letter,name in VARIANTS.items():
        p=params(letter);a,b=parts(letter)
        assert all(s.val().isValid() and len(s.solids().vals())==1 for s in [a,b])
        assert overlap(a,b)<1e-5
        r,_=parts(letter,retracted=True)
        assert overlap(a.translate((0,10,0)),b)>.01
        for released in [False,True]:
            bounds=leaf(p,released).val().BoundingBox()
            assert bounds.zmin>=0 and bounds.zmax<=p.thickness
        sweep={}
        for dy in [0,.2,.5,1,2,4,8,12,20,32,46,48]:
            v=overlap(r.translate((0,dy,0)),b);assert v<1e-5,(letter,dy,v)
            sweep[str(dy)]=v
        blocked={}
        for key,offset in [('pull_apart',(-.7,0,0)),('reverse_slide',(0,.5,0)),('end_stop',(0,-.3,0)),('front',(0,0,.4)),('rear',(0,0,-.4))]:
            v=overlap(a.translate(offset),b);assert v>.01,(letter,key,v);blocked[key]=v
        # Bending tested with spring deleted so the catch cannot fake structural capture.
        structural=a.cut(box(p.leaf_root,p.depth+1,p.leaf_y-6,p.leaf_y+6,-1,11)).intersect(box(.05,p.depth+1,0,p.height,0,p.thickness))
        rotations={}
        for axis in [(0,1,0),(1,0,0),(0,0,1)]:
            origin=(0,p.height/2,p.thickness/2)
            end=tuple(origin[i]+axis[i] for i in range(3))
            for angle in [-5,5]:
                v=overlap(structural.rotate(origin,end,angle),b)
                assert v>.01,(letter,axis,angle,v)
                rotations[f'{axis}:{angle}']=v
        # Bending take-up angle around seam (rigid bodies; not elastic stiffness).
        takeup={}
        for sign in [-1,1]:
            lo,hi=0,5
            for _ in range(16):
                mid=(lo+hi)/2
                moved=structural.rotate((0,26,5),(0,27,5),sign*mid)
                if overlap(moved,b)>1e-7:hi=mid
                else:lo=mid
            takeup[str(sign)]=hi
        s=layout(a,b);bb=s.BoundingBox()
        stem=f'{letter}_{name}'
        for ext in ['step','stl']:
            cq.exporters.export(s,str(ROOT/f'{stem}.{ext}'),**({'tolerance':.015,'angularTolerance':.08} if ext=='stl' else {}))
        cq.exporters.export(cq.Compound.makeCompound([a.val(),b.val()]),str(ROOT/f'{stem}_assembled.step'))
        width=p.rail_end-p.rail_start-(p.leaf_width+2)
        skin=(p.thickness-p.head)/2-p.clearance
        moment=100 # 5 N at a 20 mm arm: comparison, not a rating
        reaction=moment/(p.depth-1)
        report[letter]={'parameters':asdict(p),'print_size_mm':[bb.xlen,bb.ylen,bb.zlen],
          'released_slide_intersection_mm3':sweep,'locked_translation_intersection_mm3':blocked,
          'rotation_without_catch_intersection_mm3':rotations,'first_bending_contact_degrees':takeup,
          'screen':{'moment_Nmm':moment,'effective_rail_width_mm':width,'socket_skin_mm':skin,
            'tongue_root_stress_MPa':moment/(width*p.neck**2/6),
            'socket_wall_stress_MPa':6*reaction*(p.depth+p.clearance)/(width*skin**2),
            'socket_wall_deflection_mm_at_E800':reaction*(p.depth+p.clearance)**3/(3*800*(width*skin**3/12)),
            'release_strain':3*p.leaf_thickness*p.release/(2*(p.depth-p.leaf_root-3)**2)},
          'limits':'Rigid sampled motion and ideal solid-beam screens, no printed strength or stiffness rating.'}
    alt=replace(params('A'),height=56,clearance=.16)
    a,b=parts('A',p=alt);assert a.val().isValid() and b.val().isValid() and overlap(a,b)<1e-5
    report['alternate_build']='Height 56 mm, clearance .16 mm: valid and no assembled overlap.'
    report['source_sha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    (ROOT/'notes/geometry_checks.json').write_text(json.dumps(report,indent=2)+'\n')
    return layout(*parts('A'))
