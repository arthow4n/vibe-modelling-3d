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
