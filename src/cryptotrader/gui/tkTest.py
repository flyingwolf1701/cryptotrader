import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.patches import Rectangle
import datetime as dt

# Sample OHLC data
candlestick_data = [
    (1, 30000, 30500, 29900, 30600),
    (2, 30500, 30300, 30200, 30800),
    (3, 30300, 30700, 30100, 30900),
    (4, 30700, 30600, 30500, 31000),
    (5, 30600, 30800, 30400, 31100),
]

# Create a real date x-axis
base_date = dt.datetime.today()
dates = [base_date + dt.timedelta(days=i) for i in range(len(candlestick_data))]

# Start GUI
root = tk.Tk()
root.title("Crypto Candlestick Chart (Tkinter)")
root.geometry("800x400")

fig, ax = plt.subplots(figsize=(8, 4))
ax.set_title("BTC/USD Candlestick")

for i, (time, o, c, l, h) in enumerate(candlestick_data):
    color = 'green' if c >= o else 'red'
    # Wick
    ax.plot([dates[i], dates[i]], [l, h], color='black', linewidth=1)
    # Body
    rect = Rectangle(
        (dates[i] - dt.timedelta(hours=6), min(o, c)),
        width=dt.timedelta(hours=12),
        height=abs(c - o),
        color=color
    )
    ax.add_patch(rect)

ax.xaxis_date()
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))

fig.autofmt_xdate()
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
canvas.draw()

root.mainloop()
