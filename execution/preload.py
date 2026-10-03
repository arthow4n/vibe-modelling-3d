"""Qualified import-only preload. Never initialize Gmsh or a native solver here."""
import os
# Forkserver must remain single threaded before cloning native dependencies.
for _key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):
    os.environ[_key]='1'
import cadquery
if len(os.listdir('/proc/self/task')) != 1:
    raise RuntimeError('Native preload started background threads; isolated execution required')
