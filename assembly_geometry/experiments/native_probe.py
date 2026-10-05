"""Inspect the installed native solver, including outcomes that are not acceptance."""
import json
import cadquery as cq


def fixture(size=2, guess=(6, 1, 0)):
    return (cq.Assembly(name='probe')
            .add(cq.Workplane().box(size, size, size), name='fixed')
            .add(cq.Workplane().box(size, size, size), name='moving', loc=cq.Location(guess)))


def run():
    results = []
    for kind in ('point_rotation', 'plane_only', 'inconsistent', 'missing', 'changed_size'):
        a = fixture(4 if kind == 'changed_size' else 2)
        try:
            if kind != 'missing':
                a.constrain('fixed', 'Fixed')
                if kind == 'plane_only':
                    a.constrain('fixed@faces@>Z', 'moving@faces@<Z', 'Plane')
                else:
                    a.constrain('fixed@faces@>Z', 'moving@faces@<Z', 'Point')
                    a.constrain('moving', 'FixedRotation', (0, 0, 0))
                if kind == 'inconsistent':
                    a.constrain('moving', 'FixedPoint', (0, 0, 10))
            a.solve()
            stats = a._solve_result
            results.append(dict(case=kind, success=stats['success'],
                return_status=stats['return_status'], iterations=stats['iter_count'],
                objective=float(stats['opti'].value(stats['opti'].f)),
                placement=a.objects['moving'].loc.toTuple(),
                face_gap_mm=a.objects['fixed'].obj.faces('>Z').val().distance(
                    a.objects['moving'].obj.faces('<Z').val().moved(a.objects['moving'].loc))))
        except Exception as exc:
            results.append(dict(case=kind, error=f'{type(exc).__name__}: {exc}'))
    return dict(cadquery=cq.__version__, results=results)


if __name__ == '__main__':
    print(json.dumps(run(), indent=2))
