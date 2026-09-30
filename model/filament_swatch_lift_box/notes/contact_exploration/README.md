# Alternate contact exploration

The printable box, exports and print process are unchanged. This investigation
tests whether the previous release failure comes from the fixture, extraction,
numerical settings or contact formulation. It does **not** qualify the snap or
establish that the box is impossible. No physical print has been reported.

## Fixture and controlled comparisons

[analyze_release.py](../../analyze_release.py) isolates release from an unloaded
assembled state. Existing elastic closing results make that initial state a
useful diagnostic assumption; they do not prove successful closing. The actual
tab, cap window/catches and actuator remain the fixture. Only cap and actuator
motion is prescribed. Both obstacles form one contact master surface while
retaining independent motions; the flexible head is never driven directly.

The operation presses inward, lifts the cap 2 mm, withdraws the actuator, then
lifts another 10 mm and unloads. A maximum progress increment of 0.006 means
up to 0.2 mm travel during the final lift. Adaptive increments can be much
smaller; normalized time alone obscures that distinction. The shared progress
helper records actual recent travel without rerunning the solver.

The [generated results](results.md) and [summary](summary.json) are the current
run record. Native replay inputs, fixtures and logs are linked from each result.
Identical requested mesh size is not identical mesh: the summary records the
mesh-source hash. The controlled residual-tolerance trials reuse the exact mesh
of their corresponding earlier run. Failed/incomplete cases have no successful
whole-path force or strain predictions. Partial frames are diagnostics only.

## What the alternatives established

The isolated CalculiX surface-to-surface release completes but exceeds the
0.020 mm penetration screen. Its calculated forces, strain and elastic return
remain conditional diagnostic values, not an accepted mechanism rating.

The experimental CalculiX Mortar probe fails qualification before an object
study: [the known-gap diagnostic](mortar_onset.json) records a nonzero top force
while the block remains above the floor. Its native contact fields are in FRD,
outside the supported text extractor. The API therefore returns
`unsupported_output`, rather than silently treating missing contact fields as
zero penetration. This tested configuration is unqualified; it does not prove
that every Mortar configuration is unsuitable. The
[CalculiX manual](https://www.dhondt.de/ccx_2.21.pdf) prohibits repeated surfaces
across Mortar pairs, which motivated the reusable master-surface union.

The optional FEBio adapter tests frictionless sliding-elastic contact with
iteration-level projection updates, augmented Lagrangian enforcement and an
optional two-way projection. See the
[official formulation](https://febiosoftware.github.io/febio-feature-manual/features/solid_surfaceinteraction_sliding-elastic/).
Shared benchmarks establish known-gap onset, compression and separation,
contact-driven bending, force signs/balance, elastic return, independent obstacle
motion and peak Green-strain recovery. They also reject excessive overlap.
These benchmarks qualify the narrow adapter contract, not the box's edge path.

Both backends use an isotropic St Venant–Kirchhoff elastic assumption here.
FEBio uses eight volume quadrature points, compared with four in the current
CalculiX tetrahedron. Early failed FEBio run headers incorrectly described the
laws as different; those historical files are preserved, and that description
is corrected here and in the adapter. Native FEBio element principal strains
are means, so the shared layer recovers peak values at its native quadrature
points and checks the recovered means against native output. It does not use
element means as a peak-strain screen.

The default FEBio absolute free-DOF residual floor is 0.000001 N, squared for
the native parameter. It avoids chasing roundoff on an unloaded approach.
Controlled 0.001 N trials ask whether a decision-relevant residual accuracy
helps at extremely small adaptive increments. This is a numerical accuracy
choice; it cannot repair missed contact or calibrate the material.
The 0.001 N soft-contact trial passed its former actuator-withdrawal stall,
whereas the 0.001 N two-way trial still failed at the final-lift edge. This is
evidence that residual accuracy affects convergence effort, not that the path
is qualified. The [two-way trial's final saved witness](two_pass_tol001_contact_witness.json)
also separates its native gap from sampled geometric overlap.
The [soft 0.001 N trial's accepted frames](soft_tol001_contact_witness.json)
still show about 0.039 mm planar-native/CAD overlap during the final lift, versus
about 0.00023 mm native gap. It was deliberately stopped because this already
exceeds the geometric passage screen; completing later travel cannot undo an
earlier rejected passage. Its stop record states this reason explicitly.

## Contact fields do not bound geometric overlap

[The soft-contact saved-frame witness](soft_contact_witness.json) finds about
0.039 mm of tab-vertex overlap while FEBio reports about 0.00046 mm maximum
contact gap. Projection of that vertex lies inside an exactly planar native
master triangle, at the same signed depth as the CAD face. Thus curved-master
tessellation does not explain this particular witness. It is still not the
solver's matched projection point or a global intersection calculation.

[The strict two-way saved frame](two_pass_contact_witness.json) has much smaller
sampled overlap, but that run still fails to complete. Penalty and projection
direction both differ from the soft run, so their difference cannot isolate
the effect of two-way projection. The shared diagnostic samples every selected
slave face, including faces with no active native projection, and preserves the
worst geometry witness separately from the native gap.

The one-way strict-penalty trial was deliberately stopped after many tiny
accepted increments at the final-lift edge. Its retained stop record distinguishes
investigation backoff from a native convergence-limit failure. Increasing runtime
alone would not establish missed-contact quality.

Verification: the relevant analysis/evidence regression suite passed 29 tests.
After adding live-frame inspection, both one-way/two-way contact benchmark tests
passed again; the updated interruption/provenance regression also passed.
Documentation links and diff whitespace were checked. No geometry or slicing
was repeated because neither print geometry nor process changed.

## Decision and remaining work

No tested route yet provides a robust, sensitivity-qualified complete snap
operation. The unresolved requirement is contact passage through the finite
window/catch edges with acceptable geometric overlap, convergence and stable
forces/strains. Staging already exists. The investigation narrows the issue to
edge contact and acceptance, rather than a missing motion API or proof of an
impossible object. Rejoin and qualify closing plus release only after this
isolated transition passes; do not transfer partial-run force values to users.

The adapter, master union, identity-guarded saved-field recovery, progress
extraction and contact witnesses are reusable improvements driven by this
object. Further solver changes should start with these saved fixtures and a
specific failing transition, rather than another broad backend integration.
Explicit accepted frames can now be inspected using frozen run metadata before
the native solve terminates; this avoids waiting for a final result merely to
diagnose overlap. Such inspection never creates a completion claim.

Numerical uncertainty remains separate from the uncalibrated 1200 MPa isotropic
material and provisional 1.5% strain screen. No printed-layer bonding, friction,
plasticity, creep or fatigue is predicted. The complete box remains an unprinted
prototype; actual stack access, fit, force, support removal, recovery and wear
need the physical observations specified in the [object record](../../README.md).

## Reproduce and provenance

Use the root locked environment. For example:

```sh
uv run --locked python model/filament_swatch_lift_box/analyze_release.py /tmp/new_release --backend febio --two-pass --increment .006
uv run --locked python -m physical_analysis.progress /tmp/new_release
uv run --locked python model/filament_swatch_lift_box/summarize_contact_exploration.py
```

Use `--mesh-from ORIGINAL_RUN` to freeze the mesh for a numerical comparison;
the shared layer verifies its geometry and input identity. The native libraries
are installed outside the repository. FEBio 4.13.0.3ef378562 came from the
[official Linux archive](https://repo.febio.org/download/FEBio4.tar.gz), with
download SHA-256 `dc9fd41739f5d9e24357f8cf3d388808c21d63c5dda34cdd587fa76f34e01465`.
Actual executable/library hashes are in run provenance. No Python dependency,
CAD exports or slice profiles were changed. Existing CAD and slice evidence
remains applicable to the unchanged print files.

Investigation: GPT-6.1 Sol, high reasoning effort, user-provided attribution;
Codex workspace harness, provider not separately exposed, no subagents.
