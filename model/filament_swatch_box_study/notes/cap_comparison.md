# Cap exploration — authorized autonomous phase

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
another complete module until the grip trial resolves this local question.
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
strength, long rows and joined carrying remain unqualified; no new print report
has been received for I.
