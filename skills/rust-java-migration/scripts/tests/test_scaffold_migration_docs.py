"""Regression tests for the canonical four-document scaffold."""

from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scaffold_migration_docs.py"
DOCUMENTS = {
    "迁移路线图.md",
    "对象级对照表.md",
    "语义迁移对照表.md",
    "对象名称一致性检查.md",
}


class ScaffoldMigrationDocsTest(unittest.TestCase):
    def test_generates_four_detailed_current_documents(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            java_root = root / "java-module"
            package_root = java_root / "src/main/java/org/example/module"
            rust_root = root / "crate"
            output = root / "docs/module"
            package_root.mkdir(parents=True)
            (rust_root / "src").mkdir(parents=True)

            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--module",
                    "module",
                    "--java-root",
                    str(java_root),
                    "--java-package-root",
                    str(package_root),
                    "--rust-root",
                    str(rust_root),
                    "--output-dir",
                    str(output),
                    "--java-baseline",
                    "java-sha",
                    "--rust-baseline",
                    "rust-sha",
                ],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual({path.name for path in output.glob("*.md")}, DOCUMENTS)
            for path in output.glob("*.md"):
                text = path.read_text(encoding="utf-8")
                self.assertIn("current-migration-contract-start", text)
                self.assertIn("末 `2` 层", text)
                self.assertGreaterEqual(
                    sum(bool(line.strip()) for line in text.splitlines()),
                    45,
                )

    def test_force_regeneration_preserves_merged_history_appendix(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            java_root = root / "java-module"
            package_root = java_root / "src/main/java/org/example/module"
            rust_root = root / "crate"
            output = root / "docs/module"
            package_root.mkdir(parents=True)
            (rust_root / "src").mkdir(parents=True)
            command = [
                sys.executable,
                str(SCRIPT),
                "--module",
                "module",
                "--java-root",
                str(java_root),
                "--java-package-root",
                str(package_root),
                "--rust-root",
                str(rust_root),
                "--output-dir",
                str(output),
                "--java-baseline",
                "java-sha",
                "--rust-baseline",
                "rust-sha",
            ]
            first = subprocess.run(command, check=False, capture_output=True, text=True)
            self.assertEqual(first.returncode, 0, first.stderr)
            object_table = output / "对象级对照表.md"
            text = object_table.read_text(encoding="utf-8")
            current = text.split("<!-- historical-design-appendix-start -->", 1)[0]
            object_table.write_text(
                current
                + "<!-- historical-design-appendix-start -->\n"
                + "## 历史设计附录\n\n保留这段历史决策。\n",
                encoding="utf-8",
            )

            second = subprocess.run(
                [*command, "--force"],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(second.returncode, 0, second.stderr)
            regenerated = object_table.read_text(encoding="utf-8")
            self.assertIn("保留这段历史决策。", regenerated)
            self.assertEqual(
                regenerated.count("<!-- historical-design-appendix-start -->"),
                1,
            )

    def test_force_refuses_to_overwrite_current_document(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            java_root = root / "java-module"
            package_root = java_root / "src/main/java/org/example/module"
            rust_root = root / "crate"
            output = root / "docs/module"
            package_root.mkdir(parents=True)
            (rust_root / "src").mkdir(parents=True)
            command = [
                sys.executable,
                str(SCRIPT),
                "--module",
                "module",
                "--java-root",
                str(java_root),
                "--java-package-root",
                str(package_root),
                "--rust-root",
                str(rust_root),
                "--output-dir",
                str(output),
                "--java-baseline",
                "java-sha",
                "--rust-baseline",
                "rust-sha",
            ]
            first = subprocess.run(command, check=False, capture_output=True, text=True)
            self.assertEqual(first.returncode, 0, first.stderr)
            object_table = output / "对象级对照表.md"
            object_table.write_text(
                object_table.read_text(encoding="utf-8").replace(
                    "文档状态：`DRAFT`",
                    "文档状态：`CURRENT`",
                ),
                encoding="utf-8",
            )

            second = subprocess.run(
                [*command, "--force"],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(second.returncode, 2)
            self.assertIn("refusing to overwrite populated/current document", second.stderr)
            self.assertIn("文档状态：`CURRENT`", object_table.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
