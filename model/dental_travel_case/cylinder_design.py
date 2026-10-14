"""Plain two-piece threaded dental cylinder. Millimetres; no internal organizers.

Thread construction follows the repository Vaseline jar's swept flank method;
new diameter/depth/parts need their own CAD, slicing and physical qualification.
"""
import math
import cadquery as cq
from components import compound

HEIGHT=264.0
SEAM=HEIGHT/2
FLOOR=2.4
INNER_RADIUS=44.0
BODY_RADIUS=47.2
COLLAR_RADIUS=50.2
NECK_RADIUS=46.0
NECK_TOP=SEAM+13.0
RADIAL_CLEARANCE=.30
AXIAL_CLEARANCE=.25
THREAD_DEPTH=.8
THREAD_HALF_WIDTH=1.0
PITCH=3.0
THREAD_START=SEAM+2.5
THREAD_TRAVEL=4.5
FLUTE_COUNT=16
FLUTE_RADIUS=8.0
FLUTE_DEPTH=1.0
PART_SPACING=110.0
# Conservative 30 mm handle + 60 x 44 mm tube cross-sections, 0.5 mm apart.
PACKING_OFFSET=((22+30+.5)**2-30**2-22**2)/(2*((22+30+.5)+22))
TUBE_Y=-PACKING_OFFSET
BRUSH_Y=22+15+.5-PACKING_OFFSET


def circle_wire(radius,z):
    return cq.Workplane('XY',origin=(0,0,z)).circle(radius).val()


def exterior(*, straight_height,total_height):
    part=(cq.Workplane('XY').circle(BODY_RADIUS).extrude(straight_height)
          .edges('<Z').chamfer(.35))
    rise=12.0
    levels=(0,.25,.5,.75,1)
    wires=[circle_wire(BODY_RADIUS+(COLLAR_RADIUS-BODY_RADIUS)*(3*t*t-2*t*t*t),
                       straight_height+rise*t) for t in levels]
    part=part.union(cq.Workplane(obj=cq.Solid.makeLoft(wires)))
    collar_start=straight_height+rise
    part=part.union(cq.Workplane('XY',origin=(0,0,collar_start)).circle(COLLAR_RADIUS)
                    .extrude(total_height-collar_start))
    # Tapered groove ends avoid a horizontal refill ledge above each recess.
    for i in range(FLUTE_COUNT):
        angle=2*math.pi*i/FLUTE_COUNT
        ux,uy=math.cos(angle),math.sin(angle)
        def wire(radial,z):
            return cq.Workplane('XY',origin=(ux*radial,uy*radial,z)).circle(FLUTE_RADIUS).val()
        centre=BODY_RADIUS+FLUTE_RADIUS
        start=cq.Solid.makeLoft([wire(centre-.01,2),wire(centre-FLUTE_DEPTH,6)],ruled=True)
        mid=(cq.Workplane('XY',origin=(ux*(centre-FLUTE_DEPTH),uy*(centre-FLUTE_DEPTH),6))
             .circle(FLUTE_RADIUS).extrude(straight_height-12))
        end=cq.Solid.makeLoft([wire(centre-FLUTE_DEPTH,straight_height-6),wire(centre-.01,straight_height)],ruled=True)
        collar_centre=COLLAR_RADIUS+FLUTE_RADIUS
        taper=cq.Solid.makeLoft([wire(collar_centre-.01,collar_start),
                               wire(collar_centre-FLUTE_DEPTH,collar_start+4)],ruled=True)
        upper=(cq.Workplane('XY',origin=(ux*(collar_centre-FLUTE_DEPTH),uy*(collar_centre-FLUTE_DEPTH),collar_start+4))
               .circle(FLUTE_RADIUS).extrude(total_height-collar_start-4+1))
        # Separate touching cutter segments are not a fused Boolean tool.
        # Cut sequentially rather than send their shared faces as a compound.
        for cutter in (start,mid,end,taper,upper):
            part=part.cut(cutter)
    assert part.val().isValid() and len(part.solids().vals())==1,'Scalloped exterior construction'
    return part


def thread(*, cutter):
    extra=RADIAL_CLEARANCE if cutter else 0
    half=THREAD_HALF_WIDTH+(AXIAL_CLEARANCE+extra if cutter else 0)
    # Two full lead turns cover the upper flank as the cap mouth passes the
    # finite male helix's first turn; one lead turn left a tiny entry collision.
    lead=2*PITCH if cutter else 0
    path=cq.Wire.makeHelix(PITCH,THREAD_TRAVEL+lead,NECK_RADIUS)
    profile=(cq.Workplane('XZ').polyline([(NECK_RADIUS-.12,-half),
                                         (NECK_RADIUS+THREAD_DEPTH+extra,0),
                                         (NECK_RADIUS-.12,half)]).close())
    return profile.sweep(cq.Workplane(obj=path),isFrenet=True).translate((0,0,THREAD_START-lead))


def build():
    base=exterior(straight_height=112,total_height=SEAM)
    neck=(cq.Workplane('XY',origin=(0,0,SEAM-.1)).circle(NECK_RADIUS)
          .extrude(NECK_TOP-SEAM+.1).edges('>Z').chamfer(.4))
    base=base.union(neck).union(thread(cutter=False))
    bore=cq.Workplane('XY',origin=(0,0,FLOOR)).circle(INNER_RADIUS).extrude(HEIGHT)
    base=base.cut(bore)
    mouth=[e for e in base.val().Edges() if e.geomType()=='CIRCLE' and
           abs(e.Center().z-NECK_TOP)<1e-5 and abs(e.radius()-INNER_RADIUS)<1e-5]
    base=base.newObject(mouth).fillet(.4)
    print_lid=exterior(straight_height=106,total_height=HEIGHT-SEAM)
    print_lid=print_lid.cut(cq.Workplane('XY',origin=(0,0,FLOOR))
                          .circle(INNER_RADIUS).extrude(HEIGHT))
    lid=print_lid.rotate((0,0,0),(1,0,0),180).translate((0,0,HEIGHT))
    female_bore=(cq.Workplane('XY',origin=(0,0,SEAM-1)).circle(NECK_RADIUS+RADIAL_CLEARANCE)
                 .extrude(15))
    lid=lid.cut(female_bore).cut(thread(cutter=True))
    print_lid=lid.rotate((0,0,0),(1,0,0),180).translate((0,0,HEIGHT))
    return dict(base=base,lid=lid,print_lid=print_lid,
                result=compound(base,print_lid.translate((PART_SPACING,0,0))))


def references():
    # Held items display only: side by side, bristles kept attached.
    butt=FLOOR+1
    handle=cq.Workplane('XY',origin=(0,BRUSH_Y,butt)).circle(15).extrude(165)
    neck=cq.Workplane('XY').box(15,15,62,centered=(True,True,False)).translate((0,BRUSH_Y,butt+165))
    head=cq.Workplane('XY').box(15,25,28,centered=(True,True,False)).translate((0,BRUSH_Y+1,butt+227))
    tube=cq.Workplane('XY').box(60,44,160,centered=(True,True,False)).translate((0,TUBE_Y,FLOOR))
    return dict(handle=handle,neck=neck,head=head,tube=tube)


def assembly(case,*,opening_degrees,loaded):
    lid=(case['lid'].rotate((0,0,0),(0,0,1),opening_degrees)
         .translate((0,0,PITCH*opening_degrees/360)))
    a=cq.Assembly(name='plain_dental_cylinder').add(case['base'],name='lower_half').add(lid,name='upper_half')
    if loaded:
        for name,p in references().items():
            a.add(p,name=name)
    return a


def thread_test(case):
    # Shorten only the plain spans; preserve full mating band and print direction.
    z0=112.0
    top=156.0
    low=case['base'].intersect(cq.Workplane('XY').box(140,140,NECK_TOP-z0+1,centered=(True,True,False)).translate((0,0,z0)))
    low=low.union(cq.Workplane('XY',origin=(0,0,z0)).circle(BODY_RADIUS).extrude(FLOOR))
    upper=case['lid'].intersect(cq.Workplane('XY').box(140,140,top-SEAM,centered=(True,True,False)).translate((0,0,SEAM)))
    upper=upper.union(cq.Workplane('XY',origin=(0,0,top-FLOOR)).circle(BODY_RADIUS).extrude(FLOOR))
    return compound(low.translate((0,0,-z0)),
                    upper.rotate((0,0,0),(1,0,0),180).translate((PART_SPACING,0,top)))
