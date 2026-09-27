# Minimal single-postcard display

Print **[postcard_display.step](postcard_display.step)**, or the matching
[STL](postcard_display.stl). One piece, no assembly or hardware. Source:
[postcard_display.py](postcard_display.py). The two low stops face the viewer;
the long feet run behind the card. Lower the card onto both feet, centre it,
and lean it against the two rear ribs. Lift it out to change orientation.

## Design and use

Designed for stiff, flat 100 × 150 mm and A6 (105 × 148 mm) postcards in either
portrait or landscape, assuming 0.2–0.8 mm card thickness. A6 is offered by
[VistaPrint Sweden](https://www.vistaprint.se/reklammaterial/vykort); postcard
sizes are not universal. No side channels impose an exact card width.

The nominal footprint is 64 × 40 mm, height 56.6 mm. Two 8 mm-wide feet support
the bottom edge; there is no full-width front rail. Each front stop is 7 mm wide
and rises only 1.4 mm above the seating surface. The 3.2 mm-wide rear ribs extend
55 mm above the seat and support a nominal 12° backward lean. The loose 1.2 mm
bottom opening allows small settling changes in angle without squeezing the
card. Rear ribs and the low rear crossbar are concealed by a centred opaque
card from the front; transparent filament is optional, not needed for concealment.
Rounded foot corners, rounded rib corners and bevelled stop tops soften contact.

This is a gravity easel for an undisturbed, level bookshelf. It does not clamp
the card or flatten curled paper. Very thin paper, strongly curled cards,
large/heavy mounted cards and resistance to knocks are outside the checked use.
The top portion of the card remains unsupported; ordinary postcard stiffness
is assumed. Visibility of the holder from the side is intentional.

## Printing

- Qidi Q2C, PETG (transparent if desired), 0.4 mm nozzle, 0.2 mm layers.
- Two walls, 7% adaptive cubic infill; ordinary solid top/bottom layers.
- Use the supplied orientation: flat feet and crossbar on the bed, ribs upright.
- Supports off. Brim only if needed for your bed adhesion; remove it before use.
- Use your filament's calibrated PETG temperature/flow settings. No clarity claim
  is made for transparent PETG; layer lines and internal paths remain visible.
- Smooth any stringing or burrs at the card contacts before inserting a card.

The small complete holder is the first trial; no separate coupon saves useful
material. Check that both stops retain your card, it sits without rocking,
and its upper corners stay acceptably flat. Printed fit and handling have not
been physically tested. The 0.8 mm nozzle is not the reviewed setup.

## Decisions and verification

A tiny slotted block was rejected because it would concentrate support at the
bottom edge. The two triangular ribs spread backing contact up the card without
a visible frame or a full backing plate. The rear crossbar connects the feet
on the bed, avoiding an elevated bridge.

Concept screen: a 150 mm-high card at 12° places its centre of mass about
17 mm behind the seating origin, inside the feet's −2 to 38 mm fore/aft span.
The centred card's lateral centre of mass is between the two feet. This supports
static gravity stability, not resistance to impacts or drafts. For an assumed
10 g card, backing reaction at 55 mm is only about 0.03 N; no spring or
structurally demanding joint is needed. The 64 × 40 × 56.6 mm plan leaves ample
space for print aids within the 270 × 270 × 256 mm printer envelope.

Final CAD evaluated successfully with CadQuery 2.7.0 / Python 3.12.14.
[display_preview.py](display_preview.py) is an **inspection-only scene**, not a
print file. Its targeted collision assertions passed for 100 × 150 mm and A6,
both orientations, at 0.2 and 0.8 mm thickness. This checks that seated cards
clear the stand; it does not model card flexibility or friction. Inspected the
[front scene](renders/assembled/display_preview_front.png) for concealment,
and [side](renders/print/postcard_display_right.png) and
[isometric](renders/print/postcard_display_isometric.png) views for the backing,
contact stops and base connections. Render image orientation follows the shared
renderer; the STEP/STL print orientation is feet down, Z up.

FDM review: flat connected bed contact, 1.6 mm base, 1.2 mm stop thickness and
3.2 mm gussets suit multiple extrusion paths with the selected nozzle. The
backing face grows rearward only about 0.043 mm per 0.2 mm layer; the opposite
edge retreats as it rises. There are no elevated crossbars, trapped cavities
or unsupported starts. Gussets carry the small card reaction into the feet.

Final matching STEP and STL exports succeeded. OrcaSlicer **2.4.2** completed
one centred plate with no notices, no review conditions, and **no support
generated** by its automatic-support probe (30° threshold, 10 mm maximum bridge
length). Profiles: repository `.codex/skills/orca-slicer-printability/profiles/`
`qidi-q2c-petg/` printer `qidi-q2c-0.4-nozzle.json`, process
`qidi-q2c-0.20-standard-adaptive-cubic-7.json`, filament
`generic-petg-qidi-q2c-0.4.json`. Effective settings matched the intended nozzle,
material, layer height, walls and infill; support disabled, auto brim 5 mm.
Diagnostic temperatures were 245°C first layer / 250°C thereafter, bed 80°C;
these are not a calibration for the user's transparent PETG. This STL smoke
slice establishes profile-specific path acceptance, not physical print quality
or Orca GUI STEP-import verification.

Reproduce exports/review from repository root:

```sh
./evaluate_model.py model/postcard_display/postcard_display.py --views isometric,right --output-dir renders/print --slice
./evaluate_model.py model/postcard_display/display_preview.py --views front --output-dir renders/assembled
```

## Print status

| Item | Print status | Artifact(s) | User result or remaining physical checks |
| --- | --- | --- | --- |
| Test piece(s) | N/A | None | Full holder is the trial |
| Final printable object(s) | Unknown | `postcard_display.step`, `postcard_display.stl` | No user print report; check card seating, stability, curl and contact finish |

## Attribution

Primary model: **GPT-6 Astra, reasoning effort low**, as explicitly supplied by
the user on 2026-09-28. Harness: Codex agent environment. Provider: OpenAI.
No sub-agents or third-party model geometry used. Repository MIT licence applies.
