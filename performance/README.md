# Execution performance evidence

[Execution commands and contracts](../execution/README.md) describe the working
system; [implementation history](IMPLEMENTATION.md) records decisions and commits.
Benchmark summaries are versioned JSON in `benchmarks/`; unrestricted runtime
evidence stays in ignored `.execution/`.

## Reproduction

Run from the repository root after locked environment synchronization:

```sh
.venv/bin/python performance/benchmark.py --final --label final --output performance/benchmarks/final.json
.venv/bin/python performance/kernels.py --output /tmp/kernels.json
.venv/bin/python performance/motion_benchmark.py --output /tmp/motion.json
```

The workflow harness measures the complete subprocess interval, using three runs
per workload. Each final workload has its own empty controlled cache and private
coordinator: first execution is cold initialization; subsequent median is warm.
The OS page cache is not flushed. Original revision `f984a0b` supplies baseline
commands and default four-view behavior. Fixture/tool/core dependency versions
must match before interpreting differences. Do not run heavy tests simultaneously.

Cold and warm evidence, tracing overhead, CPU-budget experiments and independent
operation concurrency are consolidated after final regression verification.

## Qualified kernels and rejected approaches

The original quadratic-surface traction quadrature is batched, not approximated:
2000-face median 0.324 s to 0.0166 s. Prepared Tet4 reference inverses reduce
1000-frame strain extraction from 0.102 s to 0.0617 s. Conservative motion bounds
skip strictly separated booleans; exact distances and possible intersections
remain exact. G-code input streams instead of loading the entire file.

Existing VTK mapping outperformed the investigated SciPy spatial index (0.0184 s
versus 0.0229 s), so no competing index or SciPy dependency remains. Global
dependency-bytecode bypass increased startup costs; fresh editable-source loaders
retain locked dependency bytecode instead. Gmsh remains isolated despite passing
a narrow forkserver experiment. No measured kernel justifies Numba, Cython, Rust
or another worker framework.

## Verification scope

Qualification runs on Linux/WSL2 with CPython 3.12, CadQuery/Open Cascade, Gmsh,
OrcaSlicer, CalculiX and FEBio. Optional native IPC/PolyFEM execution is unavailable;
its orchestration, field extraction, quality and recovery guards are tested with
retained fixtures and automated coverage. Linux affinity/parent-death behavior
has not been qualified on other operating systems. This is process isolation,
not a security sandbox.
