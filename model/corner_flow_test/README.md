# CornerFlowTest

`CornerFlowTest` is a solid vase-mode calibration object for Orca Slicer. Its
constant perimeter combines sustained straight runs, sharp convex and reflex
corners, an R10 quarter-turn, R5 and R2 hairpins, and a 45-degree direction
change. Orca Slicer owns every printing and flow-calibration setting; the model
contains geometry only.

## Files and parameters

- `CornerFlowTest.py` is the authoritative parametric CadQuery source.
- `CornerFlowTest.step` is the authoritative analytic CAD export in millimetres.
- `CornerFlowTest.stl` is the matching print-ready mesh.
- `CornerFlowTest.py` asserts its bounds, analytic edge types, radii and topology
  during every build.
- `renders/print/` contains useful views of the final print orientation.
- `notes/` contains export and reference-slice evidence.

The editable parameters are `model_height = 50`, `r_small = 2`,
`r_medium = 5`, and `r_large = 10`, all in millimetres. Arc-dependent endpoints
are derived from the radii. Deliberately conservative parameter bounds reject
values that could reorder or intersect perimeter features.

## Printing

Import `CornerFlowTest.stl` into Orca Slicer without rotating it and use Orca's
maximum-volumetric-speed calibration in vase mode. Configure extrusion width,
layer height, wall behavior, infill, top/bottom layers, speed, acceleration and
the flow ramp in Orca Slicer. No such values are encoded in the geometry.

The planar 100 × 70 mm bottom face lies at Z=0. The object is a vertical prism,
so it has stable bed contact, no bridges, overhangs, holes, cavities or supports.
Its 100 × 70 × 50 mm bounds fit the repository's confirmed 260 × 260 × 250 mm
printer volume. All intentionally sharp test corners remain untreated.

## Verification

The CadQuery source was evaluated as one valid solid made from one closed outer
wire extruded vertically. The default profile has 15 straight analytic edges and
three analytic circular edges, one face at every horizontal cut, and the exact
100 × 70 × 50 mm bounds. STEP and STL were exported from the same evaluation.
The retained export report checks the STEP solid and the binary STL for finite,
non-zero-area facets, closed manifold connectivity, consistent winding, positive
volume, matching bounds/volume and bed contact. The reference PrusaSlicer smoke
slice (2.9.6) generated fresh, nonempty paths with no supports or notices, a
112.758 × 82.758 mm deposited footprint after slicer centering, and 50 mm maximum
Z. Its planar one-wall profile is independent mesh-acceptance evidence only:
the repository parser cannot analyze vase mode's intentionally non-planar spiral
extrusion. Use the actual Orca profile for vase-mode calibration.

## Physical print status

Status reviewed 2026-09-12. No separate coupon is useful because the complete
object is itself the calibration trial.

| Item | Print status | Artifact(s) | User result or remaining physical checks |
| --- | --- | --- | --- |
| Test piece(s) | N/A | N/A | The full object is intentionally the test. |
| Final printable object(s) | Unknown | `CornerFlowTest.stl` | No user print report; actual high-flow corner behavior remains to be observed with the target printer, filament and Orca profile. |

## Attribution

Primary model: **GPT-5**, reasoning effort **not exposed**; harness **Codex**;
provider **OpenAI**. No other material model contributors are recorded.
