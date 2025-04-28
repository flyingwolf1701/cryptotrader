import tkinter as tk
from src.gui.components.ui.logging_widget import LoggingWidget

def main():
    root = tk.Tk()
    root.title("Logging Widget Demo")
    root.geometry("800x600")

    logging_widget = LoggingWidget(root)
    logging_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    # Add some mock logs
    logging_widget.add_log("System started successfully.", "SUCCESS")
    logging_widget.add_log("Warning: High memory usage detected.", "WARNING")
    logging_widget.add_log("Error: Failed to connect to server.", "ERROR")

    root.mainloop()

if __name__ == "__main__":
    main()
