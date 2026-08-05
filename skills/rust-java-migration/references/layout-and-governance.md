# Layout and Migration Governance

## Workspace topology is a target-product decision

Keep two decisions separate:

1. **Which Cargo packages exist?** Derive them from independent publishing or
   reuse, dependency/feature/target isolation, proc-macro and FFI constraints,
   and distinct build/test lifecycles.
2. **Where do those packages live?** Select root-flat, hybrid/domain-grouped, or
   contained paths from the resulting package count, stable package families,
   root-directory noise, repository languages, and compatibility-sensitive
   established paths.

The Java module inventory is mandatory for traceability, but it is not a Cargo
member list. Document many-to-one and one-to-many mappings explicitly. For a
small cohesive result, prefer top-level siblings such as `freemarker/`,
`freemarker-pyo3/`, and `freemarker-test/`. When adapter/example families grow,
keep core packages visible and group the family. Use a `crates/` container when
large scale, root noise, or multi-language ownership makes the extra level pay
for itself. Treat numerical thresholds as review signals rather than policy.

The deterministic object-file mapping below begins **inside the selected target
crate's `src/`**. It does not dictate the workspace member directory.

## Source-to-target layout

- Map each Java class, interface, enum, or record to one primary Rust file.
- Convert the object name to `snake_case.rs`; keep the Rust type in `PascalCase`.
- Keep a tightly coupled Java inner builder with its primary type only when it is not an independently referenced object.
- Declare the Java module package root explicitly, remove it together with the
  organization path, and retain exactly the final two remaining package
  segments. Retain one segment when only one remains; use the crate root when
  none remains.
- Examples:
  `factory/config/BeanDefinition.java` → `factory/config/bean_definition.rs`;
  `factory/xml/support/Foo.java` → `xml/support/foo.rs`;
  `propertyeditors/PatternEditor.java` → `propertyeditors/pattern_editor.rs`.
- Do not flatten objects into the crate root and do not preserve arbitrary
  deeper paths. A same-name file at another path is `MISPLACED`, not complete.
- Keep `lib.rs` and `mod.rs` limited to module declarations, visibility, documentation, and re-exports.
- Keep runtime compatibility facades thin. Put real object behavior in the corresponding object files.

## File-size and test-organization contract

Count physical lines in every authored `.rs` file, including production,
integration tests, examples, benches, and test-support code. Rust itself defines
no universal file-length maximum, so use a project guardrail: up to 500 lines is
normal, 501–800 lines requires a cohesion review, and more than 800 lines blocks
completion. Generated, vendored, and build-output trees are outside this gate.
Do not game it by compressing unrelated statements, removing useful comments,
or moving all behavior into a generic `compat.rs`.

After documenting a 501–800-line file's cohesion review, pass its safe
repository-relative path through `--reviewed-large-file`. This suppresses only
that review warning when `--fail-on-warning` is enabled; it cannot exempt a file
above 800 lines.

When a reviewed object mixes responsibilities, keep its primary type in
the deterministic `<object>.rs` file and split coherent implementation families
into subordinate files, for example:

```text
src/factory/config/
├── bean_definition.rs
└── bean_definition/
    ├── conversion.rs
    ├── validation.rs
    └── lifecycle.rs
```

Every subordinate file still corresponds only to `BeanDefinition`, defines no
second migrated public object, and remains traceable in the object ledger. Split
by behavior, protocol, error handling, conversion, or lifecycle—not arbitrary
line ranges. Keep fields and invariants protected; use child modules or explicit
private APIs without widening visibility merely to enable the split.

Enable `clippy::too_many_lines` and treat its default 100-line function/method
threshold as a review signal, not an automatic demand to fragment cohesive
algorithms. Refactor when a routine mixes orchestration, conversion, validation,
I/O, or lifecycle responsibilities.

Follow Rust's test organization. Focused unit tests may live in a
`#[cfg(test)] mod tests` beside the module so private behavior can be tested
without widening visibility. Put public-boundary, cross-module, cross-crate,
differential, host, load, and whole-project tests under `tests/`, with shared
integration support under `tests/common/mod.rs` or a dedicated non-published
test/testkit crate. Keep bulky fixtures out of production modules.

## Execution granularity

- Treat the complete declared source module as the default implementation batch.
- Freeze all object, signature, dependency, test, example, and exception mappings
  before editing production code.
- Implement files in dependency order without object-level comparison or test
  pauses.
- Freeze the complete implementation before running the consolidated parity
  audit and unified verification suite.
- Use per-object rows for traceability and final accounting, not as execution
  checkpoints.

## Documentation contract

Every existing Java object, constructor, method, generic/value parameter,
return, exception, metadata tag, and semantic inline comment must have a
traceable Chinese Rust counterpart. Read
[Comment migration contract and example](comment-migration.md) for the complete
mapping and audit procedure.

Every migrated type and method must include Chinese Rust doc comments:

```rust
/// 智能体状态存储契约。
///
/// 保证状态加载、创建与并发可见性。
///
/// 对应 Java：`com.example.state.AgentStateStore`。
/// 来源文件：`module/src/main/java/com/example/state/AgentStateStore.java`。
pub trait AgentStateStore {
    /// 加载或创建指定槽位的状态。
    ///
    /// 对应 Java：`AgentStateStore#loadOrCreateAgentState(String)`。
    ///
    /// # 参数
    /// - `slot_key`：状态槽位标识，不能为空。
    ///
    /// # 错误
    /// - `StateError::EmptySlotKey`：`slot_key` 为空。
    /// - `StateError::Storage`：持久化或反序列化失败。
    fn load_or_create_agent_state(&self, slot_key: &str) -> Result<AgentState, StateError>;
}
```

Translate semantic points from JavaDoc, including null handling, ordering,
thread safety, defaults, exceptions, side effects, and version notes. Preserve
every `@param` as a mapped `# 参数` or `# 类型参数` entry, plus `@return` as
`# 返回值` and `@throws` as `# 错误`. Use only Rust names and real Rust error
conditions in these sections. Keep old names and exception mappings in the four
migration documents. Do not copy license-incompatible prose verbatim beyond
what the project license permits.

## Four-document governance

Each source module owns one current `迁移路线图.md`, `对象级对照表.md`,
`语义迁移对照表.md`, and `对象名称一致性检查.md`. Each file must include a
module-specific current contract with pinned SHAs, object denominator,
`retain_segments = 2`, strict state snapshot, and its own responsibility.
Scaffolded TODOs or a short count summary are not a finished document.

Keep generated current facts first. Merge valuable old grouping and decisions
into a delimited “历史设计附录” in the corresponding current file. Remove the
parallel `*-历史详细版.md` or nested duplicate after a lossless merge. Old
counts, paths, states, tests, and completion claims are never current evidence.
Regeneration must preserve the appendix.

Apply an anti-summary gate: at least three substantive level-2 sections and an
evidence table/task matrix, plus a repository-configured nonblank-line floor
(45 by default). A generated object ledger may be shorter only when the actual
object denominator is genuinely tiny and every row is still present.

## Overloads

Create one row per Java overload before implementing any of them. Decide:

- whether one generic Rust function can preserve every contract;
- which signature owns the canonical base name;
- which semantic suffix distinguishes variants;
- whether a trait, builder, `Into`, `AsRef`, iterator, or options object is clearer;
- whether Java defaults need explicit Rust wrapper functions.

Avoid numeric suffixes and avoid using Rust default arguments, which do not exist.

## Planned exceptions

An exception record must contain:

| Field | Required value |
|---|---|
| Scope | exact module/object/method |
| Object state | factual `MISSING`, `STUB`, `PARTIAL`, `UNVERIFIED`, or proven `PLATFORM_NA` |
| Reason | technical incompatibility or named dependency |
| User approval | date/issue/decision reference |
| Runtime exposure | disabled, isolated feature, or non-default facade |
| Coverage accounting | excluded from implemented and verified numerators |
| Exit criteria | concrete dependency/version/test required |
| Owner | responsible project/team |

For an approved placeholder module, record the blocker as roadmap metadata.
Preserve the object/signature plan and keep each row in its factual `MISSING`
or `STUB` state. Neither enters handled, implementation, or behavior
numerators. Never describe the module as implemented.

## Existing implementation preservation

Before editing an existing Rust port:

1. Record dirty files and current tests.
2. Query the complete module's callers and blast radius.
3. Identify all real behavior already implemented, even if its shape is imperfect.
4. Plan every missing compatibility wrapper and file split in the frozen batch manifest.
5. Apply the complete semantic batch while preserving tests and observable behavior.
6. Run one consolidated post-batch audit and final verification suite.
7. Do not replace a rich implementation with a generated facade merely to improve counts.

## Red-flag patterns

- many public migrated types in `lib.rs`, `mod.rs`, or `compat.rs`;
- per-object files containing only `pub use` of one compatibility module;
- `todo!()`, `unimplemented!()`, empty blocks, unconditional placeholder errors;
- manifest rows marked complete without executable tests;
- wildcard imports masking unclear dependencies;
- merged Java objects without an approved mapping row;
- methods that ignore parameters with `let _ = ...`;
- returns of constant/default values where Java computes results;
- tests that assert only construction or registration;
- Rust-only facades counted as migrated Java objects;
- a passing module test suite used to hide `MISSING`, `MISPLACED`, `STUB`,
  `PARTIAL`, or `UNVERIFIED` object rows;
- a dependency declared as replacement without a pinned exact symbol, adapter,
  and local integration test;
- JVM/platform exclusion asserted without JVM/bytecode/class-loader evidence;
- duplicate current and “历史详细版” documents carrying conflicting facts;
- source-documented objects, methods, parameters, returns, exceptions, or
  semantic inline comments omitted from Rust;
- generic filler comments that do not preserve the Java contract.
- any authored `.rs` file above 800 physical lines;
- any 501–800-line file or 100+-line function with no recorded cohesion review;
- integration, differential, host, load, or whole-project suites embedded in a production module.

## Upstream Rust guidance

- [Rust Style Guide](https://doc.rust-lang.org/style-guide/) — formatting, including the 100-character line-width convention; it does not define a file-length maximum.
- [Clippy lint configuration](https://doc.rust-lang.org/clippy/lint_configuration.html#too-many-lines-threshold) — the default `too_many_lines` function/method threshold is 100.
- [The Rust Book: Test organization](https://doc.rust-lang.org/book/ch11-03-test-organization.html) — unit tests may be colocated under `#[cfg(test)]`; integration tests live in `tests/`.

Treat the static audit script as a detector, then confirm every finding from source and tests.
