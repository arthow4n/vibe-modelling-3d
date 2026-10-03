"""Dedicated CAD motion screen benchmark; fixed exact distance/volume policy."""
import argparse,json,time
from pathlib import Path
import cadquery as cq
from physical_analysis import AnalysisCase,Material
from physical_analysis.motion import rigid_driver_clearance

p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);args=p.parse_args()
c=AnalysisCase('motion_benchmark');material=Material('screen',1200,.3,'Numerical timing fixture')
c.add_part('a',cq.Workplane('XY').box(5,5,5),material=material,mesh_size_mm=1)
c.add_part('b',cq.Workplane('XY').box(5,5,5).translate((0,30,0)),material=material,mesh_size_mm=1)
c.prescribe_motion('a',displacement_mm=(20,0,0));c.fix('b')
times=[]
for _ in range(3):
    started=time.perf_counter();answer=rigid_driver_clearance(c);times.append(time.perf_counter()-started)
args.output.write_text(json.dumps(dict(schema_version=1,samples_seconds=times,answer=answer),indent=2)+'\n')
print(times)
