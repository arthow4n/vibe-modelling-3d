# Historical printability lessons

These observations came from archived PrusaSlicer reviews. They illustrate
geometry and evidence questions; they do not set OrcaSlicer thresholds or the
current printer volume. Use the [OrcaSlicer skill](../SKILL.md) for new reviews.

## Path roles need geometric context

A bridge-role path can run over internal infill, and its reported length can
include anchors. In the flat sunglasses case, roughly 184 mm bridge-role paths
crossed infill inside a 3 mm panel; they were not 184 mm free-air spans. In an
earlier standing orientation, an overhead cavity wall produced roughly 87 mm
bridge-role paths and made that orientation unsuitable for the requested
support-free print. Inspect the CAD span and the material beneath and at both
ends of a path before changing the design. See the
[sunglasses history](../../../../model/sunglasses_case/notes/mechanism_history.md).

The same trials classified a roughly 12 mm loop bridge as overhang perimeter,
while a one-sided keeper lip received bridge-role paths despite lacking two
anchors. A clean slice did not prevent physical keeper droop and poor seating.
The accepted design side-printed the keeper tooth so its locking face grows
from the bed. Detect one-sided retaining projections in CAD before slicing;
path labels alone cannot establish support or surface quality.

## Inspect mesh topology only for a specific concern

Exact conical hinge tips on the sunglasses case produced degenerate STL
triangles although CAD was valid and slicing raised no warning. Small flat tips
resolved the mesh defect. Check the final mesh components and mating features
only when a current feature shows a specific defect risk that the slicer cannot
settle; do not make mesh-topology inspection routine. See the
[sunglasses history](../../../../model/sunglasses_case/notes/mechanism_history.md).

## A printed screw's drive socket is also a fit-critical surface

The book-plate user's first screw had usable threads but a poorly printed,
difficult-to-drive head socket. Its head-down print pose placed a roof over the
shallow pocket. The revision printed head-up with a deeper socket and a conical
head with a matching seat; the changed seat load path was recalculated. Check
both the fastening interface and the tool-engagement surface when selecting
orientation. The [final plate record](../../../../model/book_reading_plate/README.md#what-changed-after-the-successful-l-sample)
contains the geometry, print plan and limits.

## Allow for generated print aids near bed limits

The model bounds alone did not describe the dental case's generated brim and
supports. The historical review measured deposited paths including half line
width and compared X, Y and Z independently with that review's printer profile.
For a new layout close to bed limits, inspect Orca's preview with the selected
profile instead of routinely parsing G-code.
Its accessory clip also raised a loose-extrusion warning on the production
plate but not on a mixed coupon plate; adding a supporting pedestal resolved
the local growth problem. Review the delivered layout, and use the selected
printer profile's effective volume for new checks. The
[dental review](../../../../model/dental_travel_case/notes/slicer_review/report.md)
records the original diagnostic evidence.
