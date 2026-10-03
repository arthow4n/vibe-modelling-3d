import sys
import cadquery as cq
from physical_analysis import AnalysisCase, Material, Region
c = AnalysisCase('execution_benchmark')
c.add_part('beam', cq.Workplane('XY').box(40, 8, 2, centered=False),
           material=Material('benchmark', 1200, .3, 'Numerical benchmark only'), mesh_size_mm=2)
c.fix('beam', Region.plane('x', 0))
c.apply_force('beam', Region.plane('x', 40), force_N=(0, 0, -.1))
r = c.run(sys.argv[1]).require_completed()
print(r.metrics['max_displacement_mm'])
