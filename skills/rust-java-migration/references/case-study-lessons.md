# Case-Study Lessons

These lessons were extracted from local Hutool, hutool-rust, Vernal, and Sa-Token-Rust sources. They are design evidence, not dependencies of this skill.

## Hutool: inventory call chains, not only utility methods

A broad Java utility library contains several migration shapes:

- `BeanUtil` delegates to `BeanCopier`, whose constructor selects different typed copiers for Bean, Map, and value-provider combinations. Porting the public helper without the dispatch matrix loses behavior.
- `HttpRequest#doExecute` applies request interceptors, constructs a connection, sends data, handles cookies and manual redirects, creates a response, and applies response interceptors. A same-named Rust request function is insufficient unless interceptor order, redirect recursion, streaming, cleanup, and errors match.
- database facades reach runners, dialect selection, SQL execution, and result handlers. Object/file counts do not reveal SQL generation or transaction semantics.
- `ServiceLoaderUtil` distinguishes first, first-available, list, class-loader selection, and failure-skipping behavior. A Rust registry must preserve selection and failure contracts, not merely register providers.

Therefore, choose representative vertical call chains for every module before estimating migration effort.

## Existing Rust ports: suspicious code is not automatically wrong, but it is not proof

Current-port inspection exposed useful audit signals:

- a parameter assigned to `let _ = parameter` may indicate that Java behavior was not migrated;
- a handler returning `rows.to_vec()` can be correct for a list contract but must be compared with Java filtering, case, conversion, and exception behavior;
- English-only or generic comments may miss required Java source traceability;
- many types in `lib.rs`, `mod.rs`, or `compat.rs` can hide one-object-per-file gaps;
- a registered API or passing facade construction test does not prove method behavior.

The skill's structural audit reports these patterns without rewriting or deleting existing implementations. A human or agent must verify the actual Java contract before remediation.

## Planned Office/format modules: make incompleteness first-class

When a target module depends on unfinished document-format projects, retaining object and signature placeholders can be useful for planning. The important controls are:

- explicit user approval;
- isolated module or disabled/non-default feature;
- factual `MISSING` or `STUB` state, with the external blocker recorded as
  roadmap metadata rather than a completion-like state;
- exclusion from implemented and behavior-verified coverage;
- named upstream dependency and exit test;
- no claim that facade users can rely on the capability.

This pattern generalizes to JNI-only, hardware-only, proprietary-protocol, and pending upstream-library migrations.

## Sa-Token-Rust: copy the macro boundary, not its name mechanically

The Sa-Token-Rust workspace keeps attribute procedural macros in an independent `proc-macro = true` crate. Its public entry points are thin and delegate to per-macro implementation modules. Framework plugin crates depend on or re-export those macros while the runtime behavior remains in core/plugin APIs.

Reusable architecture:

```text
runtime core <- generated code contract
proc-macro crate <- syntax parsing and code generation
framework adapters <- optional macro re-export and runtime binding
```

Choose `-derive` or `-macros` from the public macro kinds and existing family convention. The case study's singular `-macro` spelling is an established project choice, not a universal naming rule.

Test macros at three layers: accepted expansion behavior, rejected syntax/diagnostics, and downstream framework re-export integration.

## Vernal four-document set: keep documents mutually corrective

The Vernal migration documents demonstrate four distinct questions:

1. Roadmap: what sequence, dependencies, risks, and gates lead to completion?
2. Object mapping: where does every Java object land?
3. Semantic mapping: how is each behavior implemented in Rust?
4. Name consistency: what is missing, extra, merged, renamed, partial, or unverified?

Their strongest use is cross-checking one another. A roadmap can claim an independent-file rule while an object table records merged types; a name audit can expose that conflict. The templates in this skill require status denominators and method/parameter tables so documentation cannot hide such drift.

The later Vernal correction exposed four additional failure modes:

- a large Rust crate had many same-named objects flattened into its root even
  though Spring packages defined meaningful boundaries; file counts and green
  tests hid `MISPLACED` objects;
- an AOP dependency supplied reusable Aspect capabilities, but that did not
  erase Spring's Advice, Interceptor, Advisor, auto-proxy bridge, and support
  object structure;
- “ecosystem has a similar feature” was mistakenly treated as completion
  without an exact crate version/commit, source symbol, local adapter, and
  integration test;
- a newly generated short object table and an older detailed table were kept
  as competing authorities, allowing whichever status was more convenient to
  win.

The corrected rule is deterministic: strip the organization/module package
root, retain the final two package segments (or the one/zero that exist), and
map the Java object name to a `snake_case` file. Current source/worktree facts
come first. Useful historical design material is merged after
`<!-- historical-design-appendix-start -->`; historical counts and statuses
never override the current section, and a duplicate “历史详细版” is removed
after its useful content is merged.
