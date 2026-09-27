# Reusable model evidence

During planning, check for a similar interface or manufacturing problem here,
then read the linked object's current source and evidence. Reuse a successful
builder when practical. Preserve its mating geometry and print orientation;
recheck movement, loads, stiffness and printing in the new assembly. A fit or
print result applies to the tested configuration, not every material or printer.

| Pattern | Evidence worth consulting | Transfer limit |
| --- | --- | --- |
| Captive hinge and side-printed keeper | [Sunglasses case E closure](../../../../model/sunglasses_case/notes/printing_and_design.md#e-mechanism-integration): D/E samples were printed and accepted; the integrated full case was reported working. Its source preserves the accepted interface dimensions. | Greater bearing separation, different shell stiffness, layer registration and untested fatigue can change the behavior. Translate the local interface rather than scaling it. |
| Printed screw-top closure | [Vaseline container](../../../../model/vaseline_container/README.md#decisions-and-evidence): the full base/lid pair with a 3 mm pitch thread and 0.30 mm nominal radial allowance was printed and reported good. | The actual material and print profile are unknown. Use the geometry as a starting reference, then check the new thread and opening motion. |
| Large plate joined with printed screws | [Book reading plate](../../../../model/book_reading_plate/README.md#what-changed-after-the-successful-l-sample): the sample's thread fit worked; the downward-facing drive socket printed poorly. The revised head-up screw and final plate were reported to print nicely. | The print report does not establish load capacity or long-term creep. Recalculate new load paths and check the drive socket as well as thread fit. |

Add or revise an entry autonomously when a printed result, measured model check,
or repeatable failure can save work on another object. Link to the current
object record and source, state what was actually observed and under which known
setup, and name the boundary of transfer. Keep detailed measurements and trial
history in the object directory. Remove or correct an entry when later evidence
supersedes it; do not append session narratives or untested clearance rules.

For slicer path and orientation examples, consult the separate
[historical printability lessons](../../orca-slicer-printability/references/case-lessons.md).
