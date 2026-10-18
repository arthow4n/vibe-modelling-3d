"""Locate meshing limitations on a retained actual CAD fixture, with native logs.

Diagnostic only: does not qualify a substitute geometry or publish product CAD.
"""
import argparse
import sys
from pathlib import Path
from physical_analysis.backends.structural import runtime_environment
from execution.process import run
if len(sys.argv)<2 or sys.argv[1] != "--worker":
    answer=run([sys.executable,str(Path(__file__).resolve()),"--worker",*sys.argv[1:]], env=runtime_environment())
    raise SystemExit(answer.returncode)
sys.argv.pop(1)
import gmsh
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('brep')
p.add_argument('--mesh',type=float,required=True)
p.add_argument('--optimizer',choices=('HighOrder','HighOrderFastCurving','none'),required=True)
a=p.parse_args()
gmsh.initialize()
try:
    gmsh.option.setNumber('General.NumThreads',1)
    gmsh.model.add('probe')
    print('Import retained BREP',flush=True)
    gmsh.model.occ.importShapes(a.brep)
    gmsh.model.occ.synchronize()
    print('Imported; surface count',len(gmsh.model.getEntities(2)),flush=True)
    gmsh.option.setNumber('Mesh.MeshSizeMin',a.mesh)
    gmsh.option.setNumber('Mesh.MeshSizeMax',a.mesh)
    gmsh.option.setNumber('Mesh.ElementOrder',2)
    gmsh.model.mesh.generate(3)
    tags=gmsh.model.mesh.getElements(3)[1][0]
    quality=gmsh.model.mesh.getElementQualities(tags,'minDetJac')
    print('Before optimization minDetJac',min(quality),'nonpositive',sum(q<=0 for q in quality),flush=True)
    if a.optimizer!='none':
        gmsh.model.mesh.optimize(a.optimizer)
    quality=gmsh.model.mesh.getElementQualities(tags,'minDetJac')
    print('After optimization minDetJac',min(quality),'nonpositive',sum(q<=0 for q in quality),flush=True)
finally:
    gmsh.finalize()
