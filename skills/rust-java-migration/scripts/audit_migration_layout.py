#!/usr/bin/env python3
"""Detect structural red flags in a Java-to-Rust migration tree."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path


SKIP_PARTS = {
    ".git",
    "target",
    "vendor",
    "generated",
    "tests",
    "examples",
    "benches",
}
WILDCARD_IMPORT = re.compile(r"^\s*(?:pub\s+)?use\s+[^;]*::\*\s*;", re.MULTILINE)
STUB_MACRO = re.compile(r"\b(todo|unimplemented)!\s*\(")
TYPE_DEFINITION = re.compile(
    r"^\s*(?:pub(?:\([^)]*\))?\s+)?(?:unsafe\s+)?"
    r"(?:struct|enum|trait|union)\s+([A-Za-z_][A-Za-z0-9_]*)",
    re.MULTILINE,
)
PUBLIC_ITEM = re.compile(
    r"^\s*pub(?:\([^)]*\))?\s+(?:async\s+)?"
    r"(?:unsafe\s+)?(?:fn|struct|enum|trait|union)\s+([A-Za-z_][A-Za-z0-9_]*)",
    re.MULTILINE,
)
CHINESE = re.compile(r"[\u3400-\u9fff]")


@dataclass(frozen=True)
class Finding:
    severity: str
    rule: str
    path: str
    line: int
    message: str
    allowed: bool = False


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Audit Rust migration layout without claiming semantic parity."
    )
    parser.add_argument("--rust-root", required=True, type=Path, help="Rust project root.")
    parser.add_argument(
        "--allow-stubs-in",
        action="append",
        default=[],
        metavar="RELATIVE_PATH",
        help="Approved blocked subtree; stub findings remain visible but allowed.",
    )
    parser.add_argument(
        "--require-source-comments",
        action="store_true",
        help="Warn when public items lack nearby Chinese '对应 Java' comments.",
    )
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of text.")
    parser.add_argument(
        "--summary-only",
        action="store_true",
        help="Emit counts without individual findings.",
    )
    parser.add_argument(
        "--fail-on-warning",
        action="store_true",
        help="Return failure when non-allowed warnings exist.",
    )
    return parser.parse_args()


def line_number(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def is_allowed(relative: Path, allowed_roots: tuple[Path, ...]) -> bool:
    return any(relative == root or root in relative.parents for root in allowed_roots)


def rust_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for path in root.rglob("*.rs"):
        relative = path.relative_to(root)
        if any(part in SKIP_PARTS for part in relative.parts):
            continue
        if path.name == "tests.rs" or path.stem.endswith(("_test", "_tests")):
            continue
        if "src" not in relative.parts and root.name != "src":
            continue
        files.append(path)
    return sorted(files)


def preceding_comment(text: str, offset: int, lines: int = 10) -> str:
    prefix = text[:offset].splitlines()
    return "\n".join(prefix[-lines:])


def audit_file(
    root: Path,
    path: Path,
    allowed_roots: tuple[Path, ...],
    require_source_comments: bool,
) -> list[Finding]:
    findings: list[Finding] = []
    relative = path.relative_to(root)
    relative_text = relative.as_posix()
    text = path.read_text(encoding="utf-8")
    production_text = text.split("#[cfg(test)]", 1)[0]
    allowed_stub = is_allowed(relative, allowed_roots)

    for match in WILDCARD_IMPORT.finditer(production_text):
        findings.append(
            Finding(
                "error",
                "wildcard_import",
                relative_text,
                line_number(text, match.start()),
                "production migration code must not use wildcard imports",
            )
        )

    for match in STUB_MACRO.finditer(production_text):
        findings.append(
            Finding(
                "warning" if allowed_stub else "error",
                "stub_macro",
                relative_text,
                line_number(text, match.start()),
                f"{match.group(1)}! is incomplete migration behavior",
                allowed=allowed_stub,
            )
        )

    if path.name in {"lib.rs", "mod.rs", "compat.rs"}:
        for match in TYPE_DEFINITION.finditer(production_text):
            severity = "warning" if path.name == "compat.rs" else "error"
            findings.append(
                Finding(
                    severity,
                    "type_in_facade_file",
                    relative_text,
                    line_number(text, match.start()),
                    f"{match.group(1)} is defined in {path.name}; move migrated objects "
                    "to one-object files or document a narrow facade exception",
                )
            )

    if require_source_comments:
        for match in PUBLIC_ITEM.finditer(production_text):
            context = preceding_comment(text, match.start())
            if "对应 Java" not in context or not CHINESE.search(context):
                findings.append(
                    Finding(
                        "warning",
                        "missing_java_source_comment",
                        relative_text,
                        line_number(text, match.start()),
                        f"public item {match.group(1)} lacks a nearby Chinese "
                        "'对应 Java' source comment",
                    )
                )

    return findings


def main() -> int:
    args = parse_args()
    root = args.rust_root.expanduser().resolve()
    if not root.is_dir():
        print(f"error: Rust root is not a directory: {root}", file=sys.stderr)
        return 2

    allowed_roots = tuple(Path(value) for value in args.allow_stubs_in)
    for allowed in allowed_roots:
        if allowed.is_absolute() or ".." in allowed.parts:
            print(
                f"error: --allow-stubs-in must be a safe relative path: {allowed}",
                file=sys.stderr,
            )
            return 2

    files = rust_files(root)
    findings: list[Finding] = []
    for path in files:
        try:
            findings.extend(
                audit_file(root, path, allowed_roots, args.require_source_comments)
            )
        except UnicodeDecodeError:
            findings.append(
                Finding(
                    "error",
                    "invalid_utf8",
                    path.relative_to(root).as_posix(),
                    1,
                    "Rust source is not valid UTF-8",
                )
            )

    errors = [item for item in findings if item.severity == "error" and not item.allowed]
    warnings = [
        item for item in findings if item.severity == "warning" and not item.allowed
    ]
    summary = {
        "root": str(root),
        "files_scanned": len(files),
        "errors": len(errors),
        "warnings": len(warnings),
        "allowed_findings": sum(item.allowed for item in findings),
        "semantic_parity_proven": False,
    }
    if not args.summary_only:
        summary["findings"] = [asdict(item) for item in findings]

    if args.json:
        print(json.dumps(summary, ensure_ascii=False, indent=2))
    else:
        print(
            f"scanned={len(files)} errors={len(errors)} warnings={len(warnings)} "
            f"allowed={summary['allowed_findings']} semantic_parity_proven=false"
        )
        if not args.summary_only:
            for item in findings:
                marker = "allowed" if item.allowed else item.severity
                print(f"{marker}: {item.path}:{item.line}: {item.rule}: {item.message}")

    if errors or (args.fail_on_warning and warnings):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
