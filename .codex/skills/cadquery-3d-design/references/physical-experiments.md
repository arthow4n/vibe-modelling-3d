# Small, informative physical experiments

Read during planning whenever fit, friction, flexibility, surface finish or
mechanism feel is uncertain. Use a concept calculation first when it can reject
an approach; identify what modelled geometry can establish (dimensions, local
sections, topology, rigid motion) separately from what needs a print (actual
force, wear, spring return, bonding or actual clearance). Prioritize uncertainty
by its effect on function and the cost of discovering a failure late.

## When product use fails

A user can reject a product's visible design, architecture or proposed use before
printing. Record that as product-design rejection, not a demonstrated print or
material failure. A user who physically prints and rejects a product provides
stronger evidence about its actual usefulness than internal assertions, FEA,
slicing or autonomous reviews.
Update the current object conclusion and root index immediately; remove “ready to
print” or equivalent confidence. Identify what earlier checks established narrowly
(fit, local deformation, slice acceptance) and what product relationship failed.
Do not reinterpret product-level rejection as tolerance, excessive snap force or
print-process trouble without evidence. Record unknown details as unknown.

When the failure exposes a recurring workflow problem, add one concise reusable
negative lesson and correct the responsible shared guidance. Abandoning a bad
concept is allowed; Git history can preserve retired products without dead
supported directories. Start any replacement from the user task and
[architecture gate](design-decisions.md#product-architecture-gate), not from momentum
in the rejected mechanisms. Local numerical work may remain useful independently;
it does not rehabilitate the product.

## Optional test prints for physical validation

Follow the agreed deliverable sequence and the
[feedback rules](design-decisions.md#feedback-and-autonomous-continuation).
Do not automatically finish the complete product before an experiment: qualify
a consequential unknown interface before dependent full-product refinement when
the result could change it. For an agreed sample phase, deliver that sample and
obtain the needed observation before the next phase. Continue independent work
within authorization while feedback is unavailable. If remaining uncertainty is
minor and direct completion is justified, an optional first-print sample need
not become a gate. Existing successful evidence can remove the need for a new test.

Choose the least expensive experiment capable of answering the question:

| Experiment | Represents | Typical limit |
| --- | --- | --- |
| Mechanism coupon | One specific interface, such as a snap, hinge or thread | Does not establish integrated handling, overall stiffness or product value. |
| Partial-product prototype | A section of the actual product with enough surrounding geometry to reproduce a meaningful assembly or handling interaction | Omitted span, contents or supports can still change behavior. |
| Complete prototype | The full object for integrated function, appearance and handling | May cost more, but can be the cheapest informative test for a small object or an inseparable interaction. |

The smallest specimen is not necessarily the most informative. A full-size simple
mockup can answer access or coordination cheaply; a functional mechanism trial
needs representative interfaces and manufacturing. Do not recommend a mechanism
coupon for a rejected or seriously doubtful whole-product concept; resolve product
value first. Local mechanics cannot establish enclosure usefulness or normal use.

Before recommending any physical test, answer these six questions briefly in the
existing record, without a compulsory separate report:

1. Which consequential uncertainty is tested?
2. Which real geometry, material, orientation and manufacturing conditions must
   be preserved for the observation to transfer?
3. Which parts of the product are omitted, and how does that limit the evidence?
4. What should the user do, and what observations are expected?
5. Which result would accept, revise or abandon the design or tested interface?
6. Why is this print preferable to a cheaper check or a complete-product print,
   considering preparation, material, print time and feedback cycles?

If no plausible result changes a consequential decision, omit the test. Acceptance
qualifies only what the specimen represents; it cannot validate omitted interactions.

* Consider test pieces for behavior that CAD and slicing cannot establish reliably: hinge freedom, snap-latch engagement and release, friction fits, sliding joints, clip grip, flexible tabs, printed threads, and press-fit inserts. Provide one when it can meaningfully reduce the cost of discovering a likely fit or mechanism problem; do not create coupons automatically for every feature.
* Reuse the production interface construction and parameters where practical. Preserve mating geometry, material, relevant slicing settings and print orientation, plus wall thickness, flexible length, attachment stiffness and surrounding geometry that determine the tested behavior. A shortened clip can be much stiffer than the real part. If a small sample cannot represent the interaction adequately, explain that limitation instead of treating it as a substitute for a full-part trial.
* Evaluate test pieces through the same applicable CAD and printability workflow as the model, including practical bed contact and intended component positions. Export them with clear names inside the object's directory. Make their purpose and the full-model print file easy to distinguish.
* Provide brief instructions for what to try and observe, such as whether a latch engages securely and releases comfortably, and identify the parameter to adjust if it binds or feels loose. State what the sample does not test, such as full-object stiffness, compression resistance or fatigue life. Offer a small labeled set of clearance variants only when comparison would help; avoid unnecessary samples.

When the decision depends on physical texture, finish or feel, compare
representative full-scale samples when they are more informative per cost than
complete objects. For visual form alone, use rough visual evidence first.
Produce full-object variants only if those are agreed deliverables. When several
physical hypotheses can be tested in one print session, batch distinguishable samples if their print
placement and process remain representative. Each result should point to a
specific next choice; a larger batch has value only when it saves a feedback
cycle or resolves a requested comparison.

For a structural coupon, derive the representative force, moment and restraint
from the complete assembly's load case before specifying a test load. Preserve
the effective load-bearing section, print-layer direction and relevant contact
or support conditions. A short joint sample may answer fit or driveability while
missing the full span's bending and stiffness; label that scope explicitly and
screen the complete load path separately. Do not recommend a coupon as a
strength-qualified trial when the assembly's structural screen already rejects
its joint architecture.

Before printing, coupon review establishes only preserved geometry/constraints,
experiment scope and, when sliced, acceptance under the selected profile. It
does not measure release force, friction, spring return, hinge wobble or fatigue.
Once virtual checks have narrowed the uncertainty to physical behavior, stop
generating virtual variants and recommend the informative print comparison.

## Minimize cost while preserving the experiment

Aim for the smallest useful experiment, not an arbitrary weight limit. Remove
floors, decorative surfaces or walls only when they do not materially affect
the question. Preserve mating surfaces, clearances, flexure length/thickness,
attachment stiffness, movement constraints and print orientation. Do not
shorten spring arms or scale a mechanism to reduce material.

A skeletal fixture may test seating but underrepresent enclosure stiffness;
say so. Estimate material or print time only when it changes the sample choice;
use a slicer's existing estimate when available, without adding G-code analysis
solely to obtain a precise number. Compare with a less simplified fixture when
the savings/validity tradeoff is uncertain. A complete prototype is justified
when integrated use or structure is needed for the observation, or simplifying
it saves little total cost. Do not impose a universal
bridge length or coupon mass.

## Make variants distinguishable and diagnostic

For each proposed trial, state the suspected cause, the changed parameter or
mechanism, the observable difference, and how each outcome would guide the
next decision. Keep successful geometry as a baseline. Prefer changing one
factor when isolating a cause; use clearly labeled different concepts when
the mechanism itself is uncertain. Do not multiply nearly identical variants
without explaining why the difference should be detectable.

Use the [mechanics guidance](design-decisions.md#actuation-effort-and-cheap-mechanics)
to screen force/strain where applicable before choosing physical variants. For
example, 2.2 versus 2.8 mm latch leaves can test whether insufficient stiffness
causes light release, with geometry and leverage otherwise preserved. Label
predictions as hypotheses; prefer one or two informative comparisons over a
default clearance matrix.

## Recommend a first print without blocking modelling

Deliver the agreed phase and recommend what to print first, with the six questions
above answered. Continue independent modelling within that phase while the user
is away; do not complete dependent work whose design awaits the observation.
Do not turn a minor optional sample into an unrequested approval gate or ask the
user to reauthorize work. If new evidence makes proceeding unjustified, hand off
the informative intermediate deliverable and explain the dependency.

Use [the experiment record](../assets/experiment-record.md) inside the object's
notes when there are multiple trials or iterations; omit irrelevant fields for
a simple one-off fit check. Link the record to artifact hashes/revisions and
slicer reports, distinguishing predictions, observed feedback and decisions.

For unresolved handling questions, turn the design's task walkthrough into brief
observable steps: support the object, operate it, access the item, and restore it
as applicable. Record slips, unintended contact, obstructed access or awkward
regripping separately from the suspected cause. Preserve the relevant hand/surface
support and use context; a light internal mechanism force alone does not establish
easy operation. Use a simple full-size mockup when it cheaply answers access or
coordination, and a functional print for fit, friction or snap behavior. State
which behavior the trial cannot represent; no extra mockup or coupon is required.

## Standard per-object print-status record

Keep the same small status block in each object's primary notes, even when no
coupon is proposed:

| Item | Print status | Artifact(s) | User result or remaining physical checks |
| --- | --- | --- | --- |
| Test piece(s) | Yes / No / Partial / N/A / Unknown | Exact exported file names | What was observed, or what remains to test |
| Final printable object(s) | Yes / No / Partial / N/A / Unknown | Exact exported file names, or none | What was observed, or what remains to test |

Use **N/A** for test pieces when none were designed. Use **Unknown** when the
repository has no user print report for an exported item; do not turn an absent
note into a claim that a part was not printed.
Use **N/A** for the final object during a samples-only or rough-concept phase when
no final printable object was included; both rows can be N/A for visual studies.
Update the relevant row when a later phase delivers a printable item.
Keep “printed” separate from “functionally tested”: a print can exist without a
fit, force, durability or use result. Add the report date, source revision or
artifact hash, material, orientation and printer/profile when known; record
unknown fields as unknown.

## Learning from trial prints

Record physical feedback against the tested source revision or artifact hash, interface parameters, material, print orientation, and printer/profile where known in the object's notes. Preserve a successful baseline before changing fit; adjust clearances incrementally using the observed play or binding. A changed clearance, orientation or surrounding geometry is a new configuration: distinguish the user's successful earlier print from CAD/slicer checks of the revision. Record the user's subjective result (too light / good / too stiff) and observed failure mode separately from interpretation; mark unknown settings as unknown. Do not generalize one successful coupon's tolerances to other printers or materials, or treat it as evidence for untested latch force or full-object strength.

A functional observation is not automatically material calibration. Opening
force combines stiffness, friction, dimensions, guide play and attachment
compliance. Preserve the measurement and known setup without inferring modulus
or a strength limit from it alone. Before recommending a print, choose observations
that discriminate the remaining hypotheses: for a detent, accidental-release
resistance as well as deliberate effort, rubbing location, recovery and dwell.
Use the complete object when those interactions make a coupon unrepresentative;
do not require another print solely to collect a calibration value.

## Transfer a successful mechanism deliberately

Reuse its builder where practical. Preserve actual mating geometry, nominal
clearances, flexure dimensions and print orientation; translate rather than
scale. Check interface geometry equivalence when refactoring. Recheck assembly,
movement and printing in the complete object: greater bearing separation,
different attachment stiffness or a changed layer registration can alter
behavior even when the local CAD geometry is identical. State the limits of
the successful coupon evidence; do not repeat a physically validated experiment
unless a relevant change warrants it.
