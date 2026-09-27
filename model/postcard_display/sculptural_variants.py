"""Distinct silhouettes: circular Orbit, folded Bolt, low Pebble.
All dimensions mm; print feet-down. Existing variants remain untouched.
"""
import math
import cadquery as cq
from postcard_display import BASE_HEIGHT, SLOT_GAP, SLOPE, BACK_HEIGHT
from style_variants import foundations

ORBIT_RADIUS = 25.0
ORBIT_CENTRE_Z = 28.0
ORBIT_CENTRE_Y = SLOT_GAP+(ORBIT_CENTRE_Z-BASE_HEIGHT)*SLOPE + ORBIT_RADIUS*math.sqrt(1+SLOPE*SLOPE)
ORBIT_RIB_WIDTH = 3.6
ORBIT_HALF_SPACING = 24.0
ORBIT_REAR = 60.0
BOLT_WIDTH = 12.0
BOLT_DEPTH = 6.0
BOLT_PATH = [(14.0,1.2),(25.0,18.0),(10.0,34.0),
             (SLOT_GAP+BACK_HEIGHT*SLOPE,BASE_HEIGHT+BACK_HEIGHT)]
PEBBLE_CENTRE_Y = 18.0
# height, half-width, fore/aft radius; smooth, shrinking upper sections.
PEBBLE_SECTIONS = [(0.0,28.0,18.0),(8.0,27.0,17.0),
                   (16.0,23.0,14.5),(23.0,16.0,10.0),(27.0,4.0,2.5)]


def orbit():
    part = foundations()
    cy,cz,r = ORBIT_CENTRE_Y,ORBIT_CENTRE_Z,ORBIT_RADIUS
    # Wider footprint supports the ring's rear edge without a separate joint.
    for x in [-ORBIT_HALF_SPACING,ORBIT_HALF_SPACING]:
        foot = (cq.Workplane('XY').box(8,ORBIT_REAR-12,BASE_HEIGHT,
                                      centered=(True,False,False))
                .translate((x,12,0)).edges('|Z').fillet(1))
        disk = (cq.Workplane('YZ',origin=(x-ORBIT_RIB_WIDTH/2,0,0))
                .center(cy,cz).circle(r).extrude(ORBIT_RIB_WIDTH))
        plinth = (cq.Workplane('YZ',origin=(x-ORBIT_RIB_WIDTH/2,0,0))
                  .polyline([(cy-22,1.2),(cy+22,1.2),(cy+22,17),(cy-22,17)])
                  .close().extrude(ORBIT_RIB_WIDTH))
        # Round lower opening, pointed upper closure: a porthole with a crown.
        opening = (cq.Workplane('YZ',origin=(x-5,0,0))
                   .moveTo(cy-17,27).threePointArc((cy,10),(cy+17,27))
                   .lineTo(cy,46).close().extrude(10).edges('|X').fillet(0.6))
        ring = disk.union(plinth).cut(opening)
        part = part.union(foot).union(ring)
    return part.clean()


def bolt():
    part = foundations()
    plinth = (cq.Workplane('XY').box(BOLT_WIDTH+2,13,BASE_HEIGHT,
                                    centered=(True,False,False))
              .translate((0,13,0)).edges('|Z').fillet(1))
    outline = BOLT_PATH+[(y+BOLT_DEPTH,z) for y,z in reversed(BOLT_PATH)]
    spine = (cq.Workplane('YZ',origin=(-BOLT_WIDTH/2,0,0))
             .polyline(outline).close().extrude(BOLT_WIDTH)
             .edges('|X').fillet(0.65))
    return part.union(plinth).union(spine).clean()


def pebble():
    sections = cq.Workplane('XY')
    last = 0
    for z,rx,ry in PEBBLE_SECTIONS:
        sections = sections.workplane(offset=z-last).ellipse(rx,ry)
        last = z
    mound = sections.loft().translate((0,PEBBLE_CENTRE_Y,0))
    # Trim to the card plane, retaining a broad inclined contact patch behind it.
    cutter = (cq.Workplane('YZ',origin=(-50,0,0))
              .polyline([(-40,-1),(SLOT_GAP+(-1-BASE_HEIGHT)*SLOPE,-1),
                         (SLOT_GAP+(40-BASE_HEIGHT)*SLOPE,40),(-40,40)])
              .close().extrude(100))
    return foundations().union(mound.cut(cutter)).clean()

BUILDERS = {'orbit':orbit,'bolt':bolt,'pebble':pebble}
