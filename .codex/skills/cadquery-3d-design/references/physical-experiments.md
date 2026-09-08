# Small, informative physical experiments

Read during planning whenever fit, friction, flexibility, surface finish or
mechanism feel is uncertain. Identify what CAD can establish (dimensions,
topology, rigid motion) separately from what needs a print (force, wear,
spring return, bonding or actual clearance). Prioritize uncertainty by its
effect on function and the cost of discovering a failure late.

## Optional test prints for physical validation

Finish the complete model. Include a small test piece only when it meaningfully reduces the cost of testing an uncertain interaction while preserving the relevant behavior. A test piece is an optional first print, not a default gate that makes the agent stop and wait. Continue evaluating, refining and exporting the complete design while physical feedback is unavailable; identify remaining uncertainty at handoff. Pause dependent work only when the user has requested a staged testing workflow or an essential unresolved requirement prevents a meaningful final design.

* Consider test pieces for behavior that CAD and slicing cannot establish reliably: hinge freedom, snap-latch engagement and release, friction fits, sliding joints, clip grip, flexible tabs, printed threads, and press-fit inserts. Provide one when it can meaningfully reduce the cost of discovering a likely fit or mechanism problem; do not create coupons automatically for every feature.
* Reuse the production interface construction and parameters where practical. Preserve mating geometry, material, relevant slicing settings and print orientation, plus wall thickness, flexible length, attachment stiffness and surrounding geometry that determine the tested behavior. A shortened clip can be much stiffer than the real part. If a small sample cannot represent the interaction adequately, explain that limitation instead of treating it as a substitute for a full-part trial.
* Evaluate test pieces through the same applicable CAD and printability workflow as the model, including practical bed contact and intended component positions. Export them with clear names inside the object's directory. Make their purpose and the full-model print file easy to distinguish.
* Provide brief instructions for what to try and observe, such as whether a latch engages securely and releases comfortably, and identify the parameter to adjust if it binds or feels loose. State what the sample does not test, such as full-object stiffness, compression resistance or fatigue life. Offer a small labeled set of clearance variants only when comparison would help; avoid unnecessary samples.

At handoff, deliver the full design plus any useful test pieces and explain that the user may print the samples first. Do not present the mechanism as physically validated until the relevant print has actually been tested.

## Minimize cost while preserving the experiment

Aim for the smallest useful experiment, not an arbitrary weight limit. Remove
floors, decorative surfaces or walls only when they do not materially affect
the question. Preserve mating surfaces, clearances, flexure length/thickness,
attachment stiffness, movement constraints and print orientation. Do not
shorten spring arms or scale a mechanism to reduce material.

A skeletal fixture may test seating but underrepresent enclosure stiffness;
say so. Use the slicer to estimate filament and time before recommending a
sample, and compare with a less simplified fixture when the savings/validity
tradeoff is uncertain. A full box is justified only if its structure is needed
for the intended observation. Do not impose a universal bridge length or
coupon mass.

## Make variants distinguishable and diagnostic

For each proposed trial, state the suspected cause, the changed parameter or
mechanism, the observable difference, and how each outcome would guide the
next decision. Keep successful geometry as a baseline. Prefer changing one
factor when isolating a cause; use clearly labeled different concepts when
the mechanism itself is uncertain. Do not multiply nearly identical variants
without explaining why the difference should be detectable.

More engagement travel need not mean more spring force. Separate closed play,
holding force and release effort. Label predictions as hypotheses, not measured
results. Provide one or two informative comparisons when sufficient, rather than
a default clearance matrix.

## Recommend a first print without blocking modelling

Deliver the authorized full design alongside useful samples unless the user
requested samples only. Clearly recommend which sample to print first, its
cost, what to observe, and what it does not validate. Continue independent
modelling while the user is away. Do not turn a sample into an unrequested
approval gate or ask the user to reauthorize work.

Use [the experiment record](../assets/experiment-record.md) inside the object's
notes when there are multiple trials or iterations; omit irrelevant fields for
a simple one-off fit check. Link the record to artifact hashes/revisions and
slicer reports, distinguishing predictions, observed feedback and decisions.

## Learning from trial prints

Record physical feedback against the tested source revision or artifact hash, interface parameters, and known material/profile settings in the object's notes. Preserve a successful baseline before changing fit; adjust clearances incrementally using the observed play or binding. A changed clearance, orientation or surrounding geometry is a new configuration: distinguish the user's successful earlier print from CAD/slicer checks of the revision. Do not generalize one successful coupon's tolerances to other printers or materials, or treat it as evidence for untested latch force or full-object strength.

## Transfer a successful mechanism deliberately

Reuse its builder where practical. Preserve actual mating geometry, nominal
clearances, flexure dimensions and print orientation; translate rather than
scale. Check interface geometry equivalence when refactoring. Recheck assembly,
movement and printing in the complete object: greater bearing separation,
different attachment stiffness or a changed layer registration can alter
behavior even when the local CAD geometry is identical. State the limits of
the successful coupon evidence; do not repeat a physically validated experiment
unless a relevant change warrants it.
