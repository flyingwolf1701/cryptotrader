#!/usr/bin/env python3
"""
Generate a Markdown directory tree for the `cryptotrader/` project.
- Ignores any `__pycache__` directories.
- Wraps the tree in a collapsible `<details>` block.
- Outputs to `app_file_structure.md`.

Usage:
    python3 scripts/gen_tree_md.py
"""
import os
from pathlib import Path

def tree(dir_path: Path, prefix: str, file_handle):
    # List entries, skip __pycache__, sort directories first
    entries = sorted(
        [e for e in dir_path.iterdir() if e.name != "__pycache__"],
        key=lambda e: (e.is_file(), e.name.lower())
    )
    for index, entry in enumerate(entries):
        connector = "└── " if index == len(entries) - 1 else "├── "
        name = entry.name + ("/" if entry.is_dir() else "")
        file_handle.write(f"{prefix}{connector}{name}\n")
        if entry.is_dir():
            extension = "    " if index == len(entries) - 1 else "│   "
            tree(entry, prefix + extension, file_handle)


def main():
    root = Path("cryptotrader")
    output = Path("app_file_structure.md")
    with output.open("w", encoding="utf-8") as f:
        f.write("<details>\n")
        f.write(f"<summary>{root.name}/</summary>\n\n")
        f.write("```\n")
        tree(root, "", f)
        f.write("```\n")
        f.write("</details>\n")


if __name__ == "__main__":
    if not Path("cryptotrader").exists():
        print("Error: cryptotrader/ directory not found.")
    else:
        main()
