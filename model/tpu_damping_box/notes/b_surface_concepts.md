# B surface improvement — print report and SVG discussion

[Current object record](../README.md) · [Existing B files/setup](../README.md#ordinary-classic-repair--r2)

**Decision, 2026-10-21:** B08 and B16 are approved experimental liners. B08 is the
preferred starting point for the next investigation because the user perceives
slightly fewer print issues, with little damping difference from B16. This is a
tentative preference, not a measured reliability ranking. All six latest A/B/C
pairs were printed and compared. A and C are rejected for damping relative to
S16; retain their files and negative results without recommending them again.

**Earlier SVG-phase scope:** record feedback, inspect existing evidence, research and
produce SVG suggestions. No new CAD models, STEP/STL exports, altered presets,
printing or application-liner redesign in this phase. All proposed dimensions
below are discussion choices; they are not slicer-qualified replacements.

**Latest research route:** the user favors discrete ties over ribs, asks for
curved joints and thicker skins, and authorizes autonomous slicing/path review.
The [B-derived wall study](tie_surface_study/README.md) owns those new results;
it does not replace or expand the physical approvals below.

## Physical report — 2026-10-21

The user identifies the latest A/B/C variants, associated by conversation with
R2 A16/A20/B08/B16 (`6356e74`, published in `b121b81`) and solid C12/C16
(`c71c88b`, published in `5219b7c`). Exact printed artifact hashes are unreported.
The retained comparison is **S16**, not an unspecified S variant. Latest material
brand/hardness, moisture state, printer settings, import format, orientation,
seam location, photos and detailed test protocol remain unknown. Earlier liner
reports establish 0.2 mm layers, but the latest complete runtime settings are
not independently confirmed.

| Printed pair | User result | Decision / limit |
| --- | --- | --- |
| A16 and A20 | Both damp worse than retained S16. Exterior appearance looks better, but damping is not good enough. | Reject both as damping choices; appearance does not override the rejected function. |
| C12 and C16 | Solid controls provide a little effect, perceived as almost no damping. | Reject both as damping choices; no claim that all solid TPU liners are ineffective. |
| B08 and B16 | Damping feels similar to S16 and to each other; both approved. The user ultimately describes the object-facing finish as already better than S16. B08 may have slightly fewer print issues. | Carry both approvals, start discussion from B08. Finish improvement remains incomplete. |
| S16 | Retained and compared again; useful accepted damping reference. | Preserve its scoped approval; B approval does not invalidate the successful sunglasses application. |

Approximate phone-app observations, preserved as recalled rather than calibrated
measurements:

| Comparison | Recalled displayed level |
| --- | --- |
| Direct box impact / no damping | Roughly 60–70 dB |
| A and C, initially grouped by the user | Roughly 50–55 dB |
| A, subsequently described separately | Around 50 dB |
| S16 | Around 40–45 dB |
| B08 / B16 | No numeric reading stated; subjectively similar damping |

Do not infer separate C12/C16 values, a B dB value, attenuation, percentage
reduction or repeatability from these ranges. Phone model/app, weighting,
peak/average mode, microphone position, background level, strike/shake force,
contents, repeats and timing are unreported. The recalled A/C grouping and the
subjective near-absence of C damping are both retained, without forcing them
into an invented precise ranking.

The user reports **substantial stringing** and artifacts near a seam or path
transition, dependent on print direction/travel. No exact defect locations or
photos are supplied, so strings, seam blobs, tie attachment marks and other
surface unevenness are not yet attributed to one cause. Here **object-facing**
means the inside container surface that touches the contents; shell-facing is
the opposite surface. This replaces the ambiguous use of “exterior” when
planning the improvement, without changing what was said about A's appearance.

The user believes B's small, numerous ties may make it less likely to break
in a longer print than S16. This is a hypothesis, not a successful tall-liner
trial, insertion-strength test or quantified failure rate. No new breakage is
reported in these six samples. Fatigue, long-term integrity, application fit and
reliable large-print transfer remain unqualified.

## Later review of D — 2026-10-21

The user says D1–D3 are not invalid, but they are inadequate as the main answer:
changing tie density or timing still leaves the face affected by its internal
structure. They request different architectures. Thickness is explicitly **not
constrained** in the next exploration. They clarify that the filament is normal
**black TPU**: visible surface patterns are the main issue, with occasional
apparently random bumps, explicitly excluding translucent material. They also
request substantial solid corner regions to avoid corner print defects. The existing A/B designs
have corner air regions, not dedicated full-thickness solid corner lands.

The D recommendation below is **superseded as the next direction**, not a
physical rejection or proof that its secondary experiments cannot help.
[Current architectural investigation and SVGs](preformed_surface_concepts.md) address
these clarifications. All earlier print reports and approvals remain intact.

## Investigation and proposals

The investigation below uses the existing B08/B16 geometry and saved ordinary
Classic slices. It does not reproduce the unidentified actual print settings.

### What the retained paths actually show

[Actual existing-route SVG](../renders/concepts/b_existing_routes.svg) ·
[Saved metadata](b_existing_routes.json) · [reader](../review_b_surface_routes.py).
Run `./execute.py model/tpu_damping_box/review_b_surface_routes.py` while the
original native receipts' retained raw directories remain available. It checks
the raw G-code, STL and relevant source identities against the existing R2
review before reading them. No new slice is run and no model is rebuilt.

| Existing cup, ordinary TPU Classic | Z 3.0 mm: ties present | Z 4.4 mm: between rows |
| --- | --- | --- |
| B08 | 30 geometrically disconnected deposition chains | 4 chains |
| B16 | 58 geometrically disconnected deposition chains | 4 chains |

A chain break here is a >0.005 mm discontinuity between consecutive deposited
segment endpoints in the cup. It is **not a counted seam, retraction, string,
actual travel or full-print reliability statistic**. Wipes and routed travel
can intervene. The orange dashed links in the SVG join endpoints for
explanation; they do not reproduce the actual travel commands. Only two layers
are compared; pad and inter-part moves are excluded.

Both tie-layer slices still include a **closed, full-width object-facing
contour**, with its start/end at a cavity corner. This is not another missing-wall
failure. The extra cell boundaries add nearby print work and chain starts even
though the visible face is designed flat. B16 has more such chains at this
sampled tie layer despite its larger ties. That supports investigating B08 as a
simpler starting point, but does not prove why the actual B08 print looks better.
The path sequence differs substantially between tie rows and intervening layers;
periodic attachment marks or pressure/heat changes are hypotheses to distinguish
from seam and travel artifacts.

The saved setup is Classic with 0.42/0.45 mm widths and thin-wall detection off.
It has **aligned seams**, `seam_gap=0%` and `reduce_crossing_wall=0`. Wipe is
already on; merely proposing “turn on wipe” would not be a new experiment.
Retraction length is 0.8 mm and minimum travel for retraction is 1 mm in this
saved setup; these are evidence, not newly recommended settings. Actual user
runtime values remain unknown.

### Three geometry suggestions

[Overview SVG](../renders/concepts/b_improvement_overview.svg).
All three start from B08's **1.6 mm total**, **0.5 mm continuous skins** and
**0.6 mm wall gap**. They retain flat object-facing surfaces and substantial
**0.8 mm minimum tie width**. None specifies an impossible single uninterrupted
nozzle path or guarantees fewer travels. Green marks are connections across the
gap; both skins are hidden in the wall-face sketches. These are schematic, enlarged,
non-printable diagrams, not to scale or slicer previews of new designs.

| Proposal | Candidate geometry | Question it could answer / main cost |
| --- | --- | --- |
| **D1 — phase-shift the tie heights** · [SVG](../renders/concepts/b_improvement_phase.svg) | Retain 0.8 × 0.8 mm B08 ties, 4.4 mm pitch along the wall and in height. Adjacent columns repeat Z offsets 0, 1.0, 2.2, 3.2 mm. | Does spreading tie starts across height make the surface less visibly banded? In an interior layer at most two of seven columns per face are active rather than all seven. Same nominal tie material per interior repeat, but more layers contain ties and total travel may stay the same or increase. Top/bottom row termination and corners still need design. |
| **D2 — remove alternate ties** · [SVG](../renders/concepts/b_improvement_sparse.svg) | Keep 0.8 × 0.8 mm ties only on alternating checkerboard sites. Each row has 8.8 mm horizontal spacing; the next is offset by 4.4 mm, still 4.4 mm higher. | Can genuinely fewer cell boundaries/starts improve finish and stringing without losing support or damping? About half the ties remain in an interior repeat; skin spans become longer. Reduced connection count is not itself a strength improvement. |
| **D3 — taller ties in fewer rows** · [SVG](../renders/concepts/b_improvement_tall.svg) | 0.8 mm tie width, 1.6 mm height, 4.4 mm horizontal pitch and 8.8 mm row pitch. | Do fewer geometry turn-on/turn-off heights help? At 0.2 mm layers each tie persists for eight layers rather than four. Nominal attachment fraction stays equal to B08 in the interior repeating pattern, but clear height between rows grows from 3.6 to 7.2 mm. Total tie-active layers/starts need not fall, and stiffness/damping can change despite the matched fraction. |

**Historical suggested priority (superseded by the review above):** D1 first for a controlled surface-consistency comparison
that retains the interior average tie amount, and D2 for a distinct reduction in
cell count. D3 is a lower-priority alternative for separating row-change effects
from nominal attachment amount. These are suggestions for discussion, not
approval to build them. All need ordinary Classic path review later, including
wall continuity, bridge starts, route changes, seams and actual travel/retraction
counts before any print recommendation. A longer representative upright print
would then be needed to answer the user's large-print concern; a new small cup
alone could not establish it.

These suggestions address **upright walls**. The current B floor and lid pad
would stay as the reference in a later controlled wall experiment unless a
separate change is agreed. Their horizontal roof bridging is a different routing
problem; a wall-face sketch does not qualify a floor redesign. Whole-box
corners, rims and minimum-thickness claims remain open.

### What geometry cannot settle by itself

A useful process-only comparison, proposed for later rather than implemented,
would retain B08 geometry and change one routing control at a time. Orca's
[official wall guidance](https://github.com/OrcaSlicer/OrcaSlicer/wiki/quality_settings_wall_and_surfaces#avoid-crossing-walls)
describes wall-avoiding detours and their travel-time trade-off. That is relevant
because the saved B profile has the option off; it is not a promise that every
internal move or cup-to-pad transfer can avoid the object-facing skin. No new
profile or G-code has been generated here.

The [official seam guidance](https://github.com/OrcaSlicer/OrcaSlicer/wiki/quality_settings_seam#seam-position)
explains the placement trade-offs: aligned seams concentrate a seam, while
nearest placement reduces travel but scatters seams. The current flat
object-facing contour already has a corner start in the inspected layers. First
identify whether observed defects follow that corner or the tie rows, rather
than adding a groove or moving artifacts onto broad contact faces. No seam
recess, scarf requirement or face texture is proposed. Three-wall ordering
advice cannot simply be applied to a single-path 0.5 mm skin; changing the
number in a preset does not create room for three paths.

Stringing is not evidence that the tie geometry is the only cause. Manufacturer
[moisture guidance](https://help.prusa3d.com/article/drying-filament_332086#how-to-recognize-if-the-filament-has-gathered-humidity)
identifies TPU as moisture-sensitive and connects moisture with surface defects;
its [flexible-material guidance](https://help.prusa3d.com/article/flexible-materials_2057)
also discusses stringing and oozing. Spool condition, temperatures and extrusion
restart behavior are unmeasured in these prints. A later controlled comparison
should keep spool condition, material, orientation and temperatures fixed; no
new drying temperature or arbitrary retraction increase is prescribed here.
Geometry can remove opportunities for disruptive routing, but cannot prove
that strings will disappear. Source pages were checked on 2026-10-21; live docs
may include features newer than the retained Orca 2.4.2 slices, so this proposal
uses only the existing named controls and does not assume newer seam features.

## Print status and next action

| Item | Print status | Artifacts | Evidence / next action |
| --- | --- | --- | --- |
| Latest R2 A/B and solid C test pairs | Yes — user report, 2026-10-21 | Existing `support_A16/A20/B08/B16`, `solid_C12/C16` | B08/B16 approved; A/C rejected for damping; remaining finish and tall-print limits above |
| D1/D2/D3 suggestions | N/A — SVG discussion only | Four proposal SVGs plus existing-route SVG/metadata | Discuss options; no new model or printable export |
| Final application liner | N/A — no new application design | None new | Existing dental defects and transfer question remain unresolved |

The earlier digital verification receipts predate this report and remain scoped
to CAD/slicing. Their physical UNKNOWN entries are not the current human damping
verdict; this record supplies that later verdict without rewriting old receipts.
No numerical strength/damping inference or shared automation change is justified
by the phone ranges alone.

Attribution: primary language model GPT-6 family; exact runtime identifier and
reasoning effort not exposed. Harness: Codex shared-workspace CLI/API agent;
provider OpenAI. No subagents. User supplies the print results, approval and
surface priorities; this phase authors the interpretations, retained-route
inspection and SVG proposals. Existing model/profile attribution remains intact.
No third-party diagrams or meshes were copied.
