"""Explicit pair intent and sampled rigid movement; CadQuery/OpenCascade kernels."""
from dataclasses import asdict, dataclass
import math
from OCP.BRepExtrema import BRepExtrema_DistShapeShape
from .configuration import geometry
import cadquery as cq


@dataclass(frozen=True)
class PairRequirement:
    intent: str
    max_overlap_mm3: float | None = None
    min_overlap_mm3: float | None = None
    min_gap_mm: float | None = None
    max_gap_mm: float | None = None

    def __post_init__(self):
        if not self.intent or not any(v is not None for v in (
                self.max_overlap_mm3, self.min_overlap_mm3, self.min_gap_mm, self.max_gap_mm)):
            raise ValueError('State intent and at least one numerical criterion')
        for key, value in asdict(self).items():
            if key != 'intent' and value is not None and (not math.isfinite(value) or value < 0):
                raise ValueError(f'{key} must be finite and nonnegative')
        for lo, hi in ((self.min_overlap_mm3, self.max_overlap_mm3), (self.min_gap_mm, self.max_gap_mm)):
            if lo is not None and hi is not None and lo > hi:
                raise ValueError('Contradictory criterion interval')
        if self.min_overlap_mm3 is not None and self.min_overlap_mm3 > 0 and self.min_gap_mm is not None and self.min_gap_mm > 0:
            raise ValueError('Positive overlap and positive separation cannot both be required')


@dataclass(frozen=True)
class PairResult:
    first: str
    second: str
    configuration: str | None
    requirement: PairRequirement
    calculation_completed: bool
    status: str
    overlap_mm3: float | None = None
    gap_mm: float | None = None
    closest_points_mm: tuple | None = None
    error: str | None = None
    limits: str = ('Kernel measurements, not calibrated accuracy or physical validation. '
                   'Distance is unsigned; zero can mean touching or overlap. '
                   'Closest points are distance witnesses, not contact patches or penetration depths.')

    def to_dict(self):
        return asdict(self)

    def require_passed(self):
        if self.status != 'passed':
            raise AssertionError(self.to_dict())
        return self


def check_pair(first_shape, second_shape, requirement, *, first='first', second='second', configuration=None):
    """Measure only quantities needed by intent, with no invented default tolerance.

    Declaration errors raise. Kernel/numerical failures return inconclusive.
    Overlap criteria require solid-bearing geometry; gap-only checks allow faces.
    """
    if not isinstance(requirement, PairRequirement):
        raise TypeError('Expected PairRequirement')
    a, b = geometry(first_shape), geometry(second_shape)
    need_volume = requirement.max_overlap_mm3 is not None or requirement.min_overlap_mm3 is not None
    need_gap = requirement.min_gap_mm is not None or requirement.max_gap_mm is not None
    if need_volume and (not a.Solids() or not b.Solids()):
        raise ValueError('Overlap-volume criteria require solids on both sides')
    context = dict(first=first, second=second, configuration=configuration, requirement=requirement)
    try:
        if a.isNull() or b.isNull() or not a.isValid() or not b.isValid():
            raise ValueError('Invalid input geometry')
        volume, gap, witness = None, None, None
        if need_volume:
            common = a.intersect(b)
            if not common.isValid():
                raise ValueError('Invalid intersection geometry')
            volume = common.Volume()
            if not math.isfinite(volume) or volume < 0:
                raise ValueError('Invalid intersection volume')
        if need_gap:
            distance = BRepExtrema_DistShapeShape(a.wrapped, b.wrapped)
            if not distance.IsDone() or distance.NbSolution() < 1:
                raise ValueError('Kernel distance calculation did not complete')
            gap = distance.Value()
            if not math.isfinite(gap) or gap < 0:
                raise ValueError('Invalid unsigned distance')
            witness = tuple(tuple(getattr(p, axis)() for axis in ('X', 'Y', 'Z')) for p in
                            (distance.PointOnShape1(1), distance.PointOnShape2(1)))
        passed = all(value is None or measured <= value for measured, value in (
            (volume, requirement.max_overlap_mm3), (gap, requirement.max_gap_mm))) and all(
            value is None or measured >= value for measured, value in (
                (volume, requirement.min_overlap_mm3), (gap, requirement.min_gap_mm)))
        return PairResult(**context, calculation_completed=True, status='passed' if passed else 'failed',
                          overlap_mm3=volume, gap_mm=gap, closest_points_mm=witness)
    except Exception as exc:
        return PairResult(**context, calculation_completed=False, status='inconclusive',
                          error=f'{type(exc).__name__}: {exc}')


@dataclass(frozen=True)
class MotionResult:
    configuration: str
    moving: str
    obstacle: str
    parameter: str
    units: str
    samples: tuple
    results: tuple[PairResult, ...]
    poses: tuple
    limits: str = ('Only the supplied poses were checked. Sampled success is not continuous-path proof '
                   'or a global clearance minimum. Rigid movement does not qualify elastic insertion, '
                   'force, friction, recovery, wear or practical access.')

    @property
    def calculation_completed(self):
        return all(r.calculation_completed for r in self.results)

    @property
    def status(self):
        if any(r.status == 'failed' for r in self.results):
            return 'failed'
        return 'passed' if self.calculation_completed else 'inconclusive'

    def to_dict(self):
        gaps = [(r.gap_mm, t) for t, r in zip(self.samples, self.results) if r.gap_mm is not None]
        overlaps = [(r.overlap_mm3, t) for t, r in zip(self.samples, self.results) if r.overlap_mm3 is not None]
        return dict(configuration=self.configuration, moving=self.moving, obstacle=self.obstacle,
            parameter=self.parameter, units=self.units, samples=self.samples, poses=self.poses,
            calculation_completed=self.calculation_completed, status=self.status,
            first_failure=next((dict(parameter=t, result=r.to_dict()) for t, r in zip(self.samples, self.results)
                                if r.status != 'passed'), None),
            minimum_sampled_gap=None if not gaps else dict(zip(('mm', 'parameter'), min(gaps))),
            maximum_sampled_overlap=None if not overlaps else dict(zip(('mm3', 'parameter'), max(overlaps))),
            results=[r.to_dict() for r in self.results], limits=self.limits)

    def require_passed(self):
        if self.status != 'passed':
            raise AssertionError(self.to_dict())
        return self


def sample_motion(configuration, moving, obstacle, requirement, *, samples, transform, parameter, units):
    """Apply a caller-supplied WORLD-frame rigid delta to the snapshot's moving part.

    transform(t) -> cq.Location; rotation axes/origins and translation directions
    belong in that function. Ordered finite samples are explicit, never inferred.
    The obstacle and snapshot remain unchanged. No constraint solves per sample.
    """
    samples = tuple(samples)
    if not samples or any(not math.isfinite(t) for t in samples) or any(a >= b for a, b in zip(samples, samples[1:])):
        raise ValueError('Samples must be a nonempty strictly increasing finite sequence')
    if not parameter or not units:
        raise ValueError('Movement parameter name and units required')
    if moving == obstacle:
        raise ValueError('Movement requires distinct instances')
    a, b = configuration.shape(moving), configuration.shape(obstacle)
    results, poses = [], []
    for t in samples:
        delta = transform(t)
        if not isinstance(delta, cq.Location):
            raise TypeError('transform must return cq.Location')
        poses.append((delta * configuration.location(moving)).toTuple())
        results.append(check_pair(a.moved(delta), b, requirement, first=moving, second=obstacle,
                                  configuration=configuration.name))
    return MotionResult(configuration.name, moving, obstacle, parameter, units, samples, tuple(results), tuple(poses))
