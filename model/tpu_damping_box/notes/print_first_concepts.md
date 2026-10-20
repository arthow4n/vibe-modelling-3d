# Print-first surface isolation — complete liners with few parts

[Object status](../README.md) · [Overview SVG](../renders/concepts/print_first_overview.svg) ·
[P1 nested cups: printing and assembly](../renders/concepts/print_first_nested.svg) ·
[P2 folded blank: printing and assembly](../renders/concepts/print_first_fold.svg)

The earlier E drawings explained possible springs without resolving how the
**whole liner**, including floor and lid, would print and assemble. The user's
latest correction makes that insufficient: prefer one piece, accept two, avoid
complicated assembly, and show printability in the explainer. This review replaces
the active E1/E5/E6 shortlist with two manufacturing concepts. **Neither is a
print-ready model or a verified improvement.** B08/B16 remain the approved printed
baseline. No CAD, exports, slicing or profile changes are made in this phase.

The user confirms **up to two cup pieces, plus the usual lid pad**. P1 meets
that preference: two cup parts and one pad, three pieces for the complete liner.
P2 uses one connected body blank and one pad, two total, but requires eight
folds. **Latest user correction: P1 is set aside.** The user points out that
thin TPU walls have already printed poorly in this repository, so a separately
printed thin-walled cup does not resolve the known manufacturing risk. The
earlier recommendation below is superseded. Part count was acceptable; upright
wall reliability is the objection. **P2 is also rejected:** the user dislikes
folding because adopting it to other models would introduce constructions they
consider impossible to print. A printable flat net for this simple fixture is
insufficient evidence of a usable architecture for other shapes. Do not replace
it with separate folding tiles. The existing rigid test box and its lid are
reused, not additional printed liner components.

The retained [dental wall report](../../dental_travel_case_liner/README.md#wall-
print-feedback--2026-10-19) records local breaks on both skins of the tall
liner. The short sunglasses liner was successful; exact causes and printed
dental revision remain unknown. The separate R1 missing-wall slice failure and
R2 Classic repair are different evidence: paths existing in a slice do not prove
reliable deposited walls. P1 removed print-time core junctions but retained
upright walls and offered no representative physical evidence for them. I should
have applied this known failure before recommending that architecture. Both
proposals are now retired from the active shortlist. This correction does not
establish that all thicker TPU cups fail, nor justify silently thickening P1 and
promoting it again. Thickness is unconstrained, but reliability and useful
damping would both need support for any genuinely revised construction.

## What the manufacturing review changes

| Earlier suggestion | Current decision and reason |
| --- | --- |
| E1 / P1: two cups with attached wall springs | **Set aside after the latest user correction:** still relies on upright thin TPU walls despite earlier physical failures. Integral floor posts and a simple assembly did not resolve that risk. |
| E5: independent wave insert | Retired from the active shortlist. A constant-section insert can be printed upright, but a complete liner adds core retention and floor/lid pieces for no established benefit over an integral carrier. |
| E6: loose hollow tubes | Retired. Upright open tubes need no tube roof, but arranging/retaining numerous tubes and the floor modules is the wrong assembly burden here. This is not a claim that individual tubes are unprintable. |
| E2/E4 | Remain dropped after user feedback. P2 borrows E2's useful flat-print orientation, replacing separate wall tiles with **one connected blank**, not reviving its multipart assembly. |
| E3 | Remains set aside. Thick unsupported panels or boundary supports alone do not establish better finish or damping. |

Do not rotate a complete cup onto its side and assume the cavity roof will
print. Do not show springs floating above the bed, close a broad gap with an
unexamined horizontal roof, or omit the floor and lid from the count. Those
construction shortcuts are excluded from both new proposals.

## Shared assumptions and reading the drawings

All TPU is normal **black TPU**. Blue identifies the contact skin/inner cup,
dark grey the backing/outer carrier, orange flexible core or fold-band material,
pale grey the existing rigid box, white empty space and red force/motion arrows.
No second material or hardness is implied. The drawings label these roles in
words and show a bed line and build direction. Sections are illustrative, not
to scale; exaggerated load shapes are not calculated deformation.

Use the repository's ordinary **Classic** approach, nominal 0.4 mm nozzle and
0.2 mm layers; no Arachne, custom toolpath or soluble/trapped support is assumed.
Wall and overall thickness are unconstrained by the user. New dimensions must
be selected to generate reliable Classic walls rather than repeat the earlier
missing-wall failure. A drawing cannot establish actual perimeter generation,
bridge speed, travels, seam count or surface finish.

Both proposals have **solid regions around corners**, tapering into the active
core. This is a deliberate change from the hollow A/B R2 corner cores. The
user's request does not establish a measured land width. P1's corner lands are
solid within each cup, not a bonded full-thickness bridge across its assembly
clearance. P2 uses solid fold bands and solid overlapping corner flaps; its fold
bands are thinner than the sandwich so they can bend. These are different
interpretations of a robust corner, with untested stiffness and fit.

## Historical P1 — plain inner cup in an integral spring carrier (set aside)

Print **two upright cup parts**, then drop one inside the other. The blue cup is
an ordinary closed-floor, open-top cup, with no internal-core junctions in its
wall print. The dark carrier includes the wall springs and floor posts, so no
loose cores must be placed between the cups. Print one conventional lid pad
flat. Total: **three pieces**, two seating operations, no clips, glue or tools.

The print sequence in the [detailed SVG](../renders/concepts/print_first_nested.svg)
is constructive:

1. Inner cup: solid floor directly on the bed, then walls rising from it, open
   mouth up. There is no cavity roof. Its seam still exists.
2. Carrier: solid base on the bed, then open C-shaped spring profiles repeated
   vertically from that base. Their curved shape is in **XY**, not a horizontal
   cantilever starting halfway up Z. Every new spring layer rests on the same
   spring section below. The lower and upper channel ends are not capped across
   their voids. Vertical floor posts also start on the base.
3. Stop the springs and inner cup at a common lid-seat level. The carrier's
   outer guide wall may continue higher, without bridging across the gap.
4. Print the single pad flat using a B08-style short-span closed-skin core as
   the starting architecture. Its upper skin still has bridge layers. Cup lip
   and carrier spring tops support it after assembly; there is no additional
   inner-lid/outer-lid pair.

The wall load path is contents → plain inner cup → bending spring → carrier →
existing rigid box. The before/load section shows the spring curving into its
remaining empty space as the inner panel moves outward locally. The two cups
are not welded together. Spring height, gap, wall thickness, contact/preload and
travel remain design variables; the drawing sets none as validated dimensions.

For downward impacts the inner floor rests on the carrier's integral posts.
Those posts load in compression/bending, unlike the side springs. Their
height/slenderness and top contact must be chosen to avoid simply creating a
stiff solid floor: **wall behavior does not qualify floor damping**. More overall
thickness is available if needed. No broad printed floor roof spans the gap;
the inner floor is printed on its own bed, then installed on the posts.

Solid corner zones need sufficient assembly clearance and gradual load transfer.
They can otherwise become hard bypasses that suppress the active spring travel.
Posts and wall springs can also imprint the cup **after** assembly. P1 removes
print-time core branching from the inner surface, not every source of marks,
seams, friction or poor damping.

If advanced to CAD, reject or revise it if the carrier has isolated spring
starts, its top retention closes a broad roof, its floor posts are too stiff,
corner lands jam the cup, or the lid requires more loose parts. No auxiliary
floor module is hidden in this count. The assembly meets the clarified cup-plus-
pad preference, but this does not resolve the wall-printing objection; P1 is no
longer recommended.

## Historical P2 — flat sandwich blank, folded into the existing box (rejected)

Print one connected cross-shaped body blank **contact face down**, plus one lid
pad in the same face-down orientation. The floor and four wall panels are joined
by solid flexible fold bands. Four integral solid corner flaps fold behind the
adjacent walls; the existing box holds them there. Total: **two pieces**; four
wall folds plus four flap folds, insertion, then seating the pad. No separate
tiles, tubes, pins, clips, springs or glue.

The [detailed SVG](../renders/concepts/print_first_fold.svg) separates print order
from assembly order:

1. All five contact skins start flat on the bed and print before any core exists
   above them. The resulting contact finish is the build-plate/first-layer
   finish, with its texture and possible defects; smoothness is not guaranteed.
2. Short ribs grow directly from these skins. Solid, core-free bands connect
   the panels and form the corner flaps. Core height tapers down before folds.
3. The back skins close **small cell roofs**, supported by ribs at both ends.
   An initial engineering example is 0.8 mm ribs with 1.2 mm clear gaps, not a
   universal bridge limit or selected printable specification. Core density may
   be too stiff; increasing void fraction must preserve supported roof ends.
4. Flex the four walls upward and fold their solid flaps outside the neighboring
   wall. Insert into the rigid box. Seat the one matching lid pad.

Core ribs deform between the skins under load, using the empty cells as motion
space. This retains the printed B sandwich principle while changing when/how
its contact surface prints. It is an orientation/connected-blank alternative,
not a claim to have invented a different viscoelastic mechanism. The cell core
may still affect cooling or warp the bed-printed skin after release.

The main manufacturing advantage is that there is **no growing upright contact
wall next to repeated core junctions**. The short backing bridges remain a
stringing/droop risk inside the core. A lid pad needs the same small-roof review.
Neither closed cell roofs nor dense ribs are assumed to improve damping by
being printable.

Its costs are significant: bend force and fatigue, wall spring-back, corner
stack thickness, flap sliding/overlap ridges and a larger flat print footprint.
Fold bands are solid but deliberately thinner; they are not solid full-sandwich
corner blocks. The blank must include bend allowances so its assembled outside
fits the unchanged fixture. A 34 mm-class test cup suggests a roughly 100 mm
cross before flap/bend allowances, but full-size application nets may exceed
the bed. Do not extrapolate this construction to the long dental liner without
a fresh footprint and handling check.

Reject it if folding/insertion is bothersome or if the box cannot retain all
flaps without extra fastening. **One connected print is not simple assembly by
definition.** It meets a strict two-piece count but may still fail the user's
simplicity preference. There is no fully formed one-piece cup proposed here
that demonstrably isolates all contact faces from its core during printing.

## Evidence and next decision

This phase checked the layer-support logic in the drawings, not new geometry.
The existing [R2 Classic evidence](../README.md#ordinary-classic-repair--r2) and
[B physical report](b_surface_concepts.md) establish a usable baseline, not
qualification of P1 or P2. B's previously printed short-span floor/pad cores are
a starting reference for the pad, not proof of changed spans or interfaces.

The two proposals now expose build orientation, all starts/roofs, corner
construction, floor/lid construction and complete part counts. That permits a
choice **before** modelling. Both are now retired: P1 retains the thin upright
wall risk; P2's folding architecture is rejected for adoption to other models.
No proposal remains selected from this review and no new physical test is
reported. This is a corrected architectural decision, not an inconclusive slice.

Future exploration should start from the approved B evidence and compare
preformed constructions that remain printable when adapted to real container
shapes. One cup piece is preferred, up to two cup pieces plus the usual pad are
acceptable; complicated assembly, thin separate cups and folding are not the
current route. This does not yet select another core, guarantee a smoother
surface or authorize new CAD. The next authorized phase remains concept
investigation/SVGs, with existing physical failures screened before suggestions
are recommended.

| Item | Print status | Artifact(s) | User result or remaining physical checks |
| --- | --- | --- | --- |
| Test piece(s), P1/P2 | N/A | SVG explainers only; no exported print files | No new physical trial; surface/damping remain unknown. |
| Final printable object(s), P1/P2 | N/A | None; concept phase | P1 set aside; P2 rejected. |

- CAD/export/slicer status: N/A — no new model evaluated or sliced.
- Physical validation: unknown for P1/P2; B08/B16 approval remains separate.
- Documentation validation: SVG XML parsing, raster preview inspection and
  affected local-link checks; no CAD/slicer claims derive from those checks.
- Attribution, 2026-10-21: primary model GPT-6 family; exact runtime identifier
  and reasoning effort not exposed. Codex shared-workspace CLI/API agent,
  provider OpenAI, no subagents. User supplied print/assembly preferences and
  black-TPU observations; agent authored the manufacturing revisions and SVGs.
