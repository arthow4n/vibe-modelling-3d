---
name: cadquery-3d-design
description: Design practical parametric CadQuery objects for single-material 3D printing, including fit, mechanisms, ergonomics and economical physical experiments. Use for every 3D modelling task in this repository.
---

# CadQuery 3D design

Use this skill for functional, manufacturable models. AGENTS.md owns repository
workflow, shared CadQuery command, printer setup, attribution, artifacts
and Git rules. A valid solid or clean slice alone does not establish function.

For form, handling and mechanism choices, read the repository user's
[design preferences](references/user-preferences.md). Apply relevant preferences
with their stated scope; the latest request overrides recorded defaults.

## Choose the next useful investment

Choose development strategy from the consequential uncertainty, using
[adaptive development](references/design-decisions.md#adaptive-development-and-the-next-deliverable):

- Clear requirements and a straightforward concept: complete the printable object
  directly, without compulsory variants, intermediate approvals or coupons.
- Unresolved appearance or form: compare a few inexpensive rough directions,
  even when the user has not explicitly requested variants.
- Unqualified fit or mechanics: establish the whole-product concept, then resolve
  the critical interface with targeted checks or representative experiments before
  committing to dependent full-product work.
- Combined uncertainty: settle useful form and interaction before qualifying the
  mechanics; finish the product when those decisions are sufficiently established.

These are adaptable levels of investment, not a universal sequence. Choose the
initial deliverable deliberately; rough geometry or a partial prototype can be
the complete deliverable for this phase. Stop for a consequential unresolved
decision when the next investment lacks justification; otherwise continue within
existing authorization. Follow the reference's
[feedback rules](references/design-decisions.md#feedback-and-autonomous-continuation),
without extra forms or repeated approvals.
Before new mechanisms or functional moving assemblies, apply the
[product-architecture gate](references/design-decisions.md#product-architecture-gate).
Local passes and sunk work never protect a poor concept.
User product rejection supersedes speculative confidence; follow the
[physical-failure guidance](references/physical-experiments.md#when-product-use-fails).

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
- [ ] Establish the actual handling task, critical dimensions, assembly/material preferences, operating effort, required retention and failure modes; screen consequential tolerance extremes together.
- [ ] Screen the concept with rough fit, engagement, assembly-travel and print-envelope calculations as relevant. For structurally important parts and joints, estimate loads, stiffness and force before detailed CAD; reject an infeasible concept early.
- [ ] Identify the uncertainty that could change the next decision; choose direct completion, rough form exploration, staged interface development or a combination. Recommend the next useful deliverable and relevant print assumptions; use existing agreement or delegated scope without asking again.
- [ ] Decide which remaining questions require modelled geometry and which require a physical print. For an oversized assembly, resolve segmentation and joint/load requirements with the user before finalizing it.
- [ ] When visual directions could change the choice, compare two or three meaningful rough alternatives using shared dimensions and references; inspect only views that reveal the differences. Stop exploration when the choice is adequately informed.
- [ ] For uncertain form, handling or new mechanisms, build and inspect rough complete geometry with contents, major components, openings and relevant operating states. Challenge mechanism necessity and total construction/use cost through the architecture gate. An already established product needs only affected relationships reviewed.
- [ ] Before substantial refinement, resolve consequential whole-product objections and undelegated subjective choices. Hand off the agreed rough studies if that is the phase; do not complete details while waiting for the decision that justifies them.
- [ ] For justified mechanisms, name component jobs and support/guide/seat/stop/retain/release contacts. Verify required/forbidden relationships at meaningful states; temporarily remove retention to check independent alignment, guidance, seating and stops.
- [ ] Co-design geometry, material, orientation, nozzle/layers, perimeters, infill/local solidity and supports; revise either CAD or process using the cheapest adequate evidence. Inspect actual sliced paths when a mechanical assumption depends on them; never infer calibrated material properties from settings. Plan physical experiments for remaining uncertainty.
- [ ] Before any physical test recommendation, choose a mechanism coupon, partial-product prototype or complete prototype using the [six experiment questions](references/physical-experiments.md#optional-test-prints-for-physical-validation). Preserve representative conditions; a rejected or seriously doubtful concept does not warrant a mechanism coupon.
- [ ] Develop only the critical details needed to qualify the next investment. Finish understandable parametric geometry when concept and interface evidence justify it; preserve successful interfaces and stop at the agreed staged deliverable.
- [ ] Evaluate source through the shared CadQuery command; inspect build validity and errors, then select views or targeted geometry checks for unresolved questions.
- [ ] Revisit affected [whole-object form and handling](references/design-decisions.md#whole-object-form-and-handling) relationships when detailed geometry changes them; preserve the architecture gate ahead of expensive analysis.
- [ ] Check insertion, load-bearing contact, retention, release effort and user access.
- [ ] For structurally important parts and joints, update the load and stiffness screen using measured CAD sections before recommending a structural trial.
- [ ] Use mechanics/simulation only for remaining consequential uncertainty in a worthwhile concept; consider removing the mechanism first if it alone creates extensive analysis work. Tool availability never justifies a mechanism. When contact analysis is needed, use the [decision-driven study guidance](../../../physical_analysis/README.md#plan-a-contact-study).
- [ ] Prefer [shared engineering questions](../../../physical_analysis/README.md#use) for known snap, flexure and structural situations; supply explicit physical intent, reuse identity-checked evidence and select only decision-relevant study axes. Reserve `AnalysisCase` for novel experiments.
- [ ] Review final generic FDM geometry and resolve significant defects, especially on fit-critical surfaces.
- [ ] Review exposed edges, corners and grip areas without weakening interfaces.
- [ ] Export the agreed printable layouts as STEP/STL from the same print-ready geometry and placement; check output status and any specific export concern.
- [ ] Run/reuse the final reference smoke slice for those layouts when available; investigate detailed paths only for unresolved slicer-sensitive questions.
- [ ] Save useful final views, assumptions, physical evidence and print instructions.
- [ ] Record separate print status for test piece(s) and any final printable object in the object's notes; use N/A when a category is outside the agreed phase and do not infer a physical print from CAD or slicer output.
- [ ] On user product rejection, update conclusions/readiness and the root index immediately; distinguish rejection before printing from physical use failure, identify the narrower scope of earlier passes, and feed recurring failures into shared guidance without an unsupported tolerance/process diagnosis.
- [ ] Add a reusable-evidence entry only if this work produced a transferable result; link to its detailed object record.
- [ ] Review and commit/push according to AGENTS.md.

Prioritize function, manufacturability, proportions and topology before cosmetic
detail. Iterate while substantial defects remain. Name dimensions and allowances;
do not mistake a parameter value for a verified measurement or physical result.

## Read the relevant reference

| Trigger | Reference |
| --- | --- |
| Form, grip, enclosure feel, mechanism overhead or recording user preferences | [User design preferences](references/user-preferences.md) |
| Development strategy, next deliverable, visual alternatives, feedback, requirements, whole-object handling, joints or mechanisms | [Design decisions](references/design-decisions.md) |
| Generic FDM review, final smoke slice, orientation, moving parts or support constraints | [Print planning](references/print-planning.md) |
| Fit, force, friction or durability needs physical validation | [Physical experiments](references/physical-experiments.md) |
| Dimensions, shared builders, modular source or edge treatment | [Parametric construction and edges](references/parametric-and-edges.md) |
| Captive hinge construction | [Opposing conical pivot example](references/print-in-place-hinges.md) |
| A similar model or a transferable physical result | [Reusable model evidence](references/reusable-model-lessons.md) |

Read the relevant references during planning, not only after a failed print.
Do not load every reference for every task.

## Early comparison for aesthetic alternatives

Treat rough geometry and renders as decision tools. The
[conditional exploration guidance](references/design-decisions.md#inexpensive-visual-and-form-exploration)
owns variant selection, representation and review. Trigger exploration from an
unresolved consequential visual choice, not only an explicit request for variants.
Do not invent automated aesthetic ratings or engineer each direction in full.

## Proportionate review

Ask: **What uncertainty remains, what would the result change, and what is the
cheapest reliable evidence that can resolve it?** Apply AGENTS.md's check-value,
reuse and batching rules when choosing new checks or extra manual reviews.
Apply its total-workflow-cost preference: reliable repeatable compute can save
agent turns; "cheap" does not mean minimizing computation at their expense.
Omit new checks when either outcome would lead to the same action. Established
automatic checks can run routinely without a fresh decision each time. Stop extra review
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

Complete the deliverables agreed for this phase, using the feedback rules above
when new evidence makes dependent work an unjustified commitment. A sample is
useful only when its result can change a consequential decision; finish a staged
sample phase and obtain that observation before dependent refinement.

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
