# file: architectum/scripts/script_manager.py

import subprocess
import sys
import os

SCRIPTS = [
    "file_structure_to_md.py",
    "sync_folder_structure.py",
]

def run_script(script_name: str) -> None:
    script_path = os.path.join(os.path.dirname(__file__), script_name)
    print(f"▶️ Running {script_name}...")
    result = subprocess.run([sys.executable, script_path])

    if result.returncode == 0:
        print(f"✅ {script_name} completed successfully!\n")
    else:
        print(f"❌ {script_name} failed with exit code {result.returncode}.\n")
        sys.exit(result.returncode)


def main():
    for script in SCRIPTS:
        run_script(script)


if __name__ == "__main__":
    main()
