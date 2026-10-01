# IPC thread performance

Thread-only measurements completed on 2026-10-01; the user requested commit/push
and pause afterward. This phase does not audit the linear solver or tolerance policy and
does not attempt crest passage or lift-off. [Generated measurements](summary.json)
are the source for this comparison. The machine is an AMD Ryzen 7 1700 with eight
physical cores and sixteen logical CPUs. Each configuration has one timed native
solve, run sequentially; timing statistics and a universal optimum are not claimed.

The contact prefix is a synthetic/local benchmark derived from historical
failed-product geometry, containing only a clamped elastic leaf and moving cam.
[Fixture scope](../fixtures/rounded_snap/README.md) excludes all storage architecture.
Geometry, material, numerical settings, native executable and meshes are fixed.
Thread count changes both `--max_threads` and `OMP_NUM_THREADS` /
`OPENBLAS_NUM_THREADS`. Wall time covers the native process, including initialization
and native output; it excludes Python extraction/witness time. CPU percent is
summed child user+system CPU time divided by wall time, so it can exceed 100%.

## Fixed compression

| Threads | Wall s | CPU % | Speedup | Force N | Peak displacement mm | Peak Green strain % | Status / independent mesh |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 14.18 | 99.3 | 1.000× | 11.955037599 | 0.020000000 | 0.249687516 | completed / clear |
| 2 | 11.30 | 138.2 | 1.254× | 11.955037599 | 0.020000000 | 0.249687516 | completed / clear |
| 4 | 9.53 | 175.2 | 1.488× | 11.955037599 | 0.020000000 | 0.249687516 | completed / clear |
| 8 | 8.95 | 219.4 | 1.583× | 11.955037599 | 0.020000000 | 0.249687516 | completed / clear |
| 16 | 8.59 | 325.5 | 1.651× | 11.955037599 | 0.020000000 | 0.249687516 | completed / clear |

## Fixed local rounded-contact prefix

| Threads | Wall s | CPU % | Speedup | Force N | Peak displacement mm | Peak Green strain % | Status / independent mesh |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 130.92 | 100.0 | 1.000× | 0.323032212 | 0.311943344 | 0.307218886 | completed / clear |
| 8 | 87.18 | 248.5 | 1.502× | 0.323032482 | 0.311943344 | 0.307218886 | completed / clear |
| 16 | 95.70 | 322.8 | 1.368× | 0.323032212 | 0.311943344 | 0.307218886 | completed / clear |

The compression uses 265 P1 tetrahedra / 108 deformable nodes, a 42-triangle
floor, ten steps, dt=.1, tend=1, native gradient tolerance 1e-8,
`Eigen::SimplicialLDLT`, dhat=.001 mm and 200 nonlinear iterations maximum.
Sixteen threads has the shortest observed wall time here, but only 4% separates
it from eight. All reactions agree with the same analytical compression result.

The prefix replays the synthetic local spring/cam case from
[the retained fine-motion scene](../fixtures/rounded_snap/evidence/ipc/fine_motion_crest_failure/result.json).
It uses exactly the frozen .7 mm deformable mesh: 4,625 tetrahedra, 1,295 nodes
and 1,974 exterior triangles; the .3 mm cam mesh has 2,694 triangles / 1,349 nodes.
Only the endpoint is clipped to progress .1125: 18 steps, dt=.00625, tend=.1125.
The original native tolerance 3.90625e-11, characteristic length 160,
`Eigen::SimplicialLDLT`, dhat=.001 mm and 200-iteration AL/final limits stay fixed.
No iteration-limit acceptance is enabled. The cam drives the elastic snap; no
snap deflection is prescribed. Each accepted state passes the existing independent
triangle witness, prescribed-pose checks and equilibrium screens.

Eight threads is fastest among the useful prefix subset tested (1/8/16): 1.502×
speedup, about 33% less wall time than the historical forced single-thread route.
Sixteen uses about 43% more CPU seconds than eight while taking about 10% longer.
Force, displacement and strain pass a preselected 1% equivalence screen; actual
changes are much smaller (see generated comparisons). This timing result does
not attribute the remaining serial cost to the linear solver; that audit is deferred.

**Backend policy:** the optional adapter defaults to at most eight available CPUs,
capped by process affinity (or CPU count on platforms without affinity). An
explicit `IPCSettings(threads=1)` retains the historical reproducibility setting;
other positive explicit counts remain available for measured experiments. Resolved
count, native command, thread environment and native wall/CPU time are recorded.
CalculiX's existing runtime environment and `SnapFitQuestion` selection are unchanged.

Prefix completion is not full-operation completion: the result records
`native_operation_completed=False`. This study establishes no crest crossing,
return or new lift-off capability. The approximately .0034 mm curved-CAD versus
collision-facet discrepancy from earlier studies is still unresolved. A
[sampled CAD witness at this prefix endpoint](sampled_CAD_witness.json)
keeps that evidence separate from the clean numerical mesh witness; it is not a
global CAD proof. No obstacle refinement was performed.

Replay a retained scene with its recorded command/thread environment; full
native inputs, hashes and logs are retained beside each result. The private
[fixed-scene runner](../fixed_scene_study.py) checks input, numerical mesh and CAD
identity before replay and applies the standard extractor afterward. Its caller
records every scene change. For this prefix change only `time.tend=.1125`,
`time.time_steps=18`, and the extraction mesh record's `steps=18`; leave dt-derived
numerical settings unchanged. Native outputs are regenerated in a fresh directory,
never overwritten. Generate this study's summary without solves using:

```sh
uv run --locked python -m physical_analysis.experiments.ipc.summarize_thread_performance
```

The existing adapter tests cover explicit/automatic thread handling, effective
native thread count/command/environment/timing, and preserved collision quality.
The bounded-prefix extractor now uses actual native time rather than stretching
a clipped path to progress 1; its final convergence guard uses the same actual dt.
This is prefix bookkeeping, not a changed numerical tolerance or a completed audit.
Large native VTU fields remain in the source `/tmp` runs; compact retained histories,
witnesses, meshes and replay inputs are committed.

Analysis-only attribution: primary GPT-6 family; exact runtime variant and
reasoning effort not exposed; Codex harness; provider metadata not separately
exposed. No subagents or new printed observations. Original numerical outcomes and attribution remain unchanged. The source storage
product was physically rejected and removed; this coupon is no product precedent. Further investigation is paused; a full cycle is
not justified by a thread-speed improvement alone.
