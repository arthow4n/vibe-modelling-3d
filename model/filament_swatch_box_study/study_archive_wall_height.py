"""Minimum-height screen for a continuous-rim archive, not a print model.

Single rigid card, desk-supported tray, gravity only. A friction-independent
restoring-moment screen at floor-supported first wall contact. Ignore any
retaining benefit from the flared/rounded entry; count only its straight guide.
No dynamics, contact-force solve, physical mass calibration or escape proof.
"""
from pathlib import Path
import hashlib
import json
import math
import numpy as np
import cadquery as cq
from study import swatch_dimension
import archive_r1_base_15 as r1
import swatch_reference as ref

ROOT = Path(__file__).parent
CARD_HEIGHT = ref.WIDTH  # SCAD +X becomes upright +Z: 80, not ref.HEIGHT (50).
CARD_WIDTH = ref.HEIGHT
THICKNESS = ref.THICKNESS
FLOOR = r1.FLOOR
DEPTH = r1.POCKET_DEPTH
ANGLES = np.radians(np.linspace(.25, 70, 2791))
EDGE_TRANSITION = .6  # Study allowance below the funnel; not a finished radius.


def height_screen(cg_height, cg_inward):
    """Height making gravity restore inward at every feasible first contact.

    theta = lean from vertical. Lowest bottom outer edge rests on the floor.
    Its offset to the wall is h*tan(theta). CG relative to that edge projects
    cg_height*sin(theta) - cg_inward*cos(theta) toward the wall. Therefore
    h >= cg_height*cos(theta) - cg_inward*cos(theta)**2/sin(theta).
    Test whether the peak contact fits the finite pocket, rather than assume
    the card must lean from its far end.
    """
    sin, cos = np.sin(ANGLES), np.cos(ANGLES)
    required = cg_height*cos-cg_inward*cos*cos/sin
    travel = required*np.tan(ANGLES)
    i = int(np.argmax(required))
    assert travel[i] <= DEPTH-THICKNESS*cos[i], 'Critical thin-axis pose cannot fit'
    return dict(required_straight_height_mm=float(required[i]),
                critical_lean_deg=float(np.degrees(ANGLES[i])),
                bottom_edge_to_wall_mm=float(travel[i]))


def gravity_margin(guide_height, cg_height=40., cg_inward=1.):
    """Minimum projected CG-to-contact margin over feasible thin-axis poses."""
    sin, cos = np.sin(ANGLES), np.cos(ANGLES)
    feasible = guide_height*np.tan(ANGLES)+THICKNESS*cos <= DEPTH
    margin = guide_height*np.tan(ANGLES)-cg_height*sin+cg_inward*cos
    return float(np.min(margin[feasible]))


def floor_supported_pose(card, angle, direction, guide_height):
    theta = math.radians(angle)
    # This source card has real flat bottom material at both thickness edges.
    # CAD floor-distance and +/- wall-contact witnesses below verify the fixture.
    shift = direction*(DEPTH/2-guide_height*math.tan(theta)
                       -THICKNESS/2*math.cos(theta))
    return (card.rotate((0,0,FLOOR),(1,0,FLOOR),-direction*angle)
            .translate((0,shift,THICKNESS/2*math.sin(theta))))


def main():
    card = ref.card(-THICKNESS/2).val()
    assert card.isValid()
    cg = card.Center()
    # A centred full-thickness flat bottom survives the source's corner chamfers.
    # For a horizontal fall direction n, its support radius is
    # b(n)=half_flat_width*abs(n_x)+half_thickness*abs(n_y). Its inward CG
    # offset is >=min(half_flat_width-abs(CG_x),half_thickness-abs(CG_y)).
    # Thus thin-axis leverage also bounds yaw/diagonal directions in this
    # conservative first-contact screen; no favourable side-wall friction needed.
    half_flat = CARD_WIDTH/2-swatch_dimension('left_chamfer_size')
    bottom_probe = r1.g.block(-half_flat+.01,half_flat-.01,
        -THICKNESS/2+.01,THICKNESS/2-.01,FLOOR,FLOOR+.01).val()
    assert bottom_probe.cut(card).Volume()<1e-7, 'Flat support footprint assumption fails'
    minimum_inward = min(half_flat-abs(cg.x),THICKNESS/2-abs(cg.y))
    all_direction_bound = height_screen(cg.z-FLOOR,minimum_inward)
    actual = {str(d):height_screen(cg.z-FLOOR, THICKNESS/2-d*cg.y)
              for d in (-1,1)}
    envelope = height_screen(CARD_HEIGHT/2, THICKNESS/2)
    controlling = max(envelope['required_straight_height_mm'],
        all_direction_bound['required_straight_height_mm'])
    # Sensitivity is an explicit mass-distribution scenario, not a PETG property.
    sensitivities = [dict(assumed_cg_height_mm=h, **height_screen(h,THICKNESS/2))
                     for h in (38.,40.,42.,44.)]

    # Resolve the geometric contact fixture with the actual source swatch.
    # These masks are straight retaining faces only, not replacement base CAD.
    floor = r1.g.block(-30,30,-DEPTH/2,DEPTH/2,0,FLOOR).val()
    records = []
    for guide in (30.,34.,36.,40.):
        for d in (-1,1):
            ys = sorted((d*DEPTH/2,d*(DEPTH/2+4)))
            wall = r1.g.block(-30,30,*ys,FLOOR+.1,FLOOR+guide).val()
            for angle in (4.,12.,actual[str(d)]['critical_lean_deg'],25.):
                pose = floor_supported_pose(card,angle,d,guide)
                inward = pose.translate((0,-d*.02,0))
                outward = pose.translate((0,d*.02,0))
                assert inward.intersect(wall).Volume()<1e-7
                assert outward.intersect(wall).Volume()>1e-5
                assert pose.distance(floor)<1e-7
                # The other bottom thickness edge must remain inside the pocket.
                theta = math.radians(angle)
                bottom_to_wall = guide*math.tan(theta)
                assert bottom_to_wall+THICKNESS*math.cos(theta)<DEPTH
                margin = DEPTH/2-d*pose.Center().y
                records.append(dict(straight_height_mm=guide,direction=d,
                    lean_deg=angle,gravity_restoring_lever_mm=margin,
                    source_card_floor_and_wall_contacts_verified=True))

    candidates = []
    for funnel in (0.,1.,2.,4.):
        threshold = controlling+funnel+EDGE_TRANSITION
        rounded = math.ceil(threshold)
        candidates.append(dict(entry_height_mm=funnel,
            extra_transition_allowance_mm=EDGE_TRANSITION,
            screened_wall_minimum_mm=threshold,
            rounded_candidate_mm=rounded,
            exposed_card_mm=CARD_HEIGHT-rounded,
            straight_guide_at_candidate_mm=rounded-funnel-EDGE_TRANSITION,
            minimum_uniform_gravity_lever_mm=gravity_margin(
                rounded-funnel-EDGE_TRANSITION)))

    preferred = [dict(wall_height_mm=h,entry_height_mm=2.,
                      guaranteed_straight_mm=h-2-EDGE_TRANSITION,
                      uniform_gravity_margin_mm=gravity_margin(h-2-EDGE_TRANSITION))
                 for h in (36.,38.,39.,40.,42.)]

    report = dict(study='continuous-rim minimum-height screen',
        upright_card_mm=[CARD_WIDTH,CARD_HEIGHT,THICKNESS],pocket_depth_mm=DEPTH,
        source_solid_cg_mm=[cg.x,cg.y,cg.z-FLOOR],
        uniform_rectangle=envelope,source_solid_front_back=actual,
        source_flat_bottom_mm=[2*half_flat,THICKNESS],
        all_fall_direction_source_bound=all_direction_bound,
        controlling_straight_height_mm=controlling,
        source_geometry_contact_witnesses=records,
        mass_distribution_sensitivity=sensitivities,entry_candidates=candidates,
        two_mm_entry_comparison=preferred,
        interpretation='Smallest heights passing this sufficient restoring-moment screen; '
            'not absolute escape thresholds. Ignoring entry support is conservative. '
            'Failing the screen does not prove a card falls out. Contact cases cover '
            'thin-axis front/back leaning; an inscribed bottom footprint bounds other '
            'horizontal fall directions. Actual curved rim/corner transitions, hood/key '
            'interfaces and dynamic behaviour need review before print delivery.',
        limits='Rigid card on a horizontal desk; no friction credited. Uniform-envelope '
            'and homogeneous-source CGs are explicit models, not measured printed CG. '
            'Near-threshold candidates have little restoring margin. No impacts, shaking, '
            'manual lifting, open-box carrying, creep, print calibration or physical validation.',
        source_sha256={name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest()
            for name in ('study_archive_wall_height.py','swatch_reference.py',
                         'archive_r1_base_15.py','study.py','card_base_test.py',
                         'cap_g_module_5.py','cap_e_thin_5.py',
                         '../filament_archive_swatch/filament_archive_swatch.scad')})
    path = ROOT/'notes/archive_wall_height_study.json'
    path.write_text(json.dumps(report,indent=2)+'\n')
    # Standard plotting artifact for comparing height with restoring leverage.
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig,ax = plt.subplots(figsize=(9.6,5.6))
    fig.subplots_adjust(bottom=.19,top=.9,left=.11,right=.98)
    heights = np.linspace(28,45,171)
    for funnel,color in ((0.,'#819398'),(2.,'#277b6b'),(4.,'#617dad')):
        ax.plot(heights,[gravity_margin(h-funnel-EDGE_TRANSITION) for h in heights],
                color=color,label=f'{funnel:g} mm entry + 0.6 mm transition')
    ax.axhline(0,color='#a84455',linestyle='--',label='Zero restoring margin')
    ax.scatter([38,40],[gravity_margin(35.4),gravity_margin(37.4)],
               color='#277b6b',zorder=4)
    ax.annotate('38 mm: close to limit',xy=(38,gravity_margin(35.4)),
                xytext=(34,-1.0),arrowprops={'arrowstyle':'->','color':'#277b6b'})
    ax.annotate('40 mm + short entry',xy=(40,gravity_margin(37.4)),
                xytext=(36,1.15),arrowprops={'arrowstyle':'->','color':'#277b6b'})
    ax.set(xlabel='Continuous wall height above card floor (mm)',
           ylabel='Minimum projected restoring lever (mm)',ylim=(-3.3,1.5),
           title='One 80 × 2 mm card: lowest wall-height screen')
    ax.grid(alpha=.2)
    ax.legend(loc='lower right',fontsize=9)
    fig.text(.015,.025,'Rigid uniform card, gravity only. Entry retention ignored; no physical or dynamic validation.',fontsize=8)
    stem = ROOT/'renders/concepts/archive_wall_height_screen'
    for suffix in ('.svg','.png'):
        artifact = stem.with_suffix(suffix)
        fig.savefig(artifact,dpi=160)
        if suffix=='.svg':
            artifact.write_text('\n'.join(line.rstrip()
                for line in artifact.read_text().splitlines())+'\n')
    plt.close(fig)
    print(json.dumps(dict(report=str(path),controlling_straight_height_mm=controlling,
        uniform_rectangle=envelope,source_solid_cg_mm=report['source_solid_cg_mm'],
        source_solid_front_back=actual,entry_candidates=candidates,
        contact_cases=len(records),mass_distribution_sensitivity=sensitivities,
        two_mm_entry_comparison=preferred)))


if __name__=='__main__':
    main()
