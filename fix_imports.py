# fix_imports.py
"""
A script to fix import issues in the CryptoTrader project.
Run this from the project root directory.
"""

import os
import sys
from pathlib import Path

def fix_imports():
    """Fix import issues by modifying the import statements in Python files."""
    # Add project root to Python path
    project_root = Path.cwd()
    sys.path.insert(0, str(project_root))
    print(f"Added {project_root} to Python path")
    
    # Files to modify
    files_to_modify = [
        "src/gui/components/watchlist.py",
        "src/gui/components/logging_panel.py",
        "src/gui/components/strategy_panel.py",
        "src/gui/components/trades_component.py",
        "src/gui/components/chart_widget.py",
        "src/gui/main_window.py",
    ]
    
    for file_path in files_to_modify:
        abs_path = project_root / file_path
        if not abs_path.exists():
            print(f"Warning: File not found: {abs_path}")
            continue
        
        # Read the file
        with open(abs_path, 'r') as f:
            content = f.read()
        
        # Check if the file already has the import fix
        if "__file__" in content and "sys.path.insert" in content:
            print(f"File already modified: {file_path}")
            continue
        
        # Add the import fix at the beginning of the file after the imports
        import_fix = """
# Fix import path
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))  # Add project root to Python path
"""
        
        # Find the first non-comment, non-import line
        lines = content.split('\n')
        insert_idx = 0
        
        for i, line in enumerate(lines):
            line = line.strip()
            if line and not line.startswith('#') and not line.startswith('"""') and not line.startswith("'''"):
                if not (line.startswith('import ') or line.startswith('from ')):
                    insert_idx = i
                    break
                if i > insert_idx:
                    insert_idx = i + 1
        
        # Insert the import fix
        lines.insert(insert_idx, import_fix)
        
        # Write the file back
        with open(abs_path, 'w') as f:
            f.write('\n'.join(lines))
        
        print(f"Modified: {file_path}")
    
    # Check config/__init__.py
    config_init_path = project_root / "src" / "config" / "__init__.py"
    if config_init_path.exists():
        with open(config_init_path, 'r') as f:
            content = f.read()
        
        # Check if get_logger is correctly imported
        if "from .logging import get_logger" not in content or "get_logger" not in content:
            with open(config_init_path, 'w') as f:
                if "from .secrets import Secrets" in content:
                    content = content.replace("from .secrets import Secrets", "from .secrets import Secrets\nfrom .logging import get_logger")
                    if "__all__" in content:
                        content = content.replace("__all__ = ['Secrets']", "__all__ = ['Secrets', 'get_logger']")
                    else:
                        content += "\n\n__all__ = ['Secrets', 'get_logger']"
                else:
                    content += "\nfrom .secrets import Secrets\nfrom .logging import get_logger\n\n__all__ = ['Secrets', 'get_logger']"
                
                f.write(content)
            print(f"Fixed config/__init__.py to properly export get_logger")
        else:
            print(f"config/__init__.py already correctly exports get_logger")

    # Create a batch/shell script to run the app correctly
    if os.name == 'nt':  # Windows
        run_script = project_root / "run_cryptotrader.bat"
        with open(run_script, 'w') as f:
            f.write('@echo off\n')
            f.write('set PYTHONPATH=%PYTHONPATH%;%CD%\n')
            f.write('python src/main.py\n')
        print(f"Created Windows batch file: {run_script}")
    else:  # Unix/Mac
        run_script = project_root / "run_cryptotrader.sh"
        with open(run_script, 'w') as f:
            f.write('#!/bin/bash\n')
            f.write('export PYTHONPATH=$PYTHONPATH:$(pwd)\n')
            f.write('python3 src/main.py\n')
        # Make the script executable
        os.chmod(run_script, 0o755)
        print(f"Created Unix shell script: {run_script}")
    
    print("\nImport issues fixed! You can now run components individually or use the run script.")
    print("To run the application: ")
    if os.name == 'nt':
        print("    run_cryptotrader.bat")
    else:
        print("    ./run_cryptotrader.sh")

if __name__ == "__main__":
    fix_imports()