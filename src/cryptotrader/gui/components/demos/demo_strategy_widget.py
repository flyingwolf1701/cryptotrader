import tkinter as tk
from cryptotrader.gui.components.ui.strategy_widget import StrategyWidget

def main():
    root = tk.Tk()
    root.title("Strategy Widget Demo")
    root.geometry("1000x700")

    strategy_widget = StrategyWidget(root)
    strategy_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    root.mainloop()

if __name__ == "__main__":
    main()
