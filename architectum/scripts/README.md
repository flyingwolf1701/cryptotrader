# Archetectum Scripts

This folder contains utility scripts for managing and documenting the Archetectum project.

---

## 📜 file_structure_to_md.py

Generates a Markdown file showing the full directory structure of the project, starting from the project root.

### ✨ Features

- Ignores hidden files and common junk folders (`__pycache__`, `.git`, `.venv`, `node_modules`, `dist`)
- Correctly indents and formats the structure tree
- Supports optional `--output` flag to specify the Markdown output path
- Supports optional `--depth` flag to limit recursion depth
- UTF-8 encoded output

### ⚙️ Usage

```bash
python architectum/scripts/file_structure_to_md.py
```
