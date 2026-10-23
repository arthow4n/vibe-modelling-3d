"""V2 nominal geometry, adjustable clamp/assembly path, tools and weight screens."""
import json
import math
from functools import cache
import cadquery as cq
from assembly_geometry import PairRequirement
from physical_analysis.screening import elastic_friction_grip
from vent_parameters import Parameters
from circular_vent_enclosure import window_profile
from mounting_clamp import gap_angle, bolt_position, neutral_offset
from assembly import configuration, components


@cache
def candidate():
    p=Parameters()
    hood,clamp=components(p,p.clamp_free_diameter)
    return p,hood.val(),clamp.val()


def envelope():
    p,_,_=candidate()
    assert p.outer_diameter <= 230 and (p.outer_diameter-p.valve_diameter)/2 <= 50
    assert 210 <= p.outer_diameter <= 215 and 80 <= p.depth <= 90
    assert p.shell == 1.4 and p.front == 2.4 and p.collar_wall == 2
    assert p.rib_count == 8 and p.rib_height == 3
    assert p.clamp_contact_height >= 16 and p.clamp_contact_height <= p.stationary_rim_height-2


def nominal_fit():
    p,hood,clamp=candidate()
    pose=configuration(p,p.clamp_free_diameter,0)
    whole=cq.Compound.makeCompound([pose.shape('hood'),pose.shape('clamp')])
    valve=cq.Workplane('XY').circle(p.valve_diameter/2).extrude(p.valve_projection).val()
    assert whole.intersect(valve).Volume() < 0.01, 'Nominal valve interferes with printable assembly'
    band=(cq.Workplane('XY',origin=(0,0,p.stationary_rim_height))
          .circle(p.valve_diameter/2+p.disc_clearance).circle(p.valve_diameter/2)
          .extrude(p.valve_projection-p.stationary_rim_height).val())
    assert whole.intersect(band).Volume() < 0.01, '12 mm annular keepout obstructed'
    rear=(cq.Workplane('XY',origin=(0,0,p.clamp_contact_height+0.2))
          .circle(p.bore).circle(p.valve_diameter/2+p.clamp_wall).extrude(0.1).val())
    rear_leak_cm2=rear.cut(whole).Volume()/0.1/100
    assert rear_leak_cm2 < 2.5, 'Large rear shortcut around mounting clamp'
    shield=cq.Workplane('XY',origin=(0,0,1)).circle(p.valve_diameter/2).extrude(0.1).val()
    assert shield.cut(hood).Volume() < 0.01, 'Missing shield material'


def core_radius(hood,p,z):
    # V2's three fastening lands break 8-fold symmetry: check those directions too.
    angles=[p.outlet_phase,p.outlet_phase+180/p.outlet_count]+list(p.mount_angles)
    radii=[]
    for angle in angles:
        a=math.radians(angle)
        ray=cq.Edge.makeLine(cq.Vector(0,0,z),cq.Vector((p.radius+1)*math.cos(a),(p.radius+1)*math.sin(a),z))
        vertices=hood.intersect(ray).Vertices()
        radii.append(min((math.hypot(v.X,v.Y) for v in vertices),default=p.radius))
    return min(radii)


@cache
def flow_measurements():
    p,hood,clamp=candidate()
    projected=cq.Face.makeFromWires(window_profile(p)).Area()*p.outlet_count
    table=[]
    for wall_height in (20,25,30,35):
        radius=core_radius(hood,p,p.depth-wall_height)
        table.append(dict(wall_height_mm=wall_height,core_radius_mm=round(radius,3),
            radial_clearance_mm=round(radius-p.valve_diameter/2,3),
            annular_area_cm2=round(math.pi*(radius**2-(p.valve_diameter/2)**2)/100,3)))
    # The entire forward chamber widens from the disc plane, then closes at the
    # floor blend (whose radius remains larger). Mounting lands start behind it.
    disc_radius=core_radius(hood,p,p.depth-p.valve_projection)
    band_area=math.pi*(disc_radius**2-(p.valve_diameter/2)**2)
    front_gap=p.depth-p.valve_projection-p.front-p.rib_height
    turn_area=2*math.pi*(p.valve_diameter/2)*front_gap
    hm,cm=hood.Volume()/1000*1.27,clamp.Volume()/1000*1.27
    wall_moment=hm/1000*9.81*(p.depth-hood.Center().z)/1000+cm/1000*9.81*clamp.Center().z/1000
    return dict(nominal_outlet_projected_cm2=round(projected/100,3),
        downstream_disc_plane_min_area_cm2=round(band_area/100,3),
        front_clearance_over_ribs_mm=front_gap,
        conservative_front_turn_area_cm2=round(turn_area/100,3),
        added_full_flow_sections_min_cm2=round(min(projected,band_area,turn_area)/100,3),
        rear_annular_sections=table,hood_solid_petg_mass_g=round(hm,2),
        clamp_solid_petg_mass_g=round(cm,2),combined_solid_petg_mass_g=round(hm+cm,2),
        reduction_vs_v1_percent=round(100*(1-(hm+cm)/233.27),2),
        wall_horizontal_axis_gravity_moment_Nm=round(wall_moment,4),
        taper_radial_step_per_0_2_layer_mm=round(p.slope*0.2,3),
        scope='Nominal Ø130 valve; user approximate rim20 + gap15. '
              'CAD sections and assumed 1.27 g/cm³ solid PETG mass, not hydraulic, strength or acoustic qualification.')


def flow():
    m=flow_measurements()
    assert 94 <= m['nominal_outlet_projected_cm2'] <= 100, 'Retain V1 outlet area'
    assert m['added_full_flow_sections_min_cm2'] >= 94, 'Added full-flow section regressed below V1 exits'
    assert m['front_clearance_over_ribs_mm'] >= 44.6


def material():
    m=flow_measurements()
    assert m['combined_solid_petg_mass_g'] < 233.27, 'Combined printed parts must beat V1 CAD mass'


@cache
def mounting_measurements():
    p,hood,_=candidate()
    results=[]
    for diameter in (129,129.5,130,130.5,131,131.5,132):
        pose=configuration(p,diameter,0)
        answer=pose.check('hood','clamp',PairRequirement('Seated hood clears clamp; planar seats may touch',max_overlap_mm3=0.01))
        answer.require_passed()
        assert diameter/2+p.rear_flange_width >= p.bore+1, 'Rear flange no longer overlaps hood mouth'
        bolts=[]
        for a in p.mount_angles:
            x,y=bolt_position(p,a,diameter)
            shaft=(cq.Workplane('XY',origin=(x,y,p.print_depth-p.mount_pad_thickness-1))
                   .circle(1.5).extrude(p.mount_pad_thickness+2).val())
            overlap=shaft.intersect(hood).Volume()
            assert overlap < 0.01, 'M3 shaft misses adjustable slot'
            bolts.append(round(overlap,6))
        results.append(dict(diameter_mm=diameter,split_gap_mm=round((diameter+p.clamp_wall)*math.sin(gap_angle(p,diameter)/2),3),
            bolt_shaft_overlaps_mm3=bolts))
    for withdrawal in (1,8,20):
        configuration(p,130,withdrawal).check('hood','clamp',PairRequirement(
            'Axial removal after undoing three hood screws',max_overlap_mm3=0.01)).require_passed()
    # Screw-driven overclosure represents a positive preload source; force and
    # friction are deliberately unspecified. It is not simulated contact pressure.
    preload=elastic_friction_grip(interference_mm=0.1,required_retention_N=5)
    assert preload['preload_present'] and preload['retention_screen_passes'] is None
    # A head stays wider than the slot; nut-roof and pad thickness carry the load.
    assert p.mount_slot_width < 5.5 and p.mount_pad_thickness >= 2.4
    assert p.mount_tab_thickness-2.6 >= 2.4-1e-8
    return dict(geometric_poses=results,preload_screen=preload,
        mount_land_nominal_net_area_mm2=p.mount_pad_thickness*(p.mount_pad_width-p.mount_slot_width),
        nut_roof_nominal_net_area_mm2=(p.mount_tab_thickness-2.6)*(12-5.8),
        nut_roof_nominal_stress_at_5N_per_screw_MPa=5/((p.mount_tab_thickness-2.6)*(12-5.8)),
        approximate_ring_extreme_fibre_strain=(p.rear_flange_width-neutral_offset(p))*abs(1/(129/2+neutral_offset(p))-1/(132/2+neutral_offset(p))),
        scope='Constant-neutral-arc pose hypothesis for slot sizing only; real ring deformation, torque and retention remain physical.')


def mounting():
    mounting_measurements()


def tool_access():
    p,hood,_=candidate()
    # Standard 2.5 mm ball-end Allen key, <=25 degree approach. 3 mm shaft
    # envelope; start at cap-screw socket, then move outward through a window.
    for diameter in (129,130,132):
        for angle in p.mount_angles:
            x,y=bolt_position(p,angle,diameter)
            radial=cq.Vector(x,y,0).normalized()
            start=cq.Vector(x,y,p.print_depth-p.mount_pad_thickness-1.8)
            direction=cq.Vector(radial.x*math.sin(math.radians(25)),radial.y*math.sin(math.radians(25)),-math.cos(math.radians(25)))
            shaft=cq.Solid.makeCylinder(1.5,80,start,direction)
            assert hood.intersect(shaft).Volume() < 0.01, 'Ball-end Allen approach hits hood'


if __name__ == '__main__':
    envelope(); nominal_fit(); flow(); material(); mounting(); tool_access()
    print(json.dumps(dict(flow=flow_measurements(),mount=mounting_measurements()),indent=2))
