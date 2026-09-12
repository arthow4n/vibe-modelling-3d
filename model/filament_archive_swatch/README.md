# Compact filament archive swatch

Flat **80 × 50 × 2 mm** filament sample card for labeling and comparing stored
filaments. The card combines a thumb notch, a shallow concave finger recess,
engraved brand/material/color fields, five translucency/opacity thickness steps,
and integrated chamfer/fillet test features.

This object intentionally remains an OpenSCAD source-only model. The
`filament_archive_swatch.scad` file is the authoritative source and is meant to
be edited, rendered and exported to STL in the user's SCAD live editor. No
replacement script, CadQuery source, STEP export or repository-generated STL is
included.

## Use and parameters

Open `filament_archive_swatch.scad` in an OpenSCAD-compatible live editor and
edit the three text values near the top:

- `brand_text`: maker or brand name.
- `material_text`: filament family or material, such as PLA or PETG.
- `color_text`: color name or identifier.

The remaining principal dimensions are millimetres:

| Parameter | Default | Purpose |
| --- | ---: | --- |
| `card_width` | 80 | Overall X size |
| `card_height` | 50 | Overall Y size |
| `base_thickness` | 2.0 | Main card thickness |
| `right_corner_radius` | 3 | Rounded right-side corners |
| `left_chamfer_size` | 4 | Chamfered left-side corners |
| `top_edge_chamfer` | 2.0 | Upper edge Z-layer chamfer test |
| `bottom_edge_fillet` | 2.0 | Lower edge Z-layer fillet test |
| `layer_height` | 0.2 | Intended layer-height note; the slicer controls the actual setting |

The opacity steps leave floors of **0.2, 0.4, 0.6, 0.8 and 1.0 mm**, each
nominally 10 × 8 mm. The 0.2 mm step is only one layer at the intended layer
height, so handle that area accordingly. `$fn = 60` controls the resolution of
the curved OpenSCAD geometry. The color label automatically uses a smaller text
size when its value is longer than 12 characters. The engraved text is intended
to be 0.6 mm below the card's top surface.

## Printing

Render and export the default orientation without rotating the card: its broad
face lies on the bed. The source is designed around a **0.4 mm nozzle** and
**0.2 mm layer height**. A normal flat-plate profile should not need supports;
use the actual material and first-layer settings for the target printer. The
default 80 × 50 mm footprint and 2 mm height fit within the repository's
confirmed 260 × 260 × 250 mm printer limits.

After exporting the STL from the live editor, read the opacity steps from their
remaining floor thickness and use the engraved fields for the sample's identity.
The card's asymmetric edges and right-side notch provide orientation when
handling a collection of swatches.

## Verification and scope

The user reports that this exact SCAD-generated object has been printed before
and works as intended. That physical result is the primary validation recorded
here. No new CadQuery evaluation, export check or repository reference slice was
run for this documentation-only entry, and no claim is made about a committed
STEP/STL pair.

## Physical print status

Status reviewed 2026-09-12. The user's print date, material, printer and slicer
profile were not recorded.

| Item | Print status | Artifact(s) | User result or remaining physical checks |
| --- | --- | --- | --- |
| Test piece(s) | N/A | None; the complete swatch is the intended object | No separate coupon was used or needed. |
| Final printable object(s) | Yes | `filament_archive_swatch.scad` rendered/exported by the user's live editor | User reports a previous print works as intended. Print details were not recorded. |

## Attribution

Primary language model: **Gemini 3.1 Pro**, as reported by the user. Harness or
agent environment: **Gemini chat**, as reported by the user. Reasoning effort:
**not exposed**. Provider: **user-provided / not separately recorded**. The
repository entry preserves the supplied SCAD source without modifying it.
