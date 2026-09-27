# OrcaSlicer CLI and profile notes

Use the [OrcaSlicer skill](../SKILL.md#run-the-review) for the current command,
profile arguments and report. These findings were checked with Flatpak
OrcaSlicer 2.4.2 on 2026-09-27; recheck them when the slicer or profiles change.

## STEP input in the headless CLI

Orca's GUI imports STEP, but the installed 2.4.2 headless CLI rejected a
positional `.step` file with `Unknown file format` and listed STL, OBJ and AMF
as accepted model inputs. Use the matching exported STL for the reference CLI
slice. That result cannot establish how Orca's GUI tessellates the STEP file.

## Resolved profiles matter

The headless CLI accepted bundled child preset names but did not reliably
apply inherited values. In one trial it displayed a Generic PETG preset while
exporting PLA filament type and temperatures. The repository's Q2C diagnostic
profiles therefore contain resolved parent values. Inspect effective printer,
process and filament settings from the review report rather than trusting the
preset names. Rebuild the snapshots if a new Orca version changes their schema.
The original [setup smoke record](../../../../model/vaseline_container/notes/orcaslicer_setup/README.md)
documents this profile combination, not a calibrated printer job.
