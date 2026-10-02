"""Consequential E checks: foot seating, guidance, contents and pad escape space.

Rigid pad translations are clearance witnesses, not an elastic contact solution.
"""
import json
from pathlib import Path
from physical_analysis import BeamApproximation
from physical_analysis.materials import Material
from cap_e_thin_5 import *


def run_checks():
    configurations=[]
    for count in (5,20):
        lower=base(count,include_detents=False).val()
        hood=cap(count).val()
        cards=compound(*[cq.Workplane('XY').box(50.4,2.2,80.2,centered=(True,True,False))
                        .translate((0,slot_y(i,count)-.3,MAX_SEAT_HEIGHT))
                        for i in range(count)])
        assert hood.intersect(lower).Volume()<1e-6,'Rigid body or foot obstructs hood'
        assert hood.distance(lower)<1e-6,'Rim does not contact base foot'
        assert hood.translate((0,0,.2)).distance(lower)>.05,'Rim remains seated after lift'
        lifts=(0,.2,.5,1,2,4,8,12,16,30,84)
        for lift in lifts:
            pose=hood.translate((0,0,lift))
            assert pose.intersect(lower).Volume()<1e-6,f'Guidance blocked at {lift}'
            assert pose.intersect(cards).Volume()<1e-6,f'Hood hits cards at {lift}'
        for y in detent_centres(count):
            for side in (-1,1):
                p=pad(y,side).val()
                assert p.intersect(hood).Volume()>1e-6,'Missing closed preload contact'
                assert p.intersect(hood.translate((0,0,1))).Volume()>1e-6,\
                    'Relaxed pad does not obstruct withdrawal'
                for lift in (0,.5,1,2,4,8,12,16):
                    for play in (-FIT_GAP,0,FIT_GAP):
                        # Include positive half-width error with the pad witness.
                        witness=p.translate((-side*(MAX_CREST_TRAVEL-MATING_HALF_WIDTH_ERROR),0,0))
                        pose=hood.translate((play,0,lift))
                        assert witness.intersect(pose).Volume()<1e-6,'No screened pad escape space'
                for travel in (0,MAX_CREST_TRAVEL):
                    assert leaf(y,side).val().translate((-side*travel,0,0)).intersect(cards).Volume()<1e-6,\
                        'Closure leaf reaches card envelope'
        # These probes answer skin thickness at the actual blind pocket floor.
        y=detent_centres(count)[0]
        for side in (-1,1):
            skin=block(CAP_INNER_X/2+GROOVE_DEPTH+.01,BAND_X/2-.01,
                       y-.5,y+.5,19.5,19.9)
            skin=mirrored(skin,side).val()
            assert abs(skin.Volume()-skin.intersect(hood).Volume())<1e-6,'Pocket skin interrupted'
        configurations.append(dict(count=count,lifts_mm=lifts,rim_seated=True,
            guide_and_card_path_clear=True,relaxed_pad_preload_and_withdrawal_contact=True,
            pad_only_escape_stroke_mm=MAX_CREST_TRAVEL,
            pocket_skin_mm=BAND_WALL-GROOVE_DEPTH))
    length=FLEX_LENGTH-ROOT_BLEND
    free_span=TIP_TOP_Z-(ROOT_Z+ROOT_BLEND)
    end_travel=MAX_CREST_TRAVEL*(3*free_span-length)/(2*length)
    assert end_travel+.2<BACK_RELIEF,'Rear pocket does not clear rotated tip extension'
    screens=[]
    for modulus in (1000,2000):
        material=Material('Uncalibrated effective PETG',modulus,.38,
                          'Homogeneous isotropic assumption, not printed calibration',.015)
        for travel in (NOMINAL_CREST_TRAVEL-GROOVE_DEPTH,NOMINAL_CREST_TRAVEL,
                       MAX_CREST_TRAVEL):
            answer=BeamApproximation(length,STEM_WIDTH,STEM_THICKNESS,
                'Uniform end-loaded stem, conservative shortened span; wall compliance, '
                'layer anisotropy, pad rotation, friction and root concentrations omitted',
                tip_displacement_mm=travel).screen(material)
            assert answer['small_deflection_applicable']
            assert answer['root_strain']<material.strain_limit
            screens.append(dict(modulus_MPa=modulus,travel_mm=travel,beam=answer))
    return dict(configurations=configurations,beam_screens=screens,
        free_end_travel_mm=end_travel,rear_clearance_margin_mm=BACK_RELIEF-end_travel,
        scope='Rigid guidance, rim contact, card envelope, blind-pocket skin and translated pad space. '
              'Beam screens use an explicit uncalibrated effective-solid assumption.',
        limits='No proof of coupled elastic passage or measured retention/press/pull force. '
               'Physical shell feel, optical appearance, creep and fatigue remain unknown.')


if __name__=='__main__':
    record=run_checks()
    Path(__file__).parent.joinpath('notes/cap_e_checks.json').write_text(json.dumps(record,indent=2)+'\n')
    print(json.dumps(dict(configurations=record['configurations'],
                         maximum_strain=max(s['beam']['root_strain'] for s in record['beam_screens']),
                         rear_clearance_margin_mm=record['rear_clearance_margin_mm'])))
