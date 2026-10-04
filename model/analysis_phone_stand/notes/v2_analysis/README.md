# Revision 2 analysis evidence

Current geometry and print instructions live in [the object record](../../README.md).
Results are conditional numerical evidence for explicit local fixtures, with
uncalibrated homogeneous PETG. No run establishes printed performance.

| Record | Meaning at handoff |
| --- | --- |
| `spring_final_m5/study_result.json` | Current production leaf: identity-checked baseline, increment and mesh runs from `spring_mount_corrected`, bound to the final plate's actual solid spring sections. No duplicate solves. Provisional strain/force screens and selected numerical comparisons pass. |
| `structure_m5_2048/result.json` | Final cradle with M5 pivots and crossbars moved above their axes. Service baseline completes; no current mesh sensitivity qualification. |
| `holding_study_recovered/study_result.json` | Current keeper, correct full-width root-pad restraints, two rigid guide cages, combined master surface. Baseline and doubled-penalty case complete; finer mesh times out. Mesh sensitivity and overall numerical adequacy remain unresolved. |
| `release/baseline/result.json` | Full finger-contact release/return: native 600-second timeout, no established passage or return. |
| `release_direct/baseline/result.json` | Full keeper prescribed release/return: timeout; local spring results do not replace this operation. |

Superseded records are deliberately retained. `spring_retry` records the initial thicker-leaf rejection against a
superseded root-restraint fixture; it does not qualify a comparison with the
current correctly restrained leaf. `spring_mount_corrected` is the current leaf's qualified
numerical source; `spring_final` binds the older plate. Other spring attempts
include an incorrectly restrained transition or interrupted/memory-limited work.
`structure_final` is the earlier M4 cradle, whose finer mesh failed meshing.
`structure_m5` and `structure_m5_current` contain incomplete outer-execution
attempts; their STOP records distinguish interruption and memory limits from
numerical rejection. `holding_fixture_rejected` used an invalid disconnected
mate; `holding_final`/`holding_coarse` used separate overlapping pairs;
`holding_union` clamped a narrowed transition. `holding_study` was interrupted
when a test changed the default coordinator configuration; it was recovered
as `holding_study_recovered` after isolating that test's coordinator instance.
Do not combine or promote these fixtures as evidence for the current stand.

Completed/failed native cases retain their result, history, provenance and
compressed replay inputs/geometry, while large raw field files are omitted
through `physical_analysis.evidence.retain_run`. See each result's artifacts
for replay instructions. Interrupted folders retain compressed inputs and a
STOP record; they have no invented completion result. Study reports interpret
native evidence and retain failed refinements.

Reproduce from the repository root into a **new** output directory:

```bash
./execute.py --memory-mb 2048 --timeout 900 model/analysis_phone_stand/analyze_v2.py structure NEW_DIRECTORY --mesh 2.4
./execute.py --memory-mb 2048 --timeout 1800 model/analysis_phone_stand/analyze_v2.py holding NEW_DIRECTORY --mesh 3 --study
./execute.py --memory-mb 1024 --timeout 900 model/analysis_phone_stand/analyze_v2_spring.py NEW_DIRECTORY
```

The holding study's limits are intentional: a completed coarse solve does not
justify indefinitely extending failed contact refinements. For path review,
re-slice with `--slice-keep-run` and run `review_v2_paths.py` through `execute.py`;
the temporary G-code paths in native slice reports are local to that run.
