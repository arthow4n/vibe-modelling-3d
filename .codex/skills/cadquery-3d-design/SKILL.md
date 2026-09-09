---
name: cadquery-3d-design
description: Design practical parametric CadQuery objects for single-material 3D printing, including fit, mechanisms, ergonomics and economical physical experiments. Use for every 3D modelling task in this repository.
---

# CadQuery 3D design

Use this skill for functional, manufacturable models. AGENTS.md owns repository
workflow, required CadQuery MCP evaluation, printer setup, attribution, artifacts
and Git rules. A valid solid or clean slice alone does not establish function.

## Modelling TODO checklist

Track design and validation checks in the object's notes or planning tool; track
commit/push completion in the active task checklist, as described in AGENTS.md.
Apply relevant items; this is not a requirement to run every evidence method.
Reopen affected checks after changes; do not repeat unrelated checks for a small revision.

- [ ] Confirm scope, references, user edits and required CAD tool availability.
- [ ] Establish use, critical dimensions, assembly/material preferences, mechanism effort and failure modes.
- [ ] Identify physical uncertainties early; plan worthwhile small experiments.
- [ ] Choose orientation, wall sizes, layer direction and support strategy.
- [ ] Build understandable parametric geometry; preserve critical interfaces.
- [ ] Evaluate source through CadQuery MCP; check bounds and topology; select useful views.
- [ ] Check insertion, load-bearing contact, retention, release effort and user access.
- [ ] Resolve significant print defects, especially on fit-critical surfaces; inspect targeted toolpaths when needed.
- [ ] Review exposed edges, corners and grip areas without weakening interfaces.
- [ ] Export STEP/STL from the same print-ready geometry and placement; verify artifacts.
- [ ] Save useful final views, assumptions, physical evidence and print instructions.
- [ ] Review and commit/push according to AGENTS.md.

Prioritize function, manufacturability, proportions and topology before cosmetic
detail. Iterate while substantial defects remain. Name dimensions and allowances;
do not mistake a parameter value for a verified measurement or physical result.

## Read the relevant reference

| Trigger | Reference |
| --- | --- |
| New requirements, assembly choices, mechanisms, motion checks, force estimates, “tight/loose” feedback | [Design decisions](references/design-decisions.md) |
| Orientation, moving parts, walls, roofs or support constraints | [Print planning](references/print-planning.md) |
| Fit, force, friction or durability needs physical validation | [Physical experiments](references/physical-experiments.md) |
| Dimensions, shared builders, modular source or edge treatment | [Parametric construction and edges](references/parametric-and-edges.md) |
| Captive hinge construction | [Opposing conical pivot example](references/print-in-place-hinges.md) |
| Final STEP/STL checks | [Export verification helper](references/export-verification.md) |

Read the relevant references during planning, not only after a failed print.
Do not load every reference for every task.

## Proportionate review

Ask: **What uncertainty remains, and what is the cheapest reliable evidence that
can resolve it?** Follow AGENTS.md's reuse and batching rules. Each additional
check or render needs a concrete unanswered question. Stop once adequate evidence
answers it; reopen only when relevant inputs change or a limitation is discovered.

Choose evidence by question, not as a mandatory sequence or universal ranking:

| Evidence | What it establishes within its assumptions |
| --- | --- |
| Deterministic CAD/geometric checks | Intersections, mating dimensions, wall/gap thickness, bounds, bed placement, engagement and motion/clearance within the checked scope |
| Slicer/toolpaths | Intended deposition for the selected profile: anchors, perimeters, surviving thin features, moving gaps, overhang formation, layer registration and footprint |
| CAD renders | Proportions, recognition, appearance, finger access, control comprehension, assembly layout and visual diagnosis |
| Analytical mechanics; selective simulation | Predicted stiffness, force, torque, strain or structural behavior under stated assumptions |
| Physical prints/tests | Actual fit, friction, effort, spring return, sag, material response, wear and subjective feel under tested conditions |

Trust an appropriate deterministic check for the geometric fact it establishes.
Do not render a series of intermediate poses to re-prove a checked hinge sweep.
Closed/open views may answer distinct access or layout questions; one collision
pose may diagnose the cause. If the calculation is suspect, improve or independently
cross-check it rather than compensate with more views. See
[design decisions](references/design-decisions.md) for motion scope and mechanics.
A clean slice does not prove physical function. Once only tactile or material
uncertainty remains, record the limit and offer a physical comparison if worthwhile;
more virtual variants or inspections cannot supply the missing observation.

Export STEP/STL together from the same geometry. Check the final pair once per
changed export set, rather than after every intermediate adjustment. This guards
against stale files and placement/export defects; it is not a second design
review or proof of shape identity. Batch meaningful sample variants and their
checks when useful, keeping each variant tied to a distinct hypothesis.

## Essential working rules

Use preferences already supplied. Ask targeted questions when missing information
changes fit, function or manufacturing; choose routine details autonomously.
Explain physical choices in plain language; use the design-decisions reference
to distinguish mechanism requirements and translate qualitative effort.

Continue the authorized full design; offer a first-print sample when it saves
meaningful material or time without losing the behavior under test.
A coupon is not a default stopping gate. Minimize material while preserving the
behavior under test, and make every variant answer an observable question.

Preserve successful interfaces during integration and reslice the full layout.
A change in surrounding stiffness or print height can matter without changing
nominal fit. Do not claim physical validation beyond actual user feedback.

For slicing, use [PrusaSlicer inspection](../prusa-slicer-printability/SKILL.md).
For export consistency, use the verification helper through a CadQuery MCP
evaluation entry point. Neither replaces function review or physical testing.
