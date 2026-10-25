"""Headless orthographic SVG/PNG views, using OpenCASCADE's shared-scene HLR.

No filesystem writes, cache, scheduler, geometry mutation or engineering checks.
"""
import hashlib
import io
import json
import math
import textwrap
import xml.etree.ElementTree as ET

import cadquery as cq
from assembly_geometry import Configuration
from assembly_geometry.configuration import geometry
from .spec import Inspection, Anchor, Label, Arrow, Highlight, vector, view_to_dict

NS = 'http://www.w3.org/2000/svg'
ET.register_namespace('', NS)


def node(parent, tag, **attrs):
    return ET.SubElement(parent, '{'+NS+'}'+tag,
                         {k.replace('_', '-'): str(v) for k, v in attrs.items()})


def text(parent, x, y, value, **attrs):
    el = node(parent, 'text', **dict(dict(x=x, y=y, font_family='sans-serif', font_size=13,
                                        fill='#253641'), **attrs))
    el.text = value
    return el


def annotation_text(parent, x, y, value, color):
    # CairoSVG does not implement SVG paint-order. Draw the halo first and then
    # unstroked glyphs, so labels remain readable in both SVG and actual PNG.
    text(parent, x, y, value, fill='white', stroke='white', stroke_width=3)
    text(parent, x, y, value, fill=color)


def subject_parts(subject):
    if isinstance(subject, cq.Assembly):
        subject = Configuration.explicit(subject, name='inspection')
    if isinstance(subject, Configuration):
        return {name: subject.shape(name) for name in subject.names}, {
            'name': subject.name, 'kind': subject.kind, 'parameters': dict(subject.parameters)}, {
                name: subject.location(name).toTuple() for name in subject.names}
    return {'subject': geometry(subject).copy()}, None, {'subject': cq.Location().toTuple()}


def world_point(point, locations):
    if isinstance(point, Anchor):
        if point.component not in locations:
            raise KeyError(f'Unknown anchor component {point.component!r}; available: {tuple(locations)}')
        return cq.Vertex.makeVertex(*point.point).moved(cq.Location(*locations[point.component])).Center().toTuple()
    return point


def shape_digest(shape):
    from OCP.BRepTools import BRepTools
    from OCP.TopTools import TopTools_FormatVersion
    stream = io.BytesIO()
    BRepTools.Write_s(shape.wrapped, stream, False, False,
                     TopTools_FormatVersion.TopTools_FormatVersion_VERSION_3)
    return hashlib.sha256(stream.getvalue()).hexdigest()


def section_shape(shape, section):
    """Cut an inspection copy. Infinite plane is bounded only for the Boolean tool."""
    if section is None:
        return shape.copy()
    plane = cq.Plane(origin=section.origin, normal=section.normal)
    if section.mode == 'planar':
        values = cq.Workplane(plane).add(shape).section().vals()
        return cq.Compound.makeCompound([v for v in values if isinstance(v, cq.Shape)])
    bb = shape.BoundingBox()
    from itertools import product
    extent = max((cq.Vector(*p)-vector(section.origin)).Length for p in
                 product((bb.xmin, bb.xmax), (bb.ymin, bb.ymax), (bb.zmin, bb.zmax)))+1
    sign = 1 if section.keep == 'positive' else -1
    tool = (cq.Workplane(plane).box(2*extent, 2*extent, extent, centered=(True, True, False))
            .translate((vector(section.normal).normalized()*(0 if sign == 1 else -extent)).toTuple()))
    return shape.intersect(tool.val())


def prepare(inspection):
    if not isinstance(inspection, Inspection):
        raise TypeError('Expected Inspection')
    parts, config, locations = subject_parts(inspection.subject)
    view = inspection.view
    # Resolve every declared anchor, even outside the frame or on a component
    # later removed by the section. Missing references cannot silently vanish.
    anchors = list(view.frame.region.corners()) if view.frame.region else []
    for a in view.annotations:
        anchors.extend([a.point] if isinstance(a, Label) else
                       [a.start, a.end] if isinstance(a, Arrow) else a.region.corners())
    for anchor in anchors:
        world_point(anchor, locations)
    names = view.components or tuple(parts)
    if any(n not in parts for n in names):
        raise KeyError(f'Unknown component; available: {tuple(parts)}')
    if any(n not in names for n, _ in view.colors):
        raise ValueError('Colors must reference selected components')
    selected = {n: parts[n] for n in names}
    identity = {n: shape_digest(s) for n, s in selected.items()}
    displayed = {}; removed = []
    for name, shape in selected.items():
        if shape.isNull() or not shape.isValid():
            raise ValueError(f'Invalid inspection component {name}')
        cut = section_shape(shape, view.section)
        if cut.isNull() or not cut.Edges():
            removed.append(name)
        elif not cut.isValid():
            raise ValueError(f'Invalid display section for {name}')
        else:
            displayed[name] = cut.transformShape(view.camera.matrix())
    if not displayed:
        raise ValueError('Empty section/subject: no edges to display')
    settings = dict(view=view_to_dict(view), purpose=inspection.purpose, title=inspection.title,
                    question_ids=inspection.question_ids, configuration=config,
                    subject_sha256=identity, component_locations=locations, removed_by_section=removed)
    return displayed, settings


def paths(parts, *, planar, show_hidden):
    from cadquery.occ_impl.exporters.svg import getPaths
    if planar:
        return {name: getPaths([s], []) for name, s in parts.items()}
    from OCP.HLRBRep import HLRBRep_Algo, HLRBRep_HLRToShape
    from OCP.HLRAlgo import HLRAlgo_Projector
    from OCP.gp import gp_Ax2, gp_Pnt, gp_Dir
    from OCP.BRepLib import BRepLib
    hlr = HLRBRep_Algo()
    for s in parts.values():
        hlr.Add(s.wrapped)
    # Explicit X direction preserves our world-to-camera frame (no implicit roll).
    hlr.Projector(HLRAlgo_Projector(gp_Ax2(gp_Pnt(), gp_Dir(0, 0, 1), gp_Dir(1, 0, 0))))
    hlr.Update(); hlr.Hide()
    converter = HLRBRep_HLRToShape(hlr)
    def shapes(methods, shape):
        result = []
        for method in methods:
            raw = getattr(converter, method)(shape.wrapped)
            if not raw.IsNull():
                # CadQuery's SVG exporter requires this before sampling HLR curves.
                BRepLib.BuildCurves3d_s(raw, 1e-6)
                result.append(cq.Shape(raw))
        return result
    return {name: getPaths(shapes(('VCompound', 'Rg1LineVCompound', 'OutLineVCompound'), s),
                           shapes(('HCompound', 'OutLineHCompound'), s) if show_hidden else [])
            for name, s in parts.items()}


def render(inspection, *, width=1000, height=750, prepared=None):
    """Return (SVG bytes, resolved settings). Pixel coordinates are also reported."""
    if any(not isinstance(v, int) or isinstance(v, bool) or not 200 <= v <= 4096 for v in (width, height)):
        raise ValueError('Inspection dimensions must be integers from 200 to 4096')
    parts, settings = prepare(inspection) if prepared is None else prepared
    view = inspection.view
    boxes = [s.BoundingBox() for s in parts.values()]
    full = (min(b.xmin for b in boxes), min(b.ymin for b in boxes),
            max(b.xmax for b in boxes), max(b.ymax for b in boxes))
    bounds = full
    if view.frame.region:
        pts = [view.camera.project(world_point(p, settings['component_locations'])) for p in view.frame.region.corners()]
        bounds = (min(p[0] for p in pts), min(p[1] for p in pts), max(p[0] for p in pts), max(p[1] for p in pts))
        if bounds[2] < full[0] or bounds[0] > full[2] or bounds[3] < full[1] or bounds[1] > full[3]:
            raise ValueError('Framing region is outside the projected subject')
    margin = view.frame.margin_mm
    xmin, ymin, xmax, ymax = bounds[0]-margin, bounds[1]-margin, bounds[2]+margin, bounds[3]+margin
    if xmax-xmin < 1e-10 or ymax-ymin < 1e-10:
        raise ValueError('Degenerate projected frame: choose a different camera or positive margin')
    purpose_lines = textwrap.wrap(inspection.purpose, max(15, (width-40)//7))
    legend = [f'{name}: {dict(view.colors).get(name, "#263c40")}' for name in parts]
    legend_lines = textwrap.wrap('Components — '+'; '.join(legend), max(15, (width-40)//7))
    top, bottom = 40+17*len(purpose_lines), 20+16*len(legend_lines)
    if top+bottom+40 >= height:
        raise ValueError('Image too short for captions; increase height')
    scale = min((width-48)/(xmax-xmin), (height-top-bottom-24)/(ymax-ymin))
    tx = width/2-scale*(xmin+xmax)/2
    ty = top+(height-top-bottom)/2+scale*(ymin+ymax)/2
    def pixel(p):
        x, y, _ = view.camera.project(world_point(p, settings['component_locations']))
        return tx+scale*x, ty-scale*y
    root = ET.Element('{'+NS+'}svg', width=str(width), height=str(height), viewBox=f'0 0 {width} {height}')
    node(root, 'rect', width=width, height=height, fill='white')
    text(root, 20, 25, inspection.title or 'CAD inspection')
    for i, line in enumerate(purpose_lines):
        text(root, 20, 46+17*i, line)
    defs = node(root, 'defs')
    clip = node(defs, 'clipPath', id='scene-clip')
    node(clip, 'rect', x=16, y=top, width=width-32, height=height-top-bottom)
    clipped = node(root, 'g', clip_path='url(#scene-clip)')
    projected = node(clipped, 'g', transform=f'translate({tx} {ty}) scale({scale} {-scale})', fill='none')
    curves = paths(parts, planar=view.section is not None and view.section.mode == 'planar', show_hidden=view.show_hidden)
    for name, (hidden, visible) in curves.items():
        group = node(projected, 'g', data_component=name, stroke=dict(view.colors).get(name, '#263c40'), stroke_width=1.2/scale)
        for d in hidden:
            node(group, 'path', d=d, stroke_dasharray=f'{3/scale} {3/scale}', stroke_opacity='.35')
        for d in visible:
            node(group, 'path', d=d)
    annotation_pixels = []
    for index, a in enumerate(view.annotations):
        if isinstance(a, Label):
            x, y = pixel(a.point)
            lx, ly = x+a.offset_px[0], y+a.offset_px[1]
            node(clipped, 'line', x1=lx, y1=ly, x2=x, y2=y, stroke=a.color)
            node(clipped, 'circle', cx=x, cy=y, r=3, fill=a.color)
            annotation_text(clipped, lx, ly-3, a.text, a.color)
            annotation_pixels.append(dict(kind='label', point=(x, y), text=a.text))
        elif isinstance(a, Arrow):
            start, end = pixel(a.start), pixel(a.end)
            marker = node(defs, 'marker', id=f'arrow-{index}', viewBox='0 0 10 10', refX=9, refY=5,
                          markerWidth=7, markerHeight=7, orient='auto-start-reverse')
            node(marker, 'path', d='M 0 0 L 10 5 L 0 10 z', fill=a.color)
            node(clipped, 'line', x1=start[0], y1=start[1], x2=end[0], y2=end[1],
                 stroke=a.color, stroke_width=1.5, marker_end=f'url(#arrow-{index})')
            if a.text:
                annotation_text(clipped, start[0]+5, start[1]-6, a.text, a.color)
            annotation_pixels.append(dict(kind='arrow', start=start, end=end, text=a.text))
        elif isinstance(a, Highlight):
            pts = [pixel(p) for p in a.region.corners()]
            x, y = min(p[0] for p in pts), min(p[1] for p in pts)
            w, h = max(p[0] for p in pts)-x, max(p[1] for p in pts)-y
            node(clipped, 'rect', x=x, y=y, width=w, height=h, fill='none', stroke=a.color, stroke_dasharray='5 3')
            if a.text:
                annotation_text(clipped, x+4, y+15, a.text, a.color)
            annotation_pixels.append(dict(kind='highlight', rectangle=(x, y, w, h), text=a.text))
    for i, line in enumerate(legend_lines):
        text(root, 20, height-bottom+16+16*i, line)
    resolved = dict(settings, width=width, height=height, projected_frame_mm=(xmin, ymin, xmax, ymax),
                    pixels_per_mm=scale, translation_px=(tx, ty), annotation_pixels=annotation_pixels,
                    limits='Orthographic line drawing; annotations are overlays, not visibility/contact proof. Rendering success is not engineering PASS.')
    node(root, 'metadata').text = json.dumps(resolved, sort_keys=True)
    return ET.tostring(root, encoding='utf-8'), resolved


def png(svg):
    import cairosvg
    return cairosvg.svg2png(bytestring=svg, background_color='white')


def sheet(views, *, columns=2):
    """Compose existing view SVGs without rebuilding geometry or recomputing checks."""
    if not views or not isinstance(columns, int) or columns < 1:
        raise ValueError('Sheet needs views and a positive column count')
    children = [ET.fromstring(svg) for svg in views]
    w = max(float(c.get('width')) for c in children)
    h = max(float(c.get('height')) for c in children)
    columns = min(columns, len(children))
    root = ET.Element('{'+NS+'}svg', width=str(w*columns), height=str(h*math.ceil(len(children)/columns)))
    for i, child in enumerate(children):
        # IDs are document-global, even in nested SVGs; isolate each view's clips.
        for element in child.iter():
            for key, value in list(element.attrib.items()):
                if key == 'id':
                    element.set(key, f'v{i}-{value}')
                elif 'url(#' in value:
                    element.set(key, value.replace('url(#', f'url(#v{i}-'))
        child.set('x', str((i%columns)*w)); child.set('y', str((i//columns)*h))
        root.append(child)
    return ET.tostring(root, encoding='utf-8')
