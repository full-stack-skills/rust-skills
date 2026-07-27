#!/usr/bin/env python3
"""Create the four required Java-to-Rust migration documents from templates."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path


TEMPLATE_NAMES = (
    "迁移路线图.md",
    "对象级对照表.md",
    "语义迁移对照表.md",
    "对象名称一致性检查.md",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Scaffold four per-module Java-to-Rust migration documents."
    )
    parser.add_argument("--module", required=True, help="Source module name.")
    parser.add_argument("--java-root", required=True, type=Path, help="Java module path.")
    parser.add_argument("--rust-root", required=True, type=Path, help="Rust crate/module path.")
    parser.add_argument("--output-dir", required=True, type=Path, help="Documentation directory.")
    parser.add_argument(
        "--baseline",
        required=True,
        help="Pinned baseline, for example 'java=<sha>; rust=<sha>'.",
    )
    parser.add_argument(
        "--date",
        default=dt.date.today().isoformat(),
        help="Document date in YYYY-MM-DD form (default: today).",
    )
    parser.add_argument("--force", action="store_true", help="Overwrite existing documents.")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate inputs and print destinations without writing.",
    )
    return parser.parse_args()


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


def main() -> int:
    args = parse_args()
    try:
        java_root = validate_directory(args.java_root, "Java root")
        rust_root = validate_directory(args.rust_root, "Rust root")
        template_dir = Path(__file__).resolve().parent.parent / "assets" / "templates"
        if not template_dir.is_dir():
            raise ValueError(f"template directory is missing: {template_dir}")

        output_dir = args.output_dir.expanduser().resolve()
        values = {
            "MODULE_NAME": args.module,
            # Preserve the caller's repository-relative spelling in generated
            # documents instead of leaking machine-specific absolute paths.
            "JAVA_ROOT": args.java_root.as_posix(),
            "RUST_ROOT": args.rust_root.as_posix(),
            "BASELINE": args.baseline,
            "GENERATED_DATE": args.date,
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
