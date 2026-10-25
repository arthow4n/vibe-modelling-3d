"""R5 short octagonal TPU coil: faceted bore, exterior and cord, dimensions mm."""
import math
import cadquery as cq

OUTSIDE_ACROSS_FLATS = 14.0  # about 15.2 mm across opposite octagonal corners
RADIAL_WIDTH = 3.2
AXIAL_WIDTH = 3.2
CORD_CHAMFER = 0.8  # leaves 1.6 mm flat lands, with 45-degree corner facets
TURN_GAP = 1.2  # three times R4's physically sticking 0.4 mm nominal gap
TURNS = 5
PITCH = AXIAL_WIDTH+TURN_GAP
RISE = TURNS*PITCH
OVERALL_LENGTH = RISE+AXIAL_WIDTH  # 25.2 mm nominal
MEAN_APOTHEM = (OUTSIDE_ACROSS_FLATS-RADIAL_WIDTH)/2
AXIS_HEIGHT = OUTSIDE_ACROSS_FLATS/2


def transverse_points():
    """Regular octagonal centerline, starting midway along the flat bottom."""
    a=MEAN_APOTHEM
    b=a*math.tan(math.pi/8)
    return [(0,-a),(b,-a),(a,-b),(a,b),(b,a),(-b,a),(-a,b),(-a,-b),(-b,-a),(0,-a)]


def winding_stations():
    """Advance X continuously with transverse perimeter, creating a true 3D coil."""
    points=transverse_points()
    perimeter=sum(math.dist(p,q) for p,q in zip(points,points[1:]))
    stations=[]
    for turn in range(TURNS):
        distance=0.
        for i,(y,z) in enumerate(points[:-1]):
            if i:distance+=math.dist(points[i-1],points[i])
            stations.append((AXIAL_WIDTH/2+turn*PITCH+PITCH*distance/perimeter,y,z))
    y,z=points[-1]
    stations.append((AXIAL_WIDTH/2+RISE,y,z))
    return stations


def winding_path():
    return cq.Wire.makePolygon([cq.Vector(x,y,z+AXIS_HEIGHT) for x,y,z in winding_stations()])


def section_at(x,y,z):
    """Miter section: radial scaling gives matching flat inner/outer octagons."""
    a,b,c=AXIAL_WIDTH/2,RADIAL_WIDTH/2,CORD_CHAMFER
    profile=[(-a,-b+c),(-a+c,-b),(a-c,-b),(a,-b+c),
             (a,b-c),(a-c,b),(-a+c,b),(-a,b-c)]
    # At each polygon corner, (y,z)/apothem is the outward bisector times sec(22.5°).
    # This is the exact miter for parallel octagonal inner and outer walls.
    vertices=[cq.Vector(x+u,y*(1+v/MEAN_APOTHEM),AXIS_HEIGHT+z*(1+v/MEAN_APOTHEM))
              for u,v in profile]
    return cq.Wire.makePolygon(vertices,close=True)


def cord_segments(stations):
    """Straight ruled sections share exact corner profiles, avoiding a twisting sweep."""
    wires=[section_at(*p) for p in stations]
    return [cq.Solid.makeLoft([a,b],ruled=True) for a,b in zip(wires,wires[1:])]


def build_sample():
    if not (0<CORD_CHAMFER<min(AXIAL_WIDTH,RADIAL_WIDTH)/2):
        raise ValueError('Cord chamfer must preserve substantial flat lands')
    if MEAN_APOTHEM<=RADIAL_WIDTH/2 or TURN_GAP<=0 or not isinstance(TURNS,int) or TURNS<3:
        raise ValueError('Need an open bore, positive gaps and at least three full turns')
    parts=cord_segments(winding_stations())
    for x in (AXIAL_WIDTH/2,AXIAL_WIDTH/2+RISE):
        parts.extend(cord_segments([(x,y,z) for y,z in transverse_points()]))
    shape=parts[0].fuse(*parts[1:])
    point=cq.Vector(AXIAL_WIDTH/2+2*PITCH,0,AXIS_HEIGHT-MEAN_APOTHEM)
    if not any(s.isInside(point,1e-6) for s in shape.Solids()):
        raise ValueError('Terminal fusion lost the middle winding')
    return cq.Workplane(obj=shape)


if __name__ in ('__main__','__cqgi__'):
    result=build_sample()
