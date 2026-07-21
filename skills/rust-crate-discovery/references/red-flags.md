# Red Flags Catalog

> Reference companion to [`SKILL.md`](../SKILL.md). The authoritative detection
> logic is `compute_red_flags()` in [`scripts/crate_eval.py`](../scripts/crate_eval.py).
> This document explains each flag's meaning, false-positive cases, and the
> recommended action. If a flag's threshold differs from the script, the
> **script is authoritative**.

## How to read red flags

A red flag is a *specific, machine-detectable concern* — not a vague worry.
Every flag has a precise trigger condition in code. Flags do **not** directly
subtract from the score; the score is computed independently from the
[subscores](scoring-rubric.md). Instead, flags gate the *recommendation*
string and tell the human where to look.

> **Golden rule:** a security advisory always overrides the score to `BLOCK`.
> Other flags are advisory — investigate before adopting, but they do not
> automatically disqualify a crate.

## Catalog at a glance

| # | Flag                                            | Severity   | Detection source        | Default action        |
|---|-------------------------------------------------|------------|-------------------------|-----------------------|
| 1 | RustSec advisory present                        | **Block**  | RustSec                 | Pin fixed version / replace |
| 2 | No source repository                            | **Block**  | crates.io `repository`  | Avoid — cannot audit  |
| 3 | License not declared                            | High       | crates.io `license`     | Clarify before use    |
| 4 | No release in >12 months                        | High       | crates.io `updated_at`  | Investigate / fork    |
| 5 | Last GitHub commit >6 months                    | High       | GitHub `pushed_at`      | Investigate           |
| 6 | Single maintainer + low adoption                | High       | GitHub + crates.io      | Assess bus factor     |
| 7 | No docs.rs build                                | Medium     | docs.rs                 | Check docs manually   |
| 8 | Low adoption with many versions                 | Medium     | crates.io               | Investigate quality   |
| 9 | Pre-1.0 with >20 versions                       | Medium     | crates.io               | Expect API churn      |
| 10| Copyleft license (informational)                | Low / Info | crates.io `license`     | Check policy fit      |
| 11| Few contributors (2–3)                          | Low / Info | GitHub                  | Note in review        |
| 12| Recent version has fewer downloads than older   | Low / Info | crates.io versions      | Investigate regression|

> Flags 1–9 are emitted by `compute_red_flags()`. Flags 10–12 are not
> auto-emitted today but are documented here as manual review prompts because
> the underlying signals are already collected.

---

## Block-level flags

These mean **stop and resolve before adopting**, regardless of the numeric
score. The recommendation engine forces `BLOCK` on a security advisory; the
other two require manual enforcement but should be treated the same way.

### 1. RustSec advisory present

| Aspect    | Value                                                                  |
|-----------|------------------------------------------------------------------------|
| Severity  | **Block**                                                              |
| Detection | `fetch_rustsec()` scrapes `https://rustsec.org/packages/<crate>.html` for `RUSTSEC-YYYY-NNNN` IDs |
| Threshold | ≥ 1 advisory                                                           |
| Action    | Pin to a fixed version listed in the advisory, or pick an alternative. |

**What it means**: a known vulnerability (RCE, memory unsafety, logic bug, yanked
dependency) has been filed against this crate or a version range of it.

**False positives**: *none by policy*. Even a low-severity advisory is a real,
filed, peer-reviewed disclosure. The action is always to resolve, never to
ignore. If you believe the advisory does not apply to your usage (e.g. an
optional feature you don't enable), document that decision explicitly.

**Detection caveat**: RustSec has no stable per-crate JSON API. The script
scrapes the HTML package page and regex-matches advisory IDs. If rustsec.org
changes its markup, this check silently returns empty — a missing advisory
flag is *not* proof of safety. Cross-check with `cargo audit` on a real
`Cargo.lock` for authoritative results.

```text
! 2 RustSec advisory/advisories: RUSTSEC-2024-0344, RUSTSEC-2023-0044
```

### 2. No source repository

| Aspect    | Value                                                                  |
|-----------|------------------------------------------------------------------------|
| Severity  | **Block**                                                              |
| Detection | `sig.repository` is empty after crates.io fetch                        |
| Threshold | `not sig.repository`                                                   |
| Action    | Avoid unless the publisher is a trusted org with an alternative audit path. |

**What it means**: there is no public source to read, audit, or fork. You are
depending on a binary blob with no path to self-help if the maintainer
disappears or a bug is found.

**False positives**: a crate whose `repository` field points to a non-GitHub
URL (GitLab, sourcehut, a self-hosted forge) currently loses GitHub signals
but is *not* flagged as "no source repository" — the field is populated. The
flag fires only when the field is genuinely empty.

**Action**: prefer a crate with auditable source. If you must use a no-source
crate, treat it as proprietary and apply your vendor-review process.

### 3. License not declared

| Aspect    | Value                                                                  |
|-----------|------------------------------------------------------------------------|
| Severity  | High (treat as block for commercial use)                               |
| Detection | `sig.license` is empty                                                 |
| Threshold | `not sig.license`                                                      |
| Action    | Do not use without written license clarification from the maintainer. |

**What it means**: without a license, default copyright applies — which means
**no permission to use, modify, or distribute**. This is not a stylistic
concern; it is a legal blocker for most organizations.

**False positives**: occasionally the license is declared in the README or a
`LICENSE` file but not in `Cargo.toml`'s `license` field. In that case the
flag still fires (the field is what consumers see), but the maintainer can fix
it trivially — file an issue.

**Note**: the score gives 2 points for "unknown" (neutral), but the flag
escalates it to an actionable concern. Score and flag are independent by
design.

---

## High-severity flags

These strongly suggest the crate is *not safe to depend on long-term* without
mitigation. Investigate before adopting; consider alternatives.

### 4. No release in >12 months

**Detection**: `_days_since(sig.updated_at) > 365` (High). **Action**: check the issue tracker for unresolved bugs; consider a maintained fork.

**What it means**: no release in over a year. May indicate abandonment, may indicate a "done" crate.

**False positives — the most common one**: a mature, stable crate that simply doesn't need releases (`libc`, `memchr`, `bitflags` can go years between releases while remaining healthy). Distinguish by: are open issues piling up with no response (→ abandoned)? Is the maintainer active elsewhere (→ "done, not dead")? Does it still compile on current stable Rust (a green `cargo build` is strong evidence of life)?

**Action**: read the issue tracker and the maintainer's recent activity. If unresolved security or correctness bugs sit open with no response, treat as abandoned and look for a fork or alternative.

```text
! no release in 547 days (>18 months)
```

### 5. Last GitHub commit >6 months

**Detection**: `_days_since(github_last_commit) > 180` (High). **Action**: verify development hasn't moved to a fork or another repo.

**What it means**: the source repo has gone quiet. Combined with flag 4 this is strong evidence of abandonment; on its own it may mean development moved.

**False positives**: a release-driven workflow where commits land in bursts then go quiet between releases. Also, some crates publish from a monorepo (e.g. `tokio`'s ecosystem), so the `repository` URL's commit history may understate real activity.

**Action**: check whether a successor repo exists. If the maintainer has a newer crate covering the same domain, prefer that.

### 6. Single maintainer + low adoption (bus factor)

**Detection**: `github_contributors <= 1 AND downloads < 10_000` (High). **Action**: assess whether you can fork-and-maintain if the author steps away.

**What it means**: if one person stops maintaining this, nobody is left; low adoption also means few eyes finding bugs.

**False positives**: a brand-new crate from a reputable maintainer can trip this before it gains traction — see the cold-start example in [evaluation-examples.md](../examples/evaluation-examples.md). The contributor count is GitHub-derived; a crate hosted elsewhere may have more contributors than the flag implies.

**Action**: if the crate is load-bearing for you, keep a vendored copy, consider sponsoring/contributing, and have a documented fallback plan.

---

## Medium-severity flags

These warrant investigation but are not automatic disqualifiers. Often they
reflect a trade-off the maintainer has consciously made.

### 7. No docs.rs build

**Detection**: `not sig.docs_rs_present` — HEAD probe to docs.rs returned non-200 (Medium). **Action**: check whether docs exist elsewhere; assess onboarding cost.

**What it means**: the canonical Rust documentation host has nothing for this crate — either it never built (feature/platform issue) or was published before docs.rs coverage.

**False positives**: very new crates may not have their first docs.rs build yet (lag of minutes to hours). Crates with `doctests = false` or platform-gated APIs can fail to build docs without being undocumented — check the repo's own rendered docs.

**Action**: read the README and any in-repo docs. If the only documentation is source comments, budget extra onboarding time.

### 8. Low adoption with many versions

**Detection**: `downloads < 1000 AND version_count > 5` (Medium). **Action**: investigate why adoption isn't growing despite release churn.

**What it means**: the maintainer is shipping releases but nobody is picking them up — often churn without traction (frequent breaking changes driving users away), or a niche crate with a small audience.

**False positives**: a genuinely niche crate (e.g. a bindings wrapper for an obscure library) may legitimately have few users and many patch releases. Judge by whether releases fix real bugs vs. churn the API.

**Action**: read the changelog. If versions are breaking-change after breaking-change, the API is unstable and you'll be on an upgrade treadmill.

### 9. Pre-1.0 with >20 versions

**Detection**: `major == 0 AND version_count > 20` (Medium). **Action**: pin exact version; expect breaking changes on minor bumps.

**What it means**: pre-1.0 semver lets minor bumps be breaking. Twenty-plus 0.x releases is strong evidence the API is still churning — every `cargo update` is a potential surprise.

**False positives**: some crates deliberately stay pre-1.0 while being extremely stable (the maintainer reserves the right to break but rarely exercises it). Check the actual changelog rather than the version number alone.

**Action**: pin with `=x.y.z` rather than `^x.y.z` until the crate reaches 1.0. See `rust-semver` for pinning policy.

---

## Low-severity / informational

These are not auto-emitted as red flags today, but the underlying signals are
already collected. Use them as manual review prompts.

### 10. Copyleft license

**Signal**: license contains GPL/AGPL/MPL/LGPL/SSPL.
**Meaning**: may conflict with your organization's licensing policy (many
shops ban AGPL/SSPL outright; LGPL has linking constraints).
**Action**: confirm with legal/licensing before adopting. The score already
reduces the License sub-score (1 for strong copyleft, 3 for weak).

### 11. Few contributors (2–3)

**Signal**: `github_contributors` is small but above the single-maintainer
threshold.
**Meaning**: better than one maintainer, but still thin. A key person leaving
could stall the project.
**Action**: note in your dependency review; not a blocker.

### 12. Recent version has fewer downloads than older

**Signal**: the newest published version has lower download counts than the
prior version (visible in `--verbose` raw signals or the crates.io versions
endpoint).
**Meaning**: users may be pinning to the older version — possibly due to a
regression, a breaking change, or a yank.
**Action**: read the release notes for the newer version; check for an
unresolved issue that drove users to pin.

---

## Reading flags in combination

Flags compound. A single medium flag is usually survivable; the *pattern*
matters more than any individual flag.

| Pattern                                         | Interpretation                          | Action            |
|-------------------------------------------------|-----------------------------------------|-------------------|
| Advisory (any)                                  | Security blocker                        | **Block**         |
| No repo + no license                            | Unauditable + legally unclear           | **Avoid**         |
| Stale release + stale commits + bus factor      | Abandoned                               | Find alternative  |
| No docs + pre-1.0 + 20 versions                 | Hard to learn + unstable                | High onboarding cost |
| Single medium flag, otherwise strong            | Localized concern                       | Investigate, likely OK |
| Zero flags, grade A                             | Healthy                                 | Adopt with confidence |

## When to override a flag

You may legitimately accept a flagged crate when:

- **Stale release on a "done" crate**: the issue tracker is quiet, it still
  builds on current Rust, and the API is stable. Document the decision.
- **Bus factor on a vendored dep**: you vendor the source and can patch it
  yourself.
- **Copyleft in an internal-only tool**: policy permits it for non-distributed
  software.

Always record *why* you overrode the flag, so the next reviewer doesn't
re-litigate it.

## When NOT to override

Never override:

- A security advisory without pinning to a fixed version.
- A missing license for code that ships in a distributed product.
- A no-source-repository crate in a security-critical path.

## Upstream sources

- [RustSec Advisory Database](https://rustsec.org/) — advisory IDs and fixed versions
- [rustsec/advisory-db](https://github.com/rustsec/advisory-db) — machine-readable TOML advisories
- [crates.io data access](https://crates.io/data-access) — `repository`, `license`, `updated_at` fields
- [GitHub REST API: repositories](https://docs.github.com/en/rest/repos/repos) — `pushed_at`, contributor counts
- [docs.rs](https://docs.rs) — documentation build presence
- [cargo-audit](https://github.com/rustsec/rustsec/tree/main/cargo-audit) — local authoritative advisory scanner
