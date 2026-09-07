"""Parametric USB-C socket cleaner for single-colour FDM printing.

The cleaning end is a fork rather than a full-width paddle.  Each tine is
positioned in one of the two side gutters beside the USB-C receptacle tongue;
the open centre avoids dragging over the contact fields.  Turn the tool over
to clean the opposite face of the receptacle tongue.

Print flat on the XY bed with the broad handle at Z=0.  The thin tines are
intentionally a small, sacrificial feature.  Use only with the device powered
off and disconnected; never force the tool or use it to probe energized pins.
Dimensions are in millimetres.
"""
import cadquery as cq


# USB Type-C receptacle mating-envelope references (USB-IF Figure 3-1).
# These are nominal interface values, not a claim that every low-cost socket
# has identical geometry.
RECEPTACLE_OPENING_WIDTH = 8.34
RECEPTACLE_OPENING_HEIGHT = 2.56
RECEPTACLE_SHELL_DEPTH = 6.20
TONGUE_WIDTH = 6.69
TONGUE_THICKNESS = 0.70

# User-editable functional dimensions.
TIP_INSERTION_DEPTH = RECEPTACLE_SHELL_DEPTH - 0.40  # leave a stop margin
TIP_THICKNESS = 0.55  # below the nominal 0.93 mm side-to-tongue gap
TINE_WIDTH = 0.45  # approximately one 0.4 mm nozzle line
TONGUE_CLEARANCE = 0.15  # per side, between tine and nominal tongue edge
OUTER_SIDE_CLEARANCE = (
    (RECEPTACLE_OPENING_WIDTH - TONGUE_WIDTH) / 2
    - TINE_WIDTH
    - TONGUE_CLEARANCE
)

# Hand interface and print geometry.
STOP_WIDTH = 10.5  # wider than the receptacle opening; prevents over-insertion
STOP_LENGTH = 1.6
STOP_HEIGHT = 2.8
STOP_TINE_OVERLAP = 0.05  # keeps the collar fused to the tine roots
NECK_START_Y = 6.5
NECK_END_Y = 14.5
NECK_START_WIDTH = 6.0
NECK_END_WIDTH = 12.0
NECK_HEIGHT = 4.1
HANDLE_Y = 13.6
HANDLE_LENGTH = 54.4
HANDLE_WIDTH = 15.0
HANDLE_HEIGHT = 5.5
HANDLE_CORNER_RADIUS = 3.0
LANYARD_HOLE_RADIUS = 2.15
LANYARD_HOLE_Y = HANDLE_Y + HANDLE_LENGTH - 5.2


def _rounded_box(width, length, height, y0, radius):
    """Return a box with rounded plan corners and a flat bed face."""
    part = (
        cq.Workplane("XY")
        .box(width, length, height, centered=(True, False, False))
        .translate((0, y0, 0))
    )
    part = part.edges("|Z").fillet(radius)
    return part


def _tine(x_center):
    """Make one rounded-nose scraper tine, flat on the print bed."""
    half = TINE_WIDTH / 2
    nose_radius = half
    y_end = TIP_INSERTION_DEPTH
    # The semicircular nose is tangent to the two long scraping edges.  A
    # rounded plan nose is less likely to catch the receptacle tongue on entry.
    profile = (
        cq.Workplane("XY")
        .moveTo(x_center - half, nose_radius)
        .threePointArc((x_center, 0), (x_center + half, nose_radius))
        .lineTo(x_center + half, y_end)
        .lineTo(x_center - half, y_end)
        .close()
    )
    return profile.extrude(TIP_THICKNESS)


def _stop_collar():
    """Make a rounded, wide stop that remains outside the socket mouth."""
    collar = _rounded_box(
        STOP_WIDTH,
        STOP_LENGTH,
        STOP_HEIGHT,
        TIP_INSERTION_DEPTH - STOP_TINE_OVERLAP,
        0.35,
    )
    # Keep the bed edge square for reliable first-layer contact; break the
    # exposed top perimeter so the stop is comfortable against a fingertip.
    return collar.faces(">Z").edges().chamfer(0.20)


def _neck():
    """Taper the small stop into the broad hand grip."""
    half_start = NECK_START_WIDTH / 2
    half_end = NECK_END_WIDTH / 2
    return (
        cq.Workplane("XY")
        .polyline(
            [
                (-half_start, NECK_START_Y),
                (half_start, NECK_START_Y),
                (half_end, NECK_END_Y),
                (-half_end, NECK_END_Y),
            ]
        )
        .close()
        .extrude(NECK_HEIGHT)
    )


def _handle():
    """Make the broad rounded grip and a storage/lanyard hole."""
    handle = _rounded_box(
        HANDLE_WIDTH,
        HANDLE_LENGTH,
        HANDLE_HEIGHT,
        HANDLE_Y,
        HANDLE_CORNER_RADIUS,
    )
    hole = (
        cq.Workplane("XY")
        .center(0, LANYARD_HOLE_Y)
        .circle(LANYARD_HOLE_RADIUS)
        .extrude(HANDLE_HEIGHT + 1.0)
    )
    handle = handle.cut(hole)
    # A small top edge break removes the sharp perimeter without reducing the
    # flat bed footprint.  The hole is left cylindrical for easy threading.
    return handle.faces(">Z").edges().filter(
        lambda edge: edge.Length() > 8.0
    ).chamfer(0.35)


def build_cleaner():
    """Build the single connected, print-ready cleaner."""
    side_gap = (RECEPTACLE_OPENING_WIDTH - TONGUE_WIDTH) / 2
    assert OUTER_SIDE_CLEARANCE > 0, "tine does not fit the nominal side gutter"
    assert TIP_THICKNESS < (RECEPTACLE_OPENING_HEIGHT - TONGUE_THICKNESS) / 2

    # Position each tine from the tongue edge outward.  The fork is symmetric
    # about X=0 and therefore works on either side of a reversible connector.
    tine_center = TONGUE_WIDTH / 2 + TONGUE_CLEARANCE + TINE_WIDTH / 2
    inner_gap = 2 * tine_center - TINE_WIDTH
    outer_edge = tine_center + TINE_WIDTH / 2
    assert inner_gap >= TONGUE_WIDTH + 2 * TONGUE_CLEARANCE
    assert outer_edge <= RECEPTACLE_OPENING_WIDTH / 2 - OUTER_SIDE_CLEARANCE
    left_tine = _tine(-tine_center)
    right_tine = _tine(tine_center)
    result = left_tine.union(right_tine)
    result = result.union(_stop_collar()).union(_neck()).union(_handle())
    return result


result = build_cleaner()
shape = result.val()
assert shape.isValid(), "invalid USB-C cleaner shape"
assert len(result.solids().vals()) == 1, "cleaner must be one connected solid"
bb = shape.BoundingBox()
assert abs(bb.zmin) < 0.001, "cleaner must print flat on Z=0"
assert bb.zmax <= 250.0, "cleaner exceeds the confirmed safe build height"
assert bb.xmax - bb.xmin <= 260.0 and bb.ymax - bb.ymin <= 260.0
