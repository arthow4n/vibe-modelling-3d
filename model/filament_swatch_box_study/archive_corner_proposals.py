"""Archive R2 shared parametric builders: four 15-card retaining forms.

Same floor/pocket/G exterior envelope/key targets. Low walls match J4's nominal
body top. Tall corners are L-shaped returns, not individual card slots.
Print floor down in PETG, .4 mm nozzle/.2 mm layers, two walls/7% adaptive cubic.
Printable entry points select only the base; reference cards are inspection-only.
"""
import cadquery as cq
import archive_r1_base_15 as r1

FLOOR = r1.FLOOR
TALL_HEIGHT = 40.0
LOW_TOP = r1.g.TOP_Z  # Actual J-family nominal body top: Z20.4, 18 above floor.
TOP = FLOOR+TALL_HEIGHT
ENTRY_HEIGHT = 2.0
ENTRY_EXPANSION = r1.FUNNEL_EXPANSION
WINDOW_ROOT_RADIUS = 2.0
WINDOW_PLAN_RADIUS = 1.0
RIM_RADIUS = .6
PROPOSALS = {'continuous':None,'slim':(4.,3.),'corner':(8.,6.),
             'side_guides':(8.,r1.POCKET_DEPTH/2)}


def pocket():
    straight_top = TOP-ENTRY_HEIGHT
    lower = r1.g.rounded_block(r1.POCKET_WIDTH,r1.POCKET_DEPTH,
        straight_top-FLOOR+.02,FLOOR,r1.POCKET_RADIUS)
    a = r1.rounded_wire(r1.POCKET_WIDTH,r1.POCKET_DEPTH,r1.POCKET_RADIUS,straight_top)
    b = r1.rounded_wire(r1.POCKET_WIDTH+2*ENTRY_EXPANSION,
        r1.POCKET_DEPTH+2*ENTRY_EXPANSION,r1.POCKET_RADIUS+ENTRY_EXPANSION,TOP)
    return lower.union(cq.Workplane('XY').add(a).add(b).toPending().loft())


def cut_windows(body,returns):
    if returns is None:
        return body
    rx,ry = returns
    xgap = r1.POCKET_WIDTH-2*rx
    ygap = r1.POCKET_DEPTH-2*ry
    ytool = (r1.g.block(-xgap/2,xgap/2,0,
        r1.g.BODY_DEPTH/2+2,LOW_TOP,TOP+2)
        .edges('|Y and <Z').fillet(WINDOW_ROOT_RADIUS)
        .edges('|Z').fillet(WINDOW_PLAN_RADIUS))
    body = body.cut(ytool).cut(ytool.mirror('XZ'))
    if ygap>0:
        xtool = (r1.g.block(0,r1.g.OUTER_WIDTH/2+2,
            -ygap/2,ygap/2,LOW_TOP,TOP+2)
            .edges('|X and <Z').fillet(WINDOW_ROOT_RADIUS)
            .edges('|Z').fillet(WINDOW_PLAN_RADIUS))
        body = body.cut(xtool).cut(xtool.mirror('YZ'))
    return body


def base(proposal='corner',include_detents=True):
    returns = PROPOSALS[proposal]
    body = (r1.g.rounded_block(r1.g.OUTER_WIDTH,r1.g.BODY_DEPTH,TOP,0,5.)
        .faces('<Z').edges().chamfer(.4).cut(pocket()))
    body = cut_windows(body,returns)
    # Round final window/top junctions, not only the cutting profile.
    if returns is not None:
        rims = body.faces('+Z').filter(
            lambda f: min(abs(f.Center().z-z) for z in (LOW_TOP,TOP))<1e-5)
        lips = rims.edges().filter(lambda e:
            abs(e.Center().z-TOP)<1e-5 or any(abs(abs(e.Center().x)-x)<1e-5
                for x in (r1.POCKET_WIDTH/2,r1.g.OUTER_WIDTH/2))
            or any(abs(abs(e.Center().y)-y)<1e-5
                for y in (r1.POCKET_DEPTH/2,r1.g.BODY_DEPTH/2)))
        # Exclude the tangent seams between the flat rim and 2 mm root arcs.
        body = lips.fillet(RIM_RADIUS)
    else:
        body = body.faces('>Z').edges().fillet(RIM_RADIUS)
    foot = (r1.g.rounded_block(r1.g.FOOT_X,r1.g.FOOT_DEPTH,r1.g.SEAM_Z,0,r1.g.FOOT_RADIUS)
        .faces('<Z').edges().chamfer(r1.g.FOOT_BOTTOM_CHAMFER)
        .faces('>Z').edges().fillet(r1.g.FOOT_TOP_ROUND))
    foot = foot.cut(r1.g.rounded_block(r1.g.OUTER_WIDTH-.4,r1.g.BODY_DEPTH-.4,
        r1.g.SEAM_Z+.2,-.1,4.8))
    body = body.union(foot).cut(r1.grips.pocket()).cut(r1.grips.pocket(-1))
    body = r1.apply_hood_interfaces(body,include_detents)
    for end in (-1,1):
        body = body.cut(r1.h.socket(end))
        cy = end*r1.g.MODULE_PITCH/2
        reach = r1.g.MODULE_GAP/2+r1.h.KEY_EMBED+r1.h.KEY_FIT_GAP
        body = body.cut(r1.g.block(-r1.h.KEY_HEAD_HALF_X-r1.h.KEY_FIT_GAP,
            r1.h.KEY_HEAD_HALF_X+r1.h.KEY_FIT_GAP,cy-reach,cy+reach,r1.g.SEAM_Z,TOP+1))
    mouth = body.edges('|Z').filter(lambda e:
        abs(abs(e.Center().x)-(r1.h.KEY_HEAD_HALF_X+r1.h.KEY_FIT_GAP))<1e-5
        and abs(abs(e.Center().y)-r1.g.BODY_DEPTH/2)<1e-5)
    return mouth.fillet(r1.h.ENTRY_EDGE_ROUND)
