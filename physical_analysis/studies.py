"""Read-only metric comparisons and explicit bounded engineering-question studies."""
import math
import hashlib
from dataclasses import dataclass, field, replace
from pathlib import Path
from .case import positive


def compare_results(coarse, refined, *, metrics, relative_tolerance=.05):
    """Compare explicitly chosen metric paths; convergence is not physical validation.

    Example metrics=['max_displacement_mm','peak_motion_force_N.thumb'].
    Both cases must represent the same physical question. This helper cannot
    infer that changed loads, geometry or material were intentional.
    """
    coarse.require_completed(); refined.require_completed()
    positive(relative_tolerance,'Relative tolerance')
    answer={}
    for path in metrics:
        a,b=coarse.metrics,refined.metrics
        for key in path.split('.'):
            a,b=a[key],b[key]
        if not isinstance(a,(int,float)) or not isinstance(b,(int,float)) or not math.isfinite(a+b):
            raise ValueError(f'{path} is not a finite scalar metric')
        change=abs(a-b)/max(abs(b),1e-12)
        answer[path]=dict(coarse=a,refined=b,relative_change=change,passes=change<=relative_tolerance)
    return answer


@dataclass
class QuestionStudy:
    """Opt-in, bounded one-factor refinements; no hidden solver escalation.

    Tolerance is chosen against a stated decision. Each level compares with the
    preceding level, not unrelated runs. 'stable' means the selected quantities
    passed that comparison, not asymptotic convergence or physical validation.
    A failed baseline stops the study before launching refinements.
    """
    question: object
    decision: str
    metrics: tuple[str, ...]
    relative_tolerance: float = .05
    motion_levels: int = 0
    mesh_levels: int = 0
    contact_levels: int = 0
    mesh_factor: float = .7
    contact_factor: float = 2
    absolute_tolerances: dict[str, float] = field(default_factory=dict)

    def plan(self):
        if not self.decision or not self.metrics:
            raise ValueError('Provide the decision and metrics that could change it')
        positive(self.relative_tolerance, 'Comparison tolerance')
        if not 0 < self.mesh_factor < 1 or self.contact_factor <= 1:
            raise ValueError('Refinement must reduce mesh size and increase contact penalty')
        for value in self.absolute_tolerances.values():
            positive(value, 'Absolute metric tolerance')
        controls = [('increment_sensitivity', self.motion_levels, 'max_increment', .5),
                    ('mesh_sensitivity', self.mesh_levels, 'mesh_size_mm', self.mesh_factor),
                    ('contact_parameter_sensitivity', self.contact_levels, 'penalty_N_mm3', self.contact_factor)]
        plan = {}
        for axis, levels, parameter, factor in controls:
            if not isinstance(levels, int) or not 0 <= levels <= 4:
                raise ValueError('Choose zero to four bounded refinement levels')
            if levels and not hasattr(self.question, parameter):
                raise ValueError(f'{parameter} is unsupported by this question')
            plan[axis] = [(f'{axis}_{i}', replace(self.question, **{
                parameter: getattr(self.question, parameter)*factor**i})) for i in range(1, levels+1)]
        return plan

    def run(self, directory=None, *, evidence=None):
        """Run or identity-check retained inputs, returning the baseline AnalysisResult.

        evidence maps 'baseline' and plan labels to existing native/retained run
        directories. No overwrite, no implicit unverified reuse. For historical
        evidence every result keeps its original backend identity. Missing entries
        need a new output directory. Raw native fields are not needed for reuse.
        """
        from .questions import _metric
        plan = self.plan()
        evidence = evidence or {}
        if directory is not None and (Path(directory)/'study_result.json').exists():
            raise FileExistsError('Choose a new study record; existing study evidence is not overwritten')
        def obtain(label, question):
            if label in evidence:
                return question.read_evidence(evidence[label])
            if directory is None:
                raise ValueError(f'Missing {label} evidence and no new run directory provided')
            return question.run(Path(directory)/label, numerical=True)
        baseline = obtain('baseline', self.question)
        summary = dict(decision=self.decision, relative_tolerance=self.relative_tolerance,
            absolute_tolerances=dict(self.absolute_tolerances),
            comparisons={}, comparison_limits={}, acceptance_changed={}, runs={
            'baseline':self._run_record(baseline,self.question)}, stopping_reason={})
        confidence = baseline.metrics['question']['numerical_confidence']
        if not baseline.metrics['question']['numerical_evidence_adequate']:
            for axis, entries in plan.items():
                if entries:
                    confidence[axis] = 'unresolved'
            summary['stopping_reason']['baseline'] = 'Baseline quality rejected; no refinements launched'
        else:
            for axis, entries in plan.items():
                previous = baseline
                for label, question in entries:
                    refined = obtain(label, question)
                    summary['runs'][label] = self._run_record(refined,question)
                    if not refined.metrics['question']['numerical_evidence_adequate']:
                        confidence[axis] = 'unresolved'
                        summary['stopping_reason'][axis] = 'Refinement quality rejected'
                        break
                    changes = {}
                    for metric in self.metrics:
                        a, b = _metric(previous.metrics, metric), _metric(refined.metrics, metric)
                        valid = (isinstance(a, (int, float)) and isinstance(b, (int, float))
                                 and math.isfinite(a) and math.isfinite(b))
                        relative = abs(a-b)/max(abs(b), 1e-12) if valid else None
                        passes = valid and (relative <= self.relative_tolerance or
                            abs(a-b) <= self.absolute_tolerances.get(metric, 0))
                        changes[metric] = dict(previous=a, refined=b, relative_change=relative,
                                               passes=passes if valid else None)
                    summary['comparisons'][label] = changes
                    if any(v['passes'] is None for v in changes.values()):
                        confidence[axis] = 'unresolved'
                        summary['stopping_reason'][axis] = 'Decision metric unavailable'
                        break
                    previous_record = self._run_record(previous,self.question)
                    refined_record = summary['runs'][label]
                    if any(previous_record[key] != refined_record[key] for key in ('backend_identity_sha256','versions')):
                        confidence[axis] = 'unresolved'
                        summary['comparison_limits'][label] = 'Backend/tool identity changed; descriptive comparison only'
                        previous = refined
                        continue
                    acceptance_changed = previous.metrics['question']['design_screen_passes'] != refined.metrics['question']['design_screen_passes']
                    summary['acceptance_changed'][label] = acceptance_changed
                    confidence[axis] = 'stable' if all(v['passes'] for v in changes.values()) and not acceptance_changed else 'unstable'
                    if confidence[axis] == 'stable':
                        summary['stopping_reason'][axis] = 'Selected quantities within decision tolerance'
                        break
                    previous = refined
                if entries and axis not in summary['stopping_reason']:
                    summary['stopping_reason'][axis] = ('Refinement budget exhausted; selected quantities remain sensitive'
                        if confidence[axis] == 'unstable' else 'Refinement budget exhausted without a qualified stable comparison')
        baseline.metrics['question']['study'] = summary
        baseline.provenance['question_study_sha256'] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
        baseline.metrics['question']['selected_metrics_stable'] = (
            all(confidence[axis] == 'stable' for axis, entries in plan.items() if entries)
            if any(plan.values()) else None)
        baseline.metrics['question']['baseline_quality_adequate'] = baseline.metrics['question']['numerical_evidence_adequate']
        if baseline.metrics['question']['selected_metrics_stable'] is False:
            baseline.metrics['question']['numerical_evidence_adequate'] = False
        if directory is not None:
            target = Path(directory)
            target.mkdir(parents=True, exist_ok=True)
            baseline.write(target/'study_result.json')
        return baseline

    @staticmethod
    def _run_record(result,question):
        import json
        p = result.provenance
        return dict(status=result.status,case=result.case,
            input_sha256=p.get('input_sha256'),case_sha256=p.get('case_sha256'),
            backend_identity_sha256=hashlib.sha256(json.dumps(p.get('backend_sha256',{}),sort_keys=True).encode()).hexdigest(),
            versions={key:p.get(key) for key in ('backend','version','gmsh','cadquery','python')},
            requested_travel_per_increment_mm=QuestionStudy._travel(question))

    @staticmethod
    def _travel(question):
        motions = [p.motion for p in question.mating_parts] if hasattr(question,'mating_parts') else ([question.motion] if question.motion else [])
        answer = {}
        for motion in motions:
            distance = math.sqrt(sum((v or 0)**2 for v in motion.displacement_mm))
            points = motion.progress or ((0,0),(1,1))
            slope = max(abs((b[1]-a[1])/(b[0]-a[0])) for a,b in zip(points,points[1:]))
            answer[motion.name] = distance*slope*question.max_increment
        return answer
