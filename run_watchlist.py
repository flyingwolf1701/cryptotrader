# run_watchlist.py (place in project root)
import sys
import os
from pathlib import Path

# Add the project directory to Python path
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

# Now run the original script with the proper path set up
file_to_run = project_root / "src" / "gui" / "components" / "watchlist.py"
with open(file_to_run) as f:
    exec(f.read())