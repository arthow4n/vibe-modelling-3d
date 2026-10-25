"""Fresh complete-geometry checks paired with display-only inspections."""
from dataclasses import dataclass, replace

import cadquery as cq
from assembly_geometry import Configuration, sample_motion
from .spec import Inspection, Arrow


@dataclass(frozen=True)
class CheckedInspection:
    inspection: Inspection
    answer: object  # native PairResult/MotionResult; usable by engineering_evidence()
    selected_sample: float | None = None


def pair_inspection(configuration, first, second, requirement, *, view, purpose,
                    title='', question_ids=()):
    """Check current full parts, then annotate distance witnesses when available."""
    answer = configuration.check(first, second, requirement)
    annotations = list(view.annotations)
    if answer.closest_points_mm is not None:
        a, b = answer.closest_points_mm
        annotations += [Arrow(a, b, f'unsigned gap {answer.gap_mm:g} mm')]
    if answer.error:
        purpose += f' Calculation inconclusive: {answer.error}'
    purpose += f' Pair check: {answer.status}.'
    return CheckedInspection(Inspection(configuration, replace(view, annotations=tuple(annotations)),
                                        purpose, title, question_ids), answer)


def motion_inspection(configuration, moving, obstacle, requirement, *, samples,
                      transform, parameter, units, select, view, purpose,
                      title='', question_ids=()):
    """Compute current sampled path once; render an exact recorded pose.

    select is a supplied sample value or 'first_unsuccessful'. The latter raises
    if all samples pass: callers must explicitly choose a successful overview.
    Other components retain their snapshot positions. No stale result replay.
    """
    answer = sample_motion(configuration, moving, obstacle, requirement, samples=samples,
                           transform=transform, parameter=parameter, units=units)
    if select == 'first_unsuccessful':
        index = next((i for i, r in enumerate(answer.results) if r.status != 'passed'), None)
        if index is None:
            raise ValueError('No unsuccessful sampled pose; select an explicit sample')
    else:
        if select not in answer.samples:
            raise ValueError('Selected pose must be one of the checked samples')
        index = answer.samples.index(select)
    # Poses retain absolute native placement. Recover delta without rerunning
    # an arbitrary transform callback (which might have construction side effects).
    delta = cq.Location(*answer.poses[index])*configuration.location(moving).inverse
    # Keep hierarchy/path identity by using a copied native assembly and replacing
    # only its moving node's world pose, instead of exposing flattened aliases.
    assembly = configuration.assembly()
    node = assembly.objects[assembly.name+'/'+moving] if assembly.name+'/'+moving in assembly.objects else assembly.objects[moving]
    parent_world = configuration.location(moving)*node.loc.inverse
    original_location = node.loc
    node.loc = parent_world.inverse*delta*parent_world*original_location
    # sample_motion moves this node's geometry, not a whole subtree. Compensate
    # its immediate children so every other component keeps its checked pose.
    compensation = node.loc.inverse*original_location
    for child in node.children:
        child.loc = compensation*child.loc
    # A solved snapshot has authoritative positions, but its copied constraints
    # describe the source pose. Prescribed motion does not re-solve/enforce them.
    # Clear declarations only on the display copy before adopting explicit poses.
    for _, member in assembly.traverse():
        member.constraints = []
    pose = Configuration.explicit(assembly, name=f'{configuration.name}:{parameter}={answer.samples[index]}',
                                  kind='intermediate', parameters={**configuration.parameters, parameter: answer.samples[index]})
    pair = answer.results[index]
    annotations = list(view.annotations)
    if pair.closest_points_mm is not None:
        a, b = pair.closest_points_mm
        annotations.append(Arrow(a, b, f'unsigned gap {pair.gap_mm:g} mm'))
    purpose += f' {parameter}={answer.samples[index]:g} {units}; sample {pair.status}; path {answer.status}. Sampled poses only.'
    return CheckedInspection(Inspection(pose, replace(view, annotations=tuple(annotations)), purpose,
                                        title, question_ids), answer, answer.samples[index])
