"""Rounded square tray. Edit the millimetre parameters below, then re-export."""

from tray_geometry import build_tray

CAVITY_SIZE = 220.0  # Vertical wall-to-wall size; flat floor is 200 mm wide.
INNER_CORNER_RADIUS = 30.0
INTERNAL_DEPTH = 31.0
BASE_THICKNESS = 6.0
RIM_WALL = 9.0  # Before edge rounds; nominal exterior is 238 mm.
TAPER_INSET = 7.0  # Each side; nominal lower profile is 224 mm.
FLOOR_FILLET = 10.0
INNER_RIM_FILLET = 2.5
OUTER_RIM_FILLET = 2.5
BOTTOM_FILLET = 8.0


def main():
    return build_tray(
        CAVITY_SIZE, INNER_CORNER_RADIUS, INTERNAL_DEPTH, BASE_THICKNESS,
        RIM_WALL, TAPER_INSET, FLOOR_FILLET, INNER_RIM_FILLET,
        OUTER_RIM_FILLET, BOTTOM_FILLET,
    )


result = main()
