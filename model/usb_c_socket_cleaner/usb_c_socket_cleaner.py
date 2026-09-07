"""Parametric USB-C port lint pick for single-colour FDM printing.

The cleaning end is a narrow, offset pick rather than a full-width paddle. It
fits in one side channel beside the USB-C center tongue, reaches toward the
back of the port, and has a small rear-facing hook which catches compacted
lint on the pull-out stroke. Rotate the tool in plan to use the other side of
the tongue and flip it over to work on the opposite face.

Print flat on the XY bed with the broad handle at Z=0. Use only with the
device powered off and disconnected. Never force the pick, pry against the
center tongue, or use it to probe energized pins. Dimensions are in mm.
"""
import cadquery as cq


# USB Type-C receptacle mating-envelope references (USB-IF Figure 3-1).
# These are nominal interface values, not a claim that every socket has the
# same contact spring geometry or enclosure recess.
RECEPTACLE_OPENING_WIDTH = 8.34
RECEPTACLE_OPENING_HEIGHT = 2.56
RECEPTACLE_SHELL_DEPTH = 6.20
TONGUE_WIDTH = 6.69
TONGUE_THICKNESS = 0.70

# Critical pick/interface dimensions.
PICK_INSERTION_DEPTH = RECEPTACLE_SHELL_DEPTH - 0.35
PICK_WIDTH = 0.55  # fits the nominal side channel; approximately 1–2 lines
PICK_THICKNESS = 0.35  # intentionally thin and flexible in the port
PICK_TONGUE_CLEARANCE = 0.12  # inner-side nominal clearance
PICK_LEAD_LENGTH = 0.80
PICK_NOSE_THICKNESS = 0.12
PICK_HOOK_LENGTH = 1.15
PICK_HOOK_HEIGHT = 0.55
PICK_HOOK_SHOULDER_HEIGHT = 0.35
STOP_BLADE_OVERLAP = 0.05

# Hand interface and print geometry.
STOP_WIDTH = 10.5  # wider than the receptacle opening; prevents over-insertion
STOP_LENGTH = 1.6
STOP_HEIGHT = 2.8
NECK_START_Y = PICK_INSERTION_DEPTH + 0.70
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


def _pick_position():
    """Return the positive-side center and the nominal side clearances."""
    side_gap = (RECEPTACLE_OPENING_WIDTH - TONGUE_WIDTH) / 2
    outer_clearance = side_gap - PICK_WIDTH - PICK_TONGUE_CLEARANCE
    assert outer_clearance > 0, "pick does not fit the nominal side channel"
    center = TONGUE_WIDTH / 2 + PICK_TONGUE_CLEARANCE + PICK_WIDTH / 2
    return center, outer_clearance


def _pick_stem():
    """Build the flat stem with a thin low nose for easy entry."""
    center, _ = _pick_position()
    x0 = center - PICK_WIDTH / 2
    stem_profile = (
        cq.Workplane("YZ", origin=(x0, 0, 0))
        .polyline(
            [
                (0, 0),
                (0, PICK_NOSE_THICKNESS),
                (PICK_LEAD_LENGTH, PICK_THICKNESS),
                (PICK_INSERTION_DEPTH, PICK_THICKNESS),
                (PICK_INSERTION_DEPTH, 0),
            ]
        )
        .close()
    )
    return stem_profile.extrude(PICK_WIDTH)


def _pick_hook():
    """Add a small raised pull-out hook to catch lint without metal."""
    center, _ = _pick_position()
    x0 = center - PICK_WIDTH / 2
    # The steep shoulder faces back toward the user during the pull-out
    # stroke. The ramped front is easier to push into the port.
    hook_profile = (
        cq.Workplane("YZ", origin=(x0, 0, 0))
        .polyline(
            [
                (0, 0),
                (0, PICK_NOSE_THICKNESS),
                (PICK_LEAD_LENGTH, PICK_THICKNESS),
                (PICK_HOOK_LENGTH, PICK_HOOK_HEIGHT),
                (PICK_HOOK_LENGTH + 0.12, PICK_HOOK_HEIGHT),
                (PICK_HOOK_LENGTH + 0.12, PICK_HOOK_SHOULDER_HEIGHT),
                (PICK_HOOK_LENGTH + 0.35, PICK_HOOK_SHOULDER_HEIGHT),
                (PICK_HOOK_LENGTH + 0.35, 0),
            ]
        )
        .close()
    )
    return hook_profile.extrude(PICK_WIDTH)


def _cleaning_pick():
    """Make the offset pick and fuse its pull-out hook to the stem."""
    return _pick_stem().union(_pick_hook())


def _stop_collar():
    """Make a rounded, wide stop that remains outside the socket mouth."""
    collar = _rounded_box(
        STOP_WIDTH,
        STOP_LENGTH,
        STOP_HEIGHT,
        PICK_INSERTION_DEPTH - STOP_BLADE_OVERLAP,
        0.35,
    )
    # Keep the bed edge square for reliable first-layer contact; break only
    # the exposed top perimeter for a comfortable thumb stop.
    return collar.faces(">Z").edges().chamfer(0.20)


def _neck():
    """Taper the pick stop into the broad hand grip."""
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
    """Build the single connected, print-ready pick."""
    vertical_gap = (RECEPTACLE_OPENING_HEIGHT - TONGUE_THICKNESS) / 2
    _, outer_clearance = _pick_position()
    assert PICK_WIDTH + PICK_TONGUE_CLEARANCE + outer_clearance <= (
        RECEPTACLE_OPENING_WIDTH - TONGUE_WIDTH
    ) / 2
    assert PICK_THICKNESS < vertical_gap
    assert PICK_HOOK_HEIGHT < vertical_gap
    assert PICK_INSERTION_DEPTH < RECEPTACLE_SHELL_DEPTH

    result = _cleaning_pick()
    result = result.union(_stop_collar()).union(_neck()).union(_handle())
    return result


result = build_cleaner()
shape = result.val()
assert shape.isValid(), "invalid USB-C pick shape"
assert len(result.solids().vals()) == 1, "pick must be one connected solid"
bb = shape.BoundingBox()
assert abs(bb.zmin) < 0.001, "pick must print flat on Z=0"
assert bb.zmax <= 250.0, "pick exceeds the confirmed safe build height"
assert bb.xmax - bb.xmin <= 260.0 and bb.ymax - bb.ymin <= 260.0
