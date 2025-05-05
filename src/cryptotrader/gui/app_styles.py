# Application Styles
# Updated for a cohesive dark theme across frames, labels, buttons, scrollbars, and notebook tabs.

import tkinter as tk
from tkinter import ttk
import tkinter.font as tkfont
from typing import Dict, List, Optional, Tuple


class Colors:
    """Centralized color definitions."""
    BACKGROUND = "#1e1e1e"
    BACKGROUND_LIGHT = "#2d2d30"
    FOREGROUND = "#e1e1e1"
    FOREGROUND_SECOND = "#a1a1a1"
    ACCENT = "#0a84ff"
    SUCCESS = "#28a745"
    ERROR = "#dc3545"
    BUY = "#00ff00"
    SELL = "#ff0000"


class StyleNames:
    """Constants for style names to avoid typos."""
    SUCCESS_BUTTON = 'Success.TButton'
    DANGER_BUTTON = 'Danger.TButton'


def apply_theme(root: tk.Tk) -> Dict[str, tkfont.Font]:
    """
    Apply the dark CLAM theme and register custom styles.

    This ensures ttk components respect the dark palette.

    Args:
        root: The root Tkinter window

    Returns:
        A dict of tkfont.Font instances for use in widgets.
    """
    # Prepare fonts
    fonts: Dict[str, tkfont.Font] = {
        'normal':    tkfont.Font(root, family='Segoe UI', size=10),
        'bold':      tkfont.Font(root, family='Segoe UI', size=10, weight='bold'),
        'monospace': tkfont.Font(root, family='Consolas',   size=10),
        'small':     tkfont.Font(root, family='Segoe UI', size=8),
        'large':     tkfont.Font(root, family='Segoe UI', size=12),
    }

    # Set window background
    root.configure(bg=Colors.BACKGROUND)

    # Use a theme that allows styling (clam or alt)
    style = ttk.Style(root)
    style.theme_use('clam')

    # Frame background
    style.configure('TFrame', background=Colors.BACKGROUND)
    style.configure('TLabelframe', background=Colors.BACKGROUND)

    # Notebook backgrounds
    style.configure('TNotebook', background=Colors.BACKGROUND, borderwidth=0)
    style.configure('TNotebook.Tab',
                    background=Colors.BACKGROUND_LIGHT,
                    foreground=Colors.FOREGROUND,
                    padding=(10, 5),
                    font=fonts['normal'])
    style.map('TNotebook.Tab',
              background=[('selected', Colors.ACCENT)],
              foreground=[('selected', Colors.FOREGROUND)])

    # Label and Button default fonts/colors
    common = ['TLabel', 'TButton']
    for widget in common:
        style.configure(widget,
                        background=Colors.BACKGROUND,
                        foreground=Colors.FOREGROUND,
                        font=fonts['normal'],
                        borderwidth=0)

    # Button styles
    style.configure(StyleNames.SUCCESS_BUTTON,
                    background=Colors.SUCCESS,
                    foreground=Colors.FOREGROUND)
    style.map(StyleNames.SUCCESS_BUTTON,
              background=[('active', Colors.ACCENT), ('pressed', Colors.SUCCESS)])

    style.configure(StyleNames.DANGER_BUTTON,
                    background=Colors.ERROR,
                    foreground=Colors.FOREGROUND)
    style.map(StyleNames.DANGER_BUTTON,
              background=[('active', Colors.ERROR), ('pressed', Colors.ERROR)])

    # Treeview styling
    style.configure('Treeview',
                    background=Colors.BACKGROUND,
                    foreground=Colors.FOREGROUND,
                    fieldbackground=Colors.BACKGROUND,
                    rowheight=24,
                    font=fonts['normal'])
    style.configure('Treeview.Heading',
                    background=Colors.BACKGROUND_LIGHT,
                    foreground=Colors.FOREGROUND,
                    font=fonts['bold'],
                    relief='flat')
    style.map('Treeview.Heading',
              background=[('active', Colors.ACCENT)])

    # Scrollbar styling
    style.configure('Vertical.TScrollbar',
                    background=Colors.BACKGROUND_LIGHT,
                    troughcolor=Colors.BACKGROUND,
                    arrowcolor=Colors.FOREGROUND)
    style.configure('Horizontal.TScrollbar',
                    background=Colors.BACKGROUND_LIGHT,
                    troughcolor=Colors.BACKGROUND,
                    arrowcolor=Colors.FOREGROUND)

    return fonts


def create_table(parent: tk.Widget,
                 columns: List[str],
                 height: int = 10,
                 column_widths: Optional[List[int]] = None,
                 padding: int = 2
                 ) -> Tuple[ttk.Frame, ttk.Treeview]:
    """
    Create a styled Treeview inside a dark-themed frame.
    """
    frame = ttk.Frame(parent)
    tree = ttk.Treeview(frame, columns=columns, show='headings', height=height)

    # Configure headings and columns
    for idx, label in enumerate(columns):
        tree.heading(label, text=label)
        width = column_widths[idx] if column_widths and idx < len(column_widths) else 100
        tree.column(label, width=width, anchor=tk.CENTER)

    # Scrollbar
    vsb = ttk.Scrollbar(frame, orient='vertical', command=tree.yview, style='Vertical.TScrollbar')
    hsb = ttk.Scrollbar(frame, orient='horizontal', command=tree.xview, style='Horizontal.TScrollbar')
    tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

    # Layout
    tree.grid(row=0, column=0, sticky='nsew', padx=padding, pady=padding)
    vsb.grid(row=0, column=1, sticky='ns')
    hsb.grid(row=1, column=0, sticky='ew')
    frame.grid_rowconfigure(0, weight=1)
    frame.grid_columnconfigure(0, weight=1)

    return frame, tree


def create_button(parent: tk.Widget,
                  text: str,
                  command: Optional[callable] = None,
                  width: Optional[int] = None,
                  style_name: Optional[str] = None
                  ) -> ttk.Button:
    """
    Create a styled button, defaulting to standard foreground/bg.
    """
    btn = ttk.Button(parent, text=text, command=command, style=style_name)
    if width:
        btn.config(width=width)
    return btn
