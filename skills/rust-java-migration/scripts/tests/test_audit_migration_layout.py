"""Regression tests for deterministic Java-to-Rust layout auditing."""

from __future__ import annotations

import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "audit_migration_layout.py"
SPEC = importlib.util.spec_from_file_location("audit_migration_layout", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
AUDIT = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = AUDIT
SPEC.loader.exec_module(AUDIT)


class LayoutAuditTest(unittest.TestCase):
    def test_acronyms_are_converted_without_character_splitting(self) -> None:
        self.assertEqual(AUDIT.camel_to_snake("XMLBeanFactory"), "xml_bean_factory")
        self.assertEqual(AUDIT.camel_to_snake("CRC16"), "crc16")
        self.assertEqual(AUDIT.camel_to_snake("URLClassLoader"), "url_class_loader")

    def test_expected_path_retains_last_two_package_segments(self) -> None:
        package_root = Path("/source/org/springframework/beans")
        java_file = package_root / "factory" / "xml" / "support" / "Foo.java"
        actual = AUDIT.expected_rust_path(
            package_root,
            java_file,
            Path("/target/vernal-beans"),
            2,
        )
        self.assertEqual(actual, Path("src/xml/support/foo.rs"))

    def test_expected_path_handles_zero_and_one_subpackage(self) -> None:
        package_root = Path("/source/module")
        self.assertEqual(
            AUDIT.expected_rust_path(
                package_root, package_root / "RootThing.java", Path("/crate"), 2
            ),
            Path("src/root_thing.rs"),
        )
        self.assertEqual(
            AUDIT.expected_rust_path(
                package_root,
                package_root / "support" / "Helper.java",
                Path("/crate"),
                2,
            ),
            Path("src/support/helper.rs"),
        )

    def test_missing_and_misplaced_are_distinct_findings(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            java_root = root / "java"
            rust_root = root / "crate"
            (java_root / "factory" / "config").mkdir(parents=True)
            (java_root / "factory" / "config" / "BeanDefinition.java").write_text(
                "public interface BeanDefinition {}", encoding="utf-8"
            )
            (java_root / "factory" / "support" / "MissingBean.java").parent.mkdir(
                parents=True
            )
            (java_root / "factory" / "support" / "MissingBean.java").write_text(
                "public class MissingBean {}", encoding="utf-8"
            )
            (rust_root / "src").mkdir(parents=True)
            misplaced = rust_root / "src" / "bean_definition.rs"
            misplaced.write_text(
                "pub trait BeanDefinition {}", encoding="utf-8"
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--java-package-root",
                    str(java_root),
                    "--rust-root",
                    str(rust_root),
                    "--retain-segments",
                    "2",
                ],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 1)
            self.assertIn("misplaced_object_file", result.stdout)
            self.assertIn("expected src/factory/config/bean_definition.rs", result.stdout)
            self.assertIn("missing_object_file", result.stdout)
            self.assertIn("expected Rust object file src/factory/support/missing_bean.rs", result.stdout)

    def test_empty_logic_and_non_snake_case_paths_block_completion(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            rust_root = Path(temporary) / "crate"
            source = rust_root / "src" / "BadDirectory"
            source.mkdir(parents=True)
            (source / "BadFile.rs").write_text(
                "pub struct BadFile;\nimpl BadFile { pub fn run(&self) {} }\n",
                encoding="utf-8",
            )
            result = subprocess.run(
                [sys.executable, str(SCRIPT), "--rust-root", str(rust_root)],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 1)
            self.assertIn("non_snake_case_directory", result.stdout)
            self.assertIn("non_snake_case_file", result.stdout)
            self.assertIn("stub_logic", result.stdout)
            self.assertIn("migration_completion_blocked=true", result.stdout)

    def test_file_size_uses_soft_and_hard_thresholds(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            rust_root = Path(temporary) / "crate"
            source = rust_root / "src"
            integration = rust_root / "tests"
            source.mkdir(parents=True)
            integration.mkdir(parents=True)
            (source / "service.rs").write_text(
                "pub struct Service;\n#[cfg(test)]\nmod tests { #[test] fn works() {} }\n",
                encoding="utf-8",
            )
            (integration / "review.rs").write_text(
                "\n".join(f"// line {index}" for index in range(501)) + "\n",
                encoding="utf-8",
            )
            review_result = subprocess.run(
                [sys.executable, str(SCRIPT), "--rust-root", str(rust_root)],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(review_result.returncode, 0, review_result.stdout)
            self.assertIn("rust_file_over_500_lines", review_result.stdout)
            self.assertNotIn("test_code_in_production_source", review_result.stdout)

            unreviewed_strict_result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--rust-root",
                    str(rust_root),
                    "--fail-on-warning",
                ],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(unreviewed_strict_result.returncode, 1)

            strict_review_result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--rust-root",
                    str(rust_root),
                    "--fail-on-warning",
                    "--reviewed-large-file",
                    "tests/review.rs",
                ],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(
                strict_review_result.returncode,
                0,
                strict_review_result.stdout,
            )
            self.assertIn("allowed: tests/review.rs", strict_review_result.stdout)

            (integration / "blocked.rs").write_text(
                "\n".join(f"// line {index}" for index in range(801)) + "\n",
                encoding="utf-8",
            )
            blocked_result = subprocess.run(
                [sys.executable, str(SCRIPT), "--rust-root", str(rust_root)],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(blocked_result.returncode, 1)
            self.assertIn("rust_file_over_800_lines", blocked_result.stdout)
            self.assertIn("migration_completion_blocked=true", blocked_result.stdout)


if __name__ == "__main__":
    unittest.main()
