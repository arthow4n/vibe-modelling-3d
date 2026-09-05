# Diagnostic slicing test — no geometry changes

User requirement: no supports. This task only tests the available slicer and
checks the known overhead-wall problem; it does not revise the case.

PrusaSlicer CLI 2.9.6+flathub.org successfully sliced the existing case STL in
its supplied standing orientation. review.ini uses the confirmed 260 mm bed
and PETG, with an assumed 0.4 mm nozzle and 0.2 mm layers. It is a diagnostic
configuration, not a validated printer-specific profile or printable G-code.

The no-support slice explicitly reports:

> Detected print stability issues:
> Long bridging extrusions
> Consider enabling supports.

At print Z=171.2 mm, immediately where the upper interior end wall closes,
the generated Bridge infill includes straight extrusion moves of 87.186 mm.
These are actual toolpath lengths including anchoring; they are not a separate
measurement of the unsupported air gap. Example: without_supports.gcode line
475359 in this run. measurements.json records the endpoints and layer details.
This confirms the wall is being treated as a long bridge over the cavity,
not as an ordinary supported wall. Successful G-code generation did not mean
that this is a satisfactory support-free orientation.

An automatic-support slice was also run solely for comparison before the user's
no-support clarification. It is not the proposed solution. No redesign or further
print tuning was performed. No physical print or prediction of exact sag was made.

## Reproduce

Run from the repository root:

```sh
prusa-slicer --load model/sunglasses_case/notes/slicer_review/review.ini --center 130,130 --export-gcode --output model/sunglasses_case/notes/slicer_review/without_supports.gcode model/sunglasses_case/sunglasses_case.stl
prusa-slicer --load model/sunglasses_case/notes/slicer_review/review.ini --support-material --center 130,130 --export-gcode --output model/sunglasses_case/notes/slicer_review/with_supports.gcode model/sunglasses_case/sunglasses_case.stl
python3 model/sunglasses_case/notes/slicer_review/analyze.py
```

The second command only reproduces the diagnostic comparison. G-code files are
ignored because they are large, reproducible and not machine-ready. The analysis
script uses only the Python standard library and validates its required coordinate
modes; it summarizes slicer roles and segment lengths, not physical printability.
