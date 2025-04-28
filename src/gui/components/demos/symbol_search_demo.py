# File: src/gui/components/demos/symbol_search_demo.py
"""Demo runner for SymbolSearchWidget with path hack for direct execution."""
import sys
from pathlib import Path

# ─── Adjust module search path so "src" package is visible ─────────────────────────
project_root = Path(__file__).resolve().parents[4]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
# Also add the 'src' directory itself so modules importing 'services' resolve correctly
src_path = project_root / 'src'
if src_path.exists() and str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))
# ───────────────────────────────────────────────────────────────────────────────

import tkinter as tk
from src.gui.components.ui.symbol_search_widget import SymbolSearchWidget


def main():
    root = tk.Tk()
    root.title("Symbol Search Demo")
    # Set a minimum window size so dropdown is fully visible
    root.geometry("400x200")  # width x height


    widget = SymbolSearchWidget(
        root,
        on_select=lambda s: print("Selected:", s),
        on_add=lambda s: print("Added:", s)
    )
    widget.pack(padx=10, pady=10, fill='x')

    root.mainloop()


if __name__ == "__main__":
    main()
