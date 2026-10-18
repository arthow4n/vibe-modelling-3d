# FEBio bounded-restart correction

This small native plugin exists because the full dental case exhausted memory
with PARDISO, and the installed FEBio 4.13 iterative solver aborted when asked
to reduce its Krylov restart workspace. It changes no product geometry, material,
contact law, nonlinear acceptance criterion or displacement constraint.

The inspected official source is FEBio commit
`3ef37856289269674827e1748313b6224c4041a7`. Its
[FGMRESSolver.cpp](https://github.com/febiosoftware/FEBio/blob/3ef37856289269674827e1748313b6224c4041a7/NumCore/FGMRESSolver.cpp)
initializes MKL with restart 150, changes the requested restart, calls
`dfgmres_check`, and treats every nonzero return as fatal. According to
[Intel's API documentation](https://www.intel.com/content/www/us/en/docs/onemkl/developer-reference-c/2024-2/dfgmres-check.html),
that check corrects dependent workspace offsets and reports warning/correction
codes when restart changes. The real restart-30 fixture aborted before its first
linear solve; native restart 150 solved the same problem.

`recheck.patch` permits one more check after the three documented warning or
correction codes (`-1001`, `-1010`, `-1011`). The second check must return zero.
Hard errors and unmet iterative tolerances still fail. The plugin registers a
separate `fgmres_restart_checked` class through FEBio's documented plugin API;
it does not replace symbols or modify the installed runtime. The native algorithm
and parameter definitions are copied at build time from the pinned source under
its existing MIT license. Generated source retains the full license header.
The renamed class is needed because the original class's solver state is private.

Download and unpack the exact upstream source outside the repository:

```sh
curl -fL https://github.com/febiosoftware/FEBio/archive/3ef37856289269674827e1748313b6224c4041a7.tar.gz -o /tmp/febio-sdk.tar.gz
mkdir /tmp/febio-sdk
tar -xf /tmp/febio-sdk.tar.gz -C /tmp/febio-sdk --strip-components=1
./execute.py --threads 1 physical_analysis/experiments/febio_fgmres/build.py \
  --sdk /tmp/febio-sdk --runtime "$HOME/.local/opt/febio-exploration/FEBio4" \
  --output "$HOME/.local/opt/febio-fgmres-restart-3ef378562-headers-qualified"
```

The output must be a fresh directory. The recipe guards the reviewed source,
all 289 FECore/NumCore `.h`/`.hpp`/`.inl` headers, SDK version and installed native
executable/core library hashes. It uses the
system C++ compiler and installed native MKL implementation exported by
`libnumcore.so`; `mkl_rci_abi.h` contains only the documented LP64 C declarations.
The build manifest records the compiler, command, generated source and library
identities. A different runtime needs a reviewed ABI/source association. Neither
the SDK archive nor compiled `.so` belongs in Git.

Use the returned plugin path explicitly in `FgmresILUT`. Requests retain the full
build manifest and plugin hash. The worker checks the plugin before and after
solving, verifies the runtime matches the build, and records native `-import`
in the command. Default `FebioBackend()` input remains unchanged.

Reproduce the small contact qualification through
`model/dental_travel_case/retention_febio_solver_qualification.py`, supplying
`--restart-plugin PATH`. It compares PARDISO and corrected restart 30 on the same
mesh with two deformable bodies, an open-gap control, and a deliberately
insufficient iteration budget. The fixture qualifies this native correction;
it is not a full-case opening-force result or a promise of convergence on a
much larger contact system.
