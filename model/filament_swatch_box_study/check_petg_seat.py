"""Locating and leaf-travel screens; no nonlinear contact/fatigue claim.

Nominal envelopes are conservative for the card's bottom corner chamfers.
The side-edge bevel/round is screened at the pad's rear-most contact line.
"""
import json
import math
from pathlib import Path
import cadquery as cq
from card_base_petg_5 import *
from physical_analysis import BeamApproximation
from physical_analysis.materials import Material


def run_checks():
    rigid = build_base(include_leaves=False).val()
    evidence = {"seated_rigid_checks": [], "leaf_screens": [],
                "limits": "No contact solve, friction/creep calibration or printed strength. "
                          "Headroom bounds are travel screens, not deformed whole-leaf proof."}
    for index in range(CARD_COUNT):
        y = slot_y(index, CARD_COUNT)
        for width, thickness in ((49.6, 1.8), (50, 2), (50.4, 2.2)):
            card = block(END_DATUM_X, END_DATUM_X+width,
                         y-SLOT_WIDTH/2, y-SLOT_WIDTH/2+thickness,
                         FLOOR, FLOOR+80).val()
            assert rigid.intersect(card).Volume() < 1e-6, "Rigid locator obstructs seat"
            assert front_leaf(y).val().intersect(card).Volume() > 0, "Missing front preload"
            assert side_leaf(y).val().intersect(card).Volume() > 0, "Missing side preload"
            # Rear edge at y=-1.2 is 0.2 above original swatch bed face.
            # R2 edge-round inset = 2-sqrt(4-.2^2) = ~0.010 mm.
            front_travel = thickness-SLOT_WIDTH/2-FRONT_FREE_Y
            side_travel = END_DATUM_X+width-SIDE_FREE_X-0.011
            assert 0 < front_travel < FRONT_RELIEF_BACK_Y-(FRONT_ROOT_Y+FRONT_LEAF_THICKNESS)
            assert 0 < side_travel < SIDE_RELIEF_OUTER_X-(SIDE_ROOT_X+SIDE_LEAF_THICKNESS)
            evidence["seated_rigid_checks"].append(dict(slot=index, width=width,
                thickness=thickness, front_travel_mm=front_travel, side_travel_mm=side_travel))
    # Independent guide check with both leaves omitted: hand correction through
    # the four-sided funnel must not rely on a spring to remove a rigid blockage.
    directions = [(-1,0), (1,0), (0,-1), (0,1), (-1,-1), (-1,1), (1,-1), (1,1)]
    for sx, sy in directions:
        for step in range(11):
            f = step/10
            lean_x, lean_y, yaw = sy*2*(1-f), sx*2*(1-f), sx*(1-f)
            drop = 25.2*abs(math.sin(math.radians(lean_y))) + 1.1*abs(
                math.sin(math.radians(lean_x))*math.cos(math.radians(lean_y)))
            card = (cq.Workplane('XY').box(50.4, 2.2, 80, centered=(True,True,False))
                    .rotate((0,0,0), (1,0,0), lean_x)
                    .rotate((0,0,0), (0,1,0), lean_y)
                    .rotate((0,0,0), (0,0,1), yaw)
                    .translate((0.2*f+sx*1.5*(1-f), -0.3*f+sy*(1-f),
                                TOP_Z-0.2-3.8*f+drop))).val()
            assert rigid.intersect(card).Volume() < 1e-6, f'Rigid funnel blocks direction {sx,sy}, step {step}'
    evidence['guide_entry'] = dict(samples=88, slot=2, bottom_travel_mm=3.8,
        step_mm=.38, initial_offsets_mm=[1.5,1], tilt_degrees=2, yaw_degrees=1,
        dimensions_mm=[50.4,2.2,80], result='No rigid-guide intersection detected at sampled poses',
        limitations='Leaves omitted: does not qualify elastic insertion or passive centering. Neighbours unchanged 7 mm pitch.')
    # A deliberately stiff short uniform surrogate: only the 10 mm stem flexes,
    # rigid upper ramp. Used to reject an obviously unsuitable first trial.
    # Pad/contact lever-arm details are unresolved; this is not a force rating.
    for name, b, t, travel in (("front", FRONT_LEAF_WIDTH, FRONT_LEAF_THICKNESS, 0.85),
                               ("side", SIDE_LEAF_WIDTH, SIDE_LEAF_THICKNESS, 0.95)):
        for modulus, length in ((1000, 10), (2000, 10), (1000, 13), (2000, 13)):
            material = Material("PETG trial effective assumption", modulus, .38,
                "Explicit uncalibrated isotropic assumption for concept sensitivity", .015)
            approx = BeamApproximation(length, b, t,
                "Compare short 10 mm stem with 13 mm contact height, uniform stem "
                "idealization; not nonlinear contact, pad torsion or loaded-return prediction",
                tip_displacement_mm=travel)
            screen = approx.screen(material)
            assert screen['root_strain'] < material.strain_limit
            evidence["leaf_screens"].append(dict(leaf=name, modulus_MPa=modulus,
                                                 length_mm=length, travel_mm=travel, screen=screen))
    evidence["nominal_front_touch_screen"] = []
    for modulus in (1000, 2000):
        material = Material("PETG concept assumption", modulus, .38,
                            "Uncalibrated effective modulus")
        beam = BeamApproximation(PAD_HEIGHT, FRONT_LEAF_WIDTH, FRONT_LEAF_THICKNESS,
                                 "Uniform front stem to nominal contact height",
                                 tip_displacement_mm=0.35).screen(material)
        evidence["nominal_front_touch_screen"].append(dict(
            modulus_MPa=modulus, nominal_pad_force_N=beam['force_N'],
            tip_force_to_overcome_seating_moment_N=beam['force_N']*PAD_HEIGHT/80,
            limitation="Approximate moment balance; not an observed holding force, "
                       "includes no friction or detailed pad contact."))
    return evidence


if __name__ == "__main__":
    evidence = run_checks()
    destination = Path(__file__).parent / "notes" / "petg_seat_checks.json"
    destination.write_text(json.dumps(evidence, indent=2)+"\n")
    print(json.dumps(evidence, indent=2))
