"""K dome-shoulder follower components and inspection-only mixed assembly.

This entry is inspection only; cap_k_base_5.py selects only the printable base.
Includes simplified reference cards with the actual source's spherical recess;
no engraving/text surfaces are invented. PETG .4/.2 assumed for concept sizing.
"""
import math
import cadquery as cq
import cap_j_base_5 as j
import cap_i_grip_keys as i
from study import card_reference,swatch_dimension
from physical_analysis.screening import rectangular_cantilever

SPHERE_RADIUS = 8.0
DOME_SOURCE_X = swatch_dimension('card_width')-66.0
DOME_SOURCE_Y = 9.0
DOME_SOURCE_HEIGHT = swatch_dimension('base_thickness')+6.0
DOME_X = swatch_dimension('card_height')/2-DOME_SOURCE_Y
DOME_Z = j.slots.FLOOR+DOME_SOURCE_X
CARD_THICKNESS = swatch_dimension('base_thickness')
CARD_BACK_Y = -j.slots.SLOT_WIDTH/2
CARD_FRONT_Y = CARD_BACK_Y+CARD_THICKNESS
POCKET_CENTRE_Y = CARD_BACK_Y+DOME_SOURCE_HEIGHT
SHOULDER_INNER_RADIUS = 3.8  # Shoulder-material reference, not a knife-edge crown.
SHOULDER_OUTER_RADIUS = 4.4
SEATED_TRAVEL_Y = .25  # Coordinate-Y spring travel, not sphere-normal gap.
PANEL_WIDTH = j.PANEL_WIDTH
PANEL_THICKNESS = .8
PANEL_HEIGHT = 18.6
RELIEF_BACK_Y = 4.6
CARRIER_START_Z = j.slots.FLOOR+10.0
CARRIER_FRONT_Y = 0.0
CARRIER_HALF_WIDTH = 4.0
BACKING_CLEARANCE_Y = .15
BACKING_FRONT_Y = -.3
NOSE_RADIUS = 1.8
NOSE_CONTACT_RADIUS = 4.4
ENTRY_HEIGHT = 2.1  # Lower lead grows to full contact at the dome side shoulders.

assert SHOULDER_INNER_RADIUS<SHOULDER_OUTER_RADIUS<math.sqrt(SPHERE_RADIUS**2-6**2)
assert DOME_X+SHOULDER_OUTER_RADIUS<j.PANEL_WIDTH/2+j.RELIEF_SIDE_GAP


def dome_ball(y=0,travel=0):
    return (cq.Workplane('XY').sphere(SPHERE_RADIUS)
            .translate((DOME_X,y+POCKET_CENTRE_Y-travel,DOME_Z)))


def dome_card(y=0):
    # Relative to J, the front/detailed face now faces the positive-Y follower.
    card=card_reference().translate((0,(CARD_BACK_Y+CARD_FRONT_Y)/2,0))
    # Build once at the local origin, then place it. Cutting a sphere tangent
    # to the thin back at each global coordinate creates avoidable OCC noise.
    return card.cut(dome_ball()).translate((0,y,0))


def nose_centres():
    # Internally tangent small convex spheres in the concave R8 source bowl.
    # Their rounded fronts avoid the high local bending of the first annular lip.
    scale=(SPHERE_RADIUS-NOSE_RADIUS)/SPHERE_RADIUS
    dy=-math.sqrt(SPHERE_RADIUS**2-NOSE_CONTACT_RADIUS**2)*scale
    return [(DOME_X+side*NOSE_CONTACT_RADIUS*scale,
             POCKET_CENTRE_Y-SEATED_TRAVEL_Y+dy,DOME_Z) for side in(-1,1)]


def free_nose_y():
    return nose_centres()[0][1]-NOSE_RADIUS


def shoulder_crown(y=0):
    """Two rounded shoulders, internally tangent to the bowl away from its center."""
    noses=[cq.Workplane('XY').sphere(NOSE_RADIUS).translate((x,cy+y,z))
           for x,cy,z in nose_centres()]
    pair=cq.Workplane('XY').newObject([j.g.compound(*noses)])
    # Keep the outer flank inside the spring relief and cap the rear at the
    # carrier plane. Contact crests and internal-tangent bowl points remain.
    return pair.intersect(j.g.block(-PANEL_WIDTH/2-j.RELIEF_SIDE_GAP+.1,
        PANEL_WIDTH/2+j.RELIEF_SIDE_GAP-.1,y-3,y+j.ROOT_Y+.05,DOME_Z-3,DOME_Z+3))


def crown_backing(y=0):
    """Support the shoulder nose without contacting the bowl center or carrier edges."""
    low=DOME_Z-ENTRY_HEIGHT
    high=DOME_Z+SHOULDER_OUTER_RADIUS+.1
    points=[(CARRIER_FRONT_Y,low),(j.ROOT_Y+.05,low),
            (j.ROOT_Y+.05,high),(BACKING_FRONT_Y,high),(BACKING_FRONT_Y,DOME_Z)]
    wedge=(cq.Workplane('YZ',origin=(DOME_X-SHOULDER_OUTER_RADIUS,y,0))
           .polyline(points).close().extrude(2*SHOULDER_OUTER_RADIUS))
    # The backing's sphere lies behind the card's source sphere. It carries the
    # thin shoulder crown yet leaves positive clearance around the bowl center.
    return wedge.intersect(dome_ball(y,-BACKING_CLEARANCE_Y))


def card_panel(y=0):
    stem=j.g.block(-PANEL_WIDTH/2,PANEL_WIDTH/2,
        y+j.ROOT_Y,y+j.ROOT_Y+PANEL_THICKNESS,
        j.slots.FLOOR-j.ROOT_OVERLAP,j.slots.FLOOR+PANEL_HEIGHT)
    stem=stem.faces('>Z').edges('|X').fillet(.2)
    # Shallow carrier reaches the crown from below but stops short of touching
    # the spherical pocket. Its deepest surface is Y=0, far from the thin center.
    points=[(j.ROOT_Y,CARRIER_START_Z),(j.ROOT_Y,DOME_Z-ENTRY_HEIGHT+.15),
            (CARRIER_FRONT_Y,DOME_Z-ENTRY_HEIGHT+.15),(CARRIER_FRONT_Y,DOME_Z-ENTRY_HEIGHT)]
    carrier=(cq.Workplane('YZ',origin=(DOME_X-CARRIER_HALF_WIDTH,y,0))
             .polyline(points).close().extrude(2*CARRIER_HALF_WIDTH))
    return stem.union(carrier).union(crown_backing(y)).union(shoulder_crown(y))


def rough_base(include_panels=True,include_detents=True):
    # Mirror the panel-free J seating geometry so its reliefs are on the detailed
    # side; foot, hood contacts and H ports are symmetric under this mirror.
    part=j.base(include_panels=False,include_detents=include_detents).mirror('XZ')
    for index in range(j.COUNT):
        y=j.slots.slot_y(index,j.COUNT)
        relief=j.g.block(-PANEL_WIDTH/2-j.RELIEF_SIDE_GAP,
            PANEL_WIDTH/2+j.RELIEF_SIDE_GAP,y+j.ROOT_Y-.05,y+RELIEF_BACK_Y,
            j.slots.FLOOR,j.g.TOP_Z+.2).edges('|X and <Z').fillet(j.ROOT_BLEND)
        part=part.cut(relief)
        if include_panels:
            part=part.union(card_panel(y))
    return part


def travel_screen(thickness=CARD_THICKNESS):
    # Existing source sphere centre follows the front face: thickness variation
    # changes required seated movement rather than being absorbed by a gap.
    seated=SEATED_TRAVEL_Y+thickness-CARD_THICKNESS
    crown_min_y=free_nose_y()
    peak=thickness-j.slots.SLOT_WIDTH/2-crown_min_y
    return dict(seated_travel_y_mm=seated,pass_flat_face_travel_y_mm=peak,
        available_rear_space_mm=RELIEF_BACK_Y-j.ROOT_Y-PANEL_THICKNESS,
        seated_beam=rectangular_cantilever(length_mm=DOME_SOURCE_X-j.ROOT_BLEND,
            width_mm=PANEL_WIDTH,thickness_mm=PANEL_THICKNESS,
            youngs_modulus_MPa=1200,tip_displacement_mm=seated),
        passage_beam=rectangular_cantilever(length_mm=DOME_SOURCE_X-j.ROOT_BLEND,
            width_mm=PANEL_WIDTH,thickness_mm=PANEL_THICKNESS,
            youngs_modulus_MPa=1200,tip_displacement_mm=peak))


def assembled_study():
    # One complete box exposes the changed relationship; adjacent modules, cap
    # geometry and keys do not change. Crowns overlap relaxed cards intentionally.
    b=rough_base()
    pose_y=i.module_centres()[0]
    items=[b.translate((0,pose_y,0))]
    for index in (0,2,4):
        items.append(dome_card(j.slots.slot_y(index,j.COUNT)+pose_y))
    # Existing accepted closed J box gives whole-product context without another
    # full K build or new hood/connector mechanism.
    other=i.module_centres()[1]
    items.extend((j.base().translate((0,other,0)),j.g.cap().translate((0,other,0)),i.seated_key(3)))
    return j.g.compound(*items)


if __name__ in ('__main__','__cqgi__'):
    result=assembled_study()
