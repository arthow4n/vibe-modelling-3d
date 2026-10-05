"""Read-only configurations backed by native CadQuery assemblies, in mm."""
from dataclasses import dataclass, field
import math
import re
from types import MappingProxyType
import cadquery as cq


def geometry(value):
    """Strict geometry normalization; never drop non-shape Workplane entries."""
    if isinstance(value, cq.Shape):
        return value
    if isinstance(value, cq.Workplane):
        shapes = value.vals()
        if not shapes or not all(isinstance(s, cq.Shape) for s in shapes):
            raise TypeError('Expected a nonempty Workplane containing only shapes')
        return shapes[0] if len(shapes) == 1 else cq.Compound.makeCompound(shapes)
    raise TypeError('Expected CadQuery Shape or Workplane')


def rigid_location(transform):
    """Adapt an existing rigid Workplane placement function without copying its rule.

    The function must preserve four vertex entries and order. A 1 mm right-handed
    datum frame qualifies rigidness to 1e-9 in basis-vector arithmetic (not a CAD
    clearance tolerance). Geometry-dependent placement such as bed() needs the
    actual part and should stay in its original builder instead.
    """
    points = ((0, 0, 0), (1, 0, 0), (0, 1, 0), (0, 0, 1))
    placed = transform(cq.Workplane().newObject([cq.Vertex.makeVertex(*p) for p in points]))
    if not isinstance(placed, cq.Workplane) or len(placed.vals()) != 4 or not all(
            isinstance(s, cq.Vertex) for s in placed.vals()):
        raise ValueError('Rigid placement must preserve four datum vertices and their order')
    origin, *ends = [s.Center() for s in placed.vals()]
    axes = [p-origin for p in ends]
    errors = [abs(a.dot(b)-(1 if i == j else 0)) for i, a in enumerate(axes) for j, b in enumerate(axes)]
    errors.append(abs(axes[0].cross(axes[1]).dot(axes[2])-1))
    if not all(math.isfinite(v) and v <= 1e-9 for v in errors):
        raise ValueError('Placement does not preserve a rigid right-handed frame')
    return cq.Location(cq.Plane(origin, xDir=axes[0], normal=axes[2]))


def constrain(assembly, first, kind, *, second=None, param=None):
    """Declare a native constraint, rejecting empty or multiple selector matches.

    Uses CadQuery's own query grammar/selectors. Explicit datum-shape overloads
    can continue to use Assembly.constrain directly.
    """
    from cadquery.assembly import _grammar
    for reference in (first,) if second is None else (first, second):
        query = _grammar.parse_string(reference, True)
        obj = assembly.objects[query.name].obj  # exact native identity, no aliases
        if isinstance(obj, cq.Workplane) and query.tag:
            selected = obj._getTagged(query.tag)
        else:
            geometry(obj)  # validate without changing native selection cardinality
            selected = cq.Workplane().add(obj)
        if query.selector:
            selected = getattr(selected, query.selector_kind)(query.selector)
        if len(selected.vals()) != 1 or not isinstance(selected.val(), cq.Shape):
            raise ValueError(f'Constraint reference must select exactly one shape: {reference!r}')
    if second is None:
        return assembly.constrain(first, kind, param)
    return assembly.constrain(first, second, kind, param)


def _validate_tree(assembly):
    if not isinstance(assembly, cq.Assembly):
        raise TypeError('Expected cq.Assembly')
    seen = set()
    def visit(node):
        if id(node) in seen:
            raise ValueError('Assembly contains a repeated node or cycle')
        seen.add(id(node))
        if not re.fullmatch(r'[A-Za-z][A-Za-z0-9_]*', node.name):
            raise ValueError(f'Explicit CadQuery-compatible component name required: {node.name!r}')
        if not all(math.isfinite(v) for triplet in node.loc.toTuple() for v in triplet):
            raise ValueError(f'Nonfinite placement: {node.name}')
        if abs(node.loc.wrapped.Transformation().ScaleFactor()-1) > 1e-12:
            raise ValueError(f'Assembly placement must be rigid: {node.name}')
        if len({c.name for c in node.children}) != len(node.children):
            raise ValueError('Duplicate sibling names')
        if node.obj is not None:
            s = geometry(node.obj)
            if s.isNull() or not s.isValid():
                raise ValueError(f'Invalid geometry: {node.name}')
        for child in node.children:
            visit(child)
    visit(assembly)
    if not any(True for _ in assembly):
        raise ValueError('Empty assembly')
    paths = [path[len(assembly.name)+1:] if path.startswith(assembly.name+'/') else path
             for _, path, _, _ in assembly]
    if len(set(paths)) != len(paths):
        raise ValueError('Ambiguous root-relative component identities')


def _copy(assembly, *, geometry_copy=False):
    # Native _copy preserves hierarchy/placements, but drops constraints in 2.7.
    clone = assembly._copy()
    definitions = {}
    def visit(original, copied):
        copied.loc = cq.Location(original.loc.wrapped.Transformation())
        copied.constraints = list(original.constraints)
        if geometry_copy and original.obj is not None:
            key = id(original.obj)
            if key not in definitions:
                definitions[key] = geometry(original.obj).copy()
            copied.obj = definitions[key]
        for a, b in zip(original.children, copied.children):
            visit(a, b)
        # Native _copy also loses full descendant lookup paths in 2.7. Rebuild
        # its own lookup index from its own hierarchy, using native flattening.
        copied.objects = {copied.name: copied}
        for child in copied.children:
            copied.objects.update(child._flatten())
    visit(assembly, clone)
    return clone


class Configuration:
    """Snapshot: exact root-relative paths, no short-name guessing or live updates.

    Use explicit() or solve().require_configuration(). Native assemblies remain
    the sole hierarchy/placement representation. shape() returns an isolated copy.
    """
    def __init__(self, assembly, *, name, kind, parameters, resolution=None):
        if not isinstance(name, str) or not name:
            raise ValueError('Configuration name required')
        if kind not in ('operating', 'intermediate', 'print'):
            raise ValueError('kind must be operating, intermediate or print')
        # Operating inputs are descriptive scalar values, not a geometry cache key.
        parameters = dict(parameters or {})
        if any(not isinstance(k, str) or not isinstance(v, (str, bool, int, float))
               or isinstance(v, float) and not math.isfinite(v) for k, v in parameters.items()):
            raise ValueError('Parameters must be finite scalars with string keys')
        _validate_tree(assembly)
        self._assembly = _copy(assembly, geometry_copy=True)
        self.name, self.kind = name, kind
        self.parameters = MappingProxyType(parameters)
        self.resolution = resolution

    @classmethod
    def explicit(cls, assembly, *, name, kind='operating', parameters=None):
        _validate_tree(assembly)
        if any(node.constraints for _, node in assembly.traverse()):
            raise ValueError('Constraint declarations require solve(); locations would be initial guesses')
        return cls(assembly, name=name, kind=kind, parameters=parameters)

    @property
    def names(self):
        return tuple(self._key(path) for _, path, _, _ in self._assembly)

    def _key(self, path):
        root = self._assembly.name
        return path[len(root)+1:] if path.startswith(root+'/') else path

    def shape(self, component):
        for shape, path, location, _ in self._assembly:
            if self._key(path) == component:
                return shape.moved(location).copy()
        raise KeyError(f'{self.name}: unknown component {component!r}; available: {self.names}')

    def location(self, component):
        for _, path, location, _ in self._assembly:
            if self._key(path) == component:
                return cq.Location(location.wrapped.Transformation())
        raise KeyError(f'{self.name}: unknown component {component!r}')

    def assembly(self):
        """Native copy for the existing evaluator; resolved locations are retained."""
        return _copy(self._assembly, geometry_copy=True)

    def check(self, first, second, requirement):
        from .queries import check_pair
        if first == second:
            raise ValueError('Pair requires distinct component identities')
        return check_pair(self.shape(first), self.shape(second), requirement,
                          first=first, second=second, configuration=self.name)


@dataclass(frozen=True)
class Resolution:
    status: str
    diagnostics: dict
    residuals: tuple = ()
    configuration: Configuration | None = field(default=None, repr=False)

    def require_configuration(self):
        if self.configuration is None:
            raise ValueError(f'{self.status}: {self.diagnostics}')
        return self.configuration


def solve(assembly, *, name, position_tolerance_mm, rotation_tolerance_deg,
          kind='operating', parameters=None):
    """Native solve with a qualified determinacy policy and independent residuals.

    Flat native constraints: Fixed anchors; FixedRotation for other orientations;
    FixedPoint or zero-distance Point connections to translation-anchored nodes.
    Other native constraint networks remain unsupported here (use CQ experiments).
    No arbitrary implicit anchoring and no inference of product mechanics.
    """
    _validate_tree(assembly)
    for value in (position_tolerance_mm, rotation_tolerance_deg):
        if not math.isfinite(value) or value <= 0:
            raise ValueError('Positive finite residual tolerances required')
    diagnostics = dict(cadquery=cq.__version__, position_tolerance_mm=position_tolerance_mm,
                       rotation_tolerance_deg=rotation_tolerance_deg,
                       physical_validity='not established')
    def stop(status, reason):
        return Resolution(status, {**diagnostics, 'reason': reason})
    if not assembly.constraints:
        return stop('invalid', 'No native constraints')
    if any(c.children or c.constraints for c in assembly.children):
        return stop('unsupported', 'Constraint solving is qualified only for flat assemblies; explicit hierarchies work')
    nodes = {c.name: c for c in assembly.children}
    if assembly.obj is not None:
        nodes[assembly.name] = assembly
    constraints = assembly.constraints
    allowed = {'Fixed', 'FixedRotation', 'FixedPoint', 'Point'}
    if any(c.kind not in allowed or c.kind == 'Point' and c.param not in (None, 0) for c in constraints):
        return stop('unsupported', 'Determinacy is qualified only for Fixed/FixedRotation/FixedPoint/coincident Point')
    if any(n not in nodes for c in constraints for n in c.objects):
        return stop('invalid', 'Constraint references a missing component')
    if any(c.kind in ('FixedPoint', 'FixedRotation') and (
            c.param is None or len(c.param) != 3 or not all(math.isfinite(v) for v in c.param))
           for c in constraints):
        return stop('invalid', 'Unary point/rotation target requires three finite coordinates')
    fixed = {c.objects[0] for c in constraints if c.kind == 'Fixed'}
    if assembly.obj is not None:
        fixed.add(assembly.name)  # native always locks a geometric root
    if not fixed:
        return stop('inconclusive', 'Explicit Fixed anchor required; native implicit first-entity locking is ambiguous')
    oriented = fixed | {c.objects[0] for c in constraints if c.kind == 'FixedRotation'}
    located = fixed | {c.objects[0] for c in constraints if c.kind == 'FixedPoint'}
    edges = [c.objects for c in constraints if c.kind == 'Point']
    while True:
        extended = located | {n for edge in edges if any(m in located for m in edge) for n in edge}
        if extended == located:
            break
        located = extended
    if set(nodes) - (oriented & located):
        return stop('inconclusive', f'Unqualified free placements: {sorted(set(nodes) - (oriented & located))}')
    # Native root-frame rebasing complicates global unary targets; keep qualified
    # solver coordinates unambiguous, while explicit snapshots support any root loc.
    if assembly.loc.toTuple() != cq.Location().toTuple():
        return stop('unsupported', 'Native solve requires identity root placement in the qualified policy')
    candidate = _copy(assembly)
    try:
        candidate.solve()
        stats = candidate._solve_result
        diagnostics.update(success=bool(stats['success']), return_status=stats['return_status'],
                           iterations=stats['iter_count'],
                           objective=float(stats['opti'].value(stats['opti'].f)))
        if not stats['success']:
            return stop('failed', 'Native solver did not report success')
        residuals = []
        for i, c in enumerate(constraints):
            placements = [candidate.objects[n].loc for n in c.objects]
            if c.kind in ('Point', 'FixedPoint'):
                points = [s.moved(loc * subloc).Center() for s, loc, subloc in zip(c.args, placements, c.sublocs)]
                target = points[1] if c.kind == 'Point' else cq.Vector(c.param)
                value = (points[0]-target).Length
                limit, units = position_tolerance_mm, 'mm'
            elif c.kind == 'FixedRotation':
                target = cq.Location((0, 0, 0), tuple(math.degrees(v) for v in c.param))
                relative = target.inverse * placements[0]
                q = relative.wrapped.Transformation().GetRotation()
                value = math.degrees(abs(q.GetRotationAngle()))
                limit, units = rotation_tolerance_deg, 'deg'
            else:
                # Fixed native placements are parameters, not optimization variables.
                continue
            residuals.append(dict(constraint=i, kind=c.kind, components=c.objects,
                                  value=value, limit=limit, units=units,
                                  passes=math.isfinite(value) and value <= limit))
        if not all(r['passes'] for r in residuals):
            return Resolution('residual_failed', diagnostics, tuple(residuals))
        config = Configuration(candidate, name=name, kind=kind, parameters=parameters,
                               resolution={**diagnostics, 'residuals': residuals})
        return Resolution('resolved', diagnostics, tuple(residuals), config)
    except Exception as exc:
        return stop('failed', f'{type(exc).__name__}: {exc}')
