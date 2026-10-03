# User design preferences

These preferences belong to this repository's user. They were established during
the filament swatch box discussion and explicitly requested as reusable guidance.
Use them as starting preferences for comparable handled enclosures and storage
objects, with their scope below. They are not universal manufacturing rules or
proof that a particular design works. The latest user instruction takes priority.

## Form and handling

| Preference | Design consequence | Scope and source |
| --- | --- | --- |
| Smooth, continuous exterior | Prefer flush side profiles without raised reinforcement bands or shoulders. Consider internal or local reinforcement when needed. Here, “flat” means a smooth side outline; retain rounded edges and corners. | Handled enclosures. The E band was rejected before a reported print; F's appearance was preferred while explicitly unprinted. [F record](../../../../model/filament_swatch_box_study/notes/cap_comparison.md#f--flush-exterior-reinforcement-inside). |
| Comfortable top and bottom edges | Review roof-to-side transitions, the lower rim, base foot, underside grip edges and newly exposed cuts. A tiny edge break alone may leave an overall square, uncomfortable object. Preserve functional seats and fit surfaces. | Everyday handled objects. D fit was reported okay, but edge comfort and hood bulk were rejected. [Physical history](../../../../model/filament_swatch_box_study/README.md#physical-history-and-print-status). |
| A thin-feeling hood | Start with an economical shell and reinforce only where function needs it. Review the complete exterior and grip, including opaque material use. The 0.8 mm trial shell is a model dimension, not a default wall thickness for other objects. | Swatch hood; a useful starting direction for similar covers. Translucent PETG is intended, but printed optics and thin-shell behavior remain unqualified. [Thin-hood reasoning](../../../../model/filament_swatch_box_study/notes/cap_comparison.md#e--thin-hood-with-base-mounted-detents). |
| Low overhead for modular storage | Account for repeated end material, extra parts and permanent projections. For infrequent separation, consider a compact accessible joint before adding a dedicated external handle. Show the actual joining and release direction. | Swatch modules usually remain joined. G's long arm was called unnecessary before a reported print; H's handle-free release has CAD evidence only. [H record](../../../../model/filament_swatch_box_study/notes/cap_comparison.md#h--wider-connector-without-a-handle). |
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

Printer, nozzle/layer starting settings, materials and available hardware remain
owned by [AGENTS.md](../../../../AGENTS.md). Reuse that source instead of keeping
a second settings table here. Fully printed is a swatch-box requirement, not a
repository-wide ban on the user's available hardware.

For joining interfaces, the user expects firm seated connection, rather than a
loosely captured alignment key. Entry clearance must be justified separately
from final play and retention. They report that their printer is generally very
precise; do not assume poor accuracy or add generous generic FDM allowances.
That report is not a numerical tolerance calibration. Use the actual interface
role, deliberate contact/preload and measured feedback to choose allowances.
The printed [H sample failure](../../../../model/filament_swatch_box_study/README.md#physical-history-and-print-status)
was a loose, unpreloaded connection, not an established printer defect.

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
