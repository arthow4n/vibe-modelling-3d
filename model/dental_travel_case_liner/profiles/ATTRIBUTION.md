# Orca/Qidi diagnostic process derivative

`tpu-s16-0p2-process.json` derives from
the preserved [`tpu-closed-0p1-historical-process.json`](../../tpu_damping_box/profiles/tpu-closed-0p1-historical-process.json).
It changes the preset name/ID and both layer heights from 0.1 to 0.2 mm for the
tall dental S16 inserts. Thin bridges, two walls, Arachne and 100% rectilinear
material fill are retained. This is an uncalibrated diagnostic preset.

Original sources, upstream copyright and earlier modifications are recorded in
the [parent attribution](../../tpu_damping_box/profiles/ATTRIBUTION.md).
The derived preset retains **AGPL-3.0**, with [license text](LICENSE.txt).
This profile license does not change the model geometry's repository license.

`rotary-l20-process.json` derives from the shared
[`tpu-support-classic-process.json`](../../tpu_damping_box/profiles/tpu-support-classic-process.json).
It retains Classic, two walls, 0.2 mm layers, ordinary widths and 100% fill,
and enables top-surface ironing with the retained 50% / 30 mm/s / 0.15 mm
recipe. No other process settings change. It retains the same AGPL-3.0
license and parent attribution above.
