# OrcaSlicer CLI and path interpretation

Use the [OrcaSlicer skill](../SKILL.md#run-the-review) for the current command,
profile arguments and report. The findings below were checked with Flatpak
OrcaSlicer 2.4.2 on 2026-09-27; recheck them when the slicer or profiles change.

## Resolved profiles matter

The headless CLI accepted bundled child preset names but did not reliably
apply inherited values. In one trial it displayed a Generic PETG preset while
exporting PLA filament type and temperatures. The repository's Q2C diagnostic
profiles therefore contain resolved parent values. Inspect effective printer,
process and filament settings from the review report rather than trusting the
preset names. Rebuild the snapshots if a new Orca version changes their schema.
The original [setup smoke record](../../../../model/vaseline_container/notes/orcaslicer_setup/README.md)
documents this profile combination, not a calibrated printer job.

## What the path parser establishes

The helper reads linear planar deposition in millimetres. It tracks absolute
or relative XYZ and extrusion modes, layer/role/width comments and extrusion
resets; it rejects arcs and nonplanar deposition. Historical PrusaSlicer
comments are accepted for archived model reports. Bounds include half the
reported extrusion width and generated brims/supports, and are compared with
the effective printer profile's rectangular printable area and height.

The report excludes travel, start/end machine moves and physical flow spread.
Bridge-role centerline length includes anchors and does not measure free-air
span. Missing width comments use an uncalibrated 0.45 mm fallback. Use CAD to
assess anchors, overhang geometry, local clearance and support access. The
helper's completed-slice and notice checks are summarized in its skill.
