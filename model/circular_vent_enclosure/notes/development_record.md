# Vent enclosure development record

The original sections below describe historical V1 at `19ca15f`. The V2 revision
is recorded at the end; the object README owns current print instructions.

The [object README](../README.md) owns current print/use instructions and readiness.
This record retains the decisions and discarded local geometry, not extra print variants.

## Method and finish line

Use exact CAD for nominal fit and forbidden material, geometric sections for an
initial airflow bottleneck screen, and Orca for the actual print layout and
support probe. Flow rate, downstream pressure, acoustic spectrum, actual rim
profile, fixture strength and printed properties are unavailable. CFD, acoustic
simulation and FEM would introduce decisive unknown boundary/material inputs;
they cannot qualify quietness or retention here. Finish a simple parametric V1,
paired print exports, useful views and a smoke slice, retaining those physical
questions explicitly. Single-piece architecture avoids an unqualified assembly joint.

## Interface update

Initial brief supplied Ø130 mm and 35 mm projection only. The user's follow-up
supplied approximately 20 mm rim height plus 15 mm gap to the disc. This replaced
an earlier speculative 25–35 mm emission band with the complete approximate
20–35 mm band. It does not identify a grippable Ø130 mm cylinder. The swept Ø130 mm
CAD envelope is deliberately a nominal collision reference, not measured valve CAD.
The 6 mm collar remains behind the air band. Fit clearance of 0.8 mm diametral
provides insertion room, not a holding-force source.

## Material reduction

The first 213 × 85 mm construction used 2.2 mm shell / 2.8 mm front, eight short
front ribs ending at radius 88 mm, and 46 × 37 mm windows with 45° roofs and R2 tips.
Its nominal projected exits were 93.62 cm². CAD solid-volume mass at an assumed
1.27 g/cm³ PETG density was 262.24 g, with 0.1562 N·m wall-axis gravity moment.

The user explicitly requested reducing material while retaining function. The
selected version uses the brief's lower shell/front thicknesses, 2.0 / 2.4 mm,
with eight 2 × 3 mm ribs extending into the R3 floor/wall blend and rounded rib
crests. Without the final window revision, this was 234.01 g; the delivered shape
is 233.27 g, 11.05% below the initial solid-CAD estimate. No measured plastic
density, strength or dynamic panel response is implied. Six top/bottom layers
make the front solid at the selected 0.2 mm layer height; other infill remains 7%.
The earlier default diagnostic profile estimated 203.32 g, but had fewer solid
face layers. Its mass must not be compared directly with the final 220.88 g slice
as an equal-stiffness material comparison. The 11% comparison is geometric under
the same assumed density, not a measured filament saving.

## Window/support refinement

The original slice completed without notices but the automatic-support probe
created tree support up to Z43.0, around radii 98–101 mm under the rounded window
tips. Reviewed the retained probe G-code using the shared
`physical_analysis.manufacturing.orca_linear_paths` reader; this was a local
support-location diagnostic, not a footprint or mesh audit. Supports could be
accessed through the openings, but removing the local need better fits V1 intent.

The final roofs rise 1.5 mm per tangential mm (56.3° from horizontal), use 0.65 mm
tip rounding, and extend the window height to 43 mm to preserve area (94.60 cm²).
General window corners remain R2 and exposed lips R0.65. The final selected-profile
auto-support probe generates no support. There is no broad horizontal bridge;
physical tip closure and PETG sag still require a print. This is local evidence
for this geometry/profile, not a universal printable tip radius or angle.

## Geometric flow screen

Measured actual post/window rays on the CAD. The uncut revolved interior is
axisymmetric; window cuts remove material and cannot reduce its circular core.
Two rays separated by half the window pitch cover a post and window under the
8-fold symmetry. Rear radial clearances are recorded at selected heights, and
four downstream sections at 2 mm intervals screen the entrance to the forward
chamber. A separate continuous annular keepout boolean checks 12 mm radial
clearance through the entire 20–35 mm band.

The local rear-band annular area of 58.34 cm² is not a complete-flow throat:
air enters throughout the 15 mm axial gap. The nominal source cylinder area
2π × 65 × 15 = 61.26 cm² describes only that idealized source geometry. Once past
the disc, the added annular section is at least 134.87 cm², the conservative front
turn area is 182.15 cm² (using the gap above ribs everywhere), and nominal projected
exit area is 94.60 cm². Projected area does not capture contraction, edge losses,
unequal outlet flow or the complete 3D minimum hydraulic section. Actual pressure
loss and noise remain unmeasured. None of these numbers is an airflow rating.

## Structural and use screen

With the density assumption, the delivered shape weighs about 2.29 N. Its geometric
centroid gives 0.1385 N·m gravity moment about a wall mounting plane with horizontal
axis; ceiling withdrawal differs. No friction coefficient, contact preload,
attachment capacity or load rating is available, so no analytical retention PASS
is claimed. The loose collar carries no demonstrated load.

The front has eight shallow radial supports joined into the shell blend instead
of an extra baffle. The 2.4 mm solid front satisfies the brief's thickness floor;
its stiffness/resonance is unqualified. Do not pursue a speculative modal solve
without relevant pressure/acoustic loading and a useful acceptance criterion.
Removal gives direct rear access for rinsing and inspection; drainage depends on
actual installation orientation and needs observation.

## Parametric and software review

Shape building writes no files; CAD publication stays in the shared evaluator.
The dataclass rejects nonfinite/nonpositive dimensions, invalid shapes/counts,
insufficient roof height, excessive taper and invalid height stacks. Unknown
variants are rejected by the shared product-verification CLI. User intent is
preserved in `brief.md` and its reviewed verification inventory. Physical and
subjective obligations stay UNKNOWN; nominal CAD PASS cannot satisfy them.

Construction spot checks: six windows at width54/height45.5 and eight teardrops at
width42/height55 both built valid CAD. They were not exported or sliced, and do
not inherit the delivered eight-pointed-window print evidence. Invalid shape,
roof slope, engagement and rib-count inputs were rejected. The standard entrypoint
conformance suite passes all 12 tests for this product.

Final review covers actual delivered STEP/STL geometry, placement, supplied profiles
and tool identities through the native evaluator's publication guards. The final
source review adjusted a fixed window-height restriction into a shoulder-relative
limit and made cutter depth follow hood/bore radii, so those parameters remain
usable. Rechecked final exports after these changes; no hand-edited mesh or STEP.

## Reflection

The consequential lesson is local: preserve the known emission band's clearance
before optimizing plastic, and compare mass on an equivalent geometric/process
basis. A smaller rounded window tip and steeper roof removed a concrete support
signal while preserving outlet area. Existing tools and guidance covered this
work; no shared API change or general manufacturing rule is justified by V1.

## V2 — lighter hood and long-contact adjustable clamp

The follow-up authorizes further material reduction while preserving functionality.
The user also asks for more rim contact and compliant clamping to tolerate modest
measurement error. These two requests remain active together. No physical print
report or new rim-diameter/profile/strength measurement was supplied.

### Architecture and material decision

Simply extending the old narrow collar from 6 to approximately 16 mm would push
its contraction into the 20–35 mm emission band. A separate ring lets the hood
have a broad Ø160 mm rear mouth at wall height 17.5 mm while gripping the rim over
16.7 mm. One M4 × 25 screw and nut close the slit. Three M3 × 10 socket-cap screws
and captive M3 nuts seat the hood on supported lands. This adds occasional screw
removal for cleaning, but avoids a force-sensitive printed latch and preserves
the clamp adjustment when removing the hood. Standard 3 mm and 2.5 mm ball-end
Allen tools are specified; stock fastener lengths are available, head type is not
confirmed. No printable tool is provided.

The front remains 2.4 mm solid with eight 2 × 3 mm ribs. The curved body is shorter
and thinned to 1.4 mm; the mouth and clamp band remain 2 mm. This is a deliberate
revision of the initial approximate 2 mm shell preference under the new material
request, not a rewritten user thickness criterion. Critical path coverage is
inspected on actual Orca layers rather than inferred from wall settings alone.
The delivered total solid-CAD estimate is 216.37 g versus 233.27 g for V1 (7.24%
less under the same assumed 1.27 g/cm³ density). Final print comparisons use both
parts and all selected support material; steel hardware is separate.

An intermediate unflanged ring left a large annular shortcut around the broad
hood mouth. It was rejected on whole-object airflow grounds despite clear valve
fit and bolt paths. The final 0.8 mm split flange fills that rear annulus, with
positive radial overlap at every declared diameter. A continuous rear annular
witness checks that only a small residual opening remains, mainly the intentional
clamp slit. A large opening after deleting the flange fails that check. This is
not an airtightness claim. The contact band plus flange end behind the open
20–35 mm band. The flange is printed against the bed; the grip band and supported
tab braces grow upward. It is also part of the ring's compliance/load path, not
just a cosmetic cover.

### Contacts, attachment and release

The stationary rim contacts the clamp's cylindrical inner band. Turning the M4
screw draws the ears together and contracts the slit, supplying a designed normal
load source. The split permits compliance; the broad contact distributes load
along the fixed rim. The ring is not supposed to grip the adjustable disc. The
0.5 mm insertion bevel is on the rim-entry edge, and M4 clearance is intentionally
5 mm to accommodate ear rotation, not presumed printer inaccuracy.

The hood lands seat against the ring tabs/flange, and the M3 screws provide axial
preload. Their heads are wider than the slots. Nut channels prevent rotation and
retain the nuts once screws engage. Slot clearance accommodates expected tab
movement; screw tightening removes play. To clean or inspect, remove those three
screws and lift the hood axially; undo the M4 screw only to remove the clamp.
There is no cantilevered snap tongue, unsupported latch start or speculative
friction-only loose fit.

The provisional Ø129–132 range is a geometric engineering choice. A preserved
neutral-arc, constant-curvature pose hypothesis includes the band and thin flange
cross-section in its neutral-radius estimate. It is used to size bolt slots,
not predict real deformation or contact pressure. Tab roots, local ears,
ovality, printing and friction can alter real motion; adjustment/retention remain
physical questions. Seven geometric diameters cover the declared range, while
screw preload can close a little beyond first contact before the slit bottoms.
A positive 0.1 mm normal-interference command is used only to identify a preload
source with the shared friction screen; missing stiffness and friction leave its
holding-force result unknown. No torque target or retention rating is invented.

### Fit, airflow and mechanics screens

Actual assembled CAD clears the nominal Ø130 × 35 envelope and a continuous
12 mm radial band over wall heights 20–35 mm. The front footprint remains solid.
The projected outlets remain 94.60 cm², front turn area 182.15 cm² and front rib
clearance 44.6 mm. The downstream circular-core section is 127.58 cm², still above
the exit area. Inlet-band sections near fastener lands are conservative inscribed
circles, not full-flow throats; inflow joins along the band. No hydraulic or
acoustic prediction is inferred.

Native CadQuery assemblies through `assembly_geometry.Configuration` share the
installed hood/clamp relationship. Checks cover seated forbidden overlap at all
seven diameters, actual bolt-shaft/slot clearance, and axial withdrawal after
removing screws. Rear flange overlap is retained at the diameter extremes. The
nominal thin-flange ring strain estimate is a uniform-curvature sensitivity only;
local peak strain and creep are not established.

The solid-CAD wall-axis gravity moment is approximately 0.127 N·m. Five newtons
is a provisional low-load screen (roughly 0.5 kgf, above the roughly 2 N assembled
weight), not a user handling specification. The nominal nut-roof net section is
14.88 mm², giving about 0.34 MPa if one roof alone carries 5 N. This is a demand
estimate, not a calibrated PETG allowable or load rating. The underlying fixture's
strength is unknown. Ceiling installation instead puts weight into withdrawal.

### Tool and printability corrections

Early support webs obstructed the M3 heads and driver. A recessed head seat and
short driver reliefs now preserve side webs while admitting the standard 2.5 mm
ball-end key's 25° approach. The full 3 mm shaft envelope is checked through the
windows at Ø129, 130 and 132, rather than assuming a visible head can be reached.
The window bottoms move forward to print Z4 mm; their height/area and roof slope
remain unchanged, and they remain forward of the disc plane. The relief cuts stop
inside the chamber. Whole-object print/fit checks are repeated after those edits.

A combined corner fillet on all pad transitions failed; treatment is restricted
to the broad pad seating perimeter. The clamp's insertion bevel is constructed
as a conical bore cut, avoiding a failed global chamfer over rounded slit ends.
These are local topology corrections, not shared tool changes.

V2 accepts a few grams of accessible support under recessed screw seats and any
nut-channel roof where the selected Orca process proposes it. It is not described
as support-free. The large rear mouth gives access before assembly; nut channels
open radially. Actual path views and support heights are retained with the final
manufacturing inspection. Physical support removal and PETG finish remain open.

### Handoff reflection

Retain the solid acoustic-facing panel first when trimming plastic. Greater rim
contact cannot be obtained by extending a narrow printing collar into the air
opening. The later rear-flange correction also shows why clear fit and successful
local fastener checks cannot substitute for the complete flow path. Both failures
are now guarded locally. Existing geometry, execution, slicing and manufacturing
readers were adequate; no shared API or universal printable-wall rule is warranted.

Final selected slices estimate **175.40 g hood + 33.18 g clamp = 208.58 g PETG**,
including the chosen supports, versus V1's 220.88 g: **5.57% further reduction**.
Estimated times are 4 h 21 min and 1 h 02 min on separate plates. The hardware's
unweighed steel mass is additional. Source/parameter review also rejects clocking
that would join a mounting land across the clamp split, preserves wrapped angles,
and requires the flange end to match the seating plane. These guards leave the
selected geometry unchanged; its paired native publication was re-associated
before the final path report. Selected-profile wall sections retain three paths
at Z16 and five at Z42, with under 0.08 mm uncovered in the local width-based
coverage approximation. Support tops are Z65 in the hood screw recesses and Z5
in the flange-first clamp nut channels; the saved actual path views were visually
reviewed. Both are accessible before assembly. Fit, grip, surface release and
operating airflow/noise are the next physical evidence, not further CAD ratings.

Source association review: the staged whitespace check removed only an extra
blank line at EOF from `vent_parameters.py` after CAD publication. Its parsed AST
is identical; exported geometry and the selected slice remain unchanged.
Published parameter SHA256 `26381d0a526fb059345d1b8c12b4e4d93c1b743f51e80f190dae0f8d1f0bc6ac` → formatted `b0c5d8988391cd9462950ca07de2d6569c90ad464e08b4d1100c758481e823fc`. The final path report
records the formatted source; this is no new physical qualification.
