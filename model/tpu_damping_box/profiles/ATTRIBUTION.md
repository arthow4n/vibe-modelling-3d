# Diagnostic Orca profile attribution

These two JSON snapshots derive from OrcaSlicer 2.4.2's bundled Qidi profiles,
licensed under [AGPL-3.0](LICENSE.txt), preserved here. Upstream:
[OrcaSlicer](https://github.com/OrcaSlicer/OrcaSlicer). The independently authored
CAD, drawings and experiment notes retain the repository's default MIT licence.

`tpu95a.json` resolves the installed Qidi filament chain:
`filament/Q2/fdm_filament_q_common.json`, `Generic TPU 95A @Q2C.json`,
`Generic TPU 95A @Qidi Q2C 0.4 nozzle.json`. Only inheritance flattening and
name/user-instantiation metadata changed. This is Generic TPU 95A, not HF/Aero.

`tpu-solid-process.json` derives from the repository's resolved Q2C 0.20 mm
process snapshot. Changes: 100% rectilinear fill, nominal wall/solid/infill speeds
25 mm/s, first layer and bridge speeds 15 mm/s, nominal acceleration 1000 mm/s²,
and no brim. Two wall loops and 0.20 mm layers remain. Thin regions may use the
slicer's ordinary thin-section/solid paths; these settings do not calibrate them.

Native reports and the object's README own actual effective settings and limits.
These are diagnostic path-generation profiles, not a tuned spool/printer recipe.

After a concrete toolpath failure (E and F pads bridged along the channels),
external/internal bridge angles are explicitly 180° (the X direction), relative
bridge angle is off, and align-directions-to-model is on. Internal bridge speed
is also capped at 15 mm/s. See the upstream
[bridge direction documentation](https://github.com/OrcaSlicer/OrcaSlicer/wiki/strength_settings_advanced#bridge-infill-direction).
Do not rotate individual components relative to the delivered layout when using
this common process; a changed layout needs a fresh bridge-direction review.

`tpu-selected-process.json` is a derivative of `tpu-solid-process.json` for the
focused A/E/H/I plate. It changes the diagnostic name and uses Arachne instead
of the classic wall generator to preserve 0.6 mm web geometry. Angles, supports,
material-solid fill, layer height and nominal speed limits remain the same.
Its licence is also AGPL-3.0. The selected native receipt/path review owns its
actual settings and evidence; the older batch receipt is not reused for this
new process or new plate.
