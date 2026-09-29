# Print orientation and manufacturing

## Functional process co-design

Apply [AGENTS.md](../../../../AGENTS.md#co-design-geometry-and-manufacturing):
geometry and manufacturing are joint design variables. Reorienting a flexure,
adding perimeters or making its load path locally solid can be preferable to
changing its shape. Document why, then inspect actual toolpaths when the analysis
depends on that choice. Requested infill or wall count alone is not evidence of
a solid feature. Do not assign quantitative mechanical improvements without
material/process evidence. A homogeneous-solid solve needs a defensible sliced
section, an explicit effective-material assumption, or a stated discrepancy;
even solid paths leave anisotropy and bonding uncalibrated.

## Printability

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
colour and material. Use the agreed print setup and the preferences in
`AGENTS.md` when planning feature sizes, structural sections and orientation;
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
* Size walls, ribs, pins, text, and gaps for the intended extrusion width and layer height. A 0.4 mm nozzle is not a universal minimum wall thickness or guaranteed feature resolution. Prefer multiple extrusion paths for structural walls and avoid fragile single-line features unless intentional. Expose important thicknesses as parameters; do not assume infill will rescue a weak clip or thin connection.
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
Do not add multiple reference slicers to approximate an unknown setup. Escalate
only for unresolved path-generation questions, following the probe skill; actual
fit, sag, strength and mechanism feel still require physical evidence.
