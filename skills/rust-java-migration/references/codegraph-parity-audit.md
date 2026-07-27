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

## Initial Java queries

Ask one architecture question before opening individual files:

```text
Survey Maven/Gradle modules, public packages, factories, registries, SPI,
serialization, persistence, networking, concurrency, annotations, examples,
and tests. Identify high-blast-radius public symbols and their call paths.
```

Then query concrete vertical paths:

```text
<PublicFacade> <Factory> <StrategyInterface> <ConcreteStrategy>
Show overloads, callers, implementations, error paths, side effects, and tests.
```

For every in-scope Java method capture:

- fully qualified owner and exact signature;
- visibility, static/instance nature, generic bounds, annotations;
- parameter names/order, nullable/default/varargs semantics;
- returned value, mutation, I/O, logging, caching, synchronization, and errors;
- downstream collaborators and dynamic boundaries;
- Java tests/examples that exercise the behavior.

## Rust counterpart queries

Query the Java and Rust symbol names together:

```text
<JavaTypeName> <rust_type_name> <javaMethod> <rust_method>
Show source, callers, tests, and behavior differences.
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

Status must be one of the states defined by the skill. Do not infer `BEHAVIOR_VERIFIED` from source similarity.

## Re-query rules

Re-query the exact edited symbols after implementation if the index is fresh. If CodeGraph reports pending re-index, read only the listed stale files directly. Use compiler, tests, lints, and runtime probes for correctness; CodeGraph is structural evidence, not execution proof.
