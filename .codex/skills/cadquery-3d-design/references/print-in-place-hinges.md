# Opposing conical pivots for a flat-print case

Read this example when a captive hinge must print without supports. It is one
option, not a default hinge specification or a guaranteed printable profile.

## Start with the whole object's orientation

The sunglasses case's earlier standing orientation helped its hinge but left
an overhead cavity wall with an approximately 87 mm bridge. Printing the case
open 180 degrees with both broad exterior panels on the bed removed that roof.
The hinge then had to work with a horizontal rotation axis. This illustrates
why a locally printable joint does not establish a printable complete object.

## Replace the unsupported rod and roof

Two fixed ears carry short, inward-facing conical pivots. A moving receiver
between the ears has matching recesses that capture those pivots. Sloping webs
connect the ears to the shells. In the chosen print pose, the cone undersides
and socket roofs grow along 45-degree surfaces instead of introducing a floating
horizontal rod and a broad flat ceiling.

First establish each feature's start and supporting geometry from CAD. Inspect
generated layers only when discretization or path generation remains uncertain.
A short pin can still start in air; shortening a rod alone does not fix that.
Check moving-part bed contact, persistent gaps, socket wall thickness, swept
motion and axial capture separately. A rounded crown can soften the hinge's
exterior while retaining tangent sloped undersides; a fully circular underside
would need its own support review. Angles alone do not guarantee print success.

## Interpret clearance and physical evidence

For these 45-degree conical mating faces, a radial offset measured at fixed
axial position has a surface-normal gap equal to that offset divided by sqrt(2).
Ear-end clearance is a separate axial dimension. Name and document both so a
request for a tighter hinge changes the intended interface.

The user successfully printed the earlier coupon with 0.7 mm radial cone
clearance and 0.6 mm ear-end clearance, then requested less play and a rounder
exterior. The revised 0.6/0.5 mm gaps and rounded crown passed CAD and slicer
checks but had not been physically retested at handoff. These values describe
this PETG case; they are not general clearance recommendations.

Both the coupon and complete case use the same hinge builder. The coupon keeps
local wall sections, webs and print orientation, but does not test the full
case's latch or compression resistance.

## Evidence

The completed revision is preserved at Git commit `c2fe963`. Consult its
[design and print notes](../../../../model/sunglasses_case/notes/printing_and_design.md)
and [slicer review](../../../../model/sunglasses_case/notes/support_free_review/report.md)
for dimensions, toolpath evidence and limitations; linked working files may
change in later revisions. Use the PrusaSlicer skill for investigation commands
rather than duplicating them here.
