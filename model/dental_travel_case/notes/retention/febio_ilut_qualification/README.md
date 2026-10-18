# Native FEBio bounded-memory route qualification

This is a solver fixture with two deformable contacting bodies, not an
opening-force prediction for the dental case. A 2 × 2 × 4 mm block moves toward
a 4 × 4 × 1 mm receiving body across a real 0.01 mm gap. Only the receiving
body's bottom is fixed; its contact surface can deform. Both use the same
1200 MPa, Poisson 0.3 numerical material. The normal fixture withdraws 0.02 mm;
the open-gap control moves only 0.005 mm. Both employ identical mesh, contact,
material and nonlinear controls across solver comparisons.

The full case exhausted host memory using PARDISO. Before modifying product
geometry or suppressing degrees of freedom, this investigation tested native
FGMRES with ILUT. The installed FEBio 4.13.0.3ef378562 has a restart-parameter
check defect: restart 30 aborted before any linear iteration, although native
restart 150 solved the same fixture. The API accepts the choice; the native
library rejects MKL's documented warning after its workspace correction.

The [native correction recipe](../../../../../physical_analysis/experiments/febio_fgmres/README.md)
builds an official FEBio plugin from exact upstream MIT-licensed source. It
rechecks only the documented warning/correction codes and still requires zero
on that second check. The original runtime remains unchanged. Every recorded
plugin case includes the compiled artifact hash, its build manifest, actual
native import command and original executable/core-library hashes.

The final byte-associated qualification is `header_guarded_restart30/`, with
the complete pinned SDK header set. `iterative/` retains the original restart-30
initialization failure; `restart150/` retains the working unmodified native
control. The final corrected comparison includes the genuine one-iteration
failure control. Earlier duplicate plugin rebuild comparisons and repeated
initialization failures are omitted; they added no distinct physical or solver
conclusion. The original `comparison.json` preserves their summarized outcomes.

| Quantity | PARDISO | Corrected FGMRES/ILUT, restart 30 |
| --- | ---: | ---: |
| Peak prescribed-motion reaction | 13.54714431645 N | 13.54714431645 N |
| Maximum contact penetration | 0.000001752392 mm | 0.000001752392 mm |
| Maximum principal Green strain | 0.003492209447 | 0.003492209447 |
| Maximum relative force imbalance | 2.39e-9 | 1.50e-7 |

The corrected open-gap control gives approximately 8.08e-8 N and zero contact
penetration. The deliberately inadequate corrected solve permits one iteration
with a weak fill-1 preconditioner and strict residual tolerances: eleven actual
linear solves use one iteration each, no time step is accepted, FEBio terminates
with an error, and the repository result has no successful physics metrics.
This tests failure handling rather than manufacturing a desired output value.

The working controls are maximum 1000 iterations, restart 30, relative tolerance
1e-8, absolute tolerance 1e-12, ILUT fill 12 and drop tolerance 1e-5. Failed linear
iterations remain fatal. Diagonal replacement is disabled. The fixture does not
qualify these choices for every large nonlinear/contact problem: inspect actual
linear residuals, equilibrium and parameter sensitivity on its intended consumer.

At 1.6 million equations, native workspace formulas imply about 0.78 GB Krylov
storage for restart 30 versus 3.85 GB for restart 150, plus about 0.46 GB ILUT
factor allocation at fill 12. These are allocation estimates, not measured peak
memory or evidence that the complete case fits the host. The original sparse
matrix and other native allocations remain.

Reproduce with a fresh output and archive directory:

```sh
./execute.py --threads 1 model/dental_travel_case/retention_febio_solver_qualification.py \
  /tmp/febio-ilut-new \
  --restart-plugin "$HOME/.local/opt/febio-fgmres-restart-3ef378562-headers-qualified/libfgmres_restart_checked.so" \
  --archive model/dental_travel_case/notes/retention/febio_ilut_new
```

`tests/test_febio_iterative.py` protects native agreement, the deformable receiver,
the open gap, actual iteration failure, explicit input/provenance and plugin
identity rejection. This evidence supports trying the full case with its original
degrees of freedom; it does not qualify full-size retention, mesh refinement or
the nonlinear formulation by itself.
