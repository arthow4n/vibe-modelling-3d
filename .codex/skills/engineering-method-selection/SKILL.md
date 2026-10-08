---
name: engineering-method-selection
description: Choose or reconsider engineering representations, analysis methods and solvers when the choice is consequential or uncertain, or an established method meets a meaningful limitation. Owns cross-method preferences and reusable selection lessons; clear CAD, analytical and specialist tasks can proceed directly.
---

# Engineering method selection

Use this skill at a consequential choice or limitation, not for every build,
measurement or print review. A clear, adequate method can go directly to its
specialist guidance. [Design](../cadquery-3d-design/SKILL.md) owns product purpose,
architecture and whether further evidence is worthwhile; this skill owns the
representation and method for the identified question. Specialist documents own
interfaces, operating assumptions, numerical diagnosis and qualification.

## Choose from the decision

Name the engineering question that could change the current design decision,
the decisive quantities and acceptable uncertainty. Identify the governing
geometry or physics: rigid motion or deformation, inertia, contact/friction,
material behavior, anatomy and boundary conditions. Prefer a representation that
retains the decisive behavior and produces interpretable evidence.

The recommendation is a preferred starting point, not an exclusive assignment.
Use it when it adequately represents the governing physics. Challenge it when
concrete limitations, evidence or problem characteristics justify a different
method. Do not preserve an inadequate approach because it is installed or
documented; do not routinely investigate alternatives when the established
approach already answers the question. One tool may rightly dominate a category.

Weigh engineering suitability and trustworthy evidence above implementation
convenience. Consider established domain models, initial integration, ongoing
maintenance, future reuse, total agent effort and compute cost. Ask whether added
fidelity could change the decision. An adequate analytical equation can beat a
full simulation; importing established MyoSim anatomy can justify more initial
work than handcrafted anatomy that omits important structure. Neither fewer
lines of code nor more solver complexity is a quality criterion. No ranking score
or routine comparison report is needed; consequential assumptions belong in the
existing product/study record.

## Preferred starting routes

These categories overlap. Recommendations select a method, not a claim that all
its capabilities are integrated or qualified here.

| Engineering question | Preferred representation/method and boundary |
| --- | --- |
| Exact shape, geometric fit, interference or dimensional clearance | CadQuery/OpenCASCADE on authoritative CAD, with targeted [geometric checks](../../../assembly_geometry/README.md#pair-intent-and-sampled-paths). Kernel results have stated tolerances; sampled poses do not prove a continuous path or printed fit. |
| Geometric mating and determined component placement | Native CadQuery assembly constraints. Read [constraint resolution](../../../assembly_geometry/README.md#native-constraint-resolution): the qualified adapter covers narrow determined rigid networks; placement constraints are not physical joints or supports. |
| Straightforward beam/load estimate | Appropriate analytical mechanics with justified section, loading, support and deformation assumptions. Use existing [load-path screens](../cadquery-3d-design/references/design-decisions.md#structural-load-paths-and-joint-screens); refine when omitted geometry/physics could change the answer. |
| Local structural stress, strain, deformation, stability or elastic contact | CalculiX, with Gmsh where meshing is required. Start with applicable [physical questions and studies](../../../physical_analysis/README.md#use); check formulation, material, mesh, loads and output suitability for the specific quantity. Stability modes and dynamic analyses are not automatically qualified by static bending tests. |
| Articulated mechanism motion under gravity, friction, springs, motors, impacts or control | MuJoCo with explicit bodies, joints, inertia, actuation and contact assumptions. Prefer mechanism dynamics here when local continuum response is not decisive; a joint spring/contact parameter is not a calibrated material law. |
| Articulated human reach or manipulation | Established MyoSim anatomy with MuJoCo and an appropriate kinematic/search formulation. Follow [human interaction](../articulated-human-interaction/SKILL.md); current qualification is product-local and kinematic, not physiological force or comfort. |
| Advanced nonlinear soft material, biological tissue or suitable coupled continuum behavior | Investigate FEBio against the required constitutive law/coupling and data. Its [upstream feature manual](https://febiosoftware.github.io/febio-feature-manual/) is broader than the repository's [experimental contact adapter](../../../physical_analysis/README.md#experimental-alternative-for-finite-edge-contact), which does not expose those material/coupling capabilities. Softness alone does not require FEBio. |
| Difficult deformable contact, nonintersection or surface passage | Consider PolyFEM/IPC when contact geometry is decisive. Read the [adapter limits](../../../physical_analysis/backends/polyfem.md) and [qualification checkpoint](../../../physical_analysis/experiments/ipc/README.md): generic contact/return tests exist, rounded crest passage remains unqualified. It is an investigation route, not an automatic replacement for ordinary elastic contact. |
| Optimization, inverse kinematics or design parameter search | Choose an optimizer for the actual mathematical formulation: variables, constraints, smoothness, derivatives, discrete choices and local/global search needs. SciPy bounded least squares suits the existing human residual search, not every constrained problem. Optimization searches a model; independently check feasibility and scoped acceptance. |
| Print-process feasibility or toolpath-specific behavior | Existing [manufacturing/slicer workflows](../cadquery-3d-design/references/print-planning.md), with [Orca inspection](../orca-slicer-printability/SKILL.md) when applicable. CAD or solid FEM alone does not establish actual deposited paths or printed material response. |

## Resolve consequential overlaps

- **Geometry versus motion models:** CAD is authoritative for nominal dimensions
  and exact-shape queries. Simulator collision proxies may close holes, omit
  rounding or change clearances. Check consequential proxy differences against
  CAD. CadQuery constraints resolve geometric placements; MuJoCo joints describe
  articulated motion and dynamics. Neither automatically supplies the other's
  relationships or physical qualification.
- **MuJoCo deformation versus structural FEM:** upstream MuJoCo has deformable
  flexes, including a continuum formulation, not only rigid bodies
  ([modeling documentation](https://mujoco.readthedocs.io/en/stable/modeling.html#deformable-objects)).
  Prefer structural FEM for local stress/strain, stability and constitutive
  questions; consider MuJoCo deformables when motion/contact coupling governs and
  its formulation, outputs and accuracy fit. Repository kinematic examples do
  not qualify deformable simulation.
- **Mechanism versus continuum dynamics:** prefer MuJoCo for articulated
  trajectories, control and interaction. CalculiX also supports modal/direct
  dynamics ([native manual](https://www.dhondt.de/ccx_2.21.pdf)); consider continuum
  dynamics when vibration, transient deformation or stress waves govern. Static
  repository interfaces/benchmarks do not qualify that capability. A problem with
  both effects may need a qualified reduction or combined analysis.
- **Contact formulations:** MuJoCo's [regularized contact model](https://mujoco.readthedocs.io/en/stable/computation/index.html#soft-contact-model)
  suits mechanism interaction, but numerical softness is not automatically local
  material deformation. CalculiX/FEBio continuum contact addresses local response
  under its selected enforcement/material assumptions. [IPC](https://ipc-sim.github.io/)
  targets intersection-free mesh contact; that does not establish exact-CAD
  clearance or qualify this adapter's passage. Choose by required gap, force,
  friction, deformation and path evidence, not the word “contact.”
- **Human kinematics versus tissue/force:** an established anatomical pose/path
  can answer modeled reach. Pressure, skin deformation, muscle strength and
  physiological effort need appropriate tissue or musculoskeletal models,
  parameters and qualification, often physical evidence. Keep established anatomy
  when changing the analysis; a reachable pose proves neither force capability,
  comfort nor real accessibility.
- **Analytical versus numerical:** equations are preferable when their assumptions
  bound the decisive quantity adequately. Move to numerical analysis for relevant
  section distortion, large deformation, contact, instability or coupled loading
  that invalidates those assumptions. A converged mesh cannot repair incorrect
  material or fixture assumptions.

## Distinguish capability from evidence

Keep three levels separate for the needed feature:

- **Upstream capability:** the library/solver supports it. Confirm consequential
  claims against official documentation and the actual version before relying on
  them; links above are starting references, not permanent feature guarantees.
- **Repository integration:** an interface or workflow exposes it. Inspect actual
  supported inputs and outputs; a narrow wrapper is not the solver's full scope.
- **Repository qualification:** relevant tests, examples and numerical evidence
  establish interpretation boundaries under stated conditions. Exposure, native
  completion and one successful example do not qualify all product applications.

Do not reject a suitable upstream method merely because its wrapper lacks the
feature. Investigate native APIs or make a justified object-local integration for
a real question, retaining the existing [execution/isolation contracts](../../../execution/README.md#architecture-contract-version-1)
and [implementation discipline](../coding-conventions/SKILL.md). Qualify the needed
behavior and interpretation before using it for a product conclusion. A new
capability does not by itself require a generic shared API; reusable extensions
follow [reflection](../engineering-reflection/SKILL.md#put-the-result-in-its-owning-source).

## Refine, switch, combine or remain inconclusive

Reconsider a default when decisive physics or anatomical structure is missing;
geometry proxies change the result; contact/friction or material assumptions are
inappropriate; numerical formulation/convergence is unsuitable; a more direct
qualified route avoids unnecessary approximation; or another upstream capability
improves suitability or lifecycle cost. For two genuinely suitable methods,
choose on required evidence, fidelity and total cost; compare only the unresolved
distinction that could change the decision.

Diagnose an unsuccessful solve using the specialist's failure guidance: fixture,
units, constraints, mesh/time/motion resolution, contact, outputs and numerical
controls as relevant. Nonconvergence alone proves neither product failure nor
another solver's superiority. Refine the current method for a correctable issue;
switch when a demonstrated representation/formulation limit matters. Do not
exhaust an unsuitable solver. Leave missing evidence UNKNOWN or an attempted
unresolved analysis INCONCLUSIVE rather than inventing a passing approximation.

Combine methods when each answers a distinct consequential question: authoritative
CAD geometry; structural FEM force–displacement behavior for a flexible component;
MuJoCo mechanism motion using a qualified reduction; detailed contact/material
analysis where that reduction fails. State transferred units, frames, loading,
material/rate assumptions, fitted range and omitted coupling, and check sensitivity
that could change the receiving model's answer. A fitted spring is not fully
coupled FEM dynamics; sampled simulator collision checks are not exact continuous
CAD nonintersection. Existing [product verification](../../../product_verification/README.md#composition-and-outcomes)
composes separately scoped evidence without promoting one question's success into
another's. No new coupling framework is implied.

## Improve recommendations from actual work

Through [engineering reflection](../engineering-reflection/SKILL.md), future agents
are authorized to revise this skill when concrete work establishes a better
default, demonstrated limitation, newly qualified capability, successful reusable
combination, removable solver step or decision boundary that caused incorrect
work/rework. Link the evidence and explain the transferable question class and
limits; do not turn one narrow success/failure into a universal recommendation.
Revisit defaults when experience or verified upstream developments change their
suitability. Agents can disagree for the present task before enough evidence
exists to change the shared default. Keep cross-tool lessons here, operational
lessons with the specialist and product-specific assumptions/results with the
product; improve the owning text rather than accumulate speculative features or
duplicate lesson records.
