# Closure candidate slicing — 2026-09-07

PrusaSlicer 2.9.6, diagnostic PETG profile `review.ini`, 0.4 mm nozzle,
0.2 mm layers, supports disabled. Each STL was sliced individually in its
exported open pose, centered at (130,130). These generic settings are not a
validated printer job; use the user's calibrated profile for physical trials.

Reproduce from this directory, substituting each candidate stem:

```sh
prusa-slicer --load review.ini --center 130,130 --export-gcode --output A_twin_hinge_loop_1p8.gcode ../../A_twin_hinge_loop_1p8.stl
```

| Candidate | Layers | Filament including brim | Estimated time |
| --- | ---: | ---: | --- |
| A | 195 | 63.22 g | 5h 37m 20s |
| B | 195 | 63.28 g | 5h 37m 6s |
| C | 195 | 63.63 g | 5h 43m 45s |

All three completed without warnings or support-material paths. Saved
`*_paths.json` reports describe extrusion roles, not physical printability.
`export_checks.json` records STEP/STL hashes, two closed manifold mesh
components, valid STEP solids, matching bounds and bed contact.
`summarize.py` also verified actual deposited paths including brim against the
260 × 260 × 250 mm safe volume. `summary.json` records their hashes and bounds:
X 89.323–170.679 mm, Y within 70.202–189.398 mm, maximum Z 39 mm.

## Critical layer inspection

- `loop_layers.png` shows C at Z=35.8, 36.2 and 36.4 mm. The horizontal
  loop rail starts across the two existing side leaves: about 12 mm of
  geometric bridge. The slicer labels its approximately 11.6 mm centerline
  segments as **Overhang perimeter**, not Bridge infill.
- `catch_layers.png` shows C at Z=24.4, 24.6 and 24.8 mm. The keeper lip
  projects 2.7 mm beyond its lower buttress (A: 1.9 mm). This is a one-sided
  unsupported lip, not an anchored bridge. Bridge-infill segments of about
  6.2 mm in this region do not establish support at both ends. Sag could
  consume the 0.4 mm seated latch clearance. This remains a physical trial
  risk; begin with A's smaller lip.
- Joint clearances remain the previously printed 0.20 mm radial/axial
  values. Separation of the two joints is the new anti-tilt hypothesis;
  no slice predicts printed play, friction or release force.

No claim of guaranteed support-free print quality is made. The loop bridge
fits the user's allowance for short bridges, while the keeper lip is a
separate limitation to inspect. The full-size case was not redesigned.
