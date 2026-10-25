# R9: negative relief at the eight octagon vertices

## User intent and retained control

The user says R8 is okay/not bad, is an improvement, and should be kept. They
clarify the remaining issue: in the octagonal end view, the winding's outward
vertices remain prominent and feel/look like sharp notches after the spring is
pulled apart. This is distinct from whether the swept cord section is round.
The requested next variant should bite negatively into those exterior vertices,
with modest depth and retained printability. Preserve R8 source and exports.

The feedback refers to extension and tactile/visible notches, but does not explicitly
confirm that R8 was physically printed or identify print settings. Record the
acceptance and concern without promoting its print status. R5 remains the explicitly
printed working control; R7 remains printed/rejected, and the circular direction
stays discontinued. This phase supplies one short 25.2 mm sample, not the deferred
~70 mm version or a thickness comparison batch.

## Geometry choice

R8's R0.5 convex blend only recesses an ideal 135-degree octagon vertex by about
0.041 mm along its bisector. Increasing the same small edge break would not make
the requested negative bite clear. R9 instead cuts eight identical axial scallops
centered on the true outward vertex bisectors, through both the helical circuits
and existing integrated terminal loops.

Depth is 0.55 mm radially inward from the original sharp R5 vertex. Each mouth
extends 1.0 mm to either side in the vertex's transverse tangent coordinate.
The control remains R8; it receives this subtractive operation without changing
its broad-face cord section or the inner octagonal roof. At the corner center,
about 2.91 mm radial material remains between the new surface and original bore
vertex. This nominal geometric ligament is not a strength or fatigue rating.

A raw circular gouge would introduce two abrupt cut lips. Instead use two mirrored
cubic Bezier segments: zero radial slope at the recessed center and a slope matching
each original adjacent facet at the mouth. Their meeting is smooth, and their
shoulders join the straight facets tangentially. Small rounded shoulders remain
below the old outline; the point is recessed rather than replaced by sharp lips.
Each cutter is extruded along the spring axis. It is a genuine negative corner
cut, not a new swept cord profile, an isolated bed flat or a flat zigzag spring.

Retain 14 mm across the broad facets, 7.6 mm inner across-flats bore, 3.2 mm nominal
cord dimensions away from corners, 4.4 mm pitch, 1.2 mm nominal turn gaps, five
circuits, horizontal placement and integrated end loops. Corner-to-corner size
reduces intentionally. Eightfold nominal end-envelope symmetry is retained;
the advancing helix is still chiral.

## Planned evidence and physical decision

Use the existing supplied Q2C/solid TPU setup, 0.4 mm nozzle, 0.2 mm layers,
Classic, three walls plus 100% fill (or the user's high-wall solid approach),
supports/brim/ironing off. The short flat feet remain, but corner removal shortens
them; check the retained local 5 mm² per-middle-foot contact screen. Check the
local 1 mm turn-gap screen, winding material, complete terminal loops/open bores,
and all eight unchanged inner facet planes. Neither screen is a calibrated TPU
clearance or adhesion threshold.

Sample all eight corner recesses at several radial/axial locations to distinguish
R9 from retained R8. Check each new floor leaves material behind it and removes
material that R8 retained; do not judge the cut only from outer bounding size.
Review the actual end section, a close-up overlaid with R8 and the actual bed/roof
paths. No extension-force, load capacity, tactile comfort or notch-elimination
rating follows from CAD or slicing. The useful print comparison is whether
extension exposes less pronounced corner tips without new weak bends, sticking,
roof defects or lifting. Keep terminal joins intact when freeing the sample.


## Final CAD and selected-profile evidence

CadQuery 2.8.0 reports valid geometry and completed matching horizontal STEP/STL
exports. OrcaSlicer 2.4.2 accepted the centered layout using the existing complete
supplied Q2C/solid-TPU profile triplet: 0.4 mm nozzle, 0.2 mm layers, Classic,
three walls, 100% rectilinear fill, supports/brim off and reference 230/35 °C.
No filtered notices were reported. The automatic support probe still generates
support/interface through Z11.2 mm; that flag is retained rather than called a
physical support-free verdict.

Twenty-four middle material/gap witness sets and eighteen terminal centerline
witnesses pass; terminal bores remain open and the source guard confirms connected
terminal/middle material. All eight inner facet planes are present. Each of the
eight negative-cut witnesses distinguishes R9 from R8 at 0.25 mm below the old
tip, and material is still present behind each floor. Actual radial line/solid
sections measure 0.55000 mm depth and 2.91366 mm radial ligament at all eight
sampled middle corners, above the local 2.8 mm geometric ligament screen. This
screen preserves substantial material but is not a printed strength criterion.
The actual native Bezier tool tangents match the neighboring facet slopes
±tan(22.5°), with zero slope at the mirrored floor join; no sharp mouth tangent
change is introduced in the outer-band cut profile.

Four sampled middle feet each have 5.81473 mm² planar bed contact, above the
retained 5 mm² screen. Total contact is 35.20153 mm², 67.2% of R8's 52.38406 mm².
Local turn clearance is 1.19015 mm, unchanged from R8 within numerical precision
and above the retained 1 mm screen. Flat-foot length reduces deliberately; this
material/contact tradeoff is the reason to keep this a short comparison print.
It does not predict adhesion or extension life.

The final isometric/end views and actual R8/R9 corner comparison were opened.
They show broad original facets, an unchanged inner octagon and a visibly recessed
vertex with tangent shoulders. Gray is retained R8; teal is R9, both representing
the same single-material concept. Only R9 is in the printable result. The actual
bed/middle/roof/support path plot was opened: six separate short footprints remain.
All 105 primary bridge midpoints at Z11.2/11.4 lie in representative current-layer
CAD material at 0.005 mm tolerance. This bounded check covers neither all paths
nor complete bead widths.

The automatic-probe interface midpoint review contains 452 segments. Of these,
191 lie outside the smallest nominal 7.6 mm across-flats bore projection, at
mid-heights Z2.7–3.3. Their maximum radial distance from the axis is 4.619 mm,
well inside the new exterior cuts, which begin at radial distance at least
7.027 mm. The nominal bore projection omits axial bevel clearance; this is a
spatial diagnosis of the internal beveled/gap regions, not proof of contact or
support necessity. Together with the opened support/roof path plot and retained
inner geometry, this leaves the original internal roofs/bevels as the supports-off
experiment rather than evidence that the new exterior scallops need supports.
Do not infer physical removal quality from the probe.

## Shared checks and handoff reflection

Repeated faceted-coil material/gap, terminal, inner-plane, flat-contact and local
clearance checks now live in the object-owned `coil_checks.py`. R8 and R9 call the
same functions with explicit 5 mm² contact and 1 mm gap screens; bridge midpoint
review takes explicit placement offsets and tolerance. The helpers neither build
models nor write artifacts. R9's review checks the unchanged R8 control in the
same run and compares its metrics/witnesses against retained R8 results. Its
control gap, total contact and winding witnesses match the prior record. The
refactored R8 review entry point was also rerun successfully against its retained
Orca run; its JSON check record and path image remained byte-identical in Git. This
avoids copying another entire geometry-check script; it is not a new generic
verification framework or a changed acceptance threshold.

The phase's useful correction is to distinguish a winding vertex from a swept
section edge and a small convex edge break from a negative recess. R8 remains
retained, and its parametric model plus printable files are unchanged. Record the
user's acceptance without inventing an explicit print confirmation. The physical
finish line is a comparison of extended notch feel, integrity and printing with
R8; digital depth, contact and tangent evidence cannot settle that feel.


## R9 physical feedback — 2026-10-25

The user explicitly reports printing R9: it works okay, nothing particularly
wrong, and feels improved because the edges are less obvious when extended.
Record the short sample as printed and working with a tactile improvement.
Exact spool/settings, measured recoil, strength and fatigue life remain unknown.
Keep the delivered R9 geometry and its historical digital receipts unchanged.
No further cord revision is requested; the ~70 mm version remains deferred.
