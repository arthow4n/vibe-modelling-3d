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
physical plate dimensions. Allow for likely brims/supports in the rough plan,
and check each oriented axis independently. Let the final Orca slice decide
whether its actual print aids fit. For OrcaSlicer reviews, take the
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

The user also has an on-hand screw and nut assortment
([Jula assortment 002837](https://www.jula.se/catalog/bygg-och-farg/infastning/sortimentsatser/skruvsatser/skruv-muttersats-002837/))
that should be preferred whenever screw or bolt fasteners are needed:
- **Machine screws (maskinskruvar):**
  - M3 × 10 mm (60 pcs)
  - M3 × 12 mm (60 pcs)
  - M4 × 10 mm (50 pcs)
  - M4 × 12 mm (35 pcs)
  - M4 × 25 mm (25 pcs)
  - M5 × 20 mm (25 pcs)
  - M5 × 30 mm (20 pcs)
  - M6 × 12 mm (25 pcs)
  - M6 × 20 mm (18 pcs)
  - M6 × 30 mm (12 pcs)
- **Nuts (muttrar):**
  - M3 (120 pcs)
  - M4 (110 pcs)
  - M5 (45 pcs)
  - M6 (55 pcs)

During planning, if fasteners are useful, discuss with the user whether they
prefer a fully printed design or whether using this stock hardware is
acceptable. If the user explicitly requests full autonomous implementation, use
best engineering judgment; using these available stock materials is allowed.

Do not reject an object merely because its assembled size exceeds that envelope.
Plan it as multiple printable parts when no acceptable orientation fits. Before
committing to the split and joint geometry, establish with the user the required
joint strength, relevant loads and directions, acceptable hardware/adhesive,
permanent versus demountable assembly, and any safety consequences. Recommend a
feasible joint strategy and explain its tradeoffs; do not silently assume that a
simple alignment or friction joint is structurally adequate. Plan each part for
the practical envelope; let the final slice check its selected print layout and
generated print aids. Verify the assembled interfaces and load path separately.

## Co-design geometry and manufacturing

The functional FDM object includes geometry, material, orientation, nozzle/layer
setup, perimeters, infill or locally solid regions, supports and consequential
process choices. Agents may recommend or revise any of these within the user's
authorized scope when that improves function; normal settings are starting
points. Explain consequential choices and follow existing design-agreement rules.
Prefer the cheapest adequate change, whether in CAD or manufacture.

Use the evidence loop: design → cheap engineering checks → numerical analysis
only for unresolved physical questions → manufacturing strategy → actual slice
review → physical validation. Revisit geometry or process as evidence changes.
When slicer settings affect an engineering decision, inspect the resulting paths,
not just requested settings. Do not routinely inspect paths for ordinary walls.

Never derive quantitative modulus, strength, fatigue life or strain limits from
wall count, infill, orientation or layer height without supporting evidence.
For homogeneous-solid analysis, make the relevant load-bearing feature reasonably
solid in the actual slice, document an explicit effective-material assumption,
or record the mismatch as uncertainty. Solid toolpaths do not establish isotropy,
layer bonding or bulk material properties. Separate numerical uncertainty,
material/process uncertainty and observations requiring a physical print.

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
   through the shared command and inspect validity and errors. Read named
   dimensions in the source or object notes; use targeted CAD measurements for
   geometry questions that planning cannot settle. Choose views using the
   skill's evidence guidance.
5. Compare the geometry against the intended use and references. Check access,
   insertion, retention and release as relevant. Apply the skill's
   [whole-object form and handling review](.codex/skills/cadquery-3d-design/references/design-decisions.md#whole-object-form-and-handling)
   to rough complete geometry before expensive analysis. Correct the largest functional,
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
   testing; document any remaining limitation. A samples-only phase does not
   require full-object exports.
7. Save matching print-ready exports, useful final views and one concise record
   of assumptions, print/use instructions and verification evidence. Include
   the [standard per-object print-status block](.codex/skills/cadquery-3d-design/references/physical-experiments.md#standard-per-object-print-status-record)
   for test piece(s) and the final printable object(s), using N/A when a category
   is outside the agreed phase. When a user reports a print, update the object
   block and the root model-index summary together. Add a concise entry to the
   design skill's reusable-evidence reference when a result can inform another
   model; keep the detailed evidence with its object.
8. Review, commit and push the completed work using the Git workflow below.

## Trust each stage for the question it answers

| Stage | Establish here | Trust afterward; do not repeat routinely |
| --- | --- | --- |
| Planning | Agree on the print setup and deliverable; screen rough fit, print envelope, assembly travel and relevant loads before detailed CAD. | Do not model or slice merely to discover that the concept fails simple math. |
| CAD | Build valid geometry; use specific assertions or measurements for consequential fit, motion, access and structure questions. Use views for visual questions. | A generic bounds or solid-count report is not a check against design intent. Do not add one without an expected result and decision it could change. |
| Export | Write STEP and STL from the same selected print geometry and check each export's status. | Trust successful conversion unless a concrete defect suggests otherwise; do not routinely reimport STEP, parse STL triangles or compare exported bounds. |
| Orca slice | Under the selected effective printer, process, filament and placement, check completion, notices and the automatic-support signal. | Trust Orca's acceptance of that print layout for printer fit, including generated brims/supports. Do not repeat its envelope decision with CAD bounds or a G-code reader. Generated support calls for targeted review, not automatic redesign. |
| Physical print | Check actual fit, friction, bridge quality, strength, comfort and material response where they matter. | CAD and slice success do not establish these physical outcomes. |

Trust applies only to the checked source or artifact, orientation, placement,
profile and tool version. A diagnostic profile that differs from the agreed
setup cannot establish printer fit for the agreed setup. Revisit a stage when
relevant inputs change or a specific failure creates a reason to doubt its
result. A successful STL smoke slice does not verify Orca's separate GUI STEP
import. Keep targeted checks for questions outside the earlier stage's scope;
do not create generic checkers to reprove an upstream tool's successful status.

These omissions are deliberate. The shared evaluator does not report routine
CAD bounds, size, volume, solid count or per-solid measurements. The workflow
does not routinely reopen STEP, audit STL triangles or edges, compare STEP/STL
bounds, or parse G-code motion and deposited footprint. Do not recreate those
outputs through object scripts, new tests, extra renders or manual calculations
merely because they are available. An exception needs a concrete suspected
failure, an expected result, a decision that would change with that result, and
a reason the planning work or responsible tool's own status cannot answer it.
Keep a justified check specific to that question; add it to the shared workflow
only after it has demonstrated recurring value.

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

Keep handling-review hands, held-item envelopes and supporting surfaces in an
inspection-only entry point when needed, reusing the object's component builders.
Render it without `--export` or `--slice`; the ordinary print entry point must
select only the intended printable geometry.

`--slice` implies `--export`. Exit status 2 means Orca completed the slice but
its report requires review; inspect `slice.review_required` and notices in the
JSON. Exit status 1 means evaluation or slicing failed. A render failure may
coexist with successful exports and a successful slice, so inspect stage status.
Use `--slice-existing FILE.stl` (or `.3mf`) to review an existing export without
rebuilding CAD; the same slice profile and placement options apply.

Use `--views none` for checks that need no images. Inspect structured error status:
a failed view can coexist with successful geometry or exports. Saved paths are
successful outputs only when their corresponding status says so. Build and
slice timings are reported separately. Model files are trusted Python and may write their
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

The shared renderer uses Z upright for side/isometric views and Y upright for
top/bottom views; each successful view reports its camera directions. Camera
orientation changes only the image. Print placement comes from the selected
source geometry, while an assembled inspection entry point can use a different
pose. Images made before the camera-up correction may appear tilted or sideways;
do not infer their print orientation from the screen's vertical direction.

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

## Improve shared tools from concrete needs

Agents are welcome to autonomously improve the repository's shared APIs, tools
and workflow while completing an authorized task. This includes the evolving
physical-analysis API; its current capabilities are a foundation, not a frozen
interface or a requirement to use simulation for every model. Routine reusable
improvements need no separate permission. Keep them within the task's purpose;
seek a decision if they would materially change the agreed deliverable or scope.

Let an actual consumer drive an extension: repeated manual work, a demonstrated
failure, or a concrete design question that existing tools cannot answer well.
Before adding shared functionality, identify the decision it will inform and
the operation that can transfer to other models without their specific geometry
or dimensions. A second consumer is useful evidence, not a prerequisite when
the reusable need is already clear. Prefer improving an existing abstraction;
keep object-specific fixtures, assumptions and experiments in the object directory.
Do not add speculative frameworks, duplicate established checks, or generalize
merely because something could someday be useful.

Use the cheapest adequate evidence: CAD for rigid fit and clearance, simple
calculations for suitable load screens, and numerical analysis when deformation,
contact or geometry makes those approaches insufficient or materially uncertain.
Do not run analysis merely to demonstrate the API. When extending a shared tool,
exercise it on the motivating task, validate the new behavior proportionately
(numerical benchmarks for new physical-analysis capabilities), and document its
contract and limits. Retain explicit unsupported/failure outcomes; solver
completion must not become a claim of physical validation. Feed useful fixes
back into the shared tool rather than copying solver plumbing into each model.

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

Keep one concise current decision/evidence record per object. State shared
print/use instructions and assumptions once; for multiple variants, use a
compact comparison and record only their consequential differences and specific
evidence. Update this structure as variants are added instead of appending
repeated handoff sections. Keep deliverable links, relevant verification and
physical results, the standard print-status block, and attribution easy to find.
Add detailed reports only when they answer a distinct question. Track work in
the active task checklist, but do not commit a separate completed checklist that repeats
the object's record. Preserve unique physical observations and attribution;
recover superseded process narratives from Git history when needed. Return
compact summaries and inspect full logs only for a failure or unresolved
question. Documentation-only changes need document validation, not new CAD
evaluations or slices.

For numerical studies, use generated summaries as the source for tables and keep
prose focused on the decision and limits; do not hand-maintain the same history in
several records. Retain successful and informative failed runs with the shared
[analysis evidence helper](physical_analysis/README.md#retain-analysis-evidence)
instead of copying archive/solver-file handling into each model. Model-specific
acceptance conditions and interpretation remain with the object.

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
