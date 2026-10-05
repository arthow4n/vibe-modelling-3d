"""Named plate/screw inspection, optional native solve and separate print jobs."""
import json
from dataclasses import asdict
import cadquery as cq
import components as c
from assembly_geometry import Configuration, PairRequirement, solve, rigid_location, check_pair


def build(p=c.P):
    left, right = c.halves(p)
    return left, right, c.screw(p)


def screw_location(station):
    return rigid_location(lambda frame: c.posed(frame, *station))


def configuration(parts, p=c.P, *, constrained=False):
    left, right, bolt = parts
    a = cq.Assembly(name='plate').add(left, name='left').add(right, name='right')
    for i, station in enumerate(c.stations(p)):
        a.add(bolt, name=f'screw_{i}', loc=screw_location(station))
    if not constrained:
        return Configuration.explicit(a, name='assembled', parameters=asdict(p))
    # Optional qualification path: use the original station/axis relationships,
    # but start screws displaced. The native solver alone calculates final locs.
    a.constrain('left', 'Fixed').constrain('right', 'Fixed')
    for i, station in enumerate(c.stations(p)):
        name = f'screw_{i}'
        x, y, z, _ = station
        a.objects[name].loc = cq.Location((x+3, y+2, z+1))
        a.constrain(name, 'FixedRotation', screw_location(station).toTuple()[1])
        a.constrain('left', cq.Vertex.makeVertex(x, y, z), name,
                    cq.Vertex.makeVertex(0, 0, 0), 'Point')
    return solve(a, name='assembled_native', position_tolerance_mm=1e-5,
                 rotation_tolerance_deg=1e-4, parameters=asdict(p)).require_configuration()


def print_jobs(parts, p=c.P):
    left, right, _ = parts
    jobs = {}
    for name, shape in (('left', c.print_half(left, True, p)), ('right', c.print_half(right, False, p))):
        jobs[name] = Configuration.explicit(cq.Assembly(name='print_plate').add(shape, name=name),
                                           name=f'print_{name}', kind='print')
    # Reuse the author's print placement and one definition for all four instances.
    bolt = c.print_screw(p)
    a = cq.Assembly(name='print_screws')
    for i in range(4):
        a.add(bolt, name=f'screw_{i}', loc=cq.Location((i*26, 0, 0)))
    jobs['screws'] = Configuration.explicit(a, name='print_screws', kind='print')
    return jobs


def verify(config, p=c.P):
    free = PairRequirement('Assembled plate parts clear solids; seating contact allowed', max_overlap_mm3=1e-5)
    results = [config.check('left', 'right', free).require_passed().to_dict()]
    # Global minimum distance could be zero at a lap-root edge while a seat is
    # gapped. Use the original export check's four ring points, with local crops.
    left, right = config.shape('left'), config.shape('right')
    contact = PairRequirement('Selected seating-ring patches meet without interpenetration',
                              max_overlap_mm3=1e-5, max_gap_mm=1e-6)
    for i, (x, y, z, lip) in enumerate(c.stations(p)):
        point = (x+10.8, p.split+p.lap_gap/2, z) if lip else (x+10.8, y, p.split+p.lap_gap/2)
        patch = cq.Workplane().box(.2, .2, .2).translate(point).val()
        results.append(check_pair(left.intersect(patch), right.intersect(patch), contact,
            first=f'left/seat_{i}', second=f'right/seat_{i}', configuration=config.name).require_passed().to_dict())
    for screw in (n for n in config.names if n.startswith('screw_')):
        results.extend(config.check(screw, half, free).require_passed().to_dict() for half in ('left', 'right'))
    return results


if __name__ in ('__main__', '__cqgi__'):
    parts = build()
    explicit = configuration(parts)
    if __name__ == '__main__':
        resolved = configuration(parts, constrained=True)
        print(json.dumps(dict(explicit=verify(explicit), native=verify(resolved),
                              resolution=resolved.resolution), indent=2))
    result = explicit.assembly()
