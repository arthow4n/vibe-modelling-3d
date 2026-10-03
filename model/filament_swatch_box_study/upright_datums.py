"""Object-owned opposing rails: support above AND below the spring contact."""
import cap_j_base_5 as j

RAIL_INNER_X=21.8
RAIL_OUTER_X=23.0
LOW_HEIGHT=3.5
STRAIGHT_HEIGHT=16.0


def rails(y,side=1):
    front=j.slots.SLOT_WIDTH/2
    points=[(front,j.slots.FLOOR+LOW_HEIGHT),(3.4,j.slots.FLOOR+LOW_HEIGHT),
            (3.4,j.g.TOP_Z),(j.slots.MOUTH_WIDTH/2,j.g.TOP_Z),
            (front,j.slots.FLOOR+STRAIGHT_HEIGHT)]
    parts=[]
    for end in (-1,1):
        lo,hi=sorted((end*RAIL_INNER_X,end*RAIL_OUTER_X))
        p=(j.cq.Workplane('YZ',origin=(lo,y,0)).polyline(points).close().extrude(hi-lo))
        if side<0:
            p=p.mirror('XZ',(0,y,0))
        parts.append(p)
    return j.cq.Workplane('XY').newObject([j.g.compound(*parts)])


def add_to(base,side=1):
    for n in range(j.COUNT):
        base=base.union(rails(j.slots.slot_y(n,j.COUNT),side))
    return base
