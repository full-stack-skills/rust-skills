#!/usr/bin/env python3
"""Inventory Java and Rust migration tests and flag weak Rust test signals.

The report is intentionally conservative:

* it does not map Java tests to Rust tests by name;
* it does not prove semantic parity or test value;
* it never authorizes deletion;
* it keeps parameterized/dynamic annotations visible for manual case expansion.

Use the inventory to populate the SOURCE_PARITY, RUST_OBLIGATION, and
VALUE_ADD ledgers described by the rust-java-migration-testing skill.
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Iterable


JAVA_TEST_ANNOTATION = re.compile(
    r"@(?P<kind>Test|ParameterizedTest|RepeatedTest|TestFactory|TestTemplate)\b"
    r"(?:\s*\([^)]*\))?",
    re.MULTILINE,
)
JAVA_METHOD = re.compile(
    r"(?:public|protected|private|static|final|synchronized|\s)+"
    r"(?:<[^>{};]+>\s*)?"
    r"[\w$<>\[\],?.\s]+\s+(?P<name>[A-Za-z_$][\w$]*)\s*\(",
    re.MULTILINE,
)
RUST_TEST_ATTRIBUTE = re.compile(
    r"#\[(?P<kind>"
    r"test|"
    r"tokio::test(?:\([^]]*\))?|"
    r"async_std::test|"
    r"actix_web::test|"
    r"rstest(?:\([^]]*\))?"
    r")\]",
    re.MULTILINE,
)
RUST_FUNCTION = re.compile(
    r"(?:pub(?:\([^)]*\))?\s+)?(?:async\s+)?fn\s+(?P<name>\w+)\s*(?:<[^>{}]*>)?\s*\(",
    re.MULTILINE,
)

IGNORED_RESULT_PATTERNS = (
    (re.compile(r"\blet\s+_\s*=\s*[^;]+;"), "discarded result (`let _ = ...`)"),
    (re.compile(r"\bdrop\s*\(\s*[^)]+\s*\)\s*;"), "explicitly dropped result; verify intent"),
)
WEAK_ASSERTION_PATTERNS = (
    (re.compile(r"assert!\s*\(\s*[\w.()]+\.is_ok\(\)\s*\)"), "only checks `is_ok()`"),
    (re.compile(r"assert!\s*\(\s*[\w.()]+\.is_err\(\)\s*\)"), "only checks `is_err()`"),
)
REVIEW_NAME_PATTERNS = (
    (re.compile(r"(?:^|_)(?:debug|coverage|coverage_boost|coverage_burst)(?:_|$)", re.I),
     "coverage/debug-oriented name"),
    (re.compile(r"(?:^|_)parse(?:_only|_success)?$", re.I), "parse-only name"),
    (re.compile(r"^(?:clone|debug|display|default|type_exists|feature_compiles)(?:_|$)", re.I),
     "trait/type/compile smoke-test name"),
)
HISTORY_APPENDIX_START = "<!-- historical-design-appendix-start -->"
OBJECT_STATES = (
    "MISSING",
    "MISPLACED",
    "STUB",
    "PARTIAL",
    "UNVERIFIED",
    "IMPLEMENTED",
    "DEPENDENCY_REUSED",
    "PLATFORM_NA",
    "RUST_EXTENSION",
)
INCOMPLETE_STATES = OBJECT_STATES[:5]
OBJECT_STATE = re.compile(r"\b(" + "|".join(OBJECT_STATES) + r")\b")
OBJECT_SECTION = re.compile(
    r"^##\s+.*(?:对象映射|对象级对照|对象台账).*$", re.MULTILINE
)
NEXT_H2 = re.compile(r"^##\s+", re.MULTILINE)


@dataclass
class TestItem:
    language: str
    file: str
    line: int
    name: str
    kind: str
    signals: list[str] = field(default_factory=list)

    @property
    def location(self) -> str:
        return f"{self.file}:{self.line}"


@dataclass
class ObjectLedgerSummary:
    path: str
    current_fact_only: bool
    rows_scanned: int
    state_counts: dict[str, int]

    @property
    def incomplete_count(self) -> int:
        return sum(self.state_counts.get(state, 0) for state in INCOMPLETE_STATES)

    @property
    def migration_completion_blocked(self) -> bool:
        return self.incomplete_count > 0


def source_files(root: Path, suffix: str) -> Iterable[Path]:
    """Yield source files deterministically while excluding build outputs."""
    for path in sorted(root.rglob(f"*{suffix}")):
        parts = set(path.parts)
        if parts.intersection({"target", "build", ".gradle", ".git", ".codegraph"}):
            continue
        yield path


def line_number(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def braced_body(text: str, start: int) -> str:
    """Return the first balanced braced body at or after start."""
    brace = text.find("{", start)
    if brace < 0:
        return ""
    depth = 0
    in_string = False
    escaped = False
    for index in range(brace, len(text)):
        char = text[index]
        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            continue
        if char == '"':
            in_string = True
        elif char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return text[brace:index + 1]
    return text[brace:]


def relative(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def extract_java_tests(java_root: Path) -> list[TestItem]:
    tests: list[TestItem] = []
    for path in source_files(java_root, ".java"):
        text = path.read_text(encoding="utf-8", errors="replace")
        annotations = list(JAVA_TEST_ANNOTATION.finditer(text))
        for index, annotation in enumerate(annotations):
            search_end = annotations[index + 1].start() if index + 1 < len(annotations) else len(text)
            method = JAVA_METHOD.search(text, annotation.end(), min(search_end, annotation.end() + 1600))
            if method is None:
                tests.append(
                    TestItem(
                        language="java",
                        file=relative(path, java_root),
                        line=line_number(text, annotation.start()),
                        name="<dynamic-or-unparsed>",
                        kind=annotation.group("kind"),
                        signals=["test annotation found but method signature was not parsed"],
                    )
                )
                continue
            signals: list[str] = []
            if annotation.group("kind") in {"ParameterizedTest", "RepeatedTest", "TestFactory", "TestTemplate"}:
                signals.append("expand distinct generated/parameterized cases in the parity ledger")
            tests.append(
                TestItem(
                    language="java",
                    file=relative(path, java_root),
                    line=line_number(text, annotation.start()),
                    name=method.group("name"),
                    kind=annotation.group("kind"),
                    signals=signals,
                )
            )
    return tests


def rust_signals(name: str, body: str) -> list[str]:
    signals: list[str] = []
    for pattern, explanation in REVIEW_NAME_PATTERNS:
        if pattern.search(name):
            signals.append(explanation)
    for pattern, explanation in IGNORED_RESULT_PATTERNS:
        if pattern.search(body):
            signals.append(explanation)
    for pattern, explanation in WEAK_ASSERTION_PATTERNS:
        matches = pattern.findall(body)
        strong_assertions = len(re.findall(r"assert_(?:eq|ne|matches)!\s*\(", body))
        if matches and strong_assertions == 0:
            signals.append(explanation)

    has_assertion = bool(
        re.search(
            r"\bassert(?:_eq|_ne|_matches)?!\s*\(|"
            r"\bmatches!\s*\(|"
            r"\.(?:expect|expect_err|unwrap_err)\s*\(",
            body,
        )
    )
    should_panic = "#[should_panic" in body
    if not has_assertion and not should_panic:
        signals.append("no obvious observable assertion")

    if "cache" in name.lower() and not re.search(
        r"\b(?:hit|miss|evict|invalidate|load_count|call_count|execution_count|metric)",
        body,
        re.I,
    ):
        signals.append("cache-named test has no obvious cache observation")
    return list(dict.fromkeys(signals))


def extract_rust_tests(rust_root: Path) -> list[TestItem]:
    tests: list[TestItem] = []
    for path in source_files(rust_root, ".rs"):
        text = path.read_text(encoding="utf-8", errors="replace")
        attributes = list(RUST_TEST_ATTRIBUTE.finditer(text))
        for index, attribute in enumerate(attributes):
            search_end = attributes[index + 1].start() if index + 1 < len(attributes) else len(text)
            function = RUST_FUNCTION.search(text, attribute.end(), min(search_end, attribute.end() + 1600))
            if function is None:
                tests.append(
                    TestItem(
                        language="rust",
                        file=relative(path, rust_root),
                        line=line_number(text, attribute.start()),
                        name="<unparsed>",
                        kind=attribute.group("kind"),
                        signals=["test attribute found but function signature was not parsed"],
                    )
                )
                continue
            body = braced_body(text, function.end())
            combined = text[attribute.start():function.end()] + body
            tests.append(
                TestItem(
                    language="rust",
                    file=relative(path, rust_root),
                    line=line_number(text, attribute.start()),
                    name=function.group("name"),
                    kind=attribute.group("kind"),
                    signals=rust_signals(function.group("name"), combined),
                )
            )
    return tests


def parse_object_ledger(path: Path) -> ObjectLedgerSummary:
    """Read current object facts while deliberately ignoring historical status claims."""
    text = path.read_text(encoding="utf-8")
    current = text.split(HISTORY_APPENDIX_START, 1)[0]
    section_match = OBJECT_SECTION.search(current)
    if section_match is not None:
        section_start = section_match.end()
        next_heading = NEXT_H2.search(current, section_start)
        current = current[section_start:next_heading.start() if next_heading else None]
    else:
        # Avoid counting the status-definition legend as real object rows.
        current = re.sub(
            r"^##\s+.*状态图例.*?(?=^##\s+|\Z)",
            "",
            current,
            flags=re.MULTILINE | re.DOTALL,
        )

    counts = {state: 0 for state in OBJECT_STATES}
    rows_scanned = 0
    for line in current.splitlines():
        stripped = line.strip()
        if not stripped.startswith("|") or re.fullmatch(r"[|:\-\s]+", stripped):
            continue
        match = OBJECT_STATE.search(stripped)
        if match is None:
            continue
        counts[match.group(1)] += 1
        rows_scanned += 1
    return ObjectLedgerSummary(
        path=str(path),
        current_fact_only=True,
        rows_scanned=rows_scanned,
        state_counts=counts,
    )


def markdown(
    java_root: Path,
    rust_root: Path,
    java: list[TestItem],
    rust: list[TestItem],
    ledger: ObjectLedgerSummary | None,
) -> str:
    rust_review = [item for item in rust if item.signals]
    parameterized = [item for item in java if item.signals]
    lines = [
        "# Java-to-Rust Migration Test Inventory",
        "",
        f"- Java root: `{java_root}`",
        f"- Rust root: `{rust_root}`",
        f"- Java test methods/annotations found: **{len(java)}**",
        f"- Rust test functions found: **{len(rust)}**",
        f"- Java parameterized/dynamic rows needing case expansion: **{len(parameterized)}**",
        f"- Rust manual-review candidates: **{len(rust_review)}**",
    ]
    if ledger is not None:
        lines.extend(
            [
                f"- Object ledger: `{ledger.path}`",
                f"- Current object rows scanned: **{ledger.rows_scanned}**",
                f"- Strict incomplete rows: **{ledger.incomplete_count}**",
                f"- Migration completion blocked: **{str(ledger.migration_completion_blocked).lower()}**",
            ]
        )
    lines.extend(
        [
        "",
        "> Counts and signals are static heuristics. Do not infer name-based parity,",
        "> semantic equivalence, coverage quality, or deletion decisions from this report.",
        "> Green tests never override MISSING, MISPLACED, STUB, PARTIAL, or UNVERIFIED object rows.",
        "",
        "## Java source-test inventory",
        "",
        "| Location | Annotation | Test | Ledger action |",
        "|---|---|---|---|",
        ]
    )
    for item in java:
        action = "; ".join(item.signals) if item.signals else "map inputs, assertions, effects, and cleanup"
        lines.append(f"| `{item.location}` | `{item.kind}` | `{item.name}` | {action} |")
    if not java:
        lines.append("| — | — | — | no Java tests detected; verify source/test roots and runner |")

    lines.extend(
        [
            "",
            "## Rust test inventory",
            "",
            "| Location | Attribute | Test | Review signals |",
            "|---|---|---|---|",
        ]
    )
    for item in rust:
        signals = "; ".join(item.signals) if item.signals else "none from static heuristic"
        lines.append(f"| `{item.location}` | `{item.kind}` | `{item.name}` | {signals} |")
    if not rust:
        lines.append("| — | — | — | no Rust tests detected; verify crate/test roots |")

    lines.extend(
        [
            "",
            "## Required manual work",
            "",
            "1. Create one SOURCE_PARITY row per Java test and distinct parameterized/dynamic case.",
            "2. Trace production call paths and map inputs, assertions, errors, side effects, and cleanup.",
            "3. Mark MIRRORED, ADAPTED, SPLIT, MERGED_APPROVED, NOT_APPLICABLE, BLOCKED, or MISSING.",
            "4. Add applicable Rust ownership, async, error, serialization, feature, macro, adapter, and unsafe obligations.",
            "5. Review each signal against source contracts and plausible mutants; never auto-delete.",
            "",
        ]
    )
    if ledger is not None:
        lines.extend(
            [
                "## Object-ledger completion firewall",
                "",
                "| State | Current rows | Completion effect |",
                "|---|---:|---|",
            ]
        )
        for state in OBJECT_STATES:
            effect = "blocks completion" if state in INCOMPLETE_STATES else "handled/outside denominator"
            lines.append(f"| `{state}` | {ledger.state_counts[state]} | {effect} |")
        lines.extend(
            [
                "",
                (
                    "**Conclusion: migration incomplete regardless of test results.**"
                    if ledger.migration_completion_blocked
                    else "**No strict object blocker was detected in the supplied current ledger region.**"
                ),
                "",
            ]
        )
    return "\n".join(lines)


def json_report(
    java_root: Path,
    rust_root: Path,
    java: list[TestItem],
    rust: list[TestItem],
    ledger: ObjectLedgerSummary | None,
) -> str:
    payload = {
        "java_root": str(java_root),
        "rust_root": str(rust_root),
        "summary": {
            "java_tests": len(java),
            "rust_tests": len(rust),
            "java_case_expansion_candidates": sum(bool(item.signals) for item in java),
            "rust_review_candidates": sum(bool(item.signals) for item in rust),
        },
        "java_tests": [asdict(item) for item in java],
        "rust_tests": [asdict(item) for item in rust],
        "object_ledger": (
            {
                **asdict(ledger),
                "incomplete_count": ledger.incomplete_count,
                "migration_completion_blocked": ledger.migration_completion_blocked,
            }
            if ledger is not None
            else None
        ),
        "limitations": [
            "static inventory only",
            "does not map tests by name",
            "does not prove semantic parity or test value",
            "does not authorize deletion",
        ],
    }
    return json.dumps(payload, indent=2, ensure_ascii=False)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Inventory Java/Rust migration tests and flag weak Rust test signals."
    )
    parser.add_argument("--java-root", type=Path, required=True, help="Java module/repository root")
    parser.add_argument("--rust-root", type=Path, required=True, help="Rust crate/workspace root")
    parser.add_argument("--format", choices=("markdown", "json"), default="markdown")
    parser.add_argument("--output", type=Path, help="Optional output path")
    parser.add_argument(
        "--object-ledger",
        type=Path,
        help="Current authoritative 对象级对照表; historical appendix is ignored.",
    )
    parser.add_argument(
        "--fail-on-incomplete",
        action="store_true",
        help="Exit non-zero when the current object ledger contains strict incomplete rows.",
    )
    args = parser.parse_args()

    for label, root in (("java", args.java_root), ("rust", args.rust_root)):
        if not root.exists() or not root.is_dir():
            raise SystemExit(f"{label} root is not a directory: {root}")

    java_tests = extract_java_tests(args.java_root)
    rust_tests = extract_rust_tests(args.rust_root)
    ledger: ObjectLedgerSummary | None = None
    if args.object_ledger is not None:
        if not args.object_ledger.is_file():
            raise SystemExit(f"object ledger is not a file: {args.object_ledger}")
        ledger = parse_object_ledger(args.object_ledger)
    report = (
        json_report(args.java_root, args.rust_root, java_tests, rust_tests, ledger)
        if args.format == "json"
        else markdown(args.java_root, args.rust_root, java_tests, rust_tests, ledger)
    )

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(report + "\n", encoding="utf-8")
        print(f"wrote {args.output}")
    else:
        print(report)
    if args.fail_on_incomplete and ledger is not None and ledger.migration_completion_blocked:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
