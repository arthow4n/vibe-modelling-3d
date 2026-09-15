# Rounded square tray

A single-piece, parametric shallow tray based on the supplied visual reference.
Edit the named dimensions near the top of `rounded_square_tray.py`; dependent
height and base thickness are derived in the same file.

## Geometry and assumptions

- The requested 220 × 220 mm inner usable size is the wall-to-wall cavity size.
  The R10 floor transition leaves an approximately 200 × 200 mm central flat
  tangent span; that is the unavoidable geometric consequence of adding the
  requested fillet inside the stated cavity envelope.
- The upper outer profile is 240 × 240 mm (R38), the bottom profile is
  226 × 226 mm (R31), and the loft height is 37 mm.
- The cavity floor is at Z=6 mm and the rim at Z=37 mm, giving 31 mm depth.
- The nominal top border is 10 mm on straight sides before restrained 2.5 mm
  beveled edge breaks. This follows from the specified outer and inner sizes;
  the requested “approximately 9 mm” rim is treated as a visual target.
- Intended use is a general serving/organizing tray. Food contact, dishwasher
  use, heat resistance, watertightness, and load capacity depend on material,
  slicer settings, and physical testing and are not established here.

## Printing

Print upright, with the broad flat underside on the bed. The 240 × 240 mm
footprint and 37 mm height fit the repository's 250 × 250 × 250 mm practical
envelope, leaving 5 mm clearance per XY side when centered. No supports are
intended: the outer taper grows outward gradually and the open cavity has no
roof or bridges. A brim may exceed the practical XY envelope, so use none unless
your actual build plate has enough additional room. For a 0.4 mm nozzle, use a
normal multi-perimeter profile; the 6 mm base and roughly 10 mm top wall are
substantial. Large flat parts can warp, so clean-bed adhesion and a material-
appropriate enclosure/bed temperature matter.

## Deliverables

- `rounded_square_tray.py` — authoritative parametric CadQuery source
- `rounded_square_tray.step` — editable solid export in print placement
- `rounded_square_tray.stl` — print mesh in matching placement
- `references/reference_photo.jpg` — supplied visual proportion reference
- `renders/print/rounded_square_tray_isometric.png` and
  `renders/print/rounded_square_tray_top.png` — inspection views
- `notes/export_checks.json` and `notes/slicer_review/` — verification evidence

## Verification and provenance

CAD evaluation checks validity, topology, dimensions, and the final views. The
STEP/STL pair is independently checked from the exported files. The reference
slice is only evidence for its recorded PrusaSlicer profile, not a prediction of
every printer or material.

- Primary language model: GPT-5.6 Sol
- Reasoning effort: Low
- Harness/agent environment: Codex
- Provider: OpenAI

## Physical print status

| Item | Print status | Artifact(s) | User result or remaining physical checks |
| --- | --- | --- | --- |
| Test piece(s) | N/A | None | No separate coupon is useful for this one-piece geometry. |
| Final printable object(s) | Unknown | `rounded_square_tray.step`, `rounded_square_tray.stl` | Confirm warping, surface finish, stability, and suitability for the intended contents on the user's printer/material. |

Print report date, source revision, material, orientation, and printer/profile:
unknown unless recorded above.
