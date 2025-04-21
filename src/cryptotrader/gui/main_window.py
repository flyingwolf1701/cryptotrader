from __future__ import annotations

"""Order‑book dock widget.

Streams the Binance websocket order‑book for a given symbol into a QTableView.
Replace the placeholder symbol and implement subscription callbacks later.
"""

from typing import List, Tuple

from PySide6.QtWidgets import QWidget, QTableView, QVBoxLayout
from PySide6.QtCore import (
    QAbstractTableModel,
    Qt,
    QModelIndex,
    QTimer,
    Slot,
)

# import the Binance websocket helper
from src.cryptotrader.services.binance import ws_get_order_book

class OrderBookModel(QAbstractTableModel):
    """Table model backing the order‑book view."""
    headers = ["Price", "Bid Size", "Ask Size"]

    def __init__(self, symbol: str = "BTCUSDT") -> None:
        super().__init__()
        self.symbol = symbol
        self._data: List[Tuple[float, float, float]] = []
        # TODO: subscribe to real ws_get_order_book stream
        # ws_get_order_book(symbol=self.symbol, callback=self._on_update)
        # For now, use a timer to clear data periodically
        self._timer = QTimer(self)
        self._timer.timeout.connect(self.refresh)
        self._timer.start(500)

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return len(self._data)

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return len(self.headers)

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole):
        if not index.isValid() or role != Qt.DisplayRole:
            return None
        row, col = index.row(), index.column()
        return self._data[row][col]

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.DisplayRole):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.headers[section]
        return super().headerData(section, orientation, role)

    @Slot()
    def refresh(self) -> None:
        """Placeholder refresh: replace with real order book callback."""
        # TODO: call ws_get_order_book and update self._data
        self.beginResetModel()
        # placeholder: empty out data
        self._data = []
        self.endResetModel()


class OrderBookView(QWidget):
    """Widget embedding the order‑book QTableView."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._model = OrderBookModel()
        self._view = QTableView()
        self._view.setModel(self._model)
        layout = QVBoxLayout(self)
        layout.addWidget(self._view)
        self.setLayout(layout)
