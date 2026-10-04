---
name: engineering-execution
description: Investigate computational performance, execute independent engineering studies, or recover interrupted repository work using the shared execution coordinator, automatic traces and established physical-analysis checkpoints.
---

# Engineering execution

Read [execution/README.md](../../../execution/README.md) for commands, cache
contracts, resources, recovery and performance schema. Ordinary engineering runs
need no performance-log review or service administration. For combined agent-session
and computation timing/token investigations, use
[workflow performance analysis](../workflow-performance-analysis/SKILL.md); this
skill retains ownership of computational profiling and execution correctness.
Latency diagnosis alone does not authorize resource-policy or solver changes.
Use a measured, decision-relevant hypothesis and preserve validation when a
separately justified computational optimization follows.

- Run ordinary Python files with `./execute.py`; evaluate CAD with the existing
  evaluator. Keep native solvers behind the physical-analysis APIs. Do not create
  another pool, scheduler, trace format or arbitrary-result cache.
  Use the uncapped computation defaults and follow the
  [repository deadline rule](../../../AGENTS.md#shared-engineering-execution);
  do not invent per-solve or whole-study timeouts.
- Use automatic controlled-artifact reuse. Declare deterministic geometry's
  complete inputs once; leave unknown/stateful script construction fresh. Preserve
  explicit reused/fresh evidence and use `--fresh` when fresh execution is required.
- Express CPU budgets as a percentage or integer. Independent files use
  `execution.batch.ScriptTask` dependencies and output declarations. Native
  children share/divide the admitted budget; never launch unbounded nested pools.
- For performance investigations, compare source/tool identities and cold/warm
  command latency before changing kernels. Analyze `execution.history` summaries
  and Perfetto exports; target cProfile or allocation profiling only when needed.
  Separate queue wait from initialization and kernels. Ordinary admission gates
  CPU threads and job slots. RSS measurements are diagnostic, with no shared
  memory budgets or watchdogs. Use complete option/budget comparison identities
  when available; legacy CAD argument hashes omit view/export settings.
  Native work may require solver/native sampling rather than Python profiles.
  Challenge an expensive control before optimizing its settings, following the
  [reflection checkpoint](../engineering-reflection/SKILL.md#identify-what-should-change).
- Prefer less repeated work, immutable intermediates, batching, NumPy and existing
  spatial indexes. Use compilation only when measured end-to-end savings justify
  startup and maintenance. Keep trivial calculations simple.
- Verify numerical equivalence and all engineering evidence checks. Bounds are
  conservative screens, never substitutes for required exact checks. Completion,
  numerical quality and physical validation remain separate conclusions.
- After coordinator failure, inspect incomplete job metadata. Restart arbitrary
  scripts explicitly with matching inputs; never replay unknown side effects.
  Use identity-guarded mesh/saved-field/evidence recovery for completed native work.
- Retain bounded benchmark summaries and representative traces deliberately;
  keep large raw traces/profiles local. Never make performance runs commit data
  automatically. Record rejected optimizations and unavailable native backends.
