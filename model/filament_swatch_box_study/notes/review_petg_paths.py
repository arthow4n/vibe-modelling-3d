"""Targeted leaf-section coverage from the retained Orca diagnostic run.

This checks the solid-stem idealization, not bed fit or ordinary wall paths.
Shared path capsule review; no independent G-code printer-envelope audit.
"""
import json
import sys
from pathlib import Path
from physical_analysis.manufacturing import orca_linear_paths, section_coverage

gcode = Path(sys.argv[1])
paths = list(orca_linear_paths(gcode))
# Orca centered the unchanged symmetric 59.6 x 44.4 footprint at (135,135).
# Review middle slot's stem midway up its uniform section, before any pad.
reviews = []
for x in (-5, 7, 19):
    reviews.append(dict(leaf='front', x_mm=x+135, z_mm=8.0,
        **section_coverage(paths, x_mm=x+135, z_mm=8.0, span_mm=(136.4,137.4))))
# Swap path X/Y for a transverse X section through the side leaf.
swapped = [(y,x,ny,nx,z,w,r) for x,y,nx,ny,z,w,r in paths]
reviews.append(dict(leaf='side', y_mm=134.3, z_mm=8.0,
    **section_coverage(swapped, x_mm=134.3, z_mm=8.0, span_mm=(161,161.8))))
assert all(r['uncovered_width_mm'] < .05 for r in reviews), reviews
out = dict(scope='Four uniform-stem local sections at Z=8 mm; does not establish layer bonding',
           sections=reviews, result='Each selected stem section filled within 0.05 mm')
Path(__file__).with_name('petg_leaf_paths.json').write_text(json.dumps(out, indent=2)+'\n')
print(json.dumps(out, indent=2))
