# Vernal Migration Testing Case Study

This case study extracts reusable patterns from the Vernal Framework Rust port. It is an audit of test shape, not a claim that the whole project or any named module is complete.

## Positive patterns

### Exact expression outcomes

`vernal-expression/tests/selection_projection_tests.rs` contains an `assert_eval` helper that parses, evaluates, and compares the exact `ExpressionValue`, including the source expression in the failure message. Tests such as `matches_simple` protect true and false behavior rather than only parser acceptance.

Reusable rule:

- parse success is a parser contract;
- evaluation value/error/side effect is a semantic contract;
- name and report them separately.

### Registered method behavior

`vernal-expression/tests/method_resolver_tests.rs` verifies:

- registration and lookup;
- exact registered names;
- registered-method execution and arguments;
- missing-method errors containing the missing name;
- parser-to-resolver-to-executor integration.

This is stronger than checking that a resolver type exists. It covers public lookup, dynamic dispatch, success values, and error context.

### Shared adapter lifecycle conformance

`vernal-web-testkit::ScopeCloseProbe` is reused by multiple web adapters. The probe:

- observes the actual request scope exposed by the adapter;
- never closes the resource for the implementation;
- asserts the scope remains open while the body is active;
- waits with scheduler yielding and a bounded Tokio timeout instead of a fixed sleep;
- asserts adapter-owned closure after completion or disconnect.

`ScopeCleanupTimeoutFixture` additionally verifies exactly-once cleanup, cancellation visibility, redacted warning output, and eventual background cleanup after a blocked close hook is released.

Reusable rule: put framework-neutral lifecycle assertions in one testkit, require each adapter to produce native observations, and retain adapter-specific routing/body/trailer/backpressure tests.

## Negative patterns requiring improvement

These examples are useful because they show how green tests and high coverage can overstate migration evidence.

### Ignored result

`selection_all_parse` evaluates an expression and then assigns the result to `_`. The test has no pass/fail assertion about evaluation. `constructor_ref_parse` similarly accepts the parsed result without deciding whether success or failure is correct.

Risk: missing behavior appears covered merely because the path ran.

Required improvement: assert exact value/error and state, or mark the capability incomplete.

### Parse-only test presented as semantic coverage

Selection, projection, `between`, assignment, navigation, increment/decrement, method/property/variable/type references contain parse-only checks. These may be valid parser tests, but they do not prove evaluation semantics.

Risk: a roadmap counting “one test per AST node/token” upgrades syntax recognition to behavioral parity.

Required improvement: keep parse tests as parser evidence and add input/output/error matrices for evaluator behavior.

### Generic error assertion

`matches_invalid_pattern_error` checks only `is_err()`.

Risk: the wrong failure category, location, message, source, or retryability still passes.

Required improvement: assert the stable typed error contract and any public redaction surface.

### Cache claim without cache observation

`matches_uses_moka_cache` evaluates two expressions using the same pattern and checks only final boolean values.

Risk: the test passes even if compilation/cache lookup occurs twice or the cache is absent.

Required improvement: observe loader/compile count, hit/miss/eviction/invalidation, or rename the test to the behavior it actually checks.

### Coverage-targeted duplication and discarded outcomes

Vernal contains test files and names such as `final_coverage`, `coverage_boost`, and repeated `let _ = result` patterns. The naming alone does not make a test bad, but it is a strong review signal when no distinct contract or assertion is documented.

Risk: test and line counts rise without increasing defect detection.

Required improvement: map each case to a source contract or Rust risk, merge real duplicates, and use mutation/branch evidence before removal.

## Documentation drift lesson

The Vernal expression migration documents use status summaries and count-oriented goals such as AST/token coverage, while some same-module tests are parse-only and some documented runtime paths remain placeholders or ignore inputs.

Reusable rule:

- every `IMPLEMENTED` row needs a source trace, exact test/oracle, command,
  artifact, and audited Rust SHA;
- green tests never override `MISSING`, `MISPLACED`, `STUB`, `PARTIAL`, or
  `UNVERIFIED` in the current object ledger;
- `DEPENDENCY_REUSED` tests must invoke the exact pinned upstream symbol
  through the local adapter, not merely test a similar local capability;
- file presence, object count, parser acceptance, and “at least one test” are separate structural signals;
- the four migration documents must be audited together so a later count table cannot silently contradict a technical-requirements document.

## Recommended replacement matrix

| Existing signal | Better acceptance |
|---|---|
| one test per AST node | parser cases plus evaluator success/boundary/failure matrix |
| all token kinds parse | precedence, associativity, source positions, diagnostics, evaluation |
| `is_ok()` | exact value/state/side effect |
| `is_err()` | exact stable error contract |
| path executed | plausible mutant is killed |
| copied Java test name | source case disposition with inputs/assertions |
| high Rust coverage | comparable coverage plus source parity and Rust obligations |
| adapter has tests | shared conformance suite plus native adapter tests |
