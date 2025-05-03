# architectum/scripts/sync_folder_structure.py

import argparse
import shutil
from pathlib import Path
from typing import Dict, List, Set, Tuple

import questionary
from colorama import init, Fore, Style

init(autoreset=True)
IGNORED = {"__pycache__", ".git", ".venv", "node_modules", "dist"}


def build_map(root: Path) -> Dict[str, List[str]]:
    m: Dict[str, List[str]] = {}
    for d in sorted(root.rglob("*")):
        if d.is_dir() and d.name not in IGNORED:
            rel = d.relative_to(root).as_posix()
            subs = [
                c.name
                for c in sorted(d.iterdir())
                if c.is_dir() and c.name not in IGNORED
            ]
            m[rel] = subs
    return m


def compare(a: Set[str], b: Set[str]) -> Tuple[Set[str], Set[str]]:
    return a - b, b - a  # missing_in_b, extra_in_b


def prompt_checkbox(action: str, items: Set[str]) -> List[str]:
    if not items:
        return []
    return questionary.checkbox(f"Select folders to {action}:", choices=sorted(items)).ask() or []


def main():
    cwd = Path.cwd()
    default_app = cwd / "src" / "cryptotrader"
    default_doc = cwd / "src" / "architectum" / "cryptotrader_specs"

    p = argparse.ArgumentParser(description="Sync specs ↔ code folders")
    p.add_argument(
        "--app-dir",
        type=Path,
        default=default_app,
        help="Code folder (e.g. src/cryptotrader)",
    )
    p.add_argument(
        "--doc-dir",
        type=Path,
        default=default_doc,
        help="Specs folder (e.g. src/architectum/cryptotrader_specs)",
    )
    args = p.parse_args()

    app_map = build_map(args.app_dir)
    doc_map = build_map(args.doc_dir)
    missing, extra = compare(set(app_map), set(doc_map))

    if not missing and not extra:
        print("✅ In sync—no changes needed.")
        return

    for rel in prompt_checkbox("create in specs", missing):
        (args.doc_dir / rel).mkdir(parents=True, exist_ok=True)
        print(f"{Fore.GREEN}✅ Created:{Style.RESET_ALL} {rel}")

    for rel in prompt_checkbox("delete from specs", extra):
        shutil.rmtree(args.doc_dir / rel)
        print(f"{Fore.RED}❌ Deleted:{Style.RESET_ALL} {rel}")


if __name__ == "__main__":
    main()
