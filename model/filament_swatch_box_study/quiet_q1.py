"""Q1 complete archive prototype: PETG base/hood, separately printed TPU 95A jacket.

Millimetres, assembled origin at the centre of the floor. Card pocket and entry
come from accepted archive A. New closure geometry is unprinted. No material
bond is required. The three component entry points select separate print jobs.
"""
import cadquery as cq
import archive_corner_proposals as archive
import cap_h_module_5 as h
import cap_i_grip_keys as keys
import recessed_grips as grips
import swatch_reference as ref

g = archive.r1.g
CORE_X, CORE_Y = g.OUTER_WIDTH, g.BODY_DEPTH
CORE_R = 5.0
CORE_TOP = archive.TOP
FOOT_TOP = g.SEAM_Z
JACKET_FIT = .10  # Per side, free sleeve cavity; not a friction-retention fit.
JACKET_WALL = 1.20
JACKET_X = CORE_X + 2*(JACKET_FIT+JACKET_WALL)
JACKET_Y = CORE_Y + 2*(JACKET_FIT+JACKET_WALL)
JACKET_R = CORE_R+JACKET_FIT+JACKET_WALL
RUNNER_PROJECTION = .40
RUNNER_WIDTH = 3.20
RUNNER_GAP = .25  # Per side at full runner projection; no intended travel preload.
HOOD_INNER_X = JACKET_X+2*(RUNNER_PROJECTION+RUNNER_GAP)
HOOD_INNER_Y = JACKET_Y+2*(RUNNER_PROJECTION+RUNNER_GAP)
HOOD_INNER_R = JACKET_R+RUNNER_PROJECTION+RUNNER_GAP
LOWER_WALL = 1.60
UPPER_WALL = .80
HOOD_X = HOOD_INNER_X+2*LOWER_WALL
HOOD_Y = HOOD_INNER_Y+2*LOWER_WALL
HOOD_R = HOOD_INNER_R+LOWER_WALL
FOOT_X = HOOD_X+1.0
FOOT_Y = 52.0  # Keeps the accepted key's vertical route outside the soft jacket.
SEAT_THICKNESS = .80
SEAT_TOP = FOOT_TOP+SEAT_THICKNESS
JACKET_TOP = CORE_TOP+.80
BEAD_Y = (-11.0,11.0)
BEAD_WIDTH = 8.0
BEAD_BOTTOM = 12.0
BEAD_LOWER = 13.4
BEAD_UPPER = 13.8
BEAD_TOP = 15.4
BEAD_ENGAGEMENT = .25  # Radial travel past hood wall at centred release.
BEAD_TIP_X = HOOD_INNER_X/2+BEAD_ENGAGEMENT
POCKET_DEPTH = .55
FLEX_CLEARANCE = .80  # Rigid recess behind the TPU diaphragm.
ANCHOR_DEPTH = .65  # From free sleeve cavity; .55 nominal overlap with core.
ANCHOR_BOTTOM, ANCHOR_TOP = 6.4,9.0
ANCHOR_GROOVE_DEPTH = .80
PRINT_CENTRE = (135,135,0)


def rounded(width,depth,height,z,radius):
    return g.rounded_block(width,depth,height,z,radius)


def block(x0,x1,y0,y1,z0,z1):
    return g.block(x0,x1,y0,y1,z0,z1)


def loft(sections):
    """Rounded rectangle wires (z,width,depth,radius), ruled between stations."""
    work=cq.Workplane('XY')
    for z,width,depth,radius in sections:
        work=work.add(archive.r1.rounded_wire(width,depth,radius,z))
    return work.toPending().loft(ruled=True)


def anchor_core():
    """Rigid neck within the circumferential retaining groove, sloped shoulders."""
    d=ANCHOR_GROOVE_DEPTH
    return loft([(ANCHOR_BOTTOM,CORE_X,CORE_Y,CORE_R),
                 (ANCHOR_BOTTOM+d,CORE_X-2*d,CORE_Y-2*d,CORE_R-d),
                 (ANCHOR_TOP-d,CORE_X-2*d,CORE_Y-2*d,CORE_R-d),
                 (ANCHOR_TOP,CORE_X,CORE_Y,CORE_R)])


def socket(end):
    # Translate the actual accepted H socket, including floor and nail recess.
    return h.socket(end).translate((0,end*(FOOT_Y-g.FOOT_DEPTH)/2,0))


def grip_cut(side):
    return grips.pocket(side).translate((side*(FOOT_X-g.FOOT_X)/2,0,0))


def finger(side):
    return grips.finger(side).translate((side*(FOOT_X-g.FOOT_X)/2,0,0))


def flex_recess(y,side):
    face=CORE_X/2
    # The sloped ceiling grows in the base's floor-down print direction.
    profile=[(face-FLEX_CLEARANCE,BEAD_BOTTOM-.8),
             (face+1.5,BEAD_BOTTOM-.8),(face+1.5,BEAD_TOP+1.6),
             (face,BEAD_TOP+1.6),(face-FLEX_CLEARANCE,BEAD_TOP+.8)]
    tool=(cq.Workplane('XZ',origin=(0,y+BEAD_WIDTH/2+.6,0))
          .polyline(profile).close().extrude(BEAD_WIDTH+1.2))
    return g.mirrored(tool,side)


def base():
    body=(rounded(CORE_X,CORE_Y,CORE_TOP,0,CORE_R).cut(archive.pocket())
          .faces('>Z').edges().fillet(archive.RIM_RADIUS))
    foot=(rounded(FOOT_X,FOOT_Y,FOOT_TOP,0,HOOD_R+.5)
          .faces('<Z').edges().chamfer(.8)
          .faces('>Z').edges().fillet(.6))
    # Hollow the foot above the accepted card floor; never lift the cards.
    foot=foot.cut(archive.pocket())
    body=body.union(foot)
    outer=rounded(CORE_X+4,CORE_Y+4,ANCHOR_TOP-ANCHOR_BOTTOM,
                  ANCHOR_BOTTOM,CORE_R+2)
    body=body.cut(outer.cut(anchor_core()))
    for y in BEAD_Y:
        for side in (-1,1):
            body=body.cut(flex_recess(y,side))
    for side in (-1,1):
        body=body.cut(grip_cut(side)).cut(socket(side))
    return body


def bead(y,side):
    face=JACKET_X/2
    profile=[(face-.15,BEAD_BOTTOM),(face,BEAD_BOTTOM),
             (BEAD_TIP_X,BEAD_LOWER),(BEAD_TIP_X,BEAD_UPPER),
             (face,BEAD_TOP),(face-.15,BEAD_TOP)]
    part=(cq.Workplane('XZ',origin=(0,y+BEAD_WIDTH/2,0))
          .polyline(profile).close().extrude(BEAD_WIDTH)
          .edges('|Y').filter(lambda e:e.Center().x>face+.1).fillet(.15))
    return g.mirrored(part,side)


def jacket(include_beads=True):
    outer=rounded(JACKET_X,JACKET_Y,JACKET_TOP-SEAT_TOP,SEAT_TOP,JACKET_R)
    inner=loft([(SEAT_TOP-.01,CORE_X+2*JACKET_FIT,CORE_Y+2*JACKET_FIT,CORE_R+JACKET_FIT),
                (CORE_TOP,CORE_X+2*JACKET_FIT,CORE_Y+2*JACKET_FIT,CORE_R+JACKET_FIT),
                (JACKET_TOP+.01,CORE_X-1.0,CORE_Y-1.0,CORE_R-.5)])
    part=outer.cut(inner)
    seat=rounded(HOOD_X,HOOD_Y,SEAT_THICKNESS,FOOT_TOP,HOOD_R)
    seat=seat.cut(rounded(CORE_X+2*JACKET_FIT,CORE_Y+2*JACKET_FIT,
                         SEAT_THICKNESS+.02,FOOT_TOP-.01,CORE_R+JACKET_FIT))
    part=part.union(seat)
    # Broad circumferential snap anchors the insert; local hood beads release first.
    d=ANCHOR_DEPTH
    anchor_outer=rounded(JACKET_X,JACKET_Y,ANCHOR_TOP-ANCHOR_BOTTOM,
                         ANCHOR_BOTTOM,JACKET_R)
    free_x,free_y,free_r=CORE_X+2*JACKET_FIT,CORE_Y+2*JACKET_FIT,CORE_R+JACKET_FIT
    anchor_inner=loft([(ANCHOR_BOTTOM,free_x,free_y,free_r),
                       (ANCHOR_BOTTOM+d,free_x-2*d,free_y-2*d,free_r-d),
                       (ANCHOR_TOP-d,free_x-2*d,free_y-2*d,free_r-d),
                       (ANCHOR_TOP,free_x,free_y,free_r)])
    part=part.union(anchor_outer.cut(anchor_inner))
    length=CORE_TOP-SEAT_TOP
    for side in (-1,1):
        for x in (-20.,0.,20.):
            runner=(rounded(RUNNER_WIDTH,2*RUNNER_PROJECTION,length,SEAT_TOP,.35)
                    .faces('>Z').edges().fillet(.30)
                    .translate((x,side*JACKET_Y/2,0)))
            part=part.union(runner)
        runner=(rounded(2*RUNNER_PROJECTION,RUNNER_WIDTH,length,SEAT_TOP,.35)
                .faces('>Z').edges().fillet(.30)
                .translate((side*JACKET_X/2,0,0)))
        part=part.union(runner)
        if include_beads:
            for y in BEAD_Y:
                part=part.union(bead(y,side))
    return part.cut(socket(1)).cut(socket(-1))


def hood_pocket(y,side):
    x=HOOD_INNER_X/2
    profile=[(x-.1,BEAD_BOTTOM-.3),(x,BEAD_BOTTOM-.3),
             (x+POCKET_DEPTH,BEAD_LOWER-.2),(x+POCKET_DEPTH,BEAD_UPPER+.2),
             (x,BEAD_TOP+.3),(x-.1,BEAD_TOP+.3)]
    tool=(cq.Workplane('XZ',origin=(0,y+BEAD_WIDTH/2+.4,0))
          .polyline(profile).close().extrude(BEAD_WIDTH+.8))
    return g.mirrored(tool,side)


def hood():
    outer=(rounded(HOOD_X,HOOD_Y,g.ROOF_TOP-SEAT_TOP,SEAT_TOP,HOOD_R)
           .faces('>Z').edges().fillet(g.ROOF_RADIUS)
           .faces('<Z').edges().fillet(.2))
    band_top=24.0
    lower=rounded(HOOD_INNER_X,HOOD_INNER_Y,band_top-SEAT_TOP+.1,
                  SEAT_TOP-.1,HOOD_INNER_R)
    upper=(rounded(HOOD_X-2*UPPER_WALL,HOOD_Y-2*UPPER_WALL,
                   g.ROOF_UNDERSIDE-(band_top-.8),band_top-.8,HOOD_R-UPPER_WALL)
           .faces('>Z').edges().fillet(g.ROOF_RADIUS-UPPER_WALL)
           .faces('<Z').edges().chamfer(.8))
    mouth=(rounded(HOOD_INNER_X+1.0,HOOD_INNER_Y+1.0,1.3,
                   SEAT_TOP-.1,HOOD_INNER_R+.5)
           .faces('>Z').edges().chamfer(.5))
    part=outer.cut(lower.union(upper).union(mouth))
    for y in BEAD_Y:
        for side in (-1,1):
            part=part.cut(hood_pocket(y,side))
    return part


def cards():
    card=ref.card(-ref.THICKNESS/2)
    return [card.translate((0,(i-7)*ref.THICKNESS,0)) for i in range(15)]


def print_base():
    return base().translate(PRINT_CENTRE)


def print_jacket():
    return jacket().translate((PRINT_CENTRE[0],PRINT_CENTRE[1],-FOOT_TOP))


def print_hood():
    return g.hood_print(hood()).translate(PRINT_CENTRE)
