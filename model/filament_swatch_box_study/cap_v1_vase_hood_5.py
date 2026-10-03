"""V1 vase-only SOLID slicer envelope; print roof down with spiral mode.

The filled STEP/STL is deliberate Orca vase input, NOT a conventional solid
print. One .42 mm perimeter, .2 mm layers, 4 solid bottom layers (.8 mm roof),
zero infill/top layers. nominal_shell() is inspection geometry, not export.
G hood and J2/K2 bases remain unchanged; same I key.
"""
import math
import cadquery as cq
import cap_g_module_5 as g

LINE_WIDTH=.42
ROOF=.8
NECK_DEPTH=.7
NECK_Z=18.9
NECK_HALF_SPAN=2.0
NECK_STEPS=40
ROOF_RADIUS=g.ROOF_RADIUS
# Concentric with the base foot's rounded top edge. A small smooth rim taper
# gives the .42 mm wall a positive landing on that edge, not incidental tangency.
OUTSIDE_RADIUS=g.FOOT_RADIUS-(g.FOOT_X-g.OUTSIDE_X)/2
RIM_INSET=.2
RIM_HEIGHT=1.2


def neck(z):
    d=abs(z-NECK_Z)
    return NECK_DEPTH*.5*(1+math.cos(math.pi*d/NECK_HALF_SPAN)) if d<NECK_HALF_SPAN else 0.0


def rim(z):
    h=max(0,z-g.SEAM_Z)
    return RIM_INSET*.5*(1+math.cos(math.pi*h/RIM_HEIGHT)) if h<RIM_HEIGHT else 0.0


def outline(z,inset=0,roof_round=True):
    shrink=0.0
    if roof_round and z>g.ROOF_TOP-ROOF_RADIUS:
        dz=z-(g.ROOF_TOP-ROOF_RADIUS)
        shrink=ROOF_RADIUS-math.sqrt(max(0,ROOF_RADIUS**2-dz**2))
    shrink+=rim(z)
    half_x=g.OUTSIDE_X/2-neck(z)-shrink-inset
    half_y=g.OUTSIDE_DEPTH/2-shrink-inset
    r=OUTSIDE_RADIUS-shrink-inset
    return (cq.Workplane('XY',origin=(0,0,z)).moveTo(-half_x+r,-half_y)
        .lineTo(half_x-r,-half_y).radiusArc((half_x,-half_y+r),-r)
        .lineTo(half_x,half_y-r).radiusArc((half_x-r,half_y),-r)
        .lineTo(-half_x+r,half_y).radiusArc((-half_x,half_y-r),-r)
        .lineTo(-half_x,-half_y+r).radiusArc((-half_x+r,-half_y),-r).close().val())


def neck_levels():
    return [NECK_Z-NECK_HALF_SPAN+2*NECK_HALF_SPAN*n/NECK_STEPS for n in range(NECK_STEPS+1)]


def rim_levels():
    return [g.SEAM_Z+RIM_HEIGHT*n/12 for n in range(13)]


def loft(wires):
    return cq.Workplane('XY').newObject(wires).toPending().loft(ruled=True)


def envelope():
    # Equal sections above/below the waist keep the main body exactly straight.
    levels=[*rim_levels(),*neck_levels(),g.ROOF_TOP]
    return loft([outline(z,roof_round=False) for z in levels]).faces('>Z').edges().fillet(ROOF_RADIUS)


def nominal_shell():
    # At every height, the print's inner XY boundary is one line width inwards.
    # The upper cavity ends at the last solid floor layer in roof-down printing.
    top=g.ROOF_TOP-ROOF
    round_levels=[g.ROOF_TOP-ROOF_RADIUS+.1*n for n in range(1,int((ROOF_RADIUS-ROOF)/.1)+1)
                  if g.ROOF_TOP-ROOF_RADIUS+.1*n<top-1e-7]
    levels=[g.SEAM_Z-.1,*rim_levels(),*neck_levels(),g.ROOF_TOP-ROOF_RADIUS,*round_levels,top]
    levels=sorted(set(levels))
    return envelope().cut(loft([outline(z,LINE_WIDTH) for z in levels]))


def print_input():
    return g.hood_print(envelope()).translate(g.PRINT_ANCHOR)


if __name__ in ('__main__','__cqgi__'):
    result=print_input()
