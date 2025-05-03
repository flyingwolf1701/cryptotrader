# architectum/scripts/file_structure_to_md.py

import argparse
from pathlib import Path
from typing import Optional

IGNORED_FOLDERS = {"__pycache__", ".git", ".venv", "node_modules", "dist"}


def generate_tree(
    base: Path,
    indent: str = "",
    last: bool = False,
    max_depth: Optional[int] = None,
    depth: int = 0,
) -> str:
    if max_depth is not None and depth > max_depth:
        return ""
    entries = sorted(
        [p for p in base.iterdir() if not p.name.startswith(".") and p.name not in IGNORED_FOLDERS]
    )
    lines = []
    for idx, entry in enumerate(entries):
        is_last = idx == len(entries) - 1
        conn = "└── " if is_last else "├── "
        lines.append(f"{indent}{conn}{entry.name}{'/' if entry.is_dir() else ''}")
        if entry.is_dir():
            sub = generate_tree(
                entry,
                indent + ("    " if is_last else "│   "),
                is_last,
                max_depth,
                depth + 1,
            )
            if sub:
                lines.append(sub)
    return "\n".join(lines)


def main():
    cwd = Path.cwd()
    default_spec = cwd / "src" / "architectum" / "cryptotrader_specs"
    default_app = cwd / "src" / "cryptotrader"
    default_out = cwd / "src" / "architectum" / "project_overview"

    p = argparse.ArgumentParser(description="Dump markdown trees for your app and specs.")
    p.add_argument(
        "--depth", "-d", type=int, default=None, help="Max recursion depth"
    )
    p.add_argument(
        "--spec-dir",
        type=Path,
        default=default_spec,
        help="Where your specs live (e.g. src/architectum/cryptotrader_specs)",
    )
    p.add_argument(
        "--app-dir",
        type=Path,
        default=default_app,
        help="Where your code lives (e.g. src/cryptotrader)",
    )
    p.add_argument(
        "--out-dir",
        type=Path,
        default=default_out,
        help="Where to write the .md files",
    )
    args = p.parse_args()

    args.out_dir.mkdir(parents=True, exist_ok=True)

    # Specs
    spec_md = args.out_dir / "architectum_specs_structure.md"
    spec_content = (
        "```\ncryptotrader_specs/\n"
        + generate_tree(args.spec_dir, max_depth=args.depth)
        + "\n```"
    )
    spec_md.write_text(spec_content, encoding="utf-8")
    print(f"✅ {spec_md}")

    # App
    app_md = args.out_dir / "app_structure.md"
    app_content = (
        "```\ncryptotrader/\n"
        + generate_tree(args.app_dir, max_depth=args.depth)
        + "\n```"
    )
    app_md.write_text(app_content, encoding="utf-8")
    print(f"✅ {app_md}")


if __name__ == "__main__":
    main()
