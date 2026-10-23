"""Shared V2 dimensions, mm. Wall Z=0; room is positive installed Z."""
from dataclasses import dataclass
import math


@dataclass(frozen=True)
class Parameters:
    outer_diameter: float = 213.0
    depth: float = 85.0
    shell: float = 1.4
    front: float = 2.4
    mount_diameter: float = 160.0  # hood mouth, NOT the valve grip diameter
    mount_diametral_clearance: float = 0.0  # hood mouth allowance; clamp has separate controls
    engagement: float = 3.0  # hood mouth axial land
    valve_diameter: float = 130.0
    valve_projection: float = 35.0
    stationary_rim_height: float = 20.0  # user approximate axial height; diameter unmeasured
    disc_clearance: float = 12.0  # required radial clearance at face plane
    taper_start: float = 32.0
    transition_radius: float = 4.0
    outlet_count: int = 8
    outlet_width: float = 46.0  # tangential projected width
    outlet_height: float = 43.0
    outlet_bottom: float = 4.0
    outlet_phase: float = 22.5  # degrees about print Z
    outlet_shape: str = 'pointed-arch'
    outlet_roof_slope: float = 1.5  # vertical rise per tangential mm (56.3 degrees)
    outlet_tip_radius: float = 0.65
    outlet_corner_radius: float = 2.0
    lip_radius: float = 0.5
    rib_count: int = 8  # zero disables shallow front stiffeners
    rib_width: float = 2.0
    rib_height: float = 3.0
    rib_start_radius: float = 12.0
    rib_wall_inset: float = 1.0  # ribs join the R3 floor/wall blend

    hood_standoff: float = 17.5
    collar_wall: float = 2.0
    clamp_free_diameter: float = 132.0
    clamp_min_diameter: float = 129.0
    clamp_max_diameter: float = 132.0
    clamp_wall: float = 2.0
    clamp_contact_height: float = 16.7
    rear_flange_thickness: float = 0.8
    rear_flange_width: float = 17.0
    clamp_split: float = 12.0
    clamp_ear_wall: float = 4.0
    mount_radius: float = 82.0
    mount_pad_inner: float = 77.1
    mount_pad_outer: float = 87.0
    mount_pad_width: float = 18.0
    mount_pad_thickness: float = 2.4
    mount_tab_thickness: float = 5.0
    mount_hole: float = 3.4
    mount_slot_width: float = 3.8
    clamp_bolt_hole: float = 5.0  # clearance for split-ear rotation, not printer error

    @property
    def print_depth(self):
        return self.depth-self.hood_standoff

    @property
    def mount_angles(self):
        # Three of the eight outlet centres, for radial Allen-key access.
        return tuple((self.outlet_phase+i*360/self.outlet_count)%360 for i in (0, round(self.outlet_count/3), round(2*self.outlet_count/3)))

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
        return self.print_depth - self.engagement

    @property
    def slope(self):
        return (self.radius - self.bore - self.collar_wall) / (self.shoulder_z - self.taper_start)

    def inner_radius(self, z):
        """Unrounded section; fillets are checked separately on actual CAD."""
        return max(self.bore, min(self.radius - self.shell,
            self.radius + self.slope * self.taper_start - self.slope * z
            - self.shell * math.sqrt(1 + self.slope**2)))

    def validate(self):
        if not (0 < self.clamp_min_diameter <= self.clamp_max_diameter <= self.clamp_free_diameter):
            raise ValueError('Invalid declared clamp diameter range')
        if not self.clamp_contact_height < self.hood_standoff < self.stationary_rim_height:
            raise ValueError('Mounting tabs must remain behind the original open band')
        if not (self.valve_diameter/2+self.disc_clearance < self.mount_pad_inner < self.mount_radius < self.mount_pad_outer):
            raise ValueError('Mounting pads intrude into the air keepout or miss bolt centres')
        if abs(self.clamp_contact_height+self.rear_flange_thickness-self.hood_standoff)>1e-6:
            raise ValueError('Rear flange must end at the hood seating plane')
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
                     'outlet_height', 'outlet_bottom', 'outlet_corner_radius',
                     'clamp_wall', 'rear_flange_thickness', 'rear_flange_width',
                     'mount_pad_thickness', 'mount_tab_thickness', 'clamp_split'):
            if getattr(self, name) <= 0:
                raise ValueError(f'{name} must be positive')
        if any(abs((angle+180)%360-180)<15 for angle in self.mount_angles):
            raise ValueError('Keep mounting lands at least 15 degrees away from the clamp split')
        if not (self.front < self.outlet_bottom < self.taper_start
                < self.shoulder_z < self.print_depth):
            raise ValueError('Invalid shell/front/window/taper/collar height stack')
        if not 0 < self.clamp_contact_height <= self.stationary_rim_height < self.valve_projection:
            raise ValueError('Clamp contact must remain on the stationary rim')
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
