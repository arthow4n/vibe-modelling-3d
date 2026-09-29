---
name: cadquery-3d-design
description: Design practical parametric CadQuery objects for single-material 3D printing, including fit, mechanisms, ergonomics and economical physical experiments. Use for every 3D modelling task in this repository.
---

# CadQuery 3D design

Use this skill for functional, manufacturable models. AGENTS.md owns repository
workflow, shared CadQuery command, printer setup, attribution, artifacts
and Git rules. A valid solid or clean slice alone does not establish function.

## Modelling TODO checklist

Track active design and validation checks in a planning tool or working notes;
save decisions and evidence in the object's primary notes without a duplicate
completed checklist. Track commit/push completion in the active task checklist,
as described in AGENTS.md.
Apply relevant items; this is not a requirement to run every evidence method.
Reopen affected checks after changes; avoid repeating unrelated manual or
expensive reviews for a small revision. Established automatic checks can run
with each applicable evaluation.

- [ ] Confirm scope, references, user edits, known preferences and required CAD tool availability; check the reusable-model evidence for an analogous design.
- [ ] Establish use, critical dimensions, assembly/material preferences, operating effort, required retention and failure modes; screen consequential tolerance extremes together.
- [ ] Screen the concept with rough fit, engagement, assembly-travel and print-envelope calculations as relevant. For structurally important parts and joints, estimate loads, stiffness and force before detailed CAD; reject an infeasible concept early.
- [ ] Recommend viable deliverables and a print setup, explain tradeoffs, and agree on this phase's sequence if it is not already established.
- [ ] Decide which remaining questions require modelled geometry and which require a physical print. For an oversized assembly, resolve segmentation and joint/load requirements with the user before finalizing it.
- [ ] Co-design geometry, material, orientation, nozzle/layers, perimeters, infill/local solidity and supports; revise either CAD or process using the cheapest adequate evidence. Inspect actual sliced paths when a mechanical assumption depends on them; never infer calibrated material properties from settings. Plan physical experiments for remaining uncertainty.
- [ ] Build understandable parametric geometry; preserve critical interfaces.
- [ ] Evaluate source through the shared CadQuery command; inspect build validity and errors, then select views or targeted geometry checks for unresolved questions.
- [ ] Check insertion, load-bearing contact, retention, release effort and user access.
- [ ] For structurally important parts and joints, update the load and stiffness screen using measured CAD sections before recommending a structural trial.
- [ ] When contact analysis is needed, use the [decision-driven study guidance](../../../physical_analysis/README.md#plan-a-contact-study) and connect local fixture/deformation evidence to the surrounding assembly.
- [ ] Review final generic FDM geometry and resolve significant defects, especially on fit-critical surfaces.
- [ ] Review exposed edges, corners and grip areas without weakening interfaces.
- [ ] Export the agreed printable layouts as STEP/STL from the same print-ready geometry and placement; check output status and any specific export concern.
- [ ] Run/reuse the final reference smoke slice for those layouts when available; investigate detailed paths only for unresolved slicer-sensitive questions.
- [ ] Save useful final views, assumptions, physical evidence and print instructions.
- [ ] Record separate print status for test piece(s) and any final printable object in the object's notes; use N/A when a category is outside the agreed phase and do not infer a physical print from CAD or slicer output.
- [ ] Add a reusable-evidence entry only if this work produced a transferable result; link to its detailed object record.
- [ ] Review and commit/push according to AGENTS.md.

Prioritize function, manufacturability, proportions and topology before cosmetic
detail. Iterate while substantial defects remain. Name dimensions and allowances;
do not mistake a parameter value for a verified measurement or physical result.

## Read the relevant reference

| Trigger | Reference |
| --- | --- |
| New requirements, assembly choices, load-bearing joints, mechanisms, motion checks, force estimates, “tight/loose” feedback | [Design decisions](references/design-decisions.md) |
| Generic FDM review, final smoke slice, orientation, moving parts or support constraints | [Print planning](references/print-planning.md) |
| Fit, force, friction or durability needs physical validation | [Physical experiments](references/physical-experiments.md) |
| Dimensions, shared builders, modular source or edge treatment | [Parametric construction and edges](references/parametric-and-edges.md) |
| Captive hinge construction | [Opposing conical pivot example](references/print-in-place-hinges.md) |
| A similar model or a transferable physical result | [Reusable model evidence](references/reusable-model-lessons.md) |

Read the relevant references during planning, not only after a failed print.
Do not load every reference for every task.

## Early comparison for aesthetic alternatives

When the user requests visually distinct alternatives, compare inexpensive
silhouettes or rough forms before detailed CAD and exports. Choose views that
reveal the requested differences; include the held object or use context when
it affects visibility, and use a common scale when comparing proportions.
Look for differences in overall shape, open space and support arrangement;
surface details or cutouts alone may not satisfy a request for distinct styles.
Revise repetitive concepts at this stage while preserving the functional
constraints and screening rough print feasibility.

Share the comparison early. Treat it as a design review within the agreed
scope, not an automatic approval gate: continue autonomously when authorized,
and complete the agreed deliverables. Use physical samples when material,
texture or finish is the deciding uncertainty; silhouettes cannot establish
those outcomes. This comparison is conditional on aesthetic exploration,
not a required stage for every model.

## Proportionate review

Ask: **What uncertainty remains, what would the result change, and what is the
cheapest reliable evidence that can resolve it?** Apply AGENTS.md's check-value,
reuse and batching rules when choosing new checks or extra manual reviews. Omit
them when either outcome would lead to the same action. Established automatic
checks can run routinely without a fresh decision each time. Stop extra review
once adequate evidence answers the question; reopen it when relevant inputs
change or a limitation is discovered.
Use approximate concept calculations before committing to CAD when they can
reject a weak approach. Use the evaluated model for exact geometry that the
approximation cannot establish, and physical prints for material or tactile
behavior. A changed CAD section warrants an updated calculation, not a restart
of every earlier check.

Choose evidence by question, not as a mandatory sequence or universal ranking:

| Evidence | What it establishes within its assumptions |
| --- | --- |
| Deterministic CAD/geometric checks | Intersections, mating dimensions, wall/gap thickness, engagement and motion/clearance within the checked scope |
| Slicer status and auto-support probe; GUI preview when needed | Completed slice, printer fit for the selected layout and profile, warnings and generated-support signal; preview can answer specific path or placement questions |
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

Use the shared evaluator's `--export` to write STEP/STL together, or `--slice`
to write the pair and run the reference smoke slice in one command. STEP is the
primary printable interchange file; the headless review uses the matching STL.
Confirm successful output status for the final files. Reimport or inspect mesh topology only when a
specific defect or risk warrants it. Batch meaningful sample variants and their
checks when useful, keeping each variant tied to a distinct hypothesis.

## Essential working rules

Use preferences already supplied. Ask targeted questions when missing information
changes fit, function or manufacturing; choose routine details autonomously.
Explain physical choices in plain language; use the design-decisions reference
to distinguish mechanism requirements and translate qualitative effort.

Prefer standard tool interfaces and common sizes for assembly and adjustment
(for example, hex sockets for standard Allen keys). The user already owns a
tool set and prefers those tools: do not model or export printable substitutes,
including optional drivers or wrenches, unless explicitly requested. Specify the
required standard tool and nominal size in the instructions, allow appropriate
printing clearance, and check access and engagement for the existing tool.
An all-printed object does not imply that its assembly tools must be printed.

Treat AGENTS.md's practical printer envelope as the default per-part limit, not
as a maximum allowed assembled-object size. An oversized request is a prompt to
design and validate a segmented assembly. Joint strength and assembly method are
functional requirements, not routine implementation details to guess silently;
use the design-decisions reference to resolve them.

Complete the deliverables agreed for this phase. For a full-design phase, offer
a first-print sample when it saves meaningful material or time without losing
the behavior under test. For a samples-only or explicitly staged phase, finish
that phase and use the resulting physical feedback for the next agreed phase.
Minimize material while preserving the behavior under test, and make every
variant answer an observable question.

Preserve successful interfaces during integration; the final smoke slice covers
the full printable layout. Revisit detailed paths only where changes invalidate
relevant evidence.
A change in surrounding stiffness or print height can matter without changing
nominal fit. Do not claim physical validation beyond actual user feedback.

Use [print planning](references/print-planning.md) for CAD-first FDM review and
[OrcaSlicer inspection](../orca-slicer-printability/SKILL.md) for the final smoke
slice or a slicer-sensitive question. An unknown user profile makes repository
slices reference evidence, not predictions of the user's toolpaths.
Export final STEP/STL pairs from the same evaluated geometry and check successful
output status. Apply object-specific geometric and mechanical checks where they
answer a functional question; this does not replace physical testing.
