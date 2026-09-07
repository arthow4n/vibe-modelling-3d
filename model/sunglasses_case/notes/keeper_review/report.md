# D/E printability review

PrusaSlicer 2.9.6, existing diagnostic PETG profile
`../closure_review/review.ini`, 0.4 mm nozzle, 0.2 mm layers, 5 perimeters,
8 top/bottom layers, 5 mm brim, supports disabled. This profile is for comparison,
not a printer-specific G-code delivery. Use a calibrated profile for printing.

From this directory, substitute each complete file stem:

```sh
prusa-slicer --load ../closure_review/review.ini --center 130,130 --export-gcode --output D_firm_side_printed_keeper.gcode ../../D_firm_side_printed_keeper.stl
python3 summarize.py
```

| Trial | Filament incl. brim | Estimated time | Layers |
| --- | ---: | --- | ---: |
| D | 32.62 g | 3h 46m 44s | 195 |
| E | 32.80 g | 3h 48m 43s | 195 |

Compared with the same profile on A/B/C (63.22–63.63 g), these use approximately
48% less filament. All deposited paths including their half-width and brims fit
the 260 × 260 × 250 mm safe volume. Z reaches 39 mm. `summary.json` records
actual bounds, profile/STL/G-code hashes and estimates. Neither slice emitted
warnings or support-material paths.

## What the layers show

- `keeper_layers.png`: the complete separate keeper profile exists on the bed.
  Subsequent layers follow the preceding profile; the slightly tapered male key
  shrinks upward. Its retaining shoulder is a vertical printed perimeter. Local
  paths contain Perimeter/External perimeter roles, with no Overhang perimeter
  or Bridge infill. The former hanging tooth underside has been eliminated by
  this part's separate orientation, not by relying on slicer support generation.
- `receiver_layers.png`: the diamond keyway and upward-sloping exit slit close
  gradually on the preceding layers. The front receiver does not recreate the
  unsupported flat locking tooth. These paths still require normal calibration;
  they do not establish a successful 0.04 mm wedge fit.
- `loop_layers.png`: the 12 mm loop bridge remains between two leaf anchors,
  as in the physically tested baseline. It is tagged Overhang perimeter. The
  hinge geometry, gaps and print orientation are unchanged from A/B/C.

The larger fixture still contains bridge/overhang-role paths. The separate
keeper's local result is not a claim that the entire fixture contains none.
No warning is a certification, particularly given the user's A/B/C droop report.

## CAD/export evidence

`verify_keeper_exports.py` was evaluated through CadQuery MCP. All three STEP
solids are valid; each matching STL has three closed, nondegenerate mesh
components. Individual component bounds match within 0.035 mm and all touch
the bed. `export_checks.json` records final file hashes and bounds.

For the tapered key, a loose cached/meshed B-spline bound in the source evaluation
extended to Z=-0.071 mm. The STEP reimport and optimal geometric bounds, plus
actual STL vertices, establish bed contact at Z=0. The check uses
`BRepBndLib.AddOptimal_s(shape, box, False, False)` rather than interpreting a
conservative approximate bounding box as a physical extrusion below the bed.

Rigid checks establish collision-free shell/hinge movement, obstruction when
opening with the loop seated, clearance after outward release, and capture of
the key against vertical/outward motion. The key has slight intentional wedge
interference for sideways retention. Physical testing must establish that fit,
release force, frame compliance, wear and fatigue. The production case remains
outside this revision's scope.
