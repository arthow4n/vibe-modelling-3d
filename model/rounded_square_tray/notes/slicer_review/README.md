# Reference smoke-slice evidence

`run_02/summary.json` records the final exported STL smoke check. PrusaSlicer
2.9.6 accepted the fresh mesh with no notices, no support paths, and deposited
paths inside the 250 × 250 × 250 mm practical envelope. The deposited XY bounds
including half extrusion width are 5.473–244.527 mm in both axes and maximum Z
is 37.0 mm.

The self-contained diagnostic profile assumes PETG, a 0.4 mm nozzle, 0.2 mm
layers, four perimeters, 20% gyroid infill, no brim, and no supports. It estimates
336.81 g and 1 day 2 h 16 min 23 s. These are reference-profile estimates, not
validated printer settings or guarantees of adhesion, warping, strength, surface
finish, food safety, or actual print time.

Input hashes and the exact slicer invocation are retained in `run_02/summary.json`
and `run_02/command.json`. Raw G-code and slicer logs are intentionally ignored.
