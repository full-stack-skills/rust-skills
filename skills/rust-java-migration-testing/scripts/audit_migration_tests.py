#!/usr/bin/env python3
"""Audit Java/Rust migration tests, exact source assets, and differential evidence.

The report is intentionally conservative:

* it does not map Java tests to Rust tests by name;
* it validates recorded preservation and differential evidence but cannot infer it;
* it never authorizes deletion;
* it keeps parameterized/dynamic annotations visible for manual case expansion.

Use the inventory to populate the SOURCE_PARITY, RUST_OBLIGATION, and
VALUE_ADD ledgers described by the rust-java-migration-testing skill.
"""

from __future__ import annotations

import argparse
import fnmatch
import hashlib
import json
import re
import tomllib
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
COMPLETED_TEST_DISPOSITIONS = {
    "MIRRORED",
    "ADAPTED",
    "SPLIT",
    "MERGED_APPROVED",
}
INCOMPLETE_TEST_DISPOSITIONS = {"NOT_APPLICABLE", "BLOCKED", "MISSING"}
PRESERVATION_FIELDS = (
    "contract_preserved",
    "inputs_preserved",
    "assertions_preserved",
    "fixture_state_preserved",
    "cleanup_preserved",
)
DEFAULT_TEST_ASSET_MARKERS = (
    ("src", "test", "resources"),
    ("test", "resources"),
    ("tests", "resources"),
)
SOFT_RUST_FILE_LINES = 500
HARD_RUST_FILE_LINES = 800


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


@dataclass
class SourceParitySummary:
    path: str | None
    java_tests: int
    mapped_java_tests: int
    manifest_cases: int
    java_assets: int
    verified_exact_assets: int
    acceptance_module: str | None = None
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def migration_completion_blocked(self) -> bool:
        return bool(self.errors)


def source_files(root: Path, suffix: str) -> Iterable[Path]:
    """Yield source files deterministically while excluding build outputs."""
    for path in sorted(root.rglob(f"*{suffix}")):
        parts = set(path.parts)
        if parts.intersection(
            {"target", "build", "vendor", "generated", ".gradle", ".git", ".codegraph"}
        ):
            continue
        yield path


def rust_layout_errors(rust_root: Path) -> list[str]:
    """Return hard authored-file size violations."""
    errors: list[str] = []
    for path in source_files(rust_root, ".rs"):
        text = path.read_text(encoding="utf-8", errors="replace")
        location = relative(path, rust_root)
        line_count = len(text.splitlines())
        if line_count > HARD_RUST_FILE_LINES:
            errors.append(
                f"{location}: Rust source has {line_count} lines; hard maximum is 800"
            )
    return errors


def rust_layout_warnings(rust_root: Path) -> list[str]:
    """Return files that need a cohesion review before completion."""
    warnings: list[str] = []
    for path in source_files(rust_root, ".rs"):
        text = path.read_text(encoding="utf-8", errors="replace")
        line_count = len(text.splitlines())
        if SOFT_RUST_FILE_LINES < line_count <= HARD_RUST_FILE_LINES:
            warnings.append(
                f"{relative(path, rust_root)}: Rust source has {line_count} lines; "
                "review cohesion and split only when responsibilities are mixed"
            )
    return warnings


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def path_contains_sequence(path: Path, sequence: tuple[str, ...]) -> bool:
    parts = path.parts
    width = len(sequence)
    return any(parts[index:index + width] == sequence for index in range(len(parts) - width + 1))


def discover_java_test_assets(java_root: Path, extra_roots: list[Path]) -> list[Path]:
    assets: set[Path] = set()
    for path in sorted(java_root.rglob("*")):
        if not path.is_file():
            continue
        relative_path = path.relative_to(java_root)
        if set(relative_path.parts).intersection({"target", "build", ".gradle", ".git", ".codegraph"}):
            continue
        if any(path_contains_sequence(relative_path, marker) for marker in DEFAULT_TEST_ASSET_MARKERS):
            assets.add(path)
    for root in extra_roots:
        resolved = root if root.is_absolute() else java_root / root
        resolved = resolved.resolve()
        try:
            resolved.relative_to(java_root.resolve())
        except ValueError as error:
            raise ValueError(f"test asset root escapes Java root: {root}") from error
        if not resolved.is_dir():
            raise ValueError(f"test asset root is not a directory: {root}")
        for path in resolved.rglob("*"):
            if path.is_file():
                assets.add(path)
    return sorted(assets)


def source_test_key(item: TestItem, duplicate_keys: set[str] | None = None) -> str:
    base = f"{item.file}#{item.name}"
    if duplicate_keys and base in duplicate_keys:
        return f"{item.file}:{item.line}#{item.name}"
    return base


def target_file_from_anchor(anchor: str, rust_root: Path) -> Path:
    relative_path = anchor.split("#", 1)[0]
    try:
        return manifest_file(rust_root, relative_path)
    except ValueError as error:
        raise ValueError(f"unsafe target anchor path: {anchor}") from error


def manifest_file(root: Path, relative_path: str) -> Path:
    path = Path(relative_path)
    if path.is_absolute() or ".." in path.parts:
        raise ValueError(f"unsafe manifest path: {relative_path}")
    resolved_root = root.resolve()
    candidate = (resolved_root / path).resolve()
    try:
        candidate.relative_to(resolved_root)
    except ValueError as error:
        raise ValueError(f"manifest path escapes root: {relative_path}") from error
    return candidate


def require_boolean(record: dict[str, object], field_name: str, label: str, errors: list[str]) -> None:
    if record.get(field_name) is not True:
        errors.append(f"{label}: `{field_name}` must be true")


def validate_run_record(
    run: object,
    label: str,
    manifest_path: Path,
    errors: list[str],
) -> dict[str, object] | None:
    if not isinstance(run, dict):
        errors.append(f"{label} is required")
        return None
    for field_name in ("command", "artifact"):
        if not isinstance(run.get(field_name), str) or not run[field_name].strip():
            errors.append(f"{label}.`{field_name}` is required")
    artifact = run.get("artifact")
    if isinstance(artifact, str) and artifact.strip():
        try:
            artifact_path = manifest_file(manifest_path.parent, artifact)
        except ValueError as error:
            errors.append(f"{label}: {error}")
        else:
            if not artifact_path.is_file():
                errors.append(f"{label}: artifact does not exist: {artifact_path}")
    if run.get("status") != "PASS":
        errors.append(f"{label}.`status` must be `PASS`")
    for field_name in ("failed", "skipped", "not_run"):
        if run.get(field_name) != 0:
            errors.append(f"{label}.`{field_name}` must equal 0")
    return run


def validate_acceptance_module(
    raw_module: object,
    manifest_path: Path,
    rust_root: Path,
    errors: list[str],
) -> str | None:
    label = "acceptance_module"
    if not isinstance(raw_module, dict):
        errors.append(f"{label} is required")
        return None
    package = raw_module.get("package")
    if not isinstance(package, str) or not package:
        errors.append(f"{label}.`package` is required")
        package = None
    elif not package.endswith("-test"):
        errors.append(f"{label}.`package` must use the singular `<project>-test` suffix")
    manifest = raw_module.get("manifest")
    cargo_manifest: Path | None = None
    if not isinstance(manifest, str) or not manifest:
        errors.append(f"{label}.`manifest` is required")
    else:
        try:
            cargo_manifest = manifest_file(rust_root, manifest)
        except ValueError as error:
            errors.append(f"{label}: {error}")
        else:
            if not cargo_manifest.is_file():
                errors.append(f"{label}: Cargo manifest does not exist: {cargo_manifest}")
                cargo_manifest = None
    if raw_module.get("publish") is not False:
        errors.append(f"{label}.`publish` must be false")
    components = raw_module.get("components")
    if not isinstance(components, list) or not components or not all(
        isinstance(component, str) and component for component in components
    ):
        errors.append(f"{label}.`components` must be a non-empty string list")
    validate_run_record(raw_module, label, manifest_path, errors)
    command = raw_module.get("command")
    if isinstance(package, str) and isinstance(command, str):
        selector = re.compile(
            rf"(?:^|\s)(?:-p|--package)(?:\s+|=){re.escape(package)}(?:\s|$)"
        )
        if selector.search(command) is None:
            errors.append(f"{label}.`command` must explicitly select package `{package}`")

    if cargo_manifest is not None:
        try:
            cargo_payload = tomllib.loads(cargo_manifest.read_text(encoding="utf-8"))
        except (OSError, tomllib.TOMLDecodeError) as error:
            errors.append(f"{label}: cannot parse Cargo manifest: {error}")
        else:
            cargo_package = cargo_payload.get("package", {})
            if cargo_package.get("name") != package:
                errors.append(
                    f"{label}: Cargo package name `{cargo_package.get('name')}` does not match `{package}`"
                )
            if cargo_package.get("publish") is not False:
                errors.append(f"{label}: Cargo package must set `publish = false`")

        workspace_manifest = rust_root / "Cargo.toml"
        if not workspace_manifest.is_file():
            errors.append(f"{label}: Rust workspace Cargo.toml does not exist: {workspace_manifest}")
        else:
            try:
                workspace_payload = tomllib.loads(workspace_manifest.read_text(encoding="utf-8"))
                members = workspace_payload.get("workspace", {}).get("members", [])
                module_dir = cargo_manifest.parent.relative_to(rust_root.resolve()).as_posix()
            except (OSError, ValueError, tomllib.TOMLDecodeError) as error:
                errors.append(f"{label}: cannot inspect workspace membership: {error}")
            else:
                if isinstance(package, str) and cargo_manifest.parent.name != package:
                    errors.append(
                        f"{label}: module directory `{cargo_manifest.parent.name}` must match `{package}`"
                    )
                if not isinstance(members, list) or not any(
                    isinstance(member, str) and fnmatch.fnmatch(module_dir, member)
                    for member in members
                ):
                    errors.append(f"{label}: `{module_dir}` is not a Rust workspace member")
    return package


def validate_source_parity_manifest(
    manifest_path: Path | None,
    java_root: Path,
    rust_root: Path,
    java_tests: list[TestItem],
    java_assets: list[Path],
) -> SourceParitySummary:
    summary = SourceParitySummary(
        path=str(manifest_path) if manifest_path else None,
        java_tests=len(java_tests),
        mapped_java_tests=0,
        manifest_cases=0,
        java_assets=len(java_assets),
        verified_exact_assets=0,
    )
    if manifest_path is None:
        summary.errors.append("source parity manifest is required for a completion gate")
        return summary
    if not manifest_path.is_file():
        summary.errors.append(f"source parity manifest does not exist: {manifest_path}")
        return summary
    try:
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        summary.errors.append(f"cannot read source parity manifest: {error}")
        return summary
    if payload.get("schema") != 1:
        summary.errors.append("source parity manifest `schema` must equal 1")
    for baseline in ("java_baseline", "rust_baseline"):
        if not isinstance(payload.get(baseline), str) or not payload[baseline].strip():
            summary.errors.append(f"source parity manifest `{baseline}` is required")

    summary.acceptance_module = validate_acceptance_module(
        payload.get("acceptance_module"),
        manifest_path,
        rust_root,
        summary.errors,
    )

    records = payload.get("source_tests")
    if not isinstance(records, list):
        summary.errors.append("source parity manifest `source_tests` must be a list")
        records = []
    records_by_source: dict[str, list[dict[str, object]]] = {}
    for index, raw_record in enumerate(records):
        label = f"source_tests[{index}]"
        if not isinstance(raw_record, dict):
            summary.errors.append(f"{label}: record must be an object")
            continue
        source = raw_record.get("source")
        if not isinstance(source, str) or not source:
            summary.errors.append(f"{label}: `source` is required")
            continue
        records_by_source.setdefault(source, []).append(raw_record)
        summary.manifest_cases += 1

    base_keys = [source_test_key(item) for item in java_tests]
    duplicate_keys = {key for key in base_keys if base_keys.count(key) > 1}
    extracted_keys = {source_test_key(item, duplicate_keys) for item in java_tests}
    stale_sources = sorted(set(records_by_source) - extracted_keys)
    for source in stale_sources:
        summary.errors.append(f"manifest source test was not found in Java baseline: {source}")

    for item in java_tests:
        key = source_test_key(item, duplicate_keys)
        source_records = records_by_source.get(key, [])
        if not source_records:
            summary.errors.append(f"missing source-test mapping: {key}")
            continue
        summary.mapped_java_tests += 1
        case_ids: set[str] = set()
        for index, record in enumerate(source_records):
            label = f"{key}[{index}]"
            disposition = record.get("disposition")
            if disposition not in COMPLETED_TEST_DISPOSITIONS:
                if disposition in INCOMPLETE_TEST_DISPOSITIONS:
                    summary.errors.append(f"{label}: disposition `{disposition}` blocks completion")
                else:
                    summary.errors.append(f"{label}: invalid disposition `{disposition}`")
            targets = record.get("targets")
            if not isinstance(targets, list) or not targets or not all(isinstance(value, str) and value for value in targets):
                summary.errors.append(f"{label}: non-empty string list `targets` is required")
            else:
                for target in targets:
                    try:
                        target_path = target_file_from_anchor(target, rust_root)
                    except ValueError as error:
                        summary.errors.append(f"{label}: {error}")
                        continue
                    if not target_path.is_file():
                        summary.errors.append(f"{label}: Rust target file does not exist: {target_path}")
            for field_name in PRESERVATION_FIELDS:
                require_boolean(record, field_name, label, summary.errors)
            if record.get("result_parity") != "MATCH":
                summary.errors.append(f"{label}: `result_parity` must be `MATCH`")
            evidence = record.get("evidence")
            if not isinstance(evidence, str) or not evidence.strip():
                summary.errors.append(f"{label}: non-empty `evidence` is required")
            else:
                try:
                    evidence_path = manifest_file(manifest_path.parent, evidence)
                except ValueError as error:
                    summary.errors.append(f"{label}: {error}")
                else:
                    if not evidence_path.is_file():
                        summary.errors.append(f"{label}: evidence artifact does not exist: {evidence_path}")
            case_id = record.get("case_id")
            if item.kind in {"ParameterizedTest", "RepeatedTest", "TestFactory", "TestTemplate"}:
                if not isinstance(case_id, str) or not case_id:
                    summary.errors.append(f"{label}: parameterized/dynamic test requires `case_id`")
                elif case_id in case_ids:
                    summary.errors.append(f"{label}: duplicate `case_id` `{case_id}`")
                else:
                    case_ids.add(case_id)
                require_boolean(record, "case_expansion_complete", label, summary.errors)

    asset_records = payload.get("assets")
    if not isinstance(asset_records, list):
        summary.errors.append("source parity manifest `assets` must be a list")
        asset_records = []
    assets_by_source: dict[str, dict[str, object]] = {}
    for index, raw_record in enumerate(asset_records):
        label = f"assets[{index}]"
        if not isinstance(raw_record, dict):
            summary.errors.append(f"{label}: record must be an object")
            continue
        source = raw_record.get("source")
        if not isinstance(source, str) or not source:
            summary.errors.append(f"{label}: `source` is required")
            continue
        if source in assets_by_source:
            summary.errors.append(f"{label}: duplicate source asset `{source}`")
            continue
        assets_by_source[source] = raw_record

    discovered_asset_keys = {relative(path, java_root) for path in java_assets}
    manifest_asset_keys = set(assets_by_source)
    existing_manifest_assets = {
        source
        for source in manifest_asset_keys
        if not Path(source).is_absolute()
        and ".." not in Path(source).parts
        and (java_root / source).is_file()
    }
    summary.java_assets = len(discovered_asset_keys | existing_manifest_assets)
    for source in sorted(discovered_asset_keys - manifest_asset_keys):
        summary.errors.append(f"missing source test asset mapping: {source}")
    for source in sorted(manifest_asset_keys - discovered_asset_keys):
        try:
            source_path = manifest_file(java_root, source)
        except ValueError as error:
            summary.errors.append(str(error))
            continue
        if not source_path.is_file():
            summary.errors.append(f"manifest source asset does not exist: {source}")

    for source, record in assets_by_source.items():
        label = f"asset {source}"
        try:
            source_path = manifest_file(java_root, source)
        except ValueError as error:
            summary.errors.append(f"{label}: {error}")
            continue
        target = record.get("target")
        if not source_path.is_file():
            continue
        if record.get("mode") != "COPY_EXACT":
            summary.errors.append(f"{label}: `mode` must be `COPY_EXACT`")
            continue
        if not isinstance(target, str) or not target:
            summary.errors.append(f"{label}: `target` is required")
            continue
        try:
            target_path = manifest_file(rust_root, target)
        except ValueError as error:
            summary.errors.append(f"{label}: {error}")
            continue
        if not target_path.is_file():
            summary.errors.append(f"{label}: target asset does not exist: {target_path}")
            continue
        source_hash = sha256_file(source_path)
        target_hash = sha256_file(target_path)
        declared_hash = record.get("sha256")
        if declared_hash != source_hash:
            summary.errors.append(f"{label}: declared SHA-256 does not match source ({source_hash})")
            continue
        if source_hash != target_hash:
            summary.errors.append(f"{label}: source/target SHA-256 mismatch")
            continue
        summary.verified_exact_assets += 1

    runs = payload.get("runs")
    if not isinstance(runs, dict):
        summary.errors.append("source parity manifest `runs` must be an object")
    else:
        for run_name in ("java", "rust", "differential"):
            run = runs.get(run_name)
            label = f"runs.{run_name}"
            if run_name in {"java", "rust"}:
                validate_run_record(run, label, manifest_path, summary.errors)
                continue
            if not isinstance(run, dict):
                summary.errors.append(f"{label} is required")
                continue
            for field_name in ("command", "artifact"):
                if not isinstance(run.get(field_name), str) or not run[field_name].strip():
                    summary.errors.append(f"{label}.`{field_name}` is required")
            artifact = run.get("artifact")
            if isinstance(artifact, str) and artifact.strip():
                try:
                    artifact_path = manifest_file(manifest_path.parent, artifact)
                except ValueError as error:
                    summary.errors.append(f"{label}: {error}")
                else:
                    if not artifact_path.is_file():
                        summary.errors.append(f"{label}: artifact does not exist: {artifact_path}")
            if run.get("status") != "PASS":
                summary.errors.append(f"{label}.`status` must be `PASS`")
        differential = runs.get("differential")
        if isinstance(differential, dict):
            for field_name in ("mismatched", "harness_failures", "not_run"):
                if differential.get(field_name) != 0:
                    summary.errors.append(f"runs.differential.`{field_name}` must equal 0")
            if differential.get("matched") != summary.manifest_cases:
                summary.errors.append(
                    "runs.differential.`matched` must equal the number of manifest source cases "
                    f"({summary.manifest_cases})"
                )

    return summary


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
    parity: SourceParitySummary,
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
        f"- Source parity manifest: `{parity.path or 'MISSING'}`",
        f"- Whole-project acceptance module: `{parity.acceptance_module or 'MISSING'}`",
        f"- Source tests mapped: **{parity.mapped_java_tests}/{parity.java_tests}**",
        f"- Exact source assets verified: **{parity.verified_exact_assets}/{parity.java_assets}**",
        f"- Source parity completion blocked: **{str(parity.migration_completion_blocked).lower()}**",
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
            "## Source-parity completion firewall",
            "",
            "| Dimension | Current | Required |",
            "|---|---:|---:|",
            f"| Whole-project acceptance module | {parity.acceptance_module or 'MISSING'} | `<project>-test` |",
            f"| Java test methods mapped | {parity.mapped_java_tests} | {parity.java_tests} |",
            f"| Manifest test cases | {parity.manifest_cases} | every source case |",
            f"| Exact copied assets | {parity.verified_exact_assets} | {parity.java_assets} |",
            f"| Blocking errors | {len(parity.errors)} | 0 |",
            "",
        ]
    )
    for error in parity.errors:
        lines.append(f"- ERROR: {error}")
    for warning in parity.warnings:
        lines.append(f"- WARNING: {warning}")
    if not parity.errors:
        lines.append("**Source-test and asset parity manifest passed the strict completion gate.**")
    lines.append("")
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
            "3. Mark every disposition honestly; NOT_APPLICABLE, BLOCKED, and MISSING block completion.",
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
    parity: SourceParitySummary,
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
        "source_parity": {
            **asdict(parity),
            "migration_completion_blocked": parity.migration_completion_blocked,
        },
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
        description="Audit Java/Rust tests, lossless source assets, and differential parity."
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
        "--parity-manifest",
        type=Path,
        help=(
            "JSON manifest that records the non-published <project>-test acceptance module, "
            "maps every Java test/case, proves live/golden MATCH results, and records "
            "byte-identical copied test assets."
        ),
    )
    parser.add_argument(
        "--java-test-assets-root",
        action="append",
        default=[],
        type=Path,
        help=(
            "Additional Java test-asset directory, relative to --java-root or absolute inside it; "
            "repeat for non-standard fixture/data roots."
        ),
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
    try:
        java_assets = discover_java_test_assets(args.java_root, args.java_test_assets_root)
    except ValueError as error:
        raise SystemExit(str(error)) from error
    parity = validate_source_parity_manifest(
        args.parity_manifest,
        args.java_root,
        args.rust_root,
        java_tests,
        java_assets,
    )
    parity.errors.extend(rust_layout_errors(args.rust_root))
    parity.warnings.extend(rust_layout_warnings(args.rust_root))
    ledger: ObjectLedgerSummary | None = None
    if args.object_ledger is not None:
        if not args.object_ledger.is_file():
            raise SystemExit(f"object ledger is not a file: {args.object_ledger}")
        ledger = parse_object_ledger(args.object_ledger)
    report = (
        json_report(args.java_root, args.rust_root, java_tests, rust_tests, ledger, parity)
        if args.format == "json"
        else markdown(args.java_root, args.rust_root, java_tests, rust_tests, ledger, parity)
    )

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(report + "\n", encoding="utf-8")
        print(f"wrote {args.output}")
    else:
        print(report)
    if args.fail_on_incomplete:
        object_blocked = ledger is not None and ledger.migration_completion_blocked
        if object_blocked or parity.migration_completion_blocked:
            raise SystemExit(1)


if __name__ == "__main__":
    main()
