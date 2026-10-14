"""Intent checks on native CAD; grip/latch/pin forces remain unmeasured."""
import json
from pathlib import Path
import math
import cadquery as cq
from assembly_geometry import check_pair,PairRequirement
from components import compound
from mechanisms import block
from parameters import CLIP_POSITIONS,CLIP_WALL
from r2_geometry import (HEIGHT,FLOOR,RIM,CLOSED_LINK_ANGLE,STATIONS,
                        lid_pose,link_pose,AXIS_Y,AXIS_Z,LID_AXIS_Y,rear_half)
from r2_parts import (GRIP_DIAMETER,GRIP_THROAT,GUARD_BOTTOM,GATE_SEAT,
                      GATE_STEM,snap_pin,LATCH_START,LATCH_RELEASE,compressed_pin_proxy)
from r2_design import build,references,hardware,section_test

OVERLAP=1e-5  # numerical contact allowance, mm3; not an FDM clearance


def clear(a,b,intent):
    answer=check_pair(a,b,PairRequirement(intent,max_overlap_mm3=OVERLAP))
    answer.require_passed()
    return answer.overlap_mm3 if hasattr(answer,'overlap_mm3') else None


def construction(case):
    for key in ('body','lid_print'):
        assert case[key].val().isValid(),key
        assert len(case[key].solids().vals())==1,(key,'Disconnected printed features')
    for key in ('clips','gates','links','body_pins','lid_pins'):
        for p in case[key]:
            assert p.val().isValid(),key
            assert len(p.solids().vals())==1,key
    assert hardware().isValid()
    assert section_test(case).isValid()


def fit(case):
    nominal=references(diameter=27)
    generous=references(diameter=30)
    shell=rear_half(lid_side=False)
    for name,p in generous.items():
        clear(shell,p,'30 mm brush / roomy tube shell envelope: '+name)
        clear(case['lid'],p,'Closed lid accommodates envelope: '+name)
    for name,p in nominal.items():
        clear(case['body'],p,'Complete mounted case fits revised 27 mm grip target: '+name)
    for c in case['clips']:
        clear(c,nominal['handle'],'27 mm nominal handle fits revised bore')
    for pin in case['body_pins']+case['lid_pins']+case['links']+case['gates']:
        for name,p in nominal.items():
            clear(pin,p,'Hardware does not contact held items: '+name)


def brush_capture(case):
    assert len(case['clips'])==len(case['gates'])==2
    assert GRIP_THROAT < GRIP_DIAMETER
    handle=references(diameter=27)['handle']
    for c,g in zip(case['clips'],case['gates']):
        seated=case['body'].intersect(c).val().Volume()
        assert 0 < seated < 2,('Only tested rib preload expected',seated)
        assert case['body'].intersect(c.translate((0,0,1))).val().Volume()>seated
        assert case['body'].intersect(c.translate((1,0,0))).val().Volume()>seated
        clear(c,g,'Clip gate clears the seated foot')
        assert c.translate((-1,0,0)).intersect(g).val().Volume()>OVERLAP,'Missing reverse-slide stop'
        assert g.translate((0,0,3)).intersect(handle).val().Volume()>OVERLAP,'Brush must capture gate'
    clear(handle,case['lid'],'Closed keeper leaves brush clearance')
    assert handle.translate((0,0,2.5)).intersect(case['lid']).val().Volume()>OVERLAP,'No closed lift obstruction'
    free_lift=GUARD_BOTTOM-(33+GRIP_DIAMETER/2)
    assert free_lift<GATE_STEM-(33-GRIP_DIAMETER/2-(GATE_SEAT+2))
    # Clip lips lie above the handle centre; keeper arrests lift well before
    # the centre reaches those lips, even before full arm-spreading escape.
    mouth_height=math.sqrt((GRIP_DIAMETER/2+.15)**2-(GRIP_THROAT/2)**2)
    assert free_lift<mouth_height


def closure(case):
    latch=case['latch_leaf']
    clear(latch,case['body'],'Latch is clear in the closed seated pose')
    assert latch.translate((0,0,1)).intersect(case['body']).val().Volume()>OVERLAP,'No latch retention'
    released=latch.translate((0,-LATCH_RELEASE,0))
    for dz in (0,.5,1,2,3,4):
        clear(released.translate((0,0,dz)),case['body'],'Released latch lift '+str(dz))


def pin_capture(case):
    for key,host in (('body_pins',case['body']),('lid_pins',case['lid'])):
        for pin,x in zip(case[key],STATIONS):
            clear(pin,host,'Seated snap pin clears its bearing/covered access port')
            direction=1 if x>0 else -1
            for shift in (-1,1):
                assert pin.translate((shift*direction,0,0)).intersect(host).val().Volume()>OVERLAP,'Missing head/barb capture'
    for p in case['links']:
        clear(p,case['body'],'Closed link/body bearing clearance')
        clear(p,case['lid'],'Closed link/lid bearing clearance')


def admission(case):
    # Assemble upper joints with the lid detached, then admit lower pins from
    # the outer end through the recessed access ports.
    for joint,host in (('body',case['body']),('lid',case['lid'])):
        obstacle=compound(host,*case['links'])
        for x in STATIONS:
            direction=1 if x>0 else -1
            if joint=='body': direction=-direction
            pin=compressed_pin_proxy(x,joint=joint)
            for travel in (-35,-25,-15,-10,-6,-3,-1,0):
                clear(pin.translate((direction*travel,0,0)),obstacle,
                      'Compressed snap-pin admission '+joint+' '+str(travel))


def compliance():
    r=GRIP_DIAMETER/2+.15
    length=r*(math.acos(GRIP_THROAT/(2*r))+math.pi/4)
    strain=3*CLIP_WALL*((GRIP_DIAMETER-GRIP_THROAT)/2)/(2*length**2)
    pin_screen=3*2.2*.5/(2*13.5**2)
    latch_screen=3*1.2*LATCH_RELEASE/(2*((HEIGHT/2+5.2)-LATCH_START)**2)
    assert max(strain,pin_screen,latch_screen)<.01,('Uncalibrated 1% beam screen',strain,pin_screen,latch_screen)
    return dict(grip=strain,pin=pin_screen,latch=latch_screen)


def path(case,route,*,subdivisions):
    """Coupled native-CAD path; latch release is an explicit rigid proxy.

    Native shapes validate sampled route. Free-leaf translation with a fixed root only
    represents release clearance, not actual elastic deformation or effort.
    """
    if subdivisions<1:
        raise ValueError('Positive refinement required')
    fixed=compound(case['body'],*case['clips'],*case['gates'],*case['body_pins'],
                   *references(diameter=27).values())
    rigid_lid=case['lid'].cut(case['latch_leaf'])
    points=[route[0]]
    for a,b in zip(route[:-1],route[1:]):
        for i in range(1,subdivisions+1):
            f=i/subdivisions
            points.append({key:a[key]+(b[key]-a[key])*f for key in a})
    for i,state in enumerate(points):
        phi,theta=state['lid_degrees'],state['link_degrees']
        lid=lid_pose(rigid_lid,phi,theta)
        flexible=case['latch_leaf'].translate((0,-LATCH_RELEASE,0)) if phi<=6 else case['latch_leaf']
        moving=compound(lid,lid_pose(flexible,phi,theta),
                        *[lid_pose(p,phi,theta) for p in case['lid_pins']])
        answer=check_pair(moving,fixed,PairRequirement('Coupled loaded lid path '+str(state),max_overlap_mm3=OVERLAP))
        if answer.status!='passed':
            for name,p in [('body',case['body']),('brush_clips',compound(*case['clips'])),
                           ('gates',compound(*case['gates'])),('lower_pins',compound(*case['body_pins'])),
                           *references(diameter=27).items()]:
                hit=moving.intersect(p.val() if isinstance(p,cq.Workplane) else p)
                if hit.Volume()>OVERLAP:
                    for solid in hit.Solids():
                        b=solid.BoundingBox()
                        print('Failed contact',name,hit.Volume(),[b.xmin,b.xmax,b.ymin,b.ymax,b.zmin,b.zmax],flush=True)
        answer.require_passed()
        # The table is an explicit physical obstacle, not a mesh bounds audit.
        table=block(0,50,-5,600,600,10)
        clear(moving,table,'Lid clears table '+str(state))
        for j,p in enumerate(case['links']):
            placed=link_pose(p,theta)
            clear(placed,fixed,'Moving link/fixed parts and contents '+str(state))
            clear(placed,moving,'Moving link/lid '+str(state))
            clear(placed,table,'Moving link/table '+str(state))
        if i%10==0:
            print('Native CAD path',i+1,'/',len(points),phi,theta,flush=True)
    return dict(samples=len(points),edge_subdivisions=subdivisions,
                maximum_joint_step_degrees=3/subdivisions,continuous_proof=False)


if __name__=='__main__':
    case=build()
    construction(case);print('Construction pass',flush=True)
    fit(case);print('Fit pass',flush=True)
    brush_capture(case);print('Brush capture pass',flush=True)
    closure(case);print('Closure pass',flush=True)
    pin_capture(case);print('Pin capture pass',flush=True)
    admission(case);print('Pin admission proxy pass',flush=True)
    print('Beam screens',compliance(),flush=True)
    route=json.loads((Path(__file__).parent/'notes/r2_cad_route.json').read_text())['route']
    print(path(case,route,subdivisions=1),flush=True)


def foundation_path(case,route,*,subdivisions):
    """Qualify only added feet; original full-load route evidence stays scoped.

    Original builder, moving actors and route are preserved. Actual Boolean
    differences must show an addition solely below the old bearing-base plane.
    This targets the FDM correction without repeating the unchanged full route.
    """
    added=case['body'].cut(case['motion_body'])
    assert case['motion_body'].cut(case['body']).val().Volume()<OVERLAP,'Foundation change removed original material'
    assert added.intersect(block(0,0,(FLOOR+100)/2,600,600,100-FLOOR)).val().Volume()<OVERLAP,'Added material above the original bearing-base plane'
    points=[route[0]]
    for a,b in zip(route[:-1],route[1:]):
        for i in range(1,subdivisions+1):
            f=i/subdivisions
            points.append({key:a[key]+(b[key]-a[key])*f for key in a})
    rigid=case['lid'].cut(case['latch_leaf'])
    for i,state in enumerate(points):
        phi,theta=state['lid_degrees'],state['link_degrees']
        leaf=case['latch_leaf'].translate((0,-LATCH_RELEASE,0)) if phi<=6 else case['latch_leaf']
        moving=compound(lid_pose(rigid,phi,theta),lid_pose(leaf,phi,theta),
                        *[lid_pose(p,phi,theta) for p in case['lid_pins']],
                        *[link_pose(p,theta) for p in case['links']])
        clear(moving,added,'Added bearing feet clear qualified moving actors '+str(state))
        if i%30==0:print('Foundation path',i+1,'/',len(points),flush=True)
    return dict(samples=len(points),maximum_joint_step_degrees=3/subdivisions,scope='Added foundations only')
