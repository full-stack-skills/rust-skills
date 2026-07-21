#!/usr/bin/env python3
"""crates.io discovery + multi-source evaluation tool for AI agents.

Searches crates.io, fetches metadata from 4 sources (crates.io API, docs.rs,
GitHub API, RustSec advisory), and produces a weighted 0-100 score with a
human-readable grade and red-flag list.

Usage:
    ./crate_eval.py search "orm"
    ./crate_eval.py search "database orm" --limit 5
    ./crate_eval.py eval rbatis
    ./crate_eval.py eval rbatis --json
    ./crate_eval.py compare rbatis diesel sea-orm sqlx

The tool requires network access. It sends a User-Agent header to crates.io
as required by the API policy. Rate limiting is handled by spacing requests.

Output formats:
    - default: human-readable table + report
    - --json:  machine-readable JSON for agent consumption
    - --quiet: only the top recommendation

Scoring model (weighted 0-100):
    Adoption      30  (log-scaled downloads + recent_downloads)
    Maintenance   25  (last update recency + version count + GitHub commits)
    Documentation 15  (docs.rs presence + README + description completeness)
    Maturity      15  (age + has repo + stable version >= 1.0)
    Community     10  (GitHub stars + contributors + dependents)
    License       5   (OSI-approved + permissive preferred)

Grades:
    A  >= 85   excellent — recommended
    B  70-84   good — likely suitable
    C  55-69   acceptable — verify fit
    D  40-54   risky — investigate before use
    F  < 40    avoid — significant concerns
"""

from __future__ import annotations

import argparse
import json
import math
import sys
import time
import urllib.error
import urllib.request
from dataclasses import asdict, dataclass, field
from typing import Any

USER_AGENT = "rust-crate-discovery-agent/1.0 (https://github.com/full-stack-skills/rust-skills)"
CRATES_IO_API = "https://crates.io/api/v1"
DOCS_RS = "https://docs.rs"
GITHUB_API = "https://api.github.com"
RUSTSEC_API = "https://rustsec.org/advisories"


# === HTTP helpers ===

def _get(url: str, headers: dict[str, str] | None = None, timeout: int = 15) -> Any:
    """GET URL and return parsed JSON. Returns None on 404, raises on other errors."""
    hdrs = {"User-Agent": USER_AGENT, "Accept": "application/json"}
    if headers:
        hdrs.update(headers)
    req = urllib.request.Request(url, headers=hdrs)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None
        raise


def _gh_owner_repo(repo_url: str) -> tuple[str, str] | None:
    """Extract owner/repo from a GitHub URL."""
    if not repo_url:
        return None
    repo_url = repo_url.rstrip("/")
    if "github.com/" not in repo_url:
        return None
    parts = repo_url.split("github.com/", 1)[1].split("/")
    if len(parts) >= 2:
        owner, repo = parts[0], parts[1]
        repo = repo.removesuffix(".git")
        return owner, repo
    return None


# === Data classes ===

@dataclass
class CrateSignals:
    """All raw signals collected from 4 sources."""
    name: str = ""
    description: str = ""
    repository: str = ""
    homepage: str = ""
    documentation: str = ""
    keywords: list[str] = field(default_factory=list)
    categories: list[str] = field(default_factory=list)
    license: str = ""
    max_version: str = ""
    newest_version: str = ""
    rust_version: str | None = None
    downloads: int = 0
    recent_downloads: int = 0
    created_at: str = ""
    updated_at: str = ""
    version_count: int = 0
    exact_match: bool = False
    # docs.rs
    docs_rs_present: bool = False
    docs_rs_build_status: str = ""  # "ok" | "failed" | "unknown"
    # GitHub
    github_stars: int = 0
    github_forks: int = 0
    github_open_issues: int = 0
    github_last_commit: str = ""  # ISO date
    github_contributors: int = 0
    # RustSec
    advisories: list[dict[str, str]] = field(default_factory=list)


@dataclass
class CrateScore:
    """Weighted evaluation result for one crate."""
    name: str
    grade: str
    score: int
    subscores: dict[str, int]
    signals: CrateSignals
    red_flags: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)
    recommendation: str = ""


# === Source fetchers ===

def fetch_crates_io_search(query: str, limit: int = 10, category: str | None = None) -> list[dict[str, Any]]:
    """Search crates.io for crates matching query."""
    params = [f"q={urllib.parse.quote(query)}", f"per_page={min(limit, 100)}"]
    if category:
        params.append(f"category={urllib.parse.quote(category)}")
    url = f"{CRATES_IO_API}/crates?{'&'.join(params)}"
    data = _get(url)
    if not data:
        return []
    return data.get("crates", [])[:limit]


def fetch_crates_io_detail(name: str) -> CrateSignals | None:
    """Fetch full crate metadata from crates.io."""
    data = _get(f"{CRATES_IO_API}/crates/{urllib.parse.quote(name)}")
    if not data or "crate" not in data:
        return None
    c = data["crate"]
    sig = CrateSignals(
        name=c.get("name", name),
        description=c.get("description", "") or "",
        repository=c.get("repository", "") or "",
        homepage=c.get("homepage", "") or "",
        documentation=c.get("documentation", "") or "",
        keywords=c.get("keywords", []) or [],
        categories=c.get("categories", []) or [],
        license=c.get("license", "") or "",
        max_version=c.get("max_version", "") or "",
        newest_version=c.get("newest_version", "") or "",
        rust_version=c.get("rust_version"),
        downloads=c.get("downloads", 0) or 0,
        recent_downloads=c.get("recent_downloads", 0) or 0,
        created_at=c.get("created_at", "") or "",
        updated_at=c.get("updated_at", "") or "",
        version_count=len(data.get("versions", [])),
        exact_match=c.get("exact_match", False),
    )
    # version_count may be 0 if versions not embedded; fetch summary
    if sig.version_count == 0:
        sig.version_count = c.get("versions", []) and len(c["versions"]) or 0
    # License is on the version endpoint, not the crate summary — fetch it.
    if not sig.license and sig.max_version:
        try:
            vdata = _get(f"{CRATES_IO_API}/crates/{urllib.parse.quote(name)}/{sig.max_version}")
            if vdata and "version" in vdata:
                sig.license = vdata["version"].get("license", "") or ""
                if not sig.rust_version:
                    sig.rust_version = vdata["version"].get("rust_version")
        except Exception:
            pass
    return sig


def fetch_docs_rs(name: str, version: str | None = None) -> tuple[bool, str]:
    """Check docs.rs for doc presence and build status.

    Returns (present, status) where status is 'ok', 'failed', or 'unknown'.
    """
    # We do a HEAD-like via GET on the docs.rs API or page.
    # The simplest: try the metadata redirect.
    url = f"https://docs.rs/crate/{name}/"
    if version:
        url += f"{version}/"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT}, method="HEAD")
        with urllib.request.urlopen(req, timeout=10) as resp:
            present = resp.status == 200
            return present, "ok" if present else "unknown"
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return False, "unknown"
        # 5xx or other — docs.rs may be having issues
        return True, "unknown"
    except Exception:
        return False, "unknown"


def fetch_github(repo_url: str) -> dict[str, Any]:
    """Fetch GitHub repo stats. Returns dict with stars/forks/issues/last_commit/contributors."""
    result = {"stars": 0, "forks": 0, "open_issues": 0, "last_commit": "", "contributors": 0}
    parsed = _gh_owner_repo(repo_url)
    if not parsed:
        return result
    owner, repo = parsed
    try:
        data = _get(f"{GITHUB_API}/repos/{owner}/{repo}")
        if data:
            result["stars"] = data.get("stargazers_count", 0) or 0
            result["forks"] = data.get("forks_count", 0) or 0
            result["open_issues"] = data.get("open_issues_count", 0) or 0
            pushed = data.get("pushed_at", "")
            if pushed:
                result["last_commit"] = pushed[:10]
    except Exception:
        pass
    # contributors (separate endpoint, may be rate-limited)
    try:
        # GitHub returns an array; we just need the count
        req = urllib.request.Request(
            f"{GITHUB_API}/repos/{owner}/{repo}/contributors?per_page=1&anon=true",
            headers={"User-Agent": USER_AGENT, "Accept": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            # Use Link header for total count if available
            link = resp.headers.get("Link", "")
            if "rel=\"last\"" in link:
                # parse page=N from the last URL
                import re
                m = re.search(r"page=(\d+)>; rel=\"last\"", link)
                if m:
                    result["contributors"] = int(m.group(1))
            else:
                # few contributors, count from body
                body = json.loads(resp.read().decode("utf-8"))
                result["contributors"] = len(body)
    except Exception:
        pass
    return result


def fetch_rustsec(name: str) -> list[dict[str, str]]:
    """Check RustSec for advisories. Returns list of advisory dicts."""
    # The RustSec advisory DB doesn't have a clean per-crate API.
    # We use the crates.io API's /api/v1/crates/<name>/versions and check
    # against the local cargo-audit if available. For network-only, we query
    # the RustSec advisories page indirectly via the crates.io "versions" endpoint
    # and the RustSec DB dump is too large for per-call.
    # Practical approach: query the RustSec API search.
    advisories: list[dict[str, str]] = []
    try:
        # RustSec provides a JSON feed at https://rustsec.org/advisories/<crate>.json
        # but this is unreliable. We try the packages page.
        url = f"https://rustsec.org/packages/{name}.html"
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                body = resp.read().decode("utf-8", errors="replace")
                if "No advisories" in body or "404" in body:
                    return advisories
                # crude parse: look for advisory IDs like RUSTSEC-YYYY-NNNN
                import re
                ids = re.findall(r"RUSTSEC-\d{4}-\d{2,6}", body)
                for adv_id in sorted(set(ids)):
                    advisories.append({"id": adv_id, "url": f"https://rustsec.org/advisories/{adv_id}.html"})
        except urllib.error.HTTPError:
            pass
    except Exception:
        pass
    return advisories


# === Scoring model ===

PERMISSIVE_LICENSES = {"MIT", "Apache-2.0", "BSD-3-Clause", "ISC", "0BSD", "Unlicense", "Zlib", "Unicode-DFS-2016", "Unicode-3.0"}


def _log_scale(value: int, midpoint: int, max_score: int) -> int:
    """Logarithmic scale: 0 → 0, midpoint → max_score/2, 10*midpoint → max_score."""
    if value <= 0:
        return 0
    if value <= midpoint:
        return int(max_score * 0.5 * (math.log10(value + 1) / math.log10(midpoint + 1)))
    return int(min(max_score, max_score * 0.5 + 0.5 * max_score * math.log10(value / midpoint + 1) / math.log10(10)))


def _days_since(iso_date: str) -> int | None:
    """Days since an ISO date string. None if unparseable."""
    if not iso_date:
        return None
    try:
        from datetime import datetime, timezone
        # handle fractional seconds and Z
        iso_date = iso_date.replace("Z", "+00:00")
        dt = datetime.fromisoformat(iso_date)
        now = datetime.now(timezone.utc)
        return max(0, (now - dt).days)
    except Exception:
        return None


def score_adoption(sig: CrateSignals) -> int:
    """Adoption: 30 points. Weighted between all-time downloads and recent downloads."""
    # all-time: midpoint 50k = 15 points
    all_time = _log_scale(sig.downloads, 50_000, 15)
    # recent (90 days): midpoint 5k = 15 points
    recent = _log_scale(sig.recent_downloads, 5_000, 15)
    return min(30, all_time + recent)


def score_maintenance(sig: CrateSignals) -> int:
    """Maintenance: 25 points."""
    score = 0
    days_since_update = _days_since(sig.updated_at)
    if days_since_update is not None:
        if days_since_update < 90:
            score += 12
        elif days_since_update < 365:
            score += 8
        elif days_since_update < 730:
            score += 4
        # else: 0 (stale)
    # version count: midpoint 20 = 8 points
    score += _log_scale(sig.version_count, 20, 8)
    # GitHub last commit recency: 5 points
    if sig.github_last_commit:
        days_commit = _days_since(sig.github_last_commit + "T00:00:00Z")
        if days_commit is not None:
            if days_commit < 30:
                score += 5
            elif days_commit < 180:
                score += 3
            elif days_commit < 365:
                score += 1
    return min(25, score)


def score_documentation(sig: CrateSignals) -> int:
    """Documentation: 15 points."""
    score = 0
    if sig.docs_rs_present:
        score += 7
    if sig.description and len(sig.description) > 30:
        score += 3
    if sig.documentation and (sig.documentation.startswith("https://docs.rs/") or sig.documentation.startswith("https://www.rust-lang.org/") or sig.documentation.startswith("https://")):
        score += 3
    if sig.repository:
        score += 2
    return min(15, score)


def score_maturity(sig: CrateSignals) -> int:
    """Maturity: 15 points."""
    score = 0
    # age
    age_days = _days_since(sig.created_at)
    if age_days is not None:
        if age_days > 365 * 3:
            score += 6
        elif age_days > 365:
            score += 4
        elif age_days > 90:
            score += 2
    # stable version (>= 1.0.0)
    try:
        major = int(sig.max_version.split(".")[0])
        if major >= 1:
            score += 5
        elif major == 0:
            score += 2  # pre-1.0 is fine but not as mature
    except (ValueError, IndexError):
        pass
    # has repository
    if sig.repository:
        score += 4
    return min(15, score)


def score_community(sig: CrateSignals) -> int:
    """Community: 10 points."""
    score = 0
    # stars: midpoint 500 = 6 points
    score += _log_scale(sig.github_stars, 500, 6)
    # contributors: midpoint 10 = 4 points
    score += _log_scale(sig.github_contributors, 10, 4)
    return min(10, score)


def score_license(sig: CrateSignals) -> int:
    """License: 5 points. Permissive preferred."""
    if not sig.license:
        return 2  # unknown — neutral
    licenses = [l.strip() for l in sig.license.replace(" OR ", "/").replace(" AND ", "/").split("/")]
    if any(l in PERMISSIVE_LICENSES for l in licenses):
        return 5
    if "MIT" in sig.license or "Apache" in sig.license:
        return 5
    if "MPL" in sig.license or "LGPL" in sig.license:
        return 3  # weak copyleft
    if "GPL" in sig.license or "AGPL" in sig.license or "SSPL" in sig.license:
        return 1  # strong copyleft
    return 2  # other


def compute_red_flags(sig: CrateSignals) -> list[str]:
    """List specific concerns that should give a user pause."""
    flags: list[str] = []
    # stale
    days = _days_since(sig.updated_at)
    if days is not None and days > 365:
        flags.append(f"no release in {days} days (>{days // 30} months)")
    # GitHub silent
    if sig.github_last_commit:
        d = _days_since(sig.github_last_commit + "T00:00:00Z")
        if d is not None and d > 180:
            flags.append(f"last GitHub commit {d} days ago")
    # advisories
    if sig.advisories:
        ids = ", ".join(a["id"] for a in sig.advisories)
        flags.append(f"{len(sig.advisories)} RustSec advisory/advisories: {ids}")
    # no docs
    if not sig.docs_rs_present:
        flags.append("no docs.rs build — API docs may be missing")
    # low downloads but high version (churn)
    if sig.downloads < 1000 and sig.version_count > 5:
        flags.append(f"low adoption ({sig.downloads} dl) despite {sig.version_count} releases")
    # no repo
    if not sig.repository:
        flags.append("no source repository")
    # pre-1.0 + many breaking changes implied
    try:
        major = int(sig.max_version.split(".")[0])
        if major == 0 and sig.version_count > 20:
            flags.append(f"pre-1.0 with {sig.version_count} versions — API likely unstable")
    except (ValueError, IndexError):
        pass
    # no license
    if not sig.license:
        flags.append("license not declared")
    # single owner + low community
    if sig.github_contributors <= 1 and sig.downloads < 10_000:
        flags.append("single-maintainer project with low adoption — bus factor risk")
    return flags


def compute_notes(sig: CrateSignals) -> list[str]:
    """List positive signals."""
    notes: list[str] = []
    if sig.exact_match:
        notes.append("exact name match")
    if sig.recent_downloads > sig.downloads * 0.3 / 9:  # 90-day share of all-time
        notes.append("strong recent adoption")
    days = _days_since(sig.updated_at)
    if days is not None and days < 30:
        notes.append(f"actively maintained (updated {days} days ago)")
    if sig.github_stars > 1000:
        notes.append(f"popular on GitHub ({sig.github_stars} stars)")
    if sig.docs_rs_present and sig.documentation:
        notes.append("well-documented (docs.rs + custom docs URL)")
    try:
        major = int(sig.max_version.split(".")[0])
        if major >= 1:
            notes.append(f"stable v{sig.max_version} (>= 1.0)")
    except (ValueError, IndexError):
        pass
    return notes


def grade_from_score(score: int) -> str:
    if score >= 85:
        return "A"
    if score >= 70:
        return "B"
    if score >= 55:
        return "C"
    if score >= 40:
        return "D"
    return "F"


def recommendation_for(grade: str, red_flags: list[str]) -> str:
    has_security = any("advisory" in f.lower() for f in red_flags)
    has_stale = any("no release" in f.lower() or "last github commit" in f.lower() for f in red_flags)
    if grade in ("A", "B") and not has_security:
        if grade == "A":
            return "RECOMMENDED — strong fit, low risk"
        return "LIKELY SUITABLE — verify fit for your use case"
    if grade == "C":
        return "ACCEPTABLE — investigate specific concerns before adopting"
    if has_security:
        return "BLOCK — unresolved security advisory; pin to fixed version or avoid"
    if has_stale:
        return "CAUTION — appears unmaintained; consider alternatives"
    return "RISKY — significant concerns; evaluate alternatives"


def evaluate(name: str, skip_github: bool = False, skip_rustsec: bool = False) -> CrateScore | None:
    """Full evaluation of a single crate."""
    sig = fetch_crates_io_detail(name)
    if sig is None:
        return None

    # docs.rs
    present, status = fetch_docs_rs(name, sig.max_version)
    sig.docs_rs_present = present
    sig.docs_rs_build_status = status

    # GitHub
    if not skip_github and sig.repository:
        gh = fetch_github(sig.repository)
        sig.github_stars = gh["stars"]
        sig.github_forks = gh["forks"]
        sig.github_open_issues = gh["open_issues"]
        sig.github_last_commit = gh["last_commit"]
        sig.github_contributors = gh["contributors"]
        time.sleep(0.1)  # be nice to GitHub

    # RustSec
    if not skip_rustsec:
        sig.advisories = fetch_rustsec(name)
        time.sleep(0.1)

    subscores = {
        "adoption": score_adoption(sig),
        "maintenance": score_maintenance(sig),
        "documentation": score_documentation(sig),
        "maturity": score_maturity(sig),
        "community": score_community(sig),
        "license": score_license(sig),
    }
    total = sum(subscores.values())
    grade = grade_from_score(total)
    red_flags = compute_red_flags(sig)
    notes = compute_notes(sig)
    rec = recommendation_for(grade, red_flags)

    return CrateScore(
        name=name,
        grade=grade,
        score=total,
        subscores=subscores,
        signals=sig,
        red_flags=red_flags,
        notes=notes,
        recommendation=rec,
    )


# === Output formatters ===

def format_score_human(result: CrateScore, verbose: bool = False) -> str:
    s = result.signals
    lines = [
        f"=== {result.name} === {result.grade} ({result.score}/100) — {result.recommendation}",
        f"  {s.description[:120]}",
        f"  version {s.max_version}  |  {s.downloads:,} downloads ({s.recent_downloads:,} recent)  |  license: {s.license or 'unknown'}",
        f"  repo: {s.repository or '(none)'}",
        f"  docs: {s.documentation or '(none)'}",
        "",
        "  Subscores:",
    ]
    for k, v in result.subscores.items():
        bar = "█" * (v // 2) + "░" * (25 - v // 2)
        max_for = {"adoption": 30, "maintenance": 25, "documentation": 15, "maturity": 15, "community": 10, "license": 5}
        lines.append(f"    {k:15} {bar} {v:>3}/{max_for.get(k, '?')}")
    if result.notes:
        lines.append("")
        lines.append("  Notes:")
        for n in result.notes:
            lines.append(f"    + {n}")
    if result.red_flags:
        lines.append("")
        lines.append("  Red flags:")
        for f in result.red_flags:
            lines.append(f"    ! {f}")
    if verbose:
        lines.append("")
        lines.append("  Raw signals:")
        lines.append(f"    created: {s.created_at[:10] if s.created_at else '?'}  updated: {s.updated_at[:10] if s.updated_at else '?'}")
        lines.append(f"    versions: {s.version_count}  keywords: {', '.join(s.keywords[:5]) or '(none)'}  categories: {', '.join(s.categories) or '(none)'}")
        lines.append(f"    github: ⭐{s.github_stars}  ⑂{s.github_forks}  ⚠{s.github_open_issues} issues  contributors: {s.github_contributors}")
        lines.append(f"    docs.rs: {'yes' if s.docs_rs_present else 'no'} ({s.docs_rs_build_status})  rust_version: {s.rust_version or 'unspecified'}")
    return "\n".join(lines)


def format_score_json(result: CrateScore) -> str:
    d = asdict(result)
    return json.dumps(d, indent=2, default=str)


def format_search_table(crates: list[dict[str, Any]], limit: int = 10) -> str:
    if not crates:
        return "No crates found."
    lines = [
        f"{'NAME':<32} {'VER':<10} {'DL':>10} {'RECENT':>9} {'UPDATED':<12} DESCRIPTION",
        "-" * 120,
    ]
    for c in crates[:limit]:
        name = c.get("id", "")[:30]
        ver = c.get("max_version", "")[:9]
        dl = c.get("downloads", 0) or 0
        recent = c.get("recent_downloads", 0) or 0
        updated = (c.get("updated_at", "") or "")[:10]
        desc = (c.get("description", "") or "")[:60]
        lines.append(f"{name:<32} {ver:<10} {dl:>10,} {recent:>9,} {updated:<12} {desc}")
    lines.append("")
    lines.append(f"({len(crates)} results)")
    return "\n".join(lines)


def format_compare(results: list[CrateScore]) -> str:
    lines = [
        f"{'NAME':<24} {'GRADE':<7} {'SCORE':>6} {'ADOPT':>7} {'MAINT':>7} {'DOCS':>6} {'MATUR':>7} {'COMM':>6} {'LIC':>5}  RECOMMENDATION",
        "-" * 110,
    ]
    sorted_results = sorted(results, key=lambda r: r.score, reverse=True)
    for r in sorted_results:
        sc = r.subscores
        lines.append(
            f"{r.name:<24} {r.grade:<7} {r.score:>6} "
            f"{sc['adoption']:>3}/30 {sc['maintenance']:>3}/25 {sc['documentation']:>3}/15 "
            f"{sc['maturity']:>3}/15 {sc['community']:>3}/10 {sc['license']:>3}/5  {r.recommendation}"
        )
    if sorted_results:
        winner = sorted_results[0]
        lines.append("")
        lines.append(f"Top: {winner.name} ({winner.grade}, {winner.score}/100)")
        if winner.red_flags:
            lines.append(f"  ⚠ {', '.join(winner.red_flags[:3])}")
    return "\n".join(lines)


# === CLI ===

def cmd_search(args: argparse.Namespace) -> int:
    crates = fetch_crates_io_search(args.query, limit=args.limit, category=args.category)
    if args.json:
        print(json.dumps(crates, indent=2))
    else:
        print(format_search_table(crates, limit=args.limit))
    return 0


def cmd_eval(args: argparse.Namespace) -> int:
    result = evaluate(args.name, skip_github=args.skip_github, skip_rustsec=args.skip_rustsec)
    if result is None:
        print(f"Crate '{args.name}' not found on crates.io", file=sys.stderr)
        return 1
    if args.json:
        print(format_score_json(result))
    else:
        print(format_score_human(result, verbose=args.verbose))
    return 0


def cmd_compare(args: argparse.Namespace) -> int:
    results: list[CrateScore] = []
    for name in args.names:
        r = evaluate(name, skip_github=args.skip_github, skip_rustsec=args.skip_rustsec)
        if r is None:
            print(f"  (skip: '{name}' not found)", file=sys.stderr)
        else:
            results.append(r)
        time.sleep(0.2)
    if not results:
        print("No valid crates to compare", file=sys.stderr)
        return 1
    if args.json:
        print(json.dumps([asdict(r) for r in sorted(results, key=lambda r: r.score, reverse=True)], indent=2, default=str))
    else:
        print(format_compare(results))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_search = sub.add_parser("search", help="search crates.io for crates matching a query")
    p_search.add_argument("query", help="search query (e.g. 'orm', 'database', 'async http')")
    p_search.add_argument("--limit", type=int, default=10, help="max results (default 10, max 100)")
    p_search.add_argument("--category", default=None, help="filter by category (e.g. 'database', 'web-programming::http-client')")
    p_search.add_argument("--json", action="store_true", help="output JSON")
    p_search.set_defaults(func=cmd_search)

    p_eval = sub.add_parser("eval", help="evaluate a single crate in depth")
    p_eval.add_argument("name", help="crate name (e.g. 'rbatis')")
    p_eval.add_argument("--json", action="store_true", help="output JSON")
    p_eval.add_argument("--verbose", "-v", action="store_true", help="show raw signals")
    p_eval.add_argument("--skip-github", action="store_true", help="skip GitHub API (faster, less signal)")
    p_eval.add_argument("--skip-rustsec", action="store_true", help="skip RustSec advisory check")
    p_eval.set_defaults(func=cmd_eval)

    p_cmp = sub.add_parser("compare", help="compare multiple crates side-by-side")
    p_cmp.add_argument("names", nargs="+", help="crate names to compare")
    p_cmp.add_argument("--json", action="store_true", help="output JSON")
    p_cmp.add_argument("--skip-github", action="store_true", help="skip GitHub API")
    p_cmp.add_argument("--skip-rustsec", action="store_true", help="skip RustSec check")
    p_cmp.set_defaults(func=cmd_compare)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
