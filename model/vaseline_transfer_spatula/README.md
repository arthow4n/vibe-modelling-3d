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

The 44 mm crosswise stop rests on the jar's outer neck and prevents the tool
from dropping into the opening. To use it, scrape a portion from the large
container with the rounded nose, place the blade through the small jar mouth,
and press/draw the blade against the inner wall to release the material. Repeat
as needed and leave headspace below the thread.

The source of truth is `vaseline_transfer_spatula.py`. It produces one solid in
print orientation. `verify_and_export.py` independently checks the delivered
STEP/STL pair.

## Print plan

Print flat with the blade underside and handle underside on the bed. The blade
is 2.4 mm thick and tapers to a 1.2 mm rounded scraping nose over its final
8 mm; the handle is 7 mm thick. No supports or assembly are intended. The
overall footprint is approximately 44 × 143 mm and the height is 7 mm, within
the confirmed 260 × 260 × 250 mm printer envelope.

PETG is the assumed material with a 0.4 mm nozzle. Use several perimeters and
moderate infill for a durable handle. This is not claimed sterile or medical
equipment: FDM layer lines can retain residue. For wound-care use, prefer a
clean stainless-steel or silicone tool.

## Verification and limitations

CAD checks establish one valid solid, bed contact, overall bounds, and the
nominal blade/mouth clearance. They do not establish actual scraping force,
release feel, residue cleanup, material compatibility, or fit on the unknown
large source container. The first physical use should check that the nose does
not scratch the source container and that the flat blade releases cleanly into
the small jar.

CadQuery 2.8.0 evaluation found one valid solid with a 44 × 143 × 7 mm
bounding box. The exported pair passed the independent STEP/STL checker;
details and hashes are in `notes/export_checks.json`. A PrusaSlicer 2.9.6
reference smoke slice using `notes/review.ini` produced fresh nonempty paths,
no notices, no support segments, and an in-bed deposited footprint of about
56.75 × 155.75 mm. The diagnostic estimate was 11.32 g and 56m 27s; this is
reference-profile evidence, not a prediction of the user's actual print.

## Physical print status

| Item | Print status | Artifact(s) | User result or remaining physical checks |
| --- | --- | --- | --- |
| Test piece(s) | N/A | None | The complete tool is the first proposed print; edge flexibility and release remain untested. |
| Final printable object(s) | Unknown | `vaseline_transfer_spatula.stl`, `vaseline_transfer_spatula.step` | No user print report yet. Check source-container access, blade release, and cleanup in the first use. |

## Attribution

Primary language model: **GPT-5**. Reasoning effort: **unknown/not exposed**.
Harness: **Codex**. Provider: **OpenAI**. Material contributors: none known.
