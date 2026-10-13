"""Small samples using production builders and production print orientation.

Main result is the three samples spaced on a diagnostic plate. Each sample also
has its own STEP/STL export. These test local behavior, not full-case stiffness.
"""
from design import build
from parameters import *
from mechanisms import block,hinge
from components import compound,clip,socket
import cadquery as cq

def hinge_test():
    fixed=block(0,OD/2-1.2,SEAM/2,32,WALL,SEAM)
    moving=block(0,2*HY-OD/2+1.2,SEAM/2,32,WALL,SEAM)
    fixed=fixed.union(block(0,OD/2-6,FLOOR/2,32,12,FLOOR))
    moving=moving.union(block(0,2*HY-OD/2+6,FLOOR/2,32,12,FLOOR))
    left,right,receiver=hinge(0)
    fixed=fixed.union(left).union(right)
    moving=moving.union(receiver)
    for angle in range(0,181,15):
        assert fixed.intersect(moving.rotate((0,HY,SEAM),(1,HY,SEAM),angle)).val().Volume()<0.001
    for shift in (-1,1):
        assert fixed.intersect(moving.translate((shift,0,0))).val().Volume()>0.001
    return compound(fixed,moving).translate((0,-HY,0))

def latch_test(case):
    # Crop exact walls, floor, keeper and full spring/root/grip; no shortening.
    body=case['body'].intersect(block(0,-OD/2+4,SEAM,32,16,2*SEAM))
    front=2*HY+OD/2
    lid=case['open_lid'].intersect(block(0,front-3,SEAM,32,20,2*SEAM))
    assert len(body.solids().vals())==len(lid.solids().vals())==1
    return compound(body.translate((0,OD/2,0)),lid.translate((0,30-front,0)))

def handle_test():
    base=block(0,0,FLOOR/2,28,BRUSH_LANE,FLOOR).union(socket().translate((0,0,FLOOR)))
    return compound(base,clip().translate((38,0,0)))

def samples(case):
    hinge_sample=hinge_test()
    latch_sample=latch_test(case)
    handle_sample=handle_test()
    return dict(hinge_test=hinge_sample,latch_test=latch_sample,handle_test=handle_sample,
                test_pieces=compound(hinge_sample,latch_sample.translate((50,0,0)),
                                     handle_sample.translate((100,0,0))))
