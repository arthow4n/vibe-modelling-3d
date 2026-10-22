# User design preferences

These preferences belong to this repository's user. Their source discussions
and applicable scope are recorded below. Use them as starting preferences for
comparable objects within those scopes. They are not universal manufacturing rules or
proof that a particular design works. The latest user instruction takes priority.

## Printer, manufacturing and available hardware

Read before choosing printable dimensions or a print setup; retrieve the stock
inventory when fasteners are useful. These are user defaults, not calibrated
material properties or universal design limits.

Use the Qidi Q2C **270 × 270 × 256 mm (X × Y × Z)** build volume as the default
practical printable envelope
([Q2C specifications](https://us.qidi3d.com/products/q2c)), unless the user
specifies another setup. This is the usable design limit, not the printer's
physical plate dimensions. Allow for likely brims/supports in the rough plan,
and check each oriented axis independently. Let the final Orca slice decide
whether its actual print aids fit. For OrcaSlicer reviews, take the
printable area and height from the selected printer profile; do not maintain a
separate bed-size override. Use a smaller user-confirmed safe volume by
providing a printer profile with those limits.

The user's preferred starting setup is a **0.4 mm nozzle and 0.2 mm layers**.
They also have a **0.8 mm nozzle** and several **PLA, PETG and TPU** filaments.
For the quiet swatch-box revision, the user confirms **ordinary TPU 95A**;
brand is unknown. This is available stock, not calibrated printed-material
behavior ([Q1 record](../../../../model/filament_swatch_box_study/README.md#quiet-tpu-revision--q1-prototype-2026-10-05)).
Their experience is that **two walls and 7% adaptive cubic infill** are often
enough for general prints; these are starting assumptions, not strength or
printability requirements. For a phase with printable deliverables, discuss the
proposed nozzle, layer height, material, walls and infill during initial agreement;
for rough visual studies, state only process assumptions that affect the choice.
Explain and agree on consequential changes, especially when fit, flexibility, strength, print
time or finish depends on them. Use the agreed setup to size geometry and screen
loads before slicing. The reference Orca profile is diagnostic, not a substitute
for the agreed print setup.

**Liner layer-height correction, 2026-10-16:** the user explicitly confirms that
**all liner prints so far used 0.2 mm layers**, including experiments/instructions
that requested 0.1 mm. Use 0.2 mm for future liner instructions and reference
setups unless the user explicitly agrees to another experiment. Attribute prior
liner quietness, failures and ironing feedback to the reported 0.2 mm setting;
preserve old 0.1 mm slicer receipts as diagnostic evidence only. A separate first
layer override and other unreported settings remain unknown. See the
[owning correction](../../../../model/tpu_damping_box/README.md#actual-liner-layer-height-correction--2026-10-16).

**TPU flow default, 2026-10-16:** the user requests **9 mm³/s maximum volumetric
flow**, replacing 4 mm³/s in the shared
[TPU 95A preset](../../../../model/tpu_damping_box/profiles/tpu95a.json).
This is the requested preset limit, not a measured spool calibration or a report
of past print settings. Wall/infill speed limits remain separate choices.

For thin TPU impact liners, the user means a thin **overall sandwich**, not
automatically thin webs or skins. Prefer substantial local features suitable for
their normal 0.4 mm nozzle; do not recommend marginal single-path replacements
merely because a diagnostic slice retains them. Their [I24/I20 rejection before
printing](../../../../model/tpu_damping_box/README.md#thin-feature-rejection-and-prevention)
does not establish a universal extrusion-width limit. A later
[physical comparison](../../../../model/tpu_damping_box/README.md#i22--i30--i10-print-feedback--latest-report)
accepts I22 quietness with little perceived difference from I30, but rejects
I10's broken shell-side regions. **Both continuous skins are required for this
liner follow-up.** The user allows slicer changes to explore thinner closed-skin
variants. I22's near-joining lines remain an unresolved observation, not a
calibrated minimum gap or proof of a specific process cause.

**Upcoming TPU damping iterations, 2026-10-19:** explicitly check upright wall
integrity in addition to dimensions. Aim for geometry/process configurations
that do not require Arachne; allow a thicker sandwich rather than preserving
S16's 1.6 mm at the expense of reliable walls. A stronger 1.6 mm design or about
2.0 mm are both acceptable directions, not selected or qualified replacements.
This is scoped to the ongoing liner experiment, not a general ban on Arachne.
The [owning iteration priorities](../../../../model/tpu_damping_box/README.md#upcoming-iteration-priorities--2026-10-19)
record the user's examples, unit interpretation and remaining evidence needs.

**TPU support-batch clarification, 2026-10-20:** the user explicitly requires
no Arachne and rejects the four R1 support pairs before printing because walls
disappear in their slice. They request normal slicing compatibility. The
[R2 correction](../../../../model/tpu_damping_box/README.md#ordinary-classic-repair--r2)
tests ordinary Classic widths with thin-wall detection off to establish that
it does not depend on recovery options; that diagnostic choice is not a claim
about the user's unreported checkbox settings or a global ban for other models.

**TPU surface-concept clarification, 2026-10-21:** for this liner exploration,
prefer one cup piece, accept two cup pieces plus the usual lid pad, and avoid
complicated assembly. Show how each
suggestion prints; replace impractical construction rather than deferring it.
Count floor/lid and core/retention parts explicitly; a low part count alone does
not make folding or insertion simple. The user explicitly excludes the usual
lid pad from the one/two-cup-piece limit; still show the whole-liner count.
[Owning print-first review](../../../../model/tpu_damping_box/notes/print_first_concepts.md).
This is scoped to the current liner, not a universal ban on multipart products.
Later feedback sets aside two thin upright cups because of prior wall-printing
failures, and rejects folding because adapting it to other liner shapes would
introduce impractical-to-print constructions. Future liner concepts should be
preformed and transferable to intended container shapes; a simple fixture net
alone does not settle that adoption. These are architecture decisions, not new
physical print results or a universal claim that all thick TPU cups fail. The
user subsequently permits several infill-based candidates and requires their
**actual sliced print paths** to explain the printing concept; generic pattern
icons are insufficient. [Owning configurations and path evidence](../../../../model/tpu_damping_box/notes/infill_study/README.md).
The next request favors B's discrete ties over ribs and asks for autonomous
research into thicker skins and self-designed curves, including a smoother N2,
using actual slices of B and candidates. Keep gyroid available rather than
replacing it by assumption. [Owning adaptive path study](../../../../model/tpu_damping_box/notes/tie_surface_study/README.md).
This is a current exploration preference, not proof that every rib architecture
is inferior or a new physical rejection of the approved B pairs.

**TPU liner marking clarification, 2026-10-21:** earlier tiny-label readability
feedback does not justify large/deep labels across a functional thin skin. The
user now prioritizes a small visible ID that preserves the structure under test,
and selects T08/T16 as the eventual next pair after an SVG marking discussion.
[Owning options and source-backed skin effects](../../../../model/tpu_damping_box/notes/marking_options.md).
This scopes the earlier large-label preference. The user subsequently selects
M1 compact full-text corner IDs and authorizes the full T08/T16 cup/pad pairs;
[implemented record](../../../../model/tpu_damping_box/notes/t_skin/README.md).

**Latest TPU physical baseline, 2026-10-21:** after printing both thinner follow-ups, the user prefers **L20** over T08: `2.0 mm` rather than `2.2 mm` total wall, similarly good damping and print quality almost equal to T08. L18 also damps well. L20 is the perceived sweet spot for print quality; the bottom surface has slightly fewer defects despite ironing being on, with no known cause. T08 remains an approved control; T16 remains rejected as too firm/noisier. Use L20 as the preferred starting point for this damping-box architecture. This does not establish a universal gap minimum or qualify a different application. [Owning physical report](../../../../model/tpu_damping_box/notes/thin_gap/README.md#physical-feedback--2026-10-21).

The user reports that this printer is generally precise. Do not assume poor
accuracy or use generous generic FDM clearances without an interface reason.
Choose insertion allowance, seated play and retention separately; this report
does not supply a universal measured tolerance. Apply the design skill's
[retention screen](design-decisions.md#actuation-effort-and-cheap-mechanics)
before offering a friction-retained connection for printing.

### Stock screws and nuts

The user also has an on-hand screw and nut assortment
([Jula assortment 002837](https://www.jula.se/catalog/bygg-och-farg/infastning/sortimentsatser/skruvsatser/skruv-muttersats-002837/))
available when metal screw or bolt fasteners are useful. Do not force a printed fastener to reproduce their fine standard threads merely to use a stock nut; choose the mating pair for the actual manufacturing process:

- **Machine screws (maskinskruvar):**
  - M3 × 10 mm (60 pcs)
  - M3 × 12 mm (60 pcs)
  - M4 × 10 mm (50 pcs)
  - M4 × 12 mm (35 pcs)
  - M4 × 25 mm (25 pcs)
  - M5 × 20 mm (25 pcs)
  - M5 × 30 mm (20 pcs)
  - M6 × 12 mm (25 pcs)
  - M6 × 20 mm (18 pcs)
  - M6 × 30 mm (12 pcs)
- **Nuts (muttrar):**
  - M3 (120 pcs)
  - M4 (110 pcs)
  - M5 (45 pcs)
  - M6 (55 pcs)

During planning, if fasteners are useful, discuss with the user whether they
prefer a fully printed design or whether using this stock hardware is
acceptable. If the user explicitly requests full autonomous implementation, use
best engineering judgment; using these available stock materials is allowed.

**Printed fasteners:** the user explicitly wants custom printed screws to have a solid core and be printed solid, with a matching printed nut when helpful. Prefer coarse, broad threads sized for the nozzle over fine metal-standard detail; standard hardware remains an option where appropriate. Verify actual core material after all sweep/boolean operations, then verify solid slicing separately. The [travel-case correction](../../../../model/dental_travel_case/notes/rotary_refinement.md#the-old-thread-really-was-hollow) confirms a hollow CAD thread despite an intended cylinder and passing validity checks; sparse infill was a separate issue. Existing working [book-plate custom threads](../../../../model/book_reading_plate/README.md#what-changed-after-the-successful-l-sample) are a bounded starting reference, not proof at smaller scale.

## Assembly tools

Prefer standard tool interfaces and common sizes (for example, hex sockets for
standard Allen keys). The user owns and prefers an existing tool set: do not
model or export printable substitutes, including optional drivers or wrenches,
unless explicitly requested. Specify the standard tool and nominal size, allow
appropriate printing clearance, and check access and engagement. An all-printed
object does not imply printed assembly tools.

## Form and handling

| Preference | Design consequence | Scope and source |
| --- | --- | --- |
| Large, bold printed identification | Prefer prominent lettering and generous strokes; check actual glyphs and sliced appearance. Do not assume small valid CAD text will be readable after printing. | Explicit request after [TPU liner labels proved too small](../../../../model/tpu_damping_box/README.md#user-print-feedback--2026-10-16). Applies to comparable printed IDs. No universal minimum size established. |
| Compact desk footprint for phone supports | Treat forward feet, rear supports and release mechanisms as part of the occupied desk space. Stability and accessory clearance must be balanced with compactness; extra support is not automatically worth its footprint. No numerical maximum has been supplied. | Desktop phone stands. User rejects raised easel v2 before printing as too large horizontally, specifically its rear structure and forward feet. [Rejection record](../../../../model/analysis_phone_stand/README.md#rejection-before-printing-and-footprint-explanation). |
| Smooth, continuous exterior | Prefer flush side profiles without raised reinforcement bands or shoulders. Consider internal or local reinforcement when needed. Here, “flat” means a smooth side outline; retain rounded edges and corners. | Handled enclosures. The E band was rejected before a reported print; F's appearance was preferred while explicitly unprinted. [F record](../../../../model/filament_swatch_box_study/notes/cap_comparison.md#f--flush-exterior-reinforcement-inside). |
| Protected installed hardware | Keep heads, nuts and screw tips recessed or behind smooth backing on handled enclosures, especially beside storage/loading paths. A gauge shifted around bare hardware does not establish a smooth passage. Custom printed fasteners or a printed/metal mix may be preferable when stock screw lengths intrude. | Explicit travel-case [hardware and indexing revision](../../../../model/dental_travel_case/notes/rotary_refinement.md#what-the-user-requires-and-what-changed). The subsequent custom printed-pair instruction supersedes that revision’s stock-only restriction. |
| Comfortable top and bottom edges | Review roof-to-side transitions, the lower rim, base foot, underside grip edges and newly exposed cuts, including inward corners where a cut meets a rim. The user prefers substantially rounded handled ends; a tiny edge break alone does not satisfy that preference. Distinguish plan-view corner rounds from actual top/bottom end blends, and co-design the latter with bed contact and first-layer support. Preserve functional seats and fit surfaces. | Everyday handled objects. The [M1 follow-up](../../../../model/dental_travel_case/notes/m1.md#printed-joint-feedback--2026-10-15) explicitly requests much larger top/bottom fillets and learning this across designs; R4 is a local choice, not a universal radius. D fit was reported okay, but edge comfort and hood bulk were rejected. [Physical history](../../../../model/filament_swatch_box_study/README.md#physical-history-and-print-status). R1's inward scoop/rim junctions were [rejected before printing](../../../../model/filament_swatch_box_study/notes/cap_comparison.md#r1-entrance-rejection-and-alternatives). |
| A thin-feeling hood | Start with an economical shell and reinforce only where function needs it. Review the complete exterior and grip, including opaque material use. The 0.8 mm trial shell is a model dimension, not a default wall thickness for other objects. | Swatch hood; a useful starting direction for similar covers. Translucent PETG is intended, but printed optics and thin-shell behavior remain unqualified. [Thin-hood reasoning](../../../../model/filament_swatch_box_study/notes/cap_comparison.md#e--thin-hood-with-base-mounted-detents). |
| Swatch-box damping development stopped | The user discontinued the TPU damping project. Preserve the accepted storage baseline and the lessons; do not continue Q1/Q1F or follow-up TPU variants unless the user reopens this work. Quietness remains unresolved. This is a decision for this project, not a ban on TPU for other uses. | Q1F joining works but appearance/upper fit/sliding sound disappoint. An unchanged G hood printed fully in TPU still rubs audibly against the jacket: somewhat quieter, still unacceptable; upper shell distorted but usable. [Discontinuation and physical lessons](../../../../model/filament_swatch_box_study/README.md#tpu-damping-discontinued-2026-10-06). Printed layers causing noise is the user's unconfirmed hypothesis. |
| Deliberate contrast in soft jackets | When TPU cannot match the rigid part's colour, prefer connected wall coverage and clean intentional access openings over exposed patches and isolated-looking connector bands. Locate the upper jacket edge without relying only on a lower anchor. | TPU-covered swatch bases; white PETG with black TPU Q1F was physically rejected for appearance and floating upper regions. [Feedback](../../../../model/filament_swatch_box_study/README.md#damped-prototype-print-feedback-and-svg-exploration-2026-10-06). The damping project was subsequently discontinued; this appearance lesson does not reopen it or require covering card-entry, key/grip access or every rigid surface. |
| Low overhead for modular storage | Account for repeated end material, extra parts and permanent projections. For infrequent separation, consider a compact accessible joint before adding a dedicated external handle. Show the actual joining and release direction. | Swatch modules usually remain joined. G's long arm was called unnecessary before a reported print; H's handle-free release has CAD evidence only. [H record](../../../../model/filament_swatch_box_study/notes/cap_comparison.md#h--wider-connector-without-a-handle). |
| An existing cover can keep joints captive | Where the normal cover can block an assembly key's escape, prefer that clean, enclosed arrangement over adding an exposed keeper. Preserve a deliberate removal route with the cover off. Coverage is not proof of clamping force or structural capacity. | User likes the printed swatch box's top-inserted key because the closed hood keeps it from falling out while the exterior stays clean. [Feedback](../../../../model/filament_swatch_box_study/notes/cap_comparison.md#closed-hood-as-key-keeper--user-preference). Apply only where normal cover use and release access make this useful. |
| Loaded box staying attached when lifted by its cover | Consider full-load cover lifting when feasible while keeping deliberate opening comfortable. This is desirable, not mandatory; do not add bulk, hardware or a complex mechanism solely for this occasional use. Follow the [retention load screen](design-decisions.md#actuation-effort-and-cheap-mechanics). | Comparable handled boxes with retained removable covers. Archive A with 15 cards stayed attached when lifted by its G hood; no quantitative force or durability rating follows. [Print report](../../../../model/filament_swatch_box_study/notes/cap_comparison.md#archive-r2-a-print-report--2026-10-04). |
| Recessed grips over outward flaps | Prefer accessible recessed contacts within the existing silhouette for handled enclosures. Place the opening and bearing face for the intended hand-force direction, and check access with the mating cover closed. Do not default to a large outward tab merely because it makes access easy. | Explicit reusable preference after J3/K3 outward ledges were rejected before printing; original recess form is preferred with an upward-facing contact. This does not prohibit a projection needed for another task. [Feedback](../../../../model/filament_swatch_box_study/notes/cap_comparison.md#v1-print-and-recessed-grip-feedback). |

Roundness and flush sides are compatible preferences. Neither specifies a fixed
radius, a perfectly flush base/hood footprint, nor a prohibition on a useful
handle. Choose dimensions and features for the actual task, material and print
orientation; explain consequential departures from an applicable preference.

## Project requirements and print preferences

Keep swatch-specific requirements with the
[object's requirements](../../../../model/filament_swatch_box_study/README.md#requirements-to-preserve):
upright cards with the notch above, easy entry from all directions, firm seated
alignment even with few cards, a fully printed enclosure and a seated but
removable hood. Do not silently turn these into rules for unrelated objects.

The user prefers a small five-card trial before a large swatch box and wants
earlier unprinted variants retained for comparison. This does not make every
project require coupons or every possible capacity. Use the skill's existing
development guidance and label current versus historical matching parts clearly.

Use the [printer and hardware defaults above](#printer-manufacturing-and-available-hardware)
without maintaining another settings table. Fully printed is a swatch-box requirement, not a
repository-wide ban on the user's available hardware.

For joining interfaces, the user expects firm seated connection, rather than a
loosely captured alignment key. Entry clearance must be justified separately
from final play and retention. Apply the precision/allowance distinction in the printer defaults above. Use the actual interface
role, deliberate contact/preload and measured feedback to choose allowances.
The printed [H sample failure](../../../../model/filament_swatch_box_study/README.md#physical-history-and-print-status)
was a loose, unpreloaded connection, not an established printer defect.

## Protection and mechanism visibility

For ordinary storage, the user's default is a fully covered cavity
that excludes basic dust and sheds incidental spills; do not silently substitute
an open organizer. This is not a watertightness or ingress rating. Ventilation
or open access may serve a different stated task. See the
[handling review](design-decisions.md#whole-object-form-and-handling) for closure
and access checks.

Conceal mechanisms in the assembled object where practical, with understandable,
modest controls. Prefer covers, internal interfaces or protected recesses over
exposing the entire flexure for analysis convenience. Discuss a consequential
visibility/access tradeoff when undelegated, or choose and document it under
autonomous scope. Exposure is appropriate when it serves the task.

## Proposal workflow

For an unresolved form comparison, this user prefers **SVG proposals first,
then a discussion handoff before modelling multiple CAD variants**. Drawings
make the back-and-forth faster. Use targeted rough CAD when a consequential
geometry question cannot be answered by the sketch or simple calculations;
explain that need rather than completing every alternative. Explicit approval
to finish modelling or autonomous implementation overrides this staging default.
In the archive corner round, CAD had advanced further than the user expected;
they accepted that work and authorized completion, while requesting this
preference for future rounds. [Evidence](../../../../model/filament_swatch_box_study/notes/cap_comparison.md#archive-r2--four-retaining-forms).

## Engineering computation

**Engineering explanations, 2026-10-20:** mix precise technical quantities with
everyday meaning and explain what decision they support. For example, 12.6 N is
roughly the force needed to hold up 1.3 kg; that analogy does not equate a steady
push with a knock. Provide useful SVG explanations during the discussion:
where the object is held, where/how it is pushed, movement/contact sequence,
comparable results, and which trials were completed, attempted or never done.
Do not rely on technical prose or an unannotated solver plot when the user needs
to understand the mechanism. The user explicitly requests practical stopping
criteria and rejects chasing analysis-generated problems after sufficient
evidence exists for the actual decision. Follow the
[owning decision guidance](design-decisions.md#adaptive-development-and-the-next-deliverable);
keep physical unknowns visible without automatically expanding the task.
[Source and explanatory SVGs](../../../../model/dental_travel_case/notes/short_lap.md#practical-stopping-and-explanation-feedback).

**Repeated correction, grip-placement work:** the user rejects a stream of
“inconclusive” research as a substitute for a practical engineering decision.
Conclude the requested choice using suitable evidence; distinguish the chosen
design from a specific unmeasured property or unsuccessful optional calculation.
When the agent invented the wrong acceptance problem, change the active
verification strategy and deliver the missing practical result, rather than
only stopping the solver or adding another caution. Preserve genuine unknowns
and failed evidence. [Concrete correction and selected grip](../../../../model/dental_travel_case/notes/grip_human.md#working-approach-correction);
[method owner](../../engineering-method-selection/SKILL.md#choose-from-the-decision).

For mechanical joints and catches, include a cross-section SVG explaining how
the interface holds, guides and releases. Draw movement and contact order at
comparable scale to show whether a numerical improvement physically matters,
including relevant side play. Commit useful exploration drawings and their source.
If the supposed benefit does not protect the mechanism, improve the model and
update the matching test piece too. [M4 correction](../../../../model/dental_travel_case/notes/m4.md).
The user requests practical adaptations
when a simulation is too demanding: retain the consequential mechanics in an
interpretable proxy, try reasonable corrections, and stop if those remain
unproductive. Do not prolong solver development merely to preserve the original
representation. [Dental continuation](../../../../model/dental_travel_case/notes/m3.md).

For engineering computations, the user explicitly rejects agent-invented
timeouts and increasing one arbitrary cap to another. Use the
[owning workflow rule](../../../../AGENTS.md#shared-engineering-execution).
The [phone-stand record](../../../../model/analysis_phone_stand/README.md#timeout-investigation-requested-by-the-user)
documents the interrupted useful work and removed limits.

**Do not invoke sub-agents unless the user explicitly requests them.** The user
replaced the earlier implementation–review cadence preference with this explicit
instruction during the [space-first closure research](../../../../model/dental_travel_case/notes/closure_research.md).
Do the implementation, end-to-end checks and critical self-review directly.
When independent review is explicitly requested, finish a coherent implementation
and its own verification first; do not use a reviewer to direct partial fragments.
The earlier dental-case cadence correction also identified inference cost as the reason.
If a consequential technical blocker remains after a serious attempt, an honest
partial result is acceptable. [Context](../../../../model/dental_travel_case/notes/m2.md#review-cadence-correction).

## Updating this record

Record a repeated or explicit preference with its use context and a link to the
object evidence. Treat exploratory suggestions as options until adopted; for
example, asking whether a bow tie could be larger does not establish a preferred
connector size for future models. Update an existing preference when it changes.

Keep three kinds of information distinct:

- User preferences guide subjective form and use choices.
- Object records own dimensions, matching variants, assumptions and print results.
- [Reusable model evidence](reusable-model-lessons.md) owns transferable design
  lessons, identifying whether evidence is feedback, CAD, slicing or a print.

Render approval, a planned print and a completed slice do not establish physical
fit or comfort. Read preferences early enough to shape the architecture; naming
them in a final note after detailing is too late to avoid unnecessary work.
