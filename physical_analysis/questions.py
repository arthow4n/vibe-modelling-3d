"""Known engineering questions above AnalysisCase. Units: mm, N, MPa.

No feature recognition, inferred loads or inferred printed material properties.
All answers retain the native result/status; metrics['question'] is the compact
decision record. Selections, idealizations and provisional limits remain explicit.
"""
from dataclasses import dataclass, field
import gzip
import hashlib
import json
import math
from pathlib import Path
import tempfile

from .case import AnalysisCase, Region, positive
from .materials import Material
from .results import AnalysisResult
from .screening import rectangular_cantilever


@dataclass(frozen=True)
class Support:
    region: Region
    displacement_mm: tuple = (0, 0, 0)
    name: str = 'root'


@dataclass(frozen=True)
class Motion:
    displacement_mm: tuple
    region: Region = field(default_factory=Region)
    name: str = 'drive'
    progress: tuple | None = None

    @classmethod
    def round_trip(cls, displacement_mm, *, name='drive', region=None):
        """Forward and reverse in the same elastic/contact solve, no state reset."""
        return cls(displacement_mm, region or Region(), name, ((0,0),(.5,1),(1,0)))


@dataclass(frozen=True)
class SurfaceForce:
    region: Region
    force_N: tuple


@dataclass(frozen=True)
class MatingPart:
    """Rigid translation when motion is supplied; otherwise an explicit elastic fixture."""
    name: str
    shape: object
    motion: Motion | None = None
    contact_region: Region = field(default_factory=Region)
    supports: tuple[Support, ...] = ()
    forces: tuple[SurfaceForce, ...] = ()
    material: Material | None = None


@dataclass(frozen=True)
class BeamApproximation:
    """Caller asserts applicability; inappropriate screens still remain visible."""
    length_mm: float
    width_mm: float
    thickness_mm: float
    rationale: str
    tip_force_N: float | None = None
    tip_displacement_mm: float | None = None
    adequate_for_decision: bool = False

    def screen(self, material):
        if not self.rationale:
            raise ValueError('Explain the beam idealization and relation to the CAD/loading')
        return rectangular_cantilever(length_mm=self.length_mm, width_mm=self.width_mm,
            thickness_mm=self.thickness_mm, youngs_modulus_MPa=material.youngs_modulus_MPa,
            tip_force_N=self.tip_force_N, tip_displacement_mm=self.tip_displacement_mm)


@dataclass(frozen=True)
class ManufacturingAssumption:
    """Document orientation/process; optionally review actual local Orca paths.

    Sections are explicit (x_mm, z_mm, (y_min, y_max)) in registered print XYZ.
    A filled section supports a local solid idealization, not material calibration.
    """
    description: str
    gcode: Path | None = None
    sections: tuple = ()
    maximum_uncovered_mm: float = .05

    def review(self):
        if not self.description:
            raise ValueError('Describe material/orientation/process assumptions')
        positive(self.maximum_uncovered_mm, 'Uncovered width limit')
        answer = dict(assumption=self.description, local_solid_paths_established=None)
        if self.sections:
            if self.gcode is None:
                raise ValueError('Actual G-code is required for a local path review')
            from .manufacturing import orca_linear_paths, section_coverage
            paths = list(orca_linear_paths(self.gcode))
            reviews = [section_coverage(paths, x_mm=x, z_mm=z, span_mm=span)
                       for x, z, span in self.sections]
            answer.update(sections=reviews,
                gcode_sha256=hashlib.sha256(Path(self.gcode).read_bytes()).hexdigest(),
                local_solid_paths_established=all(r['uncovered_width_mm'] <= self.maximum_uncovered_mm for r in reviews))
        return answer


@dataclass(kw_only=True)
class StructuralQuestion:
    name: str
    part: object
    material: Material
    supports: tuple[Support, ...]
    forces: tuple[SurfaceForce, ...] = ()
    motion: Motion | None = None
    observations: dict[str, Region] = field(default_factory=dict)
    part_name: str = 'part'
    mesh_size_mm: float = 2
    max_increment: float = .1
    timeout_seconds: float | None = None
    nonlinear: bool = True
    beam: BeamApproximation | None = None
    manufacturing: ManufacturingAssumption | None = None
    acceptance: dict[str, float] = field(default_factory=dict)

    def build_case(self):
        if not self.supports or not (self.forces or self.motion):
            raise ValueError('Provide explicit supports and force or displacement loading')
        return self._fixture_case()

    def _fixture_case(self):
        if not self.supports:
            raise ValueError('Provide explicit supports')
        c = AnalysisCase(self.name, nonlinear=self.nonlinear,
                         max_increment=self.max_increment, timeout_seconds=self.timeout_seconds)
        c.add_part(self.part_name, self.part, material=self.material, mesh_size_mm=self.mesh_size_mm)
        for support in self.supports:
            c.constrain(self.part_name, support.region, displacement_mm=support.displacement_mm, name=support.name)
        for force in self.forces:
            c.apply_force(self.part_name, force.region, force_N=force.force_N)
        if self.motion:
            c.prescribe_motion(self.part_name, self.motion.region, displacement_mm=self.motion.displacement_mm,
                              name=self.motion.name, progress=self.motion.progress)
        for name, region in self.observations.items():
            c.observe(self.part_name, region, name=name)
        return c

    def analytical_screen(self):
        return self.beam.screen(self.material) if self.beam else None

    def run(self, directory, *, numerical=None, mesh_from=None):
        screen = self.analytical_screen()  # always before meshing when supplied
        if numerical is None:
            numerical = not (self.beam and self.beam.adequate_for_decision and screen['small_deflection_applicable'])
        if not numerical:
            if not self.beam or not self.beam.adequate_for_decision or not screen['small_deflection_applicable']:
                raise ValueError('Analytical-only requires an explicitly adequate applicable beam approximation')
            r = AnalysisResult(self.name, 'analytical_screen', assumptions=[screen['assumptions'], self.material.source])
            manufacturing = self.manufacturing.review() if self.manufacturing else None
            material_pass = screen['root_strain'] <= self.material.strain_limit if self.material.strain_limit is not None else None
            design_pass = material_pass if not self.acceptance else None
            if manufacturing and manufacturing['local_solid_paths_established'] is False:
                design_pass = False
            r.metrics.update(analytical_screen=screen)
            r.metrics['question'] = dict(operation_completed=False, solver_completed=False,
                evidence_method='analytical', numerical_evidence_adequate=None,
                physical_limits=_physical_limits(), analytical_screen=screen,
                analytical_evidence_adequate=True, peak_actuation_force_N=abs(screen['force_N']),
                tip_displacement_mm=screen['tip_displacement_mm'],peak_strain=screen['root_strain'],
                peak_strain_location='ideal cantilever root',
                beam_rationale=self.beam.rationale,
                design_screen_passes=design_pass, manufacturing=manufacturing)
            return r
        r = self.build_case().run(directory, mesh_from=mesh_from)
        self._answer(r)
        r.write(Path(directory)/'result.json')
        return r

    def read_evidence(self, directory):
        """Bind retained evidence to this exact intent; never solve or relabel status.

        Historical backend identities are retained and reported. This is historical
        evidence interpretation, not qualification of today's backend. Name/timeout
        are not physical inputs. Geometry/material/selections/motion/settings are.
        """
        directory = Path(directory)
        r = AnalysisResult(**json.loads((directory/'result.json').read_text()))
        if r.provenance.get('backend') != 'CalculiX':
            raise ValueError('Question evidence must use the qualified CalculiX route; keep experimental backends in lower-level investigations')
        raw = (directory/'case.json').read_bytes()
        if hashlib.sha256(raw).hexdigest() != r.provenance.get('case_sha256'):
            raise ValueError('Retained case identity differs from result provenance')
        saved = json.loads(raw)
        with tempfile.TemporaryDirectory(prefix='question_identity_') as temp:
            from .backends.structural import CalculixBackend
            current = CalculixBackend().prepare_request(self.build_case(), Path(temp))
        if _intent(current) != _intent(saved):
            raise ValueError('Retained evidence geometry, physical intent or numerical settings differ')
        input_path = directory/'analysis.inp'
        compressed = directory/'analysis.inp.gz'
        if input_path.exists() or compressed.exists():
            data = input_path.read_bytes() if input_path.exists() else gzip.decompress(compressed.read_bytes())
            if hashlib.sha256(data).hexdigest() != r.provenance.get('input_sha256'):
                raise ValueError('Retained solver input identity differs from result provenance')
        else:
            raise ValueError('Retained solver input is required for evidence reuse')
        self._answer(r)
        r.metrics['question']['evidence_method'] = 'retained_numerical'
        r.metrics['question']['historical_backend_identity'] = r.provenance.get('backend_sha256')
        return r

    def _answer(self, r):
        r.provenance['question_interpreter_sha256'] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
        m = r.metrics
        balance = m.get('max_force_balance_relative')
        balance_source = 'native_summary'
        if balance is None and r.history and all('reactions_N' in h for h in r.history):
            # Older retained results contain reactions but no per-frame balance.
            # Applied forces share the case's proportional ramp; free DOFs were
            # already excluded by the native extractor. Missing fields stay missing.
            balances = []
            forces = self.forces + tuple(f for p in getattr(self, 'mating_parts', ()) for f in p.forces)
            for frame in r.history:
                reactions = list(frame['reactions_N'].values())
                applied = [frame['load_fraction']*sum(f.force_N[i] for f in forces) for i in range(3)]
                residual = math.sqrt(sum((sum(v[i] for v in reactions)+applied[i])**2 for i in range(3)))
                norm = lambda values: math.sqrt(sum(v*v for v in values))
                balances.append(residual/max(norm(applied), sum(norm(v) for v in reactions), 1))
            balance = max(balances)
            balance_source = 'computed_from_retained_reactions'
        balance_ok = balance is not None and math.isfinite(balance) and balance <= .01
        solver_completed = bool(r.history and abs(r.history[-1]['load_fraction']-1) <= 1e-6)
        adequate = r.completed and solver_completed and balance_ok
        strain = m.get('max_strain_by_part', {}).get(self.part_name)
        adequate = adequate and strain is not None and math.isfinite(strain)
        if self.motion:
            force = m.get('peak_motion_force_N', {}).get(self.motion.name)
            adequate = adequate and force is not None and math.isfinite(force)
        strain_pass = None if strain is None or self.material.strain_limit is None else strain <= self.material.strain_limit
        screens = {}
        for key, limit in self.acceptance.items():
            positive(limit, 'Acceptance limit')
            value = _metric(m, key)
            screens[key] = None if value is None else value <= limit
        screen = self.analytical_screen()
        manufacturing = self.manufacturing.review() if self.manufacturing else None
        if manufacturing and manufacturing['local_solid_paths_established'] is False:
            screens['local_solid_paths'] = False
        all_screens = [strain_pass, *screens.values()]
        r.metrics['question'] = dict(operation_completed=r.completed,
            solver_completed=solver_completed, evidence_method='numerical',
            numerical_evidence_adequate=bool(adequate),
            peak_actuation_force_N=m.get('peak_motion_force_N', {}).get(self.motion.name) if self.motion else None,
            peak_strain=strain, peak_strain_location_mm=(m.get('max_strain_element_centroid_mm')
                if m.get('max_strain_part') == self.part_name else None),
            strain_location_kind='undeformed element centroid of peak integration point',
            peak_von_mises_MPa=m.get('max_von_mises_MPa'),
            peak_stress_location_mm=m.get('max_stress_element_centroid_mm'),
            deformation_mm=m.get('observations'), max_displacement_mm=m.get('max_displacement_mm'),
            force_balance_ok=balance_ok, max_force_balance_relative=balance,
            force_balance_source=balance_source, strain_screen_passes=strain_pass, acceptance=screens,
            design_screen_passes=(False if any(x is False for x in all_screens) else
                True if all_screens and all(x is True for x in all_screens) else None) if adequate else None,
            design_screen_scope='Only the supplied provisional strain and acceptance quantities',
            analytical_screen=screen, beam_rationale=self.beam.rationale if self.beam else None,
            analytical_numerical_comparison=None,
            manufacturing=manufacturing, physical_limits=_physical_limits(),
            numerical_confidence={key: 'not_run' for key in ('increment_sensitivity', 'mesh_sensitivity', 'contact_parameter_sensitivity')})
        if screen and adequate:
            prediction, measured = (abs(screen['force_N']), r.metrics['question']['peak_actuation_force_N']) if self.motion else (abs(screen['tip_displacement_mm']), m.get('max_displacement_mm'))
            r.metrics['question']['analytical_numerical_comparison'] = dict(
                prediction=prediction, numerical=measured,
                ratio=measured/prediction if measured is not None and prediction else None,
                scope='Ideal end response versus stated CAD fixture; not a calibration or equality requirement')
        return r


@dataclass(kw_only=True)
class FlexureQuestion(StructuralQuestion):
    """Displacement or force-driven flexible feature, with optional cheap beam screen."""


@dataclass(kw_only=True)
class ContactQuestion(StructuralQuestion):
    """Supported deformable part loaded against rigid or supported elastic mates.

    Contact engagement and penetration qualify the structural answer. This does
    not establish passage, cyclic recovery, friction or bolt preload.
    """
    contact_region: Region
    mating_parts: tuple[MatingPart, ...]
    penalty_N_mm3: float
    penetration_limit_mm: float = .02
    discretization: str = 'surface_to_surface'
    contact_expected: bool = True
    combine_mating_surfaces: bool = True

    def run(self, directory, *, numerical=None, mesh_from=None):
        if numerical is False:
            raise ValueError('Contact requires numerical contact evidence')
        return super().run(directory, numerical=True, mesh_from=mesh_from)

    def build_case(self):
        if not isinstance(self.contact_expected, bool):
            raise ValueError('contact_expected must be an explicit boolean')
        if not (self.forces or self.motion or any(
                bool(p.forces) or (p.motion is not None and any(v for v in p.motion.displacement_mm if v is not None))
                or any(any(v for v in s.displacement_mm if v is not None) for s in p.supports)
                for p in self.mating_parts)):
            raise ValueError('Provide explicit force or motion loading')
        c = self._fixture_case()
        if not self.mating_parts:
            raise ValueError('Provide at least one mating part')
        for part in self.mating_parts:
            if part.motion is not None:
                if part.supports or part.forces or part.material is not None:
                    raise ValueError('Choose rigid motion or a supported deformable mate fixture')
                if any(v is None for v in part.motion.displacement_mm) or part.motion.region != Region():
                    raise ValueError('A rigid mating part needs all three translation components')
                c.add_part(part.name, part.shape, material=self.material, mesh_size_mm=self.mesh_size_mm)
                c.prescribe_motion(part.name, part.motion.region, displacement_mm=part.motion.displacement_mm,
                                  name=part.motion.name, progress=part.motion.progress)
            else:
                if not part.supports:
                    raise ValueError('A deformable mating part requires explicit supports')
                c.add_part(part.name, part.shape, material=part.material or self.material, mesh_size_mm=self.mesh_size_mm)
                for support in part.supports:
                    c.constrain(part.name, support.region, displacement_mm=support.displacement_mm,
                                name=f'{part.name}_{support.name}')
                for force in part.forces:
                    c.apply_force(part.name, force.region, force_N=force.force_N)
        if self.combine_mating_surfaces and len(self.mating_parts)>1:
            c.contact(self.part_name, self.contact_region,
                      tuple(c.select(p.name,p.contact_region) for p in self.mating_parts),
                      penalty_N_mm3=self.penalty_N_mm3, penetration_limit_mm=self.penetration_limit_mm,
                      discretization=self.discretization)
        else:
            for part in self.mating_parts:
                c.contact(self.part_name, self.contact_region, part.name, part.contact_region,
                      penalty_N_mm3=self.penalty_N_mm3, penetration_limit_mm=self.penetration_limit_mm,
                      discretization=self.discretization)
        return c

    def _answer(self, r):
        if not isinstance(self.contact_expected, bool):
            raise ValueError('contact_expected must be an explicit boolean')
        super()._answer(r)
        q, m = r.metrics['question'], r.metrics
        positive(self.penetration_limit_mm, 'Penetration limit')
        penetration = m.get('max_penetration_mm')
        penetration_ok = penetration is not None and math.isfinite(penetration) and 0 <= penetration <= self.penetration_limit_mm
        detected = m.get('contact_detected')
        engaged_ok = detected is self.contact_expected
        mate_strains = {p.name: m.get('max_strain_by_part', {}).get(p.name)
                        for p in self.mating_parts if p.motion is None}
        mate_quality = all(v is not None and math.isfinite(v) for v in mate_strains.values())
        mate_screens = {p.name: (None if mate_strains[p.name] is None or (p.material or self.material).strain_limit is None
                                else mate_strains[p.name] <= (p.material or self.material).strain_limit)
                        for p in self.mating_parts if p.motion is None}
        quality = q['numerical_evidence_adequate'] and penetration_ok and engaged_ok and mate_quality
        q.update(numerical_evidence_adequate=bool(quality), contact_quality_ok=bool(quality),
                 contact_engaged=detected, contact_expected=self.contact_expected,
                 penetration_ok=penetration_ok, max_penetration_mm=penetration,
                 contact_scope='Explicit rigid translations or supported deformable mates; sampled frictionless contact')
        if mate_strains:
            q.update(mating_part_strain=mate_strains, mating_part_strain_screens=mate_screens)
            if any(v is False for v in mate_screens.values()):
                q['design_screen_passes'] = False
            elif any(v is None for v in mate_screens.values()) and q['design_screen_passes'] is True:
                q['design_screen_passes'] = None
        q['analytical_numerical_comparison'] = None
        if not quality:
            q['design_screen_passes'] = None
        return r


@dataclass(kw_only=True)
class SnapFitQuestion(ContactQuestion):
    """Explicit contact operation; recovery need not imply reverse driver motion.

    Stationary mates are already at their initial pose. A one-way driver may
    remain at its final pose only with explicit final contact-free recovery;
    this interprets supplied evidence, not product value or printed behavior.
    """
    combine_mating_surfaces: bool = False  # preserve historical case/input identity
    contact_free_at: tuple[float, ...] = ()
    checkpoint_tolerance: float = .01
    return_observation: str | None = None
    require_driver_return: bool = True
    return_tolerance_mm: float = 1e-4
    displacement_limits_mm: dict[str, tuple] = field(default_factory=dict)

    def run(self, directory, *, numerical=None, mesh_from=None):
        if numerical is False:
            raise ValueError('A snap passage question requires contact evidence; a beam screen alone cannot answer it')
        return super().run(directory,numerical=True,mesh_from=mesh_from)

    def build_case(self):
        # Base setup supplies root/observations; mating contact supplies loading.
        if self.motion or self.forces:
            raise ValueError('Snap loading belongs on explicit mating-part motions')
        if not self.contact_expected:
            raise ValueError('A snap passage requires expected contact engagement')
        if any(p.motion is None for p in self.mating_parts):
            raise ValueError('Snap passage currently requires explicit rigid mating-part motions')
        return super().build_case()

    def _answer(self, r):
        super()._answer(r)
        q, m, h = r.metrics['question'], r.metrics, r.history
        q['analytical_numerical_comparison'] = None  # beam bending is not contact actuation
        positive(self.penetration_limit_mm, 'Penetration limit')
        positive(self.return_tolerance_mm, 'Return tolerance')
        positive(self.checkpoint_tolerance, 'Checkpoint time tolerance')
        penetration = m.get('max_penetration_mm')
        penetration_ok = penetration is not None and math.isfinite(penetration) and penetration <= self.penetration_limit_mm
        engaged = m.get('contact_detected') is True
        checkpoints = []
        for time in self.contact_free_at:
            if not 0 < time <= 1:
                raise ValueError('Contact-free checkpoints must be in (0,1]')
            frame = min(h, key=lambda f: abs(f['load_fraction']-time)) if h else None
            checkpoints.append(bool(frame and abs(frame['load_fraction']-time) <= self.checkpoint_tolerance
                                    and frame['max_contact_pressure_MPa'] <= 1e-8))
        clearance = {}
        for name, limits in self.displacement_limits_mm.items():
            if len(limits) != 3:
                raise ValueError('Displacement limits require three (lower, upper) pairs')
            rows = [f.get('observations', {}).get(name) for f in h]
            clearance[name] = bool(rows and all(row and all(
                lo <= row['min_mm'][axis] <= row['max_mm'][axis] <= hi
                for axis, (lo, hi) in enumerate(limits)) for row in rows))
        error = None
        return_requested = self.return_observation is not None
        if return_requested:
            returns = all(all(v == 0 for v in p.motion.displacement_mm) or
                          (p.motion.progress is not None and p.motion.progress[-1][1] == 0)
                          for p in self.mating_parts)
            if self.require_driver_return and not returns:
                raise ValueError('Elastic return requires all drivers to return to their initial pose')
            if not self.require_driver_return and 1 not in self.contact_free_at:
                raise ValueError('Unloaded return with a different final driver pose requires a final contact-free checkpoint at 1')
            row = h[-1].get('observations', {}).get(self.return_observation) if h else None
            if row:
                error = max(abs(v) for key in ('min_mm', 'max_mm') for v in row[key])
        quality = q['numerical_evidence_adequate'] and penetration_ok and engaged
        return_ok = error is not None and error <= self.return_tolerance_mm
        if return_requested and not self.require_driver_return:
            final_free = any(t == 1 and ok for t, ok in zip(self.contact_free_at, checkpoints))
            return_ok = return_ok and final_free
        passage = bool(quality and checkpoints and all(checkpoints) and clearance and all(clearance.values())
                       and (not return_requested or return_ok))
        forces = m.get('peak_motion_force_N', {})
        directional_forces = {}
        for part in self.mating_parts:
            motion = part.motion
            points = motion.progress or ((0,0),(1,1))
            groups = {'forward': [], 'reverse': []}
            for frame in h:
                a,b = next(((a,b) for a,b in zip(points,points[1:])
                            if frame['load_fraction'] <= b[0]+1e-9), (points[-2],points[-1]))
                value = frame.get('motion_force_N',{}).get(motion.name)
                if value is not None and b[1] != a[1]:
                    groups['forward' if b[1] > a[1] else 'reverse'].append(abs(value))
            directional_forces[motion.name] = {name:max(values) if values else None for name,values in groups.items()}
        q.update(numerical_evidence_adequate=passage, contact_quality_ok=bool(quality), contact_engaged=engaged,
            contact_passage_established=passage,
            passage_scope='Sampled native contact, caller-defined free checkpoints and displacement envelopes; no continuous no-intersection proof',
            peak_actuation_force_N=max(forces.values()) if forces else None,
            peak_actuation_force_by_driver_N=forces,
            peak_directional_actuation_force_N=directional_forces,
            elastic_return_error_mm=error, numerical_elastic_return_ok=return_ok if return_requested else None,
            elastic_return_driver_policy=('initial_pose' if self.require_driver_return else 'final_contact_free_pose') if return_requested else None,
            max_penetration_mm=penetration, penetration_ok=penetration_ok,
            contact_free_checkpoints_ok=checkpoints, displacement_envelope_ok=clearance)
        if not quality or not passage:
            q['design_screen_passes'] = None
        return r


def _physical_limits():
    return dict(material_calibrated=False, friction_modelled=False,
                printed_recovery_established=False, physically_validated=False)


def _metric(metrics, path):
    value = metrics
    for key in path.split('.'):
        if not isinstance(value, dict) or key not in value:
            return None
        value = value[key]
    return value


def _intent(request):
    """Canonical JSON normalization (tuple/list), excluding nonphysical metadata."""
    answer = json.loads(json.dumps({k: request[k] for k in (
        'nonlinear', 'max_increment', 'parts', 'constraints', 'loads', 'contacts', 'observations')}))
    for constraint in answer['constraints']:
        constraint.setdefault('progress', None)  # legacy proportional ramp
    return answer
