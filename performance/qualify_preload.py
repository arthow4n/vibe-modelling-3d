"""Native forkserver compatibility probe; run in a fresh parent per preload set."""
import argparse
import json
import multiprocessing as mp
import os
from pathlib import Path
import sys
import time


def trial(connection, gmsh_enabled):
    started=time.perf_counter()
    import cadquery as cq
    shape=cq.Workplane('XY').box(20,12,5).edges('|Z').fillet(1).val()
    moved=shape.translate((0,0,1))
    answer=dict(valid=shape.isValid(), intersection=shape.intersect(moved).Volume(),
        distance=shape.distance(moved), threads=len(list(Path('/proc/self/task').iterdir())))
    if gmsh_enabled:
        import gmsh
        gmsh.initialize();gmsh.option.setNumber('General.Terminal',0)
        gmsh.model.occ.addBox(0,0,0,1,1,1);gmsh.model.occ.synchronize()
        gmsh.option.setNumber('General.NumThreads',1);gmsh.model.mesh.generate(3)
        answer['gmsh_nodes']=len(gmsh.model.mesh.getNodes()[0]);gmsh.finalize()
    answer['seconds']=time.perf_counter()-started
    connection.send(answer);connection.close()


def main():
    p=argparse.ArgumentParser();p.add_argument('--preload',nargs='*',default=['cadquery']);p.add_argument('--gmsh',action='store_true');p.add_argument('--output',type=Path,required=True)
    args=p.parse_args();mp.set_forkserver_preload(args.preload);ctx=mp.get_context('forkserver')
    trials=[]
    for _ in range(6):
        a,b=ctx.Pipe();started=time.perf_counter();process=ctx.Process(target=trial,args=(b,args.gmsh));process.start();b.close()
        if not a.poll(30):process.kill();process.join();raise RuntimeError('Native preload timed out')
        answer=a.recv();process.join(5)
        if process.is_alive():process.kill();process.join();raise RuntimeError('Worker failed to exit')
        if process.exitcode:raise RuntimeError(f'Worker exited {process.exitcode}')
        answer['total_seconds']=time.perf_counter()-started;trials.append(answer)
    args.output.write_text(json.dumps(dict(preload=args.preload,gmsh=args.gmsh,python=sys.version,trials=trials),indent=2)+'\n')
    print(json.dumps(trials))
if __name__=='__main__':main()
