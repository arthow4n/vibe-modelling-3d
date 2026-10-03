"""Dedicated measured numerical kernels, with deterministic inputs and provenance."""
import argparse
import hashlib
import json
from pathlib import Path
import statistics
import time
import numpy as np
from physical_analysis.backends.mesh import traction_weights
from physical_analysis.backends.polyfem_output import map_points,principal_strain,Tet4GreenStrain
from physical_analysis.manufacturing import orca_linear_paths


def benchmark(function,repeats=5):
    function()  # dependency/load warmup reported separately by full command benchmarks
    times=[]
    for _ in range(repeats):
        start=time.perf_counter();answer=function();times.append(time.perf_counter()-start)
    return dict(median_seconds=statistics.median(times),samples_seconds=times)


def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);args=p.parse_args()
    nodes={};faces=[]
    points=np.array(((0,0,0),(1,0,0),(0,1,0),(.5,0,.02),(.5,.5,.03),(0,.5,.01)))
    for i in range(2000):
        ids=[i*6+j for j in range(6)]
        nodes.update({n:(point+[i*2,0,0]).tolist() for n,point in zip(ids,points)})
        faces.append((i,1,ids))
    rng=np.random.default_rng(47);actual=rng.random((20000,3));wanted=actual[rng.permutation(len(actual))]
    mesh={'points_mm':np.array([[0,0,0],[1,0,0],[0,1,0],[0,0,1]]).tolist(),'tets':[[0,1,2,3]]}
    displacement=np.array([[0,0,0],[.01,0,0],[0,.02,0],[0,0,.03]])
    prepared=Tet4GreenStrain(mesh)
    result=dict(schema_version=1,traction_2000=benchmark(lambda:traction_weights(faces,nodes)),
        mapping_20000=benchmark(lambda:map_points(wanted,actual)),
        strain_1000_frames=benchmark(lambda:[principal_strain(mesh,displacement) for _ in range(1000)]),
        prepared_strain_1000_frames=benchmark(lambda:[prepared.principal(displacement) for _ in range(1000)]),
        identity={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path('physical_analysis/backends/mesh.py'),Path('physical_analysis/backends/polyfem_output.py')]})
    args.output.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
