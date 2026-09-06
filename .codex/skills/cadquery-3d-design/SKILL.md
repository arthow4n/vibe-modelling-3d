---
name: cadquery-3d-design
description: Design practical CadQuery objects for single-colour 3D printing with functional and ergonomic reasoning, critical-dimension discipline, and deliberate edge treatment. Use for every 3D modelling task in this repository.
---

# CadQuery 3D design

Use this skill for every CadQuery modelling task in this repository. The intended deliverable is a functional, manufacturable 3D-printable object. The repository's `AGENTS.md` remains the source for tool, artifact, dependency, and Git workflow; this skill contains the design decisions that make the resulting object practical.

## Modelling TODO checklist

Use this checklist as the task plan when creating or substantially revising a model. Track it in the available planning tool or in `model/<object_name>/notes/checklist.md`. Mark items complete only after doing and reviewing the work; record why an item is not applicable or remains unverified. Reopen affected checks after geometry changes. For small edits, revisit the affected checks and final review without repeating unchanged work.

* [ ] **Confirm tools and scope.** Read the request and references, inspect existing object files and user edits, and confirm the customized CadQuery MCP `evaluate_file` tool is available. If it is missing, follow the stop-and-install instruction in `AGENTS.md` before modelling.
* [ ] **Define the job.** Identify intended use, physical interactions, critical interfaces, user access, insertion, retention, removal, loads, and likely everyday failure modes. For joints or moving parts, establish assembly and extra-material preferences before choosing their construction. Follow the requirements clarification guidance below, ask useful questions early, and establish what would count as a satisfactory result.
* [ ] **Set dimensions and assumptions.** Separate critical dimensions from vibe dimensions; record units, nominal sizes, fit allowances, and uncertain measurements. Expose important dimensions as named parameters and resolve uncertainty conservatively or ask when it materially changes the object.
* [ ] **Choose a print plan.** Establish material assumptions, nozzle, orientation, bed contact, build-volume constraints when known, layer direction, wall sizes, and support/removal strategy. Default to single-colour, single-material FDM with a 0.4 mm nozzle.
* [ ] **Build the main geometry.** Create or update the parametric CadQuery source inside the object's directory. Establish proportions, intended solids, and critical functional features before cosmetic details. Make the main dimensions and likely user adjustments easy to change, following the maintainable parametric design guidance below.
* [ ] **Evaluate and inspect.** Run `evaluate_file` on the source. Inspect errors, rendered views, bounding dimensions, volume/surface information, topology, and parameters. Compare with the request and references; a successful build alone does not complete this check.
* [ ] **Review function and printability.** Walk through installation, use, and removal; inspect fit, clearance, retention, access, strength, printable details, overhangs, and support access in the intended print orientation. Use the detailed guidance below and correct the largest discrepancies, then evaluate again.
* [ ] **Refine edges and details.** Deliberately choose fillets, chamfers, or sharp edges for exposed and interactive features. Preserve functional dimensions and bed contact. Re-evaluate after refinements and repeat affected function and printability checks.
* [ ] **Perform final review.** Inspect the latest views and geometry against the acceptance criteria. Confirm valid intended solids and no obvious functional, ergonomic, or printability defects. Repeat the build/evaluate/review loop while material improvements remain.
* [ ] **Export and verify deliverables.** Generate the required STEP/STL exports from the final source, check scale and mesh detail, and save useful isometric/front/top/right views. Inspect a slicer preview if available; record whether slicing and trial printing are verified or still outstanding.
* [ ] **Record and hand off.** Save print orientation, assembly instructions where needed, assumptions, and limitations inside the object's directory. Review the diff and artifacts, commit and push according to `AGENTS.md`, and summarize the final files and verification status.

## Requirements clarification

Treat the user's description as a starting point; they may not know which dimensions, interactions, or printing constraints matter. During interpretation and planning, actively look for ambiguity and invite clarification when the answer would improve fit, function, usability, or the printing approach. Do not wait for the user to volunteer technical requirements or silently choose between materially different uses.

* Ask a small set of focused questions in plain language, prioritizing the intended job, what the object must fit, how it is installed and used, and any important loads or environment. For example: “Should this clip onto the desk edge or be screwed underneath?” Explain why the distinction matters and offer a recommended option with its tradeoff when helpful.
* Help the user supply critical measurements: identify exactly what to measure and in which units, or request an available reference or product dimension. A named parameter makes an uncertain dimension editable; it does not establish that the fit is correct.
* Ask about printer, material, build size, or willingness to remove supports only when those answers affect the design. If the user does not know, explain a reasonable default and its implications rather than requiring them to choose CAD operations, tolerances, or slicer settings.
* Before choosing joints, hinges, closures, or other mechanisms, check whether the user accepts assembly and whether all working parts must be printed or purchased items such as rods, screws, nuts, magnets, or adhesives are acceptable. Use preferences already stated in the conversation; otherwise ask before committing to geometry that depends on them. Do not infer that access to a printer means access to hardware or assembly tools.
* When several mechanism approaches are feasible, briefly explain the relevant choices and establish the user's preference. For hinges, these may include print-in-place captive joints, separately printed snap-together joints or pins, flexible hinges, and hardware-based hinges. Discuss only useful alternatives, with their actual tradeoffs: printer clearance accuracy and freeing moving joints, assembly effort, bed footprint, material and fatigue limits, and durability. Recommend an approach suited to the task; do not assume print-in-place or any other mechanism is always best. Once the preference is clear, continue without asking again unless a new constraint requires changing it.
* Briefly state the interpreted use, proposed print approach, and important assumptions before committing to geometry. Separate confirmed requirements from assumptions. Proceed on low-impact visual choices and reversible defaults; wait for clarification before committing to an unresolved interface or use that would produce a materially different object. Continue independent planning while awaiting answers.
* Revisit questions if evaluation reveals an unforeseen conflict between function and printability. Avoid repeated approval requests for routine modelling decisions, and respect a user's request to proceed with reasonable assumptions while clearly identifying unverified fit or performance.

## Printability

Consider printability at both planning and review: first choose a feasible printing approach before building geometry, then inspect the actual evaluated geometry against that plan. Revisit the plan after changes and perform a final printability review; an early intention to make the object printable is not evidence that the finished geometry is printable.

For investigations using PrusaSlicer, apply the [PrusaSlicer printability notebook](../prusa-slicer-printability/SKILL.md). It records verified CLI techniques and requires agents to maintain new investigation knowledge automatically. Slicer checks supplement the CAD review; successful slicing alone does not establish printability.

Unless the request specifies otherwise, design for FDM/FFF printing in a single colour and material with a typical 0.4 mm nozzle. Do not rely on multi-material features or colour changes unless explicitly requested.

Choose a plausible print orientation before committing to major geometry, and revisit it as the design evolves:

* Provide a stable bed-contact surface and check the oriented dimensions against the build volume when known. Avoid unnecessary tall, slender geometry or footprints prone to lifting. Record the intended orientation and any assumed build-volume limits.
* Review downward-facing surfaces, unsupported islands, overhangs, bridges, and horizontal holes. Prefer self-supporting geometry where practical; do not assume a universal printable angle or bridge length. If supports are needed, ensure they can be accessed and removed without damaging retention features or critical surfaces. Avoid trapped support in enclosed cavities; split into separately printable parts when that materially improves manufacture and assembly.
* Size walls, ribs, pins, text, and gaps for the intended extrusion width and layer height. A 0.4 mm nozzle is not a universal minimum wall thickness or guaranteed feature resolution. Prefer multiple extrusion paths for structural walls and avoid fragile single-line features unless intentional. Expose important thicknesses as parameters; do not assume infill will rescue a weak clip or thin connection.
* Consider layer direction relative to loads, bending, and clip flexure. Avoid placing critical connections where normal use tends to separate layers. Do not assume a rigid material can flex safely: record material assumptions for clips, springs, heat exposure, or sustained loads, and adjust geometry or orientation accordingly.
* For a support-constrained enclosure or mechanism, evaluate and slice the complete rough geometry early, when a slicer is available, before refining local details. An orientation that helps a hinge may create an unsupported roof elsewhere. Include cavity closures, latch undersides and the entire print footprint; reconsider the overall layout when local fixes cannot meet the support requirement.
* Give mating and moving parts deliberate clearance rather than nominally identical dimensions. Account for orientation, hole accuracy, surface finish, and first-layer spread at bed-facing fits. Keep nominal dimensions separate from fit allowances; state whether an allowance is radial, diametral, axial, or per side. For angled mating surfaces, distinguish coordinate-direction clearance from the shortest surface-normal gap. For uncertain tight fits, provide a small test coupon or identify the fit as needing a trial print. Build the coupon from the same interface construction and parameters as the production part where practical; preserve print orientation, surrounding attachments that affect layer support or stiffness, and relevant slicing settings. State which behavior the coupon does and does not test.
* For print-in-place mechanisms, evaluate the connected print arrangement as well as the working positions. Check captive retention, movement clearance, bed contact for each moving part, unsupported starts and roofs, and whether supports would become trapped or fuse the joint. Preserve mating-part positions in the printable export; separate-part exports are not a substitute. Distinguish no assembly from no post-processing, and document any freeing of joints or support removal. A valid CAD assembly does not establish that the mechanism will print and move successfully. Trace where each pin, socket roof and attachment first appears and how subsequent layers gain support; pin length alone is not a printability test. For a concrete support-free hinge alternative, read the [opposing conical pivot example](references/print-in-place-hinges.md) when designing or diagnosing a captive hinge.

Use these assumptions when interpreting ambiguous requirements and judging whether a model is satisfactory. If the request calls for a different printer, nozzle, material, or manufacturing process, follow that request instead and record important assumptions where useful.

## Learning from trial prints

Record physical feedback against the tested source revision or artifact hash, interface parameters, and known material/profile settings in the object's notes. Preserve a successful baseline before changing fit; adjust clearances incrementally using the observed play or binding. A changed clearance, orientation or surrounding geometry is a new configuration: distinguish the user's successful earlier print from CAD/slicer checks of the revision. Do not generalize one successful coupon's tolerances to other printers or materials, or treat it as evidence for untested latch force or full-object strength.

## Functional design

Design functional objects around behavior and interaction, not only shape. Before creating geometry, reason about what must be held, supported, guided, blocked, connected, protected, or constrained; how an item enters or is installed; what retains it after insertion; what prevents accidental movement or release; how it is intentionally removed or adjusted; and what normal forces or disturbances it should tolerate.

Check whether the user can still grab, access, operate, plug in, unplug, or otherwise manipulate the relevant object. Account for required clearance, friction or retention, and flexibility where relevant. Identify obvious everyday failure modes.

For holders, docks, clips, mounts, adapters, organizers, and similar objects, reason through this sequence:

```text
How does the item enter?
How is it retained?
What prevents accidental release?
How is it intentionally removed?
Can the user still access or operate it?
```

A visible slot, opening, hook, or retaining feature is not enough if the held object can fall through, the opening blocks installation, retention is ineffective, or the user cannot reach the object. Avoid designs that require threading a long or attached item through a closed hole when it should be installable in place.

## Critical and vibe dimensions

Separate dimensions that control function from dimensions chosen mainly by visual judgment:

* **Critical dimensions** materially affect fit or function, such as cable diameter, device thickness, shaft diameter, mounting spacing, shelf or desk thickness, insertion clearance, retaining throat/opening, and mating diameter. Ask for these explicitly, infer them conservatively when reasonable, or expose them as named model parameters.
* **Vibe dimensions** do not materially affect function or printability, such as decorative curvature, non-critical taper, visual balance, and cosmetic transitions. External proportions and corner radii belong here only when they do not affect fit, strength, bed contact, or support requirements. Choose and refine these visually as needed.

Critical functional geometry takes priority over cosmetic refinement.

## Maintainable parametric design

Strongly prefer parameterized construction so the model is easy to maintain and revise when the user changes dimensions or requirements. Aim to make most major geometry respond to a small, understandable set of inputs rather than requiring edits throughout the construction code.

* Group clearly named, user-editable parameters near the top of the source, with units and brief comments where useful. Cover main dimensions, interfaces, thicknesses, clearances, repeated-feature counts and spacing, and meaningful edge treatments when likely to change.
* Define each independent dimension once. Derive dependent dimensions, feature positions, patterns, and symmetry from those inputs so a size change propagates consistently. Keep deliberate fixed dimensions, such as hardware interfaces or printability limits, independent where appropriate; do not blindly scale everything.
* Keep nominal dimensions and fit allowances distinct. Explain non-obvious relationships, and add simple checks for invalid combinations such as a wall thicker than the available space or a retaining opening larger than the item it must retain.
* Choose readable construction and feature selection that can tolerate expected dimension changes. Avoid scattered magic numbers, duplicated dimensions, and brittle assumptions about edge ordering where practical. When modifying an existing model, update its parameters and relationships before adding one-off geometry overrides.
* During review, check that a likely user request—such as changing width, device thickness, or hole spacing—can be handled through a small number of parameter edits. For nontrivial dependencies, evaluate a representative alternate configuration with `evaluate_file`, then restore and re-evaluate the requested configuration before final exports. State any known range restrictions; one alternate build does not prove every combination works.

Do not parameterize every incidental coordinate or introduce a general-purpose configuration framework without a benefit. Fixed local details are acceptable when they improve readability and are unlikely to need independent adjustment. Prioritize useful editability of the main design over parameter count.

## Components and shared parameters

Use multiple Python files when separating components or shared dimensions makes a model easier to construct, inspect, change, or debug. A single file with small builder functions is also appropriate; do not split files merely because an object contains several features.

* Keep one clear main entry point, such as `<object_name>.py`, that builds the final object from its components. Component modules may provide builder functions returning geometry; avoid triggering exports or unrelated work on import. Keep modules, parameters, evaluation entry points, and derived artifacts inside `model/<object_name>/`.
* A shared `parameters.py` or similarly named configuration module can hold the editable dimension table, units, and fit allowances. Give shared interfaces one source of truth and derive component dimensions from it; avoid copied parameter tables, circular imports, and mutable global state. Document the file the user should edit to change dimensions.
* Define component coordinate origins and assembly placements clearly. Build and evaluate a component independently with `evaluate_file` when that makes a difficult feature easier to inspect. Ensure evaluation entry points expose geometry in the form the tool expects, and verify local imports work through the tool without relying on an interactive session. A parameter-only module is not a geometry evaluation target.
* Bring components together early enough to check alignment, clearances, retention, interference, and the installation/removal sequence. Independently valid parts do not prove the assembled object works. Re-evaluate affected components and the final main entry point after changing shared parameters.
* Distinguish code organization from physical part separation. Separately built features intended as one printed part must form the intended connected solid. Parts intended to remain separate need individual printable exports and documented assembly placement; review each part's print orientation as well as the assembled fit. Splitting source files alone is not a reason to add physical joints.

## Edge treatment

For everyday objects, sharp CAD edges are not finished geometry by default. Actively decide whether exposed edges should be filleted, chamfered, or intentionally left sharp. Consider edges touched by fingers or hands, insertion openings, cable slots, clips and retaining features, handles and grips, corners likely to catch on clothing or nearby objects, parts that slide against another object, mating and alignment features, exposed corners that may chip or feel unpleasant, and 3D-printed transitions that create unnecessary stress concentrations. Visible and touchable exterior corners should usually receive intentional edge treatment unless a sharp edge is functionally required.

Prefer a **fillet** when the part is touched frequently, a softer ergonomic transition or molded/product-like appearance is desirable, reducing stress concentration is useful, or a curved transition improves handling or insertion. Prefer a **chamfer** when helping one part enter another, guiding insertion or alignment, breaking a sharp edge with minimal geometry, creating a lead-in around holes, slots, pegs, sockets, or mating interfaces, or when a flat bevel better matches the intended mechanical form. Do not mechanically fillet every edge; choose treatment based on function and visual intent.

Keep edge treatment proportional to the feature. Avoid huge radii that change intended dimensions, tiny cosmetic fillets that add complexity without value, fillets that interfere with mating surfaces or reduce retention lips, clip engagement, or required clearances, and chamfers that unintentionally enlarge openings or weaken thin walls. Preserve fit, retention, and mating geometry first, then apply edge treatment around it.

For handheld objects, assess broad corners, finger-contact rims and protruding mechanisms together. A tiny edge break can remove mathematical sharpness while leaving an uncomfortable overall shape; judge the scale of the treatment against how the object is gripped and carried, not merely whether fillets exist.

Review edge treatment in the chosen print orientation. A fillet on a bottom edge can reduce bed contact and introduce a difficult overhang; use a suitable chamfer or retain the bed-contact edge when appropriate. Recheck thin walls and lead-ins after edge treatment so smoothing does not make them unprintable.

## Design review

Prioritize corrections in this order:

1. intended function and physical interaction
2. feasible print orientation, material assumptions, and critical interfaces and dimensions
3. overall proportions and bounding dimensions
4. major topology and missing geometry
5. placement and size of major features
6. secondary features
7. edge treatment, including fillets, chamfers, transitions, and intentionally sharp edges
8. cosmetic refinements

After function, critical interfaces, and major geometry are established, explicitly review edge treatment before considering the object visually finished. Inspect rendered views for raw CAD edges that make an everyday object look unfinished or ergonomically poor.

When inspecting `evaluate_file` results, infer functional and ergonomic behavior from geometry, dimensions, and rendered views; the tool does not physically simulate use or establish slicer feasibility. Look for insufficient access or clearance, weak or ineffective retention, insertion or removal problems, held objects slipping, falling through, detaching, or moving unintentionally, and features that visually exist but are ineffective for their intended purpose.

Review printability throughout iteration, especially after changing orientation, wall thickness, interfaces, or edge treatment. Before completion, confirm each intended part is a valid solid, connected where intended, with no accidental zero-thickness contacts or internal geometry that obstructs printing or assembly. Check export units and scale, and ensure mesh resolution preserves useful curves and small functional features. If a slicer is available, inspect the intended orientation and profile for missing thin features, unsupported regions, support access, and bed contact. Otherwise state that printability was reviewed geometrically and slicing or trial printing remains unverified.

Before declaring the object complete, consider its intended function, critical interfaces, insertion and removal, user access, retention, likely everyday failure modes, and whether exposed and interactive edges have been deliberately reviewed for fillet/chamfer treatment, including whether any should remain sharp. Do not declare it complete while an obvious functional, ergonomic, or edge-treatment problem remains, even if the CAD model builds successfully.

Also require a plausible print plan: orientation, printable walls and details, layer-aware strength, fit allowances, and removable supports where needed. Save important printing and assembly assumptions in the object's source comments or notes. Correct obvious printability problems before completion, and distinguish design review from an actual successful print.

## Fillet and chamfer failure handling

If a fillet or chamfer fails because of topology or an excessive radius, do not repeatedly retry arbitrary radii. Identify the problematic edge or radius, reduce the radius or apply the treatment selectively, and preserve the successful main geometry. Do not redesign a sound model solely because a cosmetic fillet fails.
