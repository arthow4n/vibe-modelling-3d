# R5 short faceted coil: next physical experiment

## User feedback and scope

The user printed R4, says the idea can work, and reports turns sticking together
with defects. They ask for substantially more spacing but reasonable relaxed
compression. They dislike outer-only flat patches on an otherwise circular
tube, and ask for both inner and outer outlines to be flat/faceted, possibly
8- or 16-sided. A faceted rather than circular swept cord section is explicitly
acceptable. R4 adhesion, recoil, load response, exact print settings, spool and
printed hash are not reported; do not invent those observations.

The next authorized deliverable is one approximately 20–30 mm short sample for
faster physical iteration. The approximately 70 mm spring remains a future user
intent, explicitly deferred. No 70 mm R5 model/export is supplied in this phase.
Keep the roughly 15 mm transverse size, horizontal placement, symmetry, solid
TPU and integral terminal loops. Prior sources and their digital/physical
records are retained as history rather than promoted to clean-print success.

## Selected geometry

Use a regular octagonal transverse centerline with 5.4 mm apothem. The cord has
3.2 mm axial and radial width with 0.8 mm corner chamfers, giving an eight-sided
section with 1.6 mm flat lands and 45-degree chamfers. At polygon corners, scale
radial section coordinates by the exact miter factor sec(22.5°), implemented by
the corner's transverse coordinates divided by the centerline apothem. This
makes the outer and inner wall facets parallel octagons, rather than clipping
only the outer shape of a round tube. The miter preserves constant wall thickness
normal to each principal facet; the corner's diagonal section is naturally wider.

The outer octagon is 14 mm across flats and about 15.15 mm across corners. The
inner octagon is 7.6 mm across flats. The winding rises 4.4 mm along X per full
circuit, from 3.2 mm axial material plus 1.2 mm nominal gap. Five circuits give
22 mm centerline rise plus the 3.2 mm end envelope: 25.2 mm total relaxed length.
This is a continuous 3D winding, not separate stacked rings or a planar zigzag.
Closed terminal turns share the same envelope and section; no outboard frames,
feet, tabs or separate assembly parts are added.

The 1.2 mm gap is a deliberate threefold step from R4's still-sticking 0.4 mm,
not another small unqualified adjustment. It is also much larger than R3's
failed 0.15 mm. Cord occupies most of each 4.4 mm pitch, keeping a compact
specimen. No minimum gap is calibrated and no claim is made about the cause of
sticking in the user's unreported Cura toolpaths. Actual stringing/sag, spreading
and release still require printing.

Choose eight sides over sixteen for substantial bottom lands and 45-degree
shoulders around the bore. Sixteen would add shallow faces near the ceiling.
Octagonal inner roofs still include a short flat span, approximately 3.15 mm
between the inner roof corners; this is a remaining bridge, not eliminated
unsupported geometry. The chamfered cord removes the round section's changing
underside slope. Flat lands and the 135-degree polygon corners are intentional
print geometry; no marginal cosmetic fillet removes the base. Corner strain,
printed bonding, stiffness, recovery and fatigue are unqualified. No guessed
TPU modulus or structural solver is needed to choose the small print trial.

## Construction and early check

An initial fixed-binormal pipe sweep over the sharp octagonal 3D path produced
an invalid winding; the planar terminal sweep was valid, but the body and union
were not. That attempt is not delivered. The source now uses exact matched
miter profiles at every straight segment boundary and ruled lofts between them.
The axial position advances continuously by transverse path length, and the
same profiles are reused by neighboring segments. Fusing these segments and the
closed terminal turns produced valid native geometry. A retained-material guard
protects the middle winding before publication. No tolerances, alternate mesher
or ad-hoc environment were introduced to force conversion.

This exact polygonal representation keeps the questions interpretable: are the
inner/outer walls actually faceted, do the flat feet remain substantial, and do
adjacent turns have the intended clearance? Use native CAD for those decisions
and the existing Orca workflow for toolpaths. No full mechanical simulation is
used to predict printed spring return.

## Checks and manufacturing assumptions

Keep the same Q2C, 0.4 mm nozzle, 0.2 mm layers, Classic generator, solid TPU and
automatic bridge-direction setup. Three walls plus 100% fill, or the user's high
wall count, preserves solid material. Reference process speeds are 25 mm/s for
walls/fill and 15 mm/s for first layer/bridges. No brim is selected because it
could join neighboring footprints. No supports are selected because TPU support
in the bore and turn gaps would add difficult cleanup; the short roofs must be
tested. Actual Cura settings remain unknown.

Use the existing 5 mm² native planar contact trial screen per sampled middle
foot, not an adhesion calibration. The 1.0 mm local gap screen is chosen for this
1.2 mm nominal experiment, replacing prior smaller geometric criteria. Test
material on the winding, empty gap locations, open terminal bores and connected
end-to-middle material. Check all eight directions for BOTH inner and outer wall
facets on the completed CAD. The actual model views answer form/symmetry; display
geometry is not the engineering check geometry.

Because repeated sticking could also involve bridge paths, review the actual
primary bridge deposition. At the known centered placement, test each bridge-
labelled segment midpoint against CAD at representative layer mid-height. Use
0.005 mm tolerance for the absolute STL deflection (0.003 mm) plus G-code
rounding, not as an engineering gap allowance. This is a bounded check for
sampled bridges crossing empty coil gaps, not full bead-width verification or
a complete deposition audit. It cannot diagnose the prior user's unknown G-code.

## Final evidence and physical decision

The final source is valid in CadQuery 2.8.0; STEP and STL are paired in the same
horizontal placement. OrcaSlicer 2.4.2 completed the centered primary TPU slice
with supports off and no filtered notices. Reference nozzle/bed temperatures
are 230/35 °C, not spool calibration. The native report owns the exact supplied
printer/process/filament identities and source/artifact association.

All eight inner and eight outer planar wall directions are present in the
finished geometry. Twenty-four material/gap witness pairs passed across three
middle circuits. Open terminal bore and connected terminal/middle material
checks passed. A native local adjacent-turn distance measured 1.19015 mm,
exceeding the 1.0 mm criterion. Four sampled middle feet each measured 9.27838 mm²
planar bed contact, exceeding 5 mm². Total contact is 56.46766 mm² for the short
specimen; do not compare that directly with the long R4 total as an adhesion
rating. The new short sample has far less length and material to print.

The complete isometric and end views were opened and inspected. They show
matching inner/outer octagons, faceted cord, five helical circuits, substantial
flat lands and integral terminal closures. Actual bed, side-wall and roof paths
were plotted and opened. The first layer retains separate flat footprints;
the Z7 side-wall layer shows separated faceted sections. Blue means ordinary
TPU extrusion, orange bridge/probe support, gray prior-layer roof paths.

The primary has bridge-labelled extrusion at Z11.2 and Z11.4. All 105 checked
bridge midpoints lie in representative current-layer CAD material; no sampled
midpoint crosses a coil gap. The automatic support probe still generates Support
and Support interface under the roofs through Z11.2, which remains a review flag.
Do not claim faceting removed support generation. The selected supports-off
sample accepts a short-bridge/sag uncertainty for physical testing. Reference
path acceptance does not verify Cura, GUI STEP import, adhesion, clean release
or material recovery.

Cool before freeing middle turns gently; leave terminal joins intact. Report
whether the larger spaces stay open, whether the flat roofs sag, whether the
base stays attached, and only then whether the feel/recovery is useful. If
printing is clean, this geometry can inform a later explicitly requested 70 mm
revision. If it still sticks or bridges fail, revise geometry/process using that
observation; do not resume the long version just because this slice completes.

Handoff reflection: R3 and R4 show that positive geometric gaps and completed
reference slices do not calibrate TPU separation. R5 makes a substantial gap
change and changes BOTH inner and outer geometry while shortening the specimen.
Those are product-local decisions from the print report. No new universal TPU
gap, material property, software root cause or adhesion threshold is inferred.
The existing evaluator, G-code reader and native evidence are adequate; no shared
solver or framework extension is justified.
