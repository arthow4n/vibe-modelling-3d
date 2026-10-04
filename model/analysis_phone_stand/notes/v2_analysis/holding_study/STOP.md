Execution interruption, not a numerical or physical verdict: a concurrently run
backend regression test changed ENGINEERING_DATA without setting a separate
ENGINEERING_INSTANCE. Compatibility checking replaced the shared coordinator
and cancelled this refinement before it completed. The test now uses the existing
instance namespace. See holding_study_recovered for the bounded retry, which
identity-checks and reuses the completed holding_mount_corrected baseline.

The incomplete input and run metadata are retained for this diagnosis. No force,
strain, contact quality or convergence result is inferred from this run.
