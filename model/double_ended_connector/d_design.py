"""D: eight-piece split-frame connector with captive threaded barrel gates.

The split is an assembly route, not a flexure. Authoritative geometry is built
here. Assembly and print poses share definitions; all units millimeters.
"""
from functools import cache
import cadquery as cq
from assembly_geometry import Configuration
from cad_inspection import Inspection, View, Camera, Frame, Section, Label
from lock_geometry import box, cylinder, screw_thread, along_y

ROOT=2.6; CREST=3.35; PITCH=2.; RADIAL=.22; AXIAL=.12
STEM_X=6.; STEM_Y=5.; STEM_LENGTH=12.; BARREL_LENGTH=14.
SKIRT=4.; STROKE=8.; NOSE_Y=25.; NOSE_RADIUS=1.8
SCREW_X=-7.; SCREW_YS=(-3.8,3.8)
COLORS={'lower':'#263d53','upper':'#526e88','barrel_top':'#138c83',
        'stem_top':'#d29a47','stem_bottom':'#d29a47','barrel_bottom':'#138c83','screw_top':'#cb7629','screw_bottom':'#cb7629'}


def stem_thread(radial=0.,axial=0.,z0=0.,z1=12.):
    return screw_thread(root=ROOT,crest=CREST,pitch=PITCH,z0=z0,z1=z1,
                        radial=radial,axial=axial)


def frame_blank():
    # A 4 mm-thick spine fits through the nominal cord bore; central bosses
    # grow locally to support the printed assembly screws.
    body=box(-7,0,0,4,56,4).edges('|Z').fillet(1.)
    body=body.union(box(0,0,0,20,10,8).edges('|Z').fillet(.8))
    crown=box(-.5,29,0,17,4,4).edges('|Z').fillet(.9)
    nose=along_y(cylinder(NOSE_RADIUS,NOSE_Y,30),STEM_X,0)
    end=crown.union(nose)
    body=body.union(end).union(end.rotate((0,0,0),(1,0,0),180))
    # Notched sockets capture independently assembled stem roots. Narrow ribs
    # sit INSIDE the stem groove, with axial and radial clearance.
    socket=box(STEM_X,2.55,0,4.3,5.1,4.3)
    rib_zone=box(STEM_X,1.9,0,10,.4,10)
    socket=socket.cut(rib_zone).union(box(STEM_X,1.9,0,3.1,.4,3.1))
    body=body.cut(socket).cut(socket.rotate((0,0,0),(1,0,0),180))
    for y in SCREW_YS:
        boss=cylinder(4.,-4.,4.).translate((SCREW_X,y,0))
        body=body.union(boss)
    return body.clean()


def stem():
    root=box(0,0,-2.4,4.,4.,4.8).edges('|Z').fillet(.4)
    # Circumferential relief is captured by rigid ribs in both frame halves.
    ring=box(0,0,-3.1,6,6,.8).cut(box(0,0,-3.1,2.8,2.8,1.))
    root=root.cut(ring)
    return root.union(stem_thread()).union(cylinder(4.,12.,12.6)).clean()


def assembly_screw():
    shaft=screw_thread(root=2.,crest=2.7,pitch=1.6,z0=-4.,z1=3.5)
    head=cylinder(3.5,-6.4,-4.).edges('%Circle').fillet(.35)
    # Broad thumb grip; intentionally no driver/tool interface.
    for i in range(8):
        tool=cylinder(.55,-6.5,-3.9).translate((3.65,0,0)).rotate((0,0,0),(0,0,1),45*i)
        head=head.cut(tool)
    return head.union(shaft).clean()


def barrel():
    outer=cylinder(5.4,0,BARREL_LENGTH).edges('%Circle').chamfer(.35)
    tool=stem_thread(RADIAL,AXIAL,z0=-.2,z1=SKIRT+.03)
    tool=tool.union(cylinder(4.25,SKIRT,BARREL_LENGTH+.2))
    outer=outer.cut(tool)
    # Recessed finger grooves keep the envelope smooth and improve grip.
    for i in range(12):
        tool=cylinder(.55,.5,BARREL_LENGTH-.5).translate((5.55,0,0)).rotate((0,0,0),(0,0,1),30*i)
        outer=outer.cut(tool)
    return outer.clean()


@cache
def parts():
    body=frame_blank()
    lower=body.intersect(box(0,0,-10,60,80,20))
    upper=body.intersect(box(0,0,10,60,80,20))
    female=screw_thread(root=2.,crest=2.7,pitch=1.6,z0=-.15,z1=3.7,radial=.20,axial=.10)
    for y in SCREW_YS:
        lower=lower.cut(cylinder(2.95,-4.2,.2).translate((SCREW_X,y,0)))
        upper=upper.cut(female.translate((SCREW_X,y,0)))
    return {'lower':lower.clean(),'upper':upper.clean(),
            'barrel':barrel(),'stem':stem(),'screw':assembly_screw()}


def gate_pose(part, travel, sign):
    # Right-hand screw: rotation and translation must advance together.
    posed=part.rotate((0,0,0),(0,0,1),360*travel/PITCH).translate((0,0,travel))
    posed=along_y(posed,STEM_X,STEM_Y)
    return posed if sign==1 else posed.rotate((0,0,0),(1,0,0),180)


def configuration(*, top_travel, bottom_travel, exploded=False):
    if not all(0<=v<=STROKE for v in (top_travel,bottom_travel)):
        raise ValueError('D gate travel must be 0..8 mm')
    p=parts(); a=cq.Assembly(name='D_barrel_connector')
    for name in ('lower','upper'):
        z=(-9 if name=='lower' else 9) if exploded else 0
        a.add(p[name].translate((0,0,z)),name=name)
    for sign,name in ((1,'stem_top'),(-1,'stem_bottom')):
        part=along_y(p['stem'],STEM_X,STEM_Y)
        if sign==-1:part=part.rotate((0,0,0),(1,0,0),180)
        a.add(part,name=name)
    for name,travel,sign in [('barrel_top',top_travel,1),('barrel_bottom',bottom_travel,-1)]:
        a.add(gate_pose(p['barrel'],travel,sign),name=name)
    for name,y in zip(('screw_bottom','screw_top'),SCREW_YS):
        a.add(p['screw'].translate((SCREW_X,y,-16 if exploded else 0)),name=name)
    return Configuration.explicit(a,name='exploded' if exploded else 'operating',
                                  parameters={'top_travel':top_travel,'bottom_travel':bottom_travel})


def print_layout():
    p=parts(); a=cq.Assembly(name='D_eight_parts_print_layout')
    a.add(p['upper'],name='upper')
    a.add(p['lower'].rotate((0,0,0),(1,0,0),180).translate((30,0,0)),name='lower')
    for i in range(2):
        a.add(p['barrel'].translate((52,15*i-8,0)),name=f'barrel_{i+1}')
        a.add(p['screw'].translate((68,15*i-8,6.4)),name=f'screw_{i+1}')
        a.add(p['stem'].translate((82,15*i-8,4.8)),name=f'stem_{i+1}')
    return a


def inspection(state):
    settings={'closed':(STROKE,STROKE,False),'open':(0,STROKE,False),
              'assembly':(0,0,True),'section':(STROKE,STROKE,False)}
    if state not in settings:raise ValueError(state)
    t,b,e=settings[state]; config=configuration(top_travel=t,bottom_travel=b,exploded=e)
    section=Section((0,0,0),(0,0,1),mode='planar') if state=='section' else None
    camera=Camera((.8,-1.3,2.2),up=(0,1,0)) if state!='section' else Camera((0,0,1),up=(0,1,0))
    labels=(Label((STEM_X,21,0),'6 mm clear mouth' if state=='open' else 'Captive threaded barrel',offset_px=(35,-20)),)
    selected=('stem_top','barrel_top') if state=='section' else ()
    colors=tuple((k,v) for k,v in COLORS.items() if not selected or k in selected)
    if state=='section':
        labels=(Label((6,23,0),'Wide nose cup',offset_px=(50,0)),
                Label((6,15,0),'Threaded skirt',offset_px=(50,20)),
                Label((6,17.3,0),'Keeper shoulder',offset_px=(-160,-10)),
                Label((6,2,0),'Keyed root',offset_px=(50,0)))
    return Inspection(config,View(camera,components=selected,colors=colors,section=section,
                                 frame=Frame(margin_mm=4),annotations=labels),
                      purpose='Explain D assembled, open and assembly relationships.',
                      title={'closed':'D — both ends assembled and closed','open':'D — upper barrel retracted four turns',
                             'assembly':'D — lay stem/barrel units into lower frame, close upper frame, fit two hand screws',
                             'section':'D — actual planar section of one barrel and stem; frame omitted'}[state])
