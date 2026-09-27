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

Use the Qidi Q2C **270 × 270 × 256 mm (X × Y × Z)** build volume as the default
practical printable envelope
([Q2C specifications](https://us.qidi3d.com/products/q2c)), unless the user
specifies another setup. This is the usable design limit, not the printer's
physical plate dimensions. Include generated brims/supports when checking XY,
and check each oriented axis independently. For OrcaSlicer reviews, take the
printable area and height from the selected printer profile; do not maintain a
separate bed-size override. Use a smaller user-confirmed safe volume by
providing a printer profile with those limits.

The user's preferred starting setup is a **0.4 mm nozzle and 0.2 mm layers**.
They also have a **0.8 mm nozzle** and several **PLA, PETG and TPU** filaments.
Their experience is that **two walls and 7% adaptive cubic infill** are often
enough for general prints; these are starting assumptions, not strength or
printability requirements. Discuss the proposed nozzle, layer height, material,
walls and infill approach during the initial design agreement. Explain and agree
on consequential changes, especially when fit, flexibility, strength, print
time or finish depends on them. Use the agreed setup to size geometry and screen
loads before slicing. The reference Orca profile is diagnostic, not a substitute
for the agreed print setup.

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
   preferences. Look for an analogous model in the
   [reusable design evidence](.codex/skills/cadquery-3d-design/references/reusable-model-lessons.md)
   and its linked source before starting from zero; carry over only evidence
   that applies to the new geometry and print setup. Before detailed CAD, make
   the cheapest useful concept screen:
   approximate fit and assembly travel, mating engagement, print envelope, and
   loads, stiffness or force where relevant. Reject a concept that fails even
   optimistic assumptions. Identify what needs actual modelled geometry and what
   can only be learned from a physical print; do not make every simple object
   undergo structural calculations.
2. If the deliverables and sequence are not already agreed, present viable
   options and a recommendation before detailed modelling. Explain the proposed
   print setup, consequential assumptions, tradeoffs and the few decisions the
   user must make. Options may include a complete printable design, representative
   samples followed by a selected final design, or samples only. Agree on what
   this phase will deliver and when physical feedback is needed. An explicit
   choice or authorization already in the conversation counts; do not ask again.
   Oversized objects still require the joint/load agreement above. After the
   agreement, choose routine details and complete the agreed phase autonomously.
   Seek a new decision only when evidence invalidates a consequential part of
   the agreement or the agreed phase is complete. Progress updates need no
   approval gate. At a staged handoff, request the specific physical
   observations needed for the next phase.
3. Confirm `uv` and the repository's shared
   [CadQuery command](evaluate_model.py) are available. Run `uv sync --locked`
   from the repository root when the locked environment is not installed.
4. Create or revise the object's parametric Python source. Evaluate the file
   through the shared command and inspect validity, topology, bounds, parameters and errors;
   choose views using the skill's evidence guidance.
5. Compare the geometry against the intended use and references. Check access,
   insertion, retention and release as relevant. Correct the largest functional,
   structural, ergonomic or printability discrepancies and evaluate again.
   Repair the smallest underlying cause of a build failure; simplify the approach
   if it repeatedly fails. Recalculate where measured CAD geometry changes the
   concept-screen inputs. A valid build alone does not establish function.
6. Apply the skill's CAD/export checks and final generic FDM review, including
   its final reference-slice smoke check when available. Use the shared
   evaluator's `--slice` option for ordinary final layouts so paired exports
   and the smoke check come from one command. Read its automatic-support probe
   as a request to review support placement, not a rule that supports are
   forbidden. Continue until the
   concrete review questions are resolved and further iteration is unlikely to
   materially improve the result. Distinguish CAD/slicer evidence from physical
   testing; document any remaining limitation. Export the agreed printable
   layouts and smoke-slice their matching STL files with the headless Orca helper;
   a samples-only phase does not require full-object exports.
7. Save matching print-ready exports, useful final views and one concise record
   of assumptions, print/use instructions and verification evidence. Include
   the [standard per-object print-status block](.codex/skills/cadquery-3d-design/references/physical-experiments.md#standard-per-object-print-status-record)
   for test piece(s) and the final printable object(s), using N/A when a category
   is outside the agreed phase. When a user reports a print, update the object
   block and the root model-index summary together. Add a concise entry to the
   design skill's reusable-evidence reference when a result can inform another
   model; keep the detailed evidence with its object.
8. Review, commit and push the completed work using the Git workflow below.

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

Run `./evaluate_model.py model/object_name/object_name.py` from the repository
root. Its shebang runs it through `uv run --locked`; `./evaluate_model.py --help`
lists its options and defaults. The command supplies
`__file__`, the model directory as the worker's working/import directory, and a
fresh process per evaluation. Ordinary sibling imports therefore see current
source. `result` explicitly selects the output; otherwise all `show_object()`
outputs are combined. Do not mix display-only reference geometry into the
selected printable result.

`--slice` implies `--export`. Exit status 2 means Orca completed the slice but
its report requires review; inspect `slice.review_required` and notices in the
JSON. Exit status 1 means evaluation or slicing failed. A render failure may
coexist with successful exports and a successful slice, so inspect stage status.

Use `--views none` for checks that need no images. Inspect structured error status:
a failed view can coexist with successful geometry or exports. Saved paths are
successful outputs only when their corresponding status says so. Build and
render timings are separate. Model files are trusted Python and may write their
own artifacts; the command does not roll back those side effects.

For normal printable models, deliver at least `.py`, `.step` and `.stl`.
This applies to the printable objects agreed for the current phase, including
samples; it does not require full-size variants when only samples were requested.
STEP is the primary print-ready interchange file. STL is a matching secondary
export used for the headless reference slice and compatibility. An STL-based
slice does not validate Orca's separate GUI STEP import or its tessellation.
The shared evaluator meshes its STL with Orca GUI's default STEP-import
settings: 0.003 mm absolute linear deflection and 0.5 rad angular deflection.
The two paths can still produce different triangles because Orca reopens STEP
and uses a different Open Cascade version. GUI settings may also be changed.
Use the shared evaluator for new printable exports. When an object-owned exporter
is necessary, use the evaluator's absolute STL meshing settings. Older exporters
and their artifacts are historical pairs; update the script, STEP/STL pair and
affected slice evidence together when that object is next revised, rather than
silently changing an exporter without its deliverables.
Export STEP and STL from the **same geometry and print placement**, with matching
units, orientation, bed position and relative component positions. The shared
command's `--export` writes both files named after the source; `--slice` writes
the same pair and reviews the STL with OrcaSlicer. Supply compatible
`--slice-printer`, `--slice-process` and `--slice-filament` profiles when the
agreed setup differs from the diagnostic defaults. Use an object-owned wrapper
when custom checks, naming or component exports require it.
For a position-sensitive layout, use `--slice-placement preserve`. Record any
different arrangement or compound splitting intended in Orca's GUI; the CLI
smoke slice only covers the placement it actually used.
For ordinary exports, use the evaluator's successful output status and inspect
the actual files only when a concrete export concern remains; routine STEP
reimport, STL triangle parsing and bounds comparison add little value.
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

Use renders only to answer a concrete visual question. Keep the four-view
default when it is useful; request only the needed views or `--views none` for
geometry-only checks. Use `--export` for the final pair or `--slice` for the
pair plus smoke review. Reuse saved images rather than
rebuilding merely to open them.

For valid evaluation invocations, stdout is one JSON report. The example below
is illustrative, not a required summary schema. Read only the report fields
needed for the current task; inspect diagnostics and tracebacks when a failure
needs investigation.

For visual inspection, parse the JSON inside the same outer tool call that runs
the evaluator, then read only a successful view's path. Print a compact summary
of the geometry/status, output paths, errors, timings, and versions; avoid
echoing the full report or diagnostics on success. Example `functions.exec`
workflow (use the needed views/exports and set `workdir` to the repository):

```js
let run = await tools.exec_command({
  cmd: "./evaluate_model.py model/object_name/object_name.py --views isometric,front --slice 2>/dev/null",
  workdir: "/absolute/path/to/repository",
  yield_time_ms: 30000,
  max_output_tokens: 12000,
});
let stdout = run.output;
while (run.session_id) {
  run = await tools.write_stdin({
    session_id: run.session_id,
    chars: "",
    yield_time_ms: 30000,
    max_output_tokens: 12000,
  });
  stdout += run.output;
}
const report = JSON.parse(stdout);
const summary = {
  ok: report.ok,
  file_path: report.file_path,
  geometry: report.geometry && {
    valid: report.geometry.valid,
    size_mm: report.geometry.size_mm,
    topology: report.geometry.topology,
  },
  views: (report.views ?? []).map(({ view, ok, path }) => ({ view, ok, path })),
  exports: (report.exports ?? []).map(({ path, ok }) => ({ path, ok })),
  slice: report.slice && {
    ok: report.slice.ok,
    review_required: report.slice.review_required,
    support_probe: report.slice.support_probe,
    log_notices: report.slice.log_notices,
  },
  errors: (report.errors ?? []).map(({ stage, type, message, file, line, view, path }) =>
    ({ stage, type, message, file, line, view, path })),
};
text(JSON.stringify(summary, null, 2));
if (!report.ok && report.diagnostics) text(report.diagnostics);

const view = report.views?.find((item) => item.view === "isometric" && item.ok);
if (view) {
  text(`Image path: ${view.path}`); // omit view_image when only the path is needed
  image((await tools.view_image({ path: view.path })).image_url);
}
```

The shell command returns the JSON paths, not image data. `view_image` reads the
PNG sequentially within the same outer call. Choose the view based on the
question; if no image is needed, omit image loading and request `--views none`.
A successful view can still be useful when another stage failed, so select by
the entry's `ok` status rather than the report's overall `ok` alone. A path or
status alone is not visual evidence.

## Avoid repeated work

When creating a check or requesting extra manual inspection, identify the
credible failure or uncertainty it addresses and what decision its result could
change. Ask whether existing evidence or the tool's own status already answers
it. Skip a new check when no plausible result would change the design, print
plan, delivery or handling of a consequential risk. Do not add an independent
checker merely to revalidate a toolchain guarantee without a concrete reason
to doubt it. A reusable check's expected benefit must justify its development
and maintenance; record the purpose of a non-obvious check with its result,
without creating a separate justification document.

Once a useful check is built into a reusable script or the shared workflow, run
it automatically when applicable. Repeated automatic execution is not repeated
agent work and needs no new justification each time. Judge it by its marginal
runtime and resource cost, not its invocation count. Avoid repeating manual
reasoning, tool setup or expensive checks when relevant inputs and evidence are
unchanged. If an established automatic check proves consistently uninformative,
reconsider the check itself rather than skipping it case by case.

Choose the cheapest reliable evidence for the remaining question, following the
[skill's evidence selection](.codex/skills/cadquery-3d-design/SKILL.md#proportionate-review).
Build once where possible and batch exports, measurements and needed views.
Separate cheap build assertions from expensive mechanism sweeps; rerun affected
sweeps after interface changes, not merely to obtain another view.

Reuse evidence only when its relevant inputs are unchanged and recorded:

- CAD: source modules, parameters, placement and tool versions.
- Exports: actual output files and exporter settings/version.
- Slicing: the sliced STL, effective profile, command options and slicer
  version. Do not treat that result as verification of GUI STEP import.

Changed source or output files invalidate affected checks; rerun if dependencies
are unclear. Final verification must cover the final files.
Do not introduce a caching framework for a one-off task. Unchanged helpers do not
need their own regression suites rerun for every model.

Keep one concise current decision/evidence record per object; add detailed
reports only when they answer a distinct question. Track work in the active
task checklist, but do not commit a separate completed checklist that repeats
the object's record. Preserve unique physical observations and attribution;
recover superseded process narratives from Git history when needed. Return
compact summaries and inspect full logs only for a failure or unresolved
question. Documentation-only changes need document validation, not new CAD
evaluations or slices.

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
or caches. OrcaSlicer is a separate Flatpak CLI for reference slicing. Use the
repository's [OrcaSlicer printability skill](.codex/skills/orca-slicer-printability/SKILL.md).
Do not use ad-hoc virtual environments or another environment manager.

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
