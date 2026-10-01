# Experimental IPC evidence

The optional external CLI adapter and useful diagnostics remain isolated from
`SnapFitQuestion` selection and its CalculiX default. The three swatch-storage
products that motivated this work were rejected by the user and removed. The
sliding product was physically printed: its failure was whole-product architecture,
not evidence of a tolerance or process defect. Local solver checks answered narrower
questions. Git history through `d37763c` preserves those products and investigations.
No replacement design or crest investigation is part of this cleanup.

See the [adapter contract](../../backends/polyfem.md), [generated run summary](summary.json),
[minimal local rounded fixture](fixtures/rounded_snap/README.md) and
[thread-performance measurements](performance/README.md). The fixture is synthetic
numerical geometry derived from a failed product, with only an elastic leaf/root
and moving cam; no storage architecture is preserved.

The double-precision route completes open-gap, compression, SI mapping,
activation-distance controls and separation/return tests. Open-gap reaction is
roundoff; compression agrees with the SaintVenant reaction 11.9550375 N
(12 N small-strain approximation). Independent accepted-state mesh witnesses
agree with clean native contact. Native quasi-static arguments and zero inertia
fields establish absence of inertial loading; motion continuation sensitivity
remains separate.

The contact-driven beam completes and elastically returns. Its .8/.5 mm P1 meshes
give .560/.428 N and .280/.242% Green strain. The shared
[20% comparison](beam_comparison.json) rejects force precision (30.6% change),
while strain changes 16.0%. Both have recognizable bending and clean independent
triangle witnesses. The refined 24,873-element, 20-step cycle took 1,258 s versus
220 s for 6,467 elements. Its earlier timeout occurred on unloading; completing
the identical mesh answered return. These records qualify coupling/order, not
precise forces or a printed mechanism.

The retained rounded-fixture crest failure uses .7 mm deformable/.3 mm obstacle
meshes and .1 mm cam increments. Accepted states reach progress .24375,
.547 N and .945% strain; the next .25 crest step fails. Trial clearances collapse
to approximately 1e-12 mm and gradients remain far above the requested tolerance.
This localizes a near-contact boundary-feasibility/Newton convergence issue,
but does not distinguish the exact cause or establish physical blockage.
The tolerance/unit-scaling audit is still outstanding. Earlier alternative trials
and interrupted searches remain in Git history, not current product directories.

MEDIT version 1 shifted rounded-fixture rest nodes by up to 2.1e-6 mm through
float32 conversion. Independent supplied/native mesh witnesses disagreed.
Version 2 fixes that adapter defect; fresh witnesses agree. The retained
version-1 case is explicitly unqualified. Sampled CAD inspection also found
approximately .0034 mm intrusion between rounded-cam collision facets in earlier
states: this is a separate unresolved tessellation question. There is no global
exact-CAD or continuous-path nonintersection proof.

| Route | Specific numerical question answered | Limit |
| --- | --- | --- |
| CalculiX | Local rounded spring/cam passage and elastic return; approximately .4–.6 N and 1.08–1.13% strain | Force is increment-sensitive; these observations never validated the rejected product |
| FEBio experimental | Generic contact qualifications; historical isolated finite-edge release diagnosis | Native gap below .001 mm coexisted with approximately .039 mm planar geometric overlap; product scene is archived in Git, not a current fixture |
| IPC experimental | Gap/compression/return and contact-driven beam; accepted rounded prefix with independent triangle checks | No complete rounded crest passage; no lift-off solve was started |

**Current decision:** keep the narrow adapter optional for its contact qualification,
mesh-precision diagnostics and measured performance evidence. It has not supplied
a completed mechanism capability advantage and is not promoted to ordinary question
selection. The eight-thread bounded default remains justified on the measured
Ryzen 7 1700 workload: the contact prefix is 1.50× faster than one thread with
materially equivalent metrics and clean independent numerical meshes. Threading
alone justifies no long full-cycle run. No solver work was resumed for this cleanup.

Original outcomes, backend hashes and provenance remain unchanged in selected
archives; only index paths changed. Replay inputs are retained, while bulky raw
VTUs remain external `/tmp` artifacts and may no longer exist. The executable is
external and [identified here](native_identity.json). Earlier records lack some
later provenance fields. Native tests are opt-in; skipping them is no qualification.
Printed friction, bonding, material response, recovery, creep and wear remain
separate from numerical contact uncertainty. A physical product rejection is
stronger evidence about whole-product usefulness than any local numerical pass.

Historical investigation attribution: GPT-6 family (exact runtime variant and
reasoning effort not exposed), Codex harness; provider metadata not separately
exposed. No subagents. Historical records remain evidence of their tested scope.
