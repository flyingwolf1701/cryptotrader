import os
import argparse
import shutil
import questionary
from typing import Set, Tuple
from colorama import init, Fore, Style

# Initialize colorama
init(autoreset=True)

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


def calculate_drift(app_root: str, doc_root: str) -> Tuple[Set[str], Set[str]]:
    app_dirs = list_directories(app_root)
    doc_src_root = os.path.join(doc_root, "src")
    os.makedirs(doc_src_root, exist_ok=True)
    doc_dirs = list_directories(doc_src_root)
    missing_dirs = app_dirs - doc_dirs
    extra_dirs = doc_dirs - app_dirs
    return missing_dirs, extra_dirs


def prompt_create_missing(missing_dirs: Set[str], doc_src_root: str) -> None:
    if not missing_dirs:
        return

    print(f"\nFound {len(missing_dirs)} missing folders:\n")

    choices = [{"name": path, "checked": False} for path in sorted(missing_dirs)]

    selected = questionary.checkbox("Select folders to create:", choices=choices).ask()

    if not selected:
        print("❌ No folders selected for creation.")
        return

    for folder in selected:
        path_to_create = os.path.join(doc_src_root, folder)
        os.makedirs(path_to_create, exist_ok=True)
        print(f"✅ Created: src/{folder}")


def prompt_delete_extras(extra_dirs: Set[str], doc_src_root: str) -> None:
    if not extra_dirs:
        return

    print(
        f"\n{Fore.YELLOW + Style.BRIGHT}⚠️ Architectum src/ structure drift detected! {len(extra_dirs)} unexpected folders!{Style.RESET_ALL}\n"
    )

    choices = [{"name": path, "checked": False} for path in sorted(extra_dirs)]

    selected = questionary.checkbox(
        "(Select folders to delete):", choices=choices
    ).ask()

    if not selected:
        print("❌ No folders selected for deletion.")
        return

    confirm = questionary.confirm(
        f"⚠️ Are you sure you want to delete {len(selected)} folder(s)?"
    ).ask()

    if not confirm:
        print("🚫 Deletion cancelled.")
        return

    for folder in selected:
        path_to_delete = os.path.join(doc_src_root, folder)
        shutil.rmtree(path_to_delete)
        print(f"✅ Deleted: src/{folder}")


def main():
    parser = argparse.ArgumentParser(
        description="Check and optionally sync Architectum/src/ with application src/."
    )
    parser.add_argument(
        "--app-root",
        type=str,
        default=os.path.abspath(
            os.path.join(os.path.dirname(__file__), "../..", "src")
        ),
        help="Path to the real application src/ folder",
    )
    parser.add_argument(
        "--doc-root",
        type=str,
        default=os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "..", "architectum")
        ),
        help="Path to the Architectum documentation root (architectum/)",
    )
    args = parser.parse_args()

    app_src_root = args.app_root
    doc_root = args.doc_root
    doc_src_root = os.path.join(doc_root, "src")

    print("🔍 Checking Architectum src/ structure vs real src/...\n")

    missing_dirs, extra_dirs = calculate_drift(app_src_root, doc_root)

    if not missing_dirs and not extra_dirs:
        print("✅ Architectum structure matches src/. No changes needed.")
        return

    if missing_dirs:
        prompt_create_missing(missing_dirs, doc_src_root)

    if extra_dirs:
        prompt_delete_extras(extra_dirs, doc_src_root)


if __name__ == "__main__":
    main()
