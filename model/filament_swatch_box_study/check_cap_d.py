"""D: rigid guidance, actual pad engagement/escape, relief and beam screens.

Translated pads check available contact space, not elastic insertion/release.
Material, root compliance, friction, creep and comfortable effort are unqualified.
"""
import json
from pathlib import Path
from physical_analysis import BeamApproximation
from physical_analysis.materials import Material
from cap_d_snap_5 import *


def run_checks():
    configurations=[]
    for count in (5,20):
        lower=base(count).val()
        rigid=cap(count,include_detents=False).val()
        cards=compound(*[cq.Workplane('XY').box(50.4,2.2,80.2,centered=(True,True,False))
                        .translate((0,slot_y(i,count)-.3,MAX_SEAT_HEIGHT))
                        for i in range(count)])
        assert rigid.intersect(lower).Volume()<1e-6,'Shell/pads obstruct base'
        assert rigid.distance(lower)<1e-6,'No seating stop independent of detents'
        lifts=(0,.2,.4,.8,1.6,3,5,7.2,14,40,86)
        for lift in lifts:
            pose=rigid.translate((0,0,lift))
            assert pose.intersect(lower).Volume()<1e-6,f'Rigid lift blocked at {lift}'
            assert pose.intersect(cards).Volume()<1e-6,f'Cover hits cards at {lift}'
        for y in detent_centres(count):
            for side in (-1,1):
                p=pad(y,side).val()
                assert p.intersect(lower).Volume()>1e-6,'No closed preload contact'
                assert p.translate((0,0,1)).intersect(lower).Volume()>1e-6,\
                    'No obstruction to relaxed upward withdrawal'
                for lift in (0,.4,1,3,5,7.2,14):
                    assert p.translate((side*MAX_CREST_TRAVEL,0,lift)).intersect(lower).Volume()<1e-6,\
                        'Pad cannot clear within screened stroke'
                assert leaf(y,side).val().intersect(cards).Volume()<1e-6,\
                    'Detent reaches stored cards'
        # Inner card-side clearance remains >3 mm even at the inward crest.
        assert TIP_X>50.4/2+3
        configurations.append(dict(count=count,lifts_mm=lifts,
            relaxed_closed_contact=True,relaxed_lift_1mm_blocked=True,
            pad_only_translated_escape_mm=MAX_CREST_TRAVEL,
            scope='Rigid shell guidance/seat and pad contact-space checks. '
                  'Pad translations do not establish elastic release or force.'))

    length=FLEX_LENGTH-RELIEF_ROOT_RADIUS  # Conservative shortened span at root blend.
    nominal_travel=OUTER_WIDTH/2-TIP_X
    overhang=CONTACT_Z-TIP_BOTTOM_Z
    max_end_travel=MAX_CREST_TRAVEL*(1+1.5*overhang/length)
    assert max_end_travel+.2<BACK_RELIEF,'Insufficient relief for below-contact extension'
    screens=[]
    for modulus in (1000,2000):
        material=Material('Uncalibrated PETG effective assumption',modulus,.38,
                          'Explicit homogeneous isotropic screening assumption',.015)
        for travel in (nominal_travel-MATING_HALF_WIDTH_ERROR,nominal_travel,
                       nominal_travel+MATING_HALF_WIDTH_ERROR,MAX_CREST_TRAVEL):
            s=BeamApproximation(length,STEM_WIDTH,STEM_THICKNESS,
                'End-loaded uniform stem; root blend shortens effective span; '
                'pad rotation, wall compliance, layers, friction and concentrations omitted',
                tip_displacement_mm=travel).screen(material)
            assert s['small_deflection_applicable']
            assert s['root_strain']<material.strain_limit,'Provisional strain screen exceeded'
            # Ramp slope translates transverse spring work into axial effort.
            # This is an order-of-force screen, not complete cam/contact mechanics.
            ramp_slope=(CAP_INNER_X/2-TIP_X)/(TIP_LOWER_Z-TIP_BOTTOM_Z)
            screens.append(dict(modulus_MPa=modulus,travel_mm=travel,beam=s,
                four_pad_ramp_force_order_N=4*s['force_N']*ramp_slope))
    return dict(configurations=configurations,beam_screens=screens,
        flexure_relief=dict(behind_stem_mm=BACK_RELIEF,
            estimated_worst_free_end_travel_mm=max_end_travel,
            retained_clearance_margin_mm=BACK_RELIEF-max_end_travel),
        assumptions='0.75–1.15 mm centred crest travel assumes ±0.2 mm mating half-width error. '
            'A 1.55 mm one-sided bound also adds 0.4 mm nominal guide play conservatively. '
            'These are not measured print dimensions. Four times a worst one-sided spring '
            'force is not the simultaneous paired pull force. Beam strain limit 1.5% is provisional; '
            'solid stem toolpaths, layers and material response require separate evidence.',
        limits='No calibrated holding/pull force, nonlinear contact sequence, creep, fatigue, '
               'loaded carrying or printed operation qualification.')


if __name__=='__main__':
    record=run_checks()
    Path(__file__).parent.joinpath('notes/cap_d_checks.json').write_text(
        json.dumps(record,indent=2)+'\n')
    print(json.dumps(dict(configurations=record['configurations'],
                         flexure_relief=record['flexure_relief'],
                         strain_range=[min(s['beam']['root_strain'] for s in record['beam_screens']),
                                       max(s['beam']['root_strain'] for s in record['beam_screens'])])))
