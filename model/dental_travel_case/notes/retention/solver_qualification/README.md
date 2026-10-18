# CalculiX iterative linear-solver qualification

The full M1 direct solve exceeded host memory before an accepted increment.
This experiment tests an alternative native linear solve while retaining
quadratic deformable solids, frictionless surface-to-surface contact, supports,
loads and the nonlinear equilibrium problem. It does not qualify full-case
retention or reproduce the full case in a small fixture.

[Reproducer](../../../retention_solver_qualification.py):
`./execute.py --threads 1 model/dental_travel_case/retention_solver_qualification.py /tmp/new_solver_comparison`
from the repository root. A new directory is required. The shared tests also
compare identical meshes using guarded native mesh reuse and preserve an open-gap
negative control.

The fixture is a 2 × 2 × 4 mm block, initially .01 mm above a fully fixed floor.
The block can move in z; its top receives -.02 mm prescribed travel. E=1200 MPa,
Poisson ratio zero, and penalty=120000 N/mm³ are explicit analytical fixture
properties, not measured PETG properties. The approximate compressed-block load
is 12 N after closing the gap. Mesh sizes are .8 mm for the block and 1 mm for
the floor; maximum normalized motion increment is .1. Both routes use CalculiX
2.21, C3D10 elements and the same native surface-to-surface contact formulation.

| Quantity | Default direct route | Iterative scaling |
| --- | ---: | ---: |
| Peak top reaction, N | 11.92544649995 | 11.92544619704 |
| Maximum penetration, mm | .00002486458 | .00002486458 |
| Maximum principal strain magnitude | .00249071600046 | .00249071600046 |
| Maximum saved global force imbalance, relative | 3.0112e-8 | 1.4638e-5 |
| Native/extracted status | completed | completed |

The peak reaction differs by 2.54e-8 relative. At the first open-gap increment,
the iterative top reaction is about 1.46e-5 N, illustrating finite numerical
residuals rather than physical retention. Tests compare saved reaction histories
with 1e-4 N absolute / 1e-4 relative tolerances, strain and penetration to 1e-4
relative, and require global balance below 1e-4. These are numerical comparison
tolerances, not product acceptance loads. A separate .005 mm travel remains
short of the gap: no contact and less than 1e-4 N peak top reaction.

Retained [direct](direct/result.json) and [iterative](iterative/result.json) runs
contain actual histories, tool and source identities, case files, compressed
native decks, geometry and logs. They preserve their original provenance; later
extractor/provenance additions do not rewrite those historical runs. Decompress
the native deck and use its recorded CalculiX executable to replay the solve.
Raw DAT fields remain in the temporary source runs and are deliberately excluded
by the existing evidence-retention contract.

## Follow-up: incomplete Cholesky preconditioning

The full-size symmetric CG runs subsequently showed slow convergence with
scaling. The additional explicit `iterative_cholesky` choice addresses that
observed preconditioning limitation without changing physics or native residual
targets. The same contact regression, with guarded reuse of its direct mesh,
produced 11.92544649580 N peak top reaction, .00002486458 mm penetration,
.00249071600046 peak principal strain magnitude and 3.5844e-8 maximum saved global
force imbalance. Its separate open-gap control remained below 1e-4 N without
contact. The native log contains no Cholesky-to-scaling fallback warning.

The [retained Cholesky run](cholesky/result.json) preserves the requested choice,
the observed absence of fallback, actual history and compressed replay files.
Three focused tests cover rejection of unknown choices and both iterative
options against the direct comparator, including full saved reaction histories,
penetration, strain, balance and open-gap controls. This does not establish a
full-size convergence or memory result. On an asymmetric matrix, native CCX
still falls back to diagonal scaling; provenance records that logged fallback
separately from the requested preconditioner.

## Native capability and limits

The [official CalculiX 2.21 source archive](https://www.dhondt.de/ccx_2.21.src.tar.bz2)
was inspected directly: `src/statics.f` maps `ITERATIVE SCALING` to solver 2;
`src/nonlingeo.c:2857` uses `predgmres_struct` for asymmetric matrices and warns
that iterative Cholesky cannot serve that matrix, falling back to scaling.
`src/predgmres_struct.f` sets GMRES relative tolerance 1e-6 and a 10-vector
restart. Symmetric matrices instead use `src/preiter.c` / native CG with diagonal
scaling and tolerance 1e-4. The small fixture logs report the CG error-condition output, so its numerical
comparison exercises the symmetric branch. Support for the asymmetric GMRES
branch is established here by source inspection, rather than a separate
asymmetric numerical benchmark. The wrapper exposes both requested preconditioners. It does not pretend that
Cholesky supplies an asymmetric preconditioner or modify native tolerances; a
logged Cholesky fallback is retained separately from the requested choice.

This small result justifies attempting the existing full-size problem with a
lower-memory native option. It does not establish that the full assembly fits
memory, that its linear or nonlinear iterations converge, that contact pairing
is physically adequate, or that all local residuals are resolved. Full-size
completion, balance, penetration and sensitivity results must be assessed in
the product investigation. A failed iterative solve remains missing evidence;
its failure is not evidence of weak retention.
