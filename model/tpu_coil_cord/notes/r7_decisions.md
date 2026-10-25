# R7: flat-sided swept section on a circular winding

## Corrected intent and rejection

The user explicitly rejects R6 before printing. They do not want round cord
with isolated shaved contact patches. Flat inner, outer and end-facing sides
must belong to the swept section and run continuously along the circular
winding, including its terminal loops. This is a design-interpretation rejection,
not an observed printing failure or a material defect. R6's CAD/slice receipts
retain their narrow historical meaning; R6 is not an active print suggestion.

The accepted R5 remains a physically printed control. The new sample retains
five circuits, 25.2 mm relaxed length, 3.2 mm section dimensions, 1.2 mm nominal
axial gaps, horizontal placement, integrated closed terminal turns, solid TPU
and 0.4/0.2 mm manufacturing assumptions. The roughly 70 mm version remains
deferred. Connector SVG work is unchanged.

## Geometry

R7 sweeps a rounded-square 3.2 × 3.2 mm section with 0.6 mm corner radii.
Straight lands on all four section sides are 2.0 mm long. The radial faces
therefore have a straight axial-width land both inside and outside; axial faces
also have straight lands. Quarter-circle corner blends remove the sharp section
vertices without eliminating those lands. The same section closes both terminal
loops. No exterior clipping box, post-sweep flat trimming or attached foot exists.

The winding centerline is circular, mean radius 5.9 mm. The nominal outer diameter
is 15 mm and bore is 8.6 mm. Flat section sides swept around a circle make smooth
continuous inner/outer bands, not globally planar faces around a circle. This
local section meaning is the user's clarified distinction from R6. The end view
is circular; the radial/axial middle-turn section exposes the flat lands. The
chiral winding advances along the axis, so whole-helix mirror symmetry is not
claimed. The section itself has perpendicular mirror axes.

## Contact and manufacturing interpretation

Do not reintroduce shaved feet to satisfy R6's planar-area screen. In horizontal
placement a circular outer band is curved around the winding but straight across
the section's outer land. Its ideal zero-height bed contact is a tangent line
across that land; deposited first-layer width is finite. Review the actual native
section at Z0.1 mm, midway through the 0.2 mm first layer, and the sliced first-layer
paths. A first-layer section is not a measured adhesion/contact patch.

Keep supports, brim and ironing off, Classic with three walls plus 100% fill
or the user's high-wall solid approach. A brim/support mesh could join neighboring
turns and complicate freeing. The round inner roof remains a bridge/overhang
experiment; flat-sided swept cord does not eliminate the circular bore's slope.
Exact spool, Cura settings, sag and adhesion are physical unknowns. There is no
claim of increased return force, maximum extension or load rating.

## Evidence strategy

Use native winding/gap/bore witnesses and the retained local 1 mm clearance screen.
To distinguish the corrected profile from the rejected round cord, sample material
0.05 mm inside each radial face at ±0.8 mm axial offset along its 2 mm straight
land, at eight angles on three middle circuits. All 96 witnesses should be material
in R7 and empty in R6 after aligning their axes. This negative control catches
the earlier mistaken round-section architecture, rather than merely checking
validity or a positive gap. The actual middle-turn section view should show four
straight sides with tangent rounded corners. Witness first-layer land width
across ±0.8 mm at Z0.1, and inspect separate bed paths and roof support locations.
CAD export and slice evidence remain separate from visual acceptance and printing.

## Construction diagnosis and resolution

The first sketch-based section attempt moved the workplane origin and revolved
about the wrong axis; this failed immediately. After fixing placement, both the
sketch and explicit tangent-arc wire represented the requested rounded square,
but direct helix/terminal unions returned valid incomplete or empty geometry.
Changing operand order, periodic seams, fuzzy union, exact NURBS conversion or
terminal sweep representation did not provide a valid complete result. Partial
terminal arcs retained material but were invalid, so no such geometry is delivered.
These were kernel/construction diagnostics, not design or physical variants.

An overlap-supplement union initially looked successful: material survived at
both end origins and in the middle, the shape was valid, and flat-section witnesses
passed. The first-layer plot exposed a half-foot at the first end. A complete
terminal-perimeter check then found much of the first eye absent. This candidate
was rejected before handoff. A single surviving end-origin anchor was too narrow
to establish a closed attachment loop.

The final construction keeps the complete right half of that end construction,
rotates a copy 180 degrees around the vertical line through the axial midpoint,
and joins them on the shared midpoint plane. For this integer-circuit circular
helix, the rotated copy reproduces the same centerline and section on the left.
Both integral eyes therefore come from the complete right-end construction; no
coincident first-eye union is required in the delivered half. The temporary
construction's unneeded first half is discarded. These booleans partition the
body for robust construction, not to create isolated exterior contact patches.

The source guard now covers both complete terminal perimeters at 30-degree
intervals and the middle. The independent local review also samples inner/outer
flat-section material around both eyes, verifies their bores are empty, and checks
the middle winding and clearance. The explicit rounded wire uses straight lines
and tangent quarter-circle arcs for clear section intent. No dimensional
perturbation, loose mesh compound or arbitrary tolerance increase is used.


## Final delivered evidence

Final CadQuery 2.8.0 geometry is valid, with matching horizontal STEP/STL exports.
OrcaSlicer 2.4.2 completed the centered, supplied-profile Q2C solid TPU slice:
0.4 mm nozzle, 0.2 mm layers, Classic, three walls, 100% rectilinear fill, supports
and brim off, reference nozzle/bed 230/35 °C. No filtered notices were reported.
The automatic probe still proposes support/interface inside the roof through
Z11.6 mm. The intended supports-off print accepts that roof experiment; the
probe is not dismissed as a false positive or promoted to a physical verdict.

Twenty-four winding/gap/bore witness sets pass. All 96 middle flat-land witnesses
pass on R7, with zero material hits at corresponding samples on rejected R6.
Both eyes pass 120 perimeter/flat-section witnesses and retain open bores. The
source also guards connected material around both entire terminal perimeters.
Four sampled middle sections at Z0.1 mm have about 6.16762 mm² material area and
retain the expected axial land width. Local turn clearance is 1.19089 mm, above
the retained 1.0 mm geometric screen. All 54 bridge midpoints at Z12 pass the
bounded 0.005 mm current-layer CAD screen; no full-width/path guarantee follows.

The final isometric/end views, actual middle-turn section and actual path image
were opened after the corrected exports. The first layer now has six complete,
separate footprints, including both end loops. Blue paths are ordinary extrusion,
orange are primary bridges or automatic-probe supports, gray is the prior roof
layer. Source and sliced-input associations were checked against the final native
report; the local result stores source and reviewed G-code hashes.

Handoff reflection: separate trajectory shape, section shape and printing contact
before choosing construction. Record the user's clarified flat-section meaning
with its cord-specific scope. Positive validity and middle-only witnesses missed
a partial end eye; whole functional material checks now protect both terminal
loops. These are CAD and interpretation lessons, not physical TPU calibration.
The existing evaluator, native inspection and local G-code reader suffice. The
new path-plot helper stays with this object's reader; no generic execution or
verification framework was added. R6 stays rejected and R5 stays an accepted
printed control. R7 has no physical print report yet.
