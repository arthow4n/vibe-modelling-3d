"""V1 vent hood. Millimetres; bed/front at Z=0, wall/rear at Z=depth.

Nominal mounting dimensions are placeholders, not a measured valve interface.
Importing this file constructs no CAD and writes nothing.
"""
from dataclasses import dataclass
import math
import cadquery as cq


@dataclass(frozen=True)
class Parameters:
    outer_diameter: float = 213.0
    depth: float = 85.0
    shell: float = 2.0
    front: float = 2.4
    mount_diameter: float = 130.0  # stationary rim placeholder, never the disc
    mount_diametral_clearance: float = 0.8  # insertion allowance; no retention claim
    engagement: float = 6.0
    valve_diameter: float = 130.0
    valve_projection: float = 35.0
    stationary_rim_height: float = 20.0  # user approximate axial height; diameter unmeasured
    disc_clearance: float = 12.0  # required radial clearance at face plane
    taper_start: float = 38.0
    transition_radius: float = 4.0
    outlet_count: int = 8
    outlet_width: float = 46.0  # tangential projected width
    outlet_height: float = 43.0
    outlet_bottom: float = 7.0
    outlet_phase: float = 22.5  # degrees about print Z
    outlet_shape: str = 'pointed-arch'
    outlet_roof_slope: float = 1.5  # vertical rise per tangential mm (56.3 degrees)
    outlet_tip_radius: float = 0.65
    outlet_corner_radius: float = 2.0
    lip_radius: float = 0.65
    rib_count: int = 8  # zero disables shallow front stiffeners
    rib_width: float = 2.0
    rib_height: float = 3.0
    rib_start_radius: float = 12.0
    rib_wall_inset: float = 1.0  # ribs join the R3 floor/wall blend

    @property
    def rib_end_radius(self):
        return self.radius - self.shell - self.rib_wall_inset

    @property
    def radius(self):
        return self.outer_diameter / 2

    @property
    def bore(self):
        return (self.mount_diameter + self.mount_diametral_clearance) / 2

    @property
    def shoulder_z(self):
        return self.depth - self.engagement

    @property
    def slope(self):
        return (self.radius - self.bore - self.shell) / (self.shoulder_z - self.taper_start)

    def inner_radius(self, z):
        """Unrounded section; fillets are checked separately on actual CAD."""
        return max(self.bore, min(self.radius - self.shell,
            self.radius + self.slope * self.taper_start - self.slope * z
            - self.shell * math.sqrt(1 + self.slope**2)))

    def validate(self):
        if self.outlet_shape not in ('pointed-arch', 'teardrop'):
            raise ValueError('outlet_shape must be pointed-arch or teardrop')
        if type(self.outlet_count) is not int or not 6 <= self.outlet_count <= 8:
            raise ValueError('Use 6–8 outlets; other counts need a new post-width review')
        if type(self.rib_count) is not int or self.rib_count < 0:
            raise ValueError('rib_count must be a nonnegative integer')
        for name, value in vars(self).items():
            if isinstance(value, (float, int)) and not math.isfinite(value):
                raise ValueError(f'{name} must be finite')
        for name in ('outer_diameter', 'depth', 'shell', 'front', 'mount_diameter',
                     'engagement', 'valve_diameter', 'valve_projection', 'disc_clearance',
                     'stationary_rim_height', 'transition_radius', 'outlet_width',
                     'outlet_height', 'outlet_bottom', 'outlet_corner_radius'):
            if getattr(self, name) <= 0:
                raise ValueError(f'{name} must be positive')
        if not (self.front < self.outlet_bottom < self.taper_start
                < self.shoulder_z < self.depth):
            raise ValueError('Invalid shell/front/window/taper/collar height stack')
        if not 0 < self.engagement <= self.stationary_rim_height < self.valve_projection:
            raise ValueError('Collar must remain on stationary rim, behind air gap')
        if not (0 < self.bore < self.radius - self.shell and 0 < self.slope <= 1):
            raise ValueError('Rear contraction must rise at least 1 mm per radial mm')
        roof = self.outlet_width / 2 * self.outlet_roof_slope
        if self.outlet_height <= roof + 2 * self.outlet_corner_radius:
            raise ValueError('Window needs straight sides below its sloping roof')
        if self.outlet_bottom + self.outlet_height >= self.shoulder_z - self.transition_radius - self.shell:
            raise ValueError('Window must leave a continuous rear shoulder below the collar')
        if self.outlet_width >= 2 * (self.radius - self.shell) * math.sin(math.pi / self.outlet_count) - 8:
            raise ValueError('Insufficient continuous post material between outlets')
        face_z = self.depth - self.valve_projection
        if self.inner_radius(face_z) - self.valve_diameter / 2 < self.disc_clearance:
            raise ValueError('Insufficient nominal disc radial clearance')
        if face_z - self.front - self.rib_height <= self.disc_clearance:
            raise ValueError('Insufficient front clearance')
        if self.rib_count and not (0 < self.rib_width and 0 < self.rib_height
                and 0 < self.rib_start_radius < self.rib_end_radius < self.radius - self.shell and 0 < self.rib_wall_inset < 3):
            raise ValueError('Ribs must stay inside the front panel')
        if not (self.outlet_roof_slope >= 1 and 0 < self.outlet_tip_radius <= self.outlet_corner_radius):
            raise ValueError('Roof must rise at least 1:1, with a smaller rounded tip')
        if not (0 < self.lip_radius < self.shell / 2 and self.transition_radius > self.shell):
            raise ValueError('Invalid lip/transition radii')


def rounded_wire(points, radius, corners=None):
    wire = cq.Workplane('XZ').polyline(points).close().val()
    vertices = wire.Vertices()
    if corners is not None:
        vertices = [v for v in vertices if any(
            abs(v.X-x) < 1e-6 and abs(v.Z-z) < 1e-6 for x, z in corners)]
    return wire.fillet2D(radius, vertices)


def window_profile(p):
    half = p.outlet_width / 2
    bottom = p.outlet_bottom
    peak = bottom + p.outlet_height
    points = [(-half, bottom), (half, bottom), (half, peak-half*p.outlet_roof_slope),
              (0, peak), (-half, peak-half*p.outlet_roof_slope)]
    # Teardrop option points the lower end too; both retain the selected sloping upper roofs.
    if p.outlet_shape == 'teardrop':
        points = [(0, bottom), (half, bottom+half), (half, peak-half*p.outlet_roof_slope),
                  (0, peak), (-half, peak-half*p.outlet_roof_slope), (-half, bottom+half)]
        if p.outlet_height <= half*(1+p.outlet_roof_slope):
            raise ValueError('Teardrop needs positive straight sides between its end slopes')
    wire = rounded_wire(points, p.outlet_corner_radius, [point for point in points if point != (0, peak)])
    return wire.fillet2D(p.outlet_tip_radius, [v for v in wire.Vertices()
        if abs(v.X) < 1e-6 and abs(v.Z-peak) < 1e-6])


def build(p: Parameters):
    p.validate()
    r, t, b = p.radius, p.shell, p.bore
    offset = t * math.sqrt(1 + p.slope**2)
    inner_start = p.taper_start + (t-offset)/p.slope
    inner_end = p.shoulder_z + (t-offset)/p.slope
    corners = [(r, p.taper_start), (b+t, p.shoulder_z),
               (b, inner_end), (r-t, inner_start)]
    points = [(0, 0), (r, 0), (r, p.taper_start),
              (b+t, p.shoulder_z), (b+t, p.depth), (b, p.depth),
              (b, inner_end), (r-t, inner_start), (r-t, p.front), (0, p.front)]
    wire = rounded_wire(points, p.transition_radius, corners)
    # Floor/wall junction and outside bed rim are deliberately rounded separately.
    wire = wire.fillet2D(2.0, [v for v in wire.Vertices()
        if abs(v.X-r) < 1e-6 and abs(v.Z) < 1e-6])
    wire = wire.fillet2D(3.0, [v for v in wire.Vertices()
        if abs(v.X-(r-t)) < 1e-6 and abs(v.Z-p.front) < 1e-6])
    hood = cq.Workplane('XZ').add(wire).toPending().revolve(360, (0, 0), (0, 1))
    # Radial cutter extends completely through the shell, not across the chamber.
    cutter = cq.Solid.extrudeLinear(window_profile(p), [], cq.Vector(0, p.radius-p.bore+10, 0))
    cutter = cutter.translate((0, -p.radius-5, 0))
    for index in range(p.outlet_count):
        hood = hood.cut(cutter.rotate((0, 0, 0), (0, 0, 1),
                                     p.outlet_phase + index*360/p.outlet_count))
    # All resulting window lips, plus the exposed collar rim; exclude smooth seams.
    lip_edges = [e for e in hood.val().Edges() if
        p.outlet_bottom-0.01 <= e.Center().z <= p.outlet_bottom+p.outlet_height+0.01
        or abs(e.Center().z-p.depth) < 1e-6]
    hood = hood.newObject(lip_edges).fillet(p.lip_radius)
    for index in range(p.rib_count):
        length = p.rib_end_radius-p.rib_start_radius
        rib = (cq.Workplane('XY', origin=((p.rib_start_radius+p.rib_end_radius)/2, 0, p.front-0.2))
               .box(length, p.rib_width, p.rib_height+0.2, centered=(True, True, False))
               .edges('|Z').fillet(min(0.8, p.rib_width/2-0.1))
               .edges('>Z').fillet(0.6))
        hood = hood.union(rib.rotate((0, 0, 0), (0, 0, 1), index*360/p.rib_count))
    return hood


if __name__ in ('__main__', '__cqgi__'):
    result = build(Parameters())
