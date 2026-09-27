"""Three aesthetic alternatives; original postcard_display.py stays authoritative for A.
Shared feet keep the original seating plane, two stops and print orientation.
"""
import cadquery as cq
from postcard_display import (build as original, FOOT_SPACING, FOOT_WIDTH,
    FRONT_Y, REAR_Y, BASE_HEIGHT, BACK_HEIGHT, SLOT_GAP, SLOPE,
    LIP_HEIGHT, LIP_THICKNESS, CONNECTOR_Y, CONNECTOR_DEPTH, CORNER_RADIUS,
    EDGE_BREAK)

FRAME_WINDOW = [(6.0, 8.0), (29.0, 8.0), (14.2, 44.0)]
WAVE_WIDTH = 4.8
WAVE_DEPTH = 5.0
PRISM_TOP_SPACING = 30.0
PRISM_SECTIONS = [(1.2, 28.0, 7.0, 36.5), (18.0, 24.0, 6.0, 32.0),
                  (38.0, 19.0, 4.5, 23.0), (56.6, 15.0, 3.2, 15.8)]


def foundations():
    part = (cq.Workplane('XY').box(FOOT_SPACING, CONNECTOR_DEPTH, BASE_HEIGHT,
                                  centered=(True,True,False))
            .translate((0,CONNECTOR_Y,0)).edges('|Z').fillet(CORNER_RADIUS))
    for x in [-FOOT_SPACING/2, FOOT_SPACING/2]:
        pad = (cq.Workplane('XY').center(x,(FRONT_Y+REAR_Y)/2)
               .rect(FOOT_WIDTH,REAR_Y-FRONT_Y).extrude(BASE_HEIGHT)
               .edges('|Z').fillet(CORNER_RADIUS))
        lip = (cq.Workplane('XY').box(FOOT_WIDTH-1,LIP_THICKNESS,LIP_HEIGHT+0.4,
                                     centered=(True,False,False))
               .translate((x,-LIP_THICKNESS,BASE_HEIGHT-0.4))
               .edges('|Z').fillet(0.35).edges('>Z').chamfer(EDGE_BREAK))
        part = part.union(pad).union(lip)
    return part


def outline():
    # Pointed window closes gradually; no horizontal roof across the opening.
    window = (cq.Workplane('YZ',origin=(-40,0,0)).polyline(FRAME_WINDOW)
              .close().extrude(80).edges('|X').fillet(0.6))
    return original().cut(window).clean()


def wave():
    part = foundations()
    top = BASE_HEIGHT+BACK_HEIGHT
    y_top = SLOT_GAP+BACK_HEIGHT*SLOPE
    y_contact = SLOT_GAP+(BACK_HEIGHT-6)*SLOPE
    for x in [-FOOT_SPACING/2,FOOT_SPACING/2]:
        # Two smooth, nearly constant-depth stems; straight upper contact land.
        stem = (cq.Workplane('YZ',origin=(x-WAVE_WIDTH/2,0,0))
                .moveTo(14,BASE_HEIGHT-0.4)
                .spline([(17,12),(18,25),(16.5,40),(y_contact,top-6)],includeCurrent=True)
                .lineTo(y_top,top).lineTo(y_top+WAVE_DEPTH,top)
                .lineTo(y_contact+WAVE_DEPTH,top-6)
                .spline([(16.5+WAVE_DEPTH,40),(18+WAVE_DEPTH,25),
                         (17+WAVE_DEPTH,12),(14+WAVE_DEPTH,BASE_HEIGHT-0.4)],
                        includeCurrent=True)
                .close().extrude(WAVE_WIDTH).edges('|X').fillet(0.6))
        part = part.union(stem)
    return part.clean()


def prism():
    part = foundations()
    assert PRISM_SECTIONS[-1][1]*2 == PRISM_TOP_SPACING
    for sign in [-1,1]:
        sections = cq.Workplane('XY')
        last_z = 0
        for z,centre,width,rear in PRISM_SECTIONS:
            front = SLOT_GAP+max(0,z-BASE_HEIGHT)*SLOPE+0.10
            # The 0.10 setback protects seating clearance at the base overlap.
            sections = (sections.workplane(offset=z-last_z)
                        .moveTo(sign*centre-width/2,front)
                        .lineTo(sign*centre+width/2,front)
                        .lineTo(sign*centre+width/2,rear)
                        .lineTo(sign*centre-width/2,rear).close())
            last_z = z
        fin = sections.loft(ruled=True).edges('>Z').chamfer(0.3)
        part = part.union(fin)
    return part.clean()

BUILDERS = {'outline':outline, 'wave':wave, 'prism':prism}
