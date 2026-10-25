# R4: clearance and symmetric contact after the R3 print failure

## User evidence and selected change

The user canceled R3 mid-print after observing merging spiral lines and lifting
from the bed. They name Cura 3D and insufficient adhesion, but exact settings,
plate, material preparation, printed hash and the root cause are not known.
Do not diagnose a slicer defect or assert a fully tested print. R3 is a failed
partial print, superseded as the current next trial. Its native slice success
and 0.1494 mm CAD clearance did not establish printed separation or adhesion.

The user requests a little more spacing and more actual contact surface. Exact
circularity is relaxed, but at least two symmetry axes are required, preferably
more. Retain the approximately 7 cm length, approximately 15 mm size, thin cord,
horizontal winding and integral terminal loops from previous instructions.

Selected design: R3-like helical core with four identical outer clips, one on
each cardinal side. The nominal envelope is a centered 15 mm circle intersected
with a centered 14 mm square. Its external transverse outline has two orthogonal
mirror axes, two diagonal mirror axes and 90-degree rotational symmetry. The
complete chiral helix is not claimed to be mirror-symmetric. Each of the four
flats is an equivalent resting side, and the supplied placement puts one down.
This preserves a rounded outline and integrated ends rather than returning to
R2's asymmetric house roof and projecting frames.

Use 0.40 mm axial CAD spacing, versus R3's physically merging 0.15 mm. Nineteen
turns at 3.6 mm pitch plus the 3.2 mm end envelope yield 71.6 mm total length.
The untrimmed cord remains 3.2 mm round, with 0.5 mm removed from all four outer
sides. The 8.6 mm bore remains; the maximum round envelope is 15 mm and the
oriented width/height are each 14 mm. The local radial thickness at each flat's
center is 2.7 mm. This changes the local section and therefore may change feel,
strength and fatigue; no inherited force or material rating is asserted.

## Geometry and manufacturing decisions

The clipping planes add real planar bed contact through the middle turns and
both terminal loops. They leave the original cord centerline and inner bore
intact. Keeping the plane/curve edges at the feet is intentional: a lower-edge
fillet would remove the very contact being added. There are no external tabs,
extra rings, sacrificial rails or separate parts. The underlying surface remains
rounded between flats. This is a single-material TPU spring experiment.

Before measuring the candidate, choose a local geometric trial screen of at
least 5 mm² planar bed contact for each of three sampled middle feet: a several-
mm contact patch rather than a mathematical tangent or a marginal line. This is
not a calibrated adhesion threshold. Confirm planar outer faces on all four
sides, and show the actual end view to inspect the nominal symmetry. Retain
positive helical material controls, open terminal bore controls and a connected
material witness through both terminal loops and the middle.

For the spacing change, require at least 0.30 mm shortest clearance in an
isolated native adjacent-turn witness, along with point checks around several
middle turns. That criterion is a geometric guard for the selected 0.40 mm
experiment, not a universal printed gap. Do not carry R3's rejected 0.10 mm
geometric threshold forward as physical qualification.

Keep the 0.4 mm nozzle, 0.2 mm layers, solid TPU and automatic bridge-direction
reference setup. No brim is included because expanding individual foot outlines
would join adjacent turns and reintroduce removal work. Roofs remain curved,
so the automatic support signal and actual roof paths still need review. Filling
the narrow bore and turn gaps with TPU support can make removal impractical;
the selected trial remains unsupported, with sag treated as an open print result.
Actual Cura settings are unknown; Orca evidence describes its supplied profiles.
No temperature, flow, material property or adhesion improvement is calibrated.

The finish line is one revised source/STEP/STL sample with increased native
contact, wider native gaps, a visually reviewed four-flat profile and a scoped
smoke slice. The next physical print should discriminate the two reported
failures directly: whether the part stays attached and whether the turns remain
separate. No structural solver or additional geometry variants are needed to
choose that trial.


## Completed native and path checks

The final source built valid geometry and the evaluator exported matching STEP
and STL in the selected flat-down position. OrcaSlicer 2.4.2 completed the
centered primary plate with supports off and no filtered notices. The same
Q2C/TPU profiles, 0.4 mm nozzle, 0.2 mm layers, three walls and solid rectilinear
material were used. Reference temperatures 230/35 °C are not recovered Cura
settings or measured spool calibration.

All four sets of native planar outer faces are present. Three sampled middle
feet each measured 10.0102 mm² actual planar contact, exceeding the preselected
5 mm² geometric trial screen. Total native bed-plane contact is 200.7818 mm².
This measures real CAD contact, not a generic bounding box or a first-layer
extrusion-width estimate; it does not establish adhesion. The 0.5 mm trim is
retained without edge fillets that would reduce that land.

Twenty-four paired middle-turn material/void witnesses passed across three
turns and eight angles, with empty witnesses at ±0.1 mm about the gap midpoint.
The isolated native adjacent-turn gap measured 0.398127 mm, above the 0.30 mm
geometric criterion. Both end bores remain open, and native material anchors at
the two terminal loops and the middle belong to one connected solid. No printed
clearance or spring-force rating is inferred.

The actual R3/R4 reference first layers show R4's wider multi-path patches,
compared with R3's narrow contacts. The comparison retains R3's old G-code hash;
no R3 rebuild or old receipt was changed. These are Orca reference paths and
cannot identify the exact user's Cura adhesion failure. The R4 roof plot overlays
Z11.6 paths in gray, ordinary Z11.8 paths in blue and bridge-labelled TPU in
orange. The support probe still creates Support and Support interface roles
from Z0.2 through Z11.2, including material under the bore roofs. This is a
reviewed manufacturing signal, not an assertion that support has disappeared.
The unsupported trial remains the selected compromise: do not pack the bore
and turn gaps with hard-to-remove TPU supports. Circular inner-roof sag remains
physical uncertainty even though adhesion/contact geometry has improved.

The new path plot batches actual deposition segments with Matplotlib line
collections instead of making one plot artist per segment. It uses the existing
object-owned G-code reader and native reports; no alternate slice reader,
scheduler or evidence schema was introduced.

Handoff reflection: the R3 failure changes readiness and the next geometry;
its valid CAD and accepted reference slice cannot overrule the print report.
The resulting changes target the two observed problems directly, while retaining
integral ends and the requested multi-axis outer-profile symmetry. Keep the
0.15 mm fusion observation local to this TPU setup rather than declaring a
universal printer precision limit. Root cause and calibrated adhesion remain
unknown. Once the final form view is inspected, the next useful evidence is the
R4 physical trial, not more variants or numerical mechanics.


The complete isometric and end-on views were opened: the outer silhouette has
matching flats on all four sides, the inner bore remains circular, and terminal
loops stay inside the winding envelope. Named planar end-section and shortened
terminal cutaway views were also opened using `r4_inspection_views.json`; they
are display-only and do not replace the full printable geometry. The full end-on
hidden-line projection was comparatively expensive (about 278 s in the native
view report), while the focused inspections took about 4 s. Use the focused
section for future local symmetry questions; no computation deadline was applied.

The first quick-view JSON put `title` inside `view`, causing an explicit TypeError.
It was corrected to inspection-level metadata, and both named views then
succeeded. The shared CAD inspection README now shows and distinguishes that
nesting, a narrow documentation correction driven by this concrete failed call.
This changes no geometry or API. Documentation JSON syntax and the actual R4
consumer provide its validation; no unrelated API audit or solver work is needed.
