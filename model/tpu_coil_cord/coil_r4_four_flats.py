"""R4: four symmetric outer flats and wider gaps for the failed R3 print.

Millimetres. One TPU experiment; integral closed terminal turns stay within the
coil envelope. Previous sources and exports remain historical controls; R3 is a failed trial.
"""
import cadquery as cq

OUTSIDE_DIAMETER = 15.0
CORD_DIAMETER = 3.2
MEAN_RADIUS = (OUTSIDE_DIAMETER-CORD_DIAMETER)/2
RADIAL_WIDTH = CORD_DIAMETER
AXIAL_HEIGHT = CORD_DIAMETER
TURN_GAP = 0.40  # wider than the physically merging R3 gap of 0.15 mm
TURNS = 19
PITCH = AXIAL_HEIGHT + TURN_GAP
RISE = TURNS * PITCH
OVERALL_LENGTH = RISE + AXIAL_HEIGHT  # 71.6 mm
OUTER_RADIUS = MEAN_RADIUS + RADIAL_WIDTH/2
FLAT_TRIM = 0.5  # identical radial removal on all four sides
ACROSS_FLATS = OUTSIDE_DIAMETER-2*FLAT_TRIM


def section(z):
    """Round cord with nearly the same material area as R1's faceted section."""
    return cq.Workplane('XZ').moveTo(MEAN_RADIUS,z).circle(CORD_DIAMETER/2)


def build_axial():
    if not (0 < CORD_DIAMETER < 2*MEAN_RADIUS):
        raise ValueError('Cord must leave an open bore')
    if TURN_GAP <= 0 or not isinstance(TURNS,int) or TURNS < 3:
        raise ValueError('Need separated turns and an integer turn count of at least three')
    z0 = AXIAL_HEIGHT/2
    # Native one-turn edges retain the same helix while bounding each surface's
    # parameter span for meshing, rather than one long periodic spline face.
    edges = []
    for turn in range(TURNS):
        edges.extend(cq.Wire.makeHelix(PITCH,PITCH,MEAN_RADIUS)
                     .translate((0,0,z0+turn*PITCH)).Edges())
    path = cq.Wire.assembleEdges(edges)
    coil = section(z0).sweep(path,isFrenet=True)
    # These close the terminal winding in place, as on R1. They add no axial
    # extension, outboard frame or connecting tab beyond the existing coil.
    first = section(z0).revolve(360,(0,0),(0,1))
    last = (section(z0+RISE).revolve(360,(0,0),(0,1))
            .rotate((0,0,0),(0,0,1),90))
    # Fuse all three together. Sequential periodic torus/helix unions produced
    # incomplete geometry in a rejected build despite a positive validity flag.
    shape = coil.val().fuse(first.val(),last.val())
    for turn in (1,TURNS//2,TURNS-1):
        point = cq.Vector(MEAN_RADIUS,0,z0+turn*PITCH)
        if not any(solid.isInside(point,1e-6) for solid in shape.Solids()):
            raise ValueError('Terminal fusion lost the helical cord')
    return cq.Workplane(obj=shape)


def print_placement(shape):
    """Four identical flats around the axis, including the integral end loops."""
    if not (0 < FLAT_TRIM < CORD_DIAMETER/2):
        raise ValueError('Flat trim must leave the cord centerline and inner section intact')
    horizontal = shape.rotate((0,0,0),(0,1,0),90)
    prism = (cq.Workplane('XY').box(OVERALL_LENGTH+2,ACROSS_FLATS,ACROSS_FLATS)
             .translate((OVERALL_LENGTH/2,0,0)).val())
    # Avoid periodic-surface unification: it damaged earlier native end joins.
    clipped = horizontal.val().intersect(prism)
    return cq.Workplane(obj=clipped).translate((0,0,ACROSS_FLATS/2))


def build_sample():
    return print_placement(build_axial())


if __name__ in ('__main__','__cqgi__'):
    result = build_sample()
