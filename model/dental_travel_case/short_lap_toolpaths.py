"""Review multiple extrusion paths through the load-bearing sleeve/pocket skin.

This is a targeted thin-section review, not a generic footprint/mesh audit.
Supplied pair centers X0/112, Y0; Orca's centered layout shifts X79/Y135.
"""
import hashlib
import json
from pathlib import Path
from physical_analysis.manufacturing import orca_linear_paths, section_coverage
from short_lap_checks import OUT
import short_lap_reinforced as design
from short_lap_reinforced import SELECTED_OVERLAP
from closure_research_checks import hashes


def inspect():
    receipt = json.loads((OUT/'short_lap_joint_test_slice.json').read_text())
    path = Path(receipt['slice']['kept_run_directory'])/'plate_1.gcode'
    paths = list(orca_linear_paths(path))
    swapped = [(y,x,ny,nx,z,w,r) for x,y,nx,ny,z,w,r in paths]
    d = design.build(SELECTED_OVERLAP)['dimensions']
    radius = d.sleeve_width/2
    sections = {}
    # Poses and layer heights are declared for the supplied print placement.
    cases = [('body_sleeve',30.,(79+radius-d.sleeve_wall,79+radius)),
             ('cap_pocket_skin',d.length-d.latch_z,(79+112+radius+d.detent+.15,79+112+d.width/2))]
    for name,z,span in cases:
        coverage = section_coverage(swapped,x_mm=135,z_mm=z,span_mm=span)
        crossings = []
        for x,y,nx,ny,height,width,role in paths:
            if abs(height-z)>1e-5 or abs(ny-y)<1e-9 or not min(y,ny)<=135<=max(y,ny):
                continue
            at = x+(nx-x)*(135-y)/(ny-y)
            if span[0] <= at <= span[1]:
                crossings.append(dict(x_mm=at,width_mm=width,role=role))
        assert len({round(p['x_mm'],4) for p in crossings}) >= 2,(name,crossings)
        # 0.15mm permits small path-width/contour approximation discrepancies;
        # a missing full nozzle-width path is consequential and would fail.
        assert coverage['uncovered_width_mm'] < .15,(name,coverage)
        sections[name] = dict(layer_mm=z,span_mm=span,crossings=crossings,coverage=coverage)
    data = dict(scope=__doc__+' Path-width approximation; not deposited bonding, modulus or strength calibration.',
        source_sha256=hashes(('short_lap_toolpaths.py','short_lap_refinement.py','short_lap_design.py','short_lap_reinforced.py')),
        slice_input_sha256=receipt['slice']['input_sha256'],
        gcode_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),sections=sections)
    (OUT/'paths.json').write_text(json.dumps(data,indent=2)+'\n')
    print(json.dumps(data),flush=True)


if __name__ == '__main__':
    inspect()
