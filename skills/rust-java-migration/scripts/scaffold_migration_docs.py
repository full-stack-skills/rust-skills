#!/usr/bin/env python3
"""Create the four required Java-to-Rust migration documents from templates."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
from pathlib import Path


TEMPLATE_NAMES = (
    "迁移路线图.md",
    "对象级对照表.md",
    "语义迁移对照表.md",
    "对象名称一致性检查.md",
)
HISTORY_APPENDIX_START = "<!-- historical-design-appendix-start -->"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Scaffold four per-module Java-to-Rust migration documents."
    )
    parser.add_argument("--module", required=True, help="Source module name.")
    parser.add_argument("--java-root", required=True, type=Path, help="Java module path.")
    parser.add_argument(
        "--java-package-root",
        required=True,
        type=Path,
        help="Directory that represents the Java module's root package.",
    )
    parser.add_argument("--rust-root", required=True, type=Path, help="Rust crate/module path.")
    parser.add_argument("--output-dir", required=True, type=Path, help="Documentation directory.")
    parser.add_argument("--java-baseline", help="Pinned Java commit, tag, or artifact version.")
    parser.add_argument("--rust-baseline", help="Pinned Rust commit.")
    parser.add_argument(
        "--baseline",
        help="Legacy form: 'java=<sha>; rust=<sha>'. Prefer separate baseline options.",
    )
    parser.add_argument(
        "--date",
        default=dt.date.today().isoformat(),
        help="Document date in YYYY-MM-DD form (default: today).",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help=(
            "Overwrite an untouched disposable DRAFT only; never use this to merge "
            "or refresh populated current facts."
        ),
    )
    parser.add_argument(
        "--retain-segments",
        type=int,
        default=2,
        choices=(1, 2),
        help="Number of trailing Java package segments to retain (default: 2).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate inputs and print destinations without writing.",
    )
    return parser.parse_args()


def baselines(args: argparse.Namespace) -> tuple[str, str]:
    """Resolve explicit baselines, retaining the legacy combined argument."""
    if args.java_baseline or args.rust_baseline:
        if not args.java_baseline or not args.rust_baseline:
            raise ValueError("--java-baseline and --rust-baseline must be supplied together")
        if args.baseline:
            raise ValueError("use separate baseline options or --baseline, not both")
        return args.java_baseline, args.rust_baseline
    if not args.baseline:
        raise ValueError("supply --java-baseline and --rust-baseline")
    match = re.fullmatch(
        r"\s*java\s*=\s*([^;]+?)\s*;\s*rust\s*=\s*(.+?)\s*",
        args.baseline,
        re.IGNORECASE,
    )
    if match is None:
        raise ValueError("--baseline must use 'java=<sha>; rust=<sha>'")
    return match.group(1), match.group(2)


def validate_directory(path: Path, label: str) -> Path:
    resolved = path.expanduser().resolve()
    if not resolved.is_dir():
        raise ValueError(f"{label} is not a directory: {resolved}")
    return resolved


def render(template: str, values: dict[str, str]) -> str:
    rendered = template
    for key, value in values.items():
        rendered = rendered.replace("{{" + key + "}}", value)
    unresolved = sorted(
        token.split("}}", 1)[0]
        for token in rendered.split("{{")[1:]
        if "}}" in token
    )
    if unresolved:
        raise ValueError(f"unresolved template values: {', '.join(unresolved)}")
    return rendered


def preserve_historical_appendix(rendered: str, existing: str) -> str:
    """Keep a merged historical appendix when an explicit regeneration occurs."""
    if HISTORY_APPENDIX_START not in existing:
        return rendered
    existing_appendix = existing.split(HISTORY_APPENDIX_START, 1)[1]
    current = rendered.split(HISTORY_APPENDIX_START, 1)[0].rstrip()
    return (
        current
        + "\n\n"
        + HISTORY_APPENDIX_START
        + existing_appendix
    )


def main() -> int:
    args = parse_args()
    try:
        java_root = validate_directory(args.java_root, "Java root")
        java_package_root = validate_directory(args.java_package_root, "Java package root")
        validate_directory(args.rust_root, "Rust root")
        if java_package_root != java_root and java_root not in java_package_root.parents:
            raise ValueError(
                f"Java package root must be inside Java root: {java_package_root}"
            )
        java_baseline, rust_baseline = baselines(args)
        template_dir = Path(__file__).resolve().parent.parent / "assets" / "templates"
        if not template_dir.is_dir():
            raise ValueError(f"template directory is missing: {template_dir}")

        output_dir = args.output_dir.expanduser().resolve()
        values = {
            "MODULE_NAME": args.module,
            # Preserve the caller's repository-relative spelling in generated
            # documents instead of leaking machine-specific absolute paths.
            "JAVA_ROOT": args.java_root.as_posix(),
            "JAVA_PACKAGE_ROOT": args.java_package_root.as_posix(),
            "RUST_ROOT": args.rust_root.as_posix(),
            "RETAIN_SEGMENTS": str(args.retain_segments),
            "JAVA_BASELINE": java_baseline,
            "RUST_BASELINE": rust_baseline,
            "GENERATED_DATE": args.date,
            "AUDITED_DATE": args.date,
            "DOCUMENT_STATUS": "DRAFT",
        }

        planned: list[dict[str, str]] = []
        rendered_documents: list[tuple[Path, str]] = []
        for name in TEMPLATE_NAMES:
            template_path = template_dir / name
            if not template_path.is_file():
                raise ValueError(f"template is missing: {template_path}")
            destination = output_dir / name
            if destination.exists() and not args.force:
                raise FileExistsError(
                    f"refusing to overwrite {destination}; pass --force explicitly"
                )
            content = render(template_path.read_text(encoding="utf-8"), values)
            if destination.exists() and args.force:
                existing = destination.read_text(encoding="utf-8")
                if "文档状态：`DRAFT`" not in existing:
                    raise ValueError(
                        f"refusing to overwrite populated/current document: {destination}"
                    )
                content = preserve_historical_appendix(
                    content,
                    existing,
                )
            rendered_documents.append((destination, content))
            planned.append({"template": str(template_path), "output": str(destination)})

        if not args.dry_run:
            output_dir.mkdir(parents=True, exist_ok=True)
            for destination, content in rendered_documents:
                destination.write_text(content, encoding="utf-8")

        print(
            json.dumps(
                {
                    "module": args.module,
                    "dry_run": args.dry_run,
                    "documents": planned,
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 0
    except (OSError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
