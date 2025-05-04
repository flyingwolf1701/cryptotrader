#!/usr/bin/env python3
"""
Create empty spec/doc files in your Architectum docs tree based on app structure.
"""

import os
import argparse
import questionary
import sys
import subprocess
import platform

# Templates for generated filenames
TEMPLATES = [
    "{base}_spec.yaml",
    "{base}_spec.json",
    "{base}_shape.json",
    "{base}_doc.md",
    "test_{base}.py",
    "diagnostic_{base}.py",
]


def open_file(path: str):
    """Open a file in the default editor."""
    if platform.system() == "Windows":
        os.startfile(path)
    elif platform.system() == "Darwin":
        subprocess.run(["open", path])
    else:
        subprocess.run(["xdg-open", path])


def create_files(doc_root: str, rel: str, selected: list) -> list:
    """
    Given a doc_root (docs folder), a relative path, and a list of templates,
    create empty files if they don't exist and return the list of full paths.
    """
    created = []
    for tpl in selected:
        filename = tpl.format(base=os.path.basename(rel.rstrip("/")))
        folder = os.path.join(doc_root, os.path.dirname(rel))
        os.makedirs(folder, exist_ok=True)

        full_path = os.path.join(folder, filename)
        rel_path = os.path.relpath(full_path, doc_root).replace("\\", "/")
        if not os.path.exists(full_path):
            # create empty file
            with open(full_path, "w", encoding="utf-8"):
                pass
            print(f"✅ Created: {rel_path}")
            created.append(full_path)
        else:
            print(f"⚠️ Already exists: {rel_path}")
    return created


def main():
    cwd = os.getcwd()
    default_doc = os.path.join(cwd, "src", "architectum", "project_overview")
    default_app = os.path.join(cwd, "src", "cryptotrader")

    parser = argparse.ArgumentParser(
        description="Create empty spec/doc files in your Architectum docs tree."
    )
    parser.add_argument(
        "--doc-root",
        type=str,
        default=default_doc,
        help="Path to your docs folder (e.g. src/architectum/project_overview)",
    )
    parser.add_argument(
        "--app-root",
        type=str,
        default=default_app,
        help="Path to your application code (e.g. src/cryptotrader)",
    )
    args = parser.parse_args()

    # Ask for the relative path under your app tree once
    rel = questionary.text(
        "Paste the relative path inside your app (e.g. utils/helpers or utils/helpers/file.py), or 'q' to quit:"
    ).ask()
    # Graceful exit on quit command
    if rel and rel.lower() in ("q", "quit"):
        print("❌ Quit command received. Exiting.")
        sys.exit(0)
    if not rel:
        print("❌ No path provided. Exiting.")
        sys.exit(1)

    # Normalize path separators and strip leading prefixes
    rel = rel.replace("\\", "/")
    # strip any leading "src/" if present
    if rel.startswith("src/"):
        rel = rel.split("/", 1)[1]
    # strip leading app folder name if included
    app_name = os.path.basename(args.app_root)
    if rel.startswith(f"{app_name}/"):
        rel = rel.split("/", 1)[1]

    full_app = os.path.join(args.app_root, rel)
    if not os.path.exists(full_app):
        print(f"⚠️ Path not found in app: {full_app}. Exiting.")
        sys.exit(1)

    # Ask which templates to instantiate
    selected = questionary.checkbox(
        "Select file types to generate:",
        choices=TEMPLATES,
    ).ask()
    if not selected:
        print("❌ No file types selected. Exiting.")
        sys.exit(1)

    # Create the files
    created = create_files(args.doc_root, rel, selected)

    # Optionally open them
    if created and questionary.confirm("Would you like me to open those files?").ask():
        for fpath in created:
            open_file(fpath)


if __name__ == "__main__":
    main()
