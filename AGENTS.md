# AGENTS.md

This repository contains autonomous, parametric CadQuery modelling projects,
primarily for single-material FDM printing. Work toward a functional result with
minimal user intervention; the source and deliverables are the primary output.

## Design guidance and printer

For every modelling task, read and apply the repository's
[CadQuery design skill](.codex/skills/cadquery-3d-design/SKILL.md), including its
[modelling checklist](.codex/skills/cadquery-3d-design/SKILL.md#modelling-todo-checklist).
The skill owns functional design, ergonomics, critical dimensions, mechanisms,
edge treatment, print planning and physical experiments. This file owns
repository workflow, tools, ownership, attribution and delivery.

Use **260 × 260 × 250 mm (X × Y × Z)** as the default practical printable
envelope and a **0.4 mm nozzle**, unless the user specifies another setup. This
is the usable design limit, not the printer's physical plate dimensions. Include
generated brims/supports when checking XY, and check each oriented axis
independently.

Do not reject an object merely because its assembled size exceeds that envelope.
Plan it as multiple printable parts when no acceptable orientation fits. Before
committing to the split and joint geometry, establish with the user the required
joint strength, relevant loads and directions, acceptable hardware/adhesive,
permanent versus demountable assembly, and any safety consequences. Recommend a
feasible joint strategy and explain its tradeoffs; do not silently assume that a
simple alignment or friction joint is structurally adequate. Check every part,
including its print aids, against the practical envelope and verify the assembled
interfaces and load path.

## Core workflow

1. Inspect the request, references, existing files and user changes. Reuse known
   preferences. Honor requests to choose reasonable defaults autonomously;
   otherwise ask focused questions only for unresolved requirements that
   materially affect fit, function or manufacturing. Oversized objects still
   require the joint/load agreement described above unless the user already
   supplied it. Document important assumptions.
2. Confirm `uv` and the repository's shared
   [CadQuery command](scripts/evaluate_model.py) are available. Run `uv sync --locked`
   from the repository root when the locked environment is not installed.
3. Create or revise the object's parametric Python source. Evaluate the file
   through the shared command and inspect validity, topology, bounds, parameters and errors;
   choose views using the skill's evidence guidance.
4. Compare the geometry against the intended use and references. Check access,
   insertion, retention and release as relevant. Correct the largest functional,
   structural, ergonomic or printability discrepancies and evaluate again.
   Repair the smallest underlying cause of a build failure; simplify the approach
   if it repeatedly fails. A valid build alone does not establish function.
5. Apply the skill's CAD/export checks and final generic FDM review, including
   its final reference-slice smoke check when available. Continue until the
   concrete review questions are resolved and further iteration is unlikely to
   materially improve the result. Distinguish CAD/slicer evidence from physical
   testing; document any remaining limitation.
6. Save matching print-ready exports, useful final views and one concise record
   of assumptions, print/use instructions and verification evidence. Include
   the [standard per-object print-status block](.codex/skills/cadquery-3d-design/references/physical-experiments.md#standard-per-object-print-status-record)
   for test piece(s) and the final printable object(s), even when one category
   is not applicable. When a user reports a print, update the object block and
   the root model-index summary together.
7. Review, commit and push the completed work using the Git workflow below.

## Object ownership and source of truth

Each logical object or assembly owns one directory. Keep **all** its source
modules, exports, references, renders, notes and experiments inside it:

```text
model/object_name/
  object_name.py
  object_name.step
  object_name.stl
  README.md                 # or clearly linked existing project notes
  references/               # supplied images, drawings and other references
  renders/                  # useful print/assembled views
  notes/                    # checks, profiles and experiments when useful
```

Create only useful files. Independent objects need separate directories;
components of one assembly may share a directory. Do not organize object files
in global format-based directories such as `exports/` or `references/`.

The object's CadQuery Python source is authoritative. Keep likely adjustments
as named parameters with dependent geometry derived from them. Use a clear main
entry point and component modules when that improves readability; document useful
component/assembled entry points and verify imports through the shared command. Follow the
[construction guidance](.codex/skills/cadquery-3d-design/references/parametric-and-edges.md)
for parameters, components and edges. Prefer understandable CadQuery operations;
use lower-level OCP only when it materially helps. Do not make a mesh the primary
modelling representation.

## CadQuery evaluation and exports

Run `uv run --locked python scripts/evaluate_model.py model/object_name/object_name.py`
from the repository root. See [command usage](scripts/README.md) for views,
exports, reports and dependencies. The command supplies
`__file__`, the model directory as the worker's working/import directory, and a
fresh process per evaluation. Ordinary sibling imports therefore see current
source. `result` explicitly selects the output; otherwise all `show_object()`
outputs are combined. Do not mix display-only reference geometry into the
selected printable result.

Use `--views none` for checks that need no images. Inspect structured error status:
a failed view can coexist with successful geometry or exports. Saved paths are
successful outputs only when their corresponding status says so. Build and
render timings are separate. Model files are trusted Python and may write their
own artifacts; the command does not roll back those side effects.

For normal printable models, deliver at least `.py`, `.step` and `.stl`.
Export STEP and STL from the **same geometry and print placement**, with matching
units, orientation, bed position and relative component positions. The command's
`--step` and `--stl` options write both from one build; use an object-owned wrapper
when custom checks or component exports require it. Verify the actual final pair
using the [export checker](.codex/skills/cadquery-3d-design/references/export-verification.md).
Use an explicit `_assembled.step` suffix for an additional inspection pose.
Respect an explicit user request for a different export arrangement. Add 3MF or
other formats only when useful.

Retain useful final views under `renders/`; isometric, front, top and right are
available choices, not a required set. Each additional view should answer a
distinct visual question or explain the delivered object. For saved intermediate
views, use
`renders/scratch/`; retain selected final views in `renders/print/` or
`renders/assembled/`. Exterior inspection normally uses `show_hidden=false`.
Use hidden lines or sections for a specific internal-geometry question. Remove
disposable scratch output before staging; retain historical evidence deliberately.

Actually open saved views when visual judgment is needed; a path or successful
render status is not visual inspection. When the agent's tools support composing
command execution and image reading within one outer tool call, prefer running
the command, reading its successful view paths, and returning the needed images
in that same call. Those are sequential operations, not an image returned by the
shell command. Otherwise use a separate image-reading call. Reuse the saved
image; do not rebuild the model merely to open it. Keep the command's four-view
default, and explicitly choose fewer views or `--views none` when the question
does not require all four.

## Avoid repeated work

Choose the cheapest reliable evidence for the remaining question, following the
[skill's evidence selection](.codex/skills/cadquery-3d-design/SKILL.md#proportionate-review).
Build once where possible and batch exports, measurements and needed views.
Separate cheap build assertions from expensive mechanism sweeps; rerun affected
sweeps after interface changes, not merely to obtain another view.

Reuse evidence only when its relevant inputs are unchanged and recorded:

- CAD: source modules, parameters, placement and tool versions.
- Exports: actual file hashes and checker settings/version.
- Slicing: mesh, effective profile, command options and slicer version.

Changed inputs invalidate affected checks; rerun if dependencies are unclear.
The command's imported-module hashes are useful evidence, not a complete record
of arbitrary files a script reads. Final verification must cover the final files.
Do not introduce a caching framework for a one-off task. Unchanged helpers do not
need their own regression suites rerun for every model.

Keep one concise decision/evidence record. Return compact summaries and inspect
full logs only for a failure or unresolved question. Documentation-only changes
need document validation, not new CAD evaluations or slices.

## Model provenance and attribution

Record attribution **per model**, in its documentation or clearly linked notes:
primary language model, reasoning effort, harness/agent environment and provider.
Use actual runtime information or explicitly attributed user-provided information.
Record unavailable fields as `unknown` or `not exposed`; do not guess or block
otherwise completed work solely to obtain unavailable metadata. List material
contributors after the primary model when known.

Preserve historical attribution when doing documentation-only maintenance.
Existing records are linked from the [model index](README.md#models); they are
historical evidence, not defaults for future models. Keep third-party licence
and creator attribution intact; consult the root README's licensing section.

## Python dependencies

Use the root `pyproject.toml` and `uv.lock` for Python tooling. Run commands with
`uv run --locked` and commit dependency changes to both files, not environments
or caches. PrusaSlicer is a separate system command. Do not use
ad-hoc virtual environments or another environment manager.

## Git workflow and handoff

Automatic commit and push are preferred for all completed repository tasks.
Inspect status and the relevant diff, stage only requested work, and run
`git diff --cached --check`. `.gitattributes` suppresses exporter-generated STEP
whitespace noise while preserving text diffs; do not rewrite CAD exports merely
to remove spaces. Preserve unrelated user changes and omit temporary/generated
junk. Commit with a concise descriptive message and push the current upstream
branch; do not change branches merely to complete the task.

Track commit/push completion in the active task checklist and report the actual
result at handoff. Do not pre-mark it complete in committed notes, substitute
“staged” for “pushed,” or make another commit solely to tick that box.

The final response should concisely state what changed, important assumptions,
object directory and deliverables, verification and material limitations, and
the commit/push result. Report a failed push as incomplete delivery rather than
claiming success.
