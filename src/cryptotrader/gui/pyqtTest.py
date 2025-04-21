from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PySide6.QtCharts import QChart, QChartView, QCandlestickSeries, QCandlestickSet, QBarCategoryAxis
from PySide6.QtGui import QPainter
from PySide6.QtCore import Qt

# Sample OHLC data (time_index, open, close, low, high)
candlestick_data = [
    (1, 30000, 30500, 29900, 30600),
    (2, 30500, 30300, 30200, 30800),
    (3, 30300, 30700, 30100, 30900),
    (4, 30700, 30600, 30500, 31000),
    (5, 30600, 30800, 30400, 31100),
]

class CandlestickChart(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PySide6 Crypto Candlestick Chart")
        self.setGeometry(100, 100, 800, 400)

        series = QCandlestickSeries()
        series.setName("BTC/USD")
        series.setIncreasingColor(Qt.green)
        series.setDecreasingColor(Qt.red)

        # Append candlestick sets
        for i, (time_index, o, c, l, h) in enumerate(candlestick_data):
            candle = QCandlestickSet(o, h, l, c, i)
            series.append(candle)

        # Create chart
        chart = QChart()
        chart.addSeries(series)
        chart.setTitle("BTC/USD Candlestick (Fixed)")
        chart.setAnimationOptions(QChart.SeriesAnimations)

        # Create labeled x-axis
        labels = [str(t[0]) for t in candlestick_data]
        axisX = QBarCategoryAxis()
        axisX.append(labels)
        chart.setAxisX(axisX, series)

        chart.createDefaultAxes()

        # Render view
        chart_view = QChartView(chart)
        chart_view.setRenderHint(QPainter.Antialiasing)

        # Layout
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.addWidget(chart_view)
        self.setCentralWidget(container)

if __name__ == "__main__":
    app = QApplication([])
    win = CandlestickChart()
    win.show()
    app.exec()

