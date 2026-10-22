"""Short open-ended rotary trial; original guide clearance and mechanism.

The complete product keeps its 30mm sleeve. This coupon's 18mm sleeve and
large end openings reduce material and provide finger purchase, while changing
stiffness and available guide bearing length. It is not a full-case load test.
"""
from dataclasses import replace
import cadquery as cq
import m1_design as base
from rotary_refinement_design import D,build as build_case

QUICK=replace(D,seam=24.,lap=18.,length=50.)
OPENING_WIDTH=50.
OPENING_DEPTH=30.
OPENING_RADIUS=3.
EDGE_CHAMFER=.4


def open_end(part,*,end):
    if end not in ('bottom','top'):raise ValueError('Unknown opening end: '+str(end))
    low=0. if end=='bottom' else QUICK.length-2.
    tool=base.prism(OPENING_WIDTH,OPENING_DEPTH,OPENING_RADIUS,low-1.,4.)
    opened=part.cut(tool)
    # Chamfer only the hole edges at both faces of the 2mm end frame.
    edges=opened.edges().filter(lambda e: abs(e.Center().x)<OPENING_WIDTH/2+.01
        and abs(e.Center().y)<OPENING_DEPTH/2+.01
        and any(abs(e.Center().z-z)<1e-6 for z in (low,low+2.)))
    return edges.chamfer(EDGE_CHAMFER).clean()


def build():
    p=build_case('wheel',dimensions=QUICK,fastener='printed-coarse')
    p['body']=open_end(p['body'],end='bottom')
    p['body_core']=open_end(p['body_core'],end='bottom')
    p['cap']=open_end(p['cap'],end='top')
    return p


def print_layout(p):
    """Three shell/wheel parts only; print the unchanged fastener pair solid."""
    d=p['dimensions'];a=cq.Assembly(name='short_open_rotary_trial')
    a.add(p['body'],name='open_bottom_body')
    a.add(p['cap'].rotate((0,0,0),(1,0,0),180).translate((100,0,d.length)),name='open_top_cap')
    a.add(p['rotor'].rotate((0,0,0),(1,0,0),90).translate((50,80+d.pivot,d.wheel_front)),name='spring_wheel')
    return a
