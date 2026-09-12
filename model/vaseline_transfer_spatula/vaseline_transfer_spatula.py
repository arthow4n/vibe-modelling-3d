"""Flat scrape-and-fill spatula for the repository's Vaseline container.

Millimetres.  The result is the single print-ready tool in bed orientation:
the blade and handle bottom are on Z=0.
"""
import cadquery as cq


# Interface inherited from model/vaseline_container/vaseline_container.py.
TARGET_MOUTH_DIAMETER = 38.0
TARGET_MOUTH_DEPTH = 22.75  # 24.75 mm mouth height minus 2 mm floor
MOUTH_SIDE_CLEARANCE = 4.0

# Flat blade.  The 4 mm radial clearance leaves room for residue and print
# variation while keeping the blade broad enough to wipe against the wall.
BLADE_WIDTH = TARGET_MOUTH_DIAMETER - 2.0 * MOUTH_SIDE_CLEARANCE
BLADE_LENGTH = 43.0
BLADE_THICKNESS = 2.4
TIP_TAPER_LENGTH = 8.0
TIP_THICKNESS = 1.2

# Comfortable handle and a crosswise stop that rests on the jar's outer neck.
HANDLE_WIDTH = 14.0
HANDLE_LENGTH = 100.0
HANDLE_HEIGHT = 7.0
HANDLE_CORNER_RADIUS = 3.0
STOP_WIDTH = 44.0
STOP_LENGTH = 5.0
STOP_HEIGHT = 3.2
STOP_CORNER_RADIUS = 1.5


def blade_planform():
    """Make a flat paddle with a semicircular scraping nose."""
    half_width = BLADE_WIDTH / 2.0
    nose_center_y = BLADE_LENGTH - half_width
    return (
        cq.Workplane("XY")
        .moveTo(-half_width, 0)
        .lineTo(half_width, 0)
        .lineTo(half_width, nose_center_y)
        .threePointArc((0, BLADE_LENGTH), (-half_width, nose_center_y))
        .close()
    )


def blade():
    """Build the flat blade with a thin, support-free wiping nose."""
    plate = blade_planform().extrude(BLADE_THICKNESS)

    # Remove the upper part of the last 8 mm.  The underside stays flat on the
    # bed, while the rounded nose ends at a 1.2 mm scraping edge.
    taper_start = BLADE_LENGTH - TIP_TAPER_LENGTH
    cut_top = (
        cq.Workplane("YZ", origin=(-BLADE_WIDTH, 0, 0))
        .polyline(
            [
                (taper_start, BLADE_THICKNESS),
                (BLADE_LENGTH, TIP_THICKNESS),
                (BLADE_LENGTH, BLADE_THICKNESS + 1.0),
                (taper_start, BLADE_THICKNESS + 1.0),
            ]
        )
        .close()
        .extrude(2.0 * BLADE_WIDTH)
    )
    return plate.cut(cut_top)


def rounded_handle():
    handle = (
        cq.Workplane("XY")
        .center(0, -HANDLE_LENGTH / 2.0)
        .rect(HANDLE_WIDTH, HANDLE_LENGTH)
        .extrude(HANDLE_HEIGHT)
    )
    return handle.edges("|Z").fillet(HANDLE_CORNER_RADIUS)


def rim_stop():
    stop = (
        cq.Workplane("XY")
        .center(0, -STOP_LENGTH / 2.0 + 0.5)
        .rect(STOP_WIDTH, STOP_LENGTH)
        .extrude(STOP_HEIGHT)
    )
    return stop.edges("|Z").fillet(STOP_CORNER_RADIUS)


def build():
    assert BLADE_WIDTH > 0
    assert BLADE_WIDTH + 2.0 * MOUTH_SIDE_CLEARANCE <= TARGET_MOUTH_DIAMETER
    assert BLADE_LENGTH > TARGET_MOUTH_DEPTH
    assert TIP_THICKNESS > 0 and TIP_THICKNESS < BLADE_THICKNESS
    tool = blade().union(rounded_handle()).union(rim_stop())
    assert len(tool.solids().vals()) == 1
    assert tool.val().isValid()
    return tool


tool = build()
result = tool.val()
