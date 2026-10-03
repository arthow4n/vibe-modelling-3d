"""I: three preloaded replacement keys for the already printed H pockets, mm.

Print only these keys first. Number 1/2/3 means increasing grip. Existing H
blocks, base and hood are retained; no full-module revision is supplied yet.
"""
import math
import cap_h_module_5 as h
from cap_h_module_5 import cq, compound, block
from physical_analysis.screening import elastic_friction_grip

CORE_GROWTH = .15  # H pocket .20 normal offset leaves .05 normal core clearance.
KEY_SEAM_GAP = 0.0  # Design for the existing H blocks butted together, not spaced .3 mm.
ARM_THICKNESS = .8
RELIEF_WIDTH = .7
PAD_STATION = 4.35
PAD_RADIUS = .8
PAD_BASE_N = -.12
ENTRY_PROJECTION = .05
ENTRY_HEIGHT = .8
PROJECTIONS = (.30, .35, .40)  # Actual preload is projection minus H's .20 normal gap.
KEY_HEIGHT = h.KEY_TOP_Z-h.KEY_FLOOR_Z
PRINT_CENTRES = ((90,110), (115,110), (140,110))
LENGTH = math.hypot(h.KEY_HEAD_HALF_X-h.KEY_WAIST_HALF_X, h.KEY_EMBED)
TANGENT = ((h.KEY_HEAD_HALF_X-h.KEY_WAIST_HALF_X)/LENGTH, h.KEY_EMBED/LENGTH)
NORMAL = (TANGENT[1], -TANGENT[0])
RELIEF_N = CORE_GROWTH-ARM_THICKNESS-RELIEF_WIDTH/2


def key_outline():
    """H mating diagonals with the blocks fully seated against each other."""
    waist=h.KEY_WAIST_HALF_X
    head=h.KEY_HEAD_HALF_X
    depth=h.KEY_EMBED+KEY_SEAM_GAP/2
    return cq.Workplane('XY').polyline([(-waist,0),(-head,-depth),(head,-depth),
                                       (waist,0),(head,depth),(-head,depth)]).close()


def module_centres():
    return (-h.FOOT_DEPTH/2,h.FOOT_DEPTH/2)


def seated_interference(projection):
    # If an intended seam closes, its normal projection consumes grip travel.
    return projection-h.KEY_FIT_GAP-KEY_SEAM_GAP*abs(NORMAL[1])/2


def flank_point(s, n, xside=1, yside=1):
    """s runs along one H diagonal; n is its outward contact-normal distance."""
    return (xside*(h.KEY_WAIST_HALF_X+s*TANGENT[0]+n*NORMAL[0]),
            yside*(KEY_SEAM_GAP/2+s*TANGENT[1]+n*NORMAL[1]))


def pad_wire(projection, xside=1, yside=1, plane=None):
    """Rounded contact crown, clipped below the flank rather than a sharp tooth."""
    span=math.sqrt(PAD_RADIUS**2-(PAD_BASE_N-(projection-PAD_RADIUS))**2)
    a=flank_point(PAD_STATION-span,PAD_BASE_N,xside,yside)
    b=flank_point(PAD_STATION,projection,xside,yside)
    c=flank_point(PAD_STATION+span,PAD_BASE_N,xside,yside)
    plane=cq.Workplane('XY') if plane is None else plane
    return plane.moveTo(*a).threePointArc(b,c).lineTo(*a).close()


def spring_relief(xside, yside):
    # A round closed root and an open exit through the head leave a real flexure.
    a=flank_point(0, RELIEF_N, xside, yside)
    b=flank_point(LENGTH+2, RELIEF_N, xside, yside)
    corners=[flank_point(s,n,xside,yside)
             for s,n in ((0,RELIEF_N-RELIEF_WIDTH/2),
                         (LENGTH+2,RELIEF_N-RELIEF_WIDTH/2),
                         (LENGTH+2,RELIEF_N+RELIEF_WIDTH/2),
                         (0,RELIEF_N+RELIEF_WIDTH/2))]
    body=cq.Workplane('XY').polyline(corners).close().extrude(KEY_HEIGHT+.4).translate((0,0,-.2))
    for x,y in (a,b):
        body=body.union(cq.Workplane('XY').center(x,y).circle(RELIEF_WIDTH/2)
                        .extrude(KEY_HEIGHT+.4).translate((0,0,-.2)))
    return body


def grip_key(number=2, projection=None, label=True):
    if number not in (1,2,3):
        raise ValueError('Choose grip key 1, 2 or 3')
    if projection is None:
        projection=PROJECTIONS[number-1]
    if not ENTRY_PROJECTION <= projection <= .4:
        raise ValueError('Pad projection outside reviewed .05–.40 mm range')
    part=(key_outline().offset2D(CORE_GROWTH).extrude(KEY_HEIGHT)
          .faces('<Z or >Z').edges().chamfer(.15))
    for xs in (-1,1):
        for ys in (-1,1):
            bottom=pad_wire(ENTRY_PROJECTION,xs,ys)
            ramp=pad_wire(projection,xs,ys,bottom.workplane(offset=ENTRY_HEIGHT)).loft(combine=True)
            crown=(pad_wire(projection,xs,ys)
                   .extrude(KEY_HEIGHT-ENTRY_HEIGHT).translate((0,0,ENTRY_HEIGHT)))
            part=part.union(ramp.union(crown))
    for xs in (-1,1):
        for ys in (-1,1):
            part=part.cut(spring_relief(xs,ys))
    # Mark the solid centre, clear of all flexure roots and contact surfaces.
    if label:
        marking=cq.Workplane('XY').text(str(number),2.5,.3,combine=False).translate((0,0,KEY_HEIGHT-.3))
        part=part.cut(marking)
    return part


def seated_key(number=2, projection=None):
    return grip_key(number,projection).translate((0,0,h.KEY_FLOOR_Z))


def print_layout():
    for projection in PROJECTIONS:
        grip=elastic_friction_grip(interference_mm=seated_interference(projection),contact_count=4)
        if not grip['preload_present']:
            raise ValueError('A printed friction grip needs actual seated preload; revise before exporting')
    return compound(*[grip_key(i).translate((x,y,0))
                      for i,(x,y) in enumerate(PRINT_CENTRES,1)])


if __name__ in ('__main__','__cqgi__'):
    result=print_layout()
