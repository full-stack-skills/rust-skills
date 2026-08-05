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
BUILD_OUTPUT_PARTS = {".git", "target", "vendor", "generated"}
SOFT_RUST_FILE_LINES = 500
HARD_RUST_FILE_LINES = 800
WILDCARD_IMPORT = re.compile(r"^\s*(?:pub\s+)?use\s+[^;]*::\*\s*;", re.MULTILINE)
STUB_MACRO = re.compile(r"\b(todo|unimplemented)!\s*\(")
STUB_PANIC = re.compile(
    r"\bpanic!\s*\(\s*\"[^\"]*(?:not implemented|todo|placeholder)[^\"]*\"",
    re.IGNORECASE,
)
EMPTY_FUNCTION = re.compile(
    r"\bfn\s+[A-Za-z_][A-Za-z0-9_]*\s*(?:<[^{};]*>)?\s*"
    r"\([^{};]*\)\s*(?:->\s*[^{};]+)?\{\s*\}",
    re.MULTILINE,
)
SNAKE_CASE = re.compile(r"^[a-z][a-z0-9]*(?:_[a-z0-9]+)*$")
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
PUBLIC_TYPE_DEFINITION = re.compile(
    r"^\s*pub(?:\([^)]*\))?\s+(?:unsafe\s+)?"
    r"(?:struct|enum|trait|union)\s+([A-Za-z_][A-Za-z0-9_]*)",
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
        "--java-package-root",
        type=Path,
        help="Java module package root used to calculate deterministic expected paths.",
    )
    parser.add_argument(
        "--retain-segments",
        type=int,
        default=2,
        choices=(1, 2),
        help="Trailing Java package segments retained under Rust src (default: 2).",
    )
    parser.add_argument(
        "--allow-stubs-in",
        action="append",
        default=[],
        metavar="RELATIVE_PATH",
        help=(
            "Acknowledge a blocked planning subtree. Stub findings remain migration "
            "blockers and never count as completion."
        ),
    )
    parser.add_argument(
        "--require-source-comments",
        action="store_true",
        help="Warn when public items lack nearby Chinese '对应 Java' comments.",
    )
    parser.add_argument(
        "--reviewed-large-file",
        action="append",
        default=[],
        metavar="RELATIVE_PATH",
        help=(
            "Acknowledge a 501-800-line file or subtree after a recorded cohesion "
            "review; repeat as needed. Files above 800 lines cannot be acknowledged."
        ),
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


def all_rust_files(root: Path) -> list[Path]:
    """Return authored Rust files, including tests, examples, and benches."""
    return sorted(
        path
        for path in root.rglob("*.rs")
        if not set(path.relative_to(root).parts).intersection(BUILD_OUTPUT_PARTS)
    )


def audit_global_file_constraints(
    root: Path,
    path: Path,
    reviewed_large_files: tuple[Path, ...],
) -> list[Finding]:
    """Apply review and blocking thresholds to authored Rust files."""
    relative = path.relative_to(root)
    relative_text = relative.as_posix()
    text = path.read_text(encoding="utf-8")
    findings: list[Finding] = []
    line_count = len(text.splitlines())
    if line_count > HARD_RUST_FILE_LINES:
        findings.append(
            Finding(
                "error",
                "rust_file_over_800_lines",
                relative_text,
                HARD_RUST_FILE_LINES + 1,
                f"Rust source has {line_count} lines; files above 800 lines block completion",
            )
        )
    elif line_count > SOFT_RUST_FILE_LINES:
        findings.append(
            Finding(
                "warning",
                "rust_file_over_500_lines",
                relative_text,
                SOFT_RUST_FILE_LINES + 1,
                (
                    f"Rust source has {line_count} lines; review cohesion and split by "
                    "responsibility when the file mixes concerns"
                ),
                allowed=is_allowed(relative, reviewed_large_files),
            )
        )
    return findings


def java_object_files(root: Path) -> list[Path]:
    """Return source object files; package metadata is not an object."""
    files: list[Path] = []
    for path in root.rglob("*.java"):
        relative = path.relative_to(root)
        if any(part in SKIP_PARTS or part in {"build", "out"} for part in relative.parts):
            continue
        if path.name in {"package-info.java", "module-info.java"}:
            continue
        files.append(path)
    return sorted(files)


def camel_to_snake(name: str) -> str:
    """Convert Java object names, including acronym boundaries, to snake_case."""
    step_one = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", step_one).replace("-", "_").lower()


def expected_rust_path(
    java_package_root: Path,
    java_file: Path,
    rust_root: Path,
    retain_segments: int,
) -> Path:
    """Calculate the one-object Rust path from trailing Java package segments."""
    package_parts = java_file.parent.relative_to(java_package_root).parts
    retained = package_parts[-retain_segments:]
    source_prefix: tuple[str, ...] = () if rust_root.name == "src" else ("src",)
    return Path(*source_prefix, *retained, f"{camel_to_snake(java_file.stem)}.rs")


def preceding_comment(text: str, offset: int) -> str:
    """Return the complete contiguous Rust doc/attribute block before an item."""
    collected: list[str] = []
    for line in reversed(text[:offset].splitlines()):
        stripped = line.strip()
        if not stripped or stripped.startswith(("///", "//!", "#[")):
            collected.append(line)
            continue
        break
    return "\n".join(reversed(collected))


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

    source_relative = relative
    if "src" in relative.parts:
        source_relative = Path(*relative.parts[relative.parts.index("src") + 1 :])
    for segment in source_relative.parts[:-1]:
        if not SNAKE_CASE.fullmatch(segment):
            findings.append(
                Finding(
                    "error",
                    "non_snake_case_directory",
                    relative_text,
                    1,
                    f"production Rust directory is not snake_case: {segment}",
                )
            )
    if path.stem not in {"lib", "mod"} and not SNAKE_CASE.fullmatch(path.stem):
        findings.append(
            Finding(
                "error",
                "non_snake_case_file",
                relative_text,
                1,
                f"production Rust file is not snake_case: {path.name}",
            )
        )

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

    for pattern, message in (
        (STUB_PANIC, "placeholder panic is incomplete migration behavior"),
        (EMPTY_FUNCTION, "empty function body requires source-backed no-op evidence"),
    ):
        for match in pattern.finditer(production_text):
            findings.append(
                Finding(
                    "warning" if allowed_stub else "error",
                    "stub_logic",
                    relative_text,
                    line_number(text, match.start()),
                    message,
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

    public_types = [match.group(1) for match in PUBLIC_TYPE_DEFINITION.finditer(production_text)]
    primary_types = [
        name
        for name in public_types
        if not (
            name.endswith("Builder")
            and name.removesuffix("Builder") in public_types
        )
    ]
    if path.name not in {"lib.rs", "mod.rs", "compat.rs"} and len(primary_types) > 1:
        findings.append(
            Finding(
                "error",
                "multiple_public_objects",
                relative_text,
                1,
                "one Rust file exposes multiple primary migrated objects: "
                + ", ".join(primary_types),
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
                        f"public item {match.group(1)} lacks an immediately preceding "
                        "Chinese '对应 Java' source doc block",
                    )
                )

    return findings


def main() -> int:
    args = parse_args()
    root = args.rust_root.expanduser().resolve()
    if not root.is_dir():
        print(f"error: Rust root is not a directory: {root}", file=sys.stderr)
        return 2

    java_package_root: Path | None = None
    if args.java_package_root is not None:
        java_package_root = args.java_package_root.expanduser().resolve()
        if not java_package_root.is_dir():
            print(
                f"error: Java package root is not a directory: {java_package_root}",
                file=sys.stderr,
            )
            return 2

    allowed_roots = tuple(Path(value) for value in args.allow_stubs_in)
    reviewed_large_files = tuple(Path(value) for value in args.reviewed_large_file)
    for option, values in (
        ("--allow-stubs-in", allowed_roots),
        ("--reviewed-large-file", reviewed_large_files),
    ):
        for allowed in values:
            if not allowed.is_absolute() and ".." not in allowed.parts:
                continue
            print(
                f"error: {option} must be a safe relative path: {allowed}",
                file=sys.stderr,
            )
            return 2

    authored_files = all_rust_files(root)
    files = rust_files(root)
    findings: list[Finding] = []
    for path in authored_files:
        try:
            findings.extend(
                audit_global_file_constraints(root, path, reviewed_large_files)
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

    java_files: list[Path] = []
    if java_package_root is not None:
        java_files = java_object_files(java_package_root)
        rust_paths = {path.relative_to(root) for path in files}
        rust_paths_by_name: dict[str, list[Path]] = {}
        for relative in rust_paths:
            rust_paths_by_name.setdefault(relative.name, []).append(relative)
        for java_file in java_files:
            expected = expected_rust_path(
                java_package_root,
                java_file,
                root,
                args.retain_segments,
            )
            if expected in rust_paths:
                continue
            current_paths = rust_paths_by_name.get(expected.name, [])
            java_relative = java_file.relative_to(java_package_root).as_posix()
            if current_paths:
                findings.append(
                    Finding(
                        "error",
                        "misplaced_object_file",
                        java_relative,
                        1,
                        f"expected {expected.as_posix()}, found same-name file at "
                        + ", ".join(path.as_posix() for path in sorted(current_paths)),
                    )
                )
            else:
                findings.append(
                    Finding(
                        "error",
                        "missing_object_file",
                        java_relative,
                        1,
                        f"expected Rust object file {expected.as_posix()}",
                    )
                )

    errors = [item for item in findings if item.severity == "error" and not item.allowed]
    warnings = [
        item for item in findings if item.severity == "warning" and not item.allowed
    ]
    strict_blocker_rules = {
        "stub_macro",
        "stub_logic",
        "missing_object_file",
        "misplaced_object_file",
        "multiple_public_objects",
        "type_in_facade_file",
        "wildcard_import",
        "non_snake_case_directory",
        "non_snake_case_file",
        "rust_file_over_800_lines",
    }
    strict_blockers = [item for item in findings if item.rule in strict_blocker_rules]
    summary = {
        "root": str(root),
        "files_scanned": len(authored_files),
        "java_package_root": str(java_package_root) if java_package_root else None,
        "java_objects_scanned": len(java_files),
        "retain_segments": args.retain_segments,
        "errors": len(errors),
        "warnings": len(warnings),
        "allowed_findings": sum(item.allowed for item in findings),
        "strict_migration_blockers": len(strict_blockers),
        "migration_completion_blocked": bool(strict_blockers),
        "semantic_parity_proven": False,
    }
    if not args.summary_only:
        summary["findings"] = [asdict(item) for item in findings]

    if args.json:
        print(json.dumps(summary, ensure_ascii=False, indent=2))
    else:
        print(
            f"scanned={len(authored_files)} errors={len(errors)} warnings={len(warnings)} "
            f"acknowledged={summary['allowed_findings']} "
            f"strict_blockers={len(strict_blockers)} "
            f"migration_completion_blocked={str(bool(strict_blockers)).lower()} "
            "semantic_parity_proven=false"
        )
        if not args.summary_only:
            for item in findings:
                marker = "allowed" if item.allowed else item.severity
                print(f"{marker}: {item.path}:{item.line}: {item.rule}: {item.message}")

    if errors or strict_blockers or (args.fail_on_warning and warnings):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
