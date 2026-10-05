"""Independent known geometry and native-solver qualification; mm/degrees."""
import json
import math
import cadquery as cq
import pytest
from assembly_geometry import Configuration, PairRequirement, check_pair, sample_motion, solve, rigid_location, constrain


def cube(size=2):
    return cq.Workplane().box(size, size, size)


def pair(offset=4):
    part = cube()
    return cq.Assembly(name='fixture').add(part, name='fixed').add(part, name='moving', loc=cq.Location((offset, 0, 0)))


@pytest.mark.parametrize('dx,volume,gap', [(4, 0, 2), (1, 4, 0), (2, 0, 0),
                                         (2.0001, 0, .0001), (1.9999, .0004, 0)])
def test_known_signed_clearance_cases(dx, volume, gap):
    config = Configuration.explicit(pair(dx), name='pose')
    r = config.check('moving', 'fixed', PairRequirement('Measure independent box outcome',
                     max_overlap_mm3=10, min_gap_mm=0))
    assert r.calculation_completed and r.status == 'passed'
    assert r.overlap_mm3 == pytest.approx(volume, abs=1e-9)
    assert r.gap_mm == pytest.approx(gap, abs=1e-9)
    assert math.dist(*r.closest_points_mm) == pytest.approx(gap, abs=1e-9)
    assert r.first == 'moving' and r.configuration == 'pose'
    json.dumps(r.to_dict())


def test_contact_and_obstruction_intent_are_independent_of_execution():
    a, b = cube(), cube().translate((1, 0, 0))
    obstruction = check_pair(a, b, PairRequirement('Required obstruction', min_overlap_mm3=3))
    forbidden = check_pair(a, b, PairRequirement('Forbidden obstruction', max_overlap_mm3=1e-8))
    assert obstruction.status == 'passed' and forbidden.status == 'failed'
    assert obstruction.calculation_completed and forbidden.calculation_completed
    assert check_pair(a, cube().translate((2, 0, 0)), PairRequirement(
        'Required contact without penetration', max_overlap_mm3=1e-8, max_gap_mm=1e-7)).status == 'passed'
    assert check_pair(a, cube().translate((2.001, 0, 0)), PairRequirement(
        'Required contact without penetration', max_overlap_mm3=1e-8, max_gap_mm=1e-7)).status == 'failed'
    assert forbidden.gap_mm is None  # volume-only intent does not pay for distances


def test_repeated_instances_hierarchy_world_frame_and_snapshot():
    bolt = cube()
    group = cq.Assembly(name='group').add(bolt, name='bolt', loc=cq.Location((1, 0, 0)))
    root = cq.Assembly(name='root', loc=cq.Location((0, 0, 0), (0, 0, 90)))
    root.add(group, name='left', loc=cq.Location((4, 0, 0)))
    root.add(group, name='right', loc=cq.Location((8, 0, 0)))
    config = Configuration.explicit(root, name='nested')
    assert config.names == ('left/bolt', 'right/bolt')
    assert config.shape('left/bolt').Center().toTuple() == pytest.approx((0, 5, 0))
    root.children[0].loc = cq.Location((100, 0, 0))
    exported = config.assembly()
    assert exported.objects['left/bolt'].obj.isValid()
    assert exported.objects['right/bolt'].obj.isValid()
    exported.children[0].loc = cq.Location((200, 0, 0))
    returned = config.shape('left/bolt')
    returned.move(cq.Location((500, 0, 0)))
    assert config.shape('left/bolt').Center().toTuple() == pytest.approx((0, 5, 0))
    with pytest.raises(KeyError):
        config.shape('bolt')
    with pytest.raises(KeyError):
        config.shape('left')  # grouping node is not substituted with a default shape
    from evaluate_model import selected_shape
    assert selected_shape(config.assembly()).isValid()


@pytest.mark.parametrize('size', [2, 4])
def test_explicit_parameter_change_consistency(size):
    a = cq.Assembly(name='scaled').add(cube(size), name='first').add(cube(size), name='second', loc=cq.Location((size+.2, 0, 0)))
    c = Configuration.explicit(a, name='sized', parameters={'size_mm': size})
    assert c.check('first', 'second', PairRequirement('Derived clearance', min_gap_mm=.19999)).status == 'passed'
    with pytest.raises(TypeError):
        c.parameters['size_mm'] = 50


def native(size=2, guess=(6, 1, 0)):
    a = cq.Assembly(name='native').add(cube(size), name='fixed').add(cube(size), name='moving', loc=cq.Location(guess))
    a.constrain('fixed', 'Fixed')
    constrain(a, 'fixed@faces@>Z', 'Point', second='moving@faces@<Z')
    a.constrain('moving', 'FixedRotation', (0, 0, 0))
    return a


def resolve(a):
    return solve(a, name='solved', position_tolerance_mm=1e-6, rotation_tolerance_deg=1e-4)


@pytest.mark.parametrize('size,guess', [(2, (6, 1, 0)), (4, (-4, 2, 9)), (2, (0, 0, 2))])
def test_native_solve_residuals_guesses_and_geometry_change(size, guess):
    a = native(size, guess)
    r = resolve(a)
    c = r.require_configuration()
    assert r.status == 'resolved' and r.diagnostics['success']
    assert all(x['passes'] for x in r.residuals)
    assert c.shape('moving').Center().toTuple() == pytest.approx((0, 0, size), abs=1e-6)
    assert a.objects['moving'].loc.toTuple()[0] == guess  # no caller mutation
    assert c.check('fixed', 'moving', PairRequirement('Seated faces', max_gap_mm=1e-6,
                   max_overlap_mm3=1e-6)).status == 'passed'
    with pytest.raises(ValueError, match='initial guesses'):
        Configuration.explicit(a, name='invalid_explicit')


def test_native_success_cannot_hide_inconsistent_relationships():
    a = native()
    a.constrain('moving', 'FixedPoint', (0, 0, 10))
    r = resolve(a)
    assert r.diagnostics['success'] and r.status == 'residual_failed'
    assert r.configuration is None
    assert max(x['value'] for x in r.residuals if x['units'] == 'mm') == pytest.approx(4)
    with pytest.raises(ValueError, match='residual_failed'):
        r.require_configuration()


def test_underconstrained_missing_and_unsupported_resolution():
    a = pair().constrain('fixed', 'Fixed').constrain('fixed', 'moving', 'Point')
    assert resolve(a).status == 'inconclusive'  # free rotation
    assert resolve(pair()).status == 'invalid'
    a = pair().constrain('fixed@faces@>Z', 'moving@faces@<Z', 'Point').constrain('moving', 'FixedRotation', (0, 0, 0))
    assert resolve(a).status == 'inconclusive'  # implicit native anchor prohibited
    a = pair().constrain('fixed', 'Fixed').constrain('fixed@faces@>Z', 'moving@faces@<Z', 'Plane')
    assert resolve(a).status == 'unsupported'  # unqualified yaw branch
    with pytest.raises(KeyError):
        pair().constrain('missing', 'Fixed')
    with pytest.raises(IndexError):
        pair().constrain('moving@faces@>Z[100]', 'FixedPoint', (0, 0, 0))


def test_native_solver_failure_preserved(monkeypatch):
    def fail(*args, **kwargs):
        raise RuntimeError('native numerical failure')
    monkeypatch.setattr(cq.Assembly, 'solve', fail)
    r = resolve(native())
    assert r.status == 'failed' and r.configuration is None
    assert 'native numerical failure' in r.diagnostics['reason']


def test_fixedpoint_and_rotation_residual():
    a = pair().constrain('fixed', 'Fixed').constrain('moving', 'FixedPoint', (4, 0, 0)).constrain('moving', 'FixedRotation', (0, 0, 90))
    r = resolve(a)
    assert r.status == 'resolved', r
    assert r.require_configuration().location('moving').toTuple()[1] == pytest.approx((0, 0, 90), abs=1e-4)


def test_strict_native_selectors_and_existing_rigid_functions():
    with pytest.raises(ValueError, match='exactly one'):
        a = cq.Assembly(name='multiple').add(cq.Workplane().newObject([cube().val(), cube().translate((3, 0, 0)).val()]), name='many')
        constrain(a, 'many', 'FixedPoint', param=(0, 0, 0))
    with pytest.raises(ValueError, match='exactly one'):
        constrain(pair(), 'moving@faces@|Z', 'FixedPoint', param=(0, 0, 0))
    with pytest.raises(ValueError, match='exactly one'):
        constrain(pair(), 'moving@faces@>Z and <Z', 'FixedPoint', param=(0, 0, 0))
    loc = rigid_location(lambda frame: frame.rotate((1, 2, 3), (1, 2, 4), 90).translate((4, 0, 0)))
    p = cq.Vertex.makeVertex(2, 2, 3).moved(loc).Center()
    assert p.toTuple() == pytest.approx((5, 3, 3))
    with pytest.raises(ValueError, match='four datum'):
        rigid_location(lambda frame: frame.newObject(frame.vals()[:1]))
    with pytest.raises(ValueError, match='right-handed'):
        rigid_location(lambda frame: frame.newObject([cq.Vertex.makeVertex(-s.Center().x, s.Center().y, s.Center().z) for s in frame.vals()]))


def test_kernel_failure_is_inconclusive_not_zero(monkeypatch):
    def fail(*args, **kwargs):
        raise RuntimeError('boolean failure')
    monkeypatch.setattr(cq.Shape, 'intersect', fail)
    r = check_pair(cube(), cube(), PairRequirement('Clear', max_overlap_mm3=1e-8))
    assert not r.calculation_completed and r.status == 'inconclusive'
    assert r.overlap_mm3 is None and 'boolean failure' in r.error


def test_translation_coarse_sampling_can_miss_intermediate_collision():
    c = Configuration.explicit(pair(-4), name='crossing')
    req = PairRequirement('Rigid crossing prohibited', max_overlap_mm3=1e-8, min_gap_mm=0)
    args = dict(transform=lambda t: cq.Location((t, 0, 0)), parameter='travel', units='mm')
    coarse = sample_motion(c, 'moving', 'fixed', req, samples=(0, 8), **args)
    fine = sample_motion(c, 'moving', 'fixed', req, samples=(0, 4, 8), **args)
    assert coarse.status == 'passed' and 'not continuous' in coarse.limits
    assert fine.status == 'failed' and fine.to_dict()['first_failure']['parameter'] == 4
    assert fine.to_dict()['maximum_sampled_overlap']['mm3'] == pytest.approx(8)
    assert c.shape('moving').Center().x == -4
    json.dumps(fine.to_dict())


def test_rotation_obstruction_and_world_delta_pose():
    a = cq.Assembly(name='rotating').add(cube(1).translate((4, 0, 0)), name='arm').add(
        cube(1).translate((0, 4, 0)), name='stop')
    c = Configuration.explicit(a, name='rotate')
    r = sample_motion(c, 'arm', 'stop', PairRequirement('Rotation obstruction', max_overlap_mm3=1e-8),
                      samples=(0, 90, 180), transform=lambda t: cq.Location((0, 0, 0), (0, 0, t)), parameter='angle', units='deg')
    assert r.status == 'failed' and r.to_dict()['first_failure']['parameter'] == 90


@pytest.mark.parametrize('kwargs', [{}, {'max_gap_mm': -1}, {'max_overlap_mm3': float('nan')},
                                   {'min_gap_mm': 1, 'max_gap_mm': .5}, {'min_gap_mm': 1, 'min_overlap_mm3': 1}])
def test_invalid_intent(kwargs):
    with pytest.raises(ValueError):
        PairRequirement('invalid', **kwargs)


def test_invalid_references_geometry_names_and_motion():
    with pytest.raises(ValueError):
        pair().add(cube(), name='moving')
    with pytest.raises(ValueError, match='name'):
        Configuration.explicit(cq.Assembly().add(cube(), name='box'), name='bad')
    with pytest.raises(TypeError):
        check_pair(cq.Workplane().newObject([cq.Vector()]), cube(), PairRequirement('gap', min_gap_mm=0))
    c = Configuration.explicit(pair(), name='pose')
    with pytest.raises(KeyError):
        c.check('misspelled', 'fixed', PairRequirement('clear', max_overlap_mm3=0))
    for samples in ((), (0, 0), (1, 0), (0, float('nan'))):
        with pytest.raises(ValueError):
            sample_motion(c, 'moving', 'fixed', PairRequirement('clear', max_overlap_mm3=0), samples=samples,
                          transform=lambda t: cq.Location(), parameter='x', units='mm')


def test_physical_questions_and_questionstudy_accept_positioned_geometry():
    from physical_analysis import StructuralQuestion, Support, SurfaceForce, Region, PETG_SCREEN, QuestionStudy
    c = Configuration.explicit(pair(), name='physical_fixture')
    q = StructuralQuestion(name='explicit_fixture', part=c.shape('moving'), material=PETG_SCREEN,
        supports=(Support(Region.plane('x', 3)),), forces=(SurfaceForce(Region.plane('x', 5), (1, 0, 0)),),
        mesh_size_mm=1)
    case = q.build_case()
    assert next(iter(case.parts.values())).shape.Center().x == 4
    study = QuestionStudy(q, decision='Fixture displacement resolution', metrics=('max_displacement_mm',),
                          relative_tolerance=.1, mesh_levels=1)
    assert study.question is q
