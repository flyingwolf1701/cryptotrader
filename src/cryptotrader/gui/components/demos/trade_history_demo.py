import os
import argparse
import questionary

EXTENSIONS = [".yaml", ".json", ".md"]


def create_files(base_doc_path: str, relative_path: str, selected_exts: list):
    # Check if path is to a file or folder
    if relative_path.endswith(".py"):
        folder_path = os.path.join(base_doc_path, os.path.dirname(relative_path))
        base_name = os.path.splitext(os.path.basename(relative_path))[0]
    else:
        folder_path = os.path.join(base_doc_path, relative_path)
        base_name = os.path.basename(relative_path)

    os.makedirs(folder_path, exist_ok=True)

    for ext in selected_exts:
        file_name = f"{base_name}{ext}"
        file_path = os.path.join(folder_path, file_name)
        if not os.path.exists(file_path):
            with open(file_path, "w", encoding="utf-8") as f:
                pass  # Create an empty file
            rel_path = os.path.relpath(file_path, base_doc_path).replace("\\", "/")
            print(f"✅ Created: architectum/src/{rel_path}")
        else:
            rel_path = os.path.relpath(file_path, base_doc_path).replace("\\", "/")
            print(f"⚠️ Already exists: architectum/src/{rel_path}")


def main():
    parser = argparse.ArgumentParser(description="Create empty Architectum .yaml, .json, .md files.")
    parser.add_argument(
        "--doc-root",
        type=str,
        default=os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")),
        help="Path to the architectum/src folder."
    )
    parser.add_argument(
        "--app-root",
        type=str,
        default=os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "src")),
        help="Path to the real application src folder."
    )
    args = parser.parse_args()

    while True:
        relative_path = questionary.text("Paste the relative path (e.g., utils/helpers or utils/helpers/file.py):").ask().strip()

        if not relative_path:
            print("❌ No path provided. Exiting.")
            return

        relative_path = relative_path.replace("\\", "/")  # Normalize slashes for Windows

        # Remove leading 'src/' if present
        if relative_path.startswith("src/"):
            relative_path = relative_path[4:]

        full_app_path = os.path.join(args.app_root, relative_path)
        if not os.path.exists(full_app_path):
            retry = questionary.confirm("❌ Path does not exist in application src/... Would you like to try again?").ask()
            if not retry:
                print("❌ Exiting.")
                return
            continue

        break

    file_choices = [
        {"name": ext, "checked": False} for ext in EXTENSIONS
    ]

    selected = questionary.checkbox(
        "Select file types to create:",
        choices=file_choices
    ).ask()

    if not selected:
        print("❌ No file types selected. Exiting.")
        return

    create_files(args.doc_root, relative_path, selected)


if __name__ == "__main__":
    main()
