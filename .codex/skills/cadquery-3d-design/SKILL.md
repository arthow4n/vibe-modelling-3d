---
name: cadquery-3d-design
description: Design practical CadQuery objects for single-colour 3D printing with functional and ergonomic reasoning, critical-dimension discipline, and deliberate edge treatment. Use for every 3D modelling task in this repository.
---

# CadQuery 3D design

Use this skill for every CadQuery modelling task in this repository. The repository's `AGENTS.md` remains the source for tool, artifact, dependency, and Git workflow; this skill contains the design decisions that make the resulting object practical.

## Printability

Unless the request specifies otherwise, design for single-colour printing with a typical 0.4 mm nozzle and a single material. Prefer practical wall and feature sizes, avoid details too fine to resolve reliably, provide sensible clearances, and consider overhangs, bridging, supports, orientation, and bed adhesion. Do not rely on multi-material features or colour changes unless explicitly requested.

Use these assumptions when interpreting ambiguous requirements and judging whether a model is satisfactory. If the request calls for a different printer, nozzle, material, or manufacturing process, follow that request instead and record important assumptions where useful.

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
* **Vibe dimensions** do not materially affect function, such as external proportions, decorative curvature, non-critical taper, corner radii, visual balance, and cosmetic transitions. Choose and refine these visually as needed.

Critical functional geometry takes priority over cosmetic refinement.

## Edge treatment

For everyday objects, sharp CAD edges are not finished geometry by default. Actively decide whether exposed edges should be filleted, chamfered, or intentionally left sharp. Consider edges touched by fingers or hands, insertion openings, cable slots, clips and retaining features, handles and grips, corners likely to catch on clothing or nearby objects, parts that slide against another object, mating and alignment features, exposed corners that may chip or feel unpleasant, and 3D-printed transitions that create unnecessary stress concentrations. Visible and touchable exterior corners should usually receive intentional edge treatment unless a sharp edge is functionally required.

Prefer a **fillet** when the part is touched frequently, a softer ergonomic transition or molded/product-like appearance is desirable, reducing stress concentration is useful, or a curved transition improves handling or insertion. Prefer a **chamfer** when helping one part enter another, guiding insertion or alignment, breaking a sharp edge with minimal geometry, creating a lead-in around holes, slots, pegs, sockets, or mating interfaces, or when a flat bevel better matches the intended mechanical form. Do not mechanically fillet every edge; choose treatment based on function and visual intent.

Keep edge treatment proportional to the feature. Avoid huge radii that change intended dimensions, tiny cosmetic fillets that add complexity without value, fillets that interfere with mating surfaces or reduce retention lips, clip engagement, or required clearances, and chamfers that unintentionally enlarge openings or weaken thin walls. Preserve fit, retention, and mating geometry first, then apply edge treatment around it.

## Design review

Prioritize corrections in this order:

1. intended function and physical interaction
2. critical interfaces and dimensions
3. overall proportions and bounding dimensions
4. major topology and missing geometry
5. placement and size of major features
6. secondary features
7. edge treatment, including fillets, chamfers, transitions, and intentionally sharp edges
8. cosmetic refinements

After function, critical interfaces, and major geometry are established, explicitly review edge treatment before considering the object visually finished. Inspect rendered views for raw CAD edges that make an everyday object look unfinished or ergonomically poor.

When inspecting `evaluate_file` results, infer functional and ergonomic behavior from geometry, dimensions, and rendered views; the tool does not physically simulate use. Look for insufficient access or clearance, weak or ineffective retention, insertion or removal problems, held objects slipping, falling through, detaching, or moving unintentionally, and features that visually exist but are ineffective for their intended purpose.

Before declaring the object complete, consider its intended function, critical interfaces, insertion and removal, user access, retention, likely everyday failure modes, and whether exposed and interactive edges have been deliberately reviewed for fillet/chamfer treatment, including whether any should remain sharp. Do not declare it complete while an obvious functional, ergonomic, or edge-treatment problem remains, even if the CAD model builds successfully.

## Fillet and chamfer failure handling

If a fillet or chamfer fails because of topology or an excessive radius, do not repeatedly retry arbitrary radii. Identify the problematic edge or radius, reduce the radius or apply the treatment selectively, and preserve the successful main geometry. Do not redesign a sound model solely because a cosmetic fillet fails.
