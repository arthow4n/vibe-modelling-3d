"""Cheap concept screen. No CAD evaluation required."""
import json
import math
from components import *
from physical_analysis.screening import rectangular_cantilever


def screen():
    spring=rectangular_cantilever(length_mm=LATCH_LENGTH,width_mm=LATCH_WIDTH,
        thickness_mm=LATCH_THICKNESS,youngs_modulus_MPa=1200,tip_displacement_mm=TOOTH_RELEASE_TRAVEL)
    g=9.81
    cases=[]
    for angle in ANGLES:
        theta=math.radians(angle)
        center_y=CRADLE_BOTTOM+6+PHONE_HEIGHT/2
        center_normal=CRADLE_THICKNESS+PHONE_THICKNESS/2
        arm= center_y*math.cos(theta)-center_normal*math.sin(theta)
        # Include 0.10 kg moving printed assembly conservatively at local y=85.
        torque=PHONE_MASS_KG*g*arm+.10*g*85*math.cos(theta)
        cases.append(dict(angle_deg=angle,phone_com_Y_mm=PIVOT_Y+arm,
            rear_tipping_margin_mm=BASE_DEPTH-PIVOT_Y-arm,
            service_torque_Nmm=torque,tooth_tangential_force_N=torque/GEAR_ROOT,
            ideal_buckling_ratio=spring['fixed_free_euler_buckling_N']/(torque/GEAR_ROOT)))
    return dict(scope='Concept screen; hardware assembled, desk use only',spring=spring,
        cases=cases,assumptions=dict(phone_kg=PHONE_MASS_KG,phone_height_mm=PHONE_HEIGHT,
        phone_thickness_mm=PHONE_THICKNESS,moving_printed_mass_allowance_kg=.10,
        material='Solid PETG, assumed E=1200 MPa; sensitivity at 800 MPa required',
        finger_release_target_N=[2,12],strain_screen=.015,structural_sag_target_mm=2,
        hardware='M4 pivot and two M3 cradle bolts, two M3 latch bolts',
        rough_print_layout_mm=[230,240,40]))

if __name__=='__main__': print(json.dumps(screen(),indent=2))
