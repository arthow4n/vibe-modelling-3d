"""Small declared-intent reports above existing engineering operations.

No discovery, execution scheduling, identity/cache, geometry or promotion gates.
"""
from dataclasses import asdict, dataclass
from enum import StrEnum
import argparse
import json
from pathlib import Path
from typing import Callable, Iterable


class Status(StrEnum):
    PASS = 'PASS'
    FAIL = 'FAIL'
    UNKNOWN = 'UNKNOWN'
    INCONCLUSIVE = 'INCONCLUSIVE'


@dataclass(frozen=True)
class UserSource:
    reference: str
    statement: str  # explicit instruction/acceptance, not an agent's rationale

    def __post_init__(self):
        if not self.reference or not self.statement:
            raise ValueError('User provenance needs a reference and established instruction')


@dataclass(frozen=True)
class Question:
    id: str
    criterion: str
    mode: str = 'CAD'


@dataclass(frozen=True)
class UserRequirement:
    id: str
    text: str
    source: UserSource
    questions: tuple[Question, ...]

    def __post_init__(self):
        if not isinstance(self.source, UserSource):
            raise TypeError('UserRequirement needs explicit UserSource; decisions are not provenance')


@dataclass(frozen=True)
class DerivedRequirement:
    id: str
    text: str
    parents: tuple[str, ...]
    rationale: str
    questions: tuple[Question, ...]


@dataclass(frozen=True)
class DesignDecision:
    id: str
    text: str
    reference: str


@dataclass(frozen=True)
class Hypothesis:
    id: str
    text: str
    reference: str


@dataclass(frozen=True)
class Directive:
    id: str
    text: str
    source: UserSource


@dataclass(frozen=True)
class Evidence:
    id: str
    targets: tuple[tuple[str, str], ...]  # (requirement ID, question ID)
    status: Status
    summary: str
    reference: str
    scope: dict[str, str]


@dataclass(frozen=True)
class Check:
    id: str
    targets: tuple[tuple[str, str], ...]
    run: Callable[[], Iterable[Evidence]]


class CalculationInconclusive(Exception):
    """An attempted calculation cannot answer its declared criterion."""


def assertion_check(id, targets, run, reference, scope):
    """Adapt a consequential existing assertion group, without copying it.

    Invalid calculations must raise CalculationInconclusive. Assembly's existing
    require_passed dictionaries preserve failed versus inconclusive status.
    Unexpected programming exceptions are deliberately NOT swallowed.
    """
    def evaluate():
        try:
            run()
            status, message = Status.PASS, 'Existing assertion group passed; see linked criteria/limits'
        except CalculationInconclusive as exc:
            status, message = Status.INCONCLUSIVE, str(exc)
        except AssertionError as exc:
            native = exc.args[0] if exc.args else None
            status = (Status.INCONCLUSIVE if isinstance(native, dict) and
                      native.get('status') == 'inconclusive' else Status.FAIL)
            # Native failed motion dictionaries can be enormous. Keep the native
            # operation status/intent/error, not a second sampled trace.
            message = (str({k: native[k] for k in ('status', 'requirement', 'first', 'second', 'configuration',
                            'overlap_mm3', 'gap_mm', 'parameter', 'units', 'first_failure', 'error') if k in native})
                       if isinstance(native, dict) else str(exc))
        return (Evidence(id, targets, status, message, reference, scope),)
    return Check(id, targets, evaluate)


def engineering_evidence(id, targets, answer, reference, scope):
    """Consume PairResult/MotionResult without require_passed or huge traces."""
    statuses = {'passed': Status.PASS, 'failed': Status.FAIL, 'inconclusive': Status.INCONCLUSIVE}
    if answer.status not in statuses:
        raise ValueError(f'Unsupported engineering status: {answer.status}')
    return Evidence(id, targets, statuses[answer.status],
                    f'{answer.status}; sampled/pair evidence only', reference, scope)


def protect_user_requirements(previous, current, *, changes=None):
    """Review-time comparison: IDs, provenance and criteria cannot silently drift.

    Explicit later user instructions authorize supersession/removal. Wording may
    improve freely. This is an audit helper, not security against editing Python.
    """
    changes = changes or {}
    now = {r.id: r for r in current}
    for old in previous:
        if not isinstance(old, UserRequirement):
            continue
        new = now.get(old.id)
        if (not isinstance(new, UserRequirement) or
                new.source != old.source or new.questions != old.questions):
            if not isinstance(changes.get(old.id), UserSource):
                raise ValueError(f'{old.id}: user instruction required to change/remove/reclassify intent')


@dataclass(frozen=True)
class Plan:
    variant: str
    requirements: tuple[UserRequirement | DerivedRequirement, ...]
    scope: dict[str, str]
    checks: tuple[Check, ...] = ()
    retained: tuple[Evidence, ...] = ()
    non_applicable: dict[str, str] | None = None
    decisions: tuple[DesignDecision, ...] = ()
    hypotheses: tuple[Hypothesis, ...] = ()
    directives: tuple[Directive, ...] = ()

    def validate(self):
        if not self.variant or not self.scope:
            raise ValueError('Candidate needs an explicit variant and scope')
        for group,kind in ((self.decisions,DesignDecision),(self.hypotheses,Hypothesis),(self.directives,Directive)):
            if any(type(x) is not kind for x in group):
                raise TypeError(f'Expected distinct {kind.__name__} records')
        if any(not isinstance(d.source,UserSource) for d in self.directives):
            raise TypeError('Directive needs explicit user provenance')
        records = (*self.requirements, *self.decisions, *self.hypotheses, *self.directives)
        ids = [r.id for r in records]
        if any(not r.id or not r.text for r in records):
            raise ValueError('Record IDs and wording must be nonempty')
        if len(set(ids)) != len(ids):
            raise ValueError('IDs must be unique; a decision cannot also be a requirement')
        reqs = {r.id: r for r in self.requirements}
        for r in self.requirements:
            if type(r) not in (UserRequirement, DerivedRequirement):
                raise TypeError('Requirements must carry user or derived provenance')
            if (not r.questions or any(not q.id or not q.criterion or not q.mode for q in r.questions) or
                    len({q.id for q in r.questions}) != len(r.questions)):
                raise ValueError(f'{r.id}: nonempty unique questions required')
            if isinstance(r, DerivedRequirement):
                if not r.parents or r.id in r.parents or not r.rationale or any(p not in {*ids, *(e.id for e in self.retained)} for p in r.parents):
                    raise ValueError(f'{r.id}: derivation needs declared parents and rationale')
                if any(isinstance(x, (DesignDecision, Hypothesis, Directive)) and x.id in r.parents for x in records):
                    raise ValueError('A decision, hypothesis or directive is not a requirement/evidence parent')
        for rid, reason in (self.non_applicable or {}).items():
            if rid not in reqs or not reason:
                raise ValueError('Non-applicability needs a declared requirement and a reason')
        check_ids = [c.id for c in self.checks]
        if any(not id for id in check_ids) or len(set(check_ids)) != len(check_ids):
            raise ValueError('Duplicate check IDs')
        for item in (*self.checks, *self.retained):
            self.validate_targets(item.targets)
        for e in self.retained:
            self.validate_evidence(e)

    def validate_targets(self, targets):
        known = {(r.id, q.id) for r in self.requirements for q in r.questions}
        if not targets or any(t not in known for t in targets):
            raise ValueError(f'Undeclared/empty evidence targets: {targets}')

    def validate_evidence(self, e):
        if not e.id or not isinstance(e.status, Status) or not e.summary or not e.reference or not e.scope:
            raise ValueError('Evidence needs typed status, summary, reference and explicit scope')
        self.validate_targets(e.targets)

    def evaluate(self, selected=None):
        self.validate()
        if selected is not None and set(selected) - {c.id for c in self.checks}:
            raise ValueError('Unknown focused check ID')
        evidence = list(self.retained)
        for c in self.checks:
            if selected is not None and c.id not in selected:
                continue
            produced = c.run()
            for e in produced:
                self.validate_evidence(e)
                if any(t not in c.targets for t in e.targets):
                    raise ValueError(f'{c.id}: returned undeclared targets')
                evidence.append(e)
        if len({e.id for e in evidence}) != len(evidence):
            raise ValueError('Duplicate evidence IDs')
        rows = []
        for r in self.requirements:
            reason = (self.non_applicable or {}).get(r.id)
            questions = []
            for q in r.questions:
                target = (r.id, q.id)
                related = [e for e in evidence if target in e.targets]
                applicable = [e for e in related if all(k in self.scope and self.scope[k] == v for k, v in e.scope.items())]
                statuses = {e.status for e in applicable}
                # Each question is one obligation; multiple evidence sources
                # coexist. Contradiction/failure cannot be overwritten by PASS.
                status = next((s for s in (Status.FAIL, Status.INCONCLUSIVE, Status.UNKNOWN, Status.PASS)
                               if s in statuses), Status.UNKNOWN)
                questions.append(dict(id=q.id, criterion=q.criterion, mode=q.mode,
                    status=None if reason else status.value,
                    coverage=('non_applicable' if reason else 'evidence' if applicable else 'uncovered'),
                    strategies=[c.id for c in self.checks if target in c.targets],
                    evidence=[e.id for e in applicable],
                    out_of_scope=[e.id for e in related if e not in applicable]))
            rows.append(dict(id=r.id, text=r.text,
                kind='user' if isinstance(r, UserRequirement) else 'derived',
                provenance=asdict(r.source) if isinstance(r, UserRequirement) else
                    dict(parents=r.parents, rationale=r.rationale),
                non_applicable=reason, questions=questions))
        return dict(variant=self.variant, scope=self.scope, focused=selected is not None,
                    requirements=rows, evidence=[asdict(e) for e in evidence],
                    decisions=[asdict(x) for x in self.decisions],
                    hypotheses=[asdict(x) for x in self.hypotheses],
                    directives=[asdict(x) for x in self.directives])


def human_report(report):
    lines = [f"Verification: {report['variant']}" + (' (focused; omitted checks remain uncovered)' if report['focused'] else '')]
    for kind, title in (('user', 'USER REQUIREMENTS'), ('derived', 'DERIVED REQUIREMENTS')):
        lines.append(title)
        for r in report['requirements']:
            if r['kind'] != kind:
                continue
            origin = (r['provenance']['reference'] if kind == 'user' else
                      ', '.join(r['provenance']['parents']))
            lines.append(f"  {r['id']}: {r['text']} ({'source' if kind == 'user' else 'derived from'}: {origin})")
            if r['non_applicable']:
                lines.append(f"  N/A {r['id']}: {r['non_applicable']}")
            else:
                for q in r['questions']:
                    lines.append(f"  {q['status']} {r['id']}/{q['id']} [{q['mode']}, {q['coverage']}]: {q['criterion']}")
                    if q['out_of_scope']:
                        lines.append('    Out of scope: '+', '.join(q['out_of_scope']))
    for key, title, tag in (('decisions', 'CURRENT DESIGN DECISIONS', 'INFO'),
                             ('hypotheses', 'ASSUMPTIONS / HYPOTHESES', 'OPEN'),
                             ('directives', 'PROJECT DIRECTIVES / STATE', 'INFO')):
        lines.append(title)
        lines.extend(f"  {tag} {x['id']}: {x['text']}" for x in report[key])
    lines.append('EVIDENCE (including retained physical/history; never a new physical trial)')
    used={id for r in report['requirements'] if not r['non_applicable']
          for q in r['questions'] for id in q['evidence']}
    lines.extend(f"  {'' if e['id'] in used else 'OUT OF SCOPE '}{e['status']} {e['id']}: "
                 f"{e['summary']} ({e['reference']}; scope={e['scope']})" for e in report['evidence'])
    return '\n'.join(lines)


def cli(make_plan, variants):
    parser = argparse.ArgumentParser(description='Declared product verification; no global product score')
    parser.add_argument('--variant', choices=variants, default=variants[0])
    parser.add_argument('--check', action='append', help='Focus a check ID; all requirements remain visible')
    parser.add_argument('--json', action='store_true', help='Print machine-readable summary')
    parser.add_argument('--output', type=Path, help='Optional summary file; no underlying traces copied')
    args = parser.parse_args()
    report = make_plan(args.variant).evaluate(args.check)
    encoded = json.dumps(report, indent=2)+'\n'
    if args.output:
        args.output.write_text(encoded)
    print(encoded if args.json else human_report(report))
    # Mixed/unknown evidence is normal exploration. Codes are report triage,
    # not promotion gates: 1 criterion failure, 2 unresolved, 0 all obligations
    # answered. Directives remain authoritative scope information, never scored.
    statuses = {q['status'] for r in report['requirements'] for q in r['questions'] if q['status']}
    return 1 if 'FAIL' in statuses else 2 if statuses & {'UNKNOWN', 'INCONCLUSIVE'} else 0


def recorded_design_scope(root, inventory='notes/verification_sources.json'):
    """Conservative applicability guard using execution's existing file digests.

    Object-reviewed source inventories associate reported designs, not unknown
    printed artifact bytes. No cache, alternate geometry or execution identity.
    Missing/changed files invalidate transfer; read the retained human limits.
    """
    from execution.identity import digest
    record = json.loads((root/inventory).read_text())
    matches = bool(record['source_sha256']) and all((root/name).is_file() and digest(root/name) == value
                  for name, value in record['source_sha256'].items())
    return 'migration-reviewed' if matches else 'modified-or-missing-source'


def protect_recorded_intent(root, current, *, changes=None):
    """Compare the product's reviewed user-intent snapshot before any run.

    Object-owned inventory is an audit baseline, not a global registry. Later
    user supersession is explicit UserSource in changes; retain the old record.
    """
    record = json.loads((root/'notes/verification_sources.json').read_text())
    previous = tuple(UserRequirement(x['id'], x['text'], UserSource(**x['source']),
        tuple(Question(**q) for q in x['questions'])) for x in record['user_requirements'])
    protect_user_requirements(previous,current,changes=changes)
