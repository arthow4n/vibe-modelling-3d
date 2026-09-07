"""D/E: open-frame hinge/loop fixtures with a side-printed keeper insert.

All dimensions mm. Evaluate this file through CadQuery MCP. The original case
and A/B/C source remain unchanged. Hinge construction reproduces closure_trials.py
at 578bc5d; both bearing positions and clearances remain the accepted baseline.
"""
from pathlib import Path
import math
import json
import cadquery as cq

WIDTH, DEPTH, SEAM = 60.0, 40.0, 30.0
WALL, FLOOR = 3.0, 2.4
HINGE_RADIUS, HINGE_SPACING = 5.6, 36.0
CONE_GAP, EAR_GAP = 0.20, 0.20
LOOP_WIDTH, LEAF_WIDTH = 18.0, 3.0
LOOP_WALL_GAP = 3.9  # clears the insert receiver's 3.5 mm outer face
RELEASE_TRAVEL = 3.20
SEATED_GAP = 0.20  # vertical clearance, not preload
RETAINING_ANGLE = 0.0  # flat shoulder; reverse rake obstructed intentional release
KEY_ENTRY_CLEARANCE = 0.16  # leading end, coordinate allowance in r and z
KEY_SEATED_CLEARANCE = -0.04  # trailing end: slight intentional wedge interference
RAIL_HEIGHT = 3.0
VIEW = 'print'  # print / closed / section
SELECT = 'D_firm_side_printed_keeper'
EXPORT = True
ROOT = Path(globals().get('__file__', '/home/hevar/git/vibe-modelling-3d/model/sunglasses_case/keeper_latch_trials.py')).resolve().parent
HY = DEPTH/2 + HINGE_RADIUS*math.sqrt(2) + 0.8
SLOPE = math.tan(math.radians(RETAINING_ANGLE))
REACH = LOOP_WALL_GAP + RELEASE_TRAVEL
VARIANTS = {'D_firm_side_printed_keeper': 2.2, 'E_extra_firm_side_printed_keeper': 2.8}

def box(x,y,z,dx,dy,dz):
    return cq.Workplane('XY').box(dx,dy,dz).translate((x,y,z))

def yz(x, points, width):
    return cq.Workplane('YZ', origin=(x,0,0)).polyline(points).close().extrude(width)

def ear(x0,x1,moving=False):
    r=HINGE_RADIUS; t=r/math.sqrt(2)
    wall_y=HY+(1 if moving else -1)*(r*math.sqrt(2)+1.8)
    barrel=(cq.Workplane('YZ',origin=(x0,HY,SEAM)).moveTo(0,-r*math.sqrt(2))
            .lineTo(t,-t).threePointArc((r,0),(0,r)).threePointArc((-r,0),(-t,-t)).close().extrude(x1-x0))
    barrel=barrel.edges(cq.selectors.NearestToPointSelector(((x0+x1)/2,HY,SEAM-r*math.sqrt(2)))).fillet(0.8)
    web=yz(x0,[(wall_y,SEAM-r*math.sqrt(2)-abs(wall_y-HY)),(HY,SEAM-r*math.sqrt(2)),(HY,SEAM),(wall_y,SEAM)],x1-x0)
    return barrel.union(web)

def cone(x,r,d):
    return cq.Workplane(obj=cq.Solid.makeCone(r,0.12,r-0.12,cq.Vector(x,HY,SEAM),cq.Vector(d,0,0)))

def hinge(c):
    fixed=ear(c-10,c-4.5).union(ear(c+4.5,c+10))
    fixed=fixed.union(cone(c-4.5,3.5,1)).union(cone(c+4.5,3.5,-1))
    moving=ear(c-4.5+EAR_GAP,c+4.5-EAR_GAP,True)
    moving=moving.cut(cone(c-4.5,3.5+CONE_GAP,1)).cut(cone(c+4.5,3.5+CONE_GAP,-1))
    return fixed,moving

def frame():
    # Bed ring and central spine; no floor panel or tall side walls.
    outside=box(0,0,FLOOR/2,WIDTH,DEPTH,FLOOR).edges('|Z').fillet(3)
    inside=box(0,0,FLOOR/2,WIDTH-6,DEPTH-6,FLOOR+2).edges('|Z').fillet(1)
    base=outside.cut(inside).union(box(0,0,FLOOR/2,8,DEPTH,FLOOR))
    front=box(0,-DEPTH/2+WALL/2,SEAM/2,22,WALL,SEAM).edges('|Z').fillet(0.5)
    base=base.union(front)
    for c in (-HINGE_SPACING/2,HINGE_SPACING/2):
        base=base.union(box(c,DEPTH/2-WALL/2,SEAM/2,20,WALL,SEAM))
        base=base.union(yz(c-1.2,[(7,FLOOR),(17,FLOOR),(17,24)],2.4))
    for x in (-8,8):
        base=base.union(yz(x-1.2,[(-17,FLOOR),(-3,FLOOR),(-17,24)],2.4))
    return base

def keeper_bottom(r):
    return SEAM-6 + SEATED_GAP - SLOPE*(r-LOOP_WALL_GAP)

def outward_profile(x,points,w):
    return yz(x,[(-DEPTH/2-r,z) for r,z in points],w)

def receiver():
    # Side-entry diamond keyway, with a 45-degree upward exit slit.
    # The diamond roof and slit roof grow inward on preceding layers.
    boss=outward_profile(-5.5,[(-0.3,19),(3.5,22.8),(3.5,30),(-0.3,30)],12)
    diamond=outward_profile(-5.6,[(0.6,25),(1.8,23.2),(3.0,25),(1.8,26.8)],11.3)
    slit=outward_profile(-5.6,[(1.8,24.3),(3.6,26.1),(3.6,27.5),(1.8,25.7)],11.3)
    return boss.cut(diamond.union(slit))

def keeper():
    # Print this part on its X end: the functional YZ tooth outline is a
    # supported perimeter in every layer, rather than a downward overhang.
    def key_points(gap):
        return [(-DEPTH/2-r,z) for r,z in
                [(0.6+gap,25),(1.8,23.2+gap),(3.0-gap,25),(1.8,26.8-gap)]]
    # A slight wedge grips against sideways withdrawal; the leading end
    # has clearance. Tiny interference is intentional, pending physical fit.
    key=(cq.Workplane('YZ',origin=(-5.5,0,0)).polyline(key_points(KEY_SEATED_CLEARANCE)).close()
         .workplane(offset=11).polyline(key_points(KEY_ENTRY_CLEARANCE)).close().loft(ruled=True))
    neck=outward_profile(-5.5,[(1.8,24.5),(3.8,26.5),(3.8,27.5),(1.8,25.5)],11)
    tooth=outward_profile(-5.5,[(3.5,keeper_bottom(3.5)),(REACH,keeper_bottom(REACH)),
                             (REACH,25.8),(3.5,29.4)],11)
    # Constant full profile reaches the bed: no tooth appears in midair.
    return key.union(neck).union(tooth)

def keeper_print(part):
    # X=-5.5 is the bed-facing end of the complete tooth/key outline.
    posed=part.rotate((0,0,0),(0,1,0),-90)
    # Analytical placement avoids depending on loose B-spline bounding boxes.
    return posed.translate((73.4,22.1,5.5))

def loop(thickness):
    front=2*HY+DEPTH/2
    inner=LOOP_WALL_GAP; outer=inner+thickness
    def outward_profile(x,points,w):
        return yz(x,[(front+r,z) for r,z in points],w)
    # The retaining rail bridges the 12 mm gap between its two side leaves.
    def rail_z(r):
        return 2*SEAM-keeper_bottom(r)+SEATED_GAP
    latch=None
    for x in (-LOOP_WIDTH/2,LOOP_WIDTH/2-LEAF_WIDTH):
        root=outward_profile(x,[(-0.6,1.5),(outer,1.5+outer+0.6),
                                (outer,SEAM-18.5),(-0.6,SEAM-18.5)],LEAF_WIDTH)
        leaf=outward_profile(x,[(inner,SEAM-20),(outer,SEAM-20),
                               (outer,rail_z(outer)+RAIL_HEIGHT),
                               (inner,rail_z(inner)+RAIL_HEIGHT)],LEAF_WIDTH)
        part=root.union(leaf)
        part=part.edges(cq.selectors.NearestToPointSelector(
            (x+LEAF_WIDTH/2,front+inner,SEAM-18.5))).fillet(0.8)
        latch=part if latch is None else latch.union(part)
    rail=outward_profile(-LOOP_WIDTH/2,[(inner,rail_z(inner)),(outer,rail_z(outer)),
                          (outer,rail_z(outer)+RAIL_HEIGHT),(inner,rail_z(inner)+RAIL_HEIGHT)],LOOP_WIDTH)
    # Finger ledge grows at 45 degrees; keep retaining edges deliberately sharp.
    grip=outward_profile(-4,[(outer-0.1,rail_z(outer)+1),(outer+0.8,rail_z(outer)+1.9),
                             (outer+0.8,rail_z(outer)+2.8),(outer-0.1,rail_z(outer)+2.8)],8)
    return latch.union(rail).union(grip)

def close(part,angle=180):
    return part.rotate((0,HY,SEAM),(1,HY,SEAM),angle)

def build(thickness,label):
    fixed=frame(); moving=frame().rotate((0,0,0),(0,0,1),180).translate((0,2*HY,0))
    for c in (-HINGE_SPACING/2,HINGE_SPACING/2):
        a,b=hinge(c); fixed=fixed.union(a); moving=moving.union(b)
    catch=keeper(); latch=loop(thickness)
    fixed=fixed.union(receiver())
    label_shape=cq.Workplane('XY',origin=(0,0,FLOOR)).text(label,6,0.6,combine=False)
    fixed=fixed.union(label_shape)
    shell=moving
    moving=moving.union(latch)
    for part in (fixed,moving):
        assert len(part.solids().vals())==1 and part.val().isValid(), ('invalid/disconnected',len(part.solids().vals()))
        assert abs(part.val().BoundingBox().zmin)<0.001
    assert fixed.intersect(moving).val().Volume()<0.001, 'print interference'
    assembled_fixed=fixed.union(catch)
    fit_interference=fixed.intersect(catch).val().Volume()
    assert fit_interference<1.0, ('excessive wedge interference',fit_interference)
    assert assembled_fixed.intersect(close(moving)).val().Volume()<0.001, 'closed interference'
    for angle in range(0,181,5):
        assert assembled_fixed.intersect(close(shell,angle)).val().Volume()<0.001, ('shell sweep',angle)
    # Rigid geometry checks, not spring/force simulation. Locked rail must
    # obstruct opening; the flat shoulder permits deliberate outward release.
    locked=close(latch)
    assert catch.intersect(locked.translate((0,0,0.4))).val().Volume()>0.01
    assert catch.intersect(close(latch,179)).val().Volume()>0.01, 'no rotational retention'
    assert fixed.intersect(catch.translate((0,0,0.4))).val().Volume()>1, 'key not vertically captured'
    assert fixed.intersect(catch.translate((0,-0.4,0))).val().Volume()>1, 'key not outwardly captured'
    release_down=RELEASE_TRAVEL*SLOPE
    released=locked.translate((0,-RELEASE_TRAVEL-0.3,-release_down))
    for lift in (0,0.4,2,5,9):
        assert assembled_fixed.intersect(released.translate((0,0,lift))).val().Volume()<0.001, ('released',lift)
    assert catch.val().isValid() and len(catch.solids().vals())==1
    return fixed,moving,catch

metrics={}
for name,thickness in VARIANTS.items():
    fixed,moving,catch=build(thickness,name[0])
    layout=cq.Compound.makeCompound([fixed.val(),moving.val(),keeper_print(catch).val()])
    bb=layout.BoundingBox()
    assert bb.xlen<260 and bb.ylen<260 and bb.zlen<250
    metrics[name]={'loop_thickness_mm':thickness,'keeper_print_orientation':'side, tooth profile parallel to bed',
                   'loop_bridge_span_mm':LOOP_WIDTH-2*LEAF_WIDTH,
                   'release_travel_mm':RELEASE_TRAVEL,'seated_gap_mm':SEATED_GAP,
                   'retaining_angle_deg':RETAINING_ANGLE,'volume_mm3':layout.Volume(),
                   'bounds_mm':[bb.xlen,bb.ylen,bb.zlen]}
    if EXPORT:
        cq.exporters.export(layout,str(ROOT/(name+'.step')))
        cq.exporters.export(layout,str(ROOT/(name+'.stl')),tolerance=0.025,angularTolerance=0.1)
    if name==SELECT:
        result=layout if VIEW=='print' else cq.Compound.makeCompound([fixed.val(),close(moving).val(),catch.val()])
        if VIEW=='section':
            result=cq.Workplane(obj=result).intersect(box(0,-DEPTH/2,SEAM,1,25,45))
if EXPORT:
    (ROOT/'notes'/'keeper_latch_metrics.json').write_text(json.dumps(metrics,indent=2)+'\n')
