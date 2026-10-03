"""Cheap rejection screens before meshing. Explicit idealizations, mm/N/MPa."""
import math
from .case import positive


def elastic_friction_grip(*, interference_mm, contact_count=1, stiffness_N_mm=None,
                          friction_coefficient=None, required_retention_N=None):
    """Screen a friction-only elastic grip before meshing or printing.

    Interference is signed, in the contact normal direction: negative means a
    gap; positive requires elastic compression. No external normal load, hook,
    magnet, gravity restraint or wedge/cam contribution is included. Unknown
    stiffness/friction stays unknown. Nonzero preload alone is not validation.
    """
    if not math.isfinite(interference_mm):
        raise ValueError('Interference must be finite')
    if isinstance(contact_count, bool) or not isinstance(contact_count, int) or contact_count <= 0:
        raise ValueError('Contact count must be a positive integer')
    for name, value in (('stiffness_N_mm', stiffness_N_mm),
                        ('required_retention_N', required_retention_N)):
        if value is not None:
            positive(value, name)
    if friction_coefficient is not None and (not math.isfinite(friction_coefficient)
                                             or friction_coefficient < 0):
        raise ValueError('Friction coefficient must be finite and nonnegative')
    travel = max(0., interference_mm)
    normal = 0. if not travel else (None if stiffness_N_mm is None
                                    else contact_count * stiffness_N_mm * travel)
    retention = 0. if not travel or friction_coefficient == 0 else (
        None if normal is None or friction_coefficient is None else normal * friction_coefficient)
    passes = False if retention == 0 else (
        None if retention is None or required_retention_N is None else retention >= required_retention_N)
    return dict(preload_present=travel > 0, spring_travel_mm=travel,
                normal_force_N=normal, friction_retention_N=retention,
                retention_screen_passes=passes,
                assumptions='Equal linear elastic contacts; no other retaining force or external normal load. '
                            'Friction is an assumed Coulomb capacity along a sliding contact, not a full '
                            'insertion/release force, creep, wear or printed validation.')


def rectangular_cantilever(*, length_mm, width_mm, thickness_mm, youngs_modulus_MPa,
                           tip_force_N=None, tip_displacement_mm=None):
    """Euler–Bernoulli end-loaded cantilever; not a complete snap-force model."""
    for name,value in locals().copy().items():
        if name not in ('tip_force_N','tip_displacement_mm'): positive(value,name)
    if (tip_force_N is None)==(tip_displacement_mm is None):
        raise ValueError('Specify exactly one of tip force or tip displacement')
    supplied=tip_force_N if tip_force_N is not None else tip_displacement_mm
    if not math.isfinite(supplied): raise ValueError('Load/travel must be finite')
    inertia=width_mm*thickness_mm**3/12
    stiffness=3*youngs_modulus_MPa*inertia/length_mm**3
    force=tip_force_N if tip_force_N is not None else stiffness*tip_displacement_mm
    travel=force/stiffness
    return dict(force_N=force,tip_displacement_mm=travel,stiffness_N_mm=stiffness,
        root_strain=abs(3*thickness_mm*travel/(2*length_mm**2)),
        fixed_free_euler_buckling_N=math.pi**2*youngs_modulus_MPa*inertia/(4*length_mm**2),
        small_deflection_applicable=abs(travel)/length_mm<=.1 and length_mm/thickness_mm>=10,
        assumptions='Straight slender homogeneous elastic rectangular cantilever; no notches/contact/layer effects. '
                    'Euler load is an ideal instability estimate, not a strength rating.')


def circular_cam_detent(*, stiffness_N_mm, radius_sum_mm, transverse_spacing_mm):
    """Frictionless circular cams driving a linear transverse spring.

    The straight travel coordinate is x; the cam center normal separation during
    contact is y=sqrt(R²-x²), spring travel y-g and sliding force k*(y-g)*x/y.
    Its maximum occurs at y=(g*R²)^(1/3). This is an order-of-force screen:
    rigid circular profiles, no spring-axis shortening, head rotation, friction,
    enclosure/guide compliance, layer effects or calibrated material law.
    Input stiffness must come from a documented assumption or actual evidence.
    """
    for name,value in (('stiffness_N_mm',stiffness_N_mm),('radius_sum_mm',radius_sum_mm),
                       ('transverse_spacing_mm',transverse_spacing_mm)):
        positive(value,name)
    r,g=radius_sum_mm,transverse_spacing_mm
    engaged=g<r
    peak_y=(g*r*r)**(1/3) if engaged else r
    peak_x=math.sqrt(max(0,r*r-peak_y*peak_y)) if engaged else 0
    return dict(contact_possible=engaged,
        peak_slide_force_N=stiffness_N_mm*peak_x*(1-g/peak_y) if engaged else 0,
        peak_force_axial_offset_mm=peak_x,
        maximum_spring_travel_mm=max(0,r-g),
        contact_half_travel_mm=math.sqrt(max(0,r*r-g*g)),
        assumptions='Frictionless rigid circular cams and a linear transverse spring; '
                    'no axial shortening, head rotation, guide motion or material/process calibration.')
