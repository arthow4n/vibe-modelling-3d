---
name: cadquery-3d-design
description: Design or revise practical parametric CadQuery objects for single-material FDM printing. Use for every 3D modelling task in this repository; choose proportionate evidence and retrieve mechanism, manufacturing or experiment guidance only when relevant.
---

# CadQuery 3D design

[AGENTS.md](../../../AGENTS.md) owns repository execution, ownership, evidence
integrity, delivery and Git requirements. This skill owns functional design and
the choice of the next useful investment. A valid solid or clean slice alone does
not establish product value or physical function.

## Decide what to build next

Establish the actual task, contents/held item, critical dimensions, normal
interaction and foreseeable failure modes. Inspect existing source, user changes
and current object evidence. Read applicable
[user preferences](references/user-preferences.md) early: printer/manufacturing
before sizing printable features; form/protection before choosing an enclosure;
assembly tools and stock hardware before committing to fasteners. Search the
[reusable evidence index](references/reusable-model-lessons.md) for an analogous
interface or problem, then consult only the applicable linked source and limits.
Project requirements remain with their object; latest user instructions prevail.

Choose the deliverable from the uncertainty that could change the next decision:

| Situation | Next useful investment |
| --- | --- |
| Straightforward, clear object | Complete it directly with applicable CAD, FDM and delivery checks; no compulsory variants, coupons or intermediate approvals. |
| Consequential form or interaction remains open | Compare a few inexpensive rough directions using [form exploration](references/design-decisions.md#inexpensive-visual-and-form-exploration) and the user's SVG-first preference. |
| New mechanism or functional multipart/moving product | Apply the [architecture gate](references/design-decisions.md#product-architecture-gate) before detailed interfaces, tolerance studies, simulation or final slicing. Review rough complete geometry with actual contents and normal use; local mechanics cannot justify a poor product. |
| Unqualified interface or coupled physical behavior | After establishing product value, qualify the critical relationship with targeted geometry, simple mechanics or a representative experiment before dependent full-product refinement. |
| Established-product revision | Preserve accepted architecture, successful interfaces and valid evidence. Review affected relationships, including changed surrounding stiffness or print conditions; do not restart the whole process. |

Screen rough fit, engagement, assembly travel, print envelope and relevant loads
before detailed CAD when these can reject a concept. Reject an approach that fails
even optimistic assumptions. Simple objects do not need structural calculations.
Use the [concept screen](references/design-decisions.md#pre-cad-concept-screen)
for consequential fit/load uncertainty. For oversized assemblies, retrieve it
**before committing to a split or joint**: establish the required loads, assembly
permanence, allowed hardware/adhesive and failure consequences with the user; bed
fit or alignment alone does not establish a structural joint.

Use existing agreement and authorization. For printable phases, establish the
proposed nozzle, layers, material, walls/infill and consequential assumptions
using the [setup defaults](references/user-preferences.md#printer-manufacturing-and-available-hardware).
For visual studies, state only process assumptions that affect the choice.
Choose routine details autonomously. Read
[adaptive development](references/design-decisions.md#adaptive-development-and-the-next-deliverable)
and [feedback rules](references/design-decisions.md#feedback-and-autonomous-continuation)
when the next commitment depends on unresolved concept judgment or an observation.
Complete the agreed rough/sample phase without assuming it authorizes dependent
work. Delegated choices need no repeated approval; sunk work never obliges keeping
a poor concept.

## Retrieve detail before it matters

Read the relevant sections, not every reference. Early retrieval governs choices;
operation details can wait until the corresponding work is justified.

| Trigger and timing | Owner |
| --- | --- |
| Multipart components/poses shared by checks, inspection or print layouts, or consequential pair/path diagnostics; before organizing placements and checks | Recommend native `cq.Assembly` with the [assembly geometry API](references/parametric-and-edges.md#assembly-representation). Keep geometry and operating relationships object-owned; explicit opt-out allows adequate local checks and unsupported cases. |
| Unresolved handling, access, protection, grips or moving-weight stability; before mechanism refinement/expensive analysis | [Whole-object form and handling](references/design-decisions.md#whole-object-form-and-handling). Revisit affected relationships after integration. |
| Justified mechanism; before developing mating geometry | [Architecture contacts and states](references/design-decisions.md#product-architecture-gate), [motion/interface checks](references/design-decisions.md#deterministic-motion-and-interface-checks) and [actuation/retention screen](references/design-decisions.md#actuation-effort-and-cheap-mechanics). Name support, guide, seat, stop, retain and release contacts; check required contact and forbidden interference through the complete path. Screen the real holding-force source before exporting a retention sample. |
| Structurally important part/joint; before detailing and after measured sections change | [Load paths and joint screens](references/design-decisions.md#structural-load-paths-and-joint-screens). |
| Parametric source, components or edge treatment; during construction | [Parametric construction and edges](references/parametric-and-edges.md). Prioritize functional topology and proportions; treat exposed/grip edges deliberately without weakening interfaces. |
| Printable geometry; during planning and final review | [Print planning](references/print-planning.md). Co-design CAD and manufacture; inspect actual paths only when a consequential assumption depends on them. |
| Captive support-free hinge | [Conical pivot example](references/print-in-place-hinges.md), with its applicability and physical limits. |
| Consequential deformation/contact uncertainty exceeds CAD or analytical screens; before solving | [Shared engineering questions](../../../physical_analysis/README.md#use) and [study guidance](../../../physical_analysis/README.md#study-sequence). Prefer existing questions; select `QuestionStudy` before planned numerical comparisons. Independent solver qualification is separate from product acceptance. |
| Physical fit, force, friction, texture or durability could change the decision; before recommending a test | [Physical experiments](references/physical-experiments.md#optional-test-prints-for-physical-validation). Choose coupon, partial or complete prototype with representative conditions and explicit omissions; no automatic coupon requirement. |
| Print/use feedback or rejection | [Physical-feedback guidance](references/physical-experiments.md#when-product-use-fails) and [reflection](../engineering-reflection/SKILL.md). Correct readiness and root index immediately; distinguish visual rejection, print failure and uncertain causes. |

For consequential requirements shared across variants or mixed evidence sources,
use the [product verification convention](../../../product_verification/README.md).
Preserve user provenance and visible UNKNOWN coverage; compose existing checks
and retire architecture-specific derivations when appropriate. Agent choices are
challengeable, while historical physical evidence retains its scope. Simple
products can keep adequate local checks. The object record still owns nuanced
intent, hypotheses and project-state decisions.

## Build and review against intent

Use the shared evaluator to establish valid geometry and inspect errors. Repair
the smallest underlying cause of a build failure; simplify repeated failing
construction. Read dimensions from source/notes, then measure actual CAD only
where planning cannot answer a consequential question. A nominal parameter or
bounds report does not verify a contact, local gap or intended use.

Ask: **What remains uncertain, what would the result change, and what is the
cheapest reliable evidence?** Cost includes agent effort as well as computation.
Choose evidence by question, not as a mandatory sequence:

| Evidence | Establishes within its scope |
| --- | --- |
| Targeted CAD checks | Mating dimensions, required contacts, forbidden interference, engagement and clearance on the stated path/poses. Sampled motion is not continuous-path proof. |
| Useful views/task walkthrough | Proportions, appearance, component relationships, access and understandable use. A view path alone is not visual inspection. |
| Analytical mechanics or justified simulation | Predicted stiffness, force, strain or structural response under stated fixture/material assumptions; numerical quality is separate from printed validation. |
| Slice status/support probe; specific paths when needed | Toolpath acceptance and fit for the selected profile/layout, notices and support signal; no guarantee of sag, material behavior or physical fit. |
| Representative physical print | Actual fit, effort, wear, recovery and handling under tested conditions; no inferred universal tolerance or material calibration. |

Trust checked geometry rather than rendering more poses to re-prove it; improve
suspect checks instead. Once only physical/tactile uncertainty remains, record its
limit and recommend an informative test when worthwhile. Stop extra review when
adequate evidence answers the question; reopen affected evidence after relevant
changes. Continue while material functional, ergonomic or manufacturing defects
remain, and abandon concepts that perform the central task poorly.

## Finish the agreed phase

For printable deliverables, use the construction/edge and
[final FDM review and smoke check](references/print-planning.md#final-review-and-reference-smoke-slice).
Resolve available CAD fit, complete assembly-path and form questions before final
artifact batches, except when an earlier slice decides geometry. Read
[evaluator details](../../../execution/README.md#cad-evaluation-and-exports) before
export/render/report operations, and the [Orca skill](../orca-slicer-printability/SKILL.md)
for the smoke review. Reuse valid final evidence; exports must cover final geometry.

Save the phase's deliverables, useful views and concise assumptions/use/evidence
in the object's existing record, including the
[print-status block](references/physical-experiments.md#standard-per-object-print-status-record).
Apply [reflection](../engineering-reflection/SKILL.md) briefly to new evidence at
handoff, then follow AGENTS.md's review, attribution, commit and push requirements.
No duplicate completed checklist or extra reflection report is required.
