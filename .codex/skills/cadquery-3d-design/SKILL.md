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
Reopen affected checks after changes; do not repeat unrelated checks for a small revision.

- [ ] Confirm scope, references, user edits and required CAD tool availability.
- [ ] Establish use, critical dimensions, assembly/material preferences and failure modes.
- [ ] Identify physical uncertainties early; plan worthwhile small experiments.
- [ ] Choose orientation, wall sizes, layer direction and support strategy.
- [ ] Build understandable parametric geometry; preserve critical interfaces.
- [ ] Evaluate source through CadQuery MCP; inspect views, bounds and topology.
- [ ] Check insertion, load-bearing contact, retention, release and user access.
- [ ] Resolve significant print defects, especially on fit-critical surfaces; inspect sliced layers.
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
| New requirements, assembly choices, mechanisms, subjective “tight/loose” feedback | [Design decisions](references/design-decisions.md) |
| Orientation, moving parts, walls, roofs or support constraints | [Print planning](references/print-planning.md) |
| Fit, force, friction or durability needs physical validation | [Physical experiments](references/physical-experiments.md) |
| Dimensions, shared builders, modular source or edge treatment | [Parametric construction and edges](references/parametric-and-edges.md) |
| Captive hinge construction | [Opposing conical pivot example](references/print-in-place-hinges.md) |
| Final STEP/STL checks | [Export verification helper](references/export-verification.md) |

Read the relevant references during planning, not only after a failed print.
Do not load every reference for every task.

## Proportionate review

Follow AGENTS.md's reuse and batching rules. Give each additional review a
concrete question (collision, engagement, fit, manufacturability or ergonomics)
and stop when the evidence answers it. Reopen affected questions after changes,
not the entire review by default. Extra renders cannot establish holding force,
droop or feel; use a physical experiment when that is the remaining uncertainty.

Export STEP/STL together from the same geometry. Check the final pair once per
changed export set, rather than after every intermediate adjustment. This guards
against stale files and placement/export defects; it is not a second design
review or proof of shape identity. Batch meaningful sample variants and their
checks when useful, keeping each variant tied to a distinct hypothesis.

## Essential working rules

Use preferences already supplied. Ask targeted questions when missing information
changes fit, function or manufacturing; choose routine details autonomously.
Explain physical choices in plain language. Distinguish play, holding force,
movement friction and deliberate release effort when interpreting “tight.”

Continue the authorized full design while offering economical first-print samples.
A coupon is not a default stopping gate. Minimize material while preserving the
behavior under test, and make every variant answer an observable question.

Preserve successful interfaces during integration and reslice the full layout.
A change in surrounding stiffness or print height can matter without changing
nominal fit. Do not claim physical validation beyond actual user feedback.

For slicing, use [PrusaSlicer inspection](../prusa-slicer-printability/SKILL.md).
For export consistency, use the verification helper through a CadQuery MCP
evaluation entry point. Neither replaces function review or physical testing.
