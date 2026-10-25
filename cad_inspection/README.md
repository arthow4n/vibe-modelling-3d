# Reusable CAD inspections

Request named, annotated views of actual model geometry without writing another
cut/rotate/export script. Orthographic cameras, framing, sections and annotations
compose with existing assembly/check APIs. The evaluator owns execution, caching
and publication. Rendering success is not requirement acceptance or physical
validation.

## Run a view

From the repository root:

```sh
./evaluate_model.py model/circular_vent_enclosure/inspections.py --list-inspections
./evaluate_model.py model/circular_vent_enclosure/inspections.py --inspect joint-cutaway
./evaluate_model.py model/dental_travel_case/inspections.py --inspect all --output-dir renders/inspection
./evaluate_model.py model/dental_travel_case_liner/inspections.py --inspect rim-detail
```

Read JSON `available_inspections`, each `inspections[].ok`, `settings`, `evidence`
and `reused`, then **open the successful PNG** for a visual conclusion. `recipe_reused`
and `evidence_reused` separately identify retained construction/check results.
Each view
has SVG/PNG files in `<output-dir>/<source-stem>_inspections/`; selecting several
also produces `sheet.svg`/`sheet.png`. Captions and component line-color legends
are included. Annotation leaders are overlays, not visibility/contact proof.

`--inspect` repeats or accepts `all`. Listing does not call inspection factories
or generate images; it still evaluates the source's ordinary `result`. Failed
views are reported independently. An old image on disk is not a current result.
Legacy `--views front,isometric` remains compatible and shares camera frames.
Inspection image dimensions must be 200–4096 pixels to accommodate captions.

Inspection scenes may contain hardware, contents or hands: **never print/export
those scenes**. Export from the production source. Display cuts/framing do not
modify `result` or geometry used by checks.

## Declare a recipe

Keep a normal dictionary of lazy factories named `inspections` in the model
entry point. No global registry, assembly or verification plan is required for
a simple shape:

```python
from cad_inspection import Camera, Frame, Region, Section, Label, View, Inspection

def catch_detail():
    configuration = make_configuration('closed')  # existing object factory
    center = catch_center(dimensions)             # object-owned datum
    return Inspection(
        configuration,
        View(Camera((1, -2, .6), up=(0, 0, 1)),
             components=('body', 'cap'),
             frame=Frame(Region.around(center, (12, 8, 16)), margin_mm=2),
             section=Section(center, (0, 1, 0), mode='cutaway', keep='positive'),
             colors=(('body', '#1769a6'), ('cap', '#ce741c')),
             annotations=(Label(center, 'Catch'),)),
        purpose='Inspect the catch and nearby release space in the closed pose.',
        title='Closed catch', question_ids=('opening.capture',))

inspections = {'catch-detail': catch_detail}
result = make_configuration('closed').assembly()
```

Names use letters/digits/underscores/hyphens; `sheet` and `all` are reserved. Factories return
`Inspection` or `CheckedInspection` and run only when selected. Derive anchors
from current parameters/builders, rather than saved pixels or unstable face
indices. A missing selected component fails explicitly. Object-owned datum
functions may serve checks and pictures; independent acceptance/reference
fixtures must still protect against a shared mistaken assumption.

| Primitive | Contract |
| --- | --- |
| `Camera(direction, up)` | Direction **from subject toward viewer**; world upright reference. Finite nonzero/nonparallel vectors required. |
| `Camera.named(name)` | Eight established orthographic presets. |
| `Camera.look_at(eye, target, up=...)` | Derives direction; framing stays independent. No perspective/depth of field. |
| `Frame(region=None, margin_mm=2)` | Fit whole displayed subject or projected world-space region, with physical margin. Image clipping never creates solid cut faces. |
| `Region(minimum, maximum)` / `.around(center, size)` | World-space box, or component-local box with `component=...`; projects all eight corners. |
| `Section(origin, normal, mode, keep)` | `planar` contours or `cutaway` solid retaining the `positive`/`negative` normal side. `keep` is irrelevant to planar mode. |
| `View.components` | Exact assembly paths; empty selects all. A plain shape is named `subject`. |
| `View.colors` | Selected-component line colors. Shared-scene hidden-line removal preserves cross-component occlusion; no shaded material renderer. |
| `Label(point, text, offset_px)` | Model-space anchor, pixel-space text displacement. |
| `Anchor(component, point)` | Point in a component's authored frame, transformed through its existing assembly placement. Labels/arrows accept anchors; `Region.around(anchor, size)` makes framing/highlights follow the part. |
| `Arrow(start, end, text)` | Model-space endpoints, optional caption. |
| `Highlight(region, text)` | Projected region rectangle; an overlay, not a selected face. |

Subjects may be Shapes, Workplanes, native unconstrained Assemblies or stable
`assembly_geometry.Configuration` snapshots. Resolve constraints upstream. Exact
paths distinguish hierarchical/repeated instances. Recipes contain resolved data,
not serialized callbacks or implicit persistent topology names.

`settings.view` in the SVG metadata or JSON receipt is a resolved JSON-compatible
recipe (including annotation kinds). It can be reused as a quick spec's `view`;
parameter-dependent anchors should remain in the object's Python factory.

For a moving part, for example, use `Label(Anchor('cap', local_catch), 'Catch')`
and `Frame(Region.around(Anchor('cap', local_catch), (12, 8, 16)))`. The existing
assembly placement supplies rotation/translation, including ancestor/root poses.
The authored frame includes any placement already baked into the part builder;
it is not automatically the part centroid. No second component tree is created.
JSON points may likewise be `{"component": "cap", "point": [0, 0, 12]}`.

Empty sections fail. Wholly removed components appear in `removed_by_section`;
all removed fails. Frames outside projected subject bounds fail; bounds overlap
does not guarantee feature visibility. Inspect the image and change camera or
section when line drawings remain ambiguous. Annotations can point to hidden or
sectioned-away positions; they are overlays, not proof of accessibility.

## Quick JSON views

Supply `--view-spec FILE.json --inspect detail`. The file becomes a declared
input; the view uses the source's `result`, preserving native assembly names:

```json
{
  "detail": {
    "purpose": "Inspect the inside wall at the seam",
    "view": {
      "camera": {"direction": [1, -2, 0.5], "up": [0, 0, 1]},
      "frame": {"region": {"minimum": [20, -5, 30], "maximum": [35, 5, 45]}, "margin_mm": 2},
      "section": {"origin": [0, 0, 0], "normal": [0, 1, 0], "mode": "cutaway", "keep": "positive"},
      "annotations": [{"kind": "label", "point": [25, 0, 35], "text": "Seam"}]
    }
  }
}
```

`camera` may be a preset string; optional `components`, `colors` (JSON object),
`show_hidden`, `title`, and `question_ids` follow the Python contract. Unknown
fields and duplicate names are errors. Move repeated recipes into object Python
so anchors follow parameter changes. `--show-hidden` controls legacy views;
named recipes explicitly own `show_hidden`.

## Compose with engineering evidence

`pair_inspection(configuration, first, second, requirement, view=..., purpose=...)`
runs the existing complete-geometry pair check and returns `CheckedInspection`:
`.inspection` is the display recipe, `.answer` is the native `PairResult`, usable
directly by assertions or `product_verification.engineering_evidence()`. The view
includes status and an unsigned-gap arrow when closest points are available.
Witnesses are not contact patches, penetration depths or collision locations.
An illustrated failed/inconclusive check can still render successfully:
`inspections[].ok` describes rendering; read `evidence.status` for the native
engineering outcome. Its status never changes merely because a picture exists.

`motion_inspection(configuration, moving, obstacle, requirement, samples=...,
transform=..., parameter=..., units=..., select=..., view=..., purpose=...)`
checks the path once. `select` is a checked sample or `'first_unsuccessful'`;
the latter raises if all pass. It replays the exact recorded native pose without
calling the transform callback again, preserving hierarchy/root transforms and
other components. `.answer` is the native `MotionResult`; `.selected_sample`
identifies the illustration. Sampled success never means continuous clearance.
Only the selected node's geometry moves, including when that node has children;
descendants keep their checked world poses. Solved snapshots are accepted, but
the display copy discards source constraint declarations rather than re-solving
them. Source constraints/resolution and descriptive parameters remain preserved.

Both adapters calculate on complete geometry **before** display sections.
They do not attach arbitrary old results to new geometry. A shared object factory
can serve a checker and its diagnostic recipe; numerical checking must not
require rendering. `question_ids` are descriptive links, not requirements or
automatic coverage. Existing verification `Evidence.reference` can link an
inspection image/receipt without new verification CLI flags or implicit I/O.

Human-interaction scenes may supply positioned CAD/reference geometry and
model-space skin/contact points or outward-normal arrows. Keep simulator-to-CAD
units/frames and anatomy/proxy provenance in the object adapter. This renderer
does not import MuJoCo/MyoSim, validate a grasp or replace native collision checks.
Existing simulator outline/deformation plots remain appropriate.

## Identity and qualification

`--reuse` retains lazy results only under the evaluator's existing deterministic,
closed-input declaration. Non-Python assets/state require `--dependency` or an
execution declaration; unknown/stateful factories stay fresh. Subject geometry,
resolved settings, annotations, check results, runtime and implementation identify
image artifacts. `--fresh` bypasses reuse. Image reuse does not mean fresh checking
or fresh visual review. Reconstructed kernel geometry need not serialize identically;
cache misses are conservative, not evidence of changed engineering behavior.
Warm geometry/recipe retention inherits the execution layer's bounded idle-worker
capacity and lifetime. A later request may rebuild geometry even when its images
are reusable; this framework does not add a second geometry cache.

Existing `ArtifactCache`, staging, source guards and destination ownership apply.
Publication from the same source/inspection directory is serialized. A changed
input during evaluation prevents publication. SVG metadata/JSON retain resolved
settings and geometry hashes. `render()` returns `(SVG bytes, settings)` and
`sheet()` composes SVGs in memory; neither writes files or runs checks.
Managed outputs, including dynamic inspection names and reports, cannot replace
the source or a declared input, or write into a declared input directory. The
publication boundary checks the complete output set before publishing any file.

[Tests](../tests/test_cad_inspection.py) cover independent known sections/volumes,
camera raster orientation, off-center framing, shared-scene occlusion, hierarchical
motion replay, annotations, sheet ID isolation and managed discovery/reuse/export
behavior. Real object recipes exercise installed hardware, layered liners and
small catch details without revising printable geometry. Historical drawings
remain preserved.

Qualified on Python 3.14.7 / CadQuery 2.8.0: **323 tests passed**, covering the
inspection/evaluator boundary, assembly geometry, execution/telemetry and product
verification. All three object sheets were generated and visually inspected.
Regressions cover solved-snapshot replay, geometry-bearing root/nested parents
with fixed descendants, and input collisions across inspection, sheet, legacy
view, export and report publication. An independent blind review identified the
two replay defects; fix verification found no further actionable issues.
After correcting the volatile `CODEX_TOOL_CALL_ID` identity input, a separate
coding-agent tool call reused the vent's geometry, all three lazy recipes and all
three images. Ordinary model environment changes still invalidate identity.

| Consumer | Concrete reuse |
| --- | --- |
| Vent joint | Same installed assembly/hardware; camera, local anchor, frame and section replace the special rotated/cropped inspection pose. |
| Historical dental C2 | Whole, seam and catch sections share actual component builders and section/annotation primitives; existing explanatory drawings stay intact. |
| Current uniform L20 liner | Installed and rim-detail views share the real rigid/TPU scene, without rotating product geometry toward a fixed camera. |

The C2/liner sheets remain applicable across the bookkeeping-only environment
identity correction: their builders, recipes, rendering implementation and tool
versions did not change. Delivered SVG metadata was checked against each native
receipt. This does not refresh any product's physical or manufacturing evidence.
The replay/publication fixes also leave these static example renderings unchanged.

Initial implementation attribution: GPT-6-based Codex (exact variant/reasoning
effort not exposed), OpenAI, shared-workspace Codex agent; no subagents.
Follow-up fixes include an independent fresh-context Codex code review; its exact
model variant/reasoning effort is not exposed.
