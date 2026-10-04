# Vaseline transfer spatula

A flat, single-piece scrape-and-fill tool for transferring Vaseline from a
larger container into the repository's 50 mm Vaseline jar.

## Design and use

The current jar has a **38 mm internal mouth**, a **19 mm internal radius**, and
an approximately **42 mm outer neck**. The spatula blade is 30 mm wide, leaving
4 mm radial clearance per side when inserted. It is deliberately flat rather
than spoon-shaped: the broad face carries a shallow portion, while the rounded
front edge scrapes and the blade side wipes material against the receiving
jar's inner wall.

There is no crosswise stop or collar: the handle remains narrow so the blade
can be poked freely into a larger source container. To use it, scrape a portion
from the large container with the rounded nose, place the blade through the
small jar mouth, and press/draw the blade against the inner wall to release the
material. Repeat as needed and leave headspace below the thread.

The source of truth is `vaseline_transfer_spatula.py`. It produces one solid in
print orientation. The delivered STEP and STL are matching exports of that model.

## Print plan

Print flat with the blade underside and handle underside on the bed. The blade
is 2.4 mm thick and tapers to a 1.2 mm rounded scraping nose over its final
8 mm; the handle is 7 mm thick and overlaps the blade by 2 mm. No supports or
assembly are intended. The overall footprint is approximately 30 × 141 mm and
the height is 7 mm, within
the Qidi Q2C's 270 × 270 × 256 mm printer envelope.

PETG is the assumed material with a 0.4 mm nozzle. Use several perimeters and
moderate infill for a durable handle. This is not claimed sterile or medical
equipment: FDM layer lines can retain residue. For wound-care use, prefer a
clean stainless-steel or silicone tool.

## Verification and limitations

CAD checks establish one valid solid, bed contact, overall bounds, and the
nominal blade/mouth clearance. They do not establish actual scraping force,
release feel, residue cleanup, material compatibility, or fit on the unknown
large source container. The user now reports that the printed tool works well
and does its job; specific observations about scratching, release and cleanup
were not reported separately.

CadQuery 2.8.0 evaluation found one valid solid with a 30 × 141 × 7 mm
bounding box. STEP and STL were exported from that evaluation. The current final
PrusaSlicer 2.9.6 reference smoke slice is recorded in
`notes/reference_smoke_run_02/summary.json`; it produced fresh nonempty paths,
no notices, no support segments, and an in-bed deposited footprint of about
42.74 × 153.75 mm including the diagnostic skirt. The diagnostic estimate was
10.70 g and 53m 9s; this is reference-profile evidence, not a prediction of
the user's actual print.

## Physical print status

| Item | Print status | Artifact(s) | User result or remaining physical checks |
| --- | --- | --- | --- |
| Test piece(s) | N/A | None | No separate specimen; the complete tool was the trial print. |
| Final printable object(s) | Yes | Existing `vaseline_transfer_spatula` model; exact file used for the print was not reported. Available exports: `vaseline_transfer_spatula.stl`, `vaseline_transfer_spatula.step` | User reports the existing print works well and does its job; the handle size feels right. The storage footprint motivates exploring a more compact revision. Release feel, cleanup, long-term wear and print settings were not reported separately. |

The user reported this physical print on **2026-10-04**. This is positive use
feedback for the existing design, not a rejection: no functional problem was
reported. Material, printer, slicer settings and the exact exported file used
remain unknown. The original model source and attribution below are unchanged.

## Attribution

Primary language model: **GPT-5.6 Luna**. Reasoning effort: **Extra High**.
Harness: **Codex**. Provider: **OpenAI**. Material contributors: none known.
