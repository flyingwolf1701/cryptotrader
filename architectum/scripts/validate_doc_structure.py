# architectum/scripts/sync_doc_structure.py

import os
import argparse
import shutil
import questionary
from typing import Set

IGNORED_FOLDERS = {"__pycache__", ".git", ".venv", "node_modules", "dist"}


def list_directories(base_path: str) -> Set[str]:
    directories = set()
    for root, dirs, _ in os.walk(base_path):
        for dir_name in dirs:
            if dir_name.startswith(".") or dir_name in IGNORED_FOLDERS:
                continue
            full_dir_path = os.path.join(root, dir_name)
            rel_dir_path = os.path.relpath(full_dir_path, base_path)
            directories.add(rel_dir_path.replace("\\", "/"))
    return directories


def prompt_to_create(missing_dirs: Set[str], doc_src_root: str) -> None:
    if not missing_dirs:
        return

    print("\n📂 Missing folders detected under src/:\n")
    choices = [
        {"name": path, "checked": True}  # Default: checked for creation
        for path in sorted(missing_dirs)
    ]

    selected = questionary.checkbox("Select folders to create:", choices=choices).ask()

    if not selected:
        print("❌ No folders selected for creation.")
        return

    for folder in selected:
        path_to_create = os.path.join(doc_src_root, folder)
        os.makedirs(path_to_create, exist_ok=True)
        print(f"✅ Created: src/{folder}")


def prompt_to_delete(extra_dirs: Set[str], doc_src_root: str) -> None:
    if not extra_dirs:
        return

    print("\n🗑️ Extra folders detected in Architectum src/:\n")
    choices = [
        {"name": path, "checked": False}  # Default: unchecked for deletion
        for path in sorted(extra_dirs)
    ]

    selected = questionary.checkbox("Select folders to delete:", choices=choices).ask()

    if not selected:
        print("❌ No folders selected for deletion.")
        return

    for folder in selected:
        path_to_delete = os.path.join(doc_src_root, folder)
        shutil.rmtree(path_to_delete)
        print(f"✅ Deleted: src/{folder}")


def sync_doc_structure(app_root: str, doc_root: str) -> None:
    app_dirs = list_directories(app_root)

    doc_src_root = os.path.join(doc_root, "src")
    os.makedirs(doc_src_root, exist_ok=True)

    doc_dirs = list_directories(doc_src_root)

    missing_dirs = app_dirs - doc_dirs
    extra_dirs = doc_dirs - app_dirs

    if not missing_dirs and not extra_dirs:
        print("✅ Architectum structure matches src/ structure. No changes needed.")
        return

    prompt_to_create(missing_dirs, doc_src_root)
    prompt_to_delete(extra_dirs, doc_src_root)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Sync Architectum/src/ structure with application src/."
    )
    parser.add_argument(
        "--app-root",
        type=str,
        default=os.path.abspath(
            os.path.join(os.path.dirname(__file__), "../..", "src")
        ),
        help="Path to the application source folder (e.g., src/)",
    )
    parser.add_argument(
        "--doc-root",
        type=str,
        default=os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "..", "project_docs")
        ),
        help="Path to the documentation folder root (e.g., project_docs/)",
    )
    args = parser.parse_args()

    print("🔍 Checking Architectum structure vs src...\n")
    sync_doc_structure(args.app_root, args.doc_root)
