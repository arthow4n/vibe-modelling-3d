# Reusable model evidence

During planning, check for a similar interface or manufacturing problem here,
then read the linked object's current source and evidence. Reuse a successful
builder when practical. Preserve its mating geometry and print orientation;
reassess movement, loads, stiffness or printing where the new assembly changes
the relevant conditions. A fit or print result applies to the tested
configuration, not every material or printer.

| Pattern | Evidence worth consulting | Transfer limit |
| --- | --- | --- |
| Captive hinge and side-printed keeper | [Sunglasses case E closure](../../../../model/sunglasses_case/notes/printing_and_design.md#e-mechanism-integration): D/E samples were printed and accepted; the integrated full case was reported working. Its source preserves the accepted interface dimensions. | Greater bearing separation, different shell stiffness, layer registration and untested fatigue can change the behavior. Translate the local interface rather than scaling it. |
| Printed screw-top closure | [Vaseline container](../../../../model/vaseline_container/README.md#decisions-and-evidence): the full base/lid pair with a 3 mm pitch thread and 0.30 mm nominal radial allowance was printed and reported good. | The actual material and print profile are unknown. Use the geometry as a starting reference, then check the new thread and opening motion. |
| Large plate joined with printed screws | [Book reading plate](../../../../model/book_reading_plate/README.md#what-changed-after-the-successful-l-sample): the sample's thread fit worked; the downward-facing drive socket printed poorly. The revised head-up screw and final plate were reported to print nicely. | The print report does not establish load capacity or long-term creep. Recalculate the load path when loads, geometry or supports differ; review the drive socket orientation and thread interface where changed. |
| Minimal gravity postcard support | [Wave postcard display](../../../../model/postcard_display/README.md#print-status): the user reports the full Wave holder was printed and works well. Its [builder](../../../../model/postcard_display/style_variants.py) combines low front stops with curved rear arms. | Actual material, printer settings and card dimensions were not reported. Reuse the seating/retention geometry as a starting point; changed backing, footprint or card stiffness needs its own review. The report does not validate the other variants or every card size/orientation. |
| Entry clearance versus seated steadiness | [Swatch base physical history](../../../../model/filament_swatch_box_study/README.md#physical-history-and-print-status): the first PETG base rocked and varied laterally; the printed [spring revision](../../../../model/filament_swatch_box_study/card_base_petg_5.py) grips nicely front/back, but its tiny end spring gives no useful sideways pressure. | Actual dimensions, forces and nozzle/profile remain unknown. Entry paths, relaxed interference and independent spring/filled-path screens do not establish useful centering in the coupled contact sequence. The replacement corner-seat trial has no print report; do not infer a tolerance, friction or material calibration from the failure. |
| Analysis-driven flexible catch | [Phone stand API experiment](../../../../model/analysis_phone_stand/README.md#what-using-the-api-changed): prescribed release and local holding-contact solves informed a wider root and positive travel stop; force was stable across the recorded refinement studies. | Unprinted, solid PETG assumptions. Local peak strain was mesh sensitive; sharp-tooth pass-over failed. Reuse the analysis pattern, not the numerical load rating or material limit. |
| Known snap, flexure and structural questions | [Shared engineering questions](../../../../physical_analysis/README.md#use) bind explicit intent to evidence and bounded studies. Phone release reproduces retained results; the book plain-back cross-check agrees within 6%; a [local rounded-contact fixture](../../../../physical_analysis/experiments/ipc/fixtures/rounded_snap/README.md) exercises passage/return and evidence guards. | The fixture is synthetic geometry derived from a failed product, not a product precedent. Its force remains increment-sensitive. Numerical, material, manufacturing and physical evidence remain separate. |
| Numerical mesh conversion at tiny contact gaps | [IPC investigation](../../../../physical_analysis/experiments/ipc/README.md) independently compared supplied and native rest meshes and caught MEDIT version-1 float32 conversion despite high-precision ASCII. Version 2 preserves doubles; accepted-frame triangle checks catch crossing without relying on selected contact nodes. | IPC has not qualified complete rounded-fixture passage. Mesh witnesses are independent numerical evidence, not global exact-CAD or continuous-path proof; rounded obstacle facets need separate sensitivity. |
| Representative staged physical development | [Sunglasses-case development](#staged-development-and-form-exploration): accepted D/E samples preceded integration into the reported working full case. | Preserve the tested conditions and recheck changed integration; sample acceptance does not establish full-product handling or durability. |
| Form choices before detailed variants | [Postcard and tray exploration](#staged-development-and-form-exploration) produced visual comparisons and printable alternatives. Retrospective workflow judgment: rough studies would often have informed those choices earlier. | This is a sequencing lesson, not an observed print failure or a requirement for variants when a clear reference already settles form. |
| Premature mechanism commitment | [Four rejected swatch-storage designs](#four-rejected-swatch-storage-designs) repeated excessive engineering around weak product concepts despite earlier architecture guidance. | Challenge mechanism necessity and total product cost on rough complete geometry; resolve whole-product value before local mechanics. A coupon or numerical pass cannot justify the product. |

Add or revise an entry autonomously when a printed result, measured model check,
or repeatable failure can save work on another object. Link to the current
object record and source, state what was actually observed and under which known
setup, and name the boundary of transfer. Keep detailed measurements and trial
history in the object directory. For removed products, link Git history and retain
only a concise negative lesson here. Remove or correct an entry when later evidence
supersedes it; do not append session narratives or untested clearance rules.

## Staged development and form exploration

**Observed physical evidence:** the [sunglasses-case record](../../../../model/sunglasses_case/notes/printing_and_design.md#e-mechanism-integration)
reports D and E samples printed and accepted, a slight preference for E, then a
working integrated full case. Representative smaller experiments established the
consequential interface before committing to the complete print. Transfer that
sequence when local behavior is the uncertainty; preserve geometry and process,
and keep final integrated use and untested fatigue distinct from sample success.

**Retrospective design judgment:** [postcard silhouettes](../../../../model/postcard_display/README.md#three-further-sculptural-alternatives)
and [tray patterns](../../../../model/faceted_storage_tray/README.md#options-and-files)
show form choices that could have been compared in rough studies before detailed
variants and exports. Their records include positive print reports for Wave and
H respectively; those do not establish that earlier exploration would have changed
the selected style. The transferable improvement is to recognize unresolved form
choices without waiting for a variants request, then compare only meaningful
differences cheaply. Printed texture may still warrant representative samples;
silhouette alone normally warrants rough visual evidence first.

## Four rejected swatch-storage designs

The sliding box, lift-off box, upright file and hinged case were removed. The
original sliding version was physically printed and found unusable; the other
three were rejected before printing. The hinged case was rejected for visible
design, architecture and proposed use, not demonstrated print or material failure.
The earlier [three-design cleanup](https://github.com/arthow4n/vibe-modelling-3d/commit/818ee96fa37615c1ab376fad9f7c1a636de38ab6)
and [hinged-case commit](https://github.com/arthow4n/vibe-modelling-3d/commit/1c30dd337298285f9d6ae0deb97343048c95c64e)
preserve the rejected work in Git history; none is a positive product or latch pattern.

**Retrospective design judgment:** the hinged case's three screw/nut connections,
separate flexible catch, release button, surrounding reliefs and substantial
analysis were disproportionate to the improvement in browsing: the proposed use
still removed horizontal packets and fanned them in hand. The proposed retention
coupon represented local latch mechanics, omitting full enclosure, actual hinge
motion, contents and browsing. It was not physical validation, and even a successful
print could not settle whether the product was desirable.

Earlier architecture guidance alone did not prevent premature commitment. Use
[adaptive development and feedback](design-decisions.md#feedback-and-autonomous-continuation):
make the uncertain complete form and operation reviewable cheaply, and stop for
consequential concept judgment before dependent mechanisms, simulation, slicing
or coupon recommendations. Do not diagnose unobserved tolerance/material causes
for a concept rejection. Abandon weak concepts regardless of sunk work; numerical
experiments can remain independent evidence without preserving the product.
