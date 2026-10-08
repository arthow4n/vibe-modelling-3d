# Product verification

This small reporting layer preserves declared intent across variant iteration.
It consumes object-owned callables, `assembly_geometry` answers, existing
analytical/physical-question records and explicitly scoped user observations.
It has no geometry, scheduler, result cache, solver, automatic check discovery,
Markdown parser, promotion gate or overall product score.

## Concrete problem and adopted boundary

The Q1/Q1F checks were shared but aborted at the first assertion; a new
architecture could omit them and appear successful. Their CAD passes coexist
with physical noise/appearance/upper-fit failures and an authoritative stop.
The sunglasses case has successful printed samples and full-case use, but those
observations cannot qualify another mechanism/material or long-term fatigue.
Both need explicit coverage and scoped evidence, above their existing operations.
The jar demonstrates a different opening/retention strategy; the plate demonstrates
retained conditional analytical evidence. Those repeated needs justify the small
stdlib records, runner and reporters in [the implementation](__init__.py).

Each object's existing README/current record still owns nuanced intent, physical
observations, rationale, hypotheses, history and instructions. Its
`verification.py` manually links stable IDs to that record and explicitly composes
checks. There is no inference of user instructions from prose. Ordinary
construction/program invariants can remain assertions without permanent IDs.

## Records and provenance

- `UserRequirement`: user instruction or acceptance, with `UserSource(reference,
  statement)`, protected `text` meaning and optional `acceptance_criteria` for
  explicit user thresholds/dimensions. Do not manufacture user provenance from an
  agent's design rationale.
- `DerivedRequirement`: declared parent requirement/evidence IDs and derivation.
  Circular parent chains are rejected. Revise or retire it when that derivation/architecture changes. Decisions,
  hypotheses and directives cannot be parents pretending to be engineering facts.
- `DesignDecision`: challengeable implementation choice; separate from requirements.
- `Hypothesis`: open assumption/possible cause, never physical evidence.
- `Directive`: user scope/project-state instruction, never PASS/FAIL.
- `Evidence`: result for one or more `(requirement ID, question ID)` obligations,
  with summary, source reference and explicit applicability scope.

`Question(id, requirement_id, criterion, mode)` is a challengeable engineering
obligation supporting a user or derived requirement. `Plan(..., questions=...)`
owns the current decomposition; requirements do not own questions. Checks and
retained evidence keep their many-to-many `(requirement ID, question ID)` targets.

For example, stable `case.operation` intent can be decomposed into closed fit,
opening path, retention, release and physical use for E, then into thread
engagement, helical opening and axial obstruction for a future architecture.
Adding, replacing or retiring those questions and strategies needs no later user
instruction. The replacement must still meaningfully cover the active intent.
Sampling angles, axial witnesses and overlap thresholds chosen by the agent are
engineering screens; a user explicitly adopting a threshold makes it protected
acceptance intent. CAD obstruction does not answer physical effort or durability.

Each migrated object has one [reviewed inventory](../model/sunglasses_case/notes/verification_sources.json)
containing protected user intent and conservative source/evidence associations,
without duplicated engineering questions. `protect_recorded_intent()` compares
stable user IDs, `UserSource`, `text` and `acceptance_criteria` before each run.
Removal, reclassification or changes to these fields require an explicit later
`UserSource` in `changes={requirement_id: later_instruction}`. Text is compared
exactly because this audit cannot distinguish harmless rewording from weakened
meaning; use other human prose for editorial explanations. Preserve the prior
instruction and explain authorized supersession in the object's human record.
Newly established requirements need real user provenance; adding them is not
automatic proof of that provenance. Do not promote an old engineering question
into acceptance intent merely because it was in the previous snapshot.
This protects accidental/silent edits during normal use, **not** deliberate editing
of both audit baseline and guard. Git review and truthful agent records still matter.
Do not update snapshots simply to make a failing candidate pass.

## Composition and outcomes

`Plan` receives requirements, current questions, candidate scope, ordinary `Check`
callables and retained `Evidence`. Every declared question is reported even when
no check is implemented or selected. Every active requirement is also reported:
zero questions yields `questions=[]`, `coverage="uncovered"`, UNKNOWN in the human
report and `unresolved_evidence` in the CLI. Partial/missing applicable evidence
also leaves uncovered questions visible. Passing the remaining checks cannot
hide a requirement whose decomposition was removed. Variant-specific derived
requirements use `non_applicable={id: reason}`; N/A has no passing status. `Plan` rejects user
requirements in that mapping: a candidate's architecture cannot exclude user
intent. An explicit later user instruction may supersede/remove that intent
through the provenance guard; preserve the earlier instruction in the object record.

A callable may return several evidence records and cover multiple obligations.
Several callables/sources can address one obligation. A declared check that returns
nothing leaves its obligation UNKNOWN. Use separate question IDs when evidence
answers independent obligations (CAD obstruction, physical effort, wear), rather
than letting one substitute for another.
Each `Question` requires an explicit `mode` label (for example CAD, physical,
subjective or analytical);
omission cannot silently categorize a physical question as CAD.

| Result | Meaning |
| --- | --- |
| PASS | Applicable evidence satisfies the stated criterion, within its limits |
| FAIL | Applicable evidence contradicts the criterion |
| UNKNOWN | Active requirement has no decomposition, question has no applicable evidence, or evidence leaves it unanswered |
| INCONCLUSIVE | Attempted verification cannot support a conclusion |
| N/A | Explicit variant exclusion/reason; never a PASS |

For multiple applicable answers to **one question**, precedence is FAIL,
INCONCLUSIVE, UNKNOWN, PASS. All sources remain visible, including contradictory
ones. This is a conservative question summary, not a product score. Different
questions keep different answers; digital PASS never overwrites physical FAIL.

`assertion_check()` adapts existing consequential assertion groups. Ordinary
criterion assertions produce FAIL; `CalculationInconclusive` and native
`require_passed()` inconclusive dictionaries produce INCONCLUSIVE. Independent
checks continue. A group must answer one composite obligation, or only targets with the
same conclusion. For independent obligations, compose adapters returning separate
evidence records, as Q1/Q1F hood path, insert capture and landing access do; failure in one does
not falsely mark the other FAIL. Groups are the isolation boundary,
not every measurement. Unexpected programming/configuration errors propagate
clearly, instead of becoming plausible product outcomes. When adapting a legacy
kernel/solver boundary, explicitly translate its known unsuccessful calculations;
do not broadly swallow exceptions or treat invalid/absent values as zero.
`engineering_evidence()` directly consumes PairResult/MotionResult statuses.
Physical-question consumers should retain their existing `read_evidence()` /
`QuestionStudy` identity/quality/acceptance contracts; solver completion is not a
product or material PASS. No new physical-analysis API is introduced here.

## Scope and retained evidence

Evidence scope is an explicit object-owned dictionary. All its keys must match
candidate scope; mismatches remain listed as out of scope while the obligation
becomes UNKNOWN if no other applicable evidence exists. Declare consequential
architecture, material, dimensions, process/print conditions and revision when
known. An empty scope is rejected. This is applicability annotation, not a second
execution or geometry identity system.

Physical evidence is surfaced, not rerun. The migrated inventories use
`execution.identity.digest` and the existing source-hash convention to conservatively
invalidate association when reviewed source bytes change. They identify designs
as described by the user, **not exact unknown printed artifacts**. Reported
materials/settings remain unknown where the original records say so. An intended
PETG profile is not proof that a user printed PETG. The `tpu-fixture` case and the
actual `q1f-tpu-hood` history deliberately leave prior physical qualification behind.
A changed builder, dependency, candidate dimensions, material or process requires
reviewing scope. If new inputs are introduced, include them in the owning scope /
existing identity contract; updating inventory hashes alone cannot qualify a print.
Conservative source invalidation may also trigger after harmless refactors: review
and explain evidence transfer rather than fabricate another physical test.

The plate's adapter reads `notes/load_checks.json`, checks its existing input
hashes and interprets its stored screens. Its object-owned reviewed inventory
names the complete expected input and screen sets; a received result cannot
redefine its own coverage by omitting failed or missing screens. Malformed
containers, inconsistent margins and partial records are INCONCLUSIVE. A broken
configured coverage contract raises clearly. Missing/stale evidence is UNKNOWN;
malformed attempted interpretation is INCONCLUSIVE. It launches no solver or
arithmetic job. A conditional numerical screen does not establish physical load
capacity, creep, print properties or a certified rating. Original numerical,
slice and physical records remain unchanged.

## Running during iteration

Every product adopting this layer **must** expose `model/<object>/verification.py`
and delegate its command entry point directly to `product_verification.cli`:

```python
if __name__ == '__main__':
    raise SystemExit(cli(make_plan, ('declared-variant',)))
```

This is a repository command contract, not an optional convenience. The shared
helper owns argument parsing, JSON output and binary exit semantics. Do not add
object-specific parsers, flags, argument defaults or output formats. Products own
the declared variant/check names and the plan's requirements, checks and evidence;
they do not inherit engineering checks from a common verifier. A justified command
change belongs in the shared helper, documentation and conformance tests together.
Simple products retaining adequate local checks are outside this adoption contract.

Plan factories must define `make_plan(variant)` with no default or implicit
selection. Direct Python callers also name the design explicitly, for example
`make_plan('accepted-e').evaluate()`. Omitting the variant raises `TypeError`
before plan construction; the CLI already requires `--variant`.

From the repository root:

```sh
./execute.py --threads 2 model/filament_swatch_box_study/verification.py --variant q1f
./execute.py --threads 2 model/filament_swatch_box_study/verification.py --variant q1
./execute.py --threads 1 model/sunglasses_case/verification.py --variant accepted-e
./execute.py --threads 1 model/vaseline_container/verification.py --variant accepted-thread
./execute.py --threads 1 model/book_reading_plate/verification.py --variant accepted-plate
./execute.py model/sunglasses_case/verification.py --help
./execute.py model/sunglasses_case/verification.py --variant accepted-e --help
./execute.py --threads 1 model/sunglasses_case/verification.py --variant accepted-e --check e.retention
./execute.py model/sunglasses_case/verification.py --variant replacement-fixture > /tmp/case-verification.json
```

The verification CLI has only required `--variant`, optional repeatable `--check`
for focused iteration, and `--help`. There is no implicit variant selection and
no output/format flags. Generic help returns `available_variants`; variant help
also returns the plan's declared `available_checks` without running them. Use those
names, rather than guessing arguments. Omitted checks remain visibly UNKNOWN.
The shared execution wrapper's own options are unchanged.

Stdout is one JSON envelope for results, help, invalid arguments, interrupted
checks and fatal runner errors. Progress and exception diagnostics go to stderr.
Redirect stdout to save a receipt. The envelope always contains `schema_version`,
`variant`, `selected_checks`, `available_variants`, `available_checks`, `exit_reason`,
`error`, `report` and `help`. `report` contains the detailed verification
record (including requirement coverage and user acceptance criteria), or null
when no trustworthy report was produced. `error` contains exception type, message
and stage, or null; fatal program/configuration errors are not
manufactured requirement FAIL/INCONCLUSIVE results. Invalid/nonfinite JSON data
produces `report_error` with a null report. Direct Python APIs still raise program
errors; translation happens only at the CLI boundary. Interpreter startup failure
or external termination before that boundary cannot produce a CLI receipt.

Shell codes are **0** or **1** only. Read `exit_reason` and the per-question results
to distinguish engineering outcomes. Exit 0 means verification produced a valid
report or help; exit 1 means the command failed, not that the product failed:

| `exit_reason` | Meaning |
| --- | --- |
| `verification_complete` | All active requirements have questions and all applicable obligations are answered; exit 0 |
| `criterion_failed` | Applicable evidence includes FAIL; exit 0 |
| `unresolved_evidence` | UNKNOWN/INCONCLUSIVE remain without FAIL; exit 0 |
| `argument_error` | Missing/invalid variant or check selection; exit 1 |
| `execution_error` | Fatal programming/configuration error or unexpected checker exit; exit 1 |
| `report_error` | Report could not be encoded as valid JSON; exit 1 |
| `interrupted` | Verification interrupted; exit 1 |
| `help_requested` | Usage/declared choices returned without checks; exit 0 |

Successful execution does not establish product readiness or a qualification score.
Q1F's physical failures and the accepted case's unknown durability both exit 0;
their JSON preserves the engineering outcomes. Focused checks also exit 0 when
they complete, with omitted obligations still visibly UNKNOWN.
`human_report(envelope['report'])` remains available as a Python formatter for a
completed report.
Exploratory geometry is allowed under any outcome. Directives remain authoritative:
these commands do not authorize reopening damping work or recommending a print.
No detailed MotionResult/solver trace is duplicated by default; linked existing
checks/native records own their diagnostics. Python checker/factory output is
redirected to stderr, preserving JSON stdout. Saved receipts are not result caches.

## Migrated consumers and deliberate exclusions

| Product/variant | Reused evidence and boundary |
| --- | --- |
| Q1 / Q1F | Existing closed/card/hood/insert/landing/join groups extracted from `check_quiet_q1.py`; original `main()` still composes those groups and writes the established report. Q1F additionally calls its existing local connectivity/rim screens. A composed hood/insert/landing check returns independent evidence for separate requirements while sharing candidate geometry; joining includes independent opening in its own composite criterion. Physical Q1F joining PASS coexists with noise/coverage/fit FAIL; Q1 has no inferred print result. |
| All-TPU G hood on Q1F | Retained noise FAIL and distorted-but-usable observation; appearance acceptance UNKNOWN, not invented rejection. No new material-qualified CAD/print/solver work. Layer-line explanation remains OPEN; damping stop remains INFO. |
| Accepted sunglasses E full case | Existing closed, shell path, rotational/axial obstruction and released-loop checks split into callable groups. Production and product verification share both original retention witnesses. Existing source cavity, component validity, print-placement and keeper-capture assertions are callable; source validation is retained; exports use the explicit evaluator boundary. D/E coupon PASS records stay scoped to samples; separate full-case PASS does not answer fatigue. |
| Accepted threaded Vaseline pair | Existing helical path and axial obstruction functions; nominal requested envelope check; retained successful print report and wear UNKNOWN. No universal retention mechanism. |
| Accepted book plate | Existing seating/clearance group, retained analytical input-bound screens and scoped user print result. Specific physical load and long-term creep remain UNKNOWN. |
| V3 phone stand rear release | Product-local articulated kinematic endpoint/access questions replay saved joint states and sampled transitions against current CAD envelopes. Source/tool mismatches leave UNKNOWN; no complete witness is INCONCLUSIVE. Physical integrated operation stays UNKNOWN; other V3 engineering records retain their existing scope. |
| Replacement fixtures | No candidate geometry or verifier; user obligations stay UNKNOWN. Obsolete keeper/insert requirements are explicitly N/A. These are qualification fixtures, not proposed product directions. |

The one-piece rounded storage tray and printed Vaseline transfer spatula deliberately
retain their current local checks and human evidence: no coupled mechanisms or
variant verification gap justifies a plan yet. Phone stand retains its existing
local CAD/physical engineering checks alongside the narrow human-interaction
adoption. Glove insert, older swatch mechanisms and other historical scripts
remain on their existing local checks/questions; this task does not mechanically
migrate every assertion.
Adopt the convention when consequential intent can disappear across variants or
multiple independent evidence sources need preservation, regardless of solid count.
A substantive one-piece variant family can benefit; a multipart object with adequate
local evidence may still opt out. Record that choice briefly, without ceremony.

## Qualification and limits

[Semantic tests](../tests/test_product_verification.py) exercise provenance,
supersession, missing/partial/focused coverage, N/A, many-to-many composition,
alternate callables, contradictory evidence, failed/inconclusive calculations,
programming errors and scope invalidation.
[Consumer tests](../tests/test_product_verification_consumers.py) run actual checks,
compare Q1/Q1F retained legacy outcomes, reuse their placement/print-selection
qualification and preserve the wrong-hood, missing-bead and floating-card mutations.
Accepted STEP/STL bytes are fingerprinted; no exports, slices or solvers are rerun.
Existing assembly regressions remain applicable.
[CLI tests](../tests/test_product_verification_cli.py) qualify the uniform JSON
envelope, explicit choice communication, command success despite FAIL/UNKNOWN/
INCONCLUSIVE or focused unresolved coverage, mixed evidence,
argument/runtime errors, interruptions and invalid serialization without CAD work.
[Entry-point conformance tests](../tests/test_product_verification_entrypoints.py)
cover every `model/*/verification.py`, including newly added products. They require
direct delegation to the shared helper, reject implicit plan-factory defaults,
and exercise the common command behavior with a lightweight substituted plan,
without building geometry or changing the
product's engineering checks.

Coverage is only as complete as the declared catalog and truthful scopes. A nominal
parameter check is not an independent geometric dimension audit; sampled motion
is not continuous-path proof; rigid overlap is not holding force, quietness or
printed fit. Missing/stale physical evidence remains missing. This structure
protects intent and claims while leaving architecture, dimensions not explicitly
required, mechanism choices and provisional assumptions open to challenge.

Initial infrastructure attribution: GPT-6-based Codex; exact model variant and reasoning
effort not exposed; Codex shared-workspace API agent; OpenAI; no subagents.
Historical product attribution is preserved in the owning records.

Post-implementation corrections also include an independent Codex subagent code
review, started with a fresh context containing the original objectives and
preservation constraints without the implementer's conclusions. Primary correction
author and reviewer: GPT-6-based Codex; exact model variant/reasoning effort not
exposed; Codex shared-workspace API agents; OpenAI. Review covered code correctness
and future maintenance; the corrective diff received follow-up review and focused
regression qualification. This does not add product or physical qualification.

Qualification found one pre-existing plate inventory mismatch: a builder docstring
and measurement entry guard had changed since its analytical report. The object's
record documents the reviewed Git diff and exact historical/current source pairs.
Its adapter accepts only that explicit association; further changes remain UNKNOWN.
Tests also cover missing/stale/malformed/nonfinite retained calculations and a real
stored analytical criterion violation. No historical result is edited to manufacture
current identity or physical acceptance.

When replacing a strategy or changing its thresholds/sampling, explain the evidence
and why it still answers the unchanged product intent in the owning record.
User-specified numerical limits belong to protected intent; agent-selected screens
remain challengeable. The intent audit cannot prove that arbitrary Python correctly
implements its declared question. Preserve useful negative cases and review changed
claims rather than treating a passing wrapper as independent verifier qualification.

Final consumer review also found that the swatch procedure could traverse a
shortened card list while still reporting nominal capacity 15. Its existing card
group now requires the full population before traversal; incomplete attempted
fixtures are INCONCLUSIVE, rather than claiming a physical capacity failure.
The required count is in protected intent. Tests use both actual source-card
populations and deliberately remove one card. Other geometry criteria are unchanged.
The jar similarly distinguishes the reported good print from unreported specific
opening/retention handling; print quality does not qualify those physical questions.

Intent/decomposition correction contributor: GPT-6-based Codex; exact model variant
and reasoning effort not exposed; Codex shared-workspace API agent; OpenAI; no
subagents. All four consumers now keep questions in their plan declarations;
protected numerical intent comes from the existing case/jar dimension records
and swatch capacity record. Plate analytical coverage remains an engineering
contract alongside its unchanged source associations. No geometry, exports,
physical observations or readiness conclusions changed.
