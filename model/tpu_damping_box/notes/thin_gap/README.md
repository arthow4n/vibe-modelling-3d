# Thinner T08 follow-up: L20 and L18

The [current uniform L20 standard](../l20_standard.md) supersedes these thin-floor files. This record preserves the earlier experiment and its physical feedback; current walls/floor/pad all use 0.8/0.4/0.8.

**L20 remains preferred for walls and damping; interior-floor robustness is unresolved**, following the user's print comparison of both thinner variants against approved T08. L18 is also accepted. The user explicitly clarified that the printed variants are **L20/L18** after initially saying T20/T18. T08 remains an approved control; T16 remains rejected as too firm and somewhat noisier.

## Floor clarification — 2026-10-23

The user canceled a full dental L20 liner print after the early layers: wall regions look okay, but the contents-facing floor surface shows breaks/cracking and is difficult to print cleanly. They clarify this is not worse than the earlier approved experiments: their interior floors feel similarly fragile. Preserve the wall/damping preference; withdraw any implication that the floor was robustly resolved. This is one dental application print plus a user comparison with earlier experiments, not a new print of every experimental variant. [Current section explanation and SVG proposals](../../../dental_travel_case_liner/notes/floor_surface_review.md). Models and print profiles remain unchanged.

## Physical feedback — 2026-10-21

The user reports both L18 and L20 printed and fine compared with T08. Damping feels roughly equally good across all three. **L20 feels like the sweet spot**: its bottom surface has slightly fewer printing defects despite ironing being on, and overall print quality is almost equal to T08. The user prefers L20 over T08 because it is thinner (`2.0` versus `2.2 mm` total upright wall). L18 remains acceptable, but L20 is preferred for print quality.

The cause of the bottom-surface difference is unknown. The modeled floor/pad construction is unchanged, so this report does not establish that narrowing the upright gap caused a surface improvement. Ironing was on in the actual print; flow, speed and spacing are unreported. The retained digital review used no ironing. The designs are TPU 95A experiments; exact printed revision/hash, printer/profile, orientation and whether matching pads were printed or the T08 pad reused are unconfirmed. Prior user-confirmed layer height is `0.2 mm`; no new layer-height report was supplied. This is subjective physical acceptance, without acoustic measurements, internal-gap inspection or durability qualification, and does not qualify a full-size application liner.

| Pair | Skin / upright gap / skin | Total wall | Contents width | Relative wall reduction | Primary files |
| --- | --- | --- | --- | --- | --- |
| **T08, retained approved control** | 0.8 / 0.6 / 0.8 mm | 2.2 mm | 29.6 mm | — | [Existing pair](../t_skin/README.md) |
| **L20, preferred baseline** | 0.8 / 0.4 / 0.8 mm | **2.0 mm** | **30.0 mm** | 9.1% | [STEP](../../thin_gap_L20.step) · [STL](../../thin_gap_L20.stl) · [Python](../../thin_gap_L20.py) |
| **L18, accepted alternative** | 0.8 / 0.2 / 0.8 mm | **1.8 mm** | **30.4 mm** | 18.2% | [STEP](../../thin_gap_L18.step) · [STL](../../thin_gap_L18.stl) · [Python](../../thin_gap_L18.py) |

**L20/L18 encode total upright wall thickness**, not skin thickness. Both have
compact M1-style full IDs on cup and pad, with solid backing and no revision line.
The 34 × 34 × 34 mm external cup, solid corner regions and established shell fit
are retained. Each file contains one upright full cup and one flat matching pad,
placed labels-down. All units are mm; import at 100% scale. Each pair has the same
supplied bed coordinates: arrange them if importing both pairs on one plate.

## Fastest print: both cups, reuse the T08 pad

[**Two-cup STEP plate**](../../thin_gap_cups.step) ·
[matching STL](../../thin_gap_cups.stl) · [Python](../../thin_gap_cups.py) ·
[preview](../../renders/print/thin_gap_cups_isometric.png).
This plate contains **L20 + L18 cups only**, already separated on the bed; use the
printed T08 pad with each test. The full marked cup/pad pairs in the table remain
available if you want additional matching pads. Print this plate **or** the full
pairs, not both copies of each cup.

## Why reduce the gap before thinning the visible faces?

T08 is not proven to be the thinnest printable or useful liner. Its 0.8 mm skins
are already close to two ordinary nominal 0.42 mm wall-width passes. That does
not establish a universal two-line minimum: Classic paths change at ties, widths
and overlap matter, and earlier 0.5 mm B skins were physically usable but looked
worse. The new positive evidence is T08's appearance, so the first thinning
experiment protects those skins rather than immediately undoing them.

A void is not an extrusion line. A 0.4 mm nozzle does not, by itself, require a
0.4 mm modeled gap. The relevant question is whether the **actual selected
Classic paths** keep two separate skins and an open channel. Physical spreading,
sag or compression can still close that channel. With two fixed 0.8 mm skins,
1.6 mm is merely the zero-gap geometric sum, not a useful damping target or an
established manufacturing limit. The rejected solid controls and firm T16 make
physical damping the deciding evidence.

The original trial rationale was that L20 preserves more room to deform than L18. L18 was an
explicit near-limit experiment: its 0.2 mm gap may fuse, bottom out or lose useful
cushioning even when sliced paths remain separate. Neither gap is claimed as a
reliable minimum. The later report accepts the damping and finish of both variants without inspecting their internal gaps.

## What stays the same and how to print quickly

Only the upright gap, corresponding tie span and resulting cavity width change.
T08's 0.8 × 0.8 mm ties, 4.4 mm pitch/seven vertical rows, five complete ties per
row, 4 mm solid wall-end lands and local M1 corner seat are retained. Both new
IDs use the same 0.8 mm stroke style, 0.2 mm recess and 9 × 5.5 mm reserved region
on its connected 10 × 6.5 mm solid backing seat.

The **floor/pad construction is unchanged from T08**: 0.4 / 0.8 air / 0.4 mm,
with 0.8 mm posts and the pad's additional 0.2 mm intended squeeze. The corner and
label construction is also unchanged except for the new letters. Each pad is
**32.0 × 32.0 × 1.8 mm**, geometrically compatible with the printed T08 pad.
**For a faster test, reuse your T08 pad and print only the new cup.** Matching
labeled pads remain included for a fully distinguishable set. The shell needs
no reprint. Wider contents spaces allow slightly more nut travel, so differences
in shaking sound are not isolated material-property measurements.

Use the same supplied [Classic TPU process](../../profiles/tpu-support-classic-process.json),
[TPU filament profile](../../profiles/tpu95a.json) and
[Qidi Q2C 0.4 mm printer](../../../../.codex/skills/orca-slicer-printability/profiles/qidi-q2c-petg/qidi-q2c-0.4-nozzle.json).
The retained digital review setup is **0.4 mm nozzle, 0.2 mm normal/first layers, Classic,
two wall loops, ordinary 0.42/0.45 mm widths, thin-wall detection off, supports
off, thin bridges, no ironing, 100% fill inside CAD material**. Air channels are
CAD voids; the fill percentage does not fill them. Keep supplied orientation,
labels on the bed. No Arachne or narrow-width recovery preset is introduced.

The comparison is complete: both variants have user-reported acceptable damping, with L20 preferred. No repeat comparison print is required. Printed gap separation and long-term integrity remain unmeasured.

## Evidence and source scope

[Parametric source](../../thin_gap_design.py) reuses T08's horizontal-core,
corner-seat and pad builders while declaring a separate upright gap. The
approved `t_skin_design.py`, T08/T16 source entry points, STEP/STL and old native
slice records are **unchanged**. New letter paths use the same M1 stroke recipe
with L/2 glyphs added locally; historical artifact associations remain intact.

Native final reviews: [L20](L20_final.json) · [L18](L18_final.json).
[Actual wall/gap paths](../../renders/print/thin_gap_wall_paths.svg) ·
[Label/backing paths](../../renders/print/thin_gap_m1_label_paths.svg) ·
[Support-location review](../../renders/print/thin_gap_support_review.svg) ·
[Machine-readable path evidence](paths.json).
Full G-code: [L20](L20_paths.gcode.gz) · [L18](L18_paths.gcode.gz).
Product verification: [L20](L20_verification.json) · [L18](L18_verification.json).

The final review covers all four walls through 152 upright layers, outside
contours through all 170 cup layers, actual core crossings, corner/end lands,
horizontal roof/core paths, and negative letter strokes/counters/backing.
Geometry checks cover shell/pad insertion, both skins, floor/roof/contact faces,
solid corner material and complete label backing. Slicer width envelopes are
not measured printed bead shapes. The matching STL smoke review does not qualify
Orca's separate GUI STEP import.

Both paired native CAD exports are valid and both Classic slices complete with
no log notices. The retained width-envelope sections give **0.8 mm skins** and
minimum upright gaps **0.4 mm (L20) / 0.2 mm (L18)** at the sampled positions
through all 152 upright layers on all four faces. Both ties span their reduced
core gaps; label strokes/counters/backing and the horizontal roofs are retained.
These are actual slicer paths, not printed gap measurements.

All three exported layouts also pass the native slice layout check. Their auto
support probe still requests review inside the enclosed horizontal post/roof
core: Z 1.0/1.2 mm for full pairs, Z 1.0 mm for the cup-only plate. Headless review
finds no suggested interface on upright ties or IDs. Retain supports **off**, as
in the physically approved T08 horizontal construction; added internal support
would occupy the test gap and be enclosed. Actual bridge extrusion heights stay
at 0.2 mm. No claim that the probe generated no support is made.
The cup-only layout has its own [native receipt](cups_final.json),
[gap/tie/label/support review](cups_paths.json) and [G-code](cups_paths.gcode.gz).
It reuses the same cup builders; only the second cup's placement differs from
its standalone paired layout. Both full-pair geometry/publication check groups
pass; the earlier physical report accepted damping and relative finish; the 2026-10-23 clarification leaves interior-floor robustness unresolved, while printed gap separation remains unknown.

Reproduce each native review with the selected named source and the complete
profile triplet above, using `--slice --slice-placement preserve --slice-keep-run`
and `--report model/tpu_damping_box/notes/thin_gap/L20_final.json` (or L18).
Then run `./execute.py model/tpu_damping_box/review_thin_gap.py` and
`./execute.py model/tpu_damping_box/verification.py --variant L20` (or L18).
The two-cup source uses the same supplied profile triplet and native review,
with `cups_final.json` as its receipt. Run
`./execute.py model/tpu_damping_box/review_thin_gap_cups.py` for its local checks.
Read the JSON outcomes; retained digital receipts predate the physical report and do not measure printed gap separation or durability. Saved path rendering requires retained raw review directories;
the G-code archives remain inspectable after raw cleanup.

| Item | Print status | Artifact(s) | Remaining physical checks |
| --- | --- | --- | --- |
| T08 M1 control | Yes — approved control | Existing pair retained unchanged | Exact settings, durability and application transfer remain unqualified. |
| T16 M1 | Yes — rejected | Historical pair retained | Too firm/noisier; do not recommend as the improved baseline. |
| L20 liner (matching pad print unknown) | Yes — walls/damping preferred; floor limited by 2026-10-23 clarification | `thin_gap_L20.py` / `.step` / `.stl`; cup also in `thin_gap_cups.step` | Damping like T08/L18, print quality almost like T08, slightly fewer bottom defects with ironing on; thinner than T08. Gap separation and durability unmeasured. |
| L18 liner (matching pad print unknown) | Yes — accepted, 2026-10-21 | `thin_gap_L18.py` / `.step` / `.stl`; cup also in `thin_gap_cups.step` | Damping similarly good; L20 preferred for print quality. Gap separation and durability unmeasured. |
| Application liner | N/A | None new | No dental/sunglasses adaptation is delivered or qualified. |

Attribution, 2026-10-21: GPT-6 family; exact runtime identifier/reasoning effort
not exposed. Codex shared-workspace CLI/API agent, OpenAI; no subagents. User
supplies the T08/T16 physical comparison and authorizes thinner follow-up pairs.
Agent authors gap variants, label extensions, checks and local path review;
shared T08/B sources and supplied profiles retain earlier attribution. No new
physical material calibration or acoustic measurement is claimed.
