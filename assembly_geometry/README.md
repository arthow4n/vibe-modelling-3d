# Assembly geometry

Native CadQuery assemblies, stable configurations, explicit geometric
requirements and sampled rigid movement. Units are mm, mm³ and degrees. Geometry
builders remain in each object. There is no second component tree, constraint
solver, scheduler, persistent result cache or export pipeline.

This is the recommended representation for applicable new or substantially
revised multipart engineering, with an explicit opt-out. The design skill owns
[when to use it and when to opt out](../.codex/skills/cadquery-3d-design/references/parametric-and-edges.md#assembly-representation).
Ordinary shapes/direct functions remain appropriate for simple one-off geometry;
`check_pair()` also accepts Shapes/Workplanes without an assembly. Recommendation
does not imply complete engineering coverage or physical qualification.

## Public interface

Build a **native `cq.Assembly`** with explicit names and locations:

```python
import cadquery as cq
from assembly_geometry import Configuration, PairRequirement, sample_motion

part = cq.Workplane().box(2, 2, 2)
a = (cq.Assembly(name='fixture').add(part, name='fixed')
     .add(part, name='moving', loc=cq.Location((4, 0, 0))))
pose = Configuration.explicit(a, name='released', parameters={'travel_mm': 4})
answer = pose.check('moving', 'fixed', PairRequirement(
    'Release needs at least 1 mm separation', min_gap_mm=1))
answer.require_passed()
print(answer.to_dict())
```

`Configuration.explicit(assembly, name=..., kind=..., parameters=...)` captures
geometry/placements. `kind` is `operating`, `intermediate` or `print`; scalar
parameters describe the operating inputs, **not** a cache identity. Calling the
object's factory with new parameters creates a new snapshot; old ones stay stable.
Named configurations are ordinary object-owned Python functions, not another
registry or generic joint system.

- `names`: exact root-relative geometry paths; a geometric root uses its own name.
- `shape('subassembly/part')`: positioned Shape copy, including all ancestor/root
  locations and any placement already authored in the component geometry.
- `location(path)`: native accumulated placement copy relative to the author's
  geometry frame; it is not a component centroid.
- `assembly()`: independent native assembly copy for the existing evaluator.
- `check(first, second, requirement)`: component/configuration-aware pair result.

Repeated native instances can share one component definition. Hierarchy paths
stay distinct even when leaf names repeat; short-name lookup never guesses.
Grouping nodes are not substituted with geometry. Empty/invalid geometry,
unlabelled UUID nodes, duplicate siblings and incorrect paths are rejected.
Workplanes cannot silently discard vectors or other non-shape entries.
Check methods do not move the snapshot or the original assembly. Returned shape
copies isolate external placement changes from later questions.

Existing builder functions sometimes bake placement into geometry. Keep using
those functions. `rigid_location(lambda frame: posed(frame, ...))` adapts an
existing rigid Workplane transformation to native Location using four ordered
datum vertices. It rejects scale, shear/reflection and dropped entries. The 1e-9
basis arithmetic check qualifies that transformation only; it is not a universal
clearance tolerance. Geometry-dependent bed placement stays with the real part's
existing builder. New models can simply author `cq.Location` directly.

## Native constraint resolution

Use native `assembly.constrain(...)`, then:

```python
from assembly_geometry import solve, constrain

constrained = (cq.Assembly(name='seating').add(part, name='base')
               .add(part, name='cap', loc=cq.Location((6, 1, 0))))
constrained.constrain('base', 'Fixed')
constrain(constrained, 'base@faces@>Z', 'Point', second='cap@faces@<Z')
constrained.constrain('cap', 'FixedRotation', (0, 0, 0))
resolution = solve(constrained, name='seated', position_tolerance_mm=1e-6,
                   rotation_tolerance_deg=1e-4)
seated = resolution.require_configuration()
```

The qualified policy is deliberately narrow: **flat assemblies**, explicit `Fixed`
anchors, `FixedRotation` orientations, and `FixedPoint` or zero-distance `Point`
connections that connect every translation to an anchor/absolute point. A geometric
root is locked by CadQuery itself. Solve root placement must be identity. Point
constraints use native selected geometry centres. `constrain(assembly, first,
kind, second=..., param=...)` uses native selectors and rejects empty/multiple
matches before declaring the native constraint. Explicit datum-shape overloads
can use `Assembly.constrain` directly. Native selectors themselves use their first
match; this adapter cannot recover selector provenance from already declared
native constraints. Use the strict helper for selector-based declarations.

This graph policy establishes unique rigid poses for the supported relationships;
it does not solve them. **CadQuery's actual `Assembly.solve()`** (CasADi/IPOPT)
calculates them on a separate candidate. Input locations are initial guesses,
never fallback outputs. A mixed configuration must constrain its explicit fixed
parts with `Fixed`. Direct explicit snapshots reject any constraint declarations.

Native success alone is insufficient. Independent world-coordinate centre
residuals (mm) and quaternion orientation residuals (degrees) must meet the
caller's tolerances. The returned configuration contains only solved placements;
there is no competing expected-placement table. Native status, iteration count,
normalized objective and individual residuals remain in `Resolution` and
`configuration.resolution`. Objective value is not a physical residual/tolerance.

`Resolution.status` is `resolved`, `invalid`, `unsupported`, `inconclusive`,
`failed` or `residual_failed`. Only `resolved` carries a configuration.
Missing declarations/references fail; free orientations/translations and implicit
first-entity anchoring are inconclusive. Unsupported native constraint families,
nonzero Point distance branches and nested solves are not silently accepted.
Native exceptions/failure statuses and successful least-squares compromises are
preserved. Native solving must run under the ordinary execution resource budget.

Use native CadQuery directly to investigate other networks; their fully
constrained determinacy, residual interpretation and solution branches are not
qualified by this package. No general DOF-rank estimator, constraint solver or
automatic kinematics is claimed. A unique calculated pose still needs explicit
mechanical questions to establish seating, engagement, clearance and reachability.

## Pair intent and sampled paths

`PairRequirement(intent, max_overlap_mm3=..., min_overlap_mm3=...,
min_gap_mm=..., max_gap_mm=...)` supplies only the relevant criteria:

| Question | Criteria |
| --- | --- |
| Forbidden interference, contact permitted | maximum overlap volume |
| Required retention obstruction | minimum overlap volume |
| Positive separation | minimum unsigned gap |
| Required seating without penetration | maximum gap **and** maximum overlap |

Limits are inclusive and finite/nonnegative, with no default CAD tolerance. State
why the product uses its threshold. Contradictory limits are rejected. Volume
criteria require solid-bearing geometry; gap-only checks also support faces.
This package reuses CadQuery's intersection and OpenCascade's distance algorithm;
it does not implement geometric collision algorithms or infer product intent.
Only requested measurements run: a volume-only sweep does not calculate distance.

Results preserve identities, intent/criteria, numerical measurements, execution
completion, `passed`/`failed`/`inconclusive`, kernel error text and scope limits.
Unsigned distance is zero for both touch and penetration; overlap volume cannot
establish positive clearance. Gap questions retain a kernel distance witness pair
when available. These points are not a contact patch, penetration depth, force or
invented collision location. Invalid booleans, failed distances and nonfinite
measurements cannot become a zero measurement or a passing result.

```python
path = sample_motion(pose, 'moving', 'fixed', PairRequirement(
    'Specified rigid withdrawal clears obstacle', max_overlap_mm3=1e-8),
    samples=(0, 1, 2), transform=lambda t: cq.Location((t, 0, 0)),
    parameter='withdrawal', units='mm')
print(path.to_dict())
```

`transform(t)` supplies a **world-frame delta** applied to the snapshot's moving
component; the obstacle stays fixed. Native Location multiplication composes
rotation and translation. Name the axis/origin/direction in the product function;
no extra numerical solve is needed for deterministic motion. Strictly increasing
samples state the checked coverage. Results retain every requested pose/sample,
first unsuccessful parameter, largest sampled overlap and smallest sampled gap
when requested. A single attempted pull can also express required obstruction.

Sampled success means only that the criteria hold at those poses. Endpoints can
miss an intermediate collision, as the reference test deliberately demonstrates.
No adaptive/continuous guarantee, swept-volume bound, general insertion planner,
multiple-body coupling, dynamic simulation or elastic motion is implemented.
Rigid overlap does not establish force, friction, fatigue, recoverability or
printed fit. Transform callback/declaration errors raise instead of pretending
the requested movement was checked.

## Existing consumers and integration

Executable inspection/verification entry points:

```sh
./execute.py --threads 1 model/sunglasses_case/assembly_checks.py
./execute.py --threads 1 model/book_reading_plate/assembly_checks.py
./execute.py --threads 1 model/vaseline_container/assembly_checks.py
./execute.py --threads 2 model/filament_swatch_box_study/check_quiet_assembly.py --variant q1f
./evaluate_model.py model/book_reading_plate/assembly_checks.py
./execute.py --threads 2 assembly_geometry/experiments/qualify.py
./execute.py --threads 1 assembly_geometry/experiments/native_probe.py
```

The first three product inspection entries leave production checkers and accepted
exports untouched and print diagnostics without writing product evidence. The
quiet-swatch migration updates its engineering checker/inspection code and saves
native evidence in the object's existing reports. All four reuse authoritative
builders, original placements and object-owned thresholds; accepted print exports
remain unchanged. Evaluator entry uses native
`result = configuration.assembly()`.

| Consumer | Demonstrated improvement |
| --- | --- |
| Sunglasses case | Named body/lid/keeper; original hinge transform; closed and print configurations; 37 shell-only hinge poses; explicit rotational retention obstruction and prescribed released-loop lift. Reports clarify that shell motion excludes elastic loop behavior. |
| Book plate | One screw definition/four instances at original stations; assembled vs three print jobs; required contact on four selected seating-ring patches alongside forbidden solid overlap. Optional native resolution starts screws displaced, checks mm/degree residuals and reproduces original poses. A width/height candidate uses the same checks. |
| Vaseline jar | Named closed/opened/print pair; 37 poses of coupled helical withdrawal; separate required axial obstruction. Same interface transfers without a thread/joint class. |
| [Quiet swatch Q1/Q1F](../model/filament_swatch_box_study/README.md#named-assembly-engineering-2026-10-06) | Shared actual parts for checks and inspection; closed/loaded/opened, separate print jobs and mixed rows at both ends. Required floor contact uses a crop of the actual base. Wrong hood placement, absent retention beads and a floating card are rejected. Local bead masks and independent TPU access envelopes retain their explicit scope. |

At initial qualification, the phone stand, glove insert and original swatch
storage checkers informed scope without migration: they use selected rigid pairs,
two moving frames, prescribed elastic
release approximations and local source-card seating checks. A general all-pairs
checker would incorrectly flag deliberate retention overlaps. Glove coupling can
remain in its object-owned function; elastic interfaces belong to explicit
physical questions. The swatch K reflected-reference failure is already documented
by its original checker; shared kernel measurements cannot correct a bad reference
item. No new historical product failure was found in the three qualified products.

The existing evaluator deliberately converts native assemblies to compound
geometry for validation/render/export. Keep named snapshots in inspection scripts
before that selection boundary. No evaluator representation change or alternate
artifact pipeline is needed. Established print files are not re-exported/sliced
for this infrastructure task; explicit print snapshots compare against the
original layouts, and regression tests fingerprint accepted export bytes.

`configuration.shape(name)` is an ordinary positioned CadQuery Shape. Pass it
straight to `StructuralQuestion`, `FlexureQuestion`, `SnapFitQuestion` mates,
`ContactQuestion` bodies or `AnalysisCase.add_part`, with explicit material,
regions, supports and loads. All physical regions are in the resulting assembly
frame. Constraints never infer physical supports or contacts. Qualification
constructs `StructuralQuestion`/`QuestionStudy` fixtures from real positioned
plate geometry; it launches no new native physical solver and makes no load claim.
The existing question/study identity and execution contracts remain authoritative.

Ordinary parameter studies call the object factory, capture the candidate and run
the same questions. No new numerical study API, scheduler or result cache is
required. Expensive independent work uses `execute.py`; evaluator managed outputs
retain existing identity/publication/reuse safeguards. Do not mutate Python during
CAD publication. This implementation claims diagnostic consistency and preserved
placements, **not** a measured runtime improvement. Snapshot copies add work; the
reliable baseline is direct CadQuery for simple scripts.

## Remaining gaps and extension decisions

Assessment, 2026-10-06: **keep the API and recommend it within the scope above**.
The [Q1/Q1F trial](../model/filament_swatch_box_study/README.md#named-assembly-engineering-2026-10-06)
demonstrates useful shared component/pose identity, explicit required contact and
obstruction, and diagnostic failures while preserving accepted print geometry.
It does not demonstrate an implementation defect requiring an API redesign.
The justified change now is earlier skill routing and a clear opt-out. The
following distinctions keep future improvements tied to actual engineering needs.

| Observed issue or unsupported question | Current route and smallest justified next direction |
| --- | --- |
| **Coverage and reference choice remain manual.** Q1/Q1F needed actual base material for its floor witness and valid local bead-mask Booleans. Native measurements cannot detect an omitted requirement or correct a reflected source item. | Keep requirements, actual references and meaningful negative cases object-owned. Do not add an automatic all-pairs checker: intentional retention overlap makes it misleading. A future requirement-group/report helper would need to preserve declared intent and exclusions; it would not prove completeness. No missing shared operation was demonstrated here. |
| **Analysis subsets and elastic proxies need local code.** Q1/Q1F uses a bead-free insert and separately expanded TPU access envelopes; representing these as physical parts would misstate the assembly. | Its small object-owned `fixture()` handles this adequately. Keep proxy provenance and omissions in the requirement/object record. The rigid API cannot establish TPU installation strain, force, friction, recovery, wear or quietness; use physical questions or representative prints for those decisions. A generic flexible-component layer is not justified by this trial. |
| **One moving body against one fixed obstacle.** `sample_motion()` applies a world-frame delta. The earlier glove checker has two moving frames; Q1/Q1F does not require that capability. | Keep the glove's explicit local coupling. If sharing that operation becomes useful, consider a configuration-sequence query taking an object-owned pose factory plus named pair requirements, retaining both bodies' poses at each sample. Qualify on that consumer before adding it; do not introduce a joint solver. Adaptive/continuous coverage would be a separate contract. |
| **Constraint resolution is narrow and version-sensitive.** Supported flat rigid networks are qualified; arbitrary nested constraints, free DOFs and solution branches are not. Native private copy/query/solver details are tied to CadQuery 2.7.0. | Use explicit configurations for prescribed poses. Extend solving only for a concrete network with determinacy, residual and branch evidence; retain failure statuses. Requalify the existing fixtures on dependency changes. Broadening selectors or solve acceptance without that evidence would weaken the API. |
| **Verbose retained reports.** Q1/Q1F reports contain 16,835/18,885 lines (563,841/629,308 bytes), including per-sample results/poses and qualification evidence. `MotionResult.to_dict()` retains the full trace; `require_passed()` raises that dictionary on failure. | The consumer already prints a compact console summary and keeps the full evidence once. If a diagnostic reader needs bounded output, consider additive `MotionResult.to_summary_dict()` containing completion/status, sample count/range, first unsuccessful result, sampled extrema and limits, while leaving `to_dict()` unchanged. Do not drop inconclusive samples or imply continuous success. No implementation change now: the current summary is adequate and deleting trace data would lose evidence. |
| **Invalid Boolean identity comparisons got in the way of migration qualification.** Whole-scene subtraction and coincident-card subtraction failed in the local Q1/Q1F regression method, outside the pair-query API. | Reject invalid calculations. Compare the intended component set and individual parts; for rigid source-card placement, native locations and transformed source datums answered the question. This is a kernel/comparison-method limit, not a demonstrated API bug or a general geometry-equality proof. A universal Boolean equivalence helper would repeat the failure; no such extension is proposed. |

The API organizes declared evidence; it does not select good product architecture,
discover assembly order, infer physical supports, or replace independent source
references. Snapshot copies also add work, without a measured speed benefit.
Existing physical-analysis, evaluator and execution contracts continue to own
their respective questions and publication boundaries.

No API format or implementation change is needed for the demonstrated swatch
questions. The additive summary and configuration-sequence interfaces above are
proposals, not implemented capabilities or promises. Revisit them when the named
consumer has a decision or repeated work they would improve. If a future consumer
requires mostly unsupported behavior and gains little identity/diagnostic value,
opt out rather than expand the abstraction to fit it. Removing the package would
require a separate decision and preservation of its useful engineering checks;
the present evidence supports keeping it.

## Qualification and limitations

Qualified 2026-10-05 with Python 3.12.14/CadQuery 2.7.0: the admitted
`qualify.py` run passed **30 tests**, including all three product regressions,
local seating patches and the resized plate candidate. Existing evaluator and
rigid-driver regressions passed **33 tests** with
`ENGINEERING_INSTANCE=assembly-evaluator-qualification uv run --locked pytest -q tests/test_evaluate_model.py tests/test_rigid_motion.py`.
The separate instance follows the execution contract: the evaluator's
unavailable-storage test changes `ENGINEERING_DATA` and interrupted an earlier
shared-instance run; both unfinished suites were rerun rather than promoted to
completion. All three new inspection entries passed final managed CAD evaluation.
A resolved box-seat fixture also passed managed STEP/STL export and front render;
the image was inspected. Product export fingerprints remained unchanged. No new
print or physical solver run was needed.

The installed version is CadQuery **2.7.0**. Native API/source references:
[assembly documentation](https://cadquery.readthedocs.io/en/stable/assy.html),
[2.7 assembly implementation](https://github.com/CadQuery/cadquery/blob/2.7.0/cadquery/assembly.py),
[2.7 solver implementation](https://github.com/CadQuery/cadquery/blob/2.7.0/cadquery/occ_impl/solver.py).
The adapter isolates version-sensitive details: `_copy()` drops constraints and
full descendant lookup paths, `_flatten()` rebuilds the native lookup index, native
query grammar supports strict selections, and `_solve_result` contains statistics/Opti. Tests qualify their current
behavior; future dependency upgrades need the same fixtures.

`native_probe.py` established that a Point/FixedRotation seat converges from a
6/1/0 initial translation, and changing cube size from 2 to 4 moves the solution
from Z=2 to Z=4. An inconsistent target still reports `Solve_Succeeded` with a
4 mm face residual and objective approximately 0.41558. A plane-only arrangement
reports acceptable convergence while leaving approximately -112.85° yaw from
that initialization. These are native least-squares/underconstraint limitations,
not product failures. The adapter rejects unqualified freedom and inconsistent
residuals rather than treating solver termination as mechanical success.

`tests/test_assembly_geometry.py` independently qualifies known box volumes/gaps,
touching and ±0.0001 mm signed clearances, required contact/obstruction, distance
witnesses, hierarchy/root transforms, repeated identities, stable snapshots,
missing/malformed inputs, solver failure diagnostics, independent residuals,
parameter changes, rotation obstruction, and coarse motion missing an intermediate
collision. Product regressions independently compare original transformed
geometry/layouts and check established artifact bytes. Their cut-volume comparison
thresholds are the original product's engineering limits, not a universal kernel
accuracy estimate. CAD and physical-analysis compatibility are separately checked.

Successful kernel execution, supplied geometric acceptance, native numerical
qualification and physical product validity remain separate conclusions. Physical
success previously reported for the three products stays historical evidence
under its recorded conditions; this capability adds no print, force or durability
qualification.

Implementation attribution: GPT-6-based Codex (exact runtime model variant and
reasoning effort not exposed), Codex shared-workspace agent, OpenAI. No subagents.
Original product provenance and print records are unchanged.
