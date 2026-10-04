# Dependency ordering and independent variant batches

Scope: Follow-up on 2026-10-04 to the local session review of modelling work from
2026-09-22 through 2026-10-04. The changes use working-tree source based on revision
`2a1474a`; the [benchmark summary](../benchmarks/key_batch.json) retains exact source
and lock hashes. The matched probe used Linux/WSL2, Python 3.12.14, CadQuery 2.7.0,
Gmsh 4.15.2 and CalculiX 2.21 (identified in solver logs). It measures scheduling,
not product acceptance or total coding-agent productivity.

Measurements: Historical command-item timestamps show two sequential three-key
contact batches taking 375.374 and 381.730 seconds. A postcard batch already
overlapped three evaluations: 11.912 seconds elapsed versus 35.184 seconds of
combined command durations. This overlap is not a measured serial speedup. A
completed phone-stand check recorded 65.816 seconds queued and 12.625 seconds of
worker execution; admission identified CPU blocking with all eight shared CPU
allocations occupied by two jobs.

The new probe compares the actual key-analysis script's serial and batched modes
at the same three-CPU total budget. Each parallel child receives one CPU and its
own output directory. Three paired trials alternate execution order, use a
diagnostic 0.8 mm mesh and perform fresh native solves; verified mesh reuse is
allowed in both modes. Stopwatch intervals include script launch, construction,
native analysis, extraction and result delivery.

| Pair | Order | Serial, s | Parallel, s |
| --- | --- | ---: | ---: |
| 1 | Serial then parallel | 52.898 | 32.277 |
| 2 | Parallel then serial | 45.625 | 31.685 |
| 3 | Serial then parallel | 45.620 | 33.743 |
| Median | | 45.625 | 32.277 |

Findings: Median complete-batch elapsed time fell **29.3%** for this fixture.
All 18 native solves completed and passed their numerical quality checks.
Forces, strains and quality/design decisions matched exactly across modes.
Fixture configurations match after excluding mesh-reuse provenance; native decks
match except for equivalent integer/float spelling of the contact penalty.
Interpretation: independent single-thread contact cases can use otherwise idle
capacity without changing the numerical operation. The historical queued check
also supports prioritizing the next design decision; adding more concurrent
launches alone would not address that delay.

Implications: Keep quick rejection checks ahead of long dependent studies, then
batch independent cases after prerequisites pass. Whole-product review and
geometry corrections remain dependencies. Final artifact jobs wait for settled
geometry; Python edits during CAD publication can invalidate results. Useful
overlap during those jobs includes reviewing completed evidence and writing
non-Python documentation.

Changes or recommendations: [Repository workflow](../../AGENTS.md#avoid-repeated-work)
now routes agents to [dependency and capacity planning](../../execution/README.md#dependency-and-capacity-planning),
also linked from the engineering execution skill. The
[key-analysis consumer](../../model/filament_swatch_box_study/analyze_cap_i.py)
uses the existing batch API by default, preserves sequential comparison and
single-variant execution, rejects duplicate output owners and propagates child
failures. Its inherited arbitrary solve deadline is removed in accordance with
existing repository policy; explicit deadlines remain available. No scheduler
priority system, new worker framework or resource-policy change was introduced.

Verification and limitations: The shared batch dependency/failure regression
passed. Targeted consumer checks confirm single-variant failure propagation and
duplicate rejection before output creation. Skill validation, local document
targets and whitespace checks passed. Three pairs are a small sample; the first
includes warmup and OS caches were not flushed. Full-resolution 0.3 mm study
speedup, whole-session savings and the benefit of reordered checks remain
unmeasured. Historical execution retention is incomplete, and unrelated session
timing warnings do not invalidate the specifically selected positive command
intervals. The coarse probe does not replace product evidence or qualify physical
fit, force, material response or durability. Publication scanning and deliberate
factual/privacy review cover this authored aggregate text; raw histories, native
files and local diagnostics remain ignored.
