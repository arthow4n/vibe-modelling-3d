"""Reduced sunglasses case with the physically preferred E loop latch.

Millimetres. PETG, 0.4 mm nozzle; 260 x 260 x 250 mm safe build volume.
Print open and flat, plus the small side-printed keeper. Slide the keeper
into the body after printing. No hardware or hinge assembly; supports off.
"""
from pathlib import Path
import importlib.util
import json
import cadquery as cq

INNER_LENGTH = globals().get('INNER_LENGTH',158.0)
INNER_WIDTH = globals().get('INNER_WIDTH',78.0)
INNER_HEIGHT = globals().get('INNER_HEIGHT',63.0)
WALL = 3.0
FLOOR = 3.0
CORNER = 10.0
EXTERIOR_BEVEL = 2.0
RIM_ROUND = 0.6
HINGE_RADIUS = 5.6
PIVOT_RADIUS = 3.5
CONE_CLEARANCE = 0.20  # radial at fixed X; surface-normal gap is /sqrt(2)
END_CLEARANCE = 0.20  # axial ear gap, accepted E configuration
PIVOT_ROOT = 4.5
EAR_OUTER_OFFSET = 10.0
BEARING_EDGE_INSET = 52.0
LAYOUT = globals().get('LAYOUT', 'print')  # print / closed / open / section
EXPORT = globals().get('EXPORT', True)
ROOT=Path(globals().get('__file__','/home/hevar/git/vibe-modelling-3d/model/sunglasses_case/sunglasses_case.py')).resolve().parent
spec=importlib.util.spec_from_file_location('e_closure',ROOT/'e_closure.py')
closure=importlib.util.module_from_spec(spec)
spec.loader.exec_module(closure)

OW, OD = INNER_LENGTH+2*WALL, INNER_WIDTH+2*WALL
HEIGHT = INNER_HEIGHT+2*FLOOR
SEAM = HEIGHT/2
HY = OD/2+HINGE_RADIUS*2**0.5+0.8
BEARING_CENTERS = (-OW/2+BEARING_EDGE_INSET,OW/2-BEARING_EDGE_INSET)
assert WALL>=2.4 and FLOOR>=2.4 and INNER_HEIGHT>=60
assert CORNER>WALL and OW>2*BEARING_EDGE_INSET+2*EAR_OUTER_OFFSET

def block(x,y,z,dx,dy,dz):
    return cq.Workplane('XY').box(dx,dy,dz).translate((x,y,z))

def rounded(w,d,h,z,radius):
    return (cq.Workplane('XY').box(w,d,h,centered=(True,True,False))
            .edges('|Z').fillet(radius).translate((0,0,z)))

def half():
    outer=rounded(OW,OD,SEAM,0,CORNER).edges('<Z').chamfer(EXTERIOR_BEVEL)
    cavity=rounded(INNER_LENGTH,INNER_WIDTH,SEAM,FLOOR,CORNER-WALL)
    return outer.cut(cavity).edges('>Z').fillet(RIM_ROUND)

def hinge_ear(x0,x1,lid_side=False):
    side=1 if lid_side else -1
    wall_y=HY+side*(HINGE_RADIUS*2**0.5+1.8)
    r=HINGE_RADIUS; t=r/2**0.5
    barrel=(cq.Workplane('YZ',origin=(x0,HY,SEAM)).moveTo(0,-r*2**0.5)
            .lineTo(t,-t).threePointArc((r,0),(0,r)).threePointArc((-r,0),(-t,-t)).close().extrude(x1-x0))
    barrel=barrel.edges(cq.selectors.NearestToPointSelector(
        ((x0+x1)/2,HY,SEAM-r*2**0.5))).fillet(0.8)
    web=(cq.Workplane('YZ',origin=(x0,0,0)).polyline([
        (wall_y,SEAM-r*2**0.5-abs(wall_y-HY)),(HY,SEAM-r*2**0.5),
        (HY,SEAM),(wall_y,SEAM)]).close().extrude(x1-x0))
    return barrel.union(web)

def cone(x,r,direction):
    return cq.Workplane(obj=cq.Solid.makeCone(r,0.12,r-0.12,
        cq.Vector(x,HY,SEAM),cq.Vector(direction,0,0)))

def hinge(c):
    fixed=hinge_ear(c-EAR_OUTER_OFFSET,c-PIVOT_ROOT).union(hinge_ear(c+PIVOT_ROOT,c+EAR_OUTER_OFFSET))
    fixed=fixed.union(cone(c-PIVOT_ROOT,PIVOT_RADIUS,1)).union(cone(c+PIVOT_ROOT,PIVOT_RADIUS,-1))
    moving=hinge_ear(c-PIVOT_ROOT+END_CLEARANCE,c+PIVOT_ROOT-END_CLEARANCE,True)
    moving=moving.cut(cone(c-PIVOT_ROOT,PIVOT_RADIUS+CONE_CLEARANCE,1))
    moving=moving.cut(cone(c+PIVOT_ROOT,PIVOT_RADIUS+CONE_CLEARANCE,-1))
    return fixed,moving

def close(part,angle=180):
    return part.rotate((0,HY,SEAM),(1,HY,SEAM),angle)

def compound(*parts):
    return cq.Compound.makeCompound([p.val() for p in parts])

# Preserve the complete E interfaces by translation, including flexure roots.
body_shift=(0,-OD/2+closure.REFERENCE_DEPTH/2,SEAM-closure.REFERENCE_SEAM)
lid_shift=(0,2*HY+OD/2-(2*closure.REFERENCE_HY+closure.REFERENCE_DEPTH/2),SEAM-closure.REFERENCE_SEAM)
receiver=closure.receiver().translate(body_shift)
keeper=closure.keeper().translate(body_shift)
loop=closure.loop().translate(lid_shift)
body=half().union(receiver)
open_lid=half().translate((0,2*HY,0))
for c in BEARING_CENTERS:
    a,b=hinge(c)
    body=body.union(a); open_lid=open_lid.union(b)
lid_shell=open_lid
open_lid=open_lid.union(loop)
lid=close(open_lid)
# E's existing insert can also be reused: its geometry is unchanged.
print_keeper=closure.keeper().rotate((0,0,0),(0,1,0),-90).translate((OW/2+14+29.4,22.1,5.5))
print_layout=compound(body,open_lid,print_keeper)
closed=compound(body,lid,keeper)
opened=compound(body,close(open_lid,70),keeper)
result={'print':print_layout,'closed':closed,'open':opened,'section':
    cq.Workplane(obj=closed).intersect(block(0,-OD/2,SEAM,1,25,45))}[LAYOUT]

for part in (body,open_lid,keeper):
    assert len(part.solids().vals())==1 and part.val().isValid(), 'invalid/disconnected part'
assert body.intersect(open_lid).val().Volume()<0.001, 'print collision'
assert body.intersect(lid).val().Volume()<0.001, 'closed shell collision'
assert keeper.intersect(lid).val().Volume()<0.001, 'closed latch collision'
fit_interference=body.intersect(keeper).val().Volume()
assert fit_interference<1, ('excessive wedge interference',fit_interference)
# Rounded empty cavity, not a claim that the originally estimated glasses fit.
cavity=rounded(INNER_LENGTH,INNER_WIDTH,INNER_HEIGHT,FLOOR,CORNER-WALL)
for part in (body,lid,keeper):
    assert part.intersect(cavity).val().Volume()<0.001, 'intrusion into requested cavity'
for angle in range(0,181,5):
    assert body.intersect(close(lid_shell,angle)).val().Volume()<0.001, ('hinge/shell sweep',angle)
assert keeper.intersect(close(loop,179)).val().Volume()>0.01, 'no rotational retention'
assert keeper.intersect(close(loop).translate((0,0,0.4))).val().Volume()>0.01
released=close(loop).translate((0,-closure.RELEASE_TRAVEL-0.3,0))
for lift in (0,0.4,2,5,9):
    assert body.union(keeper).intersect(released.translate((0,0,lift))).val().Volume()<0.001, ('release',lift)
assert body.intersect(keeper.translate((0,0,0.4))).val().Volume()>1
assert body.intersect(keeper.translate((0,-0.4,0))).val().Volume()>1
bb=print_layout.BoundingBox()
assert bb.xlen<260 and bb.ylen<260 and bb.zlen<250
if EXPORT:
    cq.exporters.export(print_layout,str(ROOT/'sunglasses_case.step'))
    cq.exporters.export(print_layout,str(ROOT/'sunglasses_case.stl'),tolerance=0.025,angularTolerance=0.1)
    (ROOT/'notes'/'production_e_metrics.json').write_text(json.dumps({
        'interior_mm':[INNER_LENGTH,INNER_WIDTH,INNER_HEIGHT],
        'shell_exterior_mm':[OW,OD,HEIGHT], 'print_bounds_mm':[bb.xlen,bb.ylen,bb.zlen],
        'volume_mm3':print_layout.Volume(),'bearing_centers_mm':BEARING_CENTERS,
        'cone_radial_clearance_mm':CONE_CLEARANCE,'ear_axial_clearance_mm':END_CLEARANCE,
        'loop_thickness_mm':closure.LOOP_THICKNESS,'seated_latch_gap_mm':closure.SEATED_GAP,
        'release_travel_mm':closure.RELEASE_TRAVEL,'intentional_key_interference_mm3':fit_interference
    },indent=2)+'\n')
