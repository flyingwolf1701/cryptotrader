# file: architectum/scripts/sync_folder_structure.py

import argparse
import shutil
from pathlib import Path
from typing import Dict, List, Set, Tuple

import questionary
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)

IGNORED_FOLDERS = {"__pycache__", ".git", ".venv", "node_modules", "dist"}

def build_folder_map(root: Path) -> Dict[str, List[str]]:
    """
    Build a map of folders: {relative_path: [list of subfolders]}.
    Files are completely ignored.
    """
    folder_map: Dict[str, List[str]] = {}

    for path in root.glob("**/*"):
        if path.is_dir() and not any(part in IGNORED_FOLDERS for part in path.parts):
            rel_path = path.relative_to(root).as_posix()
            parent_rel_path = path.parent.relative_to(root).as_posix() if path.parent != root else ""
            folder_map.setdefault(parent_rel_path, []).append(path.name)

    return {k: sorted(v) for k, v in folder_map.items()}

def compare_folder_maps(app_map: Dict[str, List[str]], doc_map: Dict[str, List[str]]) -> Tuple[Set[str], Set[str]]:
    """
    Compare two folder maps.
    Return missing paths (in app, not in docs) and extra paths (in docs, not in app).
    """
    app_paths = set()
    for parent, children in app_map.items():
        for child in children:
            app_paths.add(f"{parent}/{child}" if parent else child)

    doc_paths = set()
    for parent, children in doc_map.items():
        for child in children:
            doc_paths.add(f"{parent}/{child}" if parent else child)

    return app_paths - doc_paths, doc_paths - app_paths

def prompt_create_missing(missing_dirs: Set[str], doc_src_root: Path) -> None:
    if not missing_dirs:
        return

    print(f"\nFound {len(missing_dirs)} missing folders:\n")
    choices = [{"name": path, "checked": False} for path in sorted(missing_dirs)]
    selected = questionary.checkbox("Select folders to create:", choices=choices).ask()

    if not selected:
        print("❌ No folders selected for creation.")
        return

    for folder in selected:
        path_to_create = doc_src_root / folder
        path_to_create.mkdir(parents=True, exist_ok=True)
        print(f"✅ Created: src/{folder}")

def prompt_delete_extras(extra_dirs: Set[str], doc_src_root: Path) -> None:
    if not extra_dirs:
        return

    print(
        f"\n{Fore.YELLOW + Style.BRIGHT}⚠️ Architectum src/ structure drift detected! {len(extra_dirs)} unexpected folders!{Style.RESET_ALL}\n"
    )

    choices = [{"name": path, "checked": False} for path in sorted(extra_dirs)]
    selected = questionary.checkbox("(Select folders to delete):", choices=choices).ask()

    if not selected:
        print("❌ No folders selected for deletion.")
        return

    confirm = questionary.confirm(f"⚠️ Are you sure you want to delete {len(selected)} folder(s)?").ask()
    if not confirm:
        print("🚫 Deletion cancelled.")
        return

    for folder in selected:
        path_to_delete = doc_src_root / folder
        if path_to_delete.exists():
            shutil.rmtree(path_to_delete)
            print(f"✅ Deleted: src/{folder}")

def main():
    parser = argparse.ArgumentParser(
        description="Sync Architectum/src/ structure with application src/."
    )
    parser.add_argument(
        "--app-root",
        type=str,
        default=str(Path(__file__).resolve().parent.parent.parent / "src"),
        help="Path to the real application src/ folder",
    )
    parser.add_argument(
        "--doc-root",
        type=str,
        default=str(Path(__file__).resolve().parent.parent),
        help="Path to the Architectum documentation root (architectum/)",
    )
    args = parser.parse_args()

    app_src_root = Path(args.app_root)
    doc_root = Path(args.doc_root)
    doc_src_root = doc_root / "src"

    print("🔍 Checking Architectum src/ structure vs real src/...\n")

    app_map = build_folder_map(app_src_root)
    doc_map = build_folder_map(doc_src_root)

    missing_dirs, extra_dirs = compare_folder_maps(app_map, doc_map)

    if not missing_dirs and not extra_dirs:
        print("✅ Architectum structure matches src/. No changes needed.")
        return

    if missing_dirs:
        prompt_create_missing(missing_dirs, doc_src_root)

    if extra_dirs:
        prompt_delete_extras(extra_dirs, doc_src_root)

if __name__ == "__main__":
    main()
