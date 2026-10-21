# Diagnostic Orca profile attribution

These JSON snapshots derive from OrcaSlicer 2.4.2's bundled Qidi profiles,
licensed under [AGPL-3.0](LICENSE.txt), preserved here. Upstream:
[OrcaSlicer](https://github.com/OrcaSlicer/OrcaSlicer). The independently authored
CAD, drawings and experiment notes retain the repository's default MIT licence.

`tpu95a.json` resolves the installed Qidi filament chain:
`filament/Q2/fdm_filament_q_common.json`, `Generic TPU 95A @Q2C.json`,
`Generic TPU 95A @Qidi Q2C 0.4 nozzle.json`. Initially only inheritance flattening
and name/user-instantiation metadata changed. On 2026-10-16 the user requested
changing `filament_max_volumetric_speed` from 4 to **9 mm³/s**; all other filament
fields remain unchanged. This is Generic TPU 95A, not HF/Aero. The requested flow
limit is not a measured spool calibration.

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

`tpu-closed-process.json` derives from `tpu-selected-process.json` for S16/S12.
Initial changes: 0.10 mm layer/initial-layer heights, nominal 0.4 mm wall/material widths,
four bottom/top shell layers, 0.4 mm top-shell thickness, and thick external and
internal bridges explicitly off. Existing Arachne, bridge direction, speed limits,
supports-off and material-fill settings remain. It retains AGPL-3.0. This profile
qualifies only the documented diagnostic paths, not a particular TPU spool or
printed gap/strength/noise performance.

Layer-height correction, 2026-10-16: the user confirms all actual liner prints
used 0.2 mm layers. The current `tpu-closed-process.json` now uses 0.20 mm layer
and initial-layer heights, with a matching name/ID. Other settings are retained;
this is still a diagnostic reference, not the user's recovered full profile.
`tpu-closed-0p1-historical-process.json` preserves the exact earlier preset for
historical 0.1 mm receipts/readers. It is not the future printing recommendation.

`tpu-surface-process.json` derives from the current `tpu-closed-process.json`
for the eight 30 mm surface coupons (2026-10-17). Changes: identifying name/ID,
`ironing_type=top` and `ironing_flow=50%`; retained ironing speed 30 mm/s and
spacing 0.15 mm are diagnostic values, not recovered user settings. The profile
retains AGPL-3.0; its native slice receipt owns effective-setting evidence.

Historical `rejected_r1/tpu-support-a-process.json` and
`rejected_r1/tpu-support-b-process.json` derive from
`tpu-surface-process.json` for the four complete support-test pairs (2026-10-20).
Both require Classic, enable thin-wall detection, use 0.2 mm layers, two
bottom/top skin layers, no absolute top-shell thickness, no seam gap, no
ironing and no prime tower. A uses 0.3 mm nominal wall/solid/infill widths with
0.4 mm first-layer width and two requested perimeter loops; gap-fill filtering
is disabled. B retains 0.4 mm
widths, uses one requested perimeter loop plus 100% solid material fill, disables
gap-fill filtering and uses automatic external/internal bridge directions for
ties across all four wall normals. A keeps X-directed bridges. These profiles
retain AGPL-3.0; historical R1 receipts and its support-path review own actual
setup-specific evidence, not physical strength or damping qualification.

`tpu-support-classic-process.json` is R2's common process, derived from the
rejected R1 B process. It requires Classic with thin-wall detection OFF, two
perimeter loops, ordinary 0.42 mm general/outer widths and 0.45 mm inner widths,
0.5 mm first-layer width and restored 2 mm gap-fill filtering. Internal solid
width is 0.45 mm and sparse material width 0.42 mm; 100% material fill is retained
without filling CAD voids. Layers remain 0.2 mm, supports/ironing remain off,
bridges stay thin with automatic directions, and the reference TPU filament
remains unchanged. This derivative retains AGPL-3.0. Native R2 receipts and
explicit wall-path checks qualify this setup only, not printed strength or damping.

The separate [N1 infill-study profiles](../notes/infill_study/README.md) also derive
from `tpu-support-classic-process.json` under this same AGPL-3.0 attribution.
Their declared changes are Gyroid 20/30% or Cross Hatch 20%, three wall loops,
Inner/Outer/Inner, infill-first off, six top/bottom layers and gyroid optimization
off. They are diagnostic settings for a straight-wall proxy, not replacements
for the approved B process or a calibrated TPU recipe.

The [B-derived tie/skin study profiles](../notes/tie_surface_study/README.md)
P2/P3/P3IOI retain this same AGPL-3.0 source attribution. They derive from
`tpu-support-classic-process.json`: name metadata, explicit infill-first off,
and the declared two/three wall-loop and Inner/Outer or Inner/Outer/Inner order
choices differ. They are diagnostic study settings; no approved B profile is
modified and no TPU recipe is calibrated.
