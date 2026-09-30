# Contact-failure diagnosis

This investigation keeps the printable geometry, material assumption, physical
path and quality limit unchanged. It asks whether a trustworthy operation can
be obtained by correcting the analysis, rather than treating failed checks as
proof of an impossible box. The [generated study table](../numerical_results.md)
and [stage summaries](../numerical_summary.json) remain the numerical source of
truth; [the diagnostic summary](summary.json) records input controls and locations.

Two mistakes were ours. The shared description called all contact finite sliding,
although CalculiX's surface-to-surface pairing stays fixed within each increment.
Also, the earlier tighter-contact study changed penalty and increment together.
It could not isolate their effects. We corrected the description and made new
fixed-penalty, fixed-mesh controls with 0.4, 0.2 and 0.1 mm maximum lid travel per
closing/final-lift increment. Their native decks differ only in the static
increment line, checked by `summarize_diagnosis.py`.

Remeshing unchanged snapshots with the same settings produced tiny node-position
differences, below 0.001 mm, despite unchanged connectivity and tool version.
The rerun coarse cycle reproduces the older coarse result closely; these small
differences do not explain away the failure. Guarded shared mesh reuse now makes
the controls exact and avoids reconstructing the mesh for each parameter change.

The fixed-mesh controls still fail contact quality. Strain and release response
are not stable with increment refinement; reducing travel does not monotonically
reduce reported penetration. The normal press/hold stage is comparatively stable,
consistent with the cheap beam stiffness screen. The unresolved question is the
head/pad passing the cap's catch and window edges, not whether a prescribed
cantilever can bend. Elastic return at the end does not qualify the intervening
contact or establish printed recovery.

The saved-field reports identify both sampled geometry inside the actual lid
and reported contact on faces whose samples are outside it. In the finer run's
worst release frame, samples really lie inside the lid, so the failure cannot
be discarded as merely a misleading field. At other transitions, native contact
gap and sampled CAD clearance disagree. These observations locate suspect
edge projection/pairing and mesh approximation; they do not prove a CalculiX
source-code defect. Actual contact quadrature locations and matched master faces
are absent from CDIS/CSTR, and ten face samples cannot bound every intersection.
Pressure/gap consistency and the real compression benchmark support the field
sign/order interpretation; duplicate element/face rows must be paired in output
order, not overwritten in a dictionary.

A separate fixed-mesh control excludes irrelevant outer cap faces from the
master contact region while keeping inner catches and the complete lower lead.
Its native input differs only in the lid master-face list. The conservative
head-Y bound in the generated summary checks outward reach against the region;
this is an analysis-selection experiment, not a modification of the container.
It also fails penetration quality and exceeds the provisional strain screen.
Removing those faces is therefore not a demonstrated fix; the ordinary analysis
keeps its original contact scope. Selection sensitivity reinforces the need to
resolve contact representation rather than claim confidence from one run.

The demonstrated limitation is unreliable edge-transition contact in this
tested quadratic-tetrahedron, penalty-contact fixture. This is not proof that
the mechanism is physically impossible, or that CalculiX cannot solve it with
another suitable setup. No operating-force rating or strain clearance is issued
from these failed cycles. Pairing/projection, surface approximation and
quasi-static equilibrium changes at snap transitions remain candidate causes;
these studies do not isolate one of them as the solver's root defect. The next
useful numerical experiment should isolate that edge/contact representation,
not repeat a whole operation with another unexplained settings combination.
A different contact formulation would need its own
qualification and geometry/path checks. Mortar is not an automatic cure: its
segmentation also updates per increment, and its restrictions prohibit reusing
the same slave surface in separate contact pairs, as this cap/pad fixture does
([CalculiX 2.21 manual, §§6.7.7 and 7.22](https://www.dhondt.de/ccx_2.21.pdf)).
That would require a deliberate contact-domain/staging change, not just a type
string or an unmotivated new backend.

The reusable work now lives in `physical_analysis`: saved-field contact location
and optional rigid-CAD comparison, guarded mesh reuse, accurate formulation
metadata, and backend identity captured before long solves. Native details stay
behind that layer. Object-specific selections, stage interpretation, control
comparisons and acceptance remain here. AGENTS.md now distinguishes fixture,
convergence, quality and design/material failures and requires localization
before unsupported conclusions or blind reruns. No cache, new solver or separate
physical coupon was added.

Reproduce the controls with the model's `analyze.py --mesh 1.6 --penalty 12000
--increment VALUE --mesh-from ORIGINAL_RUN`; add `--contact-scope mating_side`
for the surface-selection control. Retain each run with the shared evidence
helper, then run `summarize_evidence.py` with the retained labels and
`summarize_diagnosis.py`. Locate a saved event without rebuilding or solving:

```sh
uv run --locked python -m physical_analysis.diagnostics /tmp/lift_debug_increment0025 model/filament_swatch_lift_box/notes/debug/increment0025_contact_locations.json --rigid-parts lid_catch release_pad
```

Unprinted material/process, friction, comfort and long-term behavior remain
separate uncertainties in the main object record. Analysis-only changes leave
the existing CAD exports, placement and slice evidence applicable; they do not
establish actual box function. This investigation uses the main record's
GPT-6.1 Sol/high, Codex attribution.
