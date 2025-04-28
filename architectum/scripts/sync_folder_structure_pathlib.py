# file: architectum/scripts/sync_folder_structure_pathlib.py

import argparse
import shutil
import questionary
import sys
from pathlib import Path
from typing import Set, Tuple
from colorama import init, Fore, Style

# Initialize colorama
init(autoreset=True)

# Define names of folders to ignore anywhere in the path
IGNORED_FOLDER_NAMES = {"__pycache__", ".git", ".venv", "node_modules", "dist"}

def get_relative_dirs(base_path: Path) -> Set[str]:
    """
    Collect relative paths of all non-ignored directories under base_path.
    Uses pathlib for iteration and filtering.
    Ignores files completely.
    """
    if not base_path.is_dir():
        print(f"{Fore.YELLOW}Warning: Base path {base_path} not found or is not a directory.{Style.RESET_ALL}")
        return set()

    directories = set()
    # Recursively find all items (files and dirs)
    for item_path in base_path.rglob('*'):
        # --- Step 1: Keep only directories ---
        if not item_path.is_dir():
            continue # Skip files

        # --- Step 2: Check if any part of the path should be ignored ---
        try:
            relative_path_obj = item_path.relative_to(base_path)
            ignore_this = False
            # Check each component of the relative path
            for part in relative_path_obj.parts:
                if part.startswith('.') or part in IGNORED_FOLDER_NAMES:
                    ignore_this = True
                    break # No need to check further parts
            if ignore_this:
                continue # Skip this directory

            # --- Step 3: Store the valid relative path string (using as_posix) ---
            dir_path_str = relative_path_obj.as_posix()

            directories.add(dir_path_str)

        except ValueError:
            # Should generally not happen if item_path is from rglob under base_path
            print(f"{Fore.YELLOW}Warning: Could not get relative path for {item_path}{Style.RESET_ALL}")
            continue

    return directories

def calculate_drift(app_root_path: Path, doc_root_path: Path) -> Tuple[Set[str], Set[str]]:
    """
    Compare directory structures using sets of relative paths from pathlib.
    """
    print(f"Comparing:\n  App Source: {app_root_path}\n  Doc Source: {doc_root_path / 'src'}")

    app_dirs = get_relative_dirs(app_root_path)
    # Ensure the architectum/src directory exists before walking it
    doc_src_root_path = doc_root_path / "src"
    doc_src_root_path.mkdir(parents=True, exist_ok=True)
    doc_dirs = get_relative_dirs(doc_src_root_path)

    print(f"\nFound {len(app_dirs)} relevant directories in App Source.")
    print(f"Found {len(doc_dirs)} relevant directories in Doc Source.")

    missing_dirs = app_dirs - doc_dirs
    extra_dirs = doc_dirs - app_dirs
    return missing_dirs, extra_dirs

def prompt_create_missing(missing_dirs: Set[str], doc_src_root_path: Path) -> None:
    if not missing_dirs:
        return

    print(f"\nFound {len(missing_dirs)} missing folders in '{doc_src_root_path.name}/':\n")

    choices = [{"name": f"src/{path}", "checked": False} for path in sorted(missing_dirs)]

    selected_display_names = questionary.checkbox("Select folders to create:", choices=choices).ask()

    if not selected_display_names:
        print("❌ No folders selected for creation.")
        return

    # Extract relative paths from the display names
    selected_relative_paths = [name.replace("src/", "", 1) for name in selected_display_names]

    created_count = 0
    for folder_rel_str in selected_relative_paths:
        # Use pathlib's / operator to join paths
        path_to_create = doc_src_root_path / folder_rel_str
        try:
            # Create directory and any necessary parents; doesn't error if it exists
            path_to_create.mkdir(parents=True, exist_ok=True)
            print(f"✅ Created: src/{folder_rel_str}")
            created_count += 1
        except OSError as e:
             print(f"❌ Error creating src/{folder_rel_str}: {e}")
    print(f"\nCreated {created_count} folder(s).")


def prompt_delete_extras(extra_dirs: Set[str], doc_src_root_path: Path) -> None:
    if not extra_dirs:
        return

    print(
        f"\n{Fore.YELLOW + Style.BRIGHT}⚠️ Architectum src/ structure drift detected! {len(extra_dirs)} unexpected folders!{Style.RESET_ALL}\n"
    )

    choices = [{"name": f"src/{path}", "checked": False} for path in sorted(extra_dirs)]

    selected_display_names = questionary.checkbox(
        "(Select folders to delete):", choices=choices
    ).ask()

    if not selected_display_names:
        print("❌ No folders selected for deletion.")
        return

    # Extract relative paths from the display names
    selected_relative_paths = [name.replace("src/", "", 1) for name in selected_display_names]

    confirm = questionary.confirm(
        f"⚠️ Are you sure you want to delete {len(selected_relative_paths)} folder(s) and ALL their contents from '{doc_src_root_path.name}/'?"
    ).ask()

    if not confirm:
        print("🚫 Deletion cancelled.")
        return

    deleted_count = 0
    for folder_rel_str in selected_relative_paths:
        path_to_delete = doc_src_root_path / folder_rel_str
        try:
            # Verify it exists and is a directory before attempting deletion
            if path_to_delete.is_dir():
                 shutil.rmtree(path_to_delete) # shutil works fine with Path objects
                 print(f"✅ Deleted: src/{folder_rel_str}")
                 deleted_count += 1
            elif path_to_delete.exists():
                 # This shouldn't happen if get_relative_dirs works correctly
                 print(f"⚠️ Skipped deletion: src/{folder_rel_str} exists but is not a directory.")
            else:
                 print(f"⚠️ Skipped deletion: src/{folder_rel_str} no longer exists.")
        except OSError as e:
            print(f"❌ Error deleting src/{folder_rel_str}: {e}")
    print(f"\nDeleted {deleted_count} folder(s).")


def main():
    parser = argparse.ArgumentParser(
        description="Check and sync Architectum/src/ directory structure with application src/ using pathlib."
    )
    # Get script's directory using pathlib
    script_dir = Path(__file__).parent.resolve()

    # Default app_root calculation assumes script is in architectum/scripts/
    # Adjust if script location is different
    default_app_root = (script_dir / ".." / ".." / "src").resolve()

    # Default doc_root calculation assumes architectum is sibling to src's parent
    # i.e. project_root/src and project_root/architectum
    default_doc_root = (script_dir / "..").resolve() # This should be the architectum directory

    parser.add_argument(
        "--app-root",
        type=Path, # Use Path type directly
        default=default_app_root,
        help=f"Path to the real application src/ folder (default: {default_app_root})",
    )
    parser.add_argument(
        "--doc-root",
        type=Path, # Use Path type directly
        default=default_doc_root,
        help=f"Path to the Architectum documentation root (containing architectum/src/) (default: {default_doc_root})",
    )
    args = parser.parse_args()

    app_src_root_path: Path = args.app_root.resolve() # Ensure absolute path
    doc_root_path: Path = args.doc_root.resolve()     # Ensure absolute path
    doc_src_root_path: Path = doc_root_path / "src"

    # Validate input paths
    if not app_src_root_path.is_dir():
        print(f"{Fore.RED}Error: Application source directory not found or not a directory: {app_src_root_path}{Style.RESET_ALL}")
        sys.exit(1)
    # Check doc_root path exists, though src subdir will be created if needed
    if not doc_root_path.is_dir():
         print(f"{Fore.YELLOW}Warning: Documentation root directory not found: {doc_root_path}{Style.RESET_ALL}")
         # Allow script to continue, it will create architectum/src if needed


    print(f"🔍 Checking Architectum structure ('{doc_src_root_path.relative_to(doc_root_path.parent)}/') vs real source ('{app_src_root_path.relative_to(app_src_root_path.parent)}/')...\n")

    missing_dirs, extra_dirs = calculate_drift(app_src_root_path, doc_root_path)

    if not missing_dirs and not extra_dirs:
        print(f"✅ Architectum structure ('{doc_src_root_path.name}/') matches source ('{app_src_root_path.name}/'). No changes needed.")
        return

    if missing_dirs:
        prompt_create_missing(missing_dirs, doc_src_root_path)

    if extra_dirs:
        prompt_delete_extras(extra_dirs, doc_src_root_path)

    print("\n✨ Sync check complete.")

if __name__ == "__main__":
    main()