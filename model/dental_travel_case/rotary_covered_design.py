"""Scalloped facecap positively keyed to the rigid wheel hub, clear of spring."""
from dataclasses import replace
import cadquery as cq
import m1_design as base
from rotary_case_design import case as exposed_case
from rotary_refinement_design import wheel_plate,rotor_pose
from rotary_r1_design import axial_cylinder
from rotary_conical_design import wheel_recess,socket_axle,FACE_EXTENSION

GAP=.4
FACE_THICKNESS=1.2
KEY_X=7.
KEY_WIDTH=2.4
KEY_HEIGHT=2.8
KEY_ENGAGEMENT=1.8
KEY_CLEARANCE=.1
KEY_BOTTOM_CLEARANCE=.15
OFFSET=GAP+FACE_THICKNESS
EXTENSION=FACE_EXTENSION+OFFSET


def key(x,d,*,clearance,top,bottom):
    return (base.box(x,(top+bottom)/2,d.pivot,KEY_WIDTH+2*clearance,
                     top-bottom,KEY_HEIGHT+2*clearance)
            .edges('|Y').fillet(.2+clearance))


def printed_axle():
    return socket_axle(face_extension=EXTENSION)


def screw_print_pose(part):
    return part.translate((0,0,EXTENSION))


def covered_case():
    p=exposed_case();d=p['dimensions'];back=d.wheel_front+GAP;front=back+FACE_THICKNESS
    # Restore a straight through-bore in the hidden rotor: its old head recess
    # is now in the facecap. Rear relief and all spring/nose geometry remain.
    fill=wheel_recess(d).mirror('XZ')
    bore=axial_cylinder(4.2,45,d.pivot,20).mirror('XZ')
    lead=cq.Workplane(obj=cq.Solid.makeCone(4.6,4.2,.4,
         cq.Vector(0,d.wheel_front,d.pivot),cq.Vector(0,-1,0))).mirror('XZ')
    for name in ('rotor','rotor_rigid'):
        p[name]=p[name].union(fill).cut(bore).cut(lead).clean()
    cover=wheel_plate('wheel',dimensions=d,back=back,front=front)
    cover=cover.cut(wheel_recess(replace(d,wheel_front=front)))
    ring=axial_cylinder(8.6,back,d.pivot,GAP).cut(axial_cylinder(6.4,back+.01,d.pivot,GAP+.02))
    shell=cover.union(ring).clean()
    keys=[]
    for x in (-KEY_X,KEY_X):
        k=key(x,d,clearance=0.,top=back,bottom=d.wheel_front-KEY_ENGAGEMENT)
        k=k.faces('<Y').edges().chamfer(.1)
        keys.append(k.mirror('XZ'))
        hole=key(x,d,clearance=KEY_CLEARANCE,top=d.wheel_front+.01,
                 bottom=d.wheel_front-KEY_ENGAGEMENT-KEY_BOTTOM_CLEARANCE).mirror('XZ')
        for name in ('rotor','rotor_rigid'):p[name]=p[name].cut(hole).clean()
        cover=cover.union(ring).union(k).clean()
    axle=printed_axle().rotate((0,0,0),(1,0,0),90).translate((0,d.axle_front,d.pivot)).mirror('XZ')
    return dict(p,facecap=cover.mirror('XZ'),facecap_without_keys=shell.mirror('XZ'),
                drive_keys=keys,pivot_axle=axle,control_front=front)


def face_pose(p,angle):
    z=p['dimensions'].pivot
    return p['facecap'].rotate((0,0,z),(0,1,z),angle)


def wheel_print_pose(part,d):
    return part.rotate((0,0,0),(1,0,0),90).translate((0,d.pivot,d.wheel_front))


def cover_print_pose(part,p):
    d=p['dimensions']
    return part.rotate((0,0,0),(1,0,0),90).translate((0,d.pivot,p['control_front']))


def mechanism_layout(p,*,include_nut):
    if type(include_nut) is not bool:raise TypeError(include_nut)
    a=cq.Assembly(name='keyed_scalloped_wheel_and_facecap');d=p['dimensions']
    a.add(wheel_print_pose(p['rotor'],d),name='keyed_wheel')
    a.add(cover_print_pose(p['facecap'],p).translate((45,0,0)),name='matching_facecap')
    a.add(screw_print_pose(printed_axle()).translate((22.5,45,0)),name='longer_socket_screw')
    if include_nut:
        from rotary_printed_fastener_design import printed_nut
        a.add(printed_nut().translate((22.5,65,-5.5)),name='unchanged_printed_nut')
    return a


def full_layout(p):
    d=p['dimensions'];a=cq.Assembly(name='covered_rotary_case_print')
    a.add(p['body'],name='body')
    a.add(p['cap'].rotate((0,0,0),(1,0,0),180).translate((100,0,d.length)),name='cap')
    return a


def assembled(p,*,angle,lift):
    a=cq.Assembly(name='covered_rotary_case')
    for name in ('body','cap','rotor','facecap','pivot_axle','pivot_nut'):
        part=rotor_pose(p,angle) if name=='rotor' else face_pose(p,angle) if name=='facecap' else p[name]
        if name=='cap':part=part.translate((0,0,lift))
        a.add(part,name=name)
    return a
