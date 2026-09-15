# Rounded square tray

Parametric shallow tray based on the [user-supplied photograph](references/Photo-1.jpg).
The user accepted a **220 mm wall-to-wall cavity and 200 mm completely flat floor**,
preserving the approximately 240 mm exterior and generous interior fillets.

## Files and dimensions

- [Editable parameters and main entry point](rounded_square_tray.py), with
  [construction functions](tray_geometry.py). Keep these two Python files together.
- [STEP](rounded_square_tray.step) and [STL](rounded_square_tray.stl): the same
  single solid, millimetres, centred in XY with underside at Z=0 and opening upward.
- [Isometric view](renders/print/rounded_square_tray_isometric.png) shows the cavity
  and continuous rim; [front view](renders/print/rounded_square_tray_front.png)
  shows the exterior taper and bottom round.

| Feature | Dimension |
| --- | --- |
| Vertical-wall cavity / plan corner radius | 220 × 220 mm / R30 |
| Flat floor bounding size / plan corner radius | 200 × 200 mm / R20 |
| Interior depth / base / overall height | 31 / 6 / 37 mm |
| Nominal upper exterior / radius, before rounding | 238 × 238 mm / R39 |
| Nominal lower exterior / radius, before rounding | 224 × 224 mm / R32 |
| Exterior inset per side / slope from vertical | 7 mm / approximately 10.71° |
| Interior wall draft | 0° |
| Nominal upper wall thickness | 9 mm |
| Interior floor / inner rim / outer rim / bottom fillets | R10 / R2.5 / R2.5 / R8 |
| Measured flat rim width along a straight side | 3.483 mm |
| Finished overall bounds after edge rounding | 236.965 × 236.965 × 37 mm |
| Flat underside bounding size | 210.743 × 210.743 mm |

The flat floor has rounded corners: its bounding dimensions do not imply that a
sharp-cornered 200 mm square fits. Top inner rounding enlarges the mouth locally
to 225 mm, while the vertical cavity remains 220 mm. The 9 mm rim dimension is
the wall before edge rounding; both rounds consume some of the flat border.
The exterior radii are derived from the inner radius and wall thickness, keeping
concentric corner transitions. The loft has planar sides and smooth conical
corner regions; the photograph's tessellation facets are not embossed into CAD.

Adjust the named parameters in `rounded_square_tray.py`, then evaluate that file
with CadQuery MCP and export both formats from the same result. `build_tray()`
supports smaller/larger dimensions subject to its assertions and successful CAD
fillets. A smaller 180 mm cavity configuration was also evaluated successfully;
arbitrary combinations are not guaranteed. Recheck geometry, exports and print
envelope after edits.

## Printing and use

Print **flat underside on the bed, cavity upward**, as exported. Assume a 0.4 mm
nozzle. The retained [reference profile](notes/review.ini) uses PETG, 0.2 mm layers,
four perimeters, five top/bottom layers and 20% gyroid infill. It enables automatic
build-plate-only supports at a 45° threshold for the lower exterior R8 blend.
Those exposed supports can be removed from the perimeter; support contact can
leave marks on the underside transition. The upper taper and open interior need
no inaccessible support. A broad, continuous underside provides stable contact;
the measured straight wall is 5.784 mm thick at Z=20 mm and the base is 6 mm.

The reference slice uses no skirt or brim and fits the **250 × 250 × 250 mm**
practical envelope, including generated supports. If adding print aids, recheck
the deposited footprint in your slicer. Whole-layout centring places the reference
deposition between 6.518 and 243.482 mm in X and Y, reaching Z=37 mm.
Estimated consumption is **328.71 g**, with **25 h 47 min** estimated print time.
These estimates belong to the reference profile, not an actual supplied printer
configuration. Slice the STL for your printer; the diagnostic G-code is not a
delivered printer job.

Intended as a general-purpose tray without a rated payload. The thick floor feeds
loads into the continuous wall and broad base, with fillets avoiding abrupt
internal corners. Full-size warping, bottom-round surface quality, support removal
and handling stiffness remain physical checks. No separate coupon is proposed:
it would not establish full-size flatness. Food-contact suitability, liquid
tightness and heat/dishwasher resistance have not been established.

## Verification

- CadQuery MCP: one valid solid; floor at Z=6, rim at Z=37, flat floor 200 × 200,
  vertical cavity 220 × 220 at Z=20, and a continuous flat rim. See
  [measurement checks](notes/geometry_checks.json) and [their entry point](verify_geometry.py).
- [Final CAD evaluation](notes/cad_evaluation.json) records source/module hashes,
  versions, bounds, topology, successful views and matching-build exports.
  CadQuery 2.8.0, OCP 7.9.3.1.1, server 0.2.0, Python 3.12.14.
- [Independent export checks](notes/export_checks.json), run through
  [CadQuery MCP checker entry point](check_exports.py), passed: valid STEP solid,
  closed consistently wound STL component, bed placement and matching bounds and
  volumes. STL has 35,204 triangles; export tolerance 0.015 mm / 0.1 rad.
- PrusaSlicer 2.9.6 produced fresh nonempty toolpaths, with supports, within the
  practical envelope. No notices or repairs were reported in the inspected log.
  [Summary and hashes](notes/slice_review/summary.json),
  [command](notes/slice_review/command.json), and
  [path measurements](notes/slice_review/paths.json) preserve reference evidence.
  This is export-to-toolpath acceptance, not a physical print test.

### Design checklist

- [x] Scope, photograph, user changes, CAD-tool availability and dimension agreement.
- [x] Named dimensions, upright print orientation, envelope and support strategy.
- [x] Valid solid, critical surfaces, edge treatment, accessible cavity and supports.
- [x] Smaller parameter configuration and final geometry checked through MCP.
- [x] Final STEP/STL pair checked; final reference smoke slice reviewed.
- [x] Useful views, assumptions, instructions, attribution and physical limits saved.

### Print status

| Item | Print status | Artifact(s) | User result or remaining physical checks |
| --- | --- | --- | --- |
| Test piece(s) | N/A | None; full tray is the proposed trial | Full-size flatness needs the complete object |
| Final printable object(s) | Unknown | `rounded_square_tray.stl`, `rounded_square_tray.step` | No user print report; check warping, support removal, surface quality and handling stiffness |

## Attribution

- Primary language model: **GPT-6 Astra**; reasoning effort **low**, both explicitly
  supplied by the user in this session.
- Harness/agent environment: Codex in the shared local repository; provider: OpenAI.
- User supplied the design requirements and photograph. Photograph creator and
  licence are unknown; it is retained as a user-supplied reference, with no claim
  that the repository's default code licence grants rights to that photograph.
- No additional language-model contributors.
