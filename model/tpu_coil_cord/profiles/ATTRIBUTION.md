# Profile attribution

`coil-solid-process.json` derives from
[`tpu-solid-process.json`](../../tpu_damping_box/profiles/tpu-solid-process.json),
itself a resolved OrcaSlicer 2.4.2 Qidi process snapshot. Upstream is
[OrcaSlicer](https://github.com/OrcaSlicer/OrcaSlicer), licensed under
[AGPL-3.0](../../tpu_damping_box/profiles/LICENSE.txt). See the
[original attribution](../../tpu_damping_box/profiles/ATTRIBUTION.md).

Changes: descriptive name, three wall loops, explicitly disabled supports,
brim and ironing; solid material fill retained. Existing 0.2 mm layers,
Classic generator, nominal 25 mm/s and bridge 15 mm/s are retained. These
are experimental slicing settings, not calibrated TPU behavior.


`r2-horizontal-process.json` derives from `coil-solid-process.json` for the new
horizontal winding. It changes only the descriptive name, `bridge_angle=0`,
`internal_bridge_angle=0` (automatic directions) and disables
`align_infill_direction_to_model`. Solid fill, Classic paths, three walls,
0.2 mm layers, speeds and supports-off remain. The inherited fixed X-directed
bridge setting was unsuitable as the assumed direction for R2's end-frame roof
openings; actual paths are reviewed in the R2 record. This derivative retains
the same AGPL-3.0 licence and upstream attribution above.
