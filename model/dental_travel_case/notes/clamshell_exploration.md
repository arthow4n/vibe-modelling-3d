# C6 — horizontal dental clamshell, compact hinge and shorter front loop

**Current result: an unprinted computational prototype, with a matching small
short-loop trial.** The user printed two short wall-snap samples and reports
excessive engagement effort and noisy opening. Exact sample identities and print
settings are unknown. The [print report](closure_short.md#printed-feedback-and-direction-change--2026-10-19)
records the rejection and stops that mechanism family. Do not print the remaining
R1–R4 variants as the next development step.

The user now accepts horizontal opening, with the brush and toothpaste lying in
the case, and requests sunglasses-case-style operation with a much smaller hinge
or another lid connection. They subsequently request shortening the front loop,
with corresponding test pieces. This authorization supersedes the earlier
separate-cap/no-exterior-hinge strategy. Accidental-opening resistance and
protection of the contents remain requirements.

## Start with the actual views

[Three rear connections](../renders/concepts/clamshell/connections.svg) ·
[Short-loop sections and release motion](../renders/concepts/clamshell/short_loop.svg) ·
[Closed C6](../renders/concepts/clamshell/c6_closed_isometric.png) ·
[Open C6](../renders/concepts/clamshell/c6_open_isometric.png) ·
[Enlarged compact hinge](../renders/concepts/clamshell/c6_hinge_view_isometric_back.png)

The [authoritative CAD](../clamshell_design.py) builds all three alternatives.
The [study](../clamshell_study.py) and [structured results](clamshell/cad.json)
retain dimensional/operating evidence. The comparison drawings are generated
from actual CAD by [this source](../clamshell_drawings.py), not generic diagrams.
No sub-agents were used.

## Architecture comparison and selection

| Rear connection | Nominal round barrel | Rear projection beyond shell | Decision |
| --- | --- | --- | --- |
| Sunglasses reference | 11.2 mm | 14.32 mm | Working baseline, too bulky for this adaptation |
| **A: compact screw-pin hinge** | **7.6 mm** | **7.9 mm** | Selected computational prototype; captive lid, uses on-hand M3 hardware |
| B: filament-pin hinge | 5.2 mm | 5.5 mm | Smaller, but axial pin retention/walkout and wear unresolved; not a print recommendation |
| C: removable rear tongues | No axle | 4.3 mm | Rejected in its modeled form: locates the lid but does not capture rear lift |

A uses two spaced **7 mm wide** hinge modules instead of the sunglasses design's
20 mm modules. Rear projection falls about **45%**. The two plain pins replace
large interlocking conical ears; the central lid ear runs between two base ears.
The hinges remain outside the cavity and the lid stays attached during use.
The positive front release controls opening, so the whole enclosure wall does
not have to be squeezed over detents.

This reduces mechanism bulk; it does not keep the former separate-cap envelope.
Including the unchanged keeper and rear hinge, closed C6 occupies about
**264 × 89.2 × 51.2 mm**. The 74.2 mm shell width is preserved, while the external
keeper adds 7.1 mm at the front and hinge 7.9 mm at the rear. The shorter loop's
own projection is 6.5 mm, so the keeper now sets the front maximum. No interior
space is surrendered to hide this cost. A short-end pivot could move these
projections into overall length instead, but would raise the long lid roughly
264 mm during opening and need much more endwise opening space; it is a layout
alternative, not a checked or exported C6 variant. The selected long-side pivot
keeps the familiar low sunglasses-style opening and the original 264 mm shell
length. That handling/occupied-width tradeoff remains visible for user review.

A needs **two M3 × 12 screws and four M3 nuts**, from the user's recorded on-hand
assortment. Each 7 mm ear stack nominally leaves 5 mm of screw length for a pair
of nuts. The assumed nut height is 2.4 mm each; check the actual pair fits the
available thread. Use the two nuts as a jam pair at a free-running setting,
rather than squeezing the moving ear. Do not interpret the CAD as calibration of
hardware fit, screw clearance, bearing friction or resistance to loosening.
The 3.4 mm bores and .3 mm axial ear gaps are prototype fits. Pins/hardware are
not printed or included as plastic components in the exported layouts.

B preserves the same basic pivot but its nominal 2.1 mm bores need an appropriate
pin and positive axial retention. Merely cutting a piece of filament and leaving
it free to migrate is not a complete travel-case design. C is a useful negative
control: with the front loop excluded from that local check, the rear can rise
through a 2° rotation around the front without meeting a retaining shoulder.
A true hook-and-withdrawal arrangement could be explored later, but the present
locators cannot be advertised as a secure replacement for a hinge. Neither B nor
C receives printable exports or inherited physical acceptance.

## Interior and practical opening

The shell is **264 × 74.2 × 51.2 mm**, with 2 mm walls/panels and the same R4
handled-end treatment. Its nominal straight interior is **260 × 70.2 × 47.2 mm**,
using the accepted printed M1 main-cavity basis rotated onto its broad face.
This also exceeds the uniform 69.5 × 43.7 mm sleeve aperture of the recent
wall-snap research. The old 78 mm cap withdrawal sleeve and inward catch guards
are gone. The rear hinges and front loop/keeper stay outside storage space.

The original brush/toothpaste arrangement was physically confirmed by the user,
with effort during loading. That is the contents basis, not a newly calibrated
packing proxy. The new CAD checks a central rounded storage gauge and preserves
the nominal extents; it does not invent a thinner toothpaste tube or claim a
new simultaneous digital packing proof. Actual loading and alternative tubes
remain unmeasured in this new case. Existing liners are not automatically
compatible and are not part of this phase.

Support the base with one hand, pull the loop outward, lift the lid, and let the
loop recover after it clears the keeper. The lid opens to 180° in the sampled
CAD path; the open view shows 100°. Both contents can be approached from above.
The collision sweep does not establish freestanding tipping stability through
that whole motion; the use assumption is a supported base.
To close quietly, hold the loop outward while lowering the lid onto its rims,
then let it return under the keeper. Do not force it over the keeper as a
force-open snap. This operation avoids the rejected global wall-flex mechanism;
**quietness and comfortable effort have not yet been demonstrated by a print**.

Rims meet as on the sunglasses case, rather than using a deep sliding sleeve.
The cavity is covered, with no hinge slots cut through its walls. The butt seam
is not a gasket or a measured dust/water seal. Protection, latch holding force,
long-panel bending, backpack loading and durability are physical unknowns for
C6. The prototype is not promoted to a qualified travel product by CAD checks.

## Shortened front loop and why it needs its own trial

The working sunglasses **E keeper and receiver are reused unscaled**. The loop's
radial contact position, 18 mm rail width, flat retaining-shoulder direction
and **3.2 mm outward release travel** are retained. The seated axial gap increases
from .2 to **.35 mm**. Root and leaf geometry are newly adapted; no physical
success transfers to the shorter loop.

The roots move **7.5 mm toward the crossbar**. Total loop height falls from
37.5 to **30 mm**, and root-to-upper-rail span from 27.5 to **20 mm**. The clear
straight span to the lower rail is **17 mm**, versus 24.5 mm in E; rounded roots
and the rail complicate the effective bending length. Leaves are **1.8 mm thick
instead of 2.8 mm**, preserving the 3 mm individual leaf width and .8 mm root
round. Front projection including the grip reduces from 7.5 to **6.5 mm**.
Shortening the original 2.8 mm leaves without thinning would make release harder.

The unchanged E loop cannot simply be translated onto this shallower case: its
root would extend **2.9 mm above the roof**. The short loop's root ends **4.75 mm
below the roof**, so it fits without a raised attachment block or enlarging the
case. These differences are visible in the committed sections.

An ideal two-leaf, fixed-root end-load screen at assumed E900–1800 MPa predicts
roughly **3.15–6.30 N** release effort for the short loop using the nominal 20 mm
span, versus **4.56–9.12 N** for E using 27.5 mm. At equal modulus that is about
69% of the E estimate. These are provisional straight-beam comparisons, not FEM,
measured effort, or pull-off holding force. The load acts on a coupled crossbar,
the roots are rounded, and printed material/layer adhesion is uncalibrated.
Using the lower-rail span as an effective-length alternative increases both
force and strain; the complete sensitivity is retained in the structured data.
For the short loop, that expands the illustrative range to approximately
**3.15–10.26 N** and **2.16–2.99%** surface strain. These are model scenarios,
not calibrated confidence bounds or printed strength limits.
The nominal root surface-strain estimate rises from about **1.78% to 2.16%**.
There is no material-strength or fatigue PASS: a thinner, shorter loop can be
comfortable yet fail to recover or fatigue sooner.

The CAD face witness finds a genuine **19.8 mm² projected bearing area** between
the flat rail and keeper, with opposing ±Z normals and .35 mm seated axial gap.
An upward .4 mm loop shift meets the keeper; an outward 3.5 mm prescribed shift
clears it through the declared lift path. These establish actual capture geometry
and intended release, **not an opening-force or backpack-load rating**.

A further [rail-motion check](clamshell/rail_motion.json) allows the crossbar to
rise and tilt as the arms bend, rather than only translating it outward. It uses
small-slope leaf kinematics with 17 and 20 mm effective lengths, sampled every
.25 mm through 3.5 mm outward motion. With the original .2 mm gap it finds a tiny
near-touch/intersection (0.000423 mm³). That is a clearance warning, not measured
binding or force. Moving the loop .15 mm down gives .35 mm seated clearance and
no intersection in these sampled poses, while preserving radial capture and the
shoulder depth. This approximate check does not replace coupled deformation or
physical operation; it removes an avoidable geometric risk before the trial.

## Print the small matching trial first

| Layout | STEP — preferred | Matching STL | Purpose |
| --- | --- | --- | --- |
| **Short-loop trial** | [C6 latch test](../c6_latch_test.step) | [STL](../c6_latch_test.stl) | Base/lid front-wall crop plus side-printed E keeper; first useful print |
| Body | [C6 body](../c6_body.step) | [STL](../c6_body.stl) | Full experimental base; one diagonal plate |
| Lid | [C6 lid](../c6_lid.step) | [STL](../c6_lid.stl) | Full experimental lid; separate diagonal plate |
| Spare keeper | [C6 keeper](../c6_keeper.step) | [STL](../c6_keeper.stl) | Optional: the trial's keeper can be reused in the full case |

[See the actual trial layout](../renders/tests/c6/c6_latch_test_isometric_back.png).

The [trial source](../c6_latch_test.py) crops the current full body and lid at the
front, preserving the **whole new loop**, 2 mm wall/roof attachment, keeper and
print orientation. It is 50 mm wide, with a short front floor/roof strip rather
than complete 264 mm panels. It omits hinges, long-wall compliance, full packing
and backpack loads. Its hand-supported stiffness cannot calibrate the complete
case's retention, but it can reject poor release effort, sag, binding, absent
capture or poor elastic recovery before a large print.

Slide the keeper into the body's side-entry receiver, align the cropped base
and lid, hold the loop outward while seating, then release it. Verify a real
shoulder capture and deliberate outward release. Compare against the working
sunglasses case: engagement effort, opening noise, reachable grip and repeated
return, not just a click. Stop if it binds, whitens, cracks, remains spread or
needs the enclosure to be forced open. Inspect the rail underside and keeper
seating before interpreting effort. A failed trial changes this new loop, not
the discarded R1–R4 wall-snap studies. No further physical print was inferred.

## Manufacturing, numerical scope and delivery

PETG / 0.4 mm nozzle / 0.2 mm layers remains the intended starting setup. The
reference smoke uses the existing diagnostic Q2C two-wall / 7% adaptive-cubic
profile. Full halves print roof/floor down, each **45° diagonally on its own
plate**: a 264 mm straight layout leaves only 3 mm per end on the 270 mm bed,
whereas the existing 5 mm brim needs more. Diagonal placement lets the reference
slicer fit the complete halves without shortening the established interior.
Keep that supplied orientation. The keeper prints on its side, as the working E
part does. The test plate contains all three small parts separately.

The reference slicer completes all four layouts, but **manufacturing review
flags remain visible**. The lid and trial support probes suggest trees beneath
the crossbar; the lid additionally has suggestions at its small hinge bores.
The body/trial report a floating-cantilever notice. See the
[native bridge/support location witness](clamshell/support_locations.png) and
[retained data](clamshell/support_locations.json), with source/STL/G-code hashes.
The roughly 12 mm loop bridge has two end supports in CAD and the same span as
the successful E reference; the thinner rail remains a new physical print.
The primary trial is an **experimental supports-off bridge trial**, not a clean
slicer verdict or guaranteed sag-free retaining face. Inspect its underside;
do not accept a sagged shoulder or force it closed. The small hinge bores also
need a real print/fit check before relying on the full prototype. No native
warning is rewritten into physical success.

The [source association](clamshell/publication.json) ties all paired exports to
the current shared builders. `verification.py --variant clamshell-c6` composes
CAD capture/sweep, trial association, slice completion and explicit bridge review.
Earlier records and IDs are preserved. The secure-closure and end-retention
wording is explicitly updated using the later user instruction through the
existing supersession guard; it is not marked inapplicable to discard intent.
The former no-exterior-hinge and both-end cap-catch strategies are superseded;
accidental-opening resistance remains active. Full use,
force, durability and printed quietness stay UNKNOWN.

No full-assembly contact or sound simulation was warranted here. Actual CAD
motion/contact direction, the working E negative/positive experience, a modest
actuation comparison and a small representative print decide the present
architectural questions more directly. The chosen geometry is a defensible next
prototype, not a calibrated retention-force predictor.

| Item | Print status | Artifact(s) | User result or remaining physical checks |
| --- | --- | --- | --- |
| C6 short-loop trial | Unknown — no print reported | C6 latch test STEP/STL | Effort, capture, recovery, noise, rail sag and repeated use |
| C6 full prototype | Unknown — no print reported | Separate C6 body/lid, E keeper and M3 hardware | Integrated fit, hinge operation/retention, long-shell behavior and travel protection |
| Previous short wall snaps | Partial — two printed, identities unknown | Prior R1-S–R4-S exports retained | Engagement too forceful and opening noisy; development discontinued |

## Reproduce the computational evidence

From the repository root:

```sh
./execute.py --threads 1 model/dental_travel_case/clamshell_study.py
./execute.py --threads 1 model/dental_travel_case/clamshell_rail_motion.py
./execute.py --threads 1 model/dental_travel_case/clamshell_drawings.py
./execute.py --threads 1 model/dental_travel_case/verification.py --variant clamshell-c6
```

The [retained verification report](clamshell/verification.json) records scoped CAD,
matching-sample and reviewed-slice results, with physical questions UNKNOWN.
The focused regression run passed **125 tests**, covering the C6 actual shoulder,
matching loop crop, retained intent, earlier closure experiments and shared
verification entry-point contracts. No calibrated C6 holding-force result exists.
Re-publication uses `evaluate_model.py --slice` on the four layout sources above;
retain the body/lid/trial native runs for `clamshell_toolpaths.py`, review any
changed warnings, then run `clamshell_delivery.py` to associate current exports.
The hash checks intentionally reject stale evidence after geometry changes.

Attribution: GPT-6, reasoning effort not exposed; Codex CLI / OpenAI. No delegated
reviewer or other sub-agent was used, following the user's explicit preference.
