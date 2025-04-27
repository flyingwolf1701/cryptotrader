# file: architectum/scripts/file_structure_to_md.py

import os
import sys
import argparse
import subprocess
from typing import Optional

# Ignore hidden folders and common build/system folders
IGNORED_FOLDERS = {"__pycache__", ".git", ".venv", "node_modules", "dist"}


def generate_directory_tree(
    base_path: str,
    indent: str = "",
    current_depth: int = 0,
    max_depth: Optional[int] = None,
) -> str:
    """
    Recursively generate a markdown-style directory tree,
    ignoring hidden files/folders and excluded names.
    """
    tree_lines = []

    if max_depth is not None and current_depth > max_depth:
        return ""

    entries = sorted(
        entry
        for entry in os.listdir(base_path)
        if not entry.startswith(".") and entry not in IGNORED_FOLDERS
    )

    entry_count = len(entries)

    for idx, entry in enumerate(entries):
        full_path = os.path.join(base_path, entry)
        is_last = idx == entry_count - 1
        connector = "└── " if is_last else "├── "

        if os.path.isdir(full_path):
            tree_lines.append(f"{indent}{connector}{entry}/")
            subtree = generate_directory_tree(
                full_path,
                indent + ("    " if is_last else "│   "),
                current_depth + 1,
                max_depth,
            )
            if subtree:
                tree_lines.append(subtree)
        else:
            tree_lines.append(f"{indent}{connector}{entry}")

    return "\n".join(tree_lines)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate Markdown directory structure."
    )
    parser.add_argument(
        "--output",
        type=str,
        default=os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "project_structure.md")
        ),
        help="Path to save the project_structure.md file.",
    )
    parser.add_argument(
        "--depth", type=int, default=None, help="Optional max depth to recurse."
    )
    args = parser.parse_args()

    # Script and project roots
    SCRIPT_DIR = os.path.dirname(__file__)
    PROJECT_ROOT_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, "../.."))
    ARCH_ROOT_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))

    # 1) architectum_structure.md (from architectum/src/)
    ARCHITECTUM_OUTPUT = os.path.join(ARCH_ROOT_DIR, "architectum_structure.md")
    ARCH_SRC_DIR = os.path.join(ARCH_ROOT_DIR, "src")
    arch_tree = generate_directory_tree(
        ARCH_SRC_DIR, current_depth=0, max_depth=args.depth
    )

    with open(ARCHITECTUM_OUTPUT, "w", encoding="utf-8") as f:
        f.write("```\n")
        f.write("src/\n")
        f.write(arch_tree)
        f.write("\n```")
    print(f"✅ Architectum structure written to {ARCHITECTUM_OUTPUT}!")

    # 2) project_structure.md (from <repo root>/src/)
    PROJ_SRC_DIR = os.path.join(PROJECT_ROOT_DIR, "src")
    proj_tree = generate_directory_tree(
        PROJ_SRC_DIR, current_depth=0, max_depth=args.depth
    )

    with open(args.output, "w", encoding="utf-8") as f:
        f.write("```\n")
        f.write("src/\n")
        f.write(proj_tree)
        f.write("\n```")
    print(f"✅ Directory structure written to {args.output}!")

    # 3) Invoke the sync script
    sync_script = os.path.join(SCRIPT_DIR, "sync_doc_structure.py")
    print("🔄 Running sync_doc_structure.py…")
    result = subprocess.run([sys.executable, sync_script], cwd=PROJECT_ROOT_DIR)
    if result.returncode == 0:
        print("✅ sync_doc_structure.py completed successfully!")
    else:
        print(f"⚠️ sync_doc_structure.py exited with code {result.returncode}.")
        sys.exit(result.returncode)
