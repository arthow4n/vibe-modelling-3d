# Final diagnostic printability review — 2026-09-06

PrusaSlicer 2.9.6+flathub.org. Confirmed 260 × 260 × 250 mm usable volume and
0.4 mm nozzle; PETG selected. `review.ini` contains generic diagnostic temperatures
and speeds, not the user's validated printer profile. No printer was operated.

All three final slices produced fresh nonempty ASCII G-code and **no stability
warnings**. Supports and skirts were disabled. All deposited paths, including brim
and half the reported extrusion width, fit inside the safe XY bed; all layers fit
below 250 mm. `summary.json` records file/profile hashes, bounds and estimates.

| Plate | Estimated PETG | Diagnostic time | Actual deposition XY bounds, mm |
| --- | ---: | --- | --- |
| Main case | 352.86 g | 29 h 49 min | X 3.122–256.876; Y 11.202–248.220 |
| Accessories | 15.45 g | 1 h 37 min | X 50.372–209.628; Y 96.422–163.578 |
| All test pieces | 38.07 g | 3 h 46 min | X 28.622–231.378; Y 99.162–157.960 |

Actual machine speeds, material and extrusion settings will change these estimates.
The test plate is about one tenth of the complete product's material. The individual
production handle clip is about 3.2 g of solid PETG before brim and can be checked
against the real handle before printing the larger socket/shoulder test.

## Findings and corrections

- **Hinge:** inspected Z 29.0, 32.4 and 35.6 mm against preceding layers in
  `hinge_layers.png`. Cones/socket roofs grow from prior material; gaps remain
  visible. No support paths occupy the captive joints. Coupon retains exact
  geometry, orientation and axis height. Geometric sweep and axial capture checks
  pass, but physical freedom/play still need the sample print.
- **Clips:** the original circular underside widened too abruptly just above its
  foot. The accessory plate reported `Loose extrusions`; the same clip on a mixed
  test plate did not. Tiny round contact bumps were replaced with sloping ribs,
  but that alone did not resolve the warning. A tapered pedestal under the lower
  arc removed it. `clip_layers.png` shows the corrected preceding/current paths at
  2.6, 3.2 and 3.6 mm. The upper arms remain free to flex. This illustrates why a
  clean coupon slice does not replace slicing the actual accessory plate.
- **Shoulder stop:** after raising the handle for finger access, unnecessarily tall
  notch sides triggered `Thin fragile part` on the case plate. Lowering those sides
  removed the warning while preserving the verified handle-shoulder stop action.
- **Bridge roles:** the main case has bridge-labeled segments up to 22.73 mm at
  Z 9.0, across internal gyroid in a socket plinth. `socket_layers.png` confirms
  preceding infill and perimeter anchors; these are not 22.73 mm empty spans.
  Test plate has similar plinth infill bridges up to 32.14 mm; accessories up to
  5.63 mm. No bridge length is asserted to be universally safe.
- **Vent slots:** the case has 18 overhang-role segments, each about 0.558 mm,
  associated with the small arched vents. No reported long-bridge warning.
- **Topology:** export verification found no repeated-vertex triangles or unpaired
  mesh edges, and the expected solid counts. STEP/STL bounding boxes agree within
  0.03 mm and every printable export has bed contact in its supplied placement.

## Reproduction

Run from the repository root after regenerating exports with CadQuery MCP:

```sh
prusa-slicer --load model/dental_travel_case/notes/slicer_review/review.ini \
  --center 130,130 --export-gcode \
  --output model/dental_travel_case/notes/slicer_review/run/dental_travel_case.gcode \
  model/dental_travel_case/dental_travel_case.stl \
  > model/dental_travel_case/notes/slicer_review/run/dental_travel_case.log 2>&1
```

Repeat with `accessories` and `test_pieces`. Preserve all model placements; do not
split, repair, rotate or arrange captive shells independently. Then run
`python3 model/dental_travel_case/notes/slicer_review/summarize.py`.
Diagnostic G-code and raw logs stay ignored under `run/`; they are not print jobs.

Layer inspection uses the repository's `inspect_gcode.py`. The recorded windows
are clip X 50–75 / Y 110–150 at 2.6/3.2/3.6 mm; hinge X 46–69 / Y 121–151 at
29.0/32.4/35.6 mm; socket X 211–238 / Y 14–54 at 8.8/9.0/10.4 mm.

The path bounds are a conservative bound on reported straight extrusion paths,
not predicted plastic spread, ooze, sag or a complete printer-motion envelope.
Slicer success does not establish actual brush fit, surface finish, latch force,
clip retention, PETG fatigue, crush resistance or hygiene performance.
