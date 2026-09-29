"""Explicit engineering assumptions; MPa = N/mm², never a filament certification."""
from dataclasses import dataclass
import math

@dataclass(frozen=True)
class Material:
    name: str
    youngs_modulus_MPa: float
    poisson_ratio: float
    source: str
    strain_limit: float | None = None

    def __post_init__(self):
        if not self.name or not self.source:
            raise ValueError('Material name and property source/assumption are required')
        if not math.isfinite(self.youngs_modulus_MPa) or self.youngs_modulus_MPa <= 0:
            raise ValueError('Young modulus must be positive and finite')
        if not math.isfinite(self.poisson_ratio) or not -1 < self.poisson_ratio < .5:
            raise ValueError('Poisson ratio must lie between -1 and 0.5')
        if self.strain_limit is not None and (not math.isfinite(self.strain_limit) or self.strain_limit <= 0):
            raise ValueError('Strain limit must be positive and finite')

PETG_SCREEN = Material('PETG screening assumption', 1200, .38,
    'Assumed effective isotropic short-term modulus, not measured filament data. '
    'Use sensitivity studies and calibrate against the actual print.', .015)
