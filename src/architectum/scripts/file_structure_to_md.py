# file: architectum/scripts/file_structure_to_md.py

import os
import argparse
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
    Walk base_path and return a markdown-style tree (lines prefixed with ├── or └──).
    """
    entries = sorted(
        [
            e
            for e in os.listdir(base_path)
            if not e.startswith(".") and e not in IGNORED_FOLDERS
        ]
    )
    tree_lines = []
    for idx, entry in enumerate(entries):
        full_path = os.path.join(base_path, entry)
        is_last = idx == len(entries) - 1
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


def main():
    parser = argparse.ArgumentParser(
        description="Generate Markdown directory trees for both your app and your specs."
    )
    parser.add_argument(
        "--depth", type=int, default=None, help="Optional max depth to recurse."
    )
    args = parser.parse_args()

    # locate project root and set up output folder
    SCRIPT_DIR = os.path.dirname(__file__)
    PROJECT_ROOT_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, "../.."))
    OUTPUT_DIR = os.path.join(
        PROJECT_ROOT_DIR, "src", "architectum", "project_overview"
    )
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # 1) Specs structure
    SPEC_SRC_DIR = os.path.join(
        PROJECT_ROOT_DIR, "src", "architectum", "cryptotrader_specs"
    )
    SPEC_OUTPUT = os.path.join(
        OUTPUT_DIR, "architectum_specs_structure.md"
    )
    spec_tree = generate_directory_tree(
        SPEC_SRC_DIR, current_depth=0, max_depth=args.depth
    )
    with open(SPEC_OUTPUT, "w", encoding="utf-8") as f:
        f.write("```\n")
        f.write("cryptotrader_specs/\n")
        f.write(spec_tree)
        f.write("\n```")
    print(f"✅ Specs directory structure written to {SPEC_OUTPUT}!")

    # 2) App structure
    APP_SRC_DIR = os.path.join(PROJECT_ROOT_DIR, "src", "cryptotrader")
    APP_OUTPUT = os.path.join(OUTPUT_DIR, "app_structure.md")
    app_tree = generate_directory_tree(
        APP_SRC_DIR, current_depth=0, max_depth=args.depth
    )
    with open(APP_OUTPUT, "w", encoding="utf-8") as f:
        f.write("```\n")
        f.write("cryptotrader/\n")
        f.write(app_tree)
        f.write("\n```")
    print(f"✅ App directory structure written to {APP_OUTPUT}!")


if __name__ == "__main__":
    main()
