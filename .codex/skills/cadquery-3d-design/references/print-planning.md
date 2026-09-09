# Print orientation and manufacturing

## Printability

Consider printability at both planning and review: first choose a feasible printing approach before building geometry, then inspect the actual evaluated geometry against that plan. Revisit the plan after changes and perform a final printability review; an early intention to make the object printable is not evidence that the finished geometry is printable.

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

Unless the request specifies otherwise, design for FDM/FFF printing in a single colour and material with a typical 0.4 mm nozzle. Do not rely on multi-material features or colour changes unless explicitly requested.

Use the confirmed printer setup in the repository's `AGENTS.md` when present; it takes precedence over generic printer assumptions.

Choose a plausible print orientation before committing to major geometry, and revisit it as the design evolves:

* Provide a stable bed-contact surface and check the oriented dimensions against the build volume when known. Avoid unnecessary tall, slender geometry or footprints prone to lifting. Record the intended orientation and any assumed build-volume limits.
* Review downward-facing surfaces, unsupported islands, overhangs, bridges, and horizontal holes. Prefer self-supporting geometry where practical; do not assume a universal printable angle or bridge length. If supports are needed, ensure they can be accessed and removed without damaging retention features or critical surfaces. Avoid trapped support in enclosed cavities; split into separately printable parts when that materially improves manufacture and assembly.
* Size walls, ribs, pins, text, and gaps for the intended extrusion width and layer height. A 0.4 mm nozzle is not a universal minimum wall thickness or guaranteed feature resolution. Prefer multiple extrusion paths for structural walls and avoid fragile single-line features unless intentional. Expose important thicknesses as parameters; do not assume infill will rescue a weak clip or thin connection.
* Consider layer direction relative to loads, bending, and clip flexure. Avoid placing critical connections where normal use tends to separate layers. Do not assume a rigid material can flex safely: record material assumptions for clips, springs, heat exposure, or sustained loads, and adjust geometry or orientation accordingly.
* Review the complete rough geometry for orientation conflicts, including cavity closures, latch undersides and the entire footprint. Slice early only if a consequential layout decision depends on uncertain path generation: support placement, interacting print-in-place roofs/gaps, or a support-free requirement that geometry alone cannot resolve. If generic geometry establishes a comfortably feasible orientation, continue modelling without an early slice.
* Give mating and moving parts deliberate clearance rather than nominally identical dimensions. Account for orientation, hole accuracy, surface finish, and first-layer spread at bed-facing fits. Keep nominal dimensions separate from fit allowances; state whether an allowance is radial, diametral, axial, or per side. For angled mating surfaces, distinguish coordinate-direction clearance from the shortest surface-normal gap. For uncertain tight fits and other physically sensitive mechanisms, follow [optional test prints for physical validation](physical-experiments.md).
* For print-in-place mechanisms, evaluate the connected print arrangement as well as the working positions. Check captive retention, movement clearance, bed contact for each moving part, unsupported starts and roofs, and whether supports would become trapped or fuse the joint. Preserve mating-part positions in the printable export; separate-part exports are not a substitute. Distinguish no assembly from no post-processing, and document any freeing of joints or support removal. A valid CAD assembly does not establish that the mechanism will print and move successfully. Trace where each pin, socket roof and attachment first appears and how subsequent layers gain support; pin length alone is not a printability test. For a concrete support-free hinge alternative, read the [opposing conical pivot example](print-in-place-hinges.md) when designing or diagnosing a captive hinge.

Use these assumptions when interpreting ambiguous requirements and judging whether a model is satisfactory. If the request calls for a different printer, nozzle, material, or manufacturing process, follow that request instead and record important assumptions where useful.

## Final review and reference smoke slice

Always record a concise final FDM rationale: intended orientation and build fit,
stable bed contact, feature/wall/gap sizing, unsupported geometry, support access
and layer direction where relevant, alongside final CAD and export validation.
Detailed toolpath inspection is conditional; skipping layer images does not skip
this review. State material/nozzle assumptions and remaining physical uncertainty.

For normal FDM deliverables, run one final smoke slice per exported printable
layout when PrusaSlicer is available, using the
[reference probe workflow](../../prusa-slicer-printability/SKILL.md). Reuse an
existing slice of the same final artifact and relevant settings; do not slice
again merely to label it final. This checks acceptance of the actual exported
mesh by an independent manufacturing toolchain, not universal printability.
No layer windows are required. If unavailable, record the missing smoke evidence
and complete the authorized deliverables using the available CAD/export review.

Use one documented diagnostic profile unless the user's actual slicer/profile
is supplied. Actual settings supersede reference settings for toolpath-specific
claims; a suitable final actual-profile slice also satisfies the smoke check.
Do not add multiple reference slicers to approximate an unknown setup. Escalate
only for unresolved path-generation questions, following the probe skill; actual
fit, sag, strength and mechanism feel still require physical evidence.
