"""Regression tests for the object-ledger completion firewall."""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "audit_migration_tests.py"
SPEC = importlib.util.spec_from_file_location("audit_migration_tests", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
AUDIT = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = AUDIT
SPEC.loader.exec_module(AUDIT)


class ObjectLedgerTest(unittest.TestCase):
    def create_complete_parity_fixture(self, root: Path) -> tuple[Path, Path, Path]:
        java_root = root / "java"
        rust_root = root / "rust"
        java_test = java_root / "src/test/java/org/example/ExampleTest.java"
        java_asset = java_root / "src/test/resources/example.json"
        acceptance_root = rust_root / "example-test"
        rust_test = acceptance_root / "tests/example_test.rs"
        rust_asset = acceptance_root / "tests/fixtures/source/example.json"
        for path in (java_test, java_asset, rust_test, rust_asset):
            path.parent.mkdir(parents=True, exist_ok=True)
        (rust_root / "Cargo.toml").write_text(
            '[workspace]\nmembers = ["example-test"]\nresolver = "2"\n',
            encoding="utf-8",
        )
        (acceptance_root / "Cargo.toml").write_text(
            """[package]
name = "example-test"
version = "0.1.0"
edition = "2021"
publish = false
""",
            encoding="utf-8",
        )
        java_test.write_text(
            """import org.junit.jupiter.api.Test;
class ExampleTest {
    @Test
    public void returnsValue() { assertEquals(42, evaluate()); }
}
""",
            encoding="utf-8",
        )
        rust_test.write_text(
            """#[test]
fn returns_value() {
    assert_eq!(42, evaluate());
}
""",
            encoding="utf-8",
        )
        java_asset.write_text('{"value":42}\n', encoding="utf-8")
        rust_asset.write_bytes(java_asset.read_bytes())
        manifest = root / "source-test-parity.json"
        for artifact in (
            "case.json",
            "java.json",
            "rust.json",
            "diff.json",
            "whole-project.json",
        ):
            (root / artifact).write_text("{}\n", encoding="utf-8")
        manifest.write_text(
            json.dumps(
                {
                    "schema": 1,
                    "java_baseline": "java-sha",
                    "rust_baseline": "rust-sha",
                    "acceptance_module": {
                        "package": "example-test",
                        "manifest": "example-test/Cargo.toml",
                        "publish": False,
                        "components": ["example", "example-binding"],
                        "command": "cargo test -p example-test --all-features",
                        "status": "PASS",
                        "failed": 0,
                        "skipped": 0,
                        "not_run": 0,
                        "artifact": "whole-project.json",
                    },
                    "source_tests": [
                        {
                            "source": "src/test/java/org/example/ExampleTest.java#returnsValue",
                            "case_id": "default",
                            "targets": ["example-test/tests/example_test.rs#returns_value"],
                            "disposition": "MIRRORED",
                            "contract_preserved": True,
                            "inputs_preserved": True,
                            "assertions_preserved": True,
                            "fixture_state_preserved": True,
                            "cleanup_preserved": True,
                            "case_expansion_complete": True,
                            "result_parity": "MATCH",
                            "evidence": "case.json",
                        }
                    ],
                    "assets": [
                        {
                            "source": "src/test/resources/example.json",
                            "target": "example-test/tests/fixtures/source/example.json",
                            "mode": "COPY_EXACT",
                            "sha256": AUDIT.sha256_file(java_asset),
                        }
                    ],
                    "runs": {
                        "java": {
                            "command": "./mvnw test",
                            "status": "PASS",
                            "failed": 0,
                            "skipped": 0,
                            "not_run": 0,
                            "artifact": "java.json",
                        },
                        "rust": {
                            "command": "cargo test",
                            "status": "PASS",
                            "failed": 0,
                            "skipped": 0,
                            "not_run": 0,
                            "artifact": "rust.json",
                        },
                        "differential": {
                            "command": "./run-diff",
                            "status": "PASS",
                            "matched": 1,
                            "mismatched": 0,
                            "harness_failures": 0,
                            "not_run": 0,
                            "artifact": "diff.json",
                        },
                    },
                }
            ),
            encoding="utf-8",
        )
        return java_root, rust_root, manifest

    def test_current_rows_block_and_history_is_ignored(self) -> None:
        ledger_text = """# 对象级对照表

## 二、状态图例
| `MISSING` | 定义，不是对象行 |
| `IMPLEMENTED` | 定义，不是对象行 |

## 四、对象映射
| Java | Rust | 状态 |
|---|---|---|
| A | a.rs | `MISPLACED` |
| B | b.rs | `IMPLEMENTED` |

<!-- historical-design-appendix-start -->
## 历史设计附录
| OldA | old.rs | `IMPLEMENTED` |
| OldB | old.rs | `MISSING` |
"""
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "对象级对照表.md"
            path.write_text(ledger_text, encoding="utf-8")
            summary = AUDIT.parse_object_ledger(path)

        self.assertEqual(summary.rows_scanned, 2)
        self.assertEqual(summary.state_counts["MISPLACED"], 1)
        self.assertEqual(summary.state_counts["IMPLEMENTED"], 1)
        self.assertEqual(summary.state_counts["MISSING"], 0)
        self.assertTrue(summary.migration_completion_blocked)

    def test_handled_rows_do_not_block_completion(self) -> None:
        ledger_text = """# 对象级对照表
## 四、对象映射
| Java | Rust | 状态 |
|---|---|---|
| A | a.rs | `IMPLEMENTED` |
| B | dependency | `DEPENDENCY_REUSED` |
| C | N/A | `PLATFORM_NA` |
"""
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "对象级对照表.md"
            path.write_text(ledger_text, encoding="utf-8")
            summary = AUDIT.parse_object_ledger(path)

        self.assertEqual(summary.incomplete_count, 0)
        self.assertFalse(summary.migration_completion_blocked)

    def test_cli_fails_completion_gate_even_when_no_test_fails(self) -> None:
        ledger_text = """# 对象级对照表
## 四、对象映射
| Java | Rust | 状态 |
|---|---|---|
| A | a.rs | `STUB` |
"""
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            java_root = root / "java"
            rust_root = root / "rust"
            java_root.mkdir()
            rust_root.mkdir()
            ledger = root / "对象级对照表.md"
            ledger.write_text(ledger_text, encoding="utf-8")
            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--java-root",
                    str(java_root),
                    "--rust-root",
                    str(rust_root),
                    "--object-ledger",
                    str(ledger),
                    "--fail-on-incomplete",
                ],
                check=False,
                capture_output=True,
                text=True,
            )
        self.assertEqual(result.returncode, 1)
        self.assertIn("Migration completion blocked: **true**", result.stdout)
        self.assertIn("migration incomplete regardless of test results", result.stdout)

    def test_complete_source_test_and_exact_asset_parity_passes(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            java_root, rust_root, manifest = self.create_complete_parity_fixture(Path(temporary))
            java_tests = AUDIT.extract_java_tests(java_root)
            java_assets = AUDIT.discover_java_test_assets(java_root, [])
            summary = AUDIT.validate_source_parity_manifest(
                manifest,
                java_root,
                rust_root,
                java_tests,
                java_assets,
            )

        self.assertEqual(summary.mapped_java_tests, 1)
        self.assertEqual(summary.verified_exact_assets, 1)
        self.assertFalse(summary.migration_completion_blocked, summary.errors)

    def test_modified_target_asset_blocks_completion(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            java_root, rust_root, manifest = self.create_complete_parity_fixture(Path(temporary))
            (rust_root / "example-test/tests/fixtures/source/example.json").write_text(
                '{"value":43}\n', encoding="utf-8"
            )
            summary = AUDIT.validate_source_parity_manifest(
                manifest,
                java_root,
                rust_root,
                AUDIT.extract_java_tests(java_root),
                AUDIT.discover_java_test_assets(java_root, []),
            )

        self.assertTrue(summary.migration_completion_blocked)
        self.assertTrue(any("source/target SHA-256 mismatch" in error for error in summary.errors))

    def test_missing_manifest_blocks_strict_completion(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            java_root = root / "java"
            rust_root = root / "rust"
            java_root.mkdir()
            rust_root.mkdir()
            summary = AUDIT.validate_source_parity_manifest(
                None, java_root, rust_root, [], []
            )

        self.assertTrue(summary.migration_completion_blocked)
        self.assertIn("source parity manifest is required", summary.errors[0])

    def test_non_match_and_weakened_assertion_block_completion(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            java_root, rust_root, manifest = self.create_complete_parity_fixture(Path(temporary))
            payload = json.loads(manifest.read_text(encoding="utf-8"))
            payload["source_tests"][0]["assertions_preserved"] = False
            payload["source_tests"][0]["result_parity"] = "SEMANTIC_MISMATCH"
            manifest.write_text(json.dumps(payload), encoding="utf-8")
            summary = AUDIT.validate_source_parity_manifest(
                manifest,
                java_root,
                rust_root,
                AUDIT.extract_java_tests(java_root),
                AUDIT.discover_java_test_assets(java_root, []),
            )

        self.assertTrue(any("assertions_preserved" in error for error in summary.errors))
        self.assertTrue(any("result_parity" in error for error in summary.errors))

    def test_parameterized_case_requires_complete_expansion_attestation(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            java_root, rust_root, manifest = self.create_complete_parity_fixture(Path(temporary))
            java_test = java_root / "src/test/java/org/example/ExampleTest.java"
            java_test.write_text(
                java_test.read_text(encoding="utf-8").replace("@Test", "@ParameterizedTest"),
                encoding="utf-8",
            )
            payload = json.loads(manifest.read_text(encoding="utf-8"))
            del payload["source_tests"][0]["case_expansion_complete"]
            manifest.write_text(json.dumps(payload), encoding="utf-8")
            summary = AUDIT.validate_source_parity_manifest(
                manifest,
                java_root,
                rust_root,
                AUDIT.extract_java_tests(java_root),
                AUDIT.discover_java_test_assets(java_root, []),
            )

        self.assertTrue(any("case_expansion_complete" in error for error in summary.errors))

    def test_acceptance_module_must_be_non_published_workspace_member(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            java_root, rust_root, manifest = self.create_complete_parity_fixture(Path(temporary))
            cargo_manifest = rust_root / "example-test/Cargo.toml"
            cargo_manifest.write_text(
                cargo_manifest.read_text(encoding="utf-8").replace(
                    "publish = false", "publish = true"
                ),
                encoding="utf-8",
            )
            (rust_root / "Cargo.toml").write_text(
                '[workspace]\nmembers = []\nresolver = "2"\n',
                encoding="utf-8",
            )
            summary = AUDIT.validate_source_parity_manifest(
                manifest,
                java_root,
                rust_root,
                AUDIT.extract_java_tests(java_root),
                AUDIT.discover_java_test_assets(java_root, []),
            )

        self.assertTrue(summary.migration_completion_blocked)
        self.assertTrue(any("publish = false" in error for error in summary.errors))
        self.assertTrue(any("workspace member" in error for error in summary.errors))

    def test_cli_passes_only_with_complete_object_and_source_parity(self) -> None:
        ledger_text = """# 对象级对照表
## 四、对象映射
| Java | Rust | 状态 |
|---|---|---|
| A | a.rs | `IMPLEMENTED` |
"""
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            java_root, rust_root, manifest = self.create_complete_parity_fixture(root)
            ledger = root / "对象级对照表.md"
            ledger.write_text(ledger_text, encoding="utf-8")
            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--java-root",
                    str(java_root),
                    "--rust-root",
                    str(rust_root),
                    "--object-ledger",
                    str(ledger),
                    "--parity-manifest",
                    str(manifest),
                    "--fail-on-incomplete",
                ],
                check=False,
                capture_output=True,
                text=True,
            )

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("Source-test and asset parity manifest passed", result.stdout)

    def test_rust_file_size_uses_soft_and_hard_thresholds(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            rust_root = Path(temporary) / "rust"
            (rust_root / "src").mkdir(parents=True)
            (rust_root / "tests").mkdir(parents=True)
            (rust_root / "src/lib.rs").write_text(
                "pub fn value() -> usize { 1 }\n#[cfg(test)]\nmod tests { #[test] fn works() {} }\n",
                encoding="utf-8",
            )
            (rust_root / "tests/review.rs").write_text(
                "\n".join(f"// line {index}" for index in range(501)) + "\n",
                encoding="utf-8",
            )
            errors = AUDIT.rust_layout_errors(rust_root)
            warnings = AUDIT.rust_layout_warnings(rust_root)

            (rust_root / "tests/blocked.rs").write_text(
                "\n".join(f"// line {index}" for index in range(801)) + "\n",
                encoding="utf-8",
            )
            blocked_errors = AUDIT.rust_layout_errors(rust_root)

        self.assertEqual(errors, [])
        self.assertTrue(any("review cohesion" in warning for warning in warnings))
        self.assertTrue(any("hard maximum is 800" in error for error in blocked_errors))


if __name__ == "__main__":
    unittest.main()
