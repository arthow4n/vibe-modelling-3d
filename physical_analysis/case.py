"""Solver-independent static physical questions in mm, N, MPa."""
from dataclasses import dataclass, field
from pathlib import Path
import math
import re
from typing import Any, Protocol
from .materials import Material
from execution.telemetry import operation


def positive(value, name):
    if not math.isfinite(value) or value <= 0:
        raise ValueError(f'{name} must be positive and finite')


def vector(value):
    result = tuple(float(x) for x in value)
    if len(result) != 3 or not all(math.isfinite(x) for x in result):
        raise ValueError('Expected three finite vector components')
    return result

@dataclass(frozen=True)
class Region:
    """Closed coordinate box in assembly coordinates; a plane is a thin box.

    Boundary conditions use nodes. Loads and contact use entire exterior faces;
    mesh faces must fit inside the region. Empty selections fail explicitly.
    """
    lower: tuple = (-math.inf,) * 3
    upper: tuple = (math.inf,) * 3
    tolerance_mm: float = 1e-5

    def __post_init__(self):
        positive(self.tolerance_mm, 'Region tolerance')
        if len(self.lower) != 3 or len(self.upper) != 3 or any(
            math.isnan(a) or math.isnan(b) or a > b for a, b in zip(self.lower, self.upper)
        ):
            raise ValueError('Invalid region bounds')

    @classmethod
    def plane(cls, axis: str, position_mm: float, tolerance_mm=1e-5):
        if axis not in ('x', 'y', 'z') or not math.isfinite(position_mm):
            raise ValueError('Plane requires x/y/z and a finite coordinate')
        lo, hi = [-math.inf]*3, [math.inf]*3
        lo['xyz'.index(axis)] = hi['xyz'.index(axis)] = position_mm
        return cls(tuple(lo), tuple(hi), tolerance_mm)

    def contains(self, point):
        return all(a-self.tolerance_mm <= x <= b+self.tolerance_mm
                   for x, a, b in zip(point, self.lower, self.upper))

@dataclass(frozen=True)
class Selection:
    part: str
    region: Region

@dataclass
class Part:
    name: str
    shape: Any
    material: Material
    mesh_size_mm: float

@dataclass(frozen=True)
class Constraint:
    selection: Selection
    displacement_mm: tuple  # None = free DOF
    name: str
    progress: tuple | None = None  # (normalized time, translation multiplier)

@dataclass(frozen=True)
class Load:
    selection: Selection
    force_N: tuple

@dataclass(frozen=True)
class Contact:
    slave: Selection
    master: Selection | tuple[Selection, ...]
    penalty_N_mm3: float
    penetration_limit_mm: float
    discretization: str = "node_to_surface"

class Backend(Protocol):
    def run(self, case: 'AnalysisCase', directory: Path, *, mesh_from=None): ...

@dataclass
class AnalysisCase:
    name: str
    nonlinear: bool = True
    max_increment: float = .1
    timeout_seconds: float | None = None
    parts: dict[str, Part] = field(default_factory=dict, init=False)
    constraints: list[Constraint] = field(default_factory=list, init=False)
    loads: list[Load] = field(default_factory=list, init=False)
    contacts: list[Contact] = field(default_factory=list, init=False)
    observations: dict[str, Selection] = field(default_factory=dict, init=False)

    def __post_init__(self):
        if not re.fullmatch(r'[A-Za-z][A-Za-z0-9_]{0,47}', self.name):
            raise ValueError('Case name must be a short identifier')
        positive(self.max_increment, 'Maximum increment')
        if self.timeout_seconds is not None:
            positive(self.timeout_seconds, 'Timeout')
        if self.max_increment > 1:
            raise ValueError('Maximum increment cannot exceed the unit load interval')

    def add_part(self, name, shape, *, material: Material, mesh_size_mm: float):
        if name in self.parts or not re.fullmatch(r'[A-Za-z][A-Za-z0-9_]{0,47}', name):
            raise ValueError('Part names must be unique short identifiers')
        positive(mesh_size_mm, 'Mesh size')
        if not isinstance(material, Material):
            raise TypeError('Provide an explicit Material, including property assumptions')
        self.parts[name] = Part(name, shape, material, mesh_size_mm)
        return self

    def select(self, part, region=None):
        if part not in self.parts:
            raise ValueError(f'Unknown part: {part}')
        return Selection(part, region if region is not None else Region())

    def constrain(self, part, region=None, *, displacement_mm=(0, 0, 0), name=None, progress=None):
        values = tuple(displacement_mm)
        if len(values) != 3 or all(v is None for v in values) or any(
            v is not None and not math.isfinite(v) for v in values
        ):
            raise ValueError('Constraint needs three finite values or None, at least one constrained')
        if progress is not None:
            progress = tuple(tuple(vector_point) for vector_point in progress)
            if (len(progress)<2 or any(len(p)!=2 or not all(math.isfinite(x) for x in p) for p in progress)
                    or progress[0]!=(0,0) or progress[-1][0]!=1
                    or any(b[0]<=a[0] for a,b in zip(progress,progress[1:]))):
                raise ValueError('Motion progress needs increasing times from (0,0) through time 1')
            if not any(v for v in values if v is not None):
                raise ValueError('Motion progress needs a nonzero translation')
        name = name or f'BC{len(self.constraints)}'
        if not re.fullmatch(r'[A-Za-z][A-Za-z0-9_]{0,47}', name) or any(c.name == name for c in self.constraints):
            raise ValueError('Constraint names must be unique short identifiers')
        self.constraints.append(Constraint(self.select(part, region), values, name, progress))
        return self

    def fix(self, part, region=None, *, name=None):
        return self.constrain(part, region, name=name)

    def prescribe_motion(self, part, region=None, *, displacement_mm, name=None, progress=None):
        """Translation, optionally scaled by a piecewise-linear (time, multiplier) path.

        Time spans 0..1; (0,0),(.5,1),(1,0) loads and returns without resetting
        contact/deformation. None leaves a direction unconstrained.
        """
        return self.constrain(part, region, displacement_mm=displacement_mm, name=name, progress=progress)

    def apply_force(self, part, region, *, force_N):
        """Total force distributed as uniform traction on selected exterior faces."""
        values = vector(force_N)
        if not any(values):
            raise ValueError('Force must be nonzero')
        self.loads.append(Load(self.select(part, region), values))
        return self

    def contact(self, slave, slave_region, master, master_region=None, *, penalty_N_mm3, penetration_limit_mm, discretization="node_to_surface"):
        """Frictionless contact against one part or a union of selected obstacles.

        A tuple of ``case.select(...)`` values combines independently moving
        obstacles into one master surface, without joining their mechanics.
        """
        if not self.nonlinear:
            raise ValueError('Contact requires nonlinear=True')
        if discretization not in ('node_to_surface', 'surface_to_surface', 'mortar'):
            raise ValueError('Unsupported contact discretization')
        if self.contacts and any(c.discretization != discretization for c in self.contacts):
            raise ValueError('CalculiX requires one contact discretization throughout a case')
        if isinstance(master, str):
            masters = (self.select(master, master_region),)
            selected_master = masters[0]
        else:
            if master_region is not None:
                raise ValueError('A master selection union already specifies its regions')
            masters = tuple(master)
            if not masters or any(not isinstance(s, Selection) or s.part not in self.parts for s in masters):
                raise ValueError('Master union needs nonempty selections of existing parts')
            selected_master = masters
        if any(slave == s.part for s in masters):
            raise ValueError('Self-contact is outside this backend scope')
        positive(penalty_N_mm3, 'Contact penalty')
        positive(penetration_limit_mm, 'Penetration limit')
        self.contacts.append(Contact(self.select(slave, slave_region),
            selected_master, penalty_N_mm3, penetration_limit_mm, discretization))
        return self

    def observe(self, part, region, *, name):
        """Report displacement ranges and means on a meaningful feature."""
        if not re.fullmatch(r'[A-Za-z][A-Za-z0-9_]{0,47}', name) or name in self.observations:
            raise ValueError('Observation names must be unique short identifiers')
        self.observations[name] = self.select(part, region)
        return self

    @operation("analysis.case")
    def run(self, directory, *, backend: Backend | None = None, mesh_from=None):
        """Run in a NEW directory; optionally reuse a saved unchanged-part mesh.

        The backend must verify geometry, mesh settings and source identity.
        Changing motion/contact/material settings produces a new solve, not
        reuse of old physical predictions.
        """
        if backend is None:
            from .backends.structural import CalculixBackend
            backend = CalculixBackend()
        options={} if mesh_from is None else dict(mesh_from=Path(mesh_from))
        return backend.run(self, Path(directory), **options)
