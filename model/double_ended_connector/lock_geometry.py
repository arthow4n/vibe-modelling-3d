"""Object-local solids for the sequential D/E/F mechanism prototypes (mm)."""
import cadquery as cq
from math import floor


def box(x,y,z,dx,dy,dz):
    return cq.Workplane('XY').box(dx,dy,dz).translate((x,y,z))


def cylinder(radius, z0, z1):
    return cq.Workplane('XY',origin=(0,0,z0)).circle(radius).extrude(z1-z0)


def screw_thread(*, root, crest, pitch, z0, z1, radial=0., axial=0.):
    """Solid core + trapezoid helix, trimmed together; no ISO compatibility."""
    r=root+radial; c=crest+radial; start=(floor(z0/pitch)-2)*pitch
    path=cq.Wire.makeHelix(pitch,z1-start+2*pitch,r,center=(0,0,start))
    profile=[(r-.12,start-.34*pitch-axial),
             (c,start-.13*pitch-axial),(c,start+.13*pitch+axial),
             (r-.12,start+.34*pitch+axial)]
    ridge=cq.Workplane('XZ').polyline(profile).close().sweep(path,isFrenet=True)
    core=cylinder(r,start-pitch,z1+3*pitch)
    return core.union(ridge).intersect(box(0,0,(z0+z1)/2,2*c+2,2*c+2,z1-z0)).clean()


def along_y(part,x,y,z=0.):
    return part.rotate((0,0,0),(1,0,0),-90).translate((x,y,z))
