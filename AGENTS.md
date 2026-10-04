# AGENTS.md

This repository contains autonomous, parametric CadQuery projects, primarily for
single-material FDM printing. Complete the authorized task with minimal user
intervention. Functional product value and whole-object usability take precedence
over locally successful geometry, mechanisms or numerical analysis.

## Find the task guidance

Read only the applicable skill and reference sections. Retrieve early guidance
before the decision it governs, technical details before the operation, and
project evidence when its interface or result applies. Do not treat truncated
output as inspected; read the missing section. User instructions and existing
authorization override recorded defaults; do not ask again for settled choices.

| Task | Entry point and timing |
| --- | --- |
| Every 3D modelling task, including an established-product revision | [CadQuery design](.codex/skills/cadquery-3d-design/SKILL.md). It routes early product decisions, preferences and manufacturing assumptions, then conditional references. |
| Structural, flexure or contact analysis | [Physical-analysis use](physical_analysis/README.md#use) and its decision-driven [study guidance](physical_analysis/README.md#study-sequence) before solving. Product work also uses the design skill; independent numerical benchmarks do not require product review. |
| Final smoke slice or slicer-sensitive question | [Print planning](.codex/skills/cadquery-3d-design/references/print-planning.md#final-review-and-reference-smoke-slice), then [Orca inspection](.codex/skills/orca-slicer-printability/SKILL.md). |
| Physical feedback, modelling-phase handoff, reflection or workflow improvement | [Engineering reflection](.codex/skills/engineering-reflection/SKILL.md). Print feedback first goes to the object's status and root index; a failure routes to the physical-feedback reference. Routine handoffs need only a brief review of new evidence. |
| Computational profiling, execution studies or interrupted-work recovery | [Engineering execution](.codex/skills/engineering-execution/SKILL.md). Ordinary commands need no performance investigation. |
| Requested agent latency, tokens or combined workflow investigation | [Workflow performance analysis](.codex/skills/workflow-performance-analysis/SKILL.md). Session inspection is conditional, not routine. |

Skills own task methodology; their references own specialized judgment and user
preferences. [Execution documentation](execution/README.md) owns command, identity,
resource and recovery contracts; [physical-analysis documentation](physical_analysis/README.md)
owns analysis APIs and numerical evidence. Each object owns its requirements and
results; [reusable evidence](.codex/skills/cadquery-3d-design/references/reusable-model-lessons.md)
is a bounded discovery index, not a universal rulebook.

## Object ownership and source of truth

Keep each logical object or assembly in `model/<object_name>/`, including all
source modules, exports, supplied references, views, notes and experiments.
Independent objects need separate directories; assembly components may share one.
Do not create global format-based export/reference directories. Create only useful
files. The parametric CadQuery Python source is authoritative; meshes are exports.

Keep one concise current decision/evidence record (README or linked existing notes)
per object. State shared assumptions and print/use instructions once, with only
consequential variant differences. Keep deliverable links, verification, unique
physical observations, print status and attribution easy to find. Preserve valid
historical evidence deliberately; Git history can hold superseded process prose.
Do not commit a second completed checklist duplicating that record.

## Evidence integrity

Use checks that address actual design intent, with an expected result and a
decision the result can change. CAD validity, numerical convergence, provisional
material/design screens, slicer acceptance and physical validation are different
conclusions. Do not present unmeasured printed-material properties, friction,
tolerances, durability or subjective comfort as calibrated facts. Record unknowns
as unknowns. User product rejection overrides speculative confidence and requires
corrected readiness, even when local checks passed.

Trust each tool for the question it answers, under the checked inputs and limits.
Revisit affected evidence after relevant changes or a concrete reason for doubt;
do not restart all verification for every revision. Successful existing interfaces
and retained evidence must be preserved within their scope. Final verification
must cover the delivered files, placement, settings and tool identities.

Do not routinely recreate deliberately omitted CAD bounds, volume, solid counts,
STEP reimports, STL topology/bounds audits or G-code footprint checks. An exception
needs a concrete suspected failure, expected result, changed decision, and a reason
planning or the responsible tool's status cannot answer it. Successful export
conversion and Orca layout acceptance should not be independently re-proved by
generic checkers. An STL slice does not verify Orca's separate GUI STEP import.

## Shared engineering execution

Run CAD from the repository root with
`./evaluate_model.py model/<object>/<object>.py`; run ordinary experiments with
`./execute.py SCRIPT.py [ARGS...]` (options precede the script). Read
[CAD operation details](execution/README.md#cad-evaluation-and-exports) before using
exports, views or reports. Both commands bootstrap the locked uv environment and
manage resource admission, isolation, tracing and controlled artifacts. Use
`uv sync --locked` if installing the environment manually; use `uv run --locked`
for direct package commands. Dependencies belong in root `pyproject.toml` and
`uv.lock`; commit both when changed. Do not use ad-hoc environments or another
manager. OrcaSlicer is a separate host/Flatpak tool.

Do not invent wall-clock computation deadlines for modelling, analyses, slicing,
diagnostics, discovery, benchmarks or recovery. A finite runtime limit implements
only an explicit user-requested deadline, never an expected duration or precaution.
Diagnose slow work from progress and evidence. Service connection, idle-retirement
and termination-cleanup allowances have separate lifecycle roles.

Keep Gmsh/native solvers isolated through the physical-analysis APIs. Use existing
execution/batch and question/study interfaces instead of another scheduler, trace
schema or arbitrary-result cache. Geometry reuse requires complete deterministic
inputs and no required construction side effects; unknown inputs stay fresh.
Preserve identity guards, output ownership and explicit fresh/reused status. Never
replay unknown side effects or promote interrupted/failed native work to completion.
The [execution contract](execution/README.md#architecture-contract-version-1)
owns the automated safeguards and caller responsibilities, including freezing
repository Python during CAD publication and budgeting nested work.

## Avoid repeated work

Judge cost across agent turns, implementation, maintenance and compute. The user
prefers reliable repeatable compute when it saves agent effort; invocation counts
or solver runtime alone do not establish waste. Use the cheapest reliable evidence
that can change the next decision. Established automatic checks run when applicable
without a fresh justification each time; reconsider a consistently uninformative
check itself. Reuse unchanged evidence and batch independent work after its
prerequisites; keep dependent corrections and adaptive refinements sequential.
Documentation-only edits need documentation validation, not new CAD or slices.

## Improve shared tools from concrete needs

Implement justified reusable improvements within the authorized task; observing a
gap alone does not complete an authorized improvement. A concrete consumer,
demonstrated failure or repeated work must drive it. Prefer extending an existing
API or deleting duplication over speculative frameworks. Keep object geometry,
assumptions and acceptance thresholds local. Seek a decision if the extension
materially changes scope. [Reflection](.codex/skills/engineering-reflection/SKILL.md#put-the-result-in-its-owning-source)
owns extension placement, qualification and documenting a specific blocker when
completion is not justified or possible. No ordinary task requires an API audit.

## Delivery and provenance

For the phase's agreed printable objects (including samples), deliver at least
`.py`, `.step` and matching `.stl`, unless explicitly requested otherwise. STEP is
the primary print-ready interchange file. Export both from the same selected
geometry and print placement, with matching units, orientation and component
positions. Keep display-only references out of printable results. Rough studies
need useful evidence rather than print-ready exports or slicing. Apply the design
skill's final FDM review and smoke check only to the agreed printable deliverables.

Use the [standard print-status block](.codex/skills/cadquery-3d-design/references/physical-experiments.md#standard-per-object-print-status-record)
for test pieces and final objects, including N/A categories for rough/sample phases.
On user print feedback, update the object record and root model-index summary
together. Do not infer a print from a CAD or slicer result.

Record attribution per model: primary language model, reasoning effort,
harness/agent environment and provider; list material contributors when known.
Use runtime information or explicitly attributed user information; unavailable
fields are `unknown` or `not exposed` and do not block delivery. Preserve historical
attribution during documentation maintenance. Requested performance investigations
may supplement it with reviewed aggregates under the performance skill's privacy
contract. Preserve third-party licensing and attribution; see [licensing](README.md#licensing).

## Git workflow and handoff

Commit and push completed repository tasks automatically. Inspect status and the
relevant diff, preserve unrelated/concurrent changes, stage only requested work,
and run `git diff --cached --check`. Omit scratch/generated junk. `.gitattributes`
handles exporter STEP whitespace; do not rewrite exports merely to remove spaces.
Use a concise descriptive commit and push the current upstream branch; do not
switch branches merely to complete a task.

Track and report actual commit/push completion; do not pre-mark it in committed
notes, substitute staged for pushed, or commit again just to tick a box. The
handoff states changes, deliverables, relevant assumptions, verification and
material limitations. A failed push is incomplete delivery.
