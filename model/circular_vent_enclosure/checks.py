"""Targeted nominal-interface and flow screens; no physical-performance claims."""
import json
import math
from functools import cache
import cadquery as cq
from circular_vent_enclosure import Parameters, build, window_profile


@cache
def candidate():
    p = Parameters()
    return p, build(p).val()


def envelope():
    p, _ = candidate()
    assert p.outer_diameter <= 230 and (p.outer_diameter-p.valve_diameter)/2 <= 50
    assert 210 <= p.outer_diameter <= 215 and 80 <= p.depth <= 90
    assert 2 <= p.shell <= 2.4 and 2.4 <= p.front <= 3
    assert p.rib_count == 8 and p.rib_height == 3


def nominal_fit():
    p, hood = candidate()
    # A conservative 130 mm swept cylinder includes the disc and stationary body.
    valve = cq.Workplane('XY', origin=(0, 0, p.depth-p.valve_projection)).circle(
        p.valve_diameter/2).extrude(p.valve_projection+20).val()
    assert hood.intersect(valve).Volume() < 0.01, 'Nominal valve envelope intersects hood'
    # A 12 mm radial band at wall heights 20–35 mm must remain material-free.
    band = (cq.Workplane('XY', origin=(0, 0, p.depth-p.valve_projection)).circle(p.valve_diameter/2+p.disc_clearance).circle(p.valve_diameter/2)
            .extrude(p.valve_projection-p.stationary_rim_height).val())
    assert hood.intersect(band).Volume() < 0.01, 'Conditional annular emission band obstructed'
    shield = cq.Workplane('XY', origin=(0, 0, 1)).circle(p.valve_diameter/2).extrude(0.1).val()
    assert shield.cut(hood).Volume() < 0.01, 'Missing forward shield material'


def core_radius(hood, p, z):
    """Inscribed void radius from post-centre and window-centre CAD rays (eightfold symmetry), including posts and windows."""
    radii = []
    for i in range(2):
        a = math.radians(p.outlet_phase + i*180/p.outlet_count)
        end = cq.Vector((p.radius+1)*math.cos(a), (p.radius+1)*math.sin(a), z)
        ray = cq.Edge.makeLine(cq.Vector(0, 0, z), end)
        vertices = hood.intersect(ray).Vertices()
        radii.append(min((math.hypot(v.X, v.Y) for v in vertices), default=p.radius))
    return min(radii)


@cache
def flow_measurements():
    p, hood = candidate()
    projected = cq.Face.makeFromWires(window_profile(p)).Area()*p.outlet_count
    table = []
    for wall_height in (0.7, 6, 10, 15, 20, 25, 30, 35):
        radius = core_radius(hood, p, p.depth-wall_height)
        table.append(dict(wall_height_mm=wall_height, core_radius_mm=round(radius, 3),
            radial_clearance_mm=round(radius-p.valve_diameter/2, 3),
            annular_area_cm2=round(math.pi*(radius**2-(p.valve_diameter/2)**2)/100, 3)))
    # Inflow is distributed along wall heights 20–35 mm. The full flow enters
    # the forward chamber at the disc plane; rear annular slices are local gaps.
    disc_z = p.depth-p.valve_projection
    # A meridional post ray gives the minimum circular core by construction:
    # the unwindowed surface is axisymmetric and window cuts only remove material.
    full_flow_radii = [core_radius(hood, p, disc_z-i*2) for i in range(4)]
    band_area = math.pi*(min(full_flow_radii)**2-(p.valve_diameter/2)**2)
    source_area = 2*math.pi*(p.valve_diameter/2)*(p.valve_projection-p.stationary_rim_height)
    front_gap = p.depth-p.valve_projection-p.front-p.rib_height
    turn_area = 2*math.pi*(p.valve_diameter/2)*front_gap
    # Volume is measured solely to screen the brief's lightweight/cantilever load.
    mass_g = hood.Volume()/1000*1.27  # assumed solid PETG density, not a spool calibration
    center_z = hood.Center().z
    return dict(nominal_outlet_projected_cm2=round(projected/100, 3),
        downstream_disc_plane_min_area_cm2=round(band_area/100, 3),
        front_clearance_over_ribs_mm=front_gap,
        conservative_front_turn_area_cm2=round(turn_area/100, 3),
        added_full_flow_sections_min_cm2=round(min(projected, band_area, turn_area)/100, 3),
        nominal_existing_cylindrical_gap_cm2=round(source_area/100, 3),
        rear_annular_sections=table, assumed_solid_petg_mass_g=round(mass_g, 2),
        wall_horizontal_axis_gravity_moment_Nm=round(mass_g/1000*9.81*(p.depth-center_z)/1000, 4),
        taper_radial_step_per_0_2_layer_mm=round(p.slope*0.2, 3),
        scope='Nominal 130 mm disc; user approximate rim20 + gap15 = projection35. '
              'Not hydraulic effective area or pressure/noise prediction. Symmetric post/window rays; downstream axial samples at 2 mm spacing.')


def flow():
    m = flow_measurements()
    assert 80 <= m['nominal_outlet_projected_cm2'] <= 100, 'Outlet area misses initial target'
    assert m['added_full_flow_sections_min_cm2'] >= 80, 'Added full-flow section screen falls below 80 cm²'
    assert m['front_clearance_over_ribs_mm'] >= 12


if __name__ == '__main__':
    envelope()
    nominal_fit()
    flow()
    print(json.dumps(flow_measurements(), indent=2))
