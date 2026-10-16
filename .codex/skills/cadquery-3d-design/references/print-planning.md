# Print orientation and manufacturing

## Functional process co-design

Geometry, material, orientation, nozzle/layers, perimeters, infill/local solidity
and supports are joint design variables. Prefer the cheapest adequate change
in CAD or manufacture within authorized scope; explain and agree consequential
changes before relying on them. Reorienting a flexure, adding perimeters or making its load path locally solid can be preferable to
changing its shape. Document why, then inspect actual toolpaths when the analysis
depends on that choice. Requested infill or wall count alone is not evidence of
a solid feature. Never derive quantitative modulus, strength, fatigue life or
strain limits from wall count, infill, orientation or layer height without supporting evidence.
Separate numerical uncertainty, material/process uncertainty and observations
requiring a physical print. A homogeneous-solid solve needs a defensible sliced
section, an explicit effective-material assumption, or a stated discrepancy;
even solid paths leave anisotropy and bonding uncalibrated.

For thin sandwich liners, map air-core coverage through corners, pattern ends
and floor/wall junctions before accepting straight-section witnesses as whole-liner
coverage. The [sunglasses liner corner review](../../../../model/sunglasses_case_liner/README.md#corner-coverage-investigation--2026-10-16)
found deliberately solid bends after straight-wall path checks passed. Require
explicit CAD and sliced skin/core/rib witnesses at each distinct corner/contact
region when transferring a successful damping profile to a new outline.
Verify the voids as well as the material: continuous
skins, separated support paths, remaining channel width and bridge extrusion
height at representative layers. Check whether the planned bridge extrusion
height fits the gap budget, not just its direction; inspect effective settings
and recorded extrusion heights before relying on a shallow gap. Choose any
finer layers or thin-bridge settings for the specific gap and verify their actual paths, rather than treating them as
universal TPU presets. Printed sag, spreading and clamping can still close gaps.
For S16 adaptations with ironing, consult the [scoped TPU/bridged-skin finish
lesson](../../../../model/sunglasses_case_liner/README.md#ironing-flow-print-feedback--2026-10-16)
for the user's preferred initial ironing-flow trial; check the adapted skin and
channels rather than transferring surface appearance alone.
The [I10 print report](../../../../model/tpu_damping_box/README.md#i22--i30--i10-print-feedback--latest-report)
found broken shell-side regions despite valid CAD, multiple retained paths and
no proposed support. That user now requires both skins. The precise failure
cause remains unisolated; removing a backing skin needs a new physical integrity
check, not promotion from a support-probe result.

When changing a thin enclosure's material or wall construction, review whole-shell
shape stability and handling alongside fit. Reusing an accepted mesh preserves
nominal surfaces, not the printed object's behavior: a cover can still close while
its walls bulge or move. The [TPU G and PETG vase hood reports](../../../../model/filament_swatch_box_study/README.md#tpu-damping-discontinued-2026-10-06)
illustrate that distinction without establishing a common cause or universal
wall thickness. Record physical uncertainty when it affects the intended use.

## Printability

Read the [printer/setup defaults](user-preferences.md#printer-manufacturing-and-available-hardware)
before printable dimensions are chosen: the practical envelope is per part, while
the final slice uses the selected profile for layout and print-aid acceptance.

Consider printability at both planning and review: agree on a feasible nozzle,
layer height, material and wall/infill approach, and choose an orientation before
building geometry. Inspect the actual evaluated geometry against that plan. Revisit
the plan after consequential changes and perform a final printability review;
an early intention to make the object printable is not evidence that the
finished geometry is printable.

Start with slicer-independent CAD interrogation and manufacturing reasoning.
Use measurements/sections to establish orientation, bed contact, thicknesses,
clearances, unsupported starts, horizontal projections/spans and supporting
geometry at bridge ends. These establish geometry under manufacturing assumptions,
not guaranteed physical print quality. A 2.7 mm one-sided retaining lip is an
unsupported projection without needing layer screenshots to discover it. Assess
its critical surface and reorient/redesign when appropriate; no universal safe
projection or bridge span follows from this example.

A comfortably sized, supported vertical wall needs no detailed slice to confirm
ordinary perimeters. Use math for geometry; query a real slicer for uncertain
path planning rather than recreating variable-width perimeters, gap fill, bridge
classification, seams or support-generation algorithms.

Unless the request specifies otherwise, design for FDM/FFF printing in a single
colour and material. Use the agreed print setup and
[user defaults](user-preferences.md#printer-manufacturing-and-available-hardware)
when planning feature sizes, structural sections and orientation;
the slicer profile does not make those decisions for the model. Explain and
discuss consequential changes before relying on them. Do not rely on
multi-material features or colour changes unless explicitly requested.

For a proposed split assembly, compare rough part bounds and planned print aids
against the practical envelope before detailed CAD. Estimate the load on each
candidate joint in the proposed layer direction and the full-size assembly
travel. Bed fit alone does not select a viable split or print orientation; use
the early numerical screen in [structural load paths and joint screens](design-decisions.md#structural-load-paths-and-joint-screens),
then let the final Orca slice check the selected print layout and print aids.

Choose a plausible print orientation before committing to major geometry, and revisit it as the design evolves:

* Provide a stable bed-contact surface and check the oriented dimensions against the build volume when known. Avoid unnecessary tall, slender geometry or footprints prone to lifting. Record the intended orientation and any assumed build-volume limits.
* Review downward-facing surfaces, unsupported islands, overhangs, bridges, and horizontal holes. Prefer self-supporting geometry where practical; do not assume a universal printable angle or bridge length. If supports are needed, ensure they can be accessed and removed without damaging retention features or critical surfaces. Avoid trapped support in enclosed cavities; split into separately printable parts when that materially improves manufacture and assembly.
* Size walls, ribs, pins, text, and gaps for the intended extrusion width and layer height. A 0.4 mm nozzle is not a universal minimum wall thickness or guaranteed feature resolution. When the user asks for a thin liner or compact object, reduce its overall envelope separately from local web/skin thickness; do not automatically scale both down. Preserve physically successful feature sizes where practical and choose a manufacturing margin before CAD. Prefer multiple extrusion paths for critical webs and avoid making useful material depend on a marginal single path without an explicit, scoped reason. For consequential thin features, inspect distinct paths across the section, their widths, continuity and support through representative layers/orientations. A slicer accepting the plate or retaining one path is insufficient evidence of a robust feature. Keep chosen path/width criteria object-owned; include a rejected or missing-feature control when it can show that the check detects the concern. Expose important thicknesses as parameters; do not assume infill will rescue a weak clip or thin connection. The [TPU liner correction](../../../../model/tpu_damping_box/README.md#thin-feature-rejection-and-prevention) replaced user-rejected 0.4 mm webs with 0.9 mm webs while retaining much thinner overall liners; it establishes this workflow correction, not a universal 0.9 mm minimum or printed qualification.
* Make printed identification labels prominent and use bold, generous strokes. Nominal font size is not actual capital height, stroke width or legibility. Review the exterior reading direction and relevant sliced layers at the intended nozzle/layers; verify that counters remain open and strokes remain distinct. Keep labels away from contact/fit surfaces, retain backing above recesses and account for the small bridges they create. The [TPU liner print report](../../../../model/tpu_damping_box/README.md#user-print-feedback--2026-10-16) rejected 6 mm font-size labels as too small to read despite valid CAD lettering. Its replacement uses a 12 mm bold monospaced font; that is a scoped candidate, not a universally validated minimum. Reuse the user's larger/bolder preference for comparable printed labels and leave readability physical until reported.
* Consider layer direction relative to loads, bending, and clip flexure. Avoid placing critical connections where normal use tends to separate layers. Do not assume a rigid material can flex safely: record material assumptions for clips, springs, heat exposure, or sustained loads, and adjust geometry or orientation accordingly.
* Review the complete rough geometry for orientation conflicts, including cavity closures, latch undersides and the entire footprint. Slice early only if a consequential decision depends on uncertain path generation: preservation of a thin structural stem, local solid paths, support placement, interacting print-in-place roofs/gaps, or a support-free requirement that geometry alone cannot resolve. Resolve that feature before expensive downstream analysis; an early slice still covers only its actual geometry/settings. If generic geometry establishes a comfortably feasible orientation, continue modelling without an early slice.
* Give mating and moving parts deliberate clearance rather than nominally identical dimensions. Account for orientation, hole accuracy, surface finish, and first-layer spread at bed-facing fits. Keep nominal dimensions separate from fit allowances; state whether an allowance is radial, diametral, axial, or per side. For angled mating surfaces, distinguish coordinate-direction clearance from the shortest surface-normal gap. For uncertain tight fits and other physically sensitive mechanisms, follow [optional test prints for physical validation](physical-experiments.md).
* For print-in-place mechanisms, evaluate the connected print arrangement as well as the working positions. Check captive retention, movement clearance, bed contact for each moving part, unsupported starts and roofs, and whether supports would become trapped or fuse the joint. Preserve mating-part positions in the printable export; separate-part exports are not a substitute. Distinguish no assembly from no post-processing, and document any freeing of joints or support removal. A valid CAD assembly does not establish that the mechanism will print and move successfully. Trace where each pin, socket roof and attachment first appears and how subsequent layers gain support; pin length alone is not a printability test. For a concrete support-free hinge alternative, read the [opposing conical pivot example](print-in-place-hinges.md) when designing or diagnosing a captive hinge.

After changing orientation to make one critical feature printable, inspect the
surfaces that now face downward. A printed screw placed with its drive socket
upward may leave a flat head underside as an unsupported ledge. A tapered
underside can grow outward gradually; if it bears on the assembly, model its
matching seat and recheck seated position, contact and local strength. Choose
the slope and support strategy for the actual geometry and process rather than
assuming a universal printable angle. The [book plate screw case](../../../../model/book_reading_plate/README.md#what-changed-after-the-successful-l-sample)
shows the orientation and seat tradeoff.

Use these assumptions when interpreting ambiguous requirements and judging whether a model is satisfactory. If the request calls for a different printer, nozzle, material, or manufacturing process, follow that request instead and record important assumptions where useful.

## Final review and reference smoke slice

Always record a concise final FDM rationale: intended orientation and build fit,
stable bed contact, feature/wall/gap sizing, unsupported geometry, support access
and layer direction where relevant, alongside final CAD review and export
generation.
Detailed toolpath inspection is conditional; skipping layer images does not skip
this review. State material/nozzle assumptions and remaining physical uncertainty.

For normal FDM deliverables, run one final smoke slice per agreed exported
printable layout when OrcaSlicer is available, using the
[reference review workflow](../../orca-slicer-printability/SKILL.md). For an
ordinary model source, use the evaluator's `--slice` and `--views none` options
to write the pair and perform this review in one run. Reuse an
existing slice of the same final artifact and relevant settings; do not slice
again merely to label it final. STEP is the primary print-ready file. The
headless Orca CLI cannot import STEP in the installed version, so smoke-slice
the matching exported STL and state that the result does not verify Orca's GUI
STEP import. This checks toolpath generation from the delivered design's STL
and probes whether Orca's automatic support settings generate support. Support
generation is a review signal, not proof that support is physically necessary;
no generated support is not proof that a bridge or overhang will print well.
No layer windows are required. If unavailable, record the missing smoke evidence
and complete the authorized deliverables using the available CAD review and
export generation.

Use the agreed nozzle, material and process profile when supplied and compatible
with the slicer. Otherwise use one documented diagnostic profile and state any
mismatch with the intended print setup. If the mismatch changes feature or path
behavior materially, record that setup-specific smoke evidence is missing.
Actual settings supersede reference settings for toolpath-specific claims; a
suitable final actual-profile slice also satisfies the smoke check.

The user accepts removable supports when needed, with minimal contact and easy
access for removal as the preferred strategy. Use supports only where they
solve an actual manufacturing problem; protect fit and snap contact surfaces
from removal damage. Choose interface separation and placement for the selected
material/process, then inspect the resulting support where removal is
consequential. Requested gaps do not prove light adhesion or easy removal; that
remains a physical observation. Discuss consequential support/removal tradeoffs
before detailed modelling when autonomy has not been delegated; under autonomous
scope, choose and document the cheapest adequate geometry/process combination.
Do not add multiple reference slicers to approximate an unknown setup. Escalate
only for unresolved path-generation questions, following the probe skill; actual
fit, sag, strength and mechanism feel still require physical evidence.
