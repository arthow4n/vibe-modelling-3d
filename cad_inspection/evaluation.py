"""Evaluator adapter: lazy object recipes, existing controlled-artifact cache."""
from pathlib import Path
from collections.abc import Mapping

from .spec import Inspection, safe_name, view_from_dict
from .checks import CheckedInspection
from .render import prepare, render, png, sheet


def evaluate(registry, subject, args, report, artifacts, retained, write, error):
    registry = {} if registry is None else registry
    if not isinstance(registry, Mapping):
        raise TypeError('inspections must map safe names to lazy callable factories')
    for name, factory in registry.items():
        safe_name(name)
        if not callable(factory):
            raise TypeError(f'Inspection {name} must be a callable factory')
    registry = dict(registry)
    for name, spec in args.get('inspection_specs', {}).items():
        if name in registry:
            raise ValueError(f'Duplicate inspection {name}')
        safe_name(name)
        # Bind values now, without capturing the loop variables by reference.
        registry[name] = lambda spec=spec: Inspection(subject, view_from_dict(spec['view']),
            spec['purpose'], spec.get('title', ''), tuple(spec.get('question_ids', ())))
    report['available_inspections'] = list(registry)
    requested = args.get('inspect', [])
    names = list(registry) if requested == ['all'] else requested
    if any(name not in registry for name in names):
        raise ValueError(f'Unknown inspection; available: {list(registry)}')
    report['inspections'] = []
    folder = Path(args['output_dir'])/(Path(args['file_path']).stem+'_inspections')
    svgs = []
    from execution.identity import digest
    implementation = {p.name: digest(p) for p in Path(__file__).parent.glob('*.py')}
    for name in names:
        try:
            recipe_reused = name in retained
            if name not in retained:
                item = registry[name]()
                checked = item if isinstance(item, CheckedInspection) else None
                inspection = checked.inspection if checked else item
                if not isinstance(inspection, Inspection):
                    raise TypeError('Inspection factory must return Inspection or CheckedInspection')
                retained[name] = (inspection, prepare(inspection), checked)
            inspection, prepared, checked = retained[name]
            # Geometry is content-bound even for scripts without --reuse. Check
            # diagnostics, names, poses and annotations are consequential too.
            evidence = checked.answer.to_dict() if checked else None
            key = dict(inspection=prepared[1], evidence=evidence,
                       selected_sample=checked.selected_sample if checked else None,
                       width=args['width'], height=args['height'],
                       implementation=implementation, runtime=args.get('runtime'))
            svg_key = dict(key, format='SVG')
            svg = None if args.get('fresh') else artifacts.read(svg_key)
            reused = svg is not None
            if svg is None:
                svg, settings = render(inspection, width=args['width'], height=args['height'], prepared=prepared)
                if not args.get('fresh'):
                    artifacts.store(svg_key, svg)
            else:
                import json
                import xml.etree.ElementTree as ET
                settings = json.loads(ET.fromstring(svg).find('{http://www.w3.org/2000/svg}metadata').text)
            png_key = dict(key, format='PNG')
            raster = None if args.get('fresh') else artifacts.read(png_key)
            reused = reused and raster is not None
            if raster is None:
                raster = png(svg)
                if not args.get('fresh'):
                    artifacts.store(png_key, raster)
            svg_path, path = folder/(name+'.svg'), folder/(name+'.png')
            write(svg_path, svg); write(path, raster)
            report['inspections'].append(dict(name=name, ok=True, path=str(path), svg_path=str(svg_path),
                reused=reused, recipe_reused=recipe_reused,
                evidence_reused=recipe_reused if checked else None, settings=settings, evidence=evidence,
                selected_sample=checked.selected_sample if checked else None))
            svgs.append(svg)
        except Exception as exc:
            report['inspections'].append(dict(name=name, ok=False))
            error('inspection', exc, inspection=name)
    if len(names) > 1 and len(svgs) == len(names):
        try:
            svg = sheet(svgs)
            path, svg_path = folder/'sheet.png', folder/'sheet.svg'
            write(svg_path, svg); write(path, png(svg))
            report['inspection_sheet'] = dict(ok=True, path=str(path), svg_path=str(svg_path), names=names)
        except Exception as exc:
            error('inspection_sheet', exc)
