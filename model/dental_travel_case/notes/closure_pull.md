# Lifting the box by its cap — force estimate, not a payload rating

This record concerns the original long research geometry. The later
[short, lower-material specimens](closure_short.md) preserve the interfaces but
change wall stiffness and supports; these force/weight estimates do not apply
to them.

The user asks how much force the four research closures can resist, expressed
also as an understandable hanging weight, before deciding whether to print them.
The earlier unit-radial-load studies did **not** answer this question. They measured
wall flexibility, with no axial pull or cap. This continuation estimates a slow,
straight pull for R1/R2 by combining actual CAD ramp geometry with both parts'
computed radial flexibility. No source geometry or printable specimen is changed.

[Drawing and force curves](closure_research/pull_estimate.svg) ·
[Structured results](closure_research/pull_estimate.json) ·
[Reproduction source](../closure_research_pull.py) ·
[Four concepts and current specimens](closure_research.md)

## Results and practical decision

**R1 is a light snap; R2 is materially firmer. Neither result establishes a safe
loaded-box lifting rating.** Nominal values below assume E1200 MPa, the current
fit, two independent engaged catches, frictionless straight withdrawal and the
declared bench supports. Equivalent mass includes the hanging body and contents.

| Concept | Slow straight-pull peak | Equivalent static mass | Suddenly let go from seated, ideal undamped energy threshold |
| --- | --- | --- | --- |
| R1 broad-wall tip snap | **2.64 N** | **269 g** | **0.924 N / 94 g** |
| R2 end-wall tip snap | **6.22 N** | **634 g** | **2.17 N / 222 g** |
| R3 perimeter bead | Not calculated: coupled rim/peel model missing | Unknown | Unknown |
| R4 sliding lid | Not calculated for perpendicular lifting: rail/lid model missing | Unknown | Unknown |

Across E900–1800 and ±0.15 mm extra radial gap, retaining both independent
catches, the slow-pull estimates span **1.37–5.19 N (139–529 g)** for R1 and
**3.22–12.22 N (328–1246 g)** for R2. The corresponding ideal undamped seated-release
thresholds span **35–239 g** and **81–563 g**. These are tested model scenarios,
not confidence intervals or guaranteed bounds on a print. Losing one catch
halves every force/energy result in this independent-spring model. Actual peel
can change stiffness, leverage and contact sequence, so it can be worse.

The full reference body's CAD solid volume is **119.36 cm³** for either snap.
For a purely illustrative solid density of 1.27 g/cm³ it alone would weigh about
**152 g**, before contents. This is not slicer-predicted or measured print mass.
It shows why the distinction matters: R1's nominal sudden-release energy threshold
is below even that illustrative empty body; R2's leaves only about 70 g for
contents in that ideal scenario. Conversely the slow-pull peaks could suggest
much larger payloads if the initial slack and energy barrier were ignored.
Neither subtraction is a recommended payload. Actual damping/friction could
improve the release behavior; rocking, fit changes or creep could worsen it.

R2's force/energy scale is **2.35× R1** under the same reduced assumptions.
Including cap flexibility lowers the body-only estimate by about **6% for R1**
and **11.5% for R2**. Maximum nominal spring energies are only **0.762 mJ** and
**1.794 mJ**. Meaningful geometric capture therefore coexists with a small energy
barrier. The quantitative decision is to keep R1/R2 as comparative research
samples, with R2 the more promising retention direction; do not adopt either as
a robust travel closure based on this calculation alone. No geometry was changed
and no physical acceptance is claimed. R3/R4 have not been rejected for low force:
their relevant force studies are simply absent.

## What the force means physically

Hold the cap without squeezing its sidewalls. Let the body and its contents hang
straight below it. Their combined weight pulls on the bumps, which must bend the
body walls inward and/or spread the cap outward to pass the short retaining lip.
The steepest rise in stored bending energy determines the frictionless peak
pulling force. Past the lip, the walls can recover into the runout recess.
The bump therefore gives a finite snap barrier; it is not a lock requiring a
separate release control. A slow centered pull can deliberately or accidentally
open it.

There are two distinct lifting situations. If the body is supported while the
cap takes up the slack and the load increases slowly, compare against the
**quasistatic peak force**. If the cap is already held and the fully seated body
is suddenly let go, the body can accelerate through the initial play before the
bumps climb the ramp. That motion supplies energy to cross the snap. A separate
ideal **undamped seated-release** calculation compares gravitational work `W*s`
with the spring-energy increase along the same path. Its threshold is the
maximum of `(U(s) − U(0))/s`. Above it, gravity can traverse the entire modeled
barrier without a turning point. This is an energy calculation, not a dynamic
contact simulation. It omits friction/damping and assumes both catches follow
the same straight path. Its much lower weight equivalent exposes sensitivity to
initial slack; it is neither a measured drop threshold nor a safe rating.

At standard gravity, 1 N corresponds to about **102 g**, and a 250 g hanging load
pulls with about **2.45 N**. This is a force conversion, not a prediction of safe
contents mass. Include the hanging body itself, and subtract its mass before
interpreting any remainder as contents. Acceleration or a jerk increases force;
one-sided pulling can start release at a lower total load. Friction may add
resistance but is not assumed as a dependable retention source.

## Numerical representation and its boundaries

The unchanged actual full reference CAD defines the positive-side bump and cap.
At each withdrawal position, take the central section through the bump and
receiver, retain the straight boundary segments, and calculate the minimum
radial separation needed to eliminate their interference. Extrema of the
piecewise-linear profile difference occur at vertices from either profile.
This avoids assuming that the nominal projection or a selected ramp angle is the
actual capture. At five positions per fit, independent 3D solid-intersection
bisections must agree within 0.001 mm. Enlarging the radial gap enough to remove
capture is a negative control with zero elastic holding force.

Reuse the retained mesh-checked actual-body 1 N radial study. Add new CalculiX
linear elastic cap solves: 1 N outward on the inner retaining lip, complete roof
plane fixed. The cap is deformable, including its pocket and runout; it is not a
rigid receiver. The body crop remains clamped 16 mm below the seam. These represent
repeatable bench supports, not a hand or a full-height hanging body. Uniform
tractions idealize the migrating contact patch. The body load remains on its
crest; the cap load is spread over the lip. The model omits axial traction and
contact-pressure redistribution. Mean patch displacement approximates spring
compliance; patch displacement extrema are retained to expose nonuniformity.

For one catch, the radial compliances add: `C = C_body + C_cap`. For the geometric
radial clearance requirement `d(s)`, the approximate elastic energy is
`U(s) = d(s)^2 / (2 C)`. Two independent identical catches double that energy;
the axial force is its derivative with respect to cap lift. This is a reduced
frictionless spring/ramp simulation, **not a coupled assembly-contact solve**.
Cross-coupling between opposite walls, rocking, contact migration and localized
edge yielding are unresolved. The one-catch scenario simply halves this model's
energy and force; it is not a simulation or lower bound for actual peeling.

Use the same uncalibrated isotropic PETG hypothesis as the body study:
E = 1200 MPa, Poisson ratio .38; scale E over 900–1800 MPa. This is a declared
sensitivity range, not a measured distribution covering all printed anisotropy.
Change local radial fit by −0.15, 0 and +0.15 mm; this rigid receiver offset changes
capture but does not rebuild wall thickness or stiffness. It is a local fit
sensitivity, not a complete manufacturing tolerance model. No friction, creep,
wear, residual printing distortion or layer failure calibration is available.

Refine cap mesh target 2.5 → 1.75 mm, retain actual load areas, minimum quadratic
tetrahedron Jacobians and force balance, and compare patch displacement. The first
withdrawal comparison, 0.10 versus 0.05 mm, changed the nominal peak by 10.18%,
just outside the declared roughly 10% force-scale precision. Refine to **0.025
versus 0.0125 mm** over 0–6 mm: the nominal peak changes **4.62%**, below that
criterion; the nominal seated-release energy threshold is unchanged between
those grids. This is travel resolution of the reduced path, not native nonlinear
load increment convergence.
Numerical stability describes this reduced model, not its missing full-product
physics. Unit-load strain scaled to the maximum radial spring force is an
indicator only: the actual contact load distribution changes during passage.

| Refined cap study | R1 | R2 |
| --- | --- | --- |
| Body radial compliance, retained mesh study | 0.30738 mm/N | 0.12333 mm/N |
| Cap radial compliance | 0.02068 mm/N | 0.01602 mm/N |
| Cap compliance change on mesh refinement | 1.57% | 1.63% |
| Actual cap traction area | 20.945 mm² | 20.905 mm² |
| Quadratic tetrahedra / nodes | 63,227 / 125,555 | 62,544 / 124,659 |
| Minimum element Jacobian | 0.01334 | 0.01448 |
| Relative native force imbalance | 1.12e−7 | 6.66e−8 |

The body pad's radial displacement under 1 N varies 0.298–0.315 mm for R1 and
0.116–0.129 mm for R2; cap values vary 0.0177–0.0231 and 0.0135–0.0180 mm.
The mean-response spring ignores that nonuniform contact behavior. Nominal
linearly scaled peak strain indicators are body/cap **0.190% / 0.041%** for R1,
**0.371% / 0.095%** for R2. Sharp-corner peak strains are not mesh-qualified
strength predictions or recovery/fatigue evidence. The native logs identify
CalculiX 2.21; Gmsh 4.15.2 and CadQuery 2.8.0 are retained in provenance.

## Why the other variants do not receive inherited numbers

**R3 perimeter bead:** the entire rectangular rim bends together. Adding the two
local catch forces, multiplying by perimeter, or borrowing a circular snap-fit
formula would give an unsupported answer. Its force requires a distributed
rim/receiver deformation model that also allows one region to peel first. The
existing CAD interference and isolated wall-bending studies supply no such
stiffness. No numerical holding force is assigned in this continuation.

**R4 sliding lid:** lifting perpendicular to the broad lid loads the captured
rails, whereas pulling along the slide loads the small detents. Rail bending,
lid bowing and end peeling govern the lift question; detent ramp force does not
answer it. The existing wall study has neither a loaded lid nor rail contact.
A rail-lifting analysis is therefore still missing, and the 70 mm specimen cannot
qualify the full 264 mm lid. No hanging-load capacity is assigned.

This scoped adaptation answers the attainable R1/R2 force-scale question without
building another contact-solver framework. It leaves R3/R4 force coverage UNKNOWN
rather than presenting a radial bending response as holding force. Neither the
four specimens nor a new full box is physically accepted by this calculation.

## Reproduce and retained setup correction

```sh
./execute.py --threads 1 model/dental_travel_case/closure_research_pull.py run shell_broad NEW_NATIVE_DIRECTORY NEW_COMPACT_DIRECTORY
# Repeat for shell_end. Choose new destinations, never overwrite native evidence.
./execute.py --threads 1 model/dental_travel_case/closure_research_pull.py report
./execute.py model/dental_travel_case/verification.py --variant research-minimal-closures
```

The report consumes the canonical compact cap archives under
`closure_research/pull/{shell_broad,shell_end}` and checks their geometry/material/
fixture identities with `read_evidence`. Reproductions go to new directories;
comparison or deliberate replacement of canonical evidence is a separate action.
Existing body-source hashes must still match. The plot binds its source and input
record; changes to either invalidate verification. CAD, exports and slices remain
unchanged, so no new slice is warranted for this analysis-only continuation.

The first cap setup selected a 10 × 1.3 mm subpatch inside the lip. The coarse
surface mesh had no complete triangle wholly inside that box; both runs stopped
before solving with `Empty surface region`. The corrected selection spans the
10.6 mm lip width and its actual lower edge (z245.8–248.0), on the inner planar
wall. Failed setup inputs/logs remain in `pull/rejected_narrow_patch`. This is a
fixture-selection correction, not a physical failure or contact nonconvergence.

Self-review also caught the under-resolved first force peak and added the
seated-release energy scenario before interpreting equivalent grams. The final
section/curve PNG was inspected. **120 relevant tests passed**, covering the new
force/energy controls, actual profile/3D agreement, research evidence and shared
verification entry points. The refreshed research verification reports PASS for
the scoped R1/R2 proxy and existing CAD/flex/slice checks; R3/R4 force coverage and
physical holding remain UNKNOWN. This PASS does not approve a payload or a full
case. No sub-agents were used. Attribution and unprinted status remain as recorded
in the [current research record](closure_research.md).
