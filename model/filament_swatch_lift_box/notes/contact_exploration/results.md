# Generated formulation exploration

| Run | Backend | Native/API outcome | Last saved fraction | Native overlap (mm) | Diagnostic peak actuation (N) | Diagnostic peak strain |
| --- | --- | --- | ---: | ---: | --- | ---: |
| [explore_febio_compression](../analysis/explore_febio_compression/result.json) | FEBio | completed | 1 | 1.24099e-08 | BC2 12 | 0.00249687 |
| [explore_mortar_benchmark](../analysis/explore_mortar_benchmark/result.json) | CalculiX | unsupported_output | — | — | — | — |
| [explore_release_calculix](../analysis/explore_release_calculix/result.json) | CalculiX | quality_failed | 1 | 0.041659 | lid 2.22, pinch 2.9 | 0.0059713 |
| [explore_release_febio_soft](../analysis/explore_release_febio_soft/result.json) | FEBio | failed | 0.468659 | — | — | — |
| [explore_release_febio_soft_tol001](../analysis/explore_release_febio_soft_tol001/result.json) | FEBio | failed | 0.606249 | — | — | — |
| [explore_release_febio_stopped](../analysis/explore_release_febio_stopped/result.json) | FEBio | failed | 0.603528 | — | — | — |
| [explore_release_febio_two_pass](../analysis/explore_release_febio_two_pass/result.json) | FEBio | failed | 0.601723 | — | — | — |
| [explore_release_febio_two_pass_tol001](../analysis/explore_release_febio_two_pass_tol001/result.json) | FEBio | failed | 0.602144 | — | — | — |

Native completion is distinct from model acceptance. Failed or incomplete operations have no successful whole-path metrics. Release-only cases assume an unloaded assembled state; they do not prove closing. Mesh-source identity is explicit; equal requested mesh size is not equal actual mesh. Numerical force tolerance is not a material property.
