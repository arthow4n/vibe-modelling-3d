# Command stopped for checkpoint

Case: **sliding swatch snap**, current close/reopen `SnapFitQuestion` physical case.
Neither build/install nor a lift-off study was running. The original launch was:

```sh
POLYFEM_COMMAND=/home/hevar/.local/opt/polyfem-ipc/PolyFEM_bin POLYFEM_COMMIT=591b08bd5e115bdefec7e2998e98f5b56bc1367e uv run --locked python - <<'PY'
import sys
sys.path.insert(0,'model/filament_swatch_box')
from analyze import operation
from physical_analysis.backends.polyfem import PolyfemBackend,IPCSettings
q=operation(mesh=.7,cycle=True,max_increment=.00625);q.timeout_seconds=3600
r=q.build_case().run('/tmp/ipc-sliding-bounded-feasibility',backend=PolyfemBackend(IPCSettings(obstacle_mesh_size_mm=.3,bounded_feasibility_search=True)),mesh_from='/tmp/ipc-sliding-double-fine');print(r.status,r.metrics,flush=True)
PY
```

Worker command:
`/home/hevar/git/vibe-modelling-3d/.venv/bin/python3 -m physical_analysis.backends.polyfem_worker /tmp/ipc-sliding-bounded-feasibility`

Actual native command (working directory `/tmp/ipc-sliding-bounded-feasibility`):

```sh
/home/hevar/.local/opt/polyfem-ipc/PolyFEM_bin --json scene.json --max_threads 1
```

| Setting | Recorded value |
| --- | --- |
| Deformable | 4,625 P1 tetrahedra, 1,295 nodes; 1,974 exterior triangles |
| Obstacle | 2,694 triangles, 1,349 nodes; .3 mm requested surface mesh |
| Deformable mesh request | .7 mm; exact mesh reused from saved fine-motion study |
| Time | 160 uniform steps, dt=.00625, tend=1, quasistatic=true |
| Maximum cam travel per step | .1 mm |
| Final force gradient tolerance | 1e-6 N; native dt²-weighted norm 3.90625e-11 |
| Final nonlinear iteration limit | 200; iteration-limit completion rejected |
| Intermediate AL diagnostic | 50 iterations per subsolve, permits bounded subsolve exit before native projection-feasibility checks |
| AL initial/max weight | 1e12 / 1e16 |
| IPC dhat | .001 mm; classical frictionless barrier |
| CCD tolerance | 1e-6 mm |
| Threads / timeout | 1 / 3,600 s |

At interruption the log covered approximately 748 s (12.5 minutes). Accepted
states had advanced through step 32 of 160, progress .2. Step 33 was continuing
Newton iterations after two bounded AL subsolves reached their limits. The last
logged final-solve gradient was .367 versus 3.90625e-11, with trial clearance
8.14e-11 mm. Thus the process was active, but that step was not accepted progress
and continuation was not evidence of convergence. The run was stopped through
the caller's interrupt handler, which killed the entire worker/native process
group. No PolyFEM process remains running.

[Retained interrupted run](../../../model/filament_swatch_box/notes/ipc/bounded_feasibility_user_stop/result.json)
and its separate prefix diagnostics preserve `completed=False`. All 33 saved
states (including initial state) have clean independent numerical mesh witnesses;
that prefix does not establish snap passage or elastic return.
