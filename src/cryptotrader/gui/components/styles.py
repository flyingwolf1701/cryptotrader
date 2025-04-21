"""
Application Styles

This module defines color schemes and styles for the CryptoTrader dashboard.
"""

import tkinter as tk
from tkinter import ttk
import tkinter.font as tkfont

# Color definitions
class Colors:
    # Main colors
    BACKGROUND = "#1e1e1e"
    BACKGROUND_LIGHT = "#2d2d30"
    FOREGROUND = "#d4d4d4"
    ACCENT = "#007acc"
    
    # Status colors
    SUCCESS = "#6A8759"  # Green
    WARNING = "#BBB529"  # Yellow
    ERROR = "#FF5555"    # Red
    
    # Trading colors
    BUY = "#6A8759"      # Green
    SELL = "#CF6A4C"     # Red
    NEUTRAL = "#A9B7C6"  # Gray

# Font definitions
class Fonts:
    @staticmethod
    def create_fonts(root):
        """Create font objects for the application.
        
        Args:
            root: The root Tkinter window
        """
        fonts = {}
        fonts['normal'] = tkfont.Font(family="Segoe UI", size=10)
        fonts['bold'] = tkfont.Font(family="Segoe UI", size=10, weight="bold")
        fonts['monospace'] = tkfont.Font(family="Consolas", size=10)
        fonts['small'] = tkfont.Font(family="Segoe UI", size=8)
        fonts['large'] = tkfont.Font(family="Segoe UI", size=12)
        return fonts

def apply_theme(root):
    """Apply a dark theme to the entire application.
    
    Args:
        root: The root Tkinter window
    """
    # Configure the ttk theme
    style = ttk.Style(root)
    
    # Use 'clam' as a base theme to get more control over styling
    style.theme_use('clam')
    
    # Configure main window background
    root.configure(background=Colors.BACKGROUND)
    
    # Configure ttk styles
    style.configure('TFrame', background=Colors.BACKGROUND)
    style.configure('TLabel', background=Colors.BACKGROUND, foreground=Colors.FOREGROUND)
    style.configure('TButton', 
                   background=Colors.BACKGROUND_LIGHT, 
                   foreground=Colors.FOREGROUND,
                   borderwidth=1)
    style.map('TButton',
             background=[('active', Colors.ACCENT), ('pressed', Colors.ACCENT)],
             foreground=[('active', 'white'), ('pressed', 'white')])
    
    style.configure('TNotebook', background=Colors.BACKGROUND)
    style.configure('TNotebook.Tab', 
                   background=Colors.BACKGROUND_LIGHT, 
                   foreground=Colors.FOREGROUND,
                   padding=[10, 2])
    style.map('TNotebook.Tab',
             background=[('selected', Colors.BACKGROUND), ('active', Colors.ACCENT)],
             foreground=[('selected', Colors.FOREGROUND), ('active', 'white')])
    
    style.configure('TCombobox', 
                   background=Colors.BACKGROUND_LIGHT,
                   fieldbackground=Colors.BACKGROUND_LIGHT,
                   foreground=Colors.FOREGROUND,
                   arrowcolor=Colors.FOREGROUND)
    
    style.configure('Vertical.TScrollbar', 
                   background=Colors.BACKGROUND_LIGHT,
                   arrowcolor=Colors.FOREGROUND,
                   troughcolor=Colors.BACKGROUND)
    
    style.configure('Horizontal.TScrollbar', 
                   background=Colors.BACKGROUND_LIGHT,
                   arrowcolor=Colors.FOREGROUND,
                   troughcolor=Colors.BACKGROUND)
    
    style.configure('TPanedwindow', 
                   background=Colors.BACKGROUND,
                   sashwidth=4,
                   sashrelief=tk.RAISED)
    
    # Apply fonts
    fonts = Fonts.create_fonts(root)
    style.configure('TLabel', font=fonts['normal'])
    style.configure('TButton', font=fonts['normal'])
    style.configure('TNotebook.Tab', font=fonts['normal'])
    
    # Return fonts for use in the application
    return fonts

def create_table(parent, columns, height=10, column_widths=None, padding=2):
    """Create a styled table widget (Treeview).
    
    Args:
        parent: Parent widget
        columns: List of column headers
        height: Number of rows to display at once
        column_widths: List of column widths (in pixels)
        padding: Cell padding
    
    Returns:
        Tuple containing (frame, treeview)
    """
    # Create a frame to hold the table and scrollbar
    frame = ttk.Frame(parent)
    
    # Configure treeview style
    style = ttk.Style(parent)
    style.configure("Treeview", 
                   background=Colors.BACKGROUND,
                   foreground=Colors.FOREGROUND,
                   fieldbackground=Colors.BACKGROUND,
                   rowheight=25)
    style.configure("Treeview.Heading", 
                   background=Colors.BACKGROUND_LIGHT,
                   foreground=Colors.FOREGROUND,
                   relief="flat")
    style.map("Treeview.Heading",
             background=[('active', Colors.ACCENT)])
    
    # Create column identifiers
    column_ids = [f"#{i}" for i in range(len(columns))]
    
    # Create the treeview
    treeview = ttk.Treeview(frame, columns=column_ids, show='headings', height=height)
    
    # Set column headings
    for i, col in enumerate(columns):
        treeview.heading(f"#{i}", text=col)
        if column_widths and i < len(column_widths):
            treeview.column(f"#{i}", width=column_widths[i], stretch=True, anchor=tk.CENTER)
        else:
            # Default width if not specified
            treeview.column(f"#{i}", width=100, stretch=True, anchor=tk.CENTER)
    
    # Create scrollbar
    scrollbar = ttk.Scrollbar(frame, orient="vertical", command=treeview.yview)
    treeview.configure(yscrollcommand=scrollbar.set)
    
    # Pack widgets
    treeview.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    return frame, treeview

def create_button(parent, text, command=None, width=None, style=None):
    """Create a styled button widget.
    
    Args:
        parent: Parent widget
        text: Button text
        command: Button command
        width: Button width
        style: Optional button style (e.g., 'success', 'danger')
    
    Returns:
        Button widget
    """
    button = ttk.Button(parent, text=text, command=command, width=width)
    
    if style == 'success':
        custom_style = ttk.Style(parent)
        custom_style.configure('Success.TButton', background=Colors.SUCCESS)
        custom_style.map('Success.TButton',
                        background=[('active', Colors.SUCCESS), ('pressed', Colors.SUCCESS)])
        button.configure(style='Success.TButton')
    elif style == 'danger':
        custom_style = ttk.Style(parent)
        custom_style.configure('Danger.TButton', background=Colors.ERROR)
        custom_style.map('Danger.TButton',
                        background=[('active', Colors.ERROR), ('pressed', Colors.ERROR)])
        button.configure(style='Danger.TButton')
    
    return button