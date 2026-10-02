"""Specific seating and force screens for the stronger-clip corner-seat trial.

Rigid checks exclude spring deformation; spring/card overlap is intentional.
Actual corner bevel surfaces are contained by the conservative full-thickness
chamfered envelope. No friction, creep, comfort or nonlinear-contact proof.
"""
import json
import math
from pathlib import Path
import cadquery as cq
from physical_analysis import BeamApproximation
from physical_analysis.materials import Material
from card_base_corner_seat_5 import *
from study import UPRIGHT_HEIGHT, CARD_THICKNESS


def card_envelope(width=UPRIGHT_WIDTH, thickness=CARD_THICKNESS,
                  chamfer=BOTTOM_CORNER_CHAMFER):
    half=width/2
    points=[(-half+chamfer,0),(half-chamfer,0),(half,chamfer),
            (half,UPRIGHT_HEIGHT),(-half,UPRIGHT_HEIGHT),(-half,chamfer)]
    return cq.Workplane('XZ').polyline(points).close().extrude(thickness)


def seated_height(width, chamfer):
    return FLOOR+(width-UPRIGHT_WIDTH)/2+BOTTOM_CORNER_CHAMFER-chamfer


def placed_card(index, width, thickness, chamfer, dx=0, lift=0):
    return card_envelope(width,thickness,chamfer).translate((
        dx,slot_y(index,CARD_COUNT)-SLOT_WIDTH/2+thickness,
        seated_height(width,chamfer)+lift)).val()


def run_checks():
    rigid=build_base(include_leaves=False).val()
    seats=[]
    for index in range(CARD_COUNT):
        y=slot_y(index,CARD_COUNT)
        for width,thickness,chamfer in (
            (49.6,1.8,3.8),(49.6,2.2,4.2),(50,2,4),(50.4,1.8,3.8),(50.4,2.2,4.2)):
            card=placed_card(index,width,thickness,chamfer)
            assert rigid.intersect(card).Volume()<1e-6, 'Rigid seat obstructs card'
            distances=[card.distance(corner_seat(y,side).val()) for side in (-1,1)]
            assert max(distances)<1e-6, 'Card does not reach both corner seats'
            assert seated_height(width,chamfer)>FLOOR-FLOOR_RELIEF_DEPTH
            assert front_leaf(y).val().intersect(card).Volume()>0, 'Missing front preload'
            for dx in (-.1,.1):
                shifted=placed_card(index,width,thickness,chamfer,dx=dx)
                assert rigid.intersect(shifted).Volume()>1e-5, 'Sideways dead zone at seat'
            seats.append(dict(slot=index,width_mm=width,thickness_mm=thickness,
                chamfer_mm=chamfer,height_mm=seated_height(width,chamfer),
                left_right_distance_mm=distances))
    # A raised, offset card can translate downward toward the seat on either side.
    for side in (-1,1):
        for step in range(11):
            f=step/10
            dx=side*1.5*(1-f)
            card=placed_card(2,50,2,4,dx=dx,lift=abs(dx)+.05*(1-f))
            assert rigid.intersect(card).Volume()<1e-6, 'Corner-guided path blocked'
    # Funnel paths, ±1.5 X / ±1 Y, ±2-degree lean, ±1-degree yaw;
    # hand correction toward the back datum over 3.8 mm lowest-corner travel.
    for sx,sy in ((-1,0),(1,0),(0,-1),(0,1),(-1,-1),(-1,1),(1,-1),(1,1)):
        for step in range(11):
            f=step/10
            ax,ay,yaw=sy*2*(1-f),sx*2*(1-f),sx*(1-f)
            drop=25.2*abs(math.sin(math.radians(ay)))+1.1*abs(
                math.sin(math.radians(ax))*math.cos(math.radians(ay)))
            card=(card_envelope(50.4,2.2,4).translate((0,1.1,0))
                  .rotate((0,0,0),(1,0,0),ax).rotate((0,0,0),(0,1,0),ay)
                  .rotate((0,0,0),(0,0,1),yaw)
                  .translate((sx*1.5*(1-f),sy*(1-f)-.3*f,
                              TOP_Z-.2-3.8*f+drop))).val()
            assert rigid.intersect(card).Volume()<1e-6, 'Funnel correction blocked'
    screens=[]
    for modulus in (1000,2000):
        material=Material('PETG trial assumption',modulus,.38,
            'Explicit uncalibrated homogeneous isotropic effective modulus',.015)
        for travel in (.35,.55,.85):
            screen=BeamApproximation(PAD_HEIGHT,FRONT_LEAF_WIDTH,FRONT_LEAF_THICKNESS,
                'Uniform stem to 13 mm contact; local pad/plate/root/layer effects omitted',
                tip_displacement_mm=travel).screen(material)
            assert screen['small_deflection_applicable']
            assert screen['root_strain']<material.strain_limit
            assert travel<FRONT_RELIEF_BACK_Y-FRONT_ROOT_Y-FRONT_LEAF_THICKNESS
            screens.append(dict(modulus_MPa=modulus,travel_mm=travel,screen=screen))
    return dict(seated_geometry=seats,
        guidance=dict(funnel_samples=88,corner_samples=22,corner_step_mm=.15,
            result='No rigid intersection at sampled hand-guided poses; leaves omitted'),
        stiffness_ratio_vs_printed_1mm_stem=(FRONT_LEAF_THICKNESS/1.0)**3,
        beam_screens=screens,
        limits='Contact/entry friction, pad plate-bending, root strain concentrations, '
               'printed material response and fatigue need physical evidence. '
               'Grip ratio is not calibrated. Seated height changes with width/chamfer size.')


if __name__=='__main__':
    evidence=run_checks()
    path=Path(__file__).parent/'notes/corner_seat_checks.json'
    path.write_text(json.dumps(evidence,indent=2)+'\n')
    print(json.dumps(dict(seat_cases=len(evidence['seated_geometry']),
                          guidance=evidence['guidance'],
                          stiffness_ratio=evidence['stiffness_ratio_vs_printed_1mm_stem'])))
