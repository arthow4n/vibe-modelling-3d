"""Cheap rejection screens before meshing. Explicit idealizations, mm/N/MPa."""
import math
from .case import positive


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
