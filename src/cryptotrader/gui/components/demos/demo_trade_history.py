import tkinter as tk
from cryptotrader.gui.components.ui.trade_history_widget import TradeHistoryWidget

def main():
    root = tk.Tk()
    root.title("Trade History Demo")
    root.geometry("800x600")

    trade_history = TradeHistoryWidget(root)
    trade_history.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    root.mainloop()

if __name__ == "__main__":
    main()
