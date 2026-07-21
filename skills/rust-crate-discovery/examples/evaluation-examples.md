# Evaluation Examples

> Worked scenarios for [`scripts/crate_eval.py`](../scripts/crate_eval.py),
> companion to [`SKILL.md`](../SKILL.md). Each shows the command, output, and
> **how to read the output and decide**.

> **All numeric outputs below are illustrative** — captured to show the *shape*
> of the report. Live numbers shift daily; re-run the commands for current
> values. The decision logic is stable. Commands assume you are in the skill
> directory (`python3 scripts/crate_eval.py <subcommand>`).

---

## Example 1 — Picking an ORM (`rbatis` vs `diesel` vs `sea-orm` vs `sqlx`)

### Step 1: search

```bash
python3 scripts/crate_eval.py search "orm" --limit 8
```

```text
NAME                          VER        DL       RECENT  UPDATED      DESCRIPTION
--------------------------------------------------------------------------------
sea-orm                       1.1.0      1,843,566 244,103  2026-06-18   async ORM for Rust...
sqlx                          0.8.1     12,103,447 1,002,331 2026-07-02   async SQL with compile-time checks
diesel                        2.2.4      8,234,001 410,556  2026-05-30   safe ORM and query builder
rbatis                        4.9.6        657,356  19,938  2026-07-10   async ORM (dynamic SQL)
```

### Step 2: shortlist and compare

Shortlist the top four (`sqlx`, `diesel`, `sea-orm`, `rbatis`) and compare:

```bash
python3 scripts/crate_eval.py compare sqlx diesel sea-orm rbatis
```

```text
NAME                     GRADE   SCORE  ADOPT  MAINT  DOCS MATUR  COMM  LIC   RECOMMENDATION
------------------------------------------------------------------------------------------------------------
sqlx                     A        92    28/30  25/25  15/15 13/15  6/10  5/5   RECOMMENDED — strong fit, low risk
sea-orm                  A        88    26/30  24/25  15/15 13/15  5/10  5/5   RECOMMENDED — strong fit, low risk
diesel                   B        79    27/30  20/25  14/15 15/15  4/10  4/5   LIKELY SUITABLE — verify fit for your use case
rbatis                   C        61    18/30  21/25  12/15  10/15  3/10  5/5   ACCEPTABLE — investigate specific concerns
```

### Step 3: interpret

- **`sqlx` (A, 92)** — dominant adoption (12M downloads), full marks on docs/maintenance; compile-time SQL check is a unique safety feature. No red flags.
- **`sea-orm` (A, 88)** — slightly lower adoption, clean bill of health. Best fit for high-level async ORM (ActiveRecord-style) vs `sqlx`'s query-macro style.
- **`diesel` (B, 79)** — License sub-score (4/5) hints at a field-format nuance (illustrative; Diesel is MIT/Apache in reality). Mature (15/15) but synchronous-only — a fitness mismatch if you need async.
- **`rbatis` (C, 61)** — lower maturity/adoption; acceptable but out-competed on health signals.

### Step 4: decide

For a new async web service, `sqlx` or `sea-orm` is the pick — choose by **fitness**, not raw score:

| If you want…                                       | Pick      |
|----------------------------------------------------|-----------|
| Compile-time-checked SQL, hand-written queries     | `sqlx`    |
| High-level ORM, dynamic queries, ActiveRecord style | `sea-orm` |

### Step 5: hand off

Add to `Cargo.toml`, then set up `cargo-deny`. Pin policy → `rust-semver`; governance (cargo-deny, license policy, advisory response) → `rust-dependencies`.

---

## Example 2 — HTTP client (`reqwest` vs `ureq` vs `hyper` vs `isahc`)

### Search

```bash
python3 scripts/crate_eval.py search "http client" --limit 6
```

```text
NAME                          VER        DL        RECENT   UPDATED      DESCRIPTION
--------------------------------------------------------------------------------
reqwest                       0.12.5    45,234,001 3,102,447 2026-07-09   high-level HTTP client
hyper                         1.4.1     32,001,556 1,804,220 2026-07-01   low-level HTTP implementation
ureq                          2.10.1     3,421,009   210,556 2026-06-22   minimal blocking HTTP client
isahc                         1.7.2        980,123    12,009 2025-11-14   practical HTTP client (curl-backed)
```

### Compare

```bash
python3 scripts/crate_eval.py compare reqwest hyper ureq isahc
```

```text
NAME                     GRADE   SCORE  ADOPT  MAINT  DOCS MATUR  COMM  LIC   RECOMMENDATION
------------------------------------------------------------------------------------------------------------
reqwest                  A        94    30/30  24/25  15/15 13/15  7/10  5/5   RECOMMENDED — strong fit, low risk
hyper                    A        90    29/30  25/25  15/15 15/15  6/10  5/5   RECOMMENDED — strong fit, low risk
ureq                     A        86    23/30  24/25  14/15 13/15  6/10  5/5   RECOMMENDED — strong fit, low risk
isahc                    C        58    14/30  12/25  13/15  13/15  3/10  5/5   ACCEPTABLE — investigate specific concerns
```

### Interpret

- **`reqwest` (A, 94)** — maxes adoption (45M downloads) and docs; the de-facto high-level client, built on `hyper`.
- **`hyper` (A, 90)** — equally healthy, maxes maturity (15/15, oldest/most stable). But **low-level**: you write HTTP/1.1+2 plumbing, not `client.get(url).send()`.
- **`ureq` (A, 86)** — minimal, blocking, zero-async; great for a tiny dep tree (no tokio runtime).
- **`isahc` (C, 58)** — maintenance drop (12/25) and older `UPDATED` (2025-11); likely a stale-release red flag.

### Decision framework — high-level vs low-level

A **fitness** decision the score cannot make for you:

| Need                                        | Pick                |
|---------------------------------------------|---------------------|
| "Just make an HTTP request" (most apps)     | `reqwest`           |
| You are building a client/server framework  | `hyper`             |
| Blocking, minimal deps, no async runtime    | `ureq`              |
| curl-backed features (you depend on libcurl)| evaluate carefully  |

All three top picks are healthy. Confirm the API shape matches your abstraction level, then hand off to `rust-api-design`.

---

## Example 3 — Logging (`tracing` vs `log` vs `slog`)

### Compare

```bash
python3 scripts/crate_eval.py compare tracing log slog
```

```text
NAME                     GRADE   SCORE  ADOPT  MAINT  DOCS MATUR  COMM  LIC   RECOMMENDATION
------------------------------------------------------------------------------------------------------------
tracing                  A        91    28/30  25/25  15/15 14/15  8/10  5/5   RECOMMENDED — strong fit, low risk
log                      A        89    30/30  22/25  15/15 15/15  5/10  5/5   RECOMMENDED — strong fit, low risk
slog                      B        72    18/30  16/25  13/15  15/15  4/10  5/5   LIKELY SUITABLE — verify fit for your use case
```

### Interpret

- **`tracing` (A, 91)** — the modern choice: structured, async-aware, spans/events. The maintenance/community edge reflects active tokio-team stewardship.
- **`log` (A, 89)** — maxes adoption (the foundational facade every logging crate routes through) and maturity (oldest). Right pick for *libraries* that want to stay runtime-agnostic.
- **`slog` (B, 72)** — structured-logging pioneer, but maintenance (16/25) reflects a slower cadence; the ecosystem has consolidated around `tracing`.

### Ecosystem fit matters more than raw score

The gap between `tracing` (91) and `log` (89) is noise; the real question is
**architecture**: a **library** should depend on `log` (or `tracing`'s facade)
so downstream apps choose the implementation, while an **application** should
pick `tracing` for structured, async-aware output. A 2-point score difference
must not override this structural decision — the canonical case where the score
measures *health* and you must layer a *fitness* judgment on top.

---

## Example 4 — A risky crate (fictional `abandoned-crate`)

> **Fictional** crate showing how multiple red flags compound into a low grade. Numbers illustrative.

```bash
python3 scripts/crate_eval.py eval abandoned-crate -v
```

```text
=== abandoned-crate === F (34/100) — BLOCK — unresolved security advisory
  old HTTP wrapper, last touched years ago
  version 0.7.2  |  842 downloads (12 recent)  |  license: (unknown)
  repo: (none)
  docs: (none)

  Subscores:
    adoption        ███░░░░░░░░░░░░░░░░░░░░░░░   3/30
    maintenance     ░░░░░░░░░░░░░░░░░░░░░░░░░░   0/25
    documentation   █░░░░░░░░░░░░░░░░░░░░░░░░░   2/15
    maturity        ███████░░░░░░░░░░░░░░░░░░░   6/15
    community       ░░░░░░░░░░░░░░░░░░░░░░░░░░   0/10
    license         ██████████░░░░░░░░░░░░░░░░   2/5

  Red flags:
    ! no release in 1240 days (>41 months)
    ! 1 RustSec advisory/advisories: RUSTSEC-2023-0044
    ! no docs.rs build — API docs may be missing
    ! low adoption (842 dl) despite 7 releases
    ! no source repository
    ! license not declared
    ! single-maintainer project with low adoption — bus factor risk
```

### Why it scores F

Every dimension except Maturity (it is technically old) is near zero: Adoption
3/30 (842 all-time / 12 recent — nobody uses it), Maintenance 0/25 (last
release 1,240 days ago, advisory unresolved), Documentation 2/15 (no docs.rs,
no description, no repo/docs URL), Community 0/10 (no repo to query), License
2/5 (unknown). The **advisory** forces `BLOCK` even though the score already
warrants `F` — the override rule in action: security trumps grade.

### Decision

**Avoid.** Find an alternative via `search` on the same domain. If this crate
is the only option, either (a) pin to a version outside the advisory's affected
range *and* vendor it for self-maintenance, or (b) reconsider whether you need
the functionality at all.

---

## Example 5 — Cold-start (a new crate with great docs but low adoption)

> **Fictional** crate (`fresh-validation`) showing the cold-start problem. Numbers illustrative.

```bash
python3 scripts/crate_eval.py eval fresh-validation
```

```text
=== fresh-validation === C (58/100) — ACCEPTABLE — investigate specific concerns
  ergonomic input validation with derive macros
  version 0.2.0  |  310 downloads (310 recent)  |  license: MIT OR Apache-2.0
  repo: https://github.com/example/fresh-validation

  Subscores:
    adoption        █░░░░░░░░░░░░░░░░░░░░░░░░░   2/30
    maintenance     ████████████████████████░░  20/25
    documentation   ██████████████████████████  13/15
    maturity        ██████░░░░░░░░░░░░░░░░░░░░   6/15
    community       █░░░░░░░░░░░░░░░░░░░░░░░░░   1/10
    license         ██████████████████████████   5/5

  Notes:
    + actively maintained (updated 4 days ago)
    + well-documented (docs.rs + custom docs URL)
```

### Interpret

The **C grade understates quality**. The subscores tell the real story:
Documentation 13/15 (excellent onboarding), Maintenance 20/25 (updated 4 days ago), License 5/5 (clean dual permissive), Maturity 6/15 (only age is low — it's new; version is 0.2). The score is dragged down entirely by **cold-start signals**: adoption 2/30 and community 1/10 are near zero simply because the crate is two weeks old. See the [cold-start limitation](../references/scoring-rubric.md#known-limitations).

### Decision

For an **early adopter**, this is acceptable — possibly attractive. Before
adopting: (1) check the maintainer's track record (a reputable author
de-risks a young crate); (2) pin the version (`=0.2.0`) since pre-1.0 APIs
churn; (3) vendor or fork-ready, in case the maintainer abandons it.

For a **load-bearing production dependency** where stability is paramount, the
cold-start score is doing its job — wait for adoption to accrue, or accept the
risk explicitly.

---

## Common patterns

### When to trust the score vs override it

| Situation                                  | Trust score? | Why                                            |
|--------------------------------------------|:------------:|------------------------------------------------|
| General-purpose crate, broad audience      | Yes          | Signals accurately reflect adoption/health     |
| Niche / domain-specific crate              | Override down| Low adoption is structural, not a quality flag |
| Brand-new crate (<1 month)                 | Override up  | Cold-start suppresses good signals             |
| Maintained fork of an abandoned crate      | Override up  | Fork's downloads are low but it's the live one |
| Crate with a security advisory             | **Never**    | Advisory forces BLOCK regardless of score      |

### How to read subscores to find weaknesses

The subscore table localizes the problem:

- **Low Adoption, high rest** → niche or new; usually fine.
- **Low Maintenance, high Adoption** → popular-but-stale; check for a successor.
- **Low Documentation, high rest** → onboarding cost; budget time.
- **Low Community, high rest** → bus-factor risk; vendor it.
- **Low License** → policy review; not a health issue per se.
- **Low Maturity** → expect breaking changes; pin exact versions.

### When to investigate red flags vs accept them

- **Block-level** (advisory, no source, missing license) → never accept without explicit resolution.
- **High** (stale, bus factor) → investigate the issue tracker; accept only with documented mitigation.
- **Medium** (no docs, churn, pre-1.0) → usually survivable; note and move on, unless they cluster.
- **Informational** (copyleft, few contributors) → context-dependent; apply your policy.

See [`references/red-flags.md`](../references/red-flags.md) for the full catalog and override rules.

### After you decide

The post-adoption workflow is the same regardless of pick: add to `Cargo.toml`
and pin policy → `rust-semver`; set up `cargo-deny` for license + advisory
governance → `rust-dependencies`; run `cargo audit` in CI for authoritative
advisory checks. The discovery skill's job ends when the crate enters
`Cargo.toml`; manifest mechanics belong to `rust-cargo-build`.

## Upstream sources

- [crates.io](https://crates.io) — crate registry and download statistics
- [docs.rs](https://docs.rs) — documentation builds
- [RustSec Advisory Database](https://rustsec.org/) — security advisories
- [`tracing`](https://docs.rs/tracing), [`log`](https://docs.rs/log) — logging ecosystem references
- [cargo-audit](https://github.com/rustsec/rustsec/tree/main/cargo-audit) — CI advisory scanning
