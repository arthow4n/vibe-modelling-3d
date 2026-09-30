# Optional PolyFEM / IPC investigation

This external-executable adapter investigates the swatch lift-off failure where
native contact samples missed overlap at finite edges. It is absent from normal
engineering-question selection. `SnapFitQuestion` and CalculiX remain unchanged.
Qualification and the decision to keep/promote this route are recorded beside
[the experiments](../experiments/ipc/README.md).

Configure `POLYFEM_COMMAND=/absolute/path/to/PolyFEM_bin` and, when known,
`POLYFEM_COMMIT=...`. Use a native CLI, not the GUI `polyfem_app`. No upstream source,
binary, Python PolyFEM package or large runtime dependency is vendored here.
The investigation used the external executable identified in
[native_identity.json](../experiments/ipc/native_identity.json): the published
`teseoch/polyfem` container tag attributes a source commit; the executable does
not independently report that commit. Reproducing a run requires compatible
native libraries and the recorded executable/input identities, not just its name.

The adapter supports one P1 tetrahedral homogeneous SaintVenant elastic solid,
complete boundary-face support/prescribed regions, frictionless geometric
nonlinearity, translating rigid collision surfaces and continuous piecewise
linear prescribed motions. Complete obstacle translations are checked in every
accepted saved state. Force loads, overlapping support regions, interior-only
support regions, partial obstacle motion, rotations, multiple deformable bodies,
friction, plasticity, shells and rods are unsupported. They cannot silently become
another approximation. Whole deformable exterior surfaces collide; obstacle
surfaces follow the existing explicit master selections, including open patches.

```python
from physical_analysis.backends.polyfem import PolyfemBackend, IPCSettings
result = question.build_case().run(new_directory, backend=PolyfemBackend())
```

This low-level experiment does not call the stable question's CalculiX-specific
answer adapter or manufacture a penetration number. Model experiment entry
points reuse the existing questions' physical cases. `IPCSettings` is explicitly
experimental and keeps numerical investigation controls out of ordinary models.

## Units, mesh and equilibrium

The default system is mm, N, MPa, seconds and tonnes: density 1.2e-9 tonne/mm³.
The diagnostic SI mapping uses metres, kg, seconds and Pa: coordinates and
activation/CCD distances multiply by 0.001; elastic modulus multiplies by 1e6;
displacements return to mm and forces remain N. Green strain is dimensionless.
Density is an explicit native boundary-penalty metric assumption, not a calibrated
filament property or a simulated inertial load.

`time.quasistatic=true` omits native inertia. Effective native arguments and saved
zero inertia-force fields verify the chosen formulation. Physical energy forms
still carry dt²; their saved force fields undo that factor. Requested gradient
tolerance is scaled by dt²; the independent free-DOF residual remains in N.
Native characteristic length is chosen to keep the effective CCD distance fixed
when dt changes. Uniform grids include all motion knots exactly. Quasi-static
equilibrium does not remove continuation/motion-resolution sensitivity or prove
a continuous legal path between saved states.

Gmsh builds an actual P1 volume mesh and separate rigid surface meshes directly
from saved exact CAD BREPs. The MEDIT writer uses **version 2 (double precision)**.
Version 1 reads float32 even in ASCII: an early sliding run shifted rest nodes by
0.0000021 mm, larger than its barrier clearance. Independent supplied-mesh and
actual-native-mesh witnesses disagreed. That failed conversion is retained; it is
not treated as valid input geometry merely because IPC was clean on another mesh.
Current extraction checks supplied/native rest-coordinate identity. Exact
straight-tetra Green strain is reconstructed without nodal averaging; inversion,
missing fields and nonfinite data fail explicitly.

Initial triangle intersection/touching is rejected before solving. No automatic
part shift is hidden. Explicit offsets translate the rigid obstacles together,
are retained in provenance and require a reduced-offset control before they can
support a mechanism conclusion. Initial mesh clearance does not globally prove
exact-CAD clearance, especially on tessellated curves.

## Evidence and limitations

Every accepted frame has prescribed-pose, free-DOF residual, reaction balance,
zero-inertia and independent triangle intersection checks. The witness uses VTK's
triangle intersection routine, an AABB broad phase, finite-triangle distances and
closed-obstacle vertex/centroid containment. It is independent of IPC Toolkit.
Touching counts as intersection. Distance search is bounded; a clear distant
pair reports a lower bound rather than an invented exact distance.

`contact_frames` additionally samples selected flexible vertices/centroids
against exact rigid CAD. That is not a global CAD proof. Collision-facet clearance,
supplied/native mesh conversion, sampled-CAD intrusion and native barrier forces
are distinct evidence. An independent numerical mesh intersection rejects a run.
Native AL searches can temporarily free prescribed obstacle nodes; accepted
obstacle poses are verified rigid, but the saved-state witness does not certify
those transient searches as the prescribed rigid continuous path. Resolve the
relevant motion/tessellation sensitivity before claiming passage.

The opt-in `bounded_feasibility_search` diagnostic limits each intermediate AL
subsolve to 50 iterations before native projection-feasibility checks. Only that
nonphysical search permits its iteration limit; the final reduced equilibrium
still rejects iteration-limit/non-gradient completion and must satisfy the
recorded gradient tolerance and independent accepted-state checks. Extraction
verifies the effective final native policy. This control completed the generic
benchmarks, but its sliding experiment was interrupted for the user-requested
checkpoint. It has not qualified passage or earned promotion.

Obstacle forces come from exported collision-surface variational gradients;
support reactions negate elastic+contact gradients at prescribed DOFs. Compression
qualifies signs and balance. Full signed reactions retain holding forces; motion
force projections vanish on prescribed plateaus. `completed` requires a full
native history and recorded quality checks; it establishes no printed recovery,
strength, creep, bonding, friction or wear. Peak strain limits remain provisional.

```sh
POLYFEM_COMMAND=/path/to/PolyFEM_bin uv run --locked pytest -q tests/test_polyfem_ipc.py
uv run --locked python -m physical_analysis.backends.polyfem_diagnostics /path/to/stopped/run --prefix
```

Native tests are opt-in; skipped tests do not qualify a backend. Partial-prefix
diagnostics preserve `completed=False` and original solver status, never overwrite
`result.json`, and record accepted-field identities. Shared recovery only extracts
an identity-checked complete native solve; it launches no remesh or solver.
Retention keeps fixtures, numerical meshes, scene, hashes, logs and witnesses;
large VTU fields remain in the source run and can be regenerated through the
recorded CLI. Timeouts/interrupts stop the complete native process group.

Primary documentation: [PolyFEM input specification](https://polyfem.github.io/json/),
[contact documentation](https://polyfem.github.io/details/contact/),
[prescribed-obstacle example](https://polyfem.github.io/tutorials/sphere-pushing-box/sphere-pushing-box/).
The native source/input and executed behavior take precedence over stale comments.
