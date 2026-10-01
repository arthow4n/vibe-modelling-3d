# IPC investigation checkpoint

Paused at the user's request on 2026-10-01. This is an unfinished investigation,
not a qualified snap backend. The optional external CLI adapter and useful
diagnostics are retained without changing `SnapFitQuestion` or its CalculiX
default. No printed geometry, material assumption or operation was redesigned.
See the [adapter contract](../../backends/polyfem.md), [generated run summary](summary.json)
and [exact stopped command/settings](checkpoint-run.md).

The subsequent [thread-only performance phase](performance/README.md) qualifies
an automatic eight-thread preference on this machine: the bounded sliding prefix
is 1.50× faster with materially equivalent results and clean independent mesh
witnesses. It stops before the crest. Linear-solver, tolerance and crest diagnosis
remain deferred; the investigation is paused again at the user's request.

The corrected double-precision route completes open-gap, compression, SI mapping,
activation-distance control and separation/return tests. The open case has only
roundoff reaction; compression agrees with the SaintVenant analytical reaction
11.9550375 N (12 N small-strain approximation). Independent accepted-state mesh
witnesses agree with clean native contact on these cases. Native quasi-static
arguments and zero inertia fields establish absence of inertial loading; motion
continuation sensitivity remains a separate issue.

The contact-driven beam completes and elastically returns. Its .8/.5 mm P1 meshes
give 0.560/0.428 N and 0.280/0.242% Green strain. The shared
[20% comparison](beam_comparison.json) rejects force precision (30.6% change),
while strain changes 16.0%. Both remain in the expected bending regime with clean
independent triangle witnesses. The refined 24,873-element, 20-step cycle took
1,258 s versus 220 s for 6,467 elements. Its earlier 1,200 s timeout occurred on
unloading after useful peak evidence. Logs localize the cost to contact/boundary
feasibility and nonlinear solves, rather than dynamic time integration. Continuing
that identical mesh to completion answered return; further beam refinement is
not justified for the current coupling/order qualification question.

Sliding remains unqualified. The corrected .7 mm deformable/.3 mm obstacle scene
fails with .4 mm cam steps at progress .125; .1 mm steps reach .24375, then fail
at the .25 crest. Accepted states reach 0.547 N and 0.945% strain, broadly comparable
to the retained CalculiX light-detent result, but do not establish passage or
return. Projected Newton fails earlier; a weaker boundary-penalty control also
fails. A bounded intermediate AL search was interrupted at the user's checkpoint
request, with accepted states only through .2. See the
[model-owned investigation](../../../model/filament_swatch_box/notes/ipc-investigation.md).
The smallest identified numerical issue is near-contact boundary-feasibility /
Newton convergence: trial clearances collapse to approximately 1e-12 mm and
gradients remain far above the requested tolerance. This is not evidence of
physical blockage, and the bounded search has not resolved it.

An early conversion defect was caught independently: MEDIT version 1 converted
ASCII coordinates to float32, shifting sliding nodes by up to 2.1e-6 mm. Supplied
mesh and actual native mesh witnesses disagreed. Version 2 fixes that adapter
defect and fresh witnesses agree. Version-1 archives remain historical and are
unqualified for comparisons at smaller contact gaps. Sampled exact-CAD comparison
also sees about .0034 mm intrusion between rounded-cam collision facets; this
distinct tessellation uncertainty remains unresolved. No global exact-CAD or
continuous-path nonintersection proof is claimed.

| Route | Specific demonstrated evidence | Current limit |
| --- | --- | --- |
| CalculiX | Existing sliding passage/return; roughly .4–.6 N and 1.08–1.13% strain | Exact force is increment-sensitive; lift-off finite-edge contact remains rejected |
| FEBio experimental | Existing contact benchmarks and actual isolated lift release | Native near-clean gaps disagreed with independent approximately .039 mm finite-edge overlap |
| IPC experimental | Corrected gap/compression/return and contact-driven beam; independent all-triangle witnesses | No complete sliding passage; no lift-off solve started |

**Decision at checkpoint:** IPC has not yet solved the motivating physical
question. Sliding has not been reproduced as a complete IPC operation. Lift-off
remains **unresolved and untested by IPC**, because the earlier sliding rung has
not qualified. Keep this route isolated for investigation; do not promote it or
make ordinary model authors choose solver ecosystems. Independent numerical mesh
inspection agrees on corrected accepted states, while sampled exact-CAD evidence
still requires obstacle-tessellation sensitivity. Printed fit, friction, layer
bonding, material response/recovery, creep and wear remain separate uncertainties.

Any resumed study should first target the saved sliding crest/convergence issue
on the frozen mesh with a bounded diagnostic, not launch a finer full cycle by
default. Only after credible sliding qualification should the existing isolated
lift release be attempted; the complete lift sequence comes later. No new run
is authorized by this checkpoint record itself.

Provenance and replay inputs live in each retained directory; large raw VTUs
remain in the original external `/tmp` runs and are omitted from Git. The native
executable is external and [identified here](native_identity.json). Historical
archives preserve their original backend hashes and outcomes. Earlier runs lack
some package-version fields added later. Native tests are opt-in; skipping them
does not qualify the route. Final checkpoint checks are recorded in the commit
handoff; this record does not pre-claim a push.

This analysis-only phase adds no printable deliverables or physical observations.
Historical object print status and attribution remain unchanged. Investigation
attribution: primary GPT-6 family (exact runtime variant and reasoning effort not
exposed), Codex harness; provider metadata not separately exposed. No subagents.
