"""Compact TPU telephone-cord print experiment; dimensions in millimetres."""
import cadquery as cq

# One prototype only. Increase section dimensions later for a controlled trial.
MEAN_RADIUS = 8.0
RADIAL_WIDTH = 4.0
AXIAL_HEIGHT = 3.2
FLAT_WIDTH = 1.2
TURN_GAP = 0.4  # axial CAD clearance, not a measured TPU release allowance
TURNS = 6
PITCH = AXIAL_HEIGHT + TURN_GAP
RISE = TURNS * PITCH


def section(z):
    """Faceted section: flat bed land and chamfered, growing undersides."""
    r, w, h, f = MEAN_RADIUS, RADIAL_WIDTH / 2, AXIAL_HEIGHT / 2, FLAT_WIDTH / 2
    return (cq.Workplane('XZ').polyline([
        (r-f, z-h), (r+f, z-h), (r+w, z),
        (r+f, z+h), (r-f, z+h), (r-w, z),
    ]).close())


def build_sample():
    if not (0 < FLAT_WIDTH < RADIAL_WIDTH < 2 * MEAN_RADIUS):
        raise ValueError('Section must leave an open central bore and sloping sides')
    if TURN_GAP <= 0 or TURNS < 3:
        raise ValueError('A separated multi-turn coil is required')
    z0 = AXIAL_HEIGHT / 2
    path = cq.Wire.makeHelix(PITCH, RISE, MEAN_RADIUS).translate((0, 0, z0))
    # Frenet transport keeps the profile radial/axial along the cylindrical helix.
    coil = section(z0).sweep(path, isFrenet=True)
    # Closed annular eyes lie across the ends, rather than sticking out sideways.
    # Each deliberately merges into the adjacent helical end; only the middle
    # turns must separate. The central bore is accessible to metal hooks.
    bottom_eye = section(z0).revolve(360, (0, 0), (0, 1))
    # Offset the periodic surface seam from the sweep endpoint for robust union.
    top_eye = (section(z0 + RISE).revolve(360, (0, 0), (0, 1))
               .rotate((0, 0, 0), (0, 0, 1), 90))
    return coil.union(bottom_eye).union(top_eye).clean()


result = build_sample()
