# Current alternatives — 2026-10-14

The cylinder has a plain shared cavity, with **no separators, clips or organizers**.
The R2/C case instead keeps two brush grips and positive closed retention. Both
use PETG; the reported successful old socket interface is preserved. The new
27.3 mm bore and 25.4 mm nominal mouth are each 3 mm smaller than the old CAD clip.
These are CAD parameters; fillets and printed tolerance still need a fit test. The inferred
27 mm grip target is not a new measurement of the brush.

| Alternative | Closed size | Printed parts | Intended use |
| --- | --- | --- | --- |
| Plain cylinder | 264 mm long, 94.4 mm main diameter, 100.4 mm joint diameter | 2 | Simple protection and shared storage; threaded axial midpoint joint and 16 shallow grip flutes |
| Rounded R2/C case | 263.8 × 132 × 66 mm shell, front latch extends width to about 136.7 mm | 12 | Hinged access, two brush grips, foot gates and lid keepers; links recessed behind narrow rear slots |

The cylinder is the simpler option. Its 88 mm bore packs the original 30 mm brush
handle beside a conservative 60 × 44 mm tube cross-section, separated by 0.5 mm.
Usable height is 259.2 mm versus the reported 255 mm brush. Approximate dimensions
and actual tube deformation still require a physical fit check. There is no
numerical crush rating, calibrated wet-grip result or seal claim for either design.
Pack dry items. Floss remains optional spare-space storage.

## New printable layouts

Each source selects the same geometry and placement for its STEP/STL pair.

| Layout | Files and role |
| --- | --- |
| Cylinder joint test | [Python](../cylinder_thread_test.py), [STEP](../cylinder_thread_test.step), [STL](../cylinder_thread_test.stl): two short cups, full thread diameter/clearances and local grip band; assembled height 44 mm |
| Complete cylinder | [Python](../cylinder_case.py), [STEP](../cylinder_case.step), [STL](../cylinder_case.stl): two cups, exterior ends on bed, mouths upward |
| Revised loose grip | [Python](../r2_handle_clip.py), [STEP](../r2_handle_clip.step), [STL](../r2_handle_clip.stl): quickest clip test, compatible with the existing printed socket |
| R2 integrated section | [Python](../r2_section_test.py), [STEP](../r2_section_test.step), [STL](../r2_section_test.stl): 44 mm axial crop, one hinge station, grip/gate/keeper and relocated production latch; seven parts |
| R2 lower shell | [Python](../r2_body.py), [STEP](../r2_body.step), [STL](../r2_body.stl) |
| R2 upper shell | [Python](../r2_lid.py), [STEP](../r2_lid.step), [STL](../r2_lid.stl) |
| R2 accessories | [Python](../r2_hardware.py), [STEP](../r2_hardware.step), [STL](../r2_hardware.stl): two clips, two links, two long body pins, two shorter lid pins and two gate pins |

Do not print the inspection assemblies. Do not print duplicate sample hardware
if reusing it in the full case. The main cylinder pair fits one plate; print the
R2 shells separately. The reference Q2C's 270 mm bed leaves little axial margin
for a 263.8 mm shell and 3 mm brim: use the checked placement/profile and check your
actual printer's usable area.

## Assembly and informative tests

**Cylinder:** use the dedicated [cylinder print/test instructions](cylinder.md).

**R2:** print the revised clip in the existing socket first if useful. Check
insertion, holding and comfortable removal with the actual handle. The integrated
section then checks the new socket foundation, gate, closed keeper, one folding
link and latch together. The real handle passes through its open axial ends.
It omits the other hinge station, full panel flex, head clearance and axial end
stops; a successful local test does not validate the complete case.

Print clips feet down, links flat, all pins head down, shells exterior-panel down.
Assemble the two short pins into the detached lid and links first. The two longer
pins enter the lower joints from the case ends through the recessed
access ports. Their split/barbs must face along Y (across the circular bearing),
not toward the teardrop roof. Squeeze only the split free arms during insertion;
comfortable elastic insertion is still untested. Do not force a cracking pin.

Slide each clip into its preserved dovetail socket from negative X, seat it
against the backstop, and drop its small gate pin stem downward into the blind
bore. Inserting the brush traps the gate pins. Closing the lid places keeper caps
above the handle: geometric lift space is less than the clip's escape height.
This positive closed retention supplements the clip lips and does not depend
only on foot friction. Remove the brush before withdrawing gates or grips.

Pull the curved front latch outward to release it. Guide the lid out/up and rotate
it to flat open; the two-joint folding mechanism is manually guided, not a
synchronized one-axis hinge. Check the small section for binding, pinch points,
release effort and comfortable motion before printing the full shells. Rear slots
recess the links; the hinge is less exposed but not invisible or watertight.

For the complete case, confirm actual head/button clearance, close the case, then
try gentle inversion and shaking before backpack use. Closed retention depends
on the latch staying shut and PETG parts recovering properly. Force, fatigue,
creep, subjective bulk and protection against real pressure remain unmeasured.

## CAD, manufacture and physical limits

Cups flare outward from a broad flat bed patch. R2 posts/access recesses have
teardrop crowns; isolated hinge alcoves keep contents out of link travel. Raised
socket foundations are tapered, while exact mating lips and clip feet retain the
successful baseline interface. The altered foundation's stiffness is unqualified.
Lid keepers grow from its bed panel. Cylinder groove ends taper to avoid abrupt
refill ledges; thread flanks are sloped. Nominal valley walls are 2.2 mm on the
main cylinder and at least 2.1 mm at the female groove/collar region.

Straight-beam analogies screen grip, pin and latch deformation below an
agent-selected 1% strain screen. This is not a measured PETG allowable strain,
force prediction, fatigue qualification or full curved-flexure simulation.
Snap-pin admission uses opposed localized tip barbs: a split full circular barb
remained oversized in the unsplit direction. The admission proxy translates free
arms inward, leaving the head/root fixed; it does not model elastic transition.

Cylinder native CAD clears 61 helical poses at 30° increments, subsequent loaded
lift, and blocks an unturned axial pull. R2's tessellated axial sections only
shortlist a route; complete native loaded CAD, including pins, gates, clips,
contents and table, governs sampled-route acceptance. End-corner sections were
added after a small native collision escaped a coarser section search. A sampled
route is not continuous-motion or dynamic proof. Latch release uses an explicit
free-leaf clearance proxy with the root fixed, not a physical deformation result.

The shared [verification entry](../verification.py) declares `rounded-c`,
`plain-cylinder` and historical `measured-two-lane` explicitly. Questions needing
actual prints remain UNKNOWN. Slice evidence qualifies STL path acceptance for
its specific diagnostic PETG setup; it does not validate GUI STEP import, actual
fit, bridge quality, materials or use. STEP remains the primary interchange.

## Physical print status

| Item | Print status | Artifact(s) | Physical evidence/remaining checks |
| --- | --- | --- | --- |
| Test piece(s) | Partial — baseline clip and socket only, reported 2026-10-14 | Baseline introduced in `47b5862`, exact printed export unconfirmed | PETG, 0.4 mm nozzle, 0.2 mm layers; local socket insertion worked. New clip, section and threaded test **not printed** |
| Final printable object(s) | No | New R2 and cylinder layouts above | Actual fit, retention, effort, print quality and travel protection pending |

See [attribution](provenance.md). Historical measured-case exports and SVG/section
studies remain historical evidence, not the new assemblies' qualification.

The whole-form review inspected closed front/rear and loaded flat-open CAD views,
plus the cylinder exterior. The R2 rear slots reveal recessed links; tall isolated
hinge pockets add internal structure and width. The cylinder avoids that
complexity, and is the simpler recommendation for the user's plain-storage goal.

The user objected to desktop GUI use during support review. Remaining inspection
in this session uses headless slicer output and native CAD; no user-display viewer
will be reopened.


The original full-motion [native report](r2_before_foundations_verification.json)
passed 193 poses but flagged the old support probe. A headless dump of
[actual support paths](slicer_review/r2_support_roots_before.svg) placed support
only under the lower bearing bases (Z=0.2..2.2 mm). Those bases started at the
2.4 mm cup floor while their rear edges extended beyond it. Four narrow foundation
feet now carry them to the bed. The original complete builder, moving actors and
route remain unchanged; input/function fingerprints protect that retained motion
basis. Native Boolean checks confirm only material below the old base plane was
added, and a separate 193-pose check clears the added feet. This retains the valid
full route evidence while explicitly qualifying the manufacturing correction.

All seven printable layouts have completed OrcaSlicer 2.4.2 smoke slices and
support probes, with **no generated supports and no notices** in the final
receipts. The diagnostic setup is Qidi Q2C, PETG, 0.4 mm nozzle, 0.2 mm layers,
two walls, 7% adaptive cubic, 3 mm outer brim, no skirt, centered without rotation.
Temperatures, flow and speeds remain diagnostic. The current full declared
[R2 report](r2_verification.json) and [cylinder report](cylinder_verification.json)
keep unprinted physical questions UNKNOWN. Exact source-to-export association
was reviewed: the retained lid/accessory/clip exports select unchanged geometry;
body, integrated section and inspection assembly were regenerated after adding
feet. Successful baseline clip/socket mating geometry is retained without
claiming the revised foundation's stiffness or smaller grip is physically tested.

The [closed R2 inspection STEP](../r2_case_assembled.step) and
[closed cylinder inspection STEP](../cylinder_case_assembled.step) are display
poses, not print layouts. Updated R2 [front](../renders/assembled/r2_case_assembled_isometric.png)
and [rear](../renders/assembled/r2_case_assembled_isometric_back.png) views show
the recessed lower pin access and bed foundations. The [flat-open view](../renders/assembled/r2_open_view_isometric.png) shows the
loaded contents, keeper caps and folding links.

The shared assertion adapter was also corrected after an assertion without a
message produced an empty evidence summary and interrupted independent checks.
It now returns FAIL with the check ID and continues independent checks; 31 focused
verification tests passed. This is an evidence-reporting fix, not a design pass.

The pre-correction support dump preserves the relevant actual paths. Raw G-code
and temporary GUI-inspection files were removed after review.
