# Filament swatch box — thin press-on hood

**New deliverable: H, a broader connector without G's long handle.**
Previous versions are preserved. The user finds G's projecting arm unnecessary
for modules that usually remain joined. H changes the pockets and key, retaining
the compact five-card footprint and the existing G hood. No H print is reported.

## H — connector without a handle

- [Small connector test, STEP](cap_h_connector_test.step), [STL](cap_h_connector_test.stl).
- [One base, G hood and key, STEP](cap_h_module_5.step), [STL](cap_h_module_5.stl), [source](cap_h_module_5.py).
- Separate [H base STEP](cap_h_base_5.step), [H key STEP](cap_h_key.step), with matching same-name STLs. The [unchanged G hood](cap_g_hood_5.step) is compatible.

The new key is **16 × 6.7 × 3.4 mm**, with an 8 mm waist. The long arm and its
foot channel are gone; nothing projects from the side. The deeper head needs a
straight-sided entry notch in the base wall, visible when the hood is removed.
The notch is beyond the last card clip relief. Foot depth remains 44.8 mm and
hood walls/roof remain 0.8 mm. H keys/pockets differ from G; print matching parts.

![H wider connector seated between actual base ends](renders/cap_h_connector/inspect_connector_h_top.png)

Sideways spreading is the motion the bow tie prevents. To separate occasionally,
remove both hoods, lift one base about 4 mm relative to the other, then move it
away. Its pocket floor can carry the key upward until it clears the other foot;
which half retains the key and the actual effort depend on printed fit. Two
small nail recesses also let you lift the key directly. These are occasional
release provisions, not a frequent-operation handle. The key is intended to
seat without a forced interference fit; closed hoods cover upward key release.

![H complete open and closed modules](renders/cap_h_assembled/inspect_cap_h_isometric.png)

Use the same PETG, 0.4 mm nozzle, 0.2 mm layers, two walls and 7% adaptive cubic.
Print bases floor down, keys flat and hoods roof down. The small sample uses two
actual end crops and one key: bring end faces about 0.3 mm apart, seat the key,
check planar play, then try lifting one half and moving it away. Check nail
access separately. The sample omits the tall wall and hoods; full-base CAD checks
cover their geometry, but actual loaded handling, closure and frame stiffness
require the complete pair. Never infer whole-product success from the sample.

[CAD checks](notes/cap_h_checks.json) cover full-base entry, a lifted-base release
path, hood clearance/coverage and nominal nail-tip access. [Reference slices](notes/cap_h_review.json)
cover the final layouts; fit, force, nail comfort and strength remain unprinted.
This is a desk-supported storage proof, with no joined carrying rating.
[Design record](notes/cap_comparison.md#h--wider-connector-without-a-handle).

## G — retained modular five-card proof

- [Small connector test, STEP](cap_g_connector_test.step), [STL](cap_g_connector_test.stl): two actual base-end crops and one key.
- [One base, hood and key, STEP](cap_g_module_5.step), [STL](cap_g_module_5.stl), [parametric source](cap_g_module_5.py).
- Separate [base STEP](cap_g_base_5.step), [hood STEP](cap_g_hood_5.step) and [key STEP](cap_g_key.step), each with a matching same-name STL.

The foot is **44.8 mm deep**, down from F/E's 48.8 mm. Four five-card modules
with 0.3 mm joint gaps occupy 180.1 mm instead of 196.1 mm, about 8% less row
length. Each join adds one printed key; the same base repeats at either end.
The hood's main walls and roof remain 0.8 mm, with hidden reinforcement and
rounded edges. **Use G's matching base and hood together.** F/E are retained.

![G: joined closed/open modules with a removed hood](renders/cap_g_assembled/inspect_cap_g_isometric.png)

The user finds the long arm unnecessary before any reported G print. The
retained connector has a bow-tie head, a slim arm and a rounded side tab. Remove both
hoods, place the bases together on a desk and lower the key into the top pockets.
Its wide ends constrain spreading and planar movement. The closed hoods cover
straight upward withdrawal. To separate, remove both hoods and lift the key by
its side tab. Individual hoods can open with the key installed; keep the bases
supported while operating. This proof does not qualify group carrying.

![Actual end pockets and drop-in key](renders/cap_g_connector/inspect_connector_g_isometric.png)

The [joined underside](renders/cap_g_joined/inspect_joined_g_bottom.png) shows
two flat bottom skins and the exposed side tab; most of the key sits above those
skins. The [joined pocket close-up from above](renders/cap_g_joined/inspect_joined_connector_g_top.png)
omits the hoods and crops the bases to expose the seated bow-tie head and arm.
These are inspection views of the existing G geometry, not revised print files.

Print **PETG, 0.4 mm nozzle, 0.2 mm layers, two walls, 7% adaptive cubic**.
The supplied poses are base/sample floor down, hood roof down and key flat.
Separate files allow translucent PETG for the hood. Start with the small
connector test to check lowering/lifting effort, binding and desk-supported
alignment. Its two end faces should be approximately 0.3 mm apart; it has no
hoods, so upward key removal is deliberately free. The sample cannot test
closed-hood restraint, full-module stiffness or tall-box handling.

The full two-module trial needs **two bases, two hoods and one key**; the combined
file contains one of each. Check cards with one, three and five occupied slots,
then hood seating, grip/release and the joined pair's handling. G has no reported
print result. [CAD checks](notes/cap_g_checks.json), [manufacturing review](notes/cap_g_review.json)
and [local path checks](notes/cap_g_paths.json) passed. The final combined,
component and sample layouts sliced with no notices or generated supports.
Actual fit, force, comfort, optics and durability remain physical questions.
See the [design and trial record](notes/cap_comparison.md#g--compact-five-card-modules-and-drop-in-connector-proof).

## F — smooth exterior hood

- [Hood only, STEP](cap_f_hood_5.step), [matching STL](cap_f_hood_5.stl).
- [Both parts, STEP](cap_f_flat_5.step), [STL](cap_f_flat_5.stl),
  [parametric source](cap_f_flat_5.py).
- [Compatible E base, STEP](cap_e_base_5.step), [STL](cap_e_base_5.stl).

Use the same **PETG, 0.4 mm nozzle, 0.2 mm layers, two walls and 7% adaptive cubic**.
Print the hood roof down and E base floor down as supplied. If the E base is
already printed, only the F hood is needed; earlier D/ungrooved bases remain
incompatible. Hold the exposed base foot and pull the hood near its bottom,
where its concealed 1.6 mm wall supports the pockets and grip. The 0.8 mm inner
transition grows gradually in the roof-down orientation. The external band and
shoulder are gone; roof rounding remains 3 mm.

![F continuous exterior and open box](renders/cap_f_assembled/inspect_cap_f_isometric.png)

The paired and hood-only exports passed their OrcaSlicer 2.4.2 Q2C PETG reference
slices, with no notices or generated supports. The source's E base geometry,
separate exports and base-only slice evidence are unchanged. Targeted F checks
and [manufacturing evidence](notes/cap_f_review.json) cover affected guidance,
rim seating, pocket material and selected toolpaths; they do not establish
printed smoothness, optical clarity or actual holding/opening force.

Test the complete pair empty, then with one, three and five cards: check the rim
meets the foot, the sides feel comfortable, the cap stays attached under loaded
own weight, and pulling near the bottom releases it without buckling. Repeat
and compare after an overnight closed dwell. Twenty-card geometry is checked,
but this phase still supplies the five-card physical trial only. G above
separately explores joined modules; F is unchanged. See the [F design record](notes/cap_comparison.md#f--flush-exterior-reinforcement-inside),
[affected CAD checks](notes/cap_f_checks.json) and [local path record](notes/cap_f_paths.json).

## Earlier thin hood — E

E's exports and evidence below are retained history; F is the next proposed print.
The printed D fit was okay, but the hood was too bulky and exposed edges were
insufficiently rounded. The user authorizes a new matching base and mechanism
to prioritize a thin hood. E is not yet physically tested; D's fit result does
not qualify this new closure.

### E — thin hood and matching base

- [Both parts, STEP](cap_e_thin_5.step), [matching STL](cap_e_thin_5.stl),
  [parametric source](cap_e_thin_5.py).
- [Thin hood only, STEP](cap_e_hood_5.step), [STL](cap_e_hood_5.stl).
- [Matching base only, STEP](cap_e_base_5.step), [STL](cap_e_base_5.stl).

Print **both E parts**; the D base and older bases are not matching mates.
Separate files let you print the hood in translucent PETG and the base in a
different PETG colour. Use **0.4 mm nozzle, 0.2 mm layers, two walls, 7% adaptive
cubic** as before. Supplied geometry places the base floor down and hood roof
down; supports are not requested. These are reference-profile assumptions,
not confirmation of the user's exact settings or optical appearance.

The main hood walls and roof are **0.8 mm**. A **1.6 mm** lower band holds four
shallow blind snap pockets and provides a stronger place to grip. The flexing
leaves now belong to the base, so the hood no longer needs D's 6 mm wall envelope.
The upper outline is approximately **62 × 46.8 mm**, versus D's 72.4 × 57.2 mm;
the lower band is 63.6 × 48.4 mm. A 3 mm outside roof round has a matching
2.2 mm cavity round to preserve the thin shell. Corners, rim and base foot have
deliberate edge treatment; broad underside recesses return on sloped surfaces.

The hood's lower rim rests directly on the rounded base foot at Z = 5 mm.
Four-sided entry clearance guides it, the foot stops it, and four base-mounted
detents provide retention. Hold the exposed foot using its two underside grip
recesses, grip the hood's **lower band**, and pull upward. Avoid relying on
squeezing the thin upper panels to open it. Card clips and low corner seats
reuse the previous builders; local exterior-wall relief now accommodates the
closure leaves. There are only two printed parts and no release button/hardware.

![E closed and open with upright cards](renders/cap_e_assembled/inspect_cap_e_isometric.png)

The paired and separate layouts passed the OrcaSlicer 2.4.2 Q2C PETG reference
reviews with no notices or generated supports. Targeted path review found
36 sampled sections filled through the base leaves, thin long-side walls and
four roof layers; this does not establish material properties or transparency.
Rigid five/twenty-card checks confirm rim seating, sampled clear withdrawal,
blind-pocket skin and depressed pad escape space. The twenty-card geometry is
checked but is not exported or recommended before this complete five-card trial.

A conservative effective-solid beam screen predicts approximately 1.25% maximum
root strain and 1.61 mm free-end travel within 2 mm relief. The 1.5% strain screen
and 1000–2000 MPa modulus range are provisional uncalibrated assumptions; actual
hood compliance, friction, layer bonding and elastic passage are not established.
No measured retention or release force is claimed. STEP GUI import remains
separate from the successful STL smoke slices.

Try the empty pair first, then one, three and five cards. Report whether the
rim meets the foot, the corners feel comfortable, the hood feels acceptably
thin, and deliberate pulling opens it without buckling the shell. Check loaded
own-weight retention a few centimetres over a table with a hand beneath it;
repeat closure/opening and compare after an overnight closed dwell. Translucent
appearance, spring return, pocket wear and grip are physical questions. This
complete sample represents the thin hood and new base together, rather than a
local latch coupon. Joined modules remain future work.

[E design record](notes/cap_comparison.md#e--thin-hood-with-base-mounted-detents),
[geometry/beam checks](notes/cap_e_checks.json), [local path evidence](notes/cap_e_paths.json)
and [manufacturing review](notes/cap_e_review.json) retain the actual evidence.

## Printed reference — D

The previous PETG print's broad clip grips nicely, but its tiny end spring gives
no useful sideways pressure. The new base removes that spring, adds two fixed
seats matching each card's bottom corners, and strengthens the broad clip.
The user accepts a final downward press and specifically requests firmer grip.
Lateral alignment and the stronger grip still need a physical trial. The user now
authorizes autonomous cap exploration while away; this permits independent cap
concept work without promoting the corner seat to printed validation. They now
select a simple lift-off cover with retention: press it on from above and pull
deliberately to separate it.

The user confirms translucent spools are **PETG** and requests discussion only
of a thinner hood and expandable joined five-card boxes. Both remain
[future ideas](notes/cap_comparison.md#future-ideas--translucent-petg-and-joined-modules),
initially deferred until the print finished. The subsequent report makes a
slimmer hood and more pronounced rounding the next concept priorities, including
for opaque filament. The base is probably fine according to the user. The later
authorization produced the E thin-hood prototype above; modular joints remain
discussion only. D artifacts remain the printed reference, not an accepted
finished product.

Additional closure requirement: the user wants the hood's lower rim to meet
the base neatly when fully closed, while remaining easy to pull apart. The
preferred concept is a rounded base ledge supporting that rim, with accessible
base grips below the seam. This is recorded in the
[closure/handling notes](notes/cap_comparison.md#closed-seam-and-opening-grip).
The existing source seats on internal pads; that does not establish the desired
visible rim-to-base contact in the printed object.

### Historical matched prototype — D

- [Both parts, STEP](cap_d_snap_5.step), [matching STL](cap_d_snap_5.stl),
  [parametric source](cap_d_snap_5.py).
- [Cap only, STEP](cap_d_hood_5.step), [STL](cap_d_hood_5.stl).
- [Matching base only, STEP](cap_d_base_5.step), [STL](cap_d_base_5.stl).

**Print the matching base as well as the cap.** Earlier ungrooved bases are not
the intended mate. Four 0.8 mm-deep exterior grooves are the base's only functional
change; the card seats, guides and stronger broad clips stay as before. The plain
rounded hood has four hidden integral spring pads, ramped for downward entry and
upward release. Four separate end-rim pads stop the cap independently of its
snaps and contents. A continuous outer wall covers the spring relief pockets.
There are only two printed parts, with no release button or extra materials.

![D closed/open concept](renders/cap_d_assembled/inspect_cap_d_isometric.png)

Use **PETG, 0.4 mm nozzle, 0.2 mm layers, two walls, 7% adaptive cubic**. Print
the base floor down and cap roof down as supplied; no supports are requested.
The paired reference slice preserves the source's Q2C coordinates, enabling a
specific stem-path review. GUI rearrangement is allowed but is a different slice.
Hold the base's lower 6.4 mm band/underside, align the hood, and press straight
down until it reaches the rim stops. Grip the hood and pull straight up to open.
Its approximately 86 mm withdrawal clears the cap skirt past the full-height cards.

First test the empty matched pair, then one, three and five cards. Check:

1. The cap seats fully, with a distinct hold, without binding or excessive force.
2. Hold the cap a few centimetres over the table and check that the loaded base
   stays attached under its own weight; keep a hand ready beneath the base.
3. Deliberate two-hand pulling releases it cleanly, and both parts are easy to grip.
4. Repeat opening/closing, then leave it closed overnight and compare the hold.
   Report remaining play, slipping, rubbing, cracking, whitening or lost spring return.

The 5–20 N deliberate pull band is a provisional target. Nominal beam/ramp
estimates are only an order-of-force screen, not measured press, release or
retention forces. The complete five-card prototype represents the tall shell,
four interacting detents, guidance, seating and opposing grips that a local
coupon would omit. It does not qualify twenty-card holding strength, loaded
transport, creep life or fatigue. Five/twenty-card rigid checks include actual
rounded pads and sampled withdrawal; elastic motion and friction remain physical
questions. No loaded carry rating is claimed before the trial.

Likely adjustments live in `cap_d_snap_5.py`: `TIP_EXTRA_REACH` changes pad reach;
`STEM_THICKNESS` and `FLEX_LENGTH` change stiffness; `FIT_GAP` is currently inherited
from the shared dimensions. Change reach in small steps after observing actual
hold/binding; rerun the affected checks and exports. Keep earlier successful
trial files intact. Do not change the shared gap casually, since it affects A/B/C.

[D design decision](notes/cap_comparison.md#d--selected-press-on--pull-off-direction),
[rigid and beam checks](notes/cap_d_checks.json), [paired manufacturing review](notes/cap_d_review.json)
and [targeted stem-path record](notes/cap_d_paths.json) retain the assumptions and
scope. Fit was reported okay; force and spring return remain unreported, while
hood bulk and edge comfort require revision. Lower-rim contact is now also a
next-iteration requirement.

## Earlier cap alternatives

[Architecture and comparison record](notes/cap_comparison.md) owns this phase.
**A: removable hood** is the first finished five-card prototype. It continuously
covers the cards, stops on four internal rim pads, has a four-sided skirt lead-in,
and lifts off for unrestricted access. It is an unlatched desk cover; fit/friction
and any transport retention are unqualified. Its roof prints on the bed, leaving
all internal pads supported by gradual ramps.

- [A cap only](cap_a_hood_5.step), [matching STL](cap_a_hood_5.stl): try this on the
  nominal existing five-card footprint without printing a new base.
- [A cap + softer base layout](cap_a_lift_off_5.step), [STL](cap_a_lift_off_5.stl).
- [Softer base alone](base_rounded_5.step), [STL](base_rounded_5.stl): exterior corner
  radius 5 mm and upper rim radius 1 mm; functional slot crests stay 0.4 mm.
- [Twenty-card closed/open inspection](renders/cap_a_comparison/inspect_cap_a_isometric.png)
  is a full-size concept view, not a twenty-card export or physical test.

Use the existing PETG / 0.4 mm / 0.2 mm / two-wall / 7% setup. The cap requires
about 76 mm upward travel to clear the tall cards. Its 0.4 mm per-side running
gap is provisional. The full five-card cap is the meaningful first trial: check
corner fit, rim seating, easy lift/replacement, headroom and overall handling.
It includes actual height and stop geometry which a short rim coupon would omit;
twenty-row rigidity, friction and carrying behaviour remain unqualified.

[A rigid checks](notes/cap_a_checks.json) cover five/twenty-card configurations,
four-pad seating, conservative contents and sampled vertical lift. [A layout
review](notes/cap_a_review.json) records successful CAD, matching STEP/STL,
OrcaSlicer 2.4.2 Q2C PETG slice, no notices and no generated supports. No physical
cap report yet. Sources and exports for the earlier printed bases remain intact.

**B: upright-card drawer** is the second five-card prototype: [STEP layout](cap_b_drawer_5.step),
[STL](cap_b_drawer_5.stl), [source](cap_b_drawer_5.py). Pull the tray fully from its
fixed cover and place it on the table to browse. The closed front panel seats on
the housing rim; 3 mm side/top lips overlap the opening. The tray prints floor
down and the enclosure prints closed-back down, opening upward. The cap stays on
the desk, with the cost of greater table travel and a tall tray-front panel.
[Twenty-card comparison](renders/cap_b_comparison/inspect_cap_b_isometric_back.png)
and [rigid travel checks](notes/cap_b_checks.json) review this whole interaction.
The full five-card prototype preserves floor contact, guide length, contents and
front-lip geometry; test running fit, support the tray as it comes free, and
check access/reinsertion in sparse/full rows. It does not qualify twenty-row
flexure, tipping, drawer retention or loaded transport. [B reference slice](notes/cap_b_review.json)
completed with no notices/review flags and no generated supports. Actual fit and
handling are unknown, and neither B nor A has a positive closure latch.

**C: attached hinged hood** is the third five-card prototype: [STEP layout](cap_c_hinged_5.step),
[STL](cap_c_hinged_5.stl), [source](cap_c_hinged_5.py). Four printed parts comprise
the base/rear frame, U-shaped hood, axle and tapered keeper key. A fixed rear wall
and roof-height pivot let the hood swing clear of tall cards. It opens to a
180-degree shelf stop; a rear foot extends 40 mm beyond the seating base's rear
edge to improve open-box stability. This adds bulk and a permanent wall behind
the last card. [Twenty-card closed/open view](renders/cap_c_comparison/inspect_cap_c_isometric_back.png)
shows the cost of keeping the cap attached. Prefer A unless that benefit matters.

Print the layout as supplied: base floor down, hood roof down, axle head down,
key flat. Diamond bearing holes and beveled crowns avoid unsupported round-hole
roofs in the two opposite print orientations. Align the centre hood bearing
between the fixed ears, insert the axle from its headed end, then push the key
through its exposed cross slot. The key's head stays outside the shaft; its loose
taper is a trial fit, with no calibrated interference. Keep the key installed
during operation. Check that it stays in during repeated opening; a slipping key
means this retention is unqualified and needs adjustment. The cap has no closed
latch, and lifting/carrying by the cap is unqualified.

The complete five-card C print is the useful test because it retains the tall
frame, lid sweep, roof stop, foot and actual card access. A bearing coupon would
miss those relationships. With the base on a table, try empty, one, three and
five cards; support the hood while first opening, check axle/key fit, clearance,
open-stop contact, tipping and easy access to the last card, then close it.
Actual mass distribution, touch forces, hinge/stop strength, key friction, wear
and twenty-row stability remain unknown. [C rigid checks](notes/cap_c_checks.json)
cover five/twenty-card sampled opening with conservative contents and axle/key
fit; the stability sensitivity uses explicit assumed mass-density ratios, not
slicer-derived weights. [C CAD/export/slice record](notes/cap_c_review.json) is
reference manufacturing evidence; it does not establish physical operation.

The earlier recommendation to start with A cap only applied to an unlatched desk
cover. The current request selects D with press-on retention. A/B/C remain useful
historical comparisons; D's matching five-card pair is now the first print.

| Version | Primary print file | Matching STL | Status |
| --- | --- | --- | --- |
| **Current five-card corner seat** | [card_base_corner_seat_5.step](card_base_corner_seat_5.step) | [STL](card_base_corner_seat_5.stl) | CAD/slice checked; no print report |
| Previous five-card spring seat | [card_base_petg_5.step](card_base_petg_5.step) | [STL](card_base_petg_5.stl) | Printed: broad clip works; tiny end spring ineffective |
| First five-card free-clearance base | [card_base_test_5.step](card_base_test_5.step) | [STL](card_base_test_5.stl) | Printed: excessive seated rocking and lateral variation |
| First fifteen-card base | [card_base_test.step](card_base_test.step) | [STL](card_base_test.stl) | No print report; unchanged earlier interface |

The current base retains the **59.6 × 44.4 × 20.4 mm** footprint/height, five
positions on **7 mm centres**, and **80 mm tall × 50 mm wide × 2 mm thick**
nominal cards with the notch at the top. These dimensions come from the user's
[swatch source](../filament_archive_swatch/filament_archive_swatch.scad), not
measurements of printed cards. [Parametric source](card_base_corner_seat_5.py)
owns the current trial; earlier printed sources and exports remain unchanged.

![Current five-card trial](renders/corner_seat_5/card_base_corner_seat_5_isometric.png)

## Seating and handling

The four-sided funnel corrects hand placement before the lower guide. Both broad
faces and both ends open outward; the entrance is 5.6 mm across card thickness
and 56.4 mm along card width before crest rounding. The lower slot is 2.8 mm
across thickness and 54 mm along width. The wider lower ends allow initial
sideways correction, rather than demanding early alignment with a tight end stop.

Two fixed **45-degree ramps** mate with the swatch's **4 mm bottom-corner
chamfers**. At the nominal seat, both corners touch: lateral translation needs
upward movement. A final downward press can guide the card toward the centre;
front-clip friction means automatic gravity-only settling is not claimed.
The central bottom edge has 0.6 mm depth relief, leaving 1.8 mm of floor.
This lets modestly narrower cards reach both ramps instead of stopping on a
flat floor with sideways play. Actual width/corner variation can alter seated
height slightly; nominal cards retain the previous 2.4 mm bottom height.

![Bottom-corner contacts](renders/corner_seat_section/inspect_corner_seat_front.png)

This inspection shows a thin section through one seat and only the lower
28 mm of a conservative card envelope. The spring is omitted to expose the
rigid support relationship; it is not a loaded-flexure simulation or print file.

The front clip presses the card against its flat, unengraved back face. Its
**28 mm stem width, 13 mm contact height, narrow 4 mm pad and rounded ramps**
are preserved from the printed clip. The stem is **1.2 mm thick**, increased
from 1.0 mm; the simple beam model predicts **1.728 times the stiffness**, not
a calibrated increase in grip. The pad still contacts original swatch Y=16–20 mm,
clear of labels, dome and thin opacity regions. No wider contact pad or second
clip is needed for this trial. The tiny end spring and its pocket are removed.
There is 1.0 mm nominal rearward stem headroom and 0.8 mm side relief.

The task is unchanged: lower a notch-up card through the funnel, give a final
press, release it into an aligned row, then pull upward for removal. Each slot
works independently of neighbours. The back plane locates front/back angle;
corner seats locate sideways position and support the card; the clip provides
front/back pressure. Removal has no separate release action.

## Print and test

Use **PETG, 0.4 mm nozzle, 0.2 mm layers, two walls and 7% adaptive cubic**,
with the flat underside on the bed. The reference slice needs no supports.
Keep the five positions in one piece. Put the card's flat back toward the
uninterrupted groove wall, its labelled face toward the broad clip, notch up.

1. Try one card in the middle and then an end slot; press until it reaches the
   corner seat. Check sideways alignment and front/back rocking after release.
2. Try three cards and all five. Compare their resting positions and grip with
   the previous PETG print. Touch the tops lightly in both directions and release.
3. Remove/reinsert from left, right, front and back. Report sticking, excessive
   pressing/pulling effort, base lifting during removal, or awkward correction.
4. Leave cards seated overnight and check return again. Report whitening,
   cracking, permanent spring set, unequal heights or remaining lateral play.

This five-position partial-product print tests coupled corner seating, firmer
grip and reinsertion with full-size cards, real divider pitch and surrounding
geometry. It omits the cover and long row, so it does not qualify box handling,
protection, large-base tipping or long-term fatigue. A single leaf coupon would
miss the corner-seat/friction interaction; CAD cannot supply actual feel.
Accept the interface for integration only if it produces an aligned row with
firmer but usable grip. Binding or excessive effort calls for clip/preload
revision; inconsistent corner seating calls for actual card-width/chamfer
measurements before changing the ramps. Do not force a binding card.

## Decisions and evidence

The front/back clip is worth retaining because the user physically likes its
grip. Refining the rejected tiny end spring is unnecessary: fixed corner seats
perform its locating job without another flexible part, force balance or release
operation. The card's own chamfers already provide the mating geometry. A tighter
rectangular guide would retain some clearance or bind variable cards; the relieved
corner seat instead establishes two contacts, with slight height variation as its
tradeoff. The user explicitly accepts pressing and stronger grip, and subsequently
authorizes independent cap exploration. Full-product validation remains dependent
on actual seating and cap use.

[Geometric and mechanical checks](notes/corner_seat_checks.json) establish:

- 25 seating cases across all five slots, using conservative chamfered envelopes
  49.6–50.4 mm wide, 1.8–2.2 mm thick, with selected 3.8–4.2 mm corner chamfers.
  Both ramp distances are zero, rigid seat intersections are absent, the clip has
  positive relaxed interference, and ±0.1 mm lateral moves intersect the seat.
  These assumed variations are not measurements. Seated height in those cases is
  2.0–2.8 mm; the relieved central floor does not interrupt corner contact.
- 88 hand-corrected funnel poses and 22 final corner-guided poses have no rigid
  intersection with leaves omitted. Funnel travel is 3.8 mm in 0.38 mm steps;
  offsets start at ±1.5 mm X / ±1 mm Y, lean ±2°, yaw ±1°. Final corner correction
  samples 1.5 mm lateral travel in 0.15 mm steps. This is sampled path evidence,
  not passive centering, friction or elastic insertion proof.
- Shared cantilever screens use an explicit uncalibrated homogeneous isotropic
  modulus range of 1000–2000 MPa and the 13 mm contact height. Stem travels of
  0.35, 0.55 and 0.85 mm remain within 1.0 mm relief and below a provisional
  1.5% strain screen; the largest predicted strain is about 0.91%.
  The actual pad/plate bending, root concentration, layers, friction and creep
  are omitted. This is a trial screen, not printed strength or force calibration.

[Final CAD/export/slice record](notes/corner_seat_review.json): valid geometry,
matching STEP/STL, OrcaSlicer 2.4.2 reference Q2C PETG slice, no notices/review
flags, and no generated automatic supports. [Targeted stem path review](notes/corner_seat_paths.json)
found filled 1.2 mm stem sections at three X positions on each of Z=8 and 11 mm.
That supports the local solid idealization, not isotropy or layer bonding.
Source, export, profile and G-code identities are retained with the reports.

FDM review: a continuous flat floor provides bed contact; leaves and seats grow
from attached floor/body geometry. Ramps have no suspended starts or roofs;
relief pockets open upward. Outer corners, bed edges, divider crests and contact
pad have deliberate edge treatment; exact ramp mating faces remain planar.
Vertical layers make spring-root bonding a physical uncertainty. Orca accepted
the unchanged small layout under its selected printer profile, including print
aids. The user's actual profile remains unknown; the STL smoke slice does not
verify Orca's GUI STEP import. No physical claim is made for this revision.

```sh
uv run --locked python model/filament_swatch_box_study/check_corner_seat.py
./evaluate_model.py model/filament_swatch_box_study/card_base_corner_seat_5.py --views none --slice
```

## Physical history and print status

The first five-card baseline (`ff71602`) generally worked but rocked strongly
front/back when touched and varied laterally, spoiling row alignment. PETG was
confirmed; actual dimensions and settings were not. Floor contact did not tighten
its 0.8 mm thickness clearance or 4 mm width clearance. Its CAD entry checks
(1,008 sampled poses) and clean reference slices established possible entry and
slice acceptance, not seated steadiness; details remain in [baseline evidence](notes/base_tests_review.json).

The PETG locating revision (`cfa8988`) was then printed. The user reports its broad
clip pushes/grips nicely, while the tiny end spring has no useful pushing force.
They confirmed keeping the broad clip, accepted a final press and requested a
much firmer grip. This is partial physical success, not an accepted lateral seat.
Earlier [spring screens](notes/petg_seat_checks.json), [local path review](notes/petg_leaf_paths.json)
and [slice record](notes/petg_seat_review.json) did not establish useful opposing
force in the real contact sequence. The report neither calibrates material nor
identifies a print defect. Actual printed file hashes and latest settings remain
unconfirmed; PETG remains the agreed next-trial material.

The earlier straight-slot concepts were questioned for difficult reinsertion
before printing. `study.py`, `inspect_lift_off.py`, `inspect_flip.py`,
`inspect_full.py`, `inspect_guides.py` and `check_study.py` retain rough 20-slot
concept history. Their cover/hinge envelopes do not qualify any current closure.
All `inspect_*.py` entries are display-only; never export their reference cards.

The latest D prototype was then reported printed on 2026-10-02. Fit was okay;
the base is probably fine, but the hood feels too fat even for opaque filament.
The base/bottom and hood/top feel square or flat with inadequate edge rounding.
This is a physical form/handling rejection with partial fit success, not a
reported mating failure. Existing source includes small rim fillets/chamfers;
their presence did not establish the user's desired comfort. No print defect,
material cause or missing-feature diagnosis is established. The earlier rigid
checks, beam screens and clean slices remain narrower geometry/manufacturing
evidence; they did not qualify hood bulk or hand comfort. Release force, loaded
retention and durability remain unreported. Exact printed files and settings
are still unconfirmed; PETG is confirmed for the proposed translucent variant.

The table preserves completed physical trial reports and distinguishes them
from other unreported prototypes. Printed and usable remain separate questions.

| Item | Print status | Artifact(s) | User result or remaining physical checks |
| --- | --- | --- | --- |
| Test — H connector without handle | Unknown — no print report | `cap_h_connector_test.step/.stl` | Larger head and nail recesses; actual insertion, relative-base lift and occasional removal need printing. No tall wall/hoods represented by sample |
| Test — H complete five-card module | Unknown — no print report | `cap_h_module_5.step/.stl`, `cap_h_base_5.step/.stl`, `cap_h_key.step/.stl`; unchanged G hood | CAD checks passed; new entry notch, whole-base stiffness, comfort and retention remain physical questions. Desk-supported only |
| Test — G modular connector | Unknown — no print report | `cap_g_connector_test.step/.stl` | Actual end geometry; vertical fit, planar play and removal await the small trial. No hood restraint or full-module stiffness represented |
| Test — G compact five-card module | Unknown — no print report | `cap_g_module_5.step/.stl`, `cap_g_base_5.step/.stl`, `cap_g_hood_5.step/.stl`, `cap_g_key.step/.stl` | CAD/reference slices passed; reduced frame, card grip, hood seating/release and joined handling untested. Desk-supported proof only |
| Test — F flush hood with E five-card base | No — user explicitly has not printed it yet | `cap_f_flat_5.step/.stl`, `cap_f_hood_5.step/.stl`, unchanged `cap_e_base_5.step/.stl` | User prefers appearance and keeps this version; CAD/reference slices passed. Comfort, thin-shell feel, fit/seam contact, optics and retention need the complete trial |
| Test — E thin hood and matching five-card base | Unknown — no print report | `cap_e_thin_5.step/.stl`, `cap_e_hood_5.step/.stl`, `cap_e_base_5.step/.stl` | Raised exterior band rejected before printing; narrower CAD/slice evidence retained. F uses this same base with a flush hood |
| Test — selected D five-card press-on cap/base | Yes — latest prototype reported printed | `cap_d_snap_5.step/.stl`, `cap_d_hood_5.step/.stl`, `cap_d_base_5.step/.stl`; printed files unconfirmed | Fit okay; base probably fine; hood too bulky and exposed edges insufficiently rounded. Partial success; revision required. Loaded retention, force, recovery and dwell unqualified |
| Test — current five-card corner seat | Unknown — standalone artifact unconfirmed | `card_base_corner_seat_5.step/.stl` | D's integrated base reported probably fine; this separate trial and detailed centering/grip result remain unconfirmed |
| Test — A five-card hood/rounded base | Unknown | `cap_a_lift_off_5.step/.stl`, `cap_a_hood_5.step/.stl`, `base_rounded_5.step/.stl` | No report; cap fit, seating, lift, protection and handling unqualified |
| Test — B five-card drawer/enclosure | Unknown | `cap_b_drawer_5.step/.stl` | No report; running fit, overlap, tray support and card access unqualified |
| Test — C five-card hinged hood | Unknown | `cap_c_hinged_5.step/.stl` | No report; axle/key fit, last-card access, stop strength, stability and handling unqualified |
| Test — five-card PETG spring seat | Yes | `card_base_petg_5.step/.stl`, `cfa8988`; printed hash unconfirmed | Broad clip grips nicely; tiny end spring ineffective; actual forces/setup unknown |
| Test — five-card free-clearance base | Yes | `card_base_test_5.step/.stl`, `ff71602`; printed hash unconfirmed | Generally works, but rocking and sideways variation unacceptable; PETG, settings unknown |
| Test — fifteen-card first base | Unknown | `card_base_test.step/.stl` | No report; earlier clearance interface remains provisional |
| Final printable object | N/A | H/G modular proofs and F/E complete five-card prototypes; no qualified production box | Normal use and retention await physical results before full-capacity exports; joined carrying remains unqualified |

## Attribution

Primary language model: **GPT-6.1 Sol**. Reasoning effort: **high**. The exact
model and effort are explicitly user-provided, refining the earlier family-only
**GPT-6** record where variant and effort were not exposed. Harness: **Codex**,
shared repository workspace. Provider: **OpenAI**. No subagents. Swatch dimensions and reference
outline derive from the existing user-provided SCAD source; its historical
Gemini attribution remains with that object.
