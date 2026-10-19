"""C6 short-loop front-wall crop, matching full-case thickness and placement."""
import cadquery as cq
from clamshell_design import build, D, closure, base


def sample():
    p=build('screw_pin')
    crop=base.box(0,-33,26,50,26,54)
    body=p['body'].intersect(crop)
    lid=p['lid'].intersect(crop)
    printed_lid=lid.rotate((0,0,0),(1,0,0),180).translate((80,0,D.length))
    keeper=closure.keeper().rotate((0,0,0),(0,1,0),-90).translate((155,22.1,5.5))
    a=cq.Assembly(name='C6_short_loop_trial')
    a.add(body,name='base');a.add(printed_lid,name='lid');a.add(keeper,name='keeper')
    return dict(body=body,lid=lid,result=a)


result=sample()['result']
