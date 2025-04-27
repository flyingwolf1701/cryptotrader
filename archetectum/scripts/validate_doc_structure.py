import os
import argparse
import questionary
from typing import Optional

IGNORED_FOLDERS = {"__pycache__", ".git", ".venv", "node_modules", "dist"}

def list_directories(base_path):
    directories = set()
    for root, dirs, files in os.walk(base_path):
        for dir_name in dirs:
            full_dir_path = os.path.join(root, dir_name)
            rel_dir_path = os.path.relpath(full_dir_path, base_path)
            if not dir_name.startswith('.') and dir_name not in IGNORED_FOLDERS:
                directories.add(rel_dir_path.replace("\\", "/"))
    return directories

def prompt_user_to_create(missing_dirs, doc_src_root):
    """
    Interactive multi-select CLI for missing folders under src/.
    """
    if not missing_dirs:
        print("✅ No missing folders found!")
        return

    print("\n⚠️ Missing folders detected under src/:")

    choices = [
        {"name": path, "checked": False}
        for path in sorted(missing_dirs)
    ]

    selected = questionary.checkbox(
        "Select folders to create under src/ (SPACE to select, ENTER to confirm):",
        choices=choices
    ).ask()

    if not selected:
        print("❌ No folders selected. Exiting.")
        return

    for folder in selected:
        path_to_create = os.path.join(doc_src_root, folder)
        os.makedirs(path_to_create, exist_ok=True)
        print(f"✅ Created: src/{folder}")

def validate_structure(app_root, doc_root):
    app_dirs = list_directories(app_root)

    # Ensure src/ exists inside archetectum/
    doc_src_root = os.path.join(doc_root, "src")
    os.makedirs(doc_src_root, exist_ok=True)

    # List documentation folders relative to src/
    if os.path.exists(doc_src_root):
        doc_dirs = list_directories(doc_src_root)
    else:
        doc_dirs = set()

    missing_dirs = app_dirs - doc_dirs

    validate_result = prompt_user_to_create(missing_dirs, doc_src_root)
    return validate_result

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Validate that Archetectum/src/ mirrors the app/src/ folder structure.")
    parser.add_argument(
        "--app-root",
        type=str,
        default=os.path.abspath(os.path.join(os.path.dirname(__file__), "../..", "src")),
        help="Path to the application source folder (e.g., src/)"
    )
    parser.add_argument(
        "--doc-root",
        type=str,
        default=os.path.abspath(os.path.join(os.path.dirname(__file__), "..")),
        help="Path to the documentation folder root (e.g., archetectum/)"
    )
    args = parser.parse_args()

    print(f"🔍 Verifying that `{args.doc_root}/src/` mirrors `{args.app_root}` ...\n")
    validate_structure(args.app_root, args.doc_root)
