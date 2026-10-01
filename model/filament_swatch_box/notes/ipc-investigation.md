# IPC rounded-snap investigation

The geometry, E=1200 MPa, nu=0.38, rigid root, frictionless contact and retained
close/reopen motion come from the current `analyze.operation(..., cycle=True)`
`SnapFitQuestion`. No printed geometry or stable question implementation changes.

Decision: can the optional IPC route reproduce passage, the light-detent force
regime, roughly 1% strain, contact clearing at 0.5/1 and elastic return, while an
independent triangle witness agrees? Exact force precision is not the decision.

Bounded plan: freeze the .7 mm P1 deformable mesh and .3 mm rigid surface mesh;
compare .4 and .1 mm maximum cam travel per accepted step (.025/.00625 progress
increments). Use a 20% force/strain comparison for the broad conclusion, alongside
passage/return/contact-clearing checks. A failed coarse run permits the finer run
only to diagnose motion resolution; it does not establish stability. Stop a
rejected route on an independent intersection or quantified nonlinear failure.
Investigate obstacle refinement only after a credible complete path, to separate
collision-mesh geometry from the exact rounded CAD cam.

An early version-1 MEDIT experiment is unqualified: it silently rounded the
deformable rest mesh by up to 0.0000021 mm. A supplied-mesh witness intersected at
0.125 although the solver's actual rounded mesh did not. Version 2 fixes that
conversion; the two geometries and the failure remain retained. Exact-CAD samples
also found 0.00341 mm intrusion into the rounded cam between .3 mm collision
facets. This is distinct from native mesh intersection and needs tessellation
sensitivity before claiming CAD agreement.

The corrected coarse (.4 mm motion) run fails during AL at progress 0.125;
the .1 mm run advances to 0.24375 with 0.547 N and 0.945% peak strain, then fails
at the crest step 0.25. All accepted supplied/native-mesh witnesses are clean.
The final failed trial has roughly 4e-12 mm separation and native gradient norm
8.27 versus 3.91e-11 requested; these non-equilibrium AL forces are not engineering
actuation forces. Motion refinement improves progress but does not establish
passage. A same-mesh, same-motion projected-Newton control failed earlier, at
0.175, without improving the localized Hessian/continuation issue.
A dt²-scaled boundary-penalty control instead stagnated
at first engagement, hit 200 AL iterations, and was removed as an API option;
its generated native scene and failure remain retained.

Current status: **paused at the user's checkpoint request**; no complete IPC
passage established. A bounded intermediate AL search completed generic cases,
but its same-mesh 160-step sliding experiment was interrupted after accepted
progress 0.2; the next final Newton solve was active with worsening residuals.
The [checkpoint](../../../physical_analysis/experiments/ipc/checkpoint-run.md)
records the exact command, cost settings and stop. The
[shared decision record](../../../physical_analysis/experiments/ipc/README.md)
compares retained routes and preserves the unqualified status.
Native completion, passage, numerical confidence and printed validation remain
separate. Historical CalculiX evidence remains useful and unchanged.

The subsequent [thread performance study](../../../physical_analysis/experiments/ipc/performance/README.md)
replayed only a fixed prefix through progress .1125, with unchanged dt and native
tolerance. Eight threads completed in 87.18 s versus 130.92 s for one and 95.70 s
for sixteen. Accepted force/deformation/strain agree and all triangle witnesses
are clear. Sampled CAD still detects .00229 mm intrusion at that endpoint, distinct
from the earlier .0034 mm faceting discrepancy; neither is a numerical mesh
intersection. No crest crossing or obstacle refinement was attempted. The user
requested commit/push and pause after this thread-only phase.
