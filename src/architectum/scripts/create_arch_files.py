# create_docs.py

import os
import argparse
import questionary
import sys

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
    """Open a file with the system default application (Windows)."""
    try:
        os.startfile(path)
    except Exception as e:
        print(f"⚠️ Could not open {path}: {e}")

def create_files(base_doc_path: str, relative_path: str, selected_templates: list):
    # Determine folder and base name
    if relative_path.endswith(".py"):
        folder = os.path.join(base_doc_path, os.path.dirname(relative_path))
        base = os.path.splitext(os.path.basename(relative_path))[0]
    else:
        folder = os.path.join(base_doc_path, relative_path)
        base = os.path.basename(relative_path)

    os.makedirs(folder, exist_ok=True)

    architectum_root = os.path.abspath(os.path.join(base_doc_path, ".."))
    created_files = []

    for tpl in selected_templates:
        filename = tpl.format(base=base)
        full_path = os.path.join(folder, filename)
        rel_path = os.path.relpath(full_path, architectum_root).replace("\\", "/")
        if not os.path.exists(full_path):
            with open(full_path, "w", encoding="utf-8"):
                pass
            print(f"✅ Created: {rel_path}")
            created_files.append(full_path)
        else:
            print(f"⚠️ Already exists: {rel_path}")

    return created_files

def main():
    parser = argparse.ArgumentParser(description="Create empty Architectum spec/doc files.")
    parser.add_argument(
        "--doc-root", type=str,
        default=os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")),
        help="Path to the architectum/src folder."
    )
    parser.add_argument(
        "--app-root", type=str,
        default=os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "src")),
        help="Path to the real application src folder."
    )
    args = parser.parse_args()

    # Ask for the relative path
    while True:
        rel = questionary.text(
            "Paste the relative path (e.g., utils/helpers or utils/helpers/file.py):"
        ).ask()
        if not rel:
            print("❌ No path provided. Exiting.")
            sys.exit(1)

        rel = rel.replace("\\", "/")
        if rel.startswith("src/"):
            rel = rel[4:]

        full_app = os.path.join(args.app_root, rel)
        if not os.path.exists(full_app):
            retry = questionary.confirm(
                "❌ Path does not exist in application src/... Would you like to try again?"
            ).ask()
            if not retry:
                print("❌ Exiting.")
                sys.exit(1)
            continue
        break

    # Present checkbox choices based on templates
    choices = [
        {"name": tpl, "checked": False}
        for tpl in TEMPLATES
    ]
    selected = questionary.checkbox(
        "Select file templates to create:",
        choices=choices
    ).ask()

    if not selected:
        print("❌ No file types selected. Exiting.")
        sys.exit(1)

    # Create files and get list of newly created ones
    created = create_files(args.doc_root, rel, selected)

    # Prompt to open them all
    if created:
        if questionary.confirm("Would you like me to open those files?").ask():
            for f in created:
                open_file(f)

if __name__ == "__main__":
    main()
