from dearpygui.dearpygui import *
import numpy as np

# Mock wallet data
wallet_data = {"BTC": 0.5, "ETH": 2.0, "BNB": 10, "USDT": 1500}

# Sample candlestick data for plotting (OHLC)
# Format: (time, open, close, low, high)
candlestick_data = [
    (1, 30000, 30500, 29900, 30600),
    (2, 30500, 30300, 30200, 30800),
    (3, 30300, 30700, 30100, 30900),
    (4, 30700, 30600, 30500, 31000),
    (5, 30600, 30800, 30400, 31100),
]

x_data = [x[0] for x in candlestick_data]
opens = [x[1] for x in candlestick_data]
closes = [x[2] for x in candlestick_data]
lows = [x[3] for x in candlestick_data]
highs = [x[4] for x in candlestick_data]

create_context()
create_viewport(title='Crypto Dashboard', width=700, height=400)

with window(label="Wallet", tag="main_window", width=280, height=150):
    for asset, amount in wallet_data.items():
        add_text(f"{asset}: {amount}")

with window(label="Chart", pos=(300, 0), width=380, height=250):
    with plot(label="BTC/USD Candlestick", height=200, width=360) as chart_plot:
        add_plot_axis(mvXAxis, label="Time")
        with plot_axis(mvYAxis, label="Price") as y_axis:
            for i in range(len(candlestick_data)):
                color = [0, 255, 0, 255] if closes[i] >= opens[i] else [255, 0, 0, 255]
                add_error_series(
                    x=[x_data[i]],
                    y=[(highs[i] + lows[i]) / 2],
                    negative=[(highs[i] - lows[i]) / 2],
                    positive=[(highs[i] - lows[i]) / 2],
                    label=f"Wick {i}",
                    parent=y_axis
                )
                # Draw the body using rectangles
                add_rect_series(
                    pmin=[x_data[i] - 0.2, min(opens[i], closes[i])],
                    pmax=[x_data[i] + 0.2, max(opens[i], closes[i])],
                    color=color,
                    fill=color,
                    parent=y_axis
                )

set_primary_window("main_window", True)

setup_dearpygui()
show_viewport()
start_dearpygui()
destroy_context()
