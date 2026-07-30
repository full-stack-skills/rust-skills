"""Regression tests for the object-ledger completion firewall."""

from __future__ import annotations

import importlib.util
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


if __name__ == "__main__":
    unittest.main()
