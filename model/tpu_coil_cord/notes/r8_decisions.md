# R8: return to the working octagon with softer exterior edges

**Retained by the user.** Latest feedback calls R8 okay/not bad and asks to keep
it. The new request is a separate R9 with negative cuts into the outward octagon
vertices, addressing protruding notches after extension rather than the cord
section shape. An explicit R8 print confirmation was not supplied; do not infer
a print from this acceptance. See [R9 decisions](r9_decisions.md).

## Physical feedback and scope

The user printed R7. The model looked okay, but the print had many defects, so
they discontinue the circular-winding direction and return to the working
"Octo 1", identified here as accepted R5. Exact defect locations, mechanism,
spool and settings were not supplied. Do not relabel this as a proven roof,
adhesion, tolerance or material failure. R7 is Yes / printed but rejected;
it is not an active print suggestion. Its CAD/slice evidence remains historical.

R5 is explicitly still working. The new request is cosmetic/edge refinement,
especially outside, while keeping the octagonal idea. One 25.2 mm short TPU
sample remains proportionate; the ~70 mm variant is not resumed. Retain 14 mm
across flats (~15.15 mm across corners), 3.2 mm radial/axial cord, 1.2 mm nominal
turn gaps, five circuits, closed integrated terminal turns and horizontal solid
TPU setup. Existing R5 source and exports are retained unchanged.

## Options considered and selection

Recessing corners with extra straight bevels would reduce corner prominence but
create more visible ridges. Replacing the winding with many shallow facets or
large rounded transitions would move back toward the circular-print direction
the user just rejected. Tiny texture or cosmetic grooves would add geometry
without addressing the ridge silhouette. The selected direction is small convex
exterior blends, preserving substantial broad facets and the faceted inner roof.

The delivered model applies R0.5 blends only to convex edges in the outside
section zone, including the path's exterior ridges and exterior cord/chamfer
junctions. The inner half remains faceted. Concave terminal intersections are
excluded so rounding does not add material into the turn gaps. The selection
uses facet-normal offsets and local convexity, not saved face/edge numbers.
The intended outcome is a recessed, tangent transition replacing a sharp ridge,
not a fundamentally round cord or winding.

## Manufacturing checks and physical limits

Keep solid TPU, 0.4 mm nozzle / 0.2 mm layers, Classic, three walls plus 100%
fill or the previous high-wall-count solid approach, supports/brim/ironing off.
Rounded bed-adjacent exterior edges can reduce contact area and introduce local
curved transitions; preserve and measure the substantial remaining bed facets.
Use the retained local 5 mm² per-middle-foot geometric screen and 1 mm turn-gap
screen. These are design screens, not adhesion or TPU tolerance calibration.

Check connected material around both integrated end eyes, open bores, middle
winding/gaps, the retained eight inner facets and local exterior recession.
Review final isometric/end shape and selected slice paths. Native geometry and
slicing cannot establish the printed reduction in visible edges, clean release,
adhesion or force recovery. Compare the new print with the accepted R5 sample.


## Final evidence and handoff reflection

Native geometry is valid in CadQuery 2.8.0, with matching horizontal STEP/STL.
OrcaSlicer 2.4.2 accepted the centered layout under the existing complete supplied
Q2C/TPU profile triplet. Effective settings retain 0.4 mm nozzle, 0.2 mm layers,
three walls, 100% rectilinear fill, supports/brim off and reference 230/35 °C.
There were no filtered notices. The automatic probe still proposes supports
through Z11.2 beneath the roofs, like the R5 reference. Keep supports off for
the small comparative experiment; the probe does not prove either successful
support-free TPU printing or the cause of R7's defects.

Twenty-four winding/gap witnesses pass. Eighteen terminal centerline witnesses
and both open-bore checks pass; the source also guards connected terminal/middle
material after filleting. All eight inner facet planes are retained. Twenty-four
recession witnesses sample 0.01 mm inside R5's original outer miter peaks: all
are material in R5 and empty in R8, confirming real exterior relief rather than
a display-only normal change.

Four sampled middle feet each retain 8.61631 mm² planar contact, above the retained
5 mm² geometric screen and about 92.9% of R5's 9.27838 mm² per sampled foot.
Total planar contact is 52.38406 mm², about 92.8% of R5's 56.46766 mm². These
fractions describe geometry, not an adhesion force/rating. Local turn clearance
is 1.19015 mm, above the retained 1 mm screen and essentially the R5 value.

The final complete isometric/end views, magnified actual corner comparison and
actual path plot were opened. The comparison uses gray original R5 and teal R8;
both are display references to the same single-material print concept, and only
R8 goes to print exports. Separate first-layer feet and middle-turn paths are
retained. All 105 bridge midpoints at Z11.2/11.4 lie in representative current-layer
CAD material at 0.005 mm tolerance; this does not check complete bead widths or
every deposition path. Blue paths are ordinary extrusion, orange bridge/probe
support, gray the prior roof layer.

The first corner-view request failed because the display assembly's root used
CadQuery's autogenerated UUID name. Its explicit component names were already
present; adding the required explicit root name fixed inspection. Geometry,
exports and slice had completed independently of that view failure. The final
source was reevaluated, with native artifact-identity reuse of unchanged geometry
exports/views and a successful final corner inspection; the native report retains
the final source association. The inspection anchors now derive from dimensions.

Reflection stays local to the print feedback: R7's digital success did not make
its print acceptable. The user explicitly reconfirms R5 works, so preserve its
faceted architecture and vary only exterior edge treatment. The preference
record now makes that direction clear; no universal TPU radius, tolerance,
adhesion or print-defect diagnosis is inferred. Existing CAD, native inspection
and object-local path tools were sufficient; no new shared framework was needed.
The physical decision is whether the exterior looks/feels less edged while
retaining R5-like print quality. R8 is not physically qualified by these checks.
