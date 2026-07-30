# CodeGraph Parity Audit

Use this reference when both source and target repositories must be compared beyond names and file counts.

## Repository boundary

Run each query against the exact repository root containing its own `.codegraph/`. Never query a common parent that may mix sibling projects.

Record:

- repository root and current SHA;
- CodeGraph index status and any staleness warning;
- source/build roots excluded from the index;
- generated files and non-code documents requiring separate inspection.

If `.codegraph/` is absent, do not create it without authorization. State that the fallback inventory lacks graph-level dynamic call evidence.

## Initial full-batch Java queries

Build the complete module inventory before editing any target file. Ask broad
architecture and inventory questions first:

```text
Survey Maven/Gradle modules, public packages, factories, registries, SPI,
serialization, persistence, networking, concurrency, annotations, examples,
and tests. Identify high-blast-radius public symbols and their call paths.
```

Then query representative vertical paths by subsystem to resolve shared
contracts and dynamic boundaries:

```text
<PublicFacade> <Factory> <StrategyInterface> <ConcreteStrategy>
Show overloads, callers, implementations, error paths, side effects, and tests.
```

From these queries, produce a frozen manifest for every in-scope Java method:

- fully qualified owner and exact signature;
- visibility, static/instance nature, generic bounds, annotations;
- parameter names/order, nullable/default/varargs semantics;
- returned value, mutation, I/O, logging, caching, synchronization, and errors;
- downstream collaborators and dynamic boundaries;
- Java tests/examples that exercise the behavior.

Do not start implementing after the first useful path. Finish the full module
manifest, dependency topology, overload table, exception list, and test/example
inventory first.

## Consolidated Rust counterpart audit

Do not repeatedly query each Rust object immediately after editing it. After the
entire declared implementation batch is frozen, query Java and Rust symbols in
module- or subsystem-sized groups:

```text
For every row in <batch manifest>, compare the Java owner/signature with its Rust
file/type/function. Show missing or extra APIs, callers, implementations, tests,
side effects, error paths, and behavior differences grouped by subsystem.
```

Inspect ownership, borrowing, error type, async boundary, trait objects, locks/channels, feature gates, platform cfgs, and crate re-exports. A similarly named Rust function is not evidence of semantic parity.

## Dynamic boundary handling

CodeGraph may end a static path at a registry key, reflection, service loader, event bus, callback, generated method, or framework dispatch. Record the boundary and enumerate candidate implementations instead of pretending the call path is complete.

Typical Java-to-Rust dynamic mappings:

| Java boundary | Rust evidence to inspect |
|---|---|
| `ServiceLoader` | registry construction, `inventory` submissions, factory selection |
| reflection | trait/closure registry, serializer metadata, proc-macro output |
| interceptor chain | middleware/layer order, error short-circuit, response unwind |
| executor/future | spawn ownership, cancellation, join errors, shutdown |
| synchronized cache | lock scope, atomicity, eviction listener ordering |

## Required parity matrix

For each public operation maintain one row:

| Java signature | Rust API | Input mapping | Output/error mapping | Side effects | Call-path evidence | Tests | Status |
|---|---|---|---|---|---|---|---|

Status must be one of the strict states defined by the skill. Do not infer
`IMPLEMENTED` from source similarity, a same-named file, a re-export, green
tests, or a dependency with adjacent behavior. CodeGraph call paths supply
semantic evidence only after the deterministic expected path has been checked:
strip the configured Java package root and retain the final two package
segments.

## Post-implementation query rules

Run one consolidated post-implementation audit if the index is fresh. Use
targeted symbol queries only to explain findings from that audit, not as
per-object completion gates. If CodeGraph reports pending re-index, read only
the listed stale files directly and disclose the limitation. Use compiler,
tests, lints, and runtime probes only in the final unified verification phase;
CodeGraph is structural evidence, not execution proof.
