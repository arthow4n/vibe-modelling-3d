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
The cap roof's inner height is 86.8 mm: 4 mm above the conservative 82.8 mm card
top. Twenty positions use a 149.4 mm base length, well inside the default Q2C
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
