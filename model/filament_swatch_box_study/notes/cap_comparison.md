# Cap exploration — authorized autonomous phase

## J4/K4 print report — 2026-10-04

Both J4 and K4 were printed. Candidate artifacts are the STEP/STL pairs delivered
in `684ed0e`; actual printed hashes, material, nozzle/layer setup and slicer
settings were not reconfirmed. The earlier PETG/.4/.2 plan is not evidence of
the actual settings for this report.

J4 is preferred for substantially firmer card retention and is considered good
overall. Its upward-facing recesses are good, and its connection key works.
The user initially questioned J4's key, then explicitly withdrew that concern
after checking it again. Do not retain a J4 connector failure claim.
Fully inserted J4 cards still tilt, with reported movement near their bottom.
The user suspects excessive bottom clearance. That is an unverified explanation;
there are no measured clearances or confirmed contact/load-path causes.

K4's retention design is considered reasonable, but it is looser/flappier than
J4. Its upward-facing recesses are also good. Its connection key works on only
one end; the user reports that the other end has no stopping wall. The user
also identifies this form problem in K2, which remains unprinted. Record K2 as
a reported visual/inherited issue, not a second physical print failure. The
exact end identity and underlying CAD cause have not been diagnosed.

Earlier checks established unchanged parent geometry, intended local contacts,
assumed finger access and successful reference slicing. They did not establish
upright alignment in the actual J4 print or useful key capture at both K ends.
Preserving an inherited interface does not establish that it performs its job.
Do not blame printer precision, PETG response or clearance without evidence.

Current instruction: record these results and leave all geometry/exports
unchanged. J4 is the preferred current baseline with an acknowledged alignment
limitation. Future improvements, not authorized for implementation now:

- Investigate J's fully seated tilt and bottom movement before choosing a
  correction; check the clearance hypothesis against actual card seats/supports.
- Restore/qualify key stopping and capture at both K ends before claiming a
  module can join on either end; verify each non-equivalent port in the complete
  base rather than only compare it to the inherited parent.

Keep the accepted G hood and I key 3. No further hood exploration, new variant,
CAD check, slice or physical-analysis run is part of this status update.

## J4/K4 — recessed upward-facing base grips

The following is the pre-print design rationale and narrower virtual evidence.
The later print report above supersedes its untested-use statements and any
implication that preserving K2's sockets establishes two-ended joining.

User-approved direction after J3/K3 form rejection: preserve the original recess
idea, put its bearing face upward, and keep the original outline. J4 delegates
to J2 and K4 to K2, applying the same object-owned `recessed_grips.py` treatment.
The accepted G hood and I key 3 remain the matching parts; the user ends hood
exploration. No new card-support/dome mechanism or connector is introduced.

Restore the old underside cutouts, then cut two upper-open side pockets into the
foot: 18 mm length along Y, 2.2 mm depth from X=±32, nominal floor Z=2 mm below
the unchanged Z=5 hood seat. This leaves a 3 mm side opening under the closed
hood, within the original 64 × 44.8 mm footprint. Side entry avoids needing a
large exposed shelf. The pocket does remove local rim seating material; four
unchanged bearing patches outside the recesses still contact the G rim. About
79% of the original rim-only .05 mm downward-overlap proxy remains. This is a
geometric bearing comparison, not pressure, strength or deformation analysis.

Contact floors face +Z, giving the required downward reaction on the base while
the other hand lifts the hood. Each planar floor has about 22.48 mm² exposed
area. The contact root has a .6 mm round, outer floor edge .35 mm round and
plan ends 1 mm radius. Preserve the existing .8 mm bottom chamfer and perimeter
rounds. The floor increased from an initial 1.6 mm concept to 2 mm so that the
outer rounded edge above that chamfer has .85 mm nominal vertical material,
rather than .45 mm. The inner loaded contact patch is solid to the bed. None
of these dimensions establishes a force/strength rating or comfort threshold.
An initially attempted post-boolean edge fillet failed; explicit circular arcs
in the cutter provide the intended root/contact profile without that operation.

The checked access assumption is a 12 mm wide, 2.6 mm thick distal-pad/nail-edge
nose, with an 8 mm thick outer body kept beyond the hood. Side approach clears
the closed G hood, the base and a joined neighbour at the sampled positions;
pressing .05 mm downward contacts the floor. This is a deliberately small
recess, not a whole-finger pocket. The user must judge reach, actual pad/nail
contact and comfort. The section's large outside block is a reference volume,
not a tab or printed part. The closed assembly view contains only actual parts.

CAD differences prove the card support, broad spring/dome follower, closure
roots, card slots and key sockets unchanged outside the bounded lower side
regions. Added material stays in the original foot; both bases are valid
connected solids. The G hood's sampled lifting path remains clear. Surrounding
stiffness can still affect physical response; previous J2/K2 checks remain
geometric evidence, not printed upright alignment or K dome engagement.

Final FDM rationale: floor-down PETG, .4 mm nozzle, .2 mm layers, two walls and
7% adaptive cubic. Pockets are open upward with no new suspended ceiling; their
floor has ten nominal .2 mm layers, an existing chamfer at its outer underside,
and rounded entry/contact edges. Both final STEP/STL pairs and Orca 2.4.2 reviews
pass without notices or generated supports under the diagnostic Q2C profile.
GUI STEP import and actual grip/card performance remain untested. Use complete
five-card bases rather than a detached grip coupon because opening depends on
the actual hood, closing effort, footprint and joined access. Earlier variants
remain intact. No further hood variant is planned.

## V1 print and recessed-grip feedback

Recorded after the temporary no-command/no-edit pause was lifted. V1 was printed
in PETG vase mode and holds the base. The user rejects its shell stability/feel:
sides are not consistently flat, pressing one makes another bulge, and pressing
produces popping/crackling sounds. Exact artifact hash, mating base, nozzle,
process settings and measured dimensions are unknown. Shell deformation may be
consistent with a thin wall changing shape, but this report does not identify
warping, delamination, print tuning or a material cause. Earlier virtual paths
and catch checks established interface geometry, not a stable-feeling shell.
The accepted G hood remains the chosen cover; the user explicitly does not want
another hood or further hood exploration.

J2/K2 and J3/K3 have not been printed; the user will not print these grip designs.
J3/K3 are rejected for their large outward flaps, despite passing geometric
access/force-direction checks. K3's card mechanism looks plausible to the user;
this is visual feedback, not dome-engagement or grip validation. The original
recess idea is preferred, with the opening moved to the upper part of the lower
base so the exposed bearing face points upward. No outward projections.

Next authorized phase: J4/K4 five-card bases, preserving J2/K2 card supports,
accepted G hood and I key 3, with two upward-facing recessed base grips. Keep
the original exterior footprint, accessible side entry below the closed hood,
rounded contact edges and a solid floor. Check actual closed-hood access and
force direction; do not substitute positive access evidence for acceptance of
the overall form. PETG/.4 nozzle/.2 layers/two walls/7% adaptive cubic remain
the base setup. Earlier variants stay intact; no hood redesign is included.

## J3/K3 — upward-facing base holding ledges

**Superseded form choice:** unprinted and rejected for outward projections.
The following is historical design intent and narrower virtual evidence.

Current user direction: implement upward-facing grips on both J2 and K2. The
user explicitly confirms neither J2 nor K2 has been printed. Preserve those
files; J3/K3 are new five-card trial bases. Reuse PETG/.4 mm nozzle/.2 mm layers,
two walls and 7% adaptive cubic. The accepted G hood, separate V1 vase hood and
I key 3 remain unchanged. The earlier pause for discussion is resolved by this
choice; no new hood, card spring or connector exploration is included.

The original foot extends only .2 mm beyond the closed G hood. Flipping its
underside cut cannot create a comfortably exposed top contact there. Instead,
restore the old cutouts and add two low rounded ledges on the exposed X sides:
7 mm extension beyond the old foot, 24 mm length along Y, 2.4 mm height, 2 mm
plan corner radius, .6 mm top round and .6 mm bottom chamfer. The external width
becomes 78 mm versus 64 mm; depth/module spacing remains 44.8 mm. This local
projection is a deliberate access tradeoff, communicated during work. The hood
remains smooth and the ledges do not surround the entire module.

Operation: contact the upward-facing ledges to hold the base downward; lift the
hood with the other hand. Each exposed planar face has about 144.95 mm² area,
normal +Z, so a normal finger push produces the required -Z reaction on the
base. These are base holding contacts, not hood lifting tabs or clip-release
buttons. On a desk their bed-facing undersides are directly supported. Off-desk
strength, opening effort and skin contact are uncalibrated; no homogeneous beam
or solver result is used to claim a load rating for this short thick ledge.

`upward_grips.py` owns the shared object-specific treatment; J3/K3 delegate to
their preserved parent base and apply the same treatment. Restoration is
restricted below Z=3.6 and near the old X-side cuts. CAD differences prove no
change outside those bounded lower side regions: card spring/follower, upright
rails, slot bottoms, hood seating at Z=5, closure roots and key pockets keep
their checked geometry. Integration can still change physical response; this
is not a new print result or a guarantee of unchanged grip forces.

The targeted CAD checks establish one connected valid base for each variant,
upward bearing area and deliberate downward contact. A rounded bounding volume
20 mm wide/8 mm thick represents a distal finger, with a 4 mm front extent
before contact X=36.5 mm; the rest extends outward. This is an access assumption,
not anatomical or comfort simulation. It is clear of both closed G and nominal
V1 shells at contact and sampled vertical approach heights, and clear of an
adjacent joined module. The existing I key's sampled entry/lift path is clear
of added material. The actual ledge view contains no finger references; the
section includes the bounding volume solely to explain access and force
direction. Inspection references are excluded from printable exports.

Final FDM review: bases and ledges print floor down together. The ledges start on
the bed with a .6 mm bottom chamfer; there is no suspended horizontal shelf to
support. Twelve .2 mm layers form the nominal 2.4 mm height. Exposed top edges
are rounded rather than cut into a narrow nail groove. Existing springs keep
their previous orientation/setup. STEP/STL pairs and final native reference
reviews are retained separately for J3/K3. Both Orca 2.4.2 PETG slices complete
without notices or automatically generated supports, preserving print placement.
Slice success is manufacturing evidence under the diagnostic profile, not STEP
GUI import, printed comfort or a material/load rating.

The complete five-card bases are the useful trials, rather than a detached grip
coupon: opening depends on the actual hood, closure effort, surrounding foot
and joined access. Reuse the already accepted G hood first, press the ledges
while lifting, and compare reach/comfort with one and several cards. J3 keeps
the broad-spring option; K3 keeps the corrected dome option. Also check upright
alignment, actual dome contact for K3, card reinsertion/removal and dwell/recovery.
Neither prior J2/K2 CAD checks nor these grip checks establish printed card
performance. V1 remains a separate unprinted transparency trial.

## Underside grip direction review

Latest user feedback confirms the feature is the two sloped underside recesses,
not the perimeter bottom-edge chamfer. A base has been printed; its exact
variant, artifacts and settings are not identified. The user questions the
recess purpose/direction and says it looks like a misprint. This does not report
that the hood cannot be opened, nor qualify J2/K2/V1 use. Instruction at review:
review and record lessons autonomously, discuss further modelling before doing
it. No geometry, exports, print settings or scripts changed in this review.

The feature is intentional CAD, inherited from E through G/H/J/K and the J2/K2
bases. In `cap_g_module_5.py` and `cap_j_base_5.py`, the cut spans 18 mm along Y,
from the bed-facing underside. Its nominal straight XZ boundary runs from
(X=30,Z=1) toward (X=32.5,Z=3.5), with .35 mm cut-edge rounds. Material remains
above that slope. The exposed face therefore points outward/downward; a
frictionless finger push against it has an inward/upward component on the base.
This geometric force-direction conclusion needs no new CAD export or solver.
The source and retained assembled/underside views establish intentional shape;
they do not diagnose any actual print-quality defect.

Earlier notes called the recesses purchase for the opposing opening grip while
lifting the hood. That claim was not adequately established: holding the base
against hood withdrawal requires a downward reaction, which the underside ramp
does not provide by normal contact alone. Friction, finger wrap around another
face, or gripping the remaining vertical band might still hold it, but were
neither specified nor qualified as the intended interaction. The 45-degree
return helped printability; it did not establish hand-force direction. Earlier
clearance/seating/slice checks remain valid for their narrower questions, not
proof of usable opening grips. There is no tolerance or printer explanation
for this intentional surface orientation.

Recommendation for discussion: first consider removing these recesses and
restoring a smooth rounded lower band for side pinch, retaining the successful
hood, foot seating and key interfaces. That simpler grip would rely on side
friction and still needs a comfort/effort review; it is not a positive downward
ledge. An accessible upward-facing base contact can supply downward purchase,
but simply flipping the recess may put that contact under the closed hood or
compromise seating. A grip to lift the hood belongs on the hood or at a usable
separation seam. These are options, not approved geometry changes. Pause further
modelling for the user's direction. The subsequent J3/K3 section records the
user's choice and implementation; the original review remains failure evidence.

Shared lesson is added to the handling review and reusable-evidence reference:
map each hand to its part and required force, then check accessible contact
normals in the closed assembly. Do not equate a printable recess with useful
release assistance. Preserve prior artifacts and the reported accepted hood.

## J/K print feedback and revisions

Current authorized phase: record the printed J/K failures, preserve the accepted
current G hood and I key 3, deliver J2 then K2 revisions, then a separate vase-mode
hood. Earlier pause is revoked. Use PETG/.4 mm nozzle/.2 mm layers/two walls/7%
adaptive cubic for bases. The explicitly requested vase shell instead needs one
continuous perimeter and no infill; its roof becomes solid bottom layers in the
roof-down print. Work through geometry, checks/views, exports/slice and commit/push
for each variant. Exact user-printed artifacts/settings are not reconfirmed.

Observed J: strong bite, but cards visibly tilt in side view. Its rounded grip
region reaches above the old 14 mm straight-guide height, into the widening
funnel. The virtual checks imposed an upright card pose and checked access and
preload; they did not establish opposing support spanning the load region.
J2 preserves the printed-liked broad panel and adds two front-face datum rails
outside the dome and text areas. Their straight height is 16 mm from the floor,
with the last 2 mm remaining as an entry ramp. Contact lies above and below the
spring's load region; spring, sockets, foot and G hood interfaces stay unchanged.
The measured relaxed grip overlap spans Z=15.18–17.31 mm, compared with
opposing support Z=5.9–18.4 mm. The old straight wall ended at Z=16.4 mm.
The source-card checks cover 15 thickness/slot cases, contact on each rail above
and below the grip, two tilted-pose obstruction witnesses, 88 corrected funnel
poses and nine aligned descent poses. Rigid path checks exclude the spring;
they establish an available guided route, not free-fall insertion or effort.
The paired J2 export and reference PETG slice completed without notices or
automatic supports. The complete five-card base is the next physical experiment:
it preserves spring/root, guide, hood and socket surroundings. Compare sparse
and full rows, side-view alignment, reinsertion/removal and dwell. A smaller
coupon would omit the integration responsible for the tilt. J2 is unprinted;
no new force or lifetime claim follows from preserving the original spring.

Observed K: catch does not clip into the dome, even after trying both card
orientations; it presses the back instead. The old reference independently put
the sphere at holder X=+16 and front=+Y after rotating the outline notch-up.
For the real SCAD item, source X becomes holder Z; if source front +Z faces
holder +Y, source Y must become holder +X. Its dome at source Y=9 therefore
belongs at holder X=-16, not +16. The old combination has determinant -1:
it is a reflection, not a physical rotation. Both the checks and renders used
this impossible reference, and the flat-face FEA did not address orientation.
This is a reference/geometry error, not tolerance, material or printer blame.

The replacement reference constructs the source outline, notch, dome, opacity
steps and face-edge treatments before one -120-degree rotation about (1,1,1).
Engraved lettering is omitted and contact patches must stay outside its area.
K2 preserves the spring dimensions while reversing its lateral placement
and adding opposing upright datums. The source-derived bowl center is holder
(-16, 6.6, 16.4) mm for back Y=-1.4 mm. The full proper source rotation puts its
front toward +Y and notch upward; no independent recess is added afterward.
The actual-card check reaches tangential shoulder contact after 0.25 mm normal
spring travel with no rigid overlap; a 1 mm upward card movement requires more
follower motion. Old K in that claimed seated pose overlaps the real card by
about 30.93 mm³; turning the real card around produces the same wrong-face
obstruction at K2. These negative cases demonstrate that the checker can detect
the reported geometry defect. Relaxed grip overlap spans Z=15.46–17.34 mm,
inside the opposing straight support's Z=5.9–18.4 mm interval. K2 also passes
the 15 real-card thickness/slot cases and the shared sampled entry/mate checks.
Earlier K local mechanics remain narrow historical evidence, not a passed
product result. No new solver is needed to answer the handedness and support
defects: K2's spring is an exact lateral reflection with the same dimensions,
but the old archive is not relabeled as a K2 solve. Full contact sequence,
friction, material response and dwell remain physical questions.

The next K2 experiment is the full five-card base with the accepted G hood and
I key 3 alongside J2. Preserve the real card and correct orientation. Check
shoulder engagement, upright sparse/full rows, all-direction entry and deliberate
withdrawal, then seated dwell/recovery. A cropped fixture would omit the actual
guide, rail and shared interfaces; complete bases are small and directly test
the prior use failures. J and K originals remain untouched for evidence.
K2's paired export and reference PETG slice completed without notices or
automatic supports. The mixed J2/K2 whole-product view uses the source-derived
cards, and the section crosses the actual left shoulder contact at X=-20.4 mm.
Its 0.25 mm rigid panel translation illustrates nominal tangency only; it is
not a solved bending shape. K2 remains unprinted and unqualified in use.

Observed hood: printed and good to use, with no reported problem. Preserve G;
the vase variant is an additional transparency exploration. Match actual inner
wall placement to the base and define retention within a single continuous wall
before selecting its final CAD boundary and slicer settings. Do not merely
change G's wall count or promise maximum optical clarity from vase mode alone.

### V1 — smooth single-wall waist on the accepted base interfaces

Architecture choice: retain both revised bases, their four existing closure
leaves, foot and I key. A flat thin shell cannot reproduce G's hidden pockets
with a single contour. The cheapest complete alternative is a shallow continuous
waist near the catches; it adds no parts or thick external band. Outside X/Y,
rim height and rounded roof stay G's values. At the waist only X moves inward, by
at most .7 mm, with a cosine transition centered at assembled Z=18.9 mm over
Z=16.9–20.9 mm. Module pitch stays unchanged. The upper sides are straight.
For a substantial rim landing, the outside corner radius is 5.8 mm, concentric
with the actual foot's 6 mm round, and a .2 mm XY/radius inset transitions
smoothly over the bottom 1.2 mm. The first draft only touched a tiny part of the
rounded foot's top. Replace that incidental contact with a measured flat
landing, requiring over 40% of the thin rim's area supported by actual Z=5 mm
base faces. Both J2/K2 rigid variants are checked, not just shell distance zero.
The resulting 39.15 mm² contact is about 45.8% of the nominal rim area.
The user was informed of this visible smooth contour tradeoff during work.

Print setup is deliberately consequential: PETG, .4 nozzle/.2 layers, one
.42 mm perimeter, no infill/top layers, four solid bottom layers and 30 mm/s
outer-wall speed. Roof prints down, reusing G's 3 mm outside rounding. Export
the filled envelope for Orca vase mode; the inspection-only nominal shell has
an XY .42 mm inset. This avoids confusing an ordinary hollow CAD wall with the
wall Orca actually generates. The object-owned process snapshot records spiral
smoothing off and support/elephant-foot compensation off. One hood per vase
job. Native effective settings confirm these choices.

The geometry screen finds positive seated interference at all four existing
pads, additional interference during lifting, release by the sampled 2–3 mm
lift, rim seating and passage clearance against both rigid base variants,
actual 2.2 mm cards, K2 panel and I key. Peak idealized leaf translation is
.32 mm. The shared rectangular-cantilever screen uses E=1200 MPa as an explicit
uncalibrated homogeneous PETG assumption; root strain is about .263% and below
the provisional 1.5% design screen. It is not a PETG strain guarantee, FEA or
complete retention-force model. Hood compliance, root shape, layers, friction
and material relaxation remain outside that beam calculation.

The shared evaluator exports the same roof-down envelope to STEP/STL and
Orca 2.4.2 accepts the preserved placement in the Q2C PETG profile. Primary
notices are empty. The automatic-support probe fails solely because Orca rejects
enable_support=1 with spiral vase mode. Retain native review_required=true and
the diagnostic log; mark this probe N/A rather than claiming a pass. The
curved roof/bottom layers reuse the accepted hood's roof form; after the solid
.8 mm roof, its nominal first perimeter radial increment is about .197 mm
for a .42 mm line. Maximum waist increment is about .11 mm per .2 mm layer.
These are geometric overlap screens, not printed overhang-quality results.

Because actual helical paths interpolate whole-layer contours, the ideal
continuous CAD shell is only an approximation. The object-owned path study uses
the shared deposited-path reader, checks the native spiral settings,
single outer-wall role/width and continuity, then interpolates crossings through
each catch's Y plane. The measured local wall difference reaches .05565 mm,
within the .11196 mm one-layer/slope phase bound, rather than an assumed printer
tolerance. It then checks the actual radial boundary against the actual rounded
pad at that height: all four closed overlaps are .07706–.11629 mm; at .8 mm hood
lift they grow to .31906–.32465 mm; at 3 mm lift all are clear. .002 mm pad-section
thickness is explicit. Increasing the phase bound alone could not pass a missing
contact. This is narrower geometric evidence, not measured friction or opening
effort. Store the native G-code compressed and effective settings as diagnostic
evidence, not as a calibrated print job. The slice estimates 10.68 g, 1h16m57s.
At the four measured rim planes, Orca's final contour is level at assembled
Z=5 mm and lands over .2 mm onto the actual base foot. Thus vase mode does not
introduce a one-layer helical gap at those seating locations in this profile.

One small shared extension was justified by this consumer: the old path API
only returned endpoint Z. Inferring start Z from a previous deposited move
would miss non-deposited height travel, even with continuous XY. Optional
`orca_linear_paths(..., spatial=True)` now returns both XYZ endpoints from the
same parser. The planar default and its callers are unchanged. A focused
test includes a rising stroke after pure Z travel; all eight manufacturing-path
tests pass. V1 uses this exact height mode instead of the inferred-height draft;
no new worker, solver or comparison framework was added. The existing
CornerFlowTest likewise uses a solid vase envelope; its old planar diagnostic
slice is not spiral evidence and is not borrowed as qualification for V1.

Full V1 is the next experiment: tall shell/roof compliance makes a cropped
collar misleading for force and feel. Test seating, accidental separation,
deliberate opening, rim comfort, recovery and translucency against G with the
same spool. Preserve G and all older trials. V1 is unprinted and cannot establish
maximum transparency or long-term holding. The shared beam screen and extended
path reader answer these object-specific questions.
The inspected whole-product and relaxed-overlap section images are retained in
`renders/v1_assembled/` and `renders/v1_contact/` with their native reports.
Dense technical lines at the waist are the .1 mm CAD loft section seams, not
extra thickness. The section shows the .42 mm wall and intentional preload;
no solved bending pose is claimed.

The user authorizes exploration, ordinary design decisions and incremental
commit/push until approximately 19:00 Europe/Stockholm on 2026-10-02. They regard
the lower section as broadly acceptable and ask for softer edges. This is concept
acceptance and authorization to work on caps, not a report that the newest corner
seat was printed. Interpret the spoken “button” edge comment as the base's
exterior edge; no release button existed in the supplied lower section.

Preserve all published trials. The new exploration base intersects the current
seating geometry with a 5 mm exterior corner radius and 1 mm upper rim rounding;
slot crests, corner-seat faces and clips stay as designed. Initial setup remains
PETG, 0.4 mm nozzle, 0.2 mm layers, two walls and 7% adaptive cubic.

Architecture screen before detailed mechanisms:

| Direction | User action and practical benefit | Construction and main uncertainty |
| --- | --- | --- |
| A — lift-off hood | Lift cap, browse individually upright cards, replace cap. Lowest part count. | Two printed pieces; four internal stop pads and skirt guide. Unlatched desk cover; actual fit/friction unknown. |
| B — sliding outer enclosure | Pull the standing-card tray clear of its fixed cover. Cap cannot be misplaced. | Tray + housing; more table travel and a front panel. Must check card access and running fit; prior rejected horizontal-packet designs are not evidence for this layout. |
| C — hinged cap with fixed rear wall | Open an attached cap while the cards stay in place. | Four parts: frame/base, hood, axle, keeper. Rear foot, tall wall and open stop add structure; sweep and open stability need review. |

Keep the card rows vertical, notch up, independent of how many positions are
loaded. All closed concepts must continuously cover the cards and use an overlap,
not introduce finger slots into the enclosure. No airtight or water-seal claim.
The cap roof's inner height is 86.8 mm: 4 mm above a nominal-height card at the
highest screened seat, or 3.8 mm above the enlarged 80.2 mm check envelope.
Twenty positions use a 149.4 mm base length, well inside the default Q2C
envelope. Printed five-card prototypes qualify only their actual layout and
interfaces; retain whole twenty-card inspection views to judge the intended box.

A conventional low hinge on a tall five-card hood is doubtful: its front wall
can sweep into the 80 mm cards before rising above them. A top hinge also needs
the rear wall fixed to the base, otherwise that wall swings into the back row.
Do not tune a hinge until its complete card/cap sweep passes. An attached cover
is worthwhile only if the extra frame and handling still make a useful box.

A is complete and committed at `fdc459e`: valid five-card print layout and
component exports, clean reference slices, and rigid seating/lift checks for
five/twenty cards. It is the least costly construction and has unrestricted
card access. Actual skirt fit and unlatched retention remain unknown.

B's complete geometry and sampled horizontal withdrawal pass rigid checks for
five/twenty cards. The front panel, side lips and top lip close the opening with
a 3 mm overlap. The five-card print layout uses the tray floor and enclosure's
closed back on the bed, avoiding a broad unsupported ceiling. The main practical
cost is tabletop travel: a twenty-card tray needs about 157 mm to leave the
housing and should be supported, then placed on the table. It adds a tall front
panel and prevents losing the outer enclosure. No drawer latch or holding-force
claim is made. Its five-card layout passed the Orca 2.4.2 reference slice with
no notices and no generated supports. Physical running fit remains unknown.

C must use a fixed rear wall and a hinge near the roof to avoid the tall-hood
sweep problem. This costs a taller rear frame and an axle/retainer compared with
A/B. Keep its actual contents in the motion check; do not qualify a hinge in an
empty box. A standard printed axle is simpler here than forcing the successful
sunglasses conical print-in-place hinge into incompatible whole-part orientations.
That prior interface is physically useful evidence, not authorization to ignore
the tall cap's roof-down print or frame-floor print requirements.

Physical fit, new spring force, comfortable operation and protection remain
unprinted observations. Commit each reviewable variant as requested, without
equating a rendered or sliced mechanism with physical validation.

## Comparison at handoff

| Variant | Printed parts | Main operation | Practical cost | Recommendation |
| --- | --- | --- | --- | --- |
| A lift-off | 2; only 1 new print if the existing base fits | Lift about 76 mm and set cover aside | Loose unlatched cover | First trial; simplest and best card access |
| B drawer | 2 | Withdraw the tray, support it as it leaves, set it down | About 157 mm withdrawal for twenty positions; tall front panel | Alternative for a fixed desk enclosure |
| C hinged | 4 | Swing hood to the 180-degree stop, browse in place | Fixed rear wall and 40 mm rear-foot reach; axle/key assembly | Alternative when an attached cap is worth the complexity |

C's complete geometry revealed useful integration failures before printing:
the four-wall hood's inner rear corner fillets caught the rounded base during
opening; square hinge crowns obstructed the roof; and a rear-wall top corner
made a small opening contact. The U cavity, beveled crowns and top-front relief
address those causes. The keeper's original long tip touched the fixed wall;
shortening its front reach preserves cross-slot engagement without that contact.
These are deterministic CAD findings, not observed print defects.

An empty open C with equal homogeneous density for both components had only
about 3.3 mm rear stability margin for five cards and 8.2 mm for twenty, before
adding the foot. Equal density is not a justified prediction of a two-wall,
7%-infill body versus thin enclosure walls. The added foot deliberately improves
the geometry. The final check varies fixed-frame effective density to 0.5 and
1.0 of the hood's value and records the empty open-box gravity margin. Those
ratios are assumed sensitivity cases, not inferred from the print settings or
material calibration. They exclude hand forces and do not qualify printed
tipping resistance. Actual empty/sparse-box opening belongs in the physical trial.

Five-card STEP/STL layouts preserve actual enclosure height, interfaces and
contents access. Whole twenty-card renders and geometric checks screen the
intended capacity, without implying twenty-card print validation. No positive
closed retention was requested or added in this exploration: A/B are unlatched;
C has axle capture conditional on its keeper staying installed. All are desk
prototypes. Do not use any of their cap grips as qualified carrying handles.

The broad clip and new corner seats are unchanged by the cap builders. The new
1 mm upper exterior rounding and 5 mm base corners address the user's edge
feedback without changing slot crests or card-contact geometry. Recommend the
cap-only A print first, then choose a direction from actual cover fit and normal
use; simulation or more virtual variants cannot establish that feel.

## D — selected press-on / pull-off direction

The user now asks for a simple cap that encloses the base and stays attached
until deliberately pulled apart. Reuse A's two-piece lift-off architecture;
replace its unlatched skirt with four concealed integral detents, no buttons,
axles or separate fasteners. A matching base adds only shallow exterior grooves;
the broad card clips, guides and corner seats stay unchanged. Earlier A/B/C
remain historical alternatives, not the current requested closure.

Guidance comes from the four-sided skirt lead-in, seating from four end-rim
pads, and retention from side spring pads engaging 0.8 mm grooves. Moving the
rim pads to the ends keeps them from bracing the side flexures. A continuous
outer wall backs the flexure pockets, preserving the covered cavity. A 6.4 mm
lower base band and its underside remain accessible for the opposing pull grip.
Ordinary desk storage and holding the loaded base under its own weight are the
retention task; deliberate two-hand pull should release it without an extra
operation. A provisional 5–20 N pull band guides the screen, not an achieved force.

Keep PETG, 0.4 mm nozzle, 0.2 mm layers, two walls and 7% adaptive cubic. The
four nominal 16 mm-wide, 1.2 mm-thick, 16.2 mm contact-to-root stems use an
explicit uncalibrated homogeneous modulus range of 1000–2000 MPa for a simple
beam screen, conservatively shortening the span by the 0.6 mm root blend.
Expected centred crest travel is about 0.95 mm, screened at 0.75–1.15 mm;
the maximum one-sided bound also includes 0.4 mm guide play, reaching 1.55 mm.
Lengthening the stems and increasing rear relief to 2.4 mm screens that extra
travel and the lower pad's displacement beyond its loaded contact point;
the strain screen is provisional, not printed PETG qualification. Pads are
ramped in both directions. Actual friction, root/wall compliance, creep and
dimensional error remain physical questions; do not infer a retention rating.

Next useful deliverable: one complete matched five-card prototype with the
actual tall hood and base, rather than a latch coupon that omits body stiffness,
guidance, stop loading and opposing grips. Parametric five/twenty-card clearance
checks should cover the rigid shell independently of the intentionally
interfering pads. Check spring relief and actual sliced stem fill before handoff.
Then test empty/sparse/full press-on, own-weight retention and deliberate pull,
including overnight dwell. Defer full twenty-card exports until this fit and
operation are accepted. No further concept variants are needed for this request.

Final D evidence: rigid checks for five/twenty positions find no sampled shell,
seat-stop or contents obstruction. Every relaxed pad contacts the base when
closed and still obstructs a 1 mm upward move; translated pad-only witnesses
clear within the screened 1.55 mm stroke. These checks establish contact-space
relationships, not an elastic release sequence. The 16.2 mm contact-to-root span
uses 15.6 mm for the beam screen after allowing for its 0.6 mm root blend; the
largest 1.55 mm stroke stays within that screen's small-deflection applicability.
The largest predicted root strain is about 1.15%, below the provisional 1.5%
screen. Estimated lower-end travel is 1.85 mm, leaving about 0.55 mm of the
2.4 mm rear relief. Neither strain limit nor material law is printed calibration.

The paired layout, cap-only and base-only exports are valid and each passed the
OrcaSlicer 2.4.2 reference Q2C PETG review with no notices, review flags or
generated supports. Print the hood roof down and base floor down. Thin stems
grow from their attached roots, rear pockets begin beneath existing material in
the print direction, detent ramps grow gradually, and base-groove upper shoulders
return at 45 degrees. No suspended starts or trapped supports are intended.
Exterior corners/rims, mouth lead-in, pad edges and root relief have deliberate
edge treatment; the mating groove ramps remain planar.

The targeted path record addresses the solid-stem idealization only; do not
infer PETG modulus or layer bonding from filled extrusion paths. The complete
five-card matched pair is the next physical experiment. Record cap and base
dimensions/setup, seated hold, own-weight retention, press/pull feel, return and
overnight dwell; use those observations to choose reach or stiffness adjustments.
Actual twenty-row loaded retention and transport remain outside this trial.

## Future ideas — translucent PETG and joined modules

Initial user update, 2026-10-02: the latest prototype was printing; the translucent
spools are PETG. The user requested ideas and theoretical screens only, with
**no modelling until the print finished**. During this discussion they then
reported completion: fit okay, base probably fine, hood too fat even in opaque
filament, and exposed base/bottom and hood/top insufficiently rounded. The hood
therefore needs a form/handling revision; successful fit is only partial success.
Do not preserve the bulky shell merely because its local checks passed.
Exact printed artifacts/settings remain unconfirmed; loaded retention and
release force were not reported.

Continue the concept discussion around that feedback. The future mechanisms
and thicknesses below are possibilities, not accepted or print-ready variants.
No source, export, slice evidence or current print setup changes in this phase.

### Translucent hood

Keep the substantial base, complete enclosure and fully printed construction.
The present D shell has a 6.0 mm sidewall envelope and 2.4 mm roof. The sidewall
envelope accommodates the lower hidden leaves and their relief but continues
above them. Leaf roots are at Z = 31.4 mm. A provisional upper-body transition
around Z = 35 mm would leave the root region intact geometrically; that alone
does not preserve its stiffness or establish unchanged retention. Thinning only
from the inside would retain the rejected bulky outline: the next concept must
also reduce the exterior envelope. Treat opaque-PETG bulk/comfort as a requirement
alongside translucency, rather than making the change solely an optical variant.

| Discussion option | Intended appearance and handling | Main unresolved relationship |
| --- | --- | --- |
| Thin upper body, reinforced lower clip regions; approximately 1.0–1.2 mm upper walls | Slimmer frosted or tinted cover, deeper-coloured lower details; a firm opening grip | Preserve leaf support, roof stiffness and release without retaining an unnecessarily thick full collar; preferred next concept |
| Thin panels, approximately 0.8–1.0 mm, with thicker corners or selected ribs | More light through the panels, visible darker framing; reinforcement may reduce the flimsy feel | Rib locations and roof/perimeter support; all panels remain closed printed plastic |
| Very thin shell with retention moved into the substantial base | Light, flexible cover with fewer bulky features in the transparent body | New base-side flexures and a load-spreading hood rim; larger architecture change, defer rather than assume it improves the product |

Illustrative thicknesses are not a new print agreement. For equally supported,
solid panels of the same material, local bending stiffness scales with t³:
0.8 mm has (0.8/1.2)³ = 0.296, about 30% of a 1.2 mm panel's stiffness;
1.0 mm has about 58%. This is a relative thickness screen, not a prediction of
whole-hood deflection, release force, strength or printed PETG properties.
Do not apply it to the current thick, sparsely filled shell as if it were solid.

Thinner walls are an optical opportunity, not a proportional transparency
guarantee. Extrusion air gaps scatter light, so wall paths and finish matter as
well as thickness; see [Prusa's transparent-print experiments](https://blog.prusa3d.com/3d-printed-lens-and-other-transparent-objects_31231/).
Do not transfer their bulk-lens settings directly to this flexible enclosure.
Aim first for a deliberate translucent finish rather than readable labels
through a glass-clear wall. Tinted hoods also tint the apparent swatch colours;
neutral clear PETG is preferable for viewing colour without an added tint.
No coatings, separate sheets or other materials are proposed.

Form/edge priority after the print report: visibly round the roof-to-side
transition, lower exposed hood rim and base's exposed foot/grip edges. A broad
flat roof is not itself a sharp edge; rounding must address the places fingers
contact, as well as the overall silhouette. Construct the thin shell and its
rounded transitions together, preserving material and card headroom, rather
than applying a large fillet that cuts away a thin wall. Keep mating ramps,
seating stops and card-contact datums dimensionally deliberate. The current
small edge treatments were not adequate physical comfort evidence.

Envelope screen: preserving the current 60.4 × 45.2 mm five-card cavity while
using 1.2 mm upper walls gives approximately 62.8 × 47.6 mm upper exterior,
versus the present 72.4 × 57.2 mm. That is 9.6 mm less on each overall axis,
before rounded transitions or reinforcement. It does not establish the lower
clip-zone footprint; protruding reinforcement still governs modular spacing.

### Closed seam and opening grip

Further user feedback: when closed, the hood does not meet the bottom/base as
desired. The future cover should close down against the base and still allow
deliberate separation. Interpret this as a neat, positively seated lower-rim
seam, with a usable opposing base grip. The exact observed gap/location has not
been measured. Existing D geometry already has four internal pads intended to
contact the base's top rim at Z = 20.4 mm; its skirt ends at Z = 6.4 mm and leaves
that lower band exposed for gripping. That internal stop arrangement does not
establish external lower-rim contact or that the printed pads actually seated.
Do not diagnose binding or shift the existing snap alignment from this report.

Preferred concept: a small rounded ledge/foot on the base, with the hood's lower
rim resting on its upper shoulder. The side outline can meet neatly at this
seam, while a short exposed base band below it remains available to grip.
Rounded finger scoops on two opposite base sides or underneath its edges could
make that grip easier without adding a button. Keep scoops below the closure
seam so the cover still encloses the cards. They must provide useful finger
purchase, not merely decoration or a sharp fingernail slot.

Alternative if a fully flush bottom outline is preferred: extend the hood to
the base's bottom level and provide opposed underside grip recesses in the
base. This removes the exposed band but makes desk pickup and access more
demanding; it is a secondary concept, not an assumed improvement. A separate
ejector or release button adds parts/mechanisms and is not justified while
passive opposing grips could solve the task.

Keep seating, retention and gripping distinct: the ledge stops downward travel,
the printed clips retain the seated cap, and the exposed/recessed grips provide
the opposing pull. Coordinate the ledge height with detent/groove engagement
and revise or relieve redundant internal stops so they cannot leave the rim
hovering above its intended shoulder. Existing nominal pad/snap coordinates
must not be assumed compatible with a changed seating height. Maintain the
four-sided entrance and sufficient wall clearance; rim contact need not require
tightening every vertical mating surface into a friction fit.

For joined modules, keep the grip recesses accessible on the long outer sides
or underside, and place the proposed joins clear of the seating ledge, skirt
travel and grips. Changing the foot footprint affects module pitch as well as
appearance; decide these relationships with the slim hood before detailing a
joint. This requirement is still a concept update, with no new CAD or exports.

### Expandable five-card boxes

User intent: print another small box when needed, join it to existing boxes,
and retain the option to expand beyond a fixed fifteen/twenty-card capacity.
Prefer joining the **bases**, with independently removable hoods, so adding
capacity does not require one long replacement cap. Preserve card insertion,
firm upright seating and opposing cap/base grips. Joins must clear the skirt
and leave each cap's vertical withdrawal accessible.

| Discussion option | Benefit | Cost or uncertainty |
| --- | --- | --- |
| Integral sliding joints along the lower base edges | No additional pieces; join identical modules into a row | Joint assembly travel, cap clearance, empty end appearance and accessible release need consideration |
| Short separate printed keys joining underside/base sockets | Identical boxes, reversible links, tidy unused sockets; all materials still printed | Extra printed pieces and underside access; a flush key must not make the bases rock |
| Expandable printed carrier sections holding plain boxes | Existing boxes might remain usable without new side joints | More material, components and footprint; only worthwhile if compatibility matters |

Provisional preference: short printed keys connecting bases along the row of
card positions. Keep each box independently enclosed. Treat the row as supported
desk storage for now; no joined-row carrying strength is established. Connector
geometry, resistance to sliding/twisting, detachment and any carrying load must
be decided before modelling a joint. The base has only a 6.4 mm exposed band
below the current skirt, so an external joint cannot simply occupy the full
20.4 mm base side without obstructing the hood.

Capacity screen: n five-card modules hold 5n cards. Current D five-card hood
footprint is 72.4 × 57.2 mm; the corresponding base depth is 44.4 mm. Joining
bases directly face-to-face would overlap the hoods. Illustrative 2 mm gaps
between hoods require a 59.2 mm module pitch, or 14.8 mm between base ends.
This gap is a packing assumption, not qualified finger access or tolerance.
Overall row length is 57.2n + 2(n−1) mm: four modules/20 cards occupy 234.8 mm,
versus 162.2 mm for the current twenty-card hood envelope. A future thinner
hood could alter those dimensions; do not freeze joint spacing now. Repeated
end walls and four sets of detents also cost more material than one large box.
Every module remains individually printable as capacity grows; total row length
is practically limited by shelf space and handling, not a fixed card count.

Next concept decision: use the reported fit as a starting point, revise the
bulky outline and uncomfortable edges, and decide whether local clip supports
can achieve the slim form before changing the closure architecture. Revisit
upper-wall thickness and module spacing together. Joined modules remain future
ideas; the completed print does not qualify a joint or establish that a thick
collar is worth keeping. This discussion has produced no new CAD, specimens,
simulation or slices.

## E — thin hood with base-mounted detents

The user now explicitly authorizes a very thin hood and a new matching base,
including closure changes needed for the thin form. Deliver one complete
five-card prototype; keep the proven card seating source and historical D
artifacts intact. Joined modules remain a future option, not part of this trial.
Active work: concept/complete-form review, CAD and interface checks, final paired
exports/reference slice with local path review, physical-status documentation,
then review/commit/push. Physical acceptance is outside autonomous verification.

Architecture screen before detailed geometry: without detents a thin lift-off
hood guides and encloses the cards but cannot meet the requested own-weight
retention. Four integral base leaves engaging shallow hood pockets retain the
existing two-part press/pull interaction without buttons, keys or hardware.
Move flexure space into the substantial base's exterior walls; leave the hood
mostly 0.8 mm, with a short 1.6 mm lower band carrying the pockets. The band is
still much slimmer than D's 6 mm wall envelope. All parts use PETG, 0.4 mm nozzle,
0.2 mm layers, two walls and 7% adaptive cubic as before; the thin walls and
leaves need actual path review, not an assumed infill-based material law.

The rounded base foot seats the cap rim at Z = 5 mm, independently of the
detents or cards. Four-sided entry lead-in and 0.4 mm coordinate-side clearance
guide the skirt. Opposed underside recesses give purchase on the exposed foot;
pull the lower reinforced hood band rather than squeezing the upper panels.
The hood closes on the foot with a continuous visible seam; there are no internal
rim stops that can leave this lower rim suspended. The base guides/seats and
card clips remain separate from the closure leaves. Contents stay upright,
notch up, and the cap lifts vertically clear of the 80 mm cards.

Rough screen: five-card upper hood approximately 62 × 46.8 mm, lower band
63.6 × 48.4 mm, base foot 64 × 48.8 mm, roof around Z = 87.6 mm. A separated
roof-down hood and floor-down base are comfortably inside the Q2C's practical
270 × 270 × 256 mm envelope before final slicing. Main sidewalls and roof are
0.8 mm; paired inner/outer roof rounds are intended to preserve shell material.
Lower band expansion is ramped in the roof-down print direction. Base leaves
grow upward from their roots; cam pads and hood-pocket returns use slopes.

Provisional leaf screen: 12 mm width, 1.2 mm thickness, 14.8 mm contact-to-root
length, shortened by 0.6 mm root blend for the beam approximation. Nominal
crest travel 0.8 mm; the maximum 1.4 mm adds 0.4 mm guide play and an assumed
0.2 mm half-width error, not measured print error. With homogeneous effective
PETG E = 1000–2000 MPa and a provisional 1.5% strain screen, the maximum
predicted root strain is about 1.25%; free-end travel is about 1.70 mm within
2.0 mm rear relief. These calculations screen feasibility, not actual force,
elastic contact passage, layer adhesion, fatigue or creep. Thin-pocket wall
compliance can reduce retention; a complete sample represents that uncertainty.

Before final export, inspect closed/open geometry with real card references and
review the full form, foot seam and grip. Target CAD checks at seating contact,
guidance without detents, card/leaf clearance, pocket skin and rigid translated
pad witnesses; these do not prove the elastic path. The complete five-card
print, rather than a mechanism coupon, is the useful experiment for shell feel,
guide friction, seam contact and four-leaf press/pull operation together.

E handoff evidence: the complete closed/open views with actual reference cards
show the reduced outline, rounded roof, rim seated on the exposed foot and
independent access to standing cards. The card floor/seats are not filled by
the added foot: it is a perimeter ring overlapping only the outer base wall.
Local wall relief alters the exterior card-guide region above Z = 5 mm; the
low corner seats and broad card clips remain from their existing builders.

`check_cap_e.py` passed for five and twenty positions: foot/rim contact, clear
sampled rigid lift with relaxed pads removed, card-envelope clearance, preload
contact and depressed pad escape witnesses at the screened 1.4 mm stroke.
Pocket skin is 0.95 mm. Beam maximum strain is 1.25%, with 1.61 mm free-end travel
and approximately 0.39 mm rear margin. This does not qualify elastic release,
force or printed PETG properties.

The paired export and both component exports are valid and passed separate
OrcaSlicer 2.4.2 diagnostic Q2C PETG reviews: no notices, review flags or generated
supports. The preserved paired layout's targeted requested-width path review
found all 36 sampled sections filled within 0.05 mm, including the uniform
base-leaf spans, 0.8 mm sidewalls and four roof layers. Supports are not intended;
roof/corner rounds grow from the flat roof bed contact, band expansion and
pocket returns are sloped, and the base leaves/cams grow from attached roots.
Toolpaths do not establish isotropic material, optical clarity or comfort.

The experiment is the complete five-card pair, not a separate mechanism test.
Test empty/sparse/full seating, own-weight hold, deliberate lower-band/foot pull,
shell feel and edge comfort; repeat and compare after overnight dwell. Actual
printed status is **Unknown**, with no user report. Full-capacity production is
**N/A** at this handoff. Do not transfer D's reported fit to E, or treat reference
STL slicing as validation of Orca's separate GUI STEP import. Print-status and
current conclusions are also reflected in the object README and root index.

## F — flush exterior, reinforcement inside

The user requests a flat, smooth-to-hold hood exterior. Interpret this as removing
E's raised lower band/step while keeping rounded roof/corners and the very thin
main shell. This is form feedback before any reported E print; it does not
establish a physical closure failure. Deliver a five-card hood and paired layout
compatible with the existing E base, with STEP/STL, useful view and reference
slices. Active work: revised form, affected interface/path checks, exports and
records, then review/commit/push. No new mechanism or print setup is needed.

Reuse E's accepted two-part press/pull architecture. Its 1.6 mm lower wall and
snap-pocket positions remain intact; extend that exterior footprint over the
whole height and widen the upper cavity so the main walls stay 0.8 mm. The new
upper exterior is 63.6 × 48.4 mm, 1.6 mm wider on each overall axis than E's upper
body. The upper cavity is 62 × 46.8 mm. Reinforcement projects inward only at
the bottom, with a 0.8 mm-high transition; no external band or shoulder remains.
Roof and side walls stay 0.8 mm, outside roof rounding 3 mm. Four-sided entry,
foot seating, base grips and all E base leaves/ramps remain unchanged.

This is preferable to thinning E's existing pocket band externally: subtracting
0.8 mm from its 0.95 mm pocket skin would leave only 0.15 mm at the pockets.
Uniformly thickening the whole hood to 1.6 mm would abandon the thin-shell goal.
The modest upper-footprint increase preserves both thin walls and existing
closure geometry. PETG, 0.4 mm nozzle, 0.2 mm layers, two walls and 7% adaptive
cubic remain the proposed setup. Print roof down; the inner band grows inward
over its sloped transition. Paired layout remains comfortably inside the Q2C
envelope; final Orca acceptance is responsible for actual fit with print aids.

Review the outside profile visually, rim seating and withdrawn states with
actual cards, plus snap-pocket skin/escape in the affected hood. E's unchanged
base-leaf beam screen remains a feasibility assumption; wider thin panels do
not establish unchanged closure force or handling. Physical smoothness,
thin-shell feel, appearance and press/pull retention remain untested.

F handoff: front and isometric complete-product views show the continuous
external side profile with roof rounding retained. Five/twenty-card checks
passed rim seating, sampled rigid withdrawal, card clearance, relaxed preload/
withdrawal obstruction, translated pad escape space and 0.95 mm pocket skin.
The E base source and separate exports remain unchanged; no base reprint is
needed if that matching base already exists. Do not transfer physical fit or
force from D, or claim an E/F print that has not been reported.

Paired and hood-only STEP/STL exports are valid, and both OrcaSlicer 2.4.2 Q2C
PETG reviews passed without notices, review flags or generated supports. The
paired path review found all 48 selected sections filled through the base leaves,
0.8 mm sidewalls/roof and blind-pocket skins within 0.05 mm. Requested path
coverage is not actual polymer, optical clarity or material calibration.
Physical status is **Unknown**; full-capacity production remains **N/A**.
Test the complete five-card F hood/E base for smooth handling, seated seam,
loaded own-weight hold, deliberate low grip pull and change after closed dwell.

## Expandable variant — minimal additional parts

The user explicitly has not printed F yet, likes its appearance better and wants
to keep it. Preserve F/E source and exports. Their next request is to think ahead
about a separately expandable version with little additional hardware/material
or assembly burden. This phase is concept discussion and arithmetic only, not
new CAD, exports or a joint-strength qualification.

Recommend repeated base modules with independently removable F-style hoods,
joining along the row of card positions at the short ends. Keep each base
functional alone, with the same fully printed construction. Adding one module
adds capacity without replacing existing boxes, buying hardware or printing
a longer common cover. Do not link the thin hoods together or require a full
carrier frame for the ordinary desk-storage concept.

| Joining approach | Additional pieces | Product/use tradeoff |
| --- | --- | --- |
| One short printed bridge key per adjacent pair; identical female sockets in both base ends | n−1 keys for n modules | Preferred: tidy unused ends, replaceable connectors, possible local disconnection without dismantling the whole row; a broad captured key must constrain spreading, vertical mismatch and yaw |
| Integral male/female base-foot joints | None | Fewest pieces, but exposed unused male ends, wear belongs to the base, and assembly direction can force row dismantling to remove a middle module |
| Shared carrier or rails | Additional carrier sections | Could support carrying, but adds material, components and a second structure; not the first choice for low-overhead desk storage |

Preferred key concept: two short captured rails joined by a bridge, engaging
socket tracks in neighboring base feet and inserted from an accessible side.
It should finish flush with the underside, below the hood seam, with a deliberate
stop/retainer against sliding out. Geometric capture
should resist separation and vertical mismatch; do not depend on friction alone
or claim a finished lock from this description. Side insertion should allow
boxes to stay upright and avoid moving the whole row during expansion.
One sufficiently broad key is preferable to two loose fasteners per join if
the eventual stiffness and access checks support it. Exact geometry remains open.

Sockets belong below the Z = 5 mm hood seat and must avoid the card floor,
corner seats, cap leaves and underside grips. There is only a 5 mm-high foot:
verify remaining floor/track material and usable insertion/removal travel before
committing to the connector. A row of short joints must keep the hood's vertical
opening path and grip access clear. Independent hoods still mean one opening
per module; modularity is a capacity/storage choice, not automatically faster
access to every card at once.

Packing screen from the current F/E geometry: foot width 64 mm and depth
48.8 mm per five-card module; hood depth 48.4 mm. A foot-to-foot row would leave
0.4 mm nominal between hoods, but joint and hand-clearance gaps remain to be
chosen. Four five-card modules/20 cards occupy 195.2 mm before those gaps;
a corresponding single twenty-card F/E foot would be 153.8 mm. The repeated
modules therefore add about 41.4 mm (27%) in row length. These are nominal
envelope calculations, not an assembly fit, deposited-material or cost estimate.
Repeated ends/closures account for unavoidable overhead beyond the tiny keys.

Allowing five- and ten-card modules to share the same end connector reduces
overhead without imposing a fixed final capacity. A ten-card foot is nominally
83.8 mm deep; a 5+10+5 arrangement holds 20 cards in 181.4 mm before joint gaps,
uses three boxes and two keys, versus four boxes and three keys for 5+5+5+5.
For n modules the preferred construction has 2n base/hood parts and n−1 keys;
four five-card modules are eleven printed pieces, adding another is three pieces.
The connector standard belongs to the base end, independent of module length.

Carry versus desk use is still a consequential requirement: a desk join keeps
individually supported boxes aligned; carrying a joined row introduces weight,
cap-release loads, bending and twisting that grow with grip location and row
length. Do not call a captured key a qualified structural joint. Before detailed
CAD, establish whether carrying the group is required, releasability, supported
loads and permitted part overhead. A clarification has been requested while
the independent concept work continues. At this earlier discussion stage no joint
had been modelled; G below now supplies a proof, still physically untested.

## G — compact five-card modules and drop-in connector proof

The user authorizes a connector proof and new five-card variant, preserving all
previous versions and omitting ten-card modules. This is a desk-supported row
prototype. Carrying a joined group remains an unanswered requirement and is not
qualified. The delivered geometry includes one compact base/hood/key layout,
separate components, two-module inspection and a small connector fit sample.

### Architecture and overhead

Preserve the smooth 0.8 mm hood walls/roof, hidden 1.6 mm reinforcement, closure
leaves, rim-to-foot seating, broad card clips and corner seats. Trim 2 mm of each
unused end margin: the five-card entry mouths end at Y = ±16.8 mm and the body
ends at ±20.2 mm, leaving 3.4 mm. The foot becomes 64 × 44.8 mm, versus
64 × 48.8 mm; the matching hood becomes 63.6 × 44.4 mm. Card pitch and height
remain unchanged. G requires its new matching hood/base; F/E files are intact.

With a provisional 0.3 mm foot gap, four modules occupy 180.1 mm, versus
196.1 mm for four F/E modules: 16 mm, about 8%, less row length. This is a
packing comparison, not a filament saving or strength measurement. For n modules
use n bases, n hoods and n−1 identical keys. There is no carrier, separate release
button or hardware. Every base has the same pocket at both ends.

### Connector and normal use

A flat bow-tie head drops into matching open-top pockets in the adjacent feet.
Its wider ends constrain spreading, planar translation and yaw; its pocket floor
stops downward travel. A 2 mm wide arm runs below the hood rim to a rounded tab
outside the long side. The nominal pocket clearance is 0.2 mm in plan. Each head
embeds 1.8 mm
into the foot, leaving 0.4 mm nominally to the tall body for vertical entry. Key
bottom/top are Z = 1.5/4.9 mm; the hood seats at Z = 5 mm. Thus the hoods cover
upward key escape without needing a spring or friction latch. This is rigid
geometry evidence, not a measured restraint force. The tab has rounded plan
corners and 0.15 mm top/bottom edge chamfers. Base foot/hood edge treatment
retains the preceding ergonomic changes.

Place empty bases together on a desk, remove both hoods, align their end pockets
and lower the key until it seats. Then press the hoods on normally. To separate,
remove both hoods and lift the key using its exposed tab. Joining requires access
from above; unlike the earlier sliding concept, the keys are not removable with
closed hoods. Individual hood opening remains clear of the installed key. Keep
the bases on the desk while operating; this is not a row carrying handle. A row
may extend by adding identical modules, but arbitrarily long unsupported spans
are not part of this proof. One open hood is not a qualified key retention state.

The complete inspection shows one closed five-card box and one open box with
three cards, plus the removed thin hood. Port/tab access remains at the long side
and does not add features to the hood exterior. The shorter ends alter frame
support, so earlier D feedback and E beam assumptions do not validate G's grip
or closure. No full-capacity or ten-card model is delivered.

### Rejected underside route

The first underneath sliding-key model passed nominal rigid insertion/capture
checks, but its web clearance left a thin outer capture lip beginning above the
bed. Orca's sample and base slices warned of a floating cantilever and generated
supports. Local support paths placed the issue along the joint lip and curved
port, not on the key. Removing the outer lip with a sloped return lost the
spreading restraint in the CAD check. Stop that route rather than refine a poor
interface: open-top pockets remove concealed roofs and print from the floor up.
The first drop-in head reached 2.7 mm into the foot: cropped fit geometry
passed, but a full-base entry check caught its interference with the tall end
wall. Reducing the embed to 1.8 mm clears that wall. The saved check now uses
full bases for vertical entry and end crops only for the local contacts.
Only the final drop-in source/exports are delivered. Earlier F/E/D versions were
not altered. No reusable shared-tool change was needed; the existing collision
checks and support probe caught the relevant issues.

### Verification and physical trial

[CAD checks](cap_g_checks.json) cover sampled vertical key entry against the full
bases, pocket seating,
planar/spreading/yaw obstruction, hood clearance and covered upward escape; they
also cover compact hood/card withdrawal, closure pad escape and actual pocket
floor material. These are collision witnesses, not strength or force predictions.
[Manufacturing review](cap_g_review.json) retains successful STEP/STL export and
OrcaSlicer 2.4.2 Q2C PETG reference slice reports for the paired layout, separate
base/hood/key and fit sample. All final layouts have no notices or generated
supports. [Local paths](cap_g_paths.json) inspect the thin shell, closure leaves,
key arm and pocket floor. STL slicing does not establish GUI STEP import,
printed clearance, optics, layer bonding or load capacity.

Use PETG, 0.4 mm nozzle, 0.2 mm layers, two walls and 7% adaptive cubic. Print
base/sample feet floor down, hood roof down and key flat as supplied. Separate
files allow translucent PETG for the hood and another PETG colour for the base.

The economical sample contains two actual 8 mm end crops and one actual key,
preserving pockets, floor, outer port shape and print orientation. Place the
ends facing each other approximately 0.3 mm apart and lower the key; check
binding location, normal insertion/lift effort, seam alignment, spreading and
planar play under gentle desk handling. There are no hood barriers on the sample:
upward removal is intentionally free. The crops cannot qualify full-module
stiffness, tall-box handling or closed-hood restraint.

If the connector fit is useful, the complete variant can be tested with two
bases, two hoods and one key. First check card insertion/firm alignment with one,
three and five cards, comfortable gripping, complete hood seating and deliberate
release; then join the pair and compare each hood's opening effort and access.
Closed hoods should block lifting the key; remove both and check that the tab
releases it easily. Record movement separately from any suspected print cause.
Carry, force, durability and long-row behavior remain unqualified. No user print
report exists for G; F is preserved and explicitly not printed yet.

## H — wider connector without a handle

**Later physical result, 2026-10-03:** the PETG connector sample failed. Its key
falls out and there is no useful grip/join. The original handoff below records
rigid geometry and slice evidence, not qualified retention; see the
[physical history](../README.md#physical-history-and-print-status). The intended
0.2 mm normal clearance with no preload supplied no designed side friction.
This was a design omission, not an established printer-accuracy problem.

The user finds G's long arm unnecessary for modules that usually stay joined,
and suggests exploring a larger bow tie. This is form feedback before any
reported G print: retain G, but its prior fit/slice checks do not establish that
the handle is worthwhile. H keeps the compact frame and unchanged G hood.

Architecture screen: remove the arm and its long foot channel. Increase head
width from 10 to 16 mm and waist width from 6 to 8 mm; increase embed from 1.8
to 3.2 mm, making the key 16 × 6.7 × 3.4 mm.
A straight-sided notch above the foot clears top-down entry and sideways escape
after a 4 mm relative lift. The notch begins beyond the last card clip relief
(17.6 mm), at Y = 18.85 mm. Keep the 0.2 mm nominal pocket allowance. No foot
or hood growth is needed; the notch changes frame support and remains unprinted.
New exposed vertical notch mouths have 0.35 mm rounds; key top/bottom edges
retain 0.15 mm chamfers. Two small nail recesses expose the key edge/underside
for occasional
removal, without an external projection. No spring or forced interference fit
is added. Wider geometry does not establish stronger printed behavior.

Ordinary desk use remains supported. The head constrains sideways spreading;
pulling the bases apart horizontally is therefore not its intended release.
With both hoods removed, lift one base relative to the other: its pocket floor
can carry the key upward until the other pocket is clear. Alternatively lift
the key at the nail recesses. Actual friction, which half keeps the loose key,
and finger/nail comfort need printing. Closed hoods block straight upward key
release. Larger rows and joined carrying remain unqualified.

Delivered geometry: revised five-card source and complete view, wider joined
connector view, full-base insertion/separation checks and economical end-crop
fit sample; retain previous variants. PETG/.4 mm nozzle/.2 mm layers/two walls/
7% adaptive cubic remain the reference setup. Complete geometry and nail access
were inspected; CAD checks cover entry and
relative-base release with both hoods removed. All four final print layouts
exported matching STEP/STL pairs and passed Orca
2.4.2 Q2C PETG reference slices without notices or generated supports; native
reports are retained in [cap_h_review.json](cap_h_review.json). No quantitative
printed force/strength is claimed.
The floor can carry the key in the checked rigid path; friction and which base
keeps the key are physical questions. G remains historical, not a recommended
handle architecture after this feedback.

## Workflow retrospective after H

The G/H work exposed three opportunities to simplify future iterations while
keeping the same evidence:

- Native evaluator reports were manually assembled into combined review JSON.
  The shared evaluator now implements `--report PATH --summary` to save complete
  native evidence and return compact stage status in the same run, replacing
  manual report copying and repeated summary code. Keep design conclusions and
  input identity in the human record; link the saved report for details.
  Exercised on the unchanged H key's geometry-only evaluation: complete native
  evidence and summary agree, with no new exports, renders or slices.
- G and H check scripts repeat enclosure and closure assertions. Future variants
  should call one object-owned check function with their actual geometry, adding
  only the changed connector checks. This reduces copied code without reducing
  the checks run for changed geometry. Existing delivered scripts remain intact.
- End-crop specimens can reuse one built base within an evaluation. Their local
  checks still need the full-base insertion check: G's first longer drop-in head
  cleared the crop but hit the tall wall. Run that CAD check before the final
  multi-layout export/slice batch; use earlier targeted slices when printability
  itself is the remaining decision, as it was for the rejected underside lip.

These are workflow observations, not new physical validation. The guidance lives
in [AGENTS.md](../../../AGENTS.md#avoid-repeated-work) and the design skill's
[component guidance](../../../.codex/skills/cadquery-3d-design/references/parametric-and-edges.md#components-and-shared-parameters).
No model source, printable artifact or existing verification report was changed.

## I — preloaded replacement-key experiment

Scope: repair the printed H sample's failed retention with three replacement
keys, reusing H blocks/pockets and G hood. Prior exports remain. Do not produce
another complete module until the grip trial resolves this local question. The
physical report below now supports testing the unchanged matching complete parts.
PETG, 0.4 mm nozzle, 0.2 mm layers, two walls and 7% adaptive cubic remain the
setup. Reported high printer precision is not a numerical fit calibration.

The original H rigid key had 0.20 mm normal clearance and no spring preload.
The shared `elastic_friction_grip` screen now rejects this force path before
export independently of unknown material stiffness or friction. Collision
capture and a clean slice never established useful retention. I's print entry
also automatically rejects missing preload and a seam that consumes preload.

One printed bow-tie key still joins a pair without hardware or a projecting
handle. Core growth of 0.15 mm leaves 0.05 mm normal core clearance. Four diagonal
arms have 0.8 mm thickness, 0.7 mm relief slots and rounded roots/contact pads.
Pads ramp from 0.05 mm projection to full projection over 0.8 mm of height.
Keys 1/2/3 give 0.10/0.15/0.20 mm seated normal interference. The key floor seats
vertically; spring reactions on the diagonal flanks push the blocks together.
Friction supplies upward grip while hoods are off; closed hoods obstruct upward
escape. Existing nail recesses allow deliberate key removal.

**Blocks touch at the seam.** Screening initially assumed the old 0.3 mm seam,
but closing it would relieve about 0.117 mm of normal compression and remove
key 1's preload. That issue was caught before delivery; the final outline and
all affected CAD, contact and slice evidence use a zero-gap seam. No printer
accuracy explanation is needed.

[CAD checks](cap_i_checks.json) establish four intended preload patches, a clear
entry nose/core, upper notch clearance, a lifted-base release path and hood
seating/escape coverage. Short arms fall outside the slender-beam screen, so
[local native contact evidence](cap_i_physics.json) uses actual rounded
slot/root/pad geometry, a clamped cropped core and rigid flat-flank normal
compression/unloading. Effective homogeneous isotropic PETG (E=1200 MPa,
nu=0.38, provisional 1.5% strain limit) is an explicit uncalibrated assumption.
The fixture omits whole-key sliding friction, coupled arms and complete insertion.

| Key | Normal preload | Modelled one-arm force | Peak strain |
| --- | --- | --- | --- |
| 1, 0.30 mm mesh | 0.10 mm | 0.572 N | 0.668% |
| 2, 0.30 mm mesh | 0.15 mm | 0.863 N | 0.956% |
| 3, 0.30 mm mesh | 0.20 mm | 1.154 N | 1.235% |
| 3, 0.25 mm mesh | 0.20 mm | 1.149 N | 1.425% |

Current native studies passed contact, unloading, numerical recovery, envelope
and provisional material screens. Finer mesh changed force 0.48% and local
peak strain 15.4%. Do not claim precise strain convergence or a printed holding
rating. Both meshes support this first fit trial under the stated assumptions.
[Retained native evidence](cap_i_evidence/key_3_fine/result.json) is identity-bound
to the final case; no solve was repeated to archive it.

Earlier diagnostics remain separately labelled: a sharp pad with imposed local
motion exceeded the strain screen; changes to both geometry and contact fixture
prevent single-cause attribution. An earlier spaced-seam fine case also exceeded
the strain screen. A 180-second timeout was an execution stop, not native
convergence failure. These results do not describe final I.

The [final keys slice](cap_i_review.json) completed with no notices or generated
supports. [48 sampled arm/relief sections](cap_i_paths.json) had maximum uncovered
arm width 0.000357 mm and no filled relief middle. This narrowly supports the
reasonably-solid arm assumption in the calculation; it is not a separate check
of routine extrusion or a material-property measurement. Reuse it while the
geometry and relevant print settings are unchanged.

Print the three labelled keys only, numbers up, and reuse the printed H blocks.
Bring end faces into contact, then try 1, 2 and 3 as needed. Choose the lowest
number that seats with firm hand pressure, removes loose play, stays joined
during gentle turning/handling and lifts deliberately at the nail recesses.
Reject failure to seat, tool-only removal, cracking or permanent bending. Actual
grip, release, recovery and dwell decide the next revision. Full-product
strength, long rows and joined carrying were outside this key trial.

### Physical result and next complete-box trial — 2026-10-03

The user reports printing all three I replacement keys; all work. Number 3 felt
better, but they could not identify the reason and had not fully read
the suggested instructions. The report corresponds to the I set delivered in
`9d05287`; exact printed file hashes, material and settings were not reconfirmed.
Record this as successful reported sample use and a subjective preference, not
as measured holding force or confirmation of every proposed test step. The prior
PETG plan and local simulations are not material calibration from this feedback.

Decision: keep all three geometries unchanged and use number 3 as the preferred
baseline. Its 0.20 mm nominal normal compression is higher than keys 1/2 at
0.10/0.15 mm; increased preload is a plausible reason for the feel, not an
established explanation. No further connector coupon, simulation or slice is
needed for unchanged parts.

Next deliverable is already available: two `cap_h_base_5.step/.stl` bases and
two `cap_g_hood_5.step/.stl` hoods, using the printed I number 3 key. Do not use
the old combined H layout's rigid key. This preserves the successful key and
its real mating pockets, roof-down hood and floor-down base print poses, and
the established PETG 0.4 mm / 0.2 mm / two-wall / 7% adaptive-cubic setup.
Prior component slices and I's full-base/hood geometry checks still apply.

The complete pair tests the remaining integration question: card alignment and
access with sparse/full occupancy, seated hood grip/opening, comfort of rounded
edges and thin walls, and opening either module while joined on a desk. Support
the bases, butt the end faces, seat key 3, insert notch-up cards, close/open each
hood, and deliberately remove the key with both hoods off. Accept comfortable
normal storage/access with stable cards and no accidental separation; revise
the failing interaction if observed. Tall-wall/frame stiffness, hood/card
interaction and whole-box handling were omitted by the key sample, so another
coupon cannot answer those questions. The complete small pair is the cheapest
useful next print using existing exports and keys. Long-row carrying, quantified
loads and long-term durability remain outside this reported success.

## J — centered, broader card panels

The user requested this change before printing the matching complete H/G pair:
center the broad card-holding panel, make it more grippy if useful, and consider
PETG relaxation during storage. This is a pre-print design request, not a
reported physical failure of the complete base. I keys 1/2/3 remain successful;
number 3 is retained without changes. PETG, 0.4 mm nozzle, 0.2 mm layers, two
walls and 7% adaptive cubic remain the proposed print setup.

Architecture: retain the card funnels and two rigid bottom-corner seats. The
seats set lateral alignment; a centered broad panel presses the flat card back
against the opposite rigid datum. Centering the old front pad directly over the
engraved swatch face could introduce an interrupted contact, so the panel moves
to the plain-back side. Insert the card with its flat side toward the panel and
its notched long edge upright. No new card catch, tool, separate spring, or
modification of the swatch is needed.

`cap_j_base_5.py` is a new source; previous base sources/exports are preserved.
Panel center moves from X=7 to X=0 mm, width grows from 28 to 40 mm, and contact
width grows from 4 to 16 mm. Thickness stays 1.2 mm. Contact height above the
floor rises from 13 to 14 mm and panel height from 16 to 17 mm; the relief root
has a 0.6 mm blend. Nominal squeeze remains 0.35 mm for a 2 mm card, with actual
rounded contact measured separately. Broadening and slightly lengthening the
panel targets more force with no increase in the idealized nominal bending
strain; merely thickening or increasing interference would increase strain.
These are conditional short-term beam comparisons, not measured forces, plate
analysis or a creep prediction. Effective length conservatively subtracts the
root blend. The homogeneous full-width beam assumption leaves actual local
bending, printed fill, root concentration and material response uncertain.

PETG's time-dependent behavior under sustained loading is established in
[printed-PETG creep research](https://pmc.ncbi.nlm.nih.gov/articles/PMC12349189/).
Its specimens, loads and manufacturing differ from this panel; no study value
is transferred to a lifetime or spring-force rating. The design preserves rigid
corner positioning, distributes contact over a wider centered patch, and avoids
extra squeeze as the response to that concern. It does not eliminate stress
relaxation or prove long-term grip.

Next print remains the complete small pair, now using two J bases, two unchanged
G hoods and the already printed I key 3. The accepted H sockets, foot and hood
closure contacts are preserved; affected CAD checks compare the unchanged
geometry outside the union of old/new panel regions and check card seating,
entry, hood clearance and the key's required-space path. No new connector coupon
or nonlinear contact solve is needed for the unchanged joining interface.

The trial asks whether centered panels hold cards upright and aligned with one,
three and five occupied positions while preserving easy four-direction entry,
comfortable final seating and deliberate card withdrawal. It preserves full
base stiffness, actual swatches and the agreed PETG setup. Unlike another small
coupon, complete boxes also test hood closure, thin-shell comfort and joining.
Accept firm comfortable normal storage/access; revise the affected panel if it
binds, loses alignment, needs excessive insertion force or takes a permanent set.
Leave at least one card seated for several days, then compare grip and alignment
and inspect recovery after removal. That observation can reveal early relaxation;
it cannot qualify years of storage. No long-term print result has been reported.

Verification: `check_cap_j.py` passed 25 seated card cases, 88 sampled rigid
four-direction funnel poses, centered panel symmetry, hood seat/lift/card
clearance and the accepted I key's required-space path. The exterior, foot,
hood closure and ports outside the union of the old/new panel regions matched
H by CAD difference. Short-term uniform-width beam screens used explicitly
assumed E=1000–2000 MPa and a provisional 1.5% strain screen. Measured rounded
surfaces give a nominal force ratio of 1.3215 and strain ratio of 0.9535 relative
to H's panel under that idealization; the largest screened strain is 0.5514% for
a 2.2 mm card. No calibrated modulus, actual fill/bonding or lifetime is inferred.
The [checks](cap_j_checks.json) retain scope and source identities. Generic FDM
review: floor-down base has continuous bed contact; 1.2 mm panels and 0.8 mm
side reliefs suit the agreed nozzle; pads grow from attached vertical stems on
slopes and shrink toward their tips, with no suspended shelf added. Rounded
roots/contact tips and inherited exterior rounding remain intentional. Bending
across layer bonds and unknown PETG response remain physical uncertainties.

Final delivery: [J STEP/STL export and native reference review](cap_j_review.json)
completed under OrcaSlicer 2.4.2 with the established PETG 0.4 mm / 0.2 mm /
two-wall / 7% adaptive-cubic profiles, preserved base placement, no notices and
no generated automatic supports. Both matching exports and the top view
succeeded. G hood and I key exports were unchanged and their prior relevant
evidence was reused; no ordinary extrusion-path audit was added. J remains an
unprinted complete-product trial, not a long-term retention qualification.


## K — dome-shoulder follower, compatible with J

The user authorized a printable K alongside the preserved J, and requested K
be committed and pushed before any further exploration. Existing agreement:
five cards, PETG, 0.4 mm nozzle, 0.2 mm layers, two walls and 7% adaptive cubic;
no hardware. Keep the G hood, H sockets and accepted I number 3 key unchanged.

Architecture screen: use the swatch's existing spherical **recess**, rather
than add a new card feature, part or lock. The broad panel remains centered at
X=0 with 40 mm width. The dome is at X=16 mm, 14 mm above the seated floor, so
its contact is necessarily off-center. K's detailed/domed card face points
toward the positive-Y follower; J's broad contact faces the plain back.
The old centered J contact remains available as the direct comparison.

The SCAD subtracts an 8 mm sphere centered 8 mm from the back of a nominal 2 mm
card. A central plug would load a theoretically zero-thickness spot: reject it.
K instead has two rounded 1.8 mm-radius noses, internally tangent to the bowl
at 4.4 mm radial shoulder positions. The source leaves about 1.32 mm of card
material at these nominal contact points. A spherical backing stays clear of
the card center. These supported noses avoid the thin edges of the initial
annular lip. The follower has 0.25 mm nominal coordinate-Y spring travel when
seated. This is positive
preload, not a clearance fit; it cannot promise zero creep. The panel is 0.8 mm
thick. Passage over the flat face needs 1.23 mm nominal travel, or 1.43 mm for
a 2.2 mm screening card. Rear flex-space is 2.4 mm; this accommodates amplified
upper-panel motion rather than just translating the contact by its tip travel.
The 1.8–2.2 mm interval is an assumed design envelope, not measured printer error.

Development checks caught two consequential defects before handoff: an
upper-only entry ramp allowed initial upward card travel without increasing
spring motion; extending the catch over the side shoulders restores the
geometric lift catch. Moving that ramp downward then left its bottom ahead of
its carrier; extending the carrier down to the ramp base addresses the hanging
ledge. The carrier stays clear of the actual spherical card. Neither issue
was attributed to generic printer tolerance.

Native diagnosis then found local lip strain above the provisional 1.5% screen
and upper-panel motion greater than the original rear allowance. One run
completed natively but failed contact quality; the backed run completed with
acceptable penetration yet exceeded the strain and displacement screens.
Neither is physical validation or proof of actual PETG failure. Both local
fixtures are retained as rejected design screens, not passed K evidence.
Two earlier incomplete solves were deliberately stopped when CAD changed;
these were investigation stops, not convergence failures. Rounded internal-
tangent noses replace the lip and the rear relief is increased from 3.9 to
4.5 mm. The larger noses later required another 0.1 mm rear space
(final rear Y=4.6 mm),
keeping 0.8 mm of separator before the next card datum. The gap is room
for elastic passage, not clearance at the seated card
or shared key interface. The 0.8 mm-radius round noses passed the coarse strain
screen (1.40%) but
failed it on the finer mesh (1.86%); force changed only 0.95%. This changed
the design decision despite stable overall force. Enlarge the contact spheres
to 1.8 mm radius and trim their rear at the carrier plane and outer flank
inside the existing X relief. The contact points stay on the same 4.4 mm
shoulder and seated travel stays 0.25 mm. The carrier lead increases from
1.2 to 2.1 mm to support their lower extent. A first untrimmed union was invalid
CAD and was rejected before either solver started; it is not a solver or
material failure. The remaining separator thickness is 0.8 mm before
the next rigid card datum; this suits the agreed two-wall starting setup.

Verification plan and stop rule: the actual off-center plate is pressed by a
rigid flat face through the 2.2 mm card's worst nominal passage and unloaded,
using the shared `SnapFitQuestion` Gmsh/CalculiX route. E=1200 MPa, nu=0.38 and
homogeneous solid PETG are explicit uncalibrated assumptions; the provisional
short-term strain screen is 1.5%. The fixture does not solve the full vertical
card/dome/friction path, flexible card, complete-base compliance or creep.
Require native force balance, penetration below 0.02 mm, final contact freedom,
elastic return within 0.0001 mm and the supplied motion-space screens. Compare
0.8 and 0.65 mm meshes on frozen geometry because the first passing strain is
near the provisional limit. The original stop rule required both meshes to pass
and force to change less than 10%, with strain sensitivity reported. The shared
study review now explicitly requires both force and strain changes below 10%
and an unchanged provisional design decision. This leaves the K trial decision
unchanged; it does not establish convergence or a measured PETG strain limit.

[CAD checks](dome_study_checks.json) cover positive seated preload, carrier/center
clearance, actual spherical seat contact after 0.25 mm movement, a 1 mm lift
requiring more follower movement, rear passage space, five nominal seated cards,
88 reflected J rigid funnel poses and mixed K/J mates. The remaining rigid
interfaces match outside the card-panel regions. The accepted key retains four
preloaded pads, its entry space and hood-covered escape. Inspection geometry
includes real-pocket reference cards and only K's changed use relationship;
printable geometry selects the base alone. The contact spheres grow from their
shaped backing, the backing/carrier grows from the vertical panel, and inherited
exterior rounding plus a 0.2 mm panel-top fillet treat handling edges.

[Final K STEP/STL and reference review](cap_k_review.json) completed with
OrcaSlicer 2.4.2, the agreed PETG .4/.2/two-wall/7%-adaptive-cubic diagnostic
profiles, preserved placement, no notices and no generated automatic supports.
This is STL slicing, not a check of Orca GUI STEP import. J, G and I artifacts
are unchanged and their relevant evidence is reused. Two tiny support-interface
layers in an earlier lip slice were located by reusing the existing
sunglasses-case path reader after omitting its relative-coordinate start G-code;
the current geometry no longer triggers the support probe. The ordinary final
panel paths were not separately audited; homogeneous material/fill/layer bonding
remain assumptions, not calibrated facts.

The next physical comparison is one J and one K full five-card base, two unchanged
G hoods and the already printed I key 3. Full bases preserve panel/root, guide,
hood and socket surroundings that another small coupon would omit. Try one,
three and five real swatches; compare four-direction entry, final seating,
front/back and lateral steadiness, comfortable deliberate withdrawal and hood
operation while joined. K's dome face points toward its follower; J's plain
back faces its panel. Compare grip after several days seated and recovery after
removal. Revise the affected contact if it binds, rocks, visibly damages the dome
or takes a set. Complete use and dwell remain unreported; none of the virtual
checks establish printed success or years of storage.

[Current local mechanics record](cap_k_physics.json): both 0.8 and 0.65 mm
meshes passed the current strain and movement screens after identity-checked
reinterpretation for the final rear gap. Predicted peak normal forces are about
2.59 and 2.55 N; peak strain is about 1.026% and 1.031%. Force changes 1.49%
and strain 0.43% relative to the refined result; this satisfies the chosen
stopping rule, without a claim of exact convergence or calibrated material
behavior. The largest sampled crown Y movement is about 2.26 mm, leaving room
in the 2.4 mm stem rear space.

Native archives retain their original former-space question outcomes. Increasing
only the base rear relief by 0.1 mm does not change the analysed spring, wall,
root fixture or loading. The shared evidence guard verified those native inputs
before interpreting the saved fields against the actual revised space; no
solver was rerun for that change. The final CAD checks and exports/slice cover
the revised complete base. This reuse is a concrete workflow saving.

K is delivered as a printable full-base comparison; physical product acceptance
remains pending. J sources/exports, the G hood and I keys remain unchanged.


Workflow reflection: K was completed and pushed before this audit. The small-nose
coarse/fine disagreement changed the contact shape; the final broad-nose meshes
support the conditional trial. The transferable lesson is to check actual spring
motion and local contact strain when a uniform beam idealization misses torsion
or local bending. The shared API already supplies the relevant observations.

| Check family | Existing shared operation | What stays with this object |
| --- | --- | --- |
| Spring/preload screen in I/J/K | `rectangular_cantilever`, `elastic_friction_grip` | Dimensions, contact source, assumed material/friction and whether the idealization is adequate |
| Actual K plate passage and return | `SnapFitQuestion`, selected-region observations, force/penetration/return checks, guarded `read_evidence` | Off-center plate, driver/root fixture, passage travel and rear-space acceptance |
| Frozen-geometry mesh comparison | `QuestionStudy` | K's decision, metrics, mesh sizes and stopping tolerance |
| Card seating/funnels, unchanged interfaces and mixed J/K joining | CadQuery intersections, distances and rigid transforms | Which poses matter, intentional preload contacts, masks and accepted relationships |
| Print-ready pair and reference slice | Shared evaluator and Orca review | Selected printable geometry, agreed profiles and interpretation of notices/supports |

The concrete change from this audit is that `analyze_cap_k.py --review-evidence`
now delegates the formerly manual mesh comparison/report to `QuestionStudy`.
It requires the two retained runs and supplies no new run directory: it cannot
silently solve missing evidence. The report is the shared native `AnalysisResult`
format, with comparison limits, stopping reason, acceptance changes, input/tool
identities and current consumer-source hashes. The original archives retain
their former-space outcomes; current interpretation still uses the existing
identity guard. Relative change now consistently uses the refined value as
denominator (the earlier manual summary used the coarse value).

Reading that generated report exposed one small shared reporting gap: study
results did not retain their numeric relative/absolute tolerance settings.
`QuestionStudy` now records those settings beside the comparisons, making the
stopping rule inspectable without reconstructing the caller. This changes
report metadata only; comparison formulas, solver behavior and acceptance
interpretation are unchanged.

This removes repeated percentage calculations and confidence bookkeeping without
adding a dome-specific public question or a generic CAD checker. A consumer
regression verifies saved-evidence reuse and prevents solver execution; the
existing shared acceptance-crossing test covers the case where small metric
changes still reverse a pass/fail decision. No geometry, STEP/STL, print settings
or print-status claims changed. The current K trial conclusion is unchanged;
independent increment/contact sensitivity, full dome insertion and physical use
remain outside this evidence.

## Deferred exploration after the current revisions

### Future compact archival module — recorded 2026-10-04

User-requested future direction, **record only; no modelling now**. The spaced
five-card setup is liked for display and individual access but uses too much
space for archiving. Retain it as the display option and add a separate,
higher-capacity archival variant: existing swatch cards packed tightly face to
face and inserted into the box together as a stack, rather than assigned to
widely spaced individual positions.

Base the archive variant on the preferred J-style base and shared connector.
It must join existing J modules using the same accepted I key 3 interface;
preserve compatibility at both module ends and do not carry over K4's reported
missing-stop problem. Target reuse of the accepted G hood and closure as well.
G is the accepted hood referred to in this request; V1 remains a rejected shell
experiment. Exact capacity, stack allowance, bundle support/retention and whether
the unchanged G hood accommodates the eventual archive layout remain undecided.
No capacity, dimensions, mechanism or print setup change is chosen by this note.

Treat this as a separate storage use case, not simply a larger display row or
an instruction to redesign the swatch cards. Preserve current display variants.
The next development phase must establish the compact stack arrangement and
matching interfaces when the user resumes modelling. Current J tilt and K key
stop issues remain deferred; no source, export, render, slice or study is created
for this future module now.

#### Archive containment discussion sketch — 2026-10-04

The user now authorizes an SVG communication sketch, **not detailed CAD or a
printable archive model**. New requirement: the archive base should remain low
enough to take out a few cards for browsing, while the remainder stays contained
without needing the hood. Remaining cards may lean rather than remain upright;
spilling out and scattering is unacceptable. Preserve the existing spaced display
variant and its stronger upright-alignment requirement separately.

[Editable SVG](../renders/concepts/archive_containment.svg) and
[PNG preview](../renders/concepts/archive_containment.png) show one proposal:
a common stack pocket with higher end walls/corners and lowered finger-access
scoops. The walls and floor support the remaining stack; individual card clips
are omitted. A partly empty pocket is shown with leaning cards and a few selected
cards lifted out. No spring follower or adjustable end block is selected: their
earlier discussion was an option, not an agreed requirement. Prefer simple
containment if it meets the user's actual browsing use.

The drawing proposes 40–45 mm end/corner height and 25–30 mm access height above
the card floor, leaving the upper portion of each nominal 80 mm card accessible.
These are illustrative starting heights, **not verified spill prevention or
accepted dimensions**. A display-height rim may let a sparse stack tip over it;
future geometry must check sparse occupancy, front/back and sideways lean,
withdrawal without dragging neighbouring cards, and the remaining support around
the access scoops. The user subsequently confirms browsing mainly on the desk;
open-box retention during carrying or inversion is not an established requirement.
The remainder must stay contained during ordinary selection on the desk.

The current 64 × 44.8 mm outer footprint cannot contain a fully horizontal
80 mm card, even along its approximately 78 mm outer diagonal; the usable pocket
is smaller. The sketch therefore allows leaning, not fully flat lying. A truly
flat layout would need a different footprint and hood. No change to that layout
or to the accepted G hood is selected. J-style foot/recesses, two-ended I key 3
capture and G hood reuse remain targets needing archive-geometry checks.

**Phase evidence/status:** SVG renders successfully and its PNG is visually
reviewed for communication. This is a schematic concept, not mating geometry,
CAD validation, slicing evidence or a physical print. Capacity and containment
during ordinary browsing remain unresolved. Source/export/slice work is outside this
discussion phase; no shared workflow/API change is justified by this sketch.

**User response and capacity screen:** the containment concept is acceptable,
but panel 1's side looks broken. Do not copy that drawn construction into CAD;
it is an unreliable illustration, not accepted geometry. Keep the sketch as
discussion history, with this correction. Heights are still proposals.

Source parameters give nominal 2 mm cards, a 40.4 mm base-body depth and G hood
inner depths of 41.2 mm at the lower band / 42.8 mm above. The current foot is
64 × 44.8 mm. An illustrative shared pocket within the body, with 1.2–2.0 mm
end walls, has roughly 36.4–38.0 mm stack space before detailed edge, entrance
and closure treatment. These wall sizes are screen assumptions, not selected
print dimensions or calibrated allowances. Nominal stacks are 30 mm for 15 cards,
34 mm for 17, 36 mm for 18 and 40 mm for 20. Thus recommend **15 for comfortable
capacity with the existing G hood**, with **17–18 as a tighter possibility** to
check against real geometry and a measured stack. Twenty leaves no useful room
for enclosing end walls within this illustrative body and would likely require
a slightly longer module and matching hood. Do not claim a qualified maximum,
actual printed stack thickness, or any new hood authorization. No capacity is
selected by the user yet; modular expansion remains an alternative to enlarging
each box. This screen uses existing named dimensions only, without CAD or slicing.

### Other deferred improvements

J4/K4 have now been printed; the [latest report](#j4k4-print-report--2026-10-04)
owns the remaining J alignment and K key-stop issues. No correction is authorized
now: the user requests records only. Retain preferred J4, G and I key 3. V1's
shell shape/feel was rejected and further hood exploration is ended. Broader
redesigns and larger rows remain deferred. These are conditional future ideas:

- J4 is preferred for firmer card retention after the complete-base comparison.
  Preserve it as the baseline; long-term dwell/recovery remains unreported.
- If K's concept helps but its off-center contact twists or binds, explore a
  different follower support that reduces that torsion while keeping a centered
  broad panel and reduced seated bend. Avoid the thin dome center; preserve the
  existing J-compatible sockets, I key 3 and G hood. No mechanism or dimensions
  are selected, and zero PETG creep is not a design promise.
- Consider a larger card row or further joined modules only after the five-card
  complete boxes work. A ten-card module is not currently requested; joined
  carrying strength and long-term grip would need evidence before claiming them.

The current G hood is printed and accepted. Retain it with preferred J4; preserve
V1 as a completed experiment rather than an ongoing exploration.
