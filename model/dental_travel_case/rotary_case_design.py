"""Full-size PLA rotary case, revised from the physically accepted quick trial."""
from dataclasses import replace
import cadquery as cq
from rotary_refinement_design import D,build,configuration

CURRENT=replace(D,guide_clearance=.2,keeper_radius=12.8,keeper_form='wide',keeper_span=34.)


def case():
    return build('wheel',dimensions=CURRENT,fastener='printed-coarse')


def shell_layout(p):
    """Three parts at shell settings; unchanged solid fasteners print separately."""
    d=p['dimensions'];a=cq.Assembly(name='full_rotary_travel_case_print')
    a.add(p['body'],name='body')
    a.add(p['cap'].rotate((0,0,0),(1,0,0),180).translate((100,0,d.length)),name='cap')
    a.add(p['rotor'].rotate((0,0,0),(1,0,0),90).translate((50,80+d.pivot,d.wheel_front)),name='spring_wheel')
    return a
