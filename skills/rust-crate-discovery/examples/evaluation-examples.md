# Evaluation Examples

> Worked scenarios for [`scripts/crate_eval.py`](../scripts/crate_eval.py),
> companion to [`SKILL.md`](../SKILL.md). Each example shows the command, the
> output, and — most importantly — **how to read the output and decide**.

> **All numeric outputs below are illustrative**, captured to show the *shape*
> of the tool's report. Live numbers shift daily as download counters tick and
> maintainers cut releases. Re-run the commands yourself for current values.
> The decision logic, however, is stable.

The commands assume you are in the skill directory:

```bash
cd .../skills/rust-crate-discovery
python3 scripts/crate_eval.py <subcommand>
```

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
...
(8 results)
```

### Step 2: shortlist and compare

The top four by relevance are `sqlx`, `diesel`, `sea-orm`, `rbatis`. Compare:

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

- **`sqlx` (A, 92)** — dominant on adoption (12M downloads) and full marks on
  docs/maintenance. The compile-time SQL check is a unique safety feature.
  **No red flags.**
- **`sea-orm` (A, 88)** — slightly lower adoption but a clean bill of health.
  Best fit if you want a high-level async ORM (ActiveRecord-style) rather than
  `sqlx`'s query-macro style.
- **`diesel` (B, 79)** — the License sub-score (4/5) hints at a license
  nuance (illustrative: Diesel is MIT/Apache in reality; the 4 reflects an
  older `license` field format the parser didn't fully match). Mature (15/15)
  but synchronous-only — a fitness mismatch if you need async.
- **`rbatis` (C, 61)** — lower maturity (10/15, younger) and lower adoption.
  Acceptable, but the higher-scoring alternatives dominate on health signals.

### Step 4: decide

For a new async web service, `sqlx` or `sea-orm` is the pick. Choose by
**fitness**, not raw score:

| If you want…                            | Pick      |
|-----------------------------------------|-----------|
| Compile-time-checked SQL, hand-written queries | `sqlx` |
| High-level ORM, dynamic queries, ActiveRecord style | `sea-orm` |

### Step 5: hand off

Once adopted:

```bash
# Pin policy and semver → rust-semver
# Governance: cargo-deny, license policy, advisory response → rust-dependencies
```

Add the crate to `Cargo.toml`, then set up `cargo-deny` to catch future
advisories automatically. See the `rust-dependencies` skill for the
post-adoption governance workflow.

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

- **`reqwest` (A, 94)** — maxes adoption (45M downloads) and docs. The de-facto
  high-level client. Built on `hyper`.
- **`hyper` (A, 90)** — equally healthy, maxes maturity (15/15, oldest and most
  stable). But it is **low-level**: you write HTTP/1.1 and HTTP/2 plumbing, not
  `client.get(url).send()`.
- **`ureq` (A, 86)** — minimal, blocking, zero-async. Great when you want a
  tiny dependency tree (no tokio runtime).
- **`isahc` (C, 58)** — note the maintenance drop (12/25) and the older
  `UPDATED` date (2025-11). Likely a stale-release red flag.

### Decision framework — high-level vs low-level

This is a **fitness** decision the score cannot make for you:

| Need                                        | Pick      |
|---------------------------------------------|-----------|
| "Just make an HTTP request" (most apps)     | `reqwest` |
| You are building a client/server framework  | `hyper`   |
| Blocking, minimal deps, no async runtime    | `ureq`    |
| curl-backed features (you depend on libcurl)| evaluate carefully |

The score measures *health*; all three top picks are healthy. Read the docs to
confirm the API shape matches your abstraction level. Then hand off to
`rust-api-design` for the API-fit check.

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

- **`tracing` (A, 91)** — the modern choice. Structured, async-aware,
  spans/events. The maintenance/community edge reflects active tokio-team
  stewardship.
- **`log` (A, 89)** — maxes adoption (it is the foundational facade every
  logging crate routes through) and maturity (oldest). Still the right pick for
  *libraries* that want to stay runtime-agnostic.
- **`slog` (B, 72)** — structured logging pioneer, but maintenance (16/25)
  reflects a slower release cadence. Functional but the ecosystem has
  consolidated around `tracing`.

### Ecosystem fit matters more than raw score

The gap between `tracing` (91) and `log` (89) is noise. The real question is
**architecture**:

- A **library** should depend on `log` (or `tracing`'s facade) so downstream
  apps choose the implementation.
- An **application** should pick `tracing` for structured, async-aware output.

A 2-point score difference must not override this structural decision. This is
the canonical case where the score measures *health* and you must layer a
*fitness* judgment on top.

---

## Example 4 — A risky crate (fictional `abandoned-crate`)

> This crate is **fictional**, constructed to show how multiple red flags
> compound into a low grade. The numbers below are illustrative.

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

Every dimension except Maturity (it is technically old) is near zero:

- **Adoption 3/30** — 842 all-time downloads, 12 recent: nobody is using it.
- **Maintenance 0/25** — last release 1,240 days ago; no GitHub commit signal;
  the advisory is unresolved.
- **Documentation 2/15** — no docs.rs build, no description, no repo/docs URL.
- **Community 0/10** — no GitHub signals (no repo to query).
- **License 2/5** — unknown.

The **advisory** forces the recommendation to `BLOCK` even though the score
would already warrant `F`. This is the override rule in action: security
trumps grade.

### Decision

**Avoid.** Look for an alternative via `search` on the same domain. If this
crate is the only option, you must either (a) pin to a version outside the
advisory's affected range *and* vendor it for self-maintenance, or (b)
reconsider whether you need the functionality at all.

---

## Example 5 — Cold-start (a new crate with great docs but low adoption)

> The crate `fresh-validation` is **fictional**, built to show the cold-start
> problem. Numbers are illustrative.

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

The **C grade understates the crate's quality**. Look at the subscores:

- Documentation 13/15 — excellent onboarding.
- Maintenance 20/25 — actively maintained (updated 4 days ago).
- License 5/5 — clean dual permissive.
- Maturity 6/15 — only the age sub-signal is low (it's new); version is 0.2.

The score is dragged down entirely by **cold-start signals**: adoption (2/30)
and community (1/10) are near zero simply because the crate is two weeks old.
This is the known [cold-start limitation](../references/scoring-rubric.md#known-limitations).

### Decision

For an **early adopter** willing to accept a young dependency, this is
acceptable — possibly even attractive. Before adopting:

1. **Check the maintainer's track record.** Have they published other
   well-maintained crates? A reputable author substantially de-risks a young
   crate.
2. **Pin the version** (`=0.2.0`) since it's pre-1.0 and the API will churn.
3. **Vendor or fork-ready**: keep a copy in case the maintainer abandons it.

For a **load-bearing production dependency** where stability is paramount, the
cold-start score is doing its job — wait for the crate to earn adoption, or
accept the risk explicitly.

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

The subscore table localizes the problem. Patterns:

- **Low Adoption, high everything else** → niche or new; usually fine.
- **Low Maintenance, high Adoption** → popular-but-stale; check for a
  successor.
- **Low Documentation, high everything else** → onboarding cost; budget time.
- **Low Community, high everything else** → bus-factor risk; vendor it.
- **Low License** → policy review; not a health issue per se.
- **Low Maturity** → expect breaking changes; pin exact versions.

### When to investigate red flags vs accept them

- **Block-level flags** (advisory, no source, missing license) → never accept
  without explicit resolution.
- **High-severity flags** (stale, bus factor) → investigate the issue tracker;
  accept only with a documented mitigation.
- **Medium flags** (no docs, churn, pre-1.0) → usually survivable; note them
  and move on, unless they cluster.
- **Informational flags** (copyleft, few contributors) → context-dependent;
  apply your policy.

See [`references/red-flags.md`](../references/red-flags.md) for the full
catalog and the override rules.

### After you decide

Regardless of which crate you pick, the post-adoption workflow is the same:

```bash
# 1. Add to Cargo.toml and pin policy → rust-semver
# 2. Set up cargo-deny for license + advisory governance → rust-dependencies
# 3. Run cargo audit in CI → authoritative advisory check
```

The discovery skill's job ends when the crate enters `Cargo.toml`. Governance
from there belongs to `rust-dependencies`; manifest mechanics to
`rust-cargo-build`.

## Upstream sources

- [crates.io](https://crates.io) — crate registry and download statistics
- [docs.rs](https://docs.rs) — documentation builds
- [RustSec Advisory Database](https://rustsec.org/) — security advisories
- [`tracing`](https://docs.rs/tracing), [`log`](https://docs.rs/log) — logging ecosystem references
- [cargo-audit](https://github.com/rustsec/rustsec/tree/main/cargo-audit) — CI advisory scanning
