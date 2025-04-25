# run_component.py (place in project root)
import sys
import os
from pathlib import Path

# Add the project directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import and run a component
if __name__ == "__main__":
    component_name = sys.argv[1] if len(sys.argv) > 1 else "watchlist"
    
    if component_name == "watchlist":
        from src.gui.components.watchlist import WatchlistWidget
        WatchlistWidget.demo()
    # Add other components as needed