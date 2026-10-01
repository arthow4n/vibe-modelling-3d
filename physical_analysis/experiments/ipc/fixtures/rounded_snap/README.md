# Local rounded-snap numerical fixture

This is **a synthetic/local numerical contact benchmark derived from historical
failed-product geometry**. It contains only a clamped elastic leaf with root pad
and a translating cylindrical cam. There is no enclosure, lid, contents, guide,
release system or printable storage-product layout. It is not a reusable product
pattern or a recommendation for the next swatch-storage concept.

[question.py](question.py) expresses the local operation through `SnapFitQuestion`.
The nominal leaf spans 18 mm, is 2.4 mm thick and 3.2 mm deep; the cam radius is
2.4 mm and travels 8 mm out and back. Contact is frictionless, the root is clamped,
and the homogeneous elastic assumption is E=1200 MPa, nu=.38. The 1.5% provisional
strain screen is uncalibrated PETG screening, not a measured printed limit.
Historical coordinates and the identifiers `snap_cycle`, `arm`, `body_cam` remain
solely to preserve exact geometry/intent identity against retained numerical runs.
There is no dependency on any retired model or the successful archive swatch.

Retained evidence is limited to:

- [CalculiX local passage/return](evidence/calculix/cycle_base/result.json) and
  four mesh/contact/increment controls. These exercise evidence binding,
  passage/elastic-return interpretation and decision-driven sensitivity tests.
  Baseline force is .611 N and strain 1.129%; force remains increment-sensitive.
- [IPC unresolved crest](evidence/ipc/fine_motion_crest_failure/result.json):
  accepted states through progress .24375 remain independently non-intersecting;
  the next crest step fails nonlinear convergence. This is no completed passage.
- [IPC legacy conversion failure](evidence/ipc/legacy_input_timeout/result.json):
  MEDIT version 1 loses coordinate precision and supplied/native mesh witnesses
  disagree. Its numerical evidence remains unqualified.
- [Thread measurements](../../performance/README.md): the frozen contact prefix,
  not a complete operation, retains its measured eight-thread advantage.

Original input/result/log/BREP identities and outcomes are preserved from
`d37763c`; historical absolute paths in provenance describe the original runs,
not supported products or current replay paths. Large external native fields
are not archived here. Tests rebuild the minimal geometry and identity-check
retained cases; replay requires the recorded external executable and inputs.
No current finite-edge lift-off product fixture is retained: its coupled
cap/pad/enclosure scene is left in Git history. Generic contact diagnostics and
independent crossing-triangle tests retain their safeguards without that product.

The user physically printed and rejected the source sliding storage product,
and rejected the other two storage concepts visually/functionally. Local contact
success did not establish sensible component roles or normal use. That feedback
supersedes earlier product confidence; it does not change these narrow numerical
observations. IPC remains optional and unqualified for complete crest passage.

Historical contributors: GPT-6.1 Sol/high (completion) and GPT-6 Astra/low
(initial CAD/shared contact), explicitly user-reported in the retired product
record; full attribution remains in Git history. Extraction/workflow correction:
GPT-6 family, exact variant and reasoning effort not exposed; Codex harness,
provider metadata not separately exposed; no subagents. No new physical validation.
