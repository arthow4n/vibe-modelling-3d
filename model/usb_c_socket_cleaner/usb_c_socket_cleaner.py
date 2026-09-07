"""Parametric USB-C socket scraper for single-colour FDM printing.

This revision is a real flat scraper: the thin broad blade slides along the
bottom of the receptacle cavity, under the center tongue, and its crisp front
edge drags compacted lint back out on the return stroke. Turn the tool over to
clean the matching upper cavity face. The blade is plastic and intentionally
not a metal contact probe.

Print flat on the XY bed with the broad handle at Z=0. Use only with the
device powered off and disconnected. Never force the blade, pry against the
center tongue, or use it to probe energized pins. Dimensions are in mm.
"""
import cadquery as cq


# USB Type-C receptacle mating-envelope references (USB-IF Figure 3-1).
# These are nominal interface values, not a claim that every socket has
# identical clearances or the same enclosure recess.
RECEPTACLE_OPENING_WIDTH = 8.34
RECEPTACLE_OPENING_HEIGHT = 2.56
RECEPTACLE_SHELL_DEPTH = 6.20
TONGUE_WIDTH = 6.69
TONGUE_THICKNESS = 0.70

# Critical blade/interface dimensions.
BLADE_INSERTION_DEPTH = RECEPTACLE_SHELL_DEPTH - 0.35
BLADE_ROOT_WIDTH = 5.90  # narrower than the nominal tongue, with side margin
BLADE_TIP_WIDTH = 5.55
BLADE_THICKNESS = 0.45  # leaves vertical room below/above the 0.70 mm tongue
BLADE_LEAD_LENGTH = 0.90
BLADE_TIP_THICKNESS = 0.18  # thin chisel lead-in; bottom remains flat
STOP_BLADE_OVERLAP = 0.05

# Hand interface and print geometry.
STOP_WIDTH = 10.5  # wider than the receptacle opening; prevents over-insertion
STOP_LENGTH = 1.6
STOP_HEIGHT = 2.8
NECK_START_Y = BLADE_INSERTION_DEPTH + 0.70
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
    return part.edges("|Z").fillet(radius)


def _blade_footprint():
    """Return a tapered plan footprint for the centered under-tongue blade."""
    tip_half = BLADE_TIP_WIDTH / 2
    root_half = BLADE_ROOT_WIDTH / 2
    return (
        cq.Workplane("XY")
        .polyline(
            [
                (-tip_half, 0),
                (tip_half, 0),
                (root_half, BLADE_INSERTION_DEPTH),
                (-root_half, BLADE_INSERTION_DEPTH),
            ]
        )
        .close()
    )


def _scraper_blade():
    """Make a flat blade with a thin, chisel-like leading edge.

    The bottom face intentionally stays at Z=0.  In use it rests lightly on
    the cavity floor and the vertical leading edge pulls lint toward the port
    mouth.  The sloped top lead-in reduces the chance of catching the front of
    the center tongue during insertion.
    """
    blade = _blade_footprint().extrude(BLADE_THICKNESS)
    # Remove the top of the first 0.90 mm, leaving a 0.18 mm nose and a
    # support-free 45-ish degree lead-in to the full blade thickness.
    cutter = (
        cq.Workplane("YZ", origin=(-RECEPTACLE_OPENING_WIDTH / 2, 0, 0))
        .polyline(
            [
                (0, BLADE_TIP_THICKNESS),
                (0, BLADE_THICKNESS + 0.20),
                (BLADE_LEAD_LENGTH, BLADE_THICKNESS + 0.20),
                (BLADE_LEAD_LENGTH, BLADE_THICKNESS),
            ]
        )
        .close()
        .extrude(RECEPTACLE_OPENING_WIDTH)
    )
    return blade.cut(cutter)


def _stop_collar():
    """Make a rounded, wide stop that remains outside the socket mouth."""
    collar = _rounded_box(
        STOP_WIDTH,
        STOP_LENGTH,
        STOP_HEIGHT,
        BLADE_INSERTION_DEPTH - STOP_BLADE_OVERLAP,
        0.35,
    )
    # Keep the bed edge square for reliable first-layer contact; break only
    # the exposed top perimeter for a comfortable thumb stop.
    return collar.faces(">Z").edges().chamfer(0.20)


def _neck():
    """Taper the scraper stop into the broad hand grip."""
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
    # Break the upper long grip edges while preserving the flat print face.
    return handle.faces(">Z").edges().filter(
        lambda edge: edge.Length() > 8.0
    ).chamfer(0.35)


def build_cleaner():
    """Build the single connected, print-ready scraper."""
    vertical_gap = (RECEPTACLE_OPENING_HEIGHT - TONGUE_THICKNESS) / 2
    assert BLADE_ROOT_WIDTH < TONGUE_WIDTH
    assert BLADE_TIP_WIDTH <= BLADE_ROOT_WIDTH
    assert BLADE_THICKNESS < vertical_gap
    assert BLADE_INSERTION_DEPTH < RECEPTACLE_SHELL_DEPTH

    result = _scraper_blade()
    result = result.union(_stop_collar()).union(_neck()).union(_handle())
    return result


result = build_cleaner()
shape = result.val()
assert shape.isValid(), "invalid USB-C scraper shape"
assert len(result.solids().vals()) == 1, "scraper must be one connected solid"
bb = shape.BoundingBox()
assert abs(bb.zmin) < 0.001, "scraper must print flat on Z=0"
assert bb.zmax <= 250.0, "scraper exceeds the confirmed safe build height"
assert bb.xmax - bb.xmin <= 260.0 and bb.ymax - bb.ymin <= 260.0
