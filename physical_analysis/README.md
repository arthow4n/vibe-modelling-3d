# Physical questions from CadQuery

A small engineering-question layer over a solver-independent case API with a working Gmsh → CalculiX backend.
Source geometry stays in CadQuery. Callers describe named parts, material
assumptions, supports, total surface forces, translations and explicit contact
pairs. The backend owns meshing, solver input, execution and result extraction.
It supports any number of named parts/pairs; it is **not** a general mechanism,
joint/dynamics, plasticity or printed-material simulator.

## Setup

An [optional external PolyFEM/IPC investigation](backends/polyfem.md) targets
finite-edge contact where geometric nonintersection affects the answer. It has
qualified simple contact/coupling cases but has not completed crest passage in
the local rounded-contact fixture. It remains isolated from ordinary engineering-question
selection; see the [checkpoint decision](experiments/ipc/README.md).

`uv sync --locked` installs the editable Python package and pinned Gmsh binding.
Install CalculiX and Gmsh's native library dependencies on the host, for example
on Ubuntu 24.04: `sudo apt install calculix-ccx libxft2 libglu1-mesa`.
`CALCULIX_COMMAND` can name an alternative executable (a path, not shell syntax).

This development environment has no passwordless sudo. Ubuntu packages were
instead downloaded with `apt-get download` and extracted with `dpkg-deb -x`
under `~/.local/opt/physical-analysis`. The backend recognizes that prefix, or
`PHYSICAL_ANALYSIS_RUNTIME`, and adds its `usr/lib/x86_64-linux-gnu`, `blas` and
`lapack` subdirectories to the isolated worker's library path. No native binaries
are stored in Git. Required packages here were calculix-ccx, libspooles2.2t64,
libarpack2t64, liblapack3, libblas3, libgfortran5, libopenmpi3t64 and their Ubuntu
runtime dependencies, plus libxft2. A system installation is simpler elsewhere.

Run `uv run --locked python -m physical_analysis doctor` to check both tools;
run `uv run --locked pytest -q tests/test_physical_analysis.py` to qualify them.
Missing tools are failures, not silently skipped benchmarks.

## Shared execution and performance

Run object-owned analysis scripts with `./execute.py SCRIPT.py`; scripts keep normal
Python semantics. Existing APIs also work when imported directly. All backends use
the shared resource coordinator, tracing and owned subprocess lifecycle. Gmsh,
CalculiX, FEBio and IPC retain isolated worker state and existing native-completion,
strain, quality and provenance checks. Default capacity is 50% of available cores;
integer/percentage command budgets and explicit IPC settings remain configurable.
Nested analyses borrow their command's budget. The current CalculiX/Gmsh route
runs one thread: use `./execute.py --threads 1 SCRIPT.py` for sequential studies
on that route. Larger leases reserve capacity without parallelizing that solver.
Keep explicit CPU budgets for parallel batches and other backends. Computation
runs without automatic deadlines; do not invent per-run or whole-study caps.
Follow the [repository deadline rule](../AGENTS.md#shared-engineering-execution).
Independent script studies can use
`execution.batch`. RSS is diagnostic; there are no shared memory budgets.

Dependency/solver initialization, input compilation, solve, extraction and recovery
spans are retained locally without output noise. Do not inspect them routinely;
[execution documentation](../execution/README.md) describes dedicated profiling and
history analysis. Unchanged mesh candidates are selected automatically with the existing backend
identity guards; stale/deleted references remesh. Mesh snapshots are verified after
copying, and reports identify reuse. Native solves still execute freshly.
Existing explicit `mesh_from`, saved-field recovery and question-study
`evidence` are the computational checkpoints: no unknown solve or script result
is cached. Recovery never turns an incomplete solve into engineering evidence.
Surface traction integration is batched with unchanged quadrature; repeated IPC
strain extraction reuses immutable reference-tetrahedron matrices. G-code paths
stream from disk. Conservative motion bounds skip only provably empty booleans;
exact distances and all potentially intersecting poses retain native checks.

## Use

Prefer `SnapFitQuestion`, `ContactQuestion`, `FlexureQuestion` or `StructuralQuestion` for a known
physical situation. Identify the geometry and named regions explicitly; supply
loads, material assumptions and provisional acceptance limits. The shared layer
constructs the case, restraints, observations and contacts, then checks the
answer. `AnalysisCase` remains the escape hatch for genuinely novel fixtures,
such as isolated multi-driver contact-formulation investigations.
For a product, first establish coherent [physical interaction architecture](../.codex/skills/cadquery-3d-design/references/design-decisions.md#product-architecture-gate);
these questions answer remaining local physics, not whole-product usefulness.
On numerical/contact failure, read [saved-result failure diagnosis](#locate-a-contact-quality-failure)
before changing inputs, switching backend or launching another solve. It separates
invalid fixtures, native convergence, quality rejection and design screens.

```python
import cadquery as cq
from physical_analysis import (FlexureQuestion, Support, Motion, Region,
                               PETG_SCREEN, BeamApproximation)

question = FlexureQuestion(
    name='tip_push', part=cq.Workplane('XY').box(40, 8, 2, centered=False),
    material=PETG_SCREEN, supports=(Support(Region.plane('x', 0)),),
    motion=Motion((None, None, 1), Region.plane('x', 40)),
    observations={'tip': Region.plane('x', 40)}, mesh_size_mm=1,
    beam=BeamApproximation(40, 8, 2, 'Straight uniform end-loaded leaf',
                           tip_displacement_mm=1, adequate_for_decision=True))
answer = question.run('notes/tip_push')
print(answer.metrics['question'])
```

This explicitly adequate, slender, small-deflection approximation uses the cheap
beam screen without meshing. Set `numerical=True` for a cross-check; otherwise
numerical analysis is selected when no adequate applicable approximation was
supplied. Screens remain in the numerical answer, with their rationale and
response ratio. A variable section, notch, tooth or different load distribution
needs its own applicability decision; supplying dimensions alone does not make
the approximation adequate. Analytical-only results have `status='analytical_screen'`
and `completed=False`: no solver was run. Numerical results retain native status,
history, assumptions, warnings and provenance. No new result framework is used.

`StructuralQuestion` accepts `supports`, total `SurfaceForce(region, force_N)`
loads, optional prescribed `motion` and named `observations`. Supports may leave
DOFs free through `None`. No service load is inferred. `acceptance` maps existing
metric paths to explicit upper limits, for example `{'max_displacement_mm': 2}`.
Material strain limits remain provisional screens, not calibrated printed limits.

`SnapFitQuestion` takes the same `part`, `material`, `supports`, `observations`
and mesh controls, plus `contact_region`, a tuple of `MatingPart(name, shape,
motion, contact_region)`, explicit `penalty_N_mm3` and `penetration_limit_mm`.
Whole-part fully prescribed translations make the mating parts rigid drivers.
Surface-to-surface is the qualified normal default here; the low-level case's
historical node-contact default is unchanged. `Motion.round_trip(displacement)`
constructs forward/reverse travel in one solve. Piecewise `progress` remains
available for staged motions; rotations and automatic mechanism recognition are
outside this interface. All forces and signed motion histories stay available in
`AnalysisResult.history`, including reactions during stationary holding plateaus.

For passage, specify `contact_free_at` normalized-time checkpoints and
`displacement_limits_mm={observation: ((xmin,xmax),(ymin,ymax),(zmin,zmax))}`.
An optional `return_observation` requests return to the initial unloaded pose;
all moving drivers must return to their start; a stationary mating part already
satisfies that condition. This permits a press-and-return release question with
a fixed keeper and a moving finger proxy. The shared answer checks engagement,
penetration, all-frame force balance, checkpoints, displacement envelopes and
elastic return. Missing passage criteria, observations or failed native quality
cannot become a successful snap. Checkpoints use the nearest saved frame only
within `checkpoint_tolerance`; this is sampled evidence, not continuous collision
proof. Surrounding rigid-driver clearance uses the existing CAD preflight;
envelopes do not prove full deformed-flexure clearance against the enclosure.

For a one-way snap closing, the keeper may finish in its seated position while
the flexible catch returns to its initial unloaded shape. Set
`require_driver_return=False` with `return_observation` and an explicit final
`contact_free_at=(1,)` checkpoint to check that recovery without inventing an
unintended opening motion. The default still requires drivers to return to their
start. Both policies verify the observed leaf displacement; the alternate policy
also requires the sampled final contact-free condition. Neither establishes
printed recovery or permits a loaded final state to count as unloaded return.
Independent synthetic-history contract tests cover stationary mates and one-way
recovery, including rejected loaded/residual/missing-evidence states. They test
the answer policy, not native contact qualification or a product mechanism.

`metrics['question']` distinguishes `solver_completed` (a full extracted history),
`operation_completed` (native accepted completion), `numerical_evidence_adequate`
(the requested checks), `design_screen_passes` (only the supplied provisional
limits), and `physical_limits.physically_validated` (never inferred). A completed
history rejected for penetration may have `solver_completed=True` while the
others remain false/unknown. Peak locations are undeformed element centroids of
the peak integration points; missing historical stress locations stay unknown.
Elastic numerical return does **not** establish printed recovery. The layer
does not infer calibration, friction, fatigue, plasticity or creep.

Associate `ManufacturingAssumption(description, gcode, sections,
maximum_uncovered_mm=...)` when solidity
matters. Explicit registered sections `(x_mm, z_mm, (y0,y1))` use actual Orca
paths through the existing coverage helper. An uncovered section rejects the
solid-section provisional screen. Section acceptance requires an explicit uncovered
width limit, recorded beside the result. Description-only records leave path coverage
unknown. Neither mode turns walls/infill/orientation into material properties.

### Force-loaded contact questions

`ContactQuestion` extends `StructuralQuestion` with explicit `contact_region`,
`mating_parts`, `penalty_N_mm3`, `penetration_limit_mm` and `discretization`.
It accepts ordinary surface `forces` and/or `motion` on the deformable part,
as well as prescribed translations of rigid mates. Each mate must be one
connected solid. Rigid mates specify all three translations; stationary mates use
`Motion((0,0,0), name='unique_support_name')`.
For a deformable mate, omit `motion` and supply explicit `supports`, optional
`forces` and an explicit `material`, even when it matches the question's material.
For example, `MatingPart('housing', housing, contact_region=roof,
supports=(Support(foundation),), material=housing_material)` permits the printed housing to share deformation
and load. Mixing rigid motion with those elastic-fixture fields is rejected.
Every elastic body's finite strain and supplied material limit enter the answer;
missing mate strain cannot qualify a result. Constraints use a mate-name prefix,
so constraint identifiers must still satisfy the existing case naming rules.
No freely rotating joints, friction, thread preload or contact-free body dynamics
are introduced. Analytical-only execution is rejected.

Multiple mates use one combined master surface by default, avoiding overlapping
slave definitions while preserving separate mate motions/reactions.
`combine_mating_surfaces=False` retains separate pairs when explicitly needed.
`SnapFitQuestion` defaults to separate pairs to preserve historical input
identities; new multi-obstacle fixtures can explicitly select the combined route.
Native two-stop qualification covers force transfer across independently fixed
mates. The phone fixture exposed the need for this existing backend facility;
the earlier overlapping-pair solve timed out and remains unqualified.

The answer requires native completion, equilibrium, finite strain, finite bounded
penetration and observed contact matching `contact_expected` (default `True`).
Use `contact_expected=False` only for an explicitly supported open-gap question.
Missing contact fields and failed solves leave the design screen unqualified.
`SnapFitQuestion` shares this construction but additionally requires engagement,
passage checkpoints, displacement envelopes and any requested elastic return.
It still rejects direct deformable-part loads; its drivers define the operation.
Snap passage currently requires rigid mate translations. Existing rigid-mate
signatures and retained case identities are preserved. Studies skip elastic
mates when reporting prescribed travel and include the main part's own motion.

The [compact fully printed phone stand](../model/analysis_phone_stand/analyze_v3.py)
uses deformable contact to distinguish nose bending from housing compliance
under its 30 N local lock-load screen. The initial nose failed the provisional
strain limit while the housing passed, directing reinforcement to the nose.
An independent pair of equal cantilevers qualifies shared deformation: a 0.1 N
load and 0.2 mm gap produce about 0.267 mm loaded-beam displacement, with finite
mate strain, equilibrium, bounded penetration and retained-identity checks.
This extends fixture construction above the existing multipart backend; it does
not qualify printed properties or an unrestricted moving assembly.

The [raised phone-stand consumer](../model/analysis_phone_stand/analyze_v2.py)
applies a 5 N lifting force to its flexible keeper against two stationary guide
cages. This resolves the previous force-plus-contact question-layer gap without
duplicating case/solver plumbing. A native clamped-beam benchmark under 0.1 N
qualifies gap closure and load transfer: the free 0.333 mm response is limited by
a stop at 0.2 mm, with equilibrium, penetration and retained-identity checks.
This qualifies the wrapper's existing frictionless backend route, not printed
PETG or a general bolted-joint model. `QuestionStudy` and `read_evidence` apply
unchanged, including explicit unsupported/failure outcomes.

### Standard question studies and retained evidence

For an explicitly constructed snap question:

```python
from physical_analysis import QuestionStudy
study = QuestionStudy(snap_question, decision='Force precision for prototype selection',
    metrics=('question.peak_actuation_force_N', 'question.peak_strain'),
    relative_tolerance=.10, motion_levels=2, mesh_levels=1, contact_levels=1)
answer = study.run('notes/study')
```

Select only axes that can affect the decision (all default to zero). The bounded
plan halves the motion increment, reduces mesh size by 0.7 or doubles contact
penalty, one factor at a time. Mesh/contact factors and absolute metric tolerances
are explicit overrides. Requested travel per increment is reported in mm from
each progress segment; actual adaptive increments may be smaller. A baseline
without adequate numerical quality stops without refinements. A completed design
screen failure can still be refined to resolve uncertainty near a limit; when
the failure already settles the design decision, revise the product instead of
requesting that refinement. Each level compares decision quantities with
the preceding level, stopping that axis when its quantities meet the tolerance.
The answer reports `stable`, `unstable`, `unresolved` or `not_run` and the stopping
reason; stability is a bounded comparison, not proof of asymptotic convergence.
The saved study records its relative and absolute metric tolerances alongside
the comparisons, so the numerical stopping rule remains explicit in evidence.
Both `QuestionStudy` and `compare_results` require `relative_tolerance`; omission
cannot choose an acceptance rule. Existing callers retain their previous limits
explicitly rather than retuning the numerical question.
`baseline_quality_adequate` preserves the operation checks; requested unstable or
unresolved studies make overall `numerical_evidence_adequate=False` without
erasing independently established passage or changing native completion/status.
Failed refinements and missing quantities remain unresolved. Force precision
and provisional strain acceptance are separate; convergence does not calibrate
material properties. Crossing a supplied acceptance limit prevents a stable
classification even if the relative change is small. Backend/tool identity
changes make a comparison descriptive; later matching levels can still establish
their own comparison. The caller chooses tolerances against the stated action.

Pass `evidence={'baseline': existing_run, 'increment_sensitivity_1': refined_run,
...}` to reuse checked runs; a missing entry requires a new output directory.
`question.read_evidence(path)` compares current geometry hashes, material,
supports, selections, motion, contacts, observations and numerical settings to
the saved case, and checks case/input hashes against result provenance. Changing
intent fails explicitly. Case names and timeouts are not physical inputs.
Historical backend versions/implementation identities are preserved and exposed;
interpreting historical evidence does not qualify today's backend. No saved solve
is rerun merely to add interpretation. Native result status is never promoted.

The [swatch-box K consumer](../model/filament_swatch_box_study/analyze_cap_k.py)
uses this route for its saved 0.8/0.65 mm meshes:

```bash
./execute.py model/filament_swatch_box_study/analyze_cap_k.py --review-evidence
```

It supplies every planned evidence entry and no run directory, so missing or
mismatched evidence fails instead of launching a solve. The native
[`AnalysisResult` report](../model/filament_swatch_box_study/notes/cap_k_physics.json)
replaces its manually assembled comparison: input identity, tool identity,
force/strain sensitivity and acceptance changes use the existing shared study
contract. Geometry, the current rear-space limit and the provisional material
assumptions remain in the consumer. Both selected quantities meet its 10%
comparison threshold; increment/contact sensitivity and printed behavior remain
unestablished. Relative change uses the refined value as denominator. This
consumer also exposed missing threshold metadata: studies now retain the chosen
relative/absolute tolerances, without changing comparison or solver behavior.

The [local rounded-contact fixture](experiments/ipc/fixtures/rounded_snap/README.md),
[phone stand](../model/analysis_phone_stand/analyze.py) and
[book plate](../model/book_reading_plate/analyze.py) exercise evidence binding,
positive/negative answers and native cross-checks in
`uv run --locked pytest -q tests/test_engineering_questions.py`.
The fixture is synthetic numerical geometry derived from a physically rejected
storage product, not a product precedent. Local CalculiX passage/return is retained;
force remains increment-sensitive. The book's plain-back calculation agrees with
structural analysis, while its monolithic L face-load fixture exposes section
distortion absent from the beam assumption. Existing joint equations remain the
cheaper primary screen. No numerical pass validates whole-product architecture.

### Lower-level experiments

```python
import cadquery as cq
from physical_analysis import AnalysisCase, Region, PETG_SCREEN

beam = cq.Workplane('XY').box(40, 8, 2, centered=False)
case = AnalysisCase('tip_load', nonlinear=True)
case.add_part('arm', beam, material=PETG_SCREEN, mesh_size_mm=1)
case.fix('arm', Region.plane('x', 0))
case.apply_force('arm', Region.plane('x', 40), force_N=(0, 0, -0.1))
answer = case.run('notes/tip_load_run_01').require_completed()
print(answer.metrics)
```

All coordinates are assembly coordinates, in mm. Forces are N, stress and
modulus are MPa. `Region()` means the entire part; `Region(lower, upper)` is a
box. Plane regions select a coordinate plane. Constraints select nodes; surface
loads/contact select **complete exterior quadratic triangle faces** inside the
region. Empty selections fail. Partition a CAD face when a small load patch
needs exact boundaries; a box cutting through triangles approximates that patch.
Total force is integrated over the selected surface, not multiplied by node count.

The optional [assembly geometry API](../assembly_geometry/README.md#existing-consumers-and-integration)
provides authoritative positioned Shapes through `configuration.shape(name)`.
Pass these directly to existing questions or `AnalysisCase.add_part`; regions
use that same assembly frame. Native CAD constraints do not imply physical
supports, loads or contact pairs. `QuestionStudy` remains the numerical-study
interface; ordinary Python geometry studies can reuse the same configurations
and geometric requirements before any solve.

`fix(part, region)` fixes all three displacement components.
`constrain(..., displacement_mm=(0, None, None))` fixes only x.
`prescribe_motion(..., displacement_mm=(None, None, 1))` ramps z to 1 mm while
leaving x/y free. It translates a selected region, not a hinge rotation.
A fully prescribed part behaves as a moving obstacle; otherwise an explicit
material and sufficient supports are required. Do not overconstrain a flexure's
free face unless that is the actual loading fixture.

```python
case.contact('spring', Region.plane('z', 2),
             'obstacle', Region.plane('z', 2.1), penalty_N_mm3=60000,
             penetration_limit_mm=.05)
```

Contact uses frictionless penalty contact. The default
`discretization="node_to_surface"` preserves existing cases; the optional
`discretization="surface_to_surface"` integrates over contacting faces and is
qualified by the compression benchmark and local rounded-contact studies.
The [CalculiX 2.21 manual](https://www.dhondt.de/ccx_2.21.pdf) cautions against
node-to-face contact with quadratic elements. Surface-to-surface contact enabled
the historical local rounded-cam pass-over studies after node-contact timeouts;
geometry also changed, so this is not an isolated formulation comparison.
Both choices require an explicit penalty stiffness.
`master` may instead be a nonempty tuple of `case.select(part, region)` values.
This makes one surface from multiple independently moving obstacles; it does
not join their mechanics. Duplicate selected faces fail. For example, the same
latch can touch a cap and a press actuator through one contact interface.
CalculiX requires one contact discretization throughout the deck.
In CalculiX 2.21, node-to-surface normally updates the pairing during Newton
iterations, freezing it from iteration nine to improve convergence;
surface-to-surface updates it once at the start of each increment and keeps it
fixed during that increment ([manual, §7.22 and §10.4](https://www.dhondt.de/ccx_2.21.pdf)).
Surface-to-surface can accumulate large total travel, but each increment must
resolve changes at edges and curved leads. It is not the same per-iteration
finite-sliding algorithm. Earlier result assumption strings calling every
formulation finite sliding are inaccurate descriptions, not evidence of that
capability. Keep those historical results and reassess consequential motion
resolution instead of silently relabelling their predictions.
Check engagement, penetration, force balance, mesh sensitivity and penalty
sensitivity before using its numbers. No geometry is silently adjusted to close
gaps. Loads retain one proportional static ramp. A translation can instead follow a
piecewise-linear progress curve in the same nonlinear step:

```python
case.prescribe_motion('obstacle', displacement_mm=(-8, 0, 0), name='drive',
                      progress=((0, 0), (.5, 1), (1, 0)))
```

Each pair is normalized time and multiplier of the reference translation.
Times must increase from `(0, 0)` through time 1; the curve can reverse or pause.
This example drives 8 mm and returns, retaining contact/deformation in one solve.
It is a quasi-static path, not elapsed seconds, dynamics or a fatigue cycle model.
The solver samples converged increments; a progress knot is not guaranteed to be
an output frame. Check actual motion, contact passage and increment sensitivity.
During a pause the projected motion force is zero; reaction vectors still report
holding forces. At a knot the signed projection uses the incoming segment.
Multiple steps, rotations, friction, rigid-body joints, contact activation changes
and self-contact remain unsupported.

## Plan a contact study

### Experimental alternative for finite-edge contact

A historical finite-edge release investigation exposed a need for updating
contact projections during iteration and controlling overlap through augmentation. The optional
`physical_analysis.backends.febio.FebioBackend` uses FEBio's frictionless
`sliding-elastic` formulation. It accepts the existing case intent, with
`surface_to_surface` contact and prescribed nonlinear translations. Force
loading, rotations, dynamics and other material laws are not supported by this
narrow adapter; the default backend remains CalculiX.

```python
from physical_analysis.backends.febio import FebioBackend
result = case.run(directory, backend=FebioBackend(), mesh_from=previous_run)
```

The numerical penalty remains explicit. Augmented Lagrangian enforcement is
enabled by default; its native gap criterion is one tenth of the case's stated
penetration limit. Projections update without an iteration limit, node
relocation and friction are disabled, and the nonsymmetric tangent is used.
`two_pass=True` checks projections in both directions and checks native maximum
overlap on **both** surfaces; reported contact area remains the primary area's
sum. These choices are numerical strategies, not fabricated material properties.
See the [official formulation documentation](https://febiosoftware.github.io/febio-feature-manual/features/solid_surfaceinteraction_sliding-elastic/).

Zero supports use zero-valued prescribed displacements because FEBio's fixed
DOFs do not retain the needed reaction fields. Native nodal forces are negated
to match the shared external-actuation-force convention. An explicit 1e-12
native squared-residual floor avoids chasing roundoff during an unloaded
approach; independent force-balance and native-field checks remain in force.
`force_residual_tolerance_N` explicitly sets that absolute free-DOF residual
norm (default 1e-6 N); FEBio's native `min_residual` receives its square.
If tiny adaptive increments make the relative displacement criterion chase
irrelevant corrections, choose a residual accuracy against the engineering
decision, then check sensitivity. This may resolve convergence effort; it
cannot repair missed contact, pass geometric witnesses, or calibrate material.
Benchmarks cover open-gap onset, compression/unloading, bending driven by
contact, independent obstacle motion, peak-strain recovery and rejection of
excessive overlap. They do not qualify a new finite-edge operating sequence.

Install the [official standalone FEBio Linux archive](https://repo.febio.org/download/)
outside the repository and set `FEBIO_RUNTIME` to its `FEBio4` directory or
`FEBIO_COMMAND` to its executable. The investigation used 4.13.0.3ef378562;
record the downloaded archive hash and actual version. Native executable and
core/mechanics/numerics library hashes are recorded in results. No Python
dependency or new environment manager is needed. The `.inp` retained with a
FEBio case is the shared mesh deck; `.feb` is its actual native solve input.

For long contact runs, `python -m physical_analysis.progress RUN` reads compact
native accepted-increment records and converts recent progress to actual
prescribed driver travel. It does not forecast convergence or assert contact
quality. Run metadata is saved before the native solve so timeout/interruption
can retain mesh and implementation identity; no successful metrics are inferred.

CalculiX `discretization="mortar"` is an **unqualified experimental probe**:
its contact output is in FRD, outside the text extractor's supported contract.
It returns `unsupported_output`, with no successful contact metrics. The known
open-gap probe also exposed premature contact in that tested configuration.
It is not promoted as a solution, and this does not prove all Mortar setups
incapable. The [native manual](https://www.dhondt.de/ccx_2.21.pdf) also prohibits
repeated surfaces across Mortar pairs; a union of selected obstacles expresses
the cap/actuator interface without that duplicate definition.

### Study sequence

Before solving, name the design decision, relevant quantities and acceptable
uncertainty. Separate passage, strain, recovery and operating-force targets;
they need not require the same precision. Use the cheapest analytical force
screen first when applicable, including consequential guide/fit extremes.
Choose residual, travel-resolution and sensitivity tolerances around the accuracy
that could change the next action. Benchmark identities can need much tighter
accuracy than a first-print force estimate. Treat tool qualification, failure
diagnosis and product acceptance as distinct purposes; state which one a study
serves. Extra decimal places do not remove uncertainty in material, friction or
fixture assumptions.

Before an investigation run or batch, state the question in ordinary language, what
result would distinguish the explanations, what action each outcome would
change, and when to stop. Keep this in the existing object record; no separate
form is required. Reuse that question and stopping rules for controlled
comparisons; do not create repeated manual entries for automatic checks.
Inspect consequential accepted frames early, including during
a running solve when available, rather than waiting for completion merely to
discover a rejecting overlap. Optional solver routes belong to investigations
with a concrete need, not the default checklist for every model.

Qualify a new formulation/backend on a known open gap, contact onset,
compression and separation/return before interpreting the object's operation.
Check signed forces, force balance, output availability and the strain measure.
CalculiX Mortar and FEBio exposed different output locations, force conventions
and strain-output averaging; successful native termination did not establish a
compatible result contract. Missing fields fail explicitly rather than becoming
zero penetration. An opening-only fixture may isolate a failure, but its
assembled initial state is a dependency, not evidence that closing succeeds.

Inspect finite-edge geometry when it drives the decision. A native maximum gap
can miss a penetrating vertex between surface integration points. A historical
finite-edge fixture study found a vertex behind a selected **planar native master triangle**, not
just inside a curved CAD approximation, despite a much smaller reported gap.
The diagnostic helper can retain that planar-facet witness; it does not provide
a global intersection bound or identify the solver's matched projection.

For a new operation, first obtain and inspect one complete representative path:
actual motion, contact passage, reaction history, strain location, penetration
and return. Check travel-increment resolution before spending on mesh/penalty
studies when narrow contact events or force peaks could be under-resolved.
Then compare mesh and contact settings at adequate travel resolution, varying
one factor where practical. Revisit coupled sensitivities if a change alters the
contact sequence; no study order guarantees convergence. Do not treat all runs
sharing a coarse increment as independent evidence of a resolved force peak.

For fixed-mesh controls, use `case.run(new_directory, mesh_from=existing_run)`.
This performs a new solve on the saved nodes/elements; it does not reuse old
predictions. Source input/case hashes must match their result provenance, and
ordered part names, fixture BREP hashes and mesh-size settings must match the
new case. Geometry or mesh changes are rejected; material, constraints, contact
and increments are compiled afresh. The original mesh input/case are copied
into the new run and retained by the evidence helper. This avoids assuming
that remeshing with the same requested size creates an identical mesh: the
historical finite-edge study exposed different node positions with unchanged
geometry, settings, mesher version and adapter. Compare mesh-refinement runs separately.

Choose relative or absolute change criteria against the decision before repeated
refinement. A small absolute force change may leave the same first-print decision
while failing a percentage criterion; record the failure and conditional force
range, rather than renaming it convergence. Stop when additional precision cannot
change the next action, keeping unresolved numerical limits separate from
material/friction uncertainty. Identify numerical quality screens, provisional
design targets and evidence-backed physical limits separately: a penetration
screen is not automatically a measured physical failure boundary. Do not relax
a screen to make a run pass; document why a revised threshold is sufficient for
the decision and recheck affected evidence.

A saved frame that rejects the current route can justify stopping before the
whole path finishes. Continue only when the remaining solve or refinement could
answer a named diagnostic question. Retain the witness and stop reason; deliberate
backoff is not a native convergence-limit failure. Report useful tool/debugging
findings separately from confidence in the object's operation. Established
benchmarks should run automatically when applicable, without repeating manual
review of already qualified behavior.

Existing `studies.compare_results` reads completed
results without rerunning a solver. Local-fixture completion does not establish
whole-assembly compliance or collision clearance.

## Result contract

`completed` means the solver finished the entire normalized load interval,
required nodal/integration-point fields exist and force imbalance at every saved
increment is below 1% (normalized by the larger of applied force, summed reaction magnitudes
and 1 N). It does **not** mean the design is adequate. `status`, `errors` and
`warnings` distinguish failures, timeouts and completed solves with notices.
`require_completed()` raises on incomplete analyses. Partial solves never return
successful metrics. Peak forces are reaction-vector magnitudes per constraint
region, including only its prescribed DOFs; history retains signed components
and per-frame force imbalance.
Overlapping constraint regions may report the same reaction in both regions;
force balance deduplicates constrained node/DOF pairs.

The parser accepts CalculiX's fixed-width numbers with omitted `E` markers in
three-digit exponents, preserving tiny elastic-return fields. If extraction
fails after a completed solve, the private worker's `--postprocess-only` recovery
can reuse its saved mesh and fields in the configured native environment. It
requires a byte-identical regenerated input, checks the saved solver completion
log and reruns field/quality checks; it neither remeshes nor launches a solver.
Recovery records its provenance and leaves the original input/log intact.
Keep the original artifacts; this is not an importer for arbitrary solver decks.

Use the shared wrapper for either backend:

```sh
uv run --locked python -m physical_analysis.recovery /tmp/existing_run
```

`recover_run(directory)` verifies original input/case identity, uses the same
process-group cleanup as a solve, regenerates byte-identical native input, and
rechecks existing fields. It launches no native solver and preserves the original
result when recovery fails. A successful extraction repair records a separate
recovery log; failed quality screens remain failures. Large raw fields must still
be present locally.

Strain is the maximum absolute principal mechanical strain at integration
points across saved increments, with the part, element and integration point.
It is neither engineering shear strain nor a promise of elastic recovery.
The named material strain limit is an explicit screening assumption. Sharp
fixed edges can create mesh-sensitive singularities. Inspect/converge the
quantity relevant to the design rather than treating a peak as a universal
failure criterion. Displacement includes prescribed rigid travel.

The optional FEBio route reports **Green–Lagrange strain**, recovered
from nodal kinematics at the explicitly selected tet10 G8 points. The recovered
principal-strain means must agree with FEBio's native element logs within
1e-6 absolute strain. Element means alone cannot establish peak strain. Read
each result's material law and strain assumptions when transferring a screen
or comparing backends. CalculiX's nonlinear elastic E output is also Lagrangian
strain; with no thermal loading it is the same strain measure. The selected
elastic laws share the St Venant–Kirchhoff intent, while volume quadrature and
contact algorithms differ ([CalculiX 2.21, §§6.8.1 and 7.36](https://www.dhondt.de/ccx_2.21.pdf)).

`observe(part, region, name='tooth')` adds signed displacement minima, maxima
and means for a feature. History includes these observations and the signed
reaction projected along each prescribed translation and its current progress
direction. `peak_motion_force_N`
is the corresponding actuation-force magnitude; it excludes orthogonal holding
reactions. `check_strain_limits()` returns per-part conditional screening results.
At a stationary plateau in a progress curve, the motion-direction force is zero
because there is no current travel. A press-and-hold release still needs holding
effort: read the relevant axis of its recorded `reactions_N` across that plateau,
not only `peak_motion_force_N`. All reaction components remain available.

Choose driver contact faces for the intended load transfer. For a normal press
actuator, including its side faces can add unintended vertical restraint;
an engineering block is not a model of skin or grip. Conversely, include real
cap edges that cross the snap during motion. Keep these fixture choices and
their omitted physical behavior with the object.

Contact penetration above the explicit, required `penetration_limit_mm`
rejects the result with `status='quality_failed'`, retaining diagnostic metrics.
Choose a tighter limit when fit requires it. Unknown solver parameters fail
instead of being accepted as warnings. Other warning messages include context.

Each new run directory owns `case.json`, geometry BREP snapshots, solver input,
raw `.dat` results, logs, increment status and `result.json`. Existing directories
are never overwritten. Hashes, mesh sizes, tool versions and boundary selections
are retained. `AnalysisCase` and engineering questions default to
`timeout_seconds=None`: worker initialization, meshing, solving and extraction
have no automatic wall-clock limit. Recovery and contact diagnostics are also
uncapped. An explicit user-requested limit can use a positive `timeout_seconds`;
if it expires, the worker and solver process group are stopped together.
Gmsh's global state is
isolated per run, so independent callers can run concurrently.
Timed-out native runs retain the sampled resource summary in
`provenance.execution_resources` when available. This is partial CPU/RSS and
elapsed-time evidence, never completion or convergence evidence. A surrounding
command can expire first and terminate the caller before it writes a native
result; inspect its separate execution record and partial logs in that case.
Caller interruption also stops that isolated process group, records an
`interrupted` result, and re-raises `KeyboardInterrupt`. Retain it as incomplete
evidence if useful; cancelling a superseded design must not leave its solver
running in the background.

The worker streams full result fields one increment at a time, retaining a
compact history. This bounds full-field memory independently of increment count;
the compatibility `parse_dat` helper still collects frames when called directly.
A historical large contact study exposed a silent worker failure after a completed
solve with nearly 1 GB of text fields. A worker failure now reports its exit code even when
its log is empty. Recovery can re-extract the saved solve; it must still satisfy
the input-identity and completion checks above, and does not repair contact quality.

Before meshing, moving pairs of fully prescribed whole-part translations receive
a sampled CAD clearance screen. Their relative progress knots are subdivided
to at most 0.25 mm relative travel per interval. An overlap above 1e-7 mm³ returns
`invalid_rigid_motion` without launching the solver; the case, fixtures and
`rigid_driver_clearance.json` remain available. This catches collisions between
rigid drivers that would otherwise be ignored when contact is defined only to
the flexible part. No sampled overlap is not continuous-path proof. Partial
region constraints, deformable parts and static relative pairs are excluded;
contact/deformation still needs its own analysis. For example, a press actuator
must withdraw before another rigid driver passes it; generic tests cover this
preflight independently of the retired source products.

The default PETG material is an explicitly assumed homogeneous solid, **not a
model of two walls and 7% infill**. Use geometry that represents the load-bearing
section, a documented conservative effective material, or an appropriate solid
print. Calibrate against physical tests before claiming real force or strength.

## Locate a contact-quality failure

First distinguish invalid fixtures/generated input, native convergence failure,
completed solves rejected by quality checks, and provisional material/design
screens. None alone proves the product impossible or the backend incapable.
Localize the failure in saved logs, histories and fields and verify the actual
formulation's documented behavior before changing geometry, numerical settings
or backend. Qualify a new backend through the [study sequence](#study-sequence).
A deliberate investigation stop is distinct from native convergence failure.

Before launching another solve, use the saved result, input and raw fields:

```sh
uv run --locked python -m physical_analysis.diagnostics /tmp/box_run model/box/notes/contact_locations.json --rigid-parts lid_catch release_pad
```

`physical_analysis.diagnostics.contact_frames(run, fractions=None,
rigid_parts=())` defaults to the saved frame with greatest reported penetration.
Pass `--fractions .29 .75` or an explicit Python sequence for other saved frames.
The isolated adapter reads the original C3D10 mesh, pairs CDIS/CSTR rows in output
order, groups repeated element/face identifiers without mistaking them for unique
integration points, and returns pressures, gaps and ten deformed quadratic-face
samples. Optional named rigid parts use their saved BREP and actual recorded
uniform translation to report signed sample distances: positive outside,
negative inside. Input/case identity is checked against result provenance;
changed fixture snapshots, missing frames or deforming comparison parts fail.

Native contact gaps and sampled CAD distances answer different questions.
Matched master faces and actual contact quadrature coordinates are not present
in these fields; face samples do not prove absence of intersection. A discrepancy
helps locate a suspect projection, edge transition or mesh approximation. It
does not erase a failed quality screen or prove a solver defect. Keep the report
with the model, including its limits. The helper is read-only and needs raw DAT
fields still present in the original run; compact archives omit those fields.

For FEBio, the same helper samples **every selected slave face**, including
faces with no detected projection. It records native maximum gap separately
and retains the worst sampled face for each rigid CAD driver. Native FEBio gap
is positive for overlap, unlike this CalculiX version's negative CDIS sign.
Requested converged frames from an incomplete native run can be inspected
without turning them into a completed operation. FEBio requires its original
nodal/contact logs; compact archives retain replay inputs and summaries instead.
An explicit accepted fraction can also be inspected before a final result file
exists, using the frozen `run_metadata.json` identity. Missing/incomplete frames
still fail, and the report remains `no_final_result`; no completion is inferred.
For a worst sampled point on an exactly planar native master triangle, the
helper also records its projection, triangle and signed plane distance. This
can distinguish a real overlap witness from curved-master tessellation error;
it is not a native matched contact point or an intersection bound. In a historical
finite-edge release (product scene archived in Git through `d37763c`), a native gap
below 0.001 mm coexisted with a 0.039 mm planar vertex overlap. A small native
maximum gap alone therefore cannot establish passage.

## Retain analysis evidence

Use `physical_analysis.evidence.retain_run(run, destination)` or:

```sh
uv run --locked python -m physical_analysis.evidence /tmp/box_run model/your_object/notes/analysis/new_trial
```

The destination must be new. The helper preserves result history, assumptions,
failure status and provenance; copies the case and increment record; and retains
available input, logs, selected regions and all fixture BREPs as deterministic
gzip files. Artifact links name only files actually copied. Bulky raw fields are
excluded; replay instructions come from the backend. Failed/timeout runs can be
retained without claiming completion. This archives an existing CalculiX or FEBio run;
it launches no solver, changes no source run, and does not replace original raw
fields needed for postprocess-only recovery. Older object archives remain valid
historical records even when they contain fewer artifacts.

Reused-mesh runs also retain `mesh_source.inp.gz` and `mesh_source_case.json`.
Unpack the mesh-source input as well as the run input before postprocess-only
recovery; source identity is still checked. `mesh_from` expects an existing run
with uncompressed input/case/result files, not a compressed archive directly.

Keep object-specific metrics, acceptance conditions and plots with their model.
Do not copy this file-retention implementation or hand-maintain a second history
table; derive summaries from retained results and link them from the decision
record.

## Evidence and extension

This API is an evolving foundation. Agents should actively identify reusable gaps
in real modelling questions and implement justified in-scope extensions, following
the repository's [shared-tool guidance](../AGENTS.md#improve-shared-tools-from-concrete-needs).
Use simpler CAD checks or analytical screens when they adequately answer the
design question. Explicitly agreed analysis exercises may also pursue named tool
capabilities and qualification criteria; evaluate product usefulness independently.
Keep model-specific fixtures with their object, and bring reusable analysis behavior
into this package with an exercised consumer and appropriate numerical evidence.

Acceptance tests cover beam bending/refinement, displacement-controlled flexure,
contact onset and an open gap, contact penalty sensitivity, contact-driven flexure, force balance,
invalid regions, conflicting constraints, ignored solver parameters, excessive penetration,
feature observations, surface-contact compression/open gap, a contact load-and-return
cycle, missing solver, timeout and stale-run
protection. Benchmarks qualify these analysis types, not every nonlinear model.

The implementation follows the [CalculiX 2.21 manual](https://www.dhondt.de/ccx_2.21.pdf)
and [Gmsh API documentation](https://gmsh.info/doc/texinfo/). Tetrahedral midside
node ordering is explicitly converted to C3D10 ordering. Loads integrate
quadratic surface shape functions. CalculiX 2.21 contact `.dat` output uses
negative normal CDIS for overlap in the compression benchmark; penetration is
reported as `max(0, -CDIS_normal)` and tested against pressure/penalty.

Add a backend by implementing `run(case, directory) -> AnalysisResult`. Reject
unsupported case features explicitly. Add a numerical benchmark before exposing
a new analysis type; keep solver keywords out of object scripts. Future joint
networks and material laws should extend the case contract only when a concrete
model needs them. The [local numerical fixture](experiments/ipc/fixtures/rounded_snap/README.md)
exercises rounded contact-driven pass-over and reopening with mesh/contact/increment sensitivity;
its numerical result is conditional on frictionless elastic solids and a locally
clamped root. Sharp-tooth pass-over remains unqualified: the phone-stand
experiment did not converge, and its failed result is retained with that model.
The current process isolation targets POSIX hosts.

`physical_analysis.screening.rectangular_cantilever` provides a cheap beam and
buckling rejection screen before meshing. `physical_analysis.studies.compare_results`
compares named metrics from already completed runs without launching new solves.
Convergence of force does not imply convergence of a local strain concentration.

### Friction-only retention screen

`physical_analysis.screening.elastic_friction_grip(interference_mm=...,
contact_count=..., stiffness_N_mm=None, friction_coefficient=None,
required_retention_N=None)` rejects an elastic friction-only grip with no preload
before meshing or printing. Signed interference is measured in the contact normal
direction: a negative value is a gap. With no external normal load or other
retainer, zero/negative interference gives zero designed friction capacity even
when material stiffness or friction is unknown. Positive interference reports
required travel; unknown force remains `None`, never a successful force rating.
Supplying stiffness and friction gives a conditional Coulomb capacity, not a
complete wedge/cam release prediction or a measured printed holding force.
Supply effective interference after assembly closure and settling, not just in
an initial gapped pose. The I consumer rejects both absent preload and seam
closure that would consume its weakest key's preload before export.

The [H swatch sample](../model/filament_swatch_box_study/README.md#physical-history-and-print-status)
was physically rejected after a clearanced rigid key fell out. The new screen
rejects that design without blaming printer accuracy; the replacement-key check
uses actual pad/pocket interference. Its purpose is to catch a missing retention
load path, not replace CAD contacts, a needed nonlinear solve or tactile testing.

### Sliced manufacturing paths

For a mechanical assumption that depends on actual sliced solidity or support
placement, `physical_analysis.manufacturing.orca_linear_paths(path)` yields
linear deposited segments with Orca's width/role metadata for consequential
local feature reviews. It requires
absolute XYZ, relative E and linear layer moves; incompatible modes fail.
The default record is `(x0,y0,x1,y1,z1,width,role)` for planar section tools.
Use `orca_linear_paths(path, spatial=True)` for
`(x0,y0,z0,x1,y1,z1,width,role)` on rising paths. The start Z includes preceding
non-deposited travel; inferring it from the last deposited endpoint can be wrong.
Spatial records must not be passed to the planar `section_coverage` API.
The [V1 swatch hood](../model/filament_swatch_box_study/README.md#v1-single-wall-vase-hood--additional-transparency-trial)
uses exact segment heights to measure its helical mating wall at each catch.
Keep geometry registration, section choices, support access and decisions with
the object. This does not replace Orca's layout acceptance, predict polymer
properties or justify routine G-code inspection of ordinary walls.

For a consequential local fill question,
`section_coverage(paths, x_mm=..., z_mm=..., span_mm=(y0,y1))` clips and unions
the recorded-width extrusion strokes on one Y section, excluding support and
brim roles. It returns filled/uncovered widths, internal gaps and intervals.
The planar capsule approximation includes parallel segments and finite rounded
ends; it does not measure deposited polymer. Select consequential sections and
interpret them in the object, without inferring modulus, isotropy or bonding.

`physical_analysis.screening.circular_cam_detent` screens two rigid circular
profiles against a linear transverse spring, returning pass-over travel and peak
frictionless sliding force from an explicitly supplied stiffness. This can
help interpret increment-sensitive reaction forces in rounded contact benchmarks.
It omits head rotation, spring-axis shortening, guide compliance and friction; stiffness
and printed material properties require separate assumptions/evidence. An
independent sampled-angle projection qualifies the analytical maximum. It does
not replace nonlinear contact analysis when those interactions matter.
