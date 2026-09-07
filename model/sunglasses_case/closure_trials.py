"""Small closure experiments; evaluate with CadQuery MCP. Millimetres.

Independent from the production case. Each file contains a complete captive
hinge plus loop latch. STEP and STL share the open print pose. No supports.
"""
from pathlib import Path
import json
import cadquery as cq

WIDTH = 60.0
DEPTH = 40.0
SEAM = 30.0
WALL = 3.0
FLOOR = 2.4
HINGE_RADIUS = 5.6
CONE_GAP = 0.20
EAR_GAP = 0.20
HINGE_SPACING = 36.0
LEAF_THICKNESS = 1.8
VIEW = "print"  # print / closed / section
SELECT = "C_located_loop_2p6"
EXPORT = True
ROOT = Path(globals().get("__file__", "/home/hevar/git/vibe-modelling-3d/model/sunglasses_case/closure_trials.py")).resolve().parent
HY = DEPTH/2 + HINGE_RADIUS*2**0.5 + 0.8
VARIANTS = {"A_twin_hinge_loop_1p8": (1.8, False),
            "B_twin_hinge_loop_2p6": (2.6, False),
            "C_located_loop_2p6": (2.6, True)}

def box(x,y,z,dx,dy,dz):
    return cq.Workplane("XY").box(dx,dy,dz).translate((x,y,z))

def yz(x, points, width):
    return cq.Workplane("YZ", origin=(x,0,0)).polyline(points).close().extrude(width)

def cup():
    outer = cq.Workplane("XY").box(WIDTH,DEPTH,SEAM,centered=(True,True,False)).edges("|Z").fillet(4)
    outer = outer.edges("<Z").chamfer(0.8)
    inner = cq.Workplane("XY").box(WIDTH-2*WALL,DEPTH-2*WALL,SEAM,centered=(True,True,False)).edges("|Z").fillet(1)
    return outer.cut(inner.translate((0,0,FLOOR))).edges(">Z").chamfer(0.3)

def ear(x0,x1,moving=False):
    r=HINGE_RADIUS; t=r/2**0.5
    wall_y=HY+(1 if moving else -1)*(r*2**0.5+1.8)
    barrel=(cq.Workplane("YZ",origin=(x0,HY,SEAM)).moveTo(0,-r*2**0.5)
            .lineTo(t,-t).threePointArc((r,0),(0,r)).threePointArc((-r,0),(-t,-t)).close().extrude(x1-x0))
    barrel=barrel.edges(cq.selectors.NearestToPointSelector(((x0+x1)/2,HY,SEAM-r*2**0.5))).fillet(0.8)
    web=yz(x0,[(wall_y,SEAM-r*2**0.5-abs(wall_y-HY)),(HY,SEAM-r*2**0.5),(HY,SEAM),(wall_y,SEAM)],x1-x0)
    return barrel.union(web)

def cone(x,r,d):
    return cq.Workplane(obj=cq.Solid.makeCone(r,0.12,r-0.12,cq.Vector(x,HY,SEAM),cq.Vector(d,0,0)))

def hinge(c):
    fixed=ear(c-10,c-4.5).union(ear(c+4.5,c+10))
    fixed=fixed.union(cone(c-4.5,3.5,1)).union(cone(c+4.5,3.5,-1))
    moving=ear(c-4.5+EAR_GAP,c+4.5-EAR_GAP,True)
    moving=moving.cut(cone(c-4.5,3.5+CONE_GAP,1)).cut(cone(c+4.5,3.5+CONE_GAP,-1))
    return fixed,moving

def loop_latch():
    front=2*HY+DEPTH/2
    inner=front+0.8; outer=inner+LEAF_THICKNESS
    latch=None
    # Two long leaves leave an open window for the fixed catch. Root ramps
    # start on the wall; upper rail bridges the 12 mm window between leaves.
    for x in (-7.5,7.5):
        root=yz(x-1.5,[(front-0.6,SEAM-24),(outer,SEAM-20.8),
                      (outer,SEAM-18.5),(front-0.6,SEAM-18.5)],3)
        leaf=box(x,(inner+outer)/2,(SEAM-20.8+SEAM+9)/2,3,LEAF_THICKNESS,29.8)
        leaf=leaf.edges("|Z").fillet(0.25)
        part=root.union(leaf)
        latch=part if latch is None else latch.union(part)
    rail=box(0,(inner+outer)/2,SEAM+7.5,18,LEAF_THICKNESS,3)
    # 0.4 mm finger ledge grows on a short 45-degree ramp.
    grip=yz(-6,[(outer-0.2,SEAM+7),(outer+0.8,SEAM+8),
                (outer+0.8,SEAM+9),(outer-0.2,SEAM+9)],12)
    return latch.union(rail).union(grip)

def catch(overlap):
    front=-DEPTH/2; reach=overlap+0.8; bottom=SEAM-5.6
    # Flat underside retains the loop's rail. Top ramp helps closing.
    beam=yz(-5,[(front+0.3,bottom),(front-reach,bottom),
                (front-reach,bottom+1.6),(front+0.3,bottom+reach+1.9)],10)
    # Buttress stops before the loop's inner face, preserving its release
    # path. The remaining overlap projects beyond it; inspect sliced paths.
    beam=beam.union(yz(-5,[(front+0.3,bottom-1),(front-0.7,bottom),
                          (front+0.3,bottom)],10))
    return beam

def close(part,angle=180):
    return part.rotate((0,HY,SEAM),(1,HY,SEAM),angle)

def build(overlap,located,label):
    fixed=cup(); moving=cup().translate((0,2*HY,0))
    for c in (-HINGE_SPACING/2,HINGE_SPACING/2):
        a,b=hinge(c); fixed=fixed.union(a); moving=moving.union(b)
    keeper=catch(overlap); latch=loop_latch()
    fixed=fixed.union(keeper); moving=moving.union(latch)
    fixed=fixed.union(cq.Workplane("XY",origin=(0,0,FLOOR)).text(label,7,0.6,combine=False))
    if located:
        # Internal side tabs extend above the seam into the lid cavity.
        # 0.20 mm clearance to the straight inner side wall, chamfered entry.
        for side in (-1,1):
            tab=box(side*(WIDTH/2-WALL-1.2),-8,SEAM,2,12,5)
            tab=tab.edges(">Z").chamfer(0.6)
            foot=box(side*(WIDTH/2-WALL-0.6),-8,SEAM-2.5,2.4,12,2)
            fixed=fixed.union(tab).union(foot)
    assert len(fixed.solids().vals())==len(moving.solids().vals())==1
    assert fixed.val().isValid() and moving.val().isValid()
    assert fixed.intersect(moving).val().Volume()<1e-5
    collision=fixed.intersect(close(moving)).val().Volume()
    assert collision<1e-5, f'closed collision {overlap} {located} {collision}'
    # With latch held outward, check hinge/cup sweep independently of snap flex.
    shell=moving.cut(latch)
    for angle in range(0,181,5):
        assert fixed.intersect(close(shell,angle)).val().Volume()<0.001, f'shell sweep {angle}'
    # Locked opening must hit the keeper; a hand-released loop must clear it.
    locked=close(latch)
    assert keeper.intersect(locked.translate((0,0,0.8))).val().Volume()>0.01, 'no positive retention'
    released=locked.translate((0,-overlap-0.4,0))
    for lift in (0.8,2,4,7):
        assert keeper.intersect(released.translate((0,0,lift))).val().Volume()<0.001
    for part in (fixed,moving):
        assert abs(part.val().BoundingBox().zmin)<0.02
    return fixed,moving

summaries={}
def first_tilt_contact(centres):
    pairs=[hinge(c) for c in centres]
    a=cq.Workplane(obj=cq.Compound.makeCompound([p[0].val() for p in pairs]))
    b=cq.Workplane(obj=cq.Compound.makeCompound([p[1].val() for p in pairs]))
    for tenth in range(1,51):
        angle=tenth/10
        tilted=b.rotate((0,HY,SEAM),(0,HY+1,SEAM),angle)
        if a.intersect(tilted).val().Volume()>0.001:
            return angle
    return None

tilt={'single_joint_first_contact_deg':first_tilt_contact([0]),
      'twin_joint_first_contact_deg':first_tilt_contact([-HINGE_SPACING/2,HINGE_SPACING/2]),
      'scope':'Rigid CAD tilt about Y through hinge midpoint; 0.1 degree steps, not print measurement.'}
for name,(overlap,located) in VARIANTS.items():
    fixed,moving=build(overlap,located,name[0])
    layout=cq.Compound.makeCompound([fixed.val(),moving.val()])
    bb=layout.BoundingBox()
    assert bb.xlen<260 and bb.ylen<260 and bb.zlen<250
    summaries[name]={'overlap_mm':overlap,'hinge_spacing_mm':HINGE_SPACING,
                     'radial_cone_gap_mm':CONE_GAP,'axial_ear_gap_mm':EAR_GAP,
                     'locating_tabs':located,'volume_mm3':layout.Volume(),
                     'bounds_mm':[bb.xlen,bb.ylen,bb.zlen]}
    summaries[name]['tilt_comparison']=tilt
    if EXPORT:
        cq.exporters.export(layout,str(ROOT/(name+'.stl')),tolerance=0.025,angularTolerance=0.1)
        cq.exporters.export(layout,str(ROOT/(name+'.step')))
    if name==SELECT:
        result=layout if VIEW=='print' else cq.Compound.makeCompound([fixed.val(),close(moving).val()])
        if VIEW=='section':
            result=cq.Workplane(obj=result).intersect(box(0,-DEPTH/2,SEAM,2,30,50))
if EXPORT:
    (ROOT/'notes'/'closure_trials_metrics.json').write_text(json.dumps(summaries,indent=2)+'\n')
