import os
import argparse
from typing import Optional

# Ignore hidden folders and common build/system folders
IGNORED_FOLDERS = {"__pycache__", ".git", ".venv", "node_modules", "dist"}

def generate_directory_tree(base_path: str, indent: str = "", current_depth: int = 0, max_depth: Optional[int] = None) -> str:
    """
    Recursively generate a markdown-style directory tree,
    ignoring hidden files/folders and excluded names.
    """
    tree_lines = []

    if max_depth is not None and current_depth > max_depth:
        return ""

    entries = sorted(
        entry for entry in os.listdir(base_path)
        if not entry.startswith('.') and entry not in IGNORED_FOLDERS
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
                max_depth
            )
            if subtree:
                tree_lines.append(subtree)
        else:
            tree_lines.append(f"{indent}{connector}{entry}")

    return "\n".join(tree_lines)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate Markdown directory structure.")
    parser.add_argument(
        "--output",
        type=str,
        default=os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "project_structure.md")),
        help="Path to save the output Markdown file."
    )
    parser.add_argument(
        "--depth",
        type=int,
        default=None,
        help="Optional max depth to recurse."
    )
    args = parser.parse_args()

    # Go up to project root
    SCRIPT_DIR = os.path.dirname(__file__)
    PROJECT_ROOT_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, "../.."))

    output = generate_directory_tree(PROJECT_ROOT_DIR, current_depth=0, max_depth=args.depth)

    with open(args.output, "w", encoding="utf-8") as f:
        f.write("```\n")
        f.write(output)
        f.write("\n```")

    print(f"✅ Directory structure written to {args.output}!")
