# scripts/set_sys_path.py

import os
import sys
import functools

def fix_imports():
    """
    Manually adjust sys.path to include project root.
    Call this at the top of standalone scripts if needed.
    """
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

def set_project_sys_path():
    """
    For decorator use inside scripts to recheck sys.path at runtime.
    """
    fix_imports()

def set_sys_path(func):
    """
    Decorator to guarantee sys.path is set before function execution.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        set_project_sys_path()
        return func(*args, **kwargs)
    return wrapper
