#!/usr/bin/env python3
"""Validate rust-skills structure and optionally compile golden examples."""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILLS_DIR = ROOT / "skills"
MANIFEST = ROOT / ".claude-plugin" / "plugin.json"
SCENARIOS = ROOT / "evaluation" / "scenarios.json"
NAME_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
LINK_PATTERN = re.compile(r"\[[^\]]*\]\(([^)]+)\)")


def parse_frontmatter(path: Path) -> tuple[dict[str, str], list[str]]:
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0].strip() != "---":
        return {}, lines
    try:
        end = lines.index("---", 1)
    except ValueError:
        return {}, lines

    metadata: dict[str, str] = {}
    for line in lines[1:end]:
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        metadata[key.strip()] = value.strip().strip('"\'')
    return metadata, lines


def relative_link_errors(path: Path) -> list[str]:
    errors: list[str] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        for target in LINK_PATTERN.findall(line):
            target = target.strip().strip("<>")
            if not target or target.startswith(("http://", "https://", "mailto:", "#")):
                continue
            relative_target = target.split("#", 1)[0]
            if relative_target and not (path.parent / relative_target).resolve().exists():
                errors.append(f"{path.relative_to(ROOT)}:{line_number}: missing link {target}")
    return errors


def check_repository(require_examples: bool) -> tuple[list[str], list[Path]]:
    errors: list[str] = []
    golden_manifests: list[Path] = []

    if not (ROOT / "LICENSE").is_file():
        errors.append("LICENSE is missing")

    manifest_data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    manifest_paths = [Path(item.removeprefix("./")) for item in manifest_data.get("skills", [])]
    manifest_names = [path.name for path in manifest_paths]
    directory_names = sorted(path.name for path in SKILLS_DIR.iterdir() if path.is_dir())

    if len(manifest_names) != len(set(manifest_names)):
        errors.append("plugin manifest contains duplicate skill paths")
    if sorted(manifest_names) != directory_names:
        errors.append(
            "plugin manifest and skills directories differ: "
            f"manifest={sorted(manifest_names)}, directories={directory_names}"
        )

    seen_names: set[str] = set()
    for skill_name in directory_names:
        skill_dir = SKILLS_DIR / skill_name
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.is_file():
            errors.append(f"skills/{skill_name}/SKILL.md is missing")
            continue

        metadata, lines = parse_frontmatter(skill_md)
        extra_keys = sorted(set(metadata) - {"name", "description"})
        if extra_keys:
            errors.append(f"skills/{skill_name}: unexpected frontmatter keys: {extra_keys}")
        if metadata.get("name") != skill_name:
            errors.append(
                f"skills/{skill_name}: frontmatter name is {metadata.get('name')!r}"
            )
        if not metadata.get("description"):
            errors.append(f"skills/{skill_name}: description is missing")
        if not NAME_PATTERN.fullmatch(skill_name):
            errors.append(f"skills/{skill_name}: invalid skill name")
        if skill_name in seen_names:
            errors.append(f"skills/{skill_name}: duplicate skill name")
        seen_names.add(skill_name)
        if len(lines) > 500:
            errors.append(f"skills/{skill_name}/SKILL.md has {len(lines)} lines; maximum is 500")

        agent_yaml = skill_dir / "agents" / "openai.yaml"
        if not agent_yaml.is_file():
            errors.append(f"skills/{skill_name}/agents/openai.yaml is missing")
        else:
            agent_text = agent_yaml.read_text(encoding="utf-8")
            if f"${skill_name}" not in agent_text:
                errors.append(
                    f"skills/{skill_name}/agents/openai.yaml default prompt must mention ${skill_name}"
                )

        manifests = sorted((skill_dir / "examples").glob("golden-*/Cargo.toml"))
        if require_examples and not manifests:
            errors.append(f"skills/{skill_name}: no examples/golden-*/Cargo.toml found")
        golden_manifests.extend(manifests)

    for markdown in sorted(ROOT.rglob("*.md")):
        errors.extend(relative_link_errors(markdown))
        fence_count = sum(
            1 for line in markdown.read_text(encoding="utf-8").splitlines() if line.startswith("```")
        )
        if fence_count % 2:
            errors.append(f"{markdown.relative_to(ROOT)}: unclosed fenced code block")

    for readme in (ROOT / "README.md", ROOT / "README.zh-CN.md"):
        text = readme.read_text(encoding="utf-8")
        if str(len(directory_names)) not in text or "rust-stable" not in text:
            errors.append(f"{readme.name}: missing current skill count or rust-stable entry")

    if not SCENARIOS.is_file():
        errors.append("evaluation/scenarios.json is missing")
    else:
        scenario_data = json.loads(SCENARIOS.read_text(encoding="utf-8"))
        cases = scenario_data.get("cases", [])
        case_ids: set[str] = set()
        covered_skills: set[str] = set()
        for case in cases:
            case_id = case.get("id")
            if not case_id or case_id in case_ids:
                errors.append(f"evaluation scenario has missing or duplicate id: {case_id!r}")
            case_ids.add(case_id)
            if not case.get("prompt") or not case.get("assertions"):
                errors.append(f"evaluation scenario {case_id!r} lacks prompt or assertions")
            for expected_skill in case.get("expected_skills", []):
                if expected_skill not in directory_names:
                    errors.append(
                        f"evaluation scenario {case_id!r} references unknown skill {expected_skill!r}"
                    )
                covered_skills.add(expected_skill)
        missing_coverage = sorted(set(directory_names) - covered_skills)
        if missing_coverage:
            errors.append(f"evaluation scenarios do not cover skills: {missing_coverage}")

    return errors, golden_manifests


def run_command(command: list[str], cwd: Path, environment: dict[str, str]) -> str | None:
    completed = subprocess.run(
        command,
        cwd=cwd,
        env=environment,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    if completed.returncode == 0:
        return None
    return f"{' '.join(command)} failed in {cwd}:\n{completed.stdout.rstrip()}"


def check_examples(manifests: list[Path]) -> list[str]:
    errors: list[str] = []
    with tempfile.TemporaryDirectory(prefix="rust-skills-validation-") as temporary:
        temporary_root = Path(temporary)
        for index, source_manifest in enumerate(manifests):
            source_crate = source_manifest.parent
            crate = temporary_root / f"crate-{index:02d}-{source_crate.name}"
            shutil.copytree(source_crate, crate)
            environment = os.environ.copy()
            environment["CARGO_TARGET_DIR"] = str(temporary_root / "target")

            commands = [
                ["cargo", "fmt", "--manifest-path", str(crate / "Cargo.toml"), "--", "--check"],
                [
                    "cargo",
                    "check",
                    "--manifest-path",
                    str(crate / "Cargo.toml"),
                    "--all-targets",
                    "--all-features",
                    "--offline",
                ],
                [
                    "cargo",
                    "test",
                    "--manifest-path",
                    str(crate / "Cargo.toml"),
                    "--all-targets",
                    "--all-features",
                    "--offline",
                ],
                [
                    "cargo",
                    "clippy",
                    "--manifest-path",
                    str(crate / "Cargo.toml"),
                    "--all-targets",
                    "--all-features",
                    "--offline",
                    "--",
                    "-D",
                    "warnings",
                ],
            ]
            for command in commands:
                error = run_command(command, crate, environment)
                if error:
                    errors.append(error)
                    break
            else:
                print(f"[OK] {source_crate.relative_to(ROOT)}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check-examples",
        action="store_true",
        help="copy, format-check, compile, test and lint every golden example",
    )
    arguments = parser.parse_args()

    errors, manifests = check_repository(require_examples=True)
    if not errors and arguments.check_examples:
        errors.extend(check_examples(manifests))

    if errors:
        print(f"Validation failed with {len(errors)} error(s):", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    skill_count = sum(1 for path in SKILLS_DIR.iterdir() if path.is_dir())
    print(
        f"Validated {skill_count} skills, "
        f"{len(manifests)} golden examples, and all local Markdown links."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
