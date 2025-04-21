"""
Strategy Panel Component

Allows users to configure and execute trading strategies.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLabel, QComboBox, QLineEdit, QHeaderView,
    QDialog, QFormLayout, QDoubleSpinBox, QSpinBox, QDialogButtonBox
)
from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtGui import QColor, QBrush

from cryptotrader.config import get_logger

logger = get_logger(__name__)

class StrategyParametersDialog(QDialog):
    """Dialog for configuring strategy parameters."""
    
    def __init__(self, strategy_type, parameters=None, parent=None):
        super().__init__(parent)
        
        self.strategy_type = strategy_type
        self.parameters = parameters or {}
        
        self.setWindowTitle(f"{strategy_type} Strategy Parameters")
        self.resize(400, 200)
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize the UI components."""
        layout = QVBoxLayout(self)
        
        # Form layout for parameters
        form_layout = QFormLayout()
        
        # Parameter input widgets
        self.param_widgets = {}
        
        # Add different parameters based on strategy type
        if self.strategy_type == "Technical":
            # MACD Parameters
            self.param_widgets["ema_fast"] = QSpinBox()
            self.param_widgets["ema_fast"].setRange(3, 50)
            self.param_widgets["ema_fast"].setValue(self.parameters.get("ema_fast", 12))
            form_layout.addRow("MACD Fast Length:", self.param_widgets["ema_fast"])
            
            self.param_widgets["ema_slow"] = QSpinBox()
            self.param_widgets["ema_slow"].setRange(10, 100)
            self.param_widgets["ema_slow"].setValue(self.parameters.get("ema_slow", 26))
            form_layout.addRow("MACD Slow Length:", self.param_widgets["ema_slow"])
            
            self.param_widgets["ema_signal"] = QSpinBox()
            self.param_widgets["ema_signal"].setRange(2, 20)
            self.param_widgets["ema_signal"].setValue(self.parameters.get("ema_signal", 9))
            form_layout.addRow("MACD Signal Length:", self.param_widgets["ema_signal"])
            
        elif self.strategy_type == "Breakout":
            # Breakout Parameters
            self.param_widgets["min_volume"] = QDoubleSpinBox()
            self.param_widgets["min_volume"].setRange(0, 100000)
            self.param_widgets["min_volume"].setDecimals(2)
            self.param_widgets["min_volume"].setValue(self.parameters.get("min_volume", 100))
            form_layout.addRow("Minimum Volume:", self.param_widgets["min_volume"])
        
        # Add form to layout
        layout.addLayout(form_layout)
        
        # Button box
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        
        layout.addWidget(button_box)
    
    def get_parameters(self):
        """Get the configured parameters."""
        result = {}
        
        for name, widget in self.param_widgets.items():
            result[name] = widget.value()
        
        return result


class StrategyPanel(QWidget):
    """Widget for configuring and running trading strategies."""
    
    # Signal emitted when a log message should be displayed
    log_message = Signal(str, str)
    
    def __init__(self, market_client):
        super().__init__()
        
        self.market_client = market_client
        self.available_symbols = []
        self.active_strategies = {}
        self.strategy_parameters = {}
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize the UI components."""
        # Main layout
        layout = QVBoxLayout(self)
        
        # Control section
        controls_layout = QHBoxLayout()
        
        # Add strategy button
        self.add_btn = QPushButton("Add Strategy")
        self.add_btn.clicked.connect(self.add_strategy_row)
        controls_layout.addWidget(self.add_btn)
        
        controls_layout.addStretch()
        
        layout.addLayout(controls_layout)
        
        # Create table
        self.table = QTableWidget()
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels([
            "Strategy", "Symbol", "Timeframe", "Balance %", "TP %", "SL %", 
            "Parameters", "Status", "Actions"
        ])
        
        # Set column widths
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        for col in [6, 7, 8]:  # Parameters, Status, Actions
            self.table.horizontalHeader().setSectionResizeMode(col, QHeaderView.ResizeToContents)
        
        layout.addWidget(self.table)
        
        # Available strategy types
        self.strategy_types = ["Technical", "Breakout"]
        
        # Available timeframes
        self.timeframes = ["1m", "5m", "15m", "30m", "1h", "4h", "1d"]
    
    def set_available_symbols(self, symbols):
        """Set the list of available trading symbols."""
        self.available_symbols = sorted(symbols)
    
    def add_strategy_row(self):
        """Add a new strategy configuration row to the table."""
        row = self.table.rowCount()
        self.table.insertRow(row)
        
        # Strategy Type (dropdown)
        strategy_combo = QComboBox()
        strategy_combo.addItems(self.strategy_types)
        self.table.setCellWidget(row, 0, strategy_combo)
        
        # Symbol (dropdown)
        symbol_combo = QComboBox()
        symbol_combo.addItems(self.available_symbols or ["BTCUSDT", "ETHUSDT", "BNBUSDT"])
        self.table.setCellWidget(row, 1, symbol_combo)
        
        # Timeframe (dropdown)
        timeframe_combo = QComboBox()
        timeframe_combo.addItems(self.timeframes)
        self.table.setCellWidget(row, 2, timeframe_combo)
        
        # Balance % (input)
        balance_input = QLineEdit("10")  # Default to 10%
        balance_input.setAlignment(Qt.AlignCenter)
        self.table.setCellWidget(row, 3, balance_input)
        
        # Take Profit % (input)
        tp_input = QLineEdit("2")  # Default to 2%
        tp_input.setAlignment(Qt.AlignCenter)
        self.table.setCellWidget(row, 4, tp_input)
        
        # Stop Loss % (input)
        sl_input = QLineEdit("1")  # Default to 1%
        sl_input.setAlignment(Qt.AlignCenter)
        self.table.setCellWidget(row, 5, sl_input)
        
        # Parameters button
        params_btn = QPushButton("Set Params")
        params_btn.clicked.connect(lambda: self.show_parameters_dialog(row))
        self.table.setCellWidget(row, 6, params_btn)
        
        # Status (label)
        status_label = QLabel("INACTIVE")
        status_label.setAlignment(Qt.AlignCenter)
        status_label.setStyleSheet("color: #888888;")
        self.table.setCellWidget(row, 7, status_label)
        
        # Actions (container for buttons)
        actions_widget = QWidget()
        actions_layout = QHBoxLayout(actions_widget)
        actions_layout.setContentsMargins(0, 0, 0, 0)
        
        # Activate/Deactivate button
        toggle_btn = QPushButton("Start")
        toggle_btn.setStyleSheet("background-color: darkgreen; color: white;")
        toggle_btn.clicked.connect(lambda: self.toggle_strategy(row))
        
        # Delete button
        delete_btn = QPushButton("Delete")
        delete_btn.setStyleSheet("background-color: darkred; color: white;")
        delete_btn.clicked.connect(lambda: self.delete_strategy(row))
        
        actions_layout.addWidget(toggle_btn)
        actions_layout.addWidget(delete_btn)
        
        self.table.setCellWidget(row, 8, actions_widget)
        
        # Initialize parameters dictionary for this row
        self.strategy_parameters[row] = {}
        
        self.log_message.emit(f"Added new strategy configuration (row {row+1})", "INFO")
    
    def show_parameters_dialog(self, row):
        """Show the parameters dialog for a strategy."""
        strategy_type = self.table.cellWidget(row, 0).currentText()
        
        # Get existing parameters if any
        existing_params = self.strategy_parameters.get(row, {})
        
        # Show dialog
        dialog = StrategyParametersDialog(strategy_type, existing_params, self)
        if dialog.exec():
            # Save parameters
            self.strategy_parameters[row] = dialog.get_parameters()
            self.log_message.emit(f"Updated parameters for {strategy_type} strategy", "INFO")
    
    def toggle_strategy(self, row):
        """Toggle a strategy between active and inactive states."""
        # Get button and status label
        actions_widget = self.table.cellWidget(row, 8)
        toggle_btn = actions_widget.layout().itemAt(0).widget()
        status_label = self.table.cellWidget(row, 7)
        
        # Get current status
        is_active = status_label.text() == "ACTIVE"
        
        # Validate inputs before activating
        if not is_active:
            if not self._validate_strategy_inputs(row):
                return
        
        # Toggle status
        if is_active:
            # Deactivate
            status_label.setText("INACTIVE")
            status_label.setStyleSheet("color: #888888;")
            toggle_btn.setText("Start")
            toggle_btn.setStyleSheet("background-color: darkgreen; color: white;")
            
            # Enable input fields
            for col in range(6):
                widget = self.table.cellWidget(row, col)
                widget.setEnabled(True)
            
            # Log deactivation
            strategy_type = self.table.cellWidget(row, 0).currentText()
            symbol = self.table.cellWidget(row, 1).currentText()
            timeframe = self.table.cellWidget(row, 2).currentText()
            self.log_message.emit(f"Stopped {strategy_type} strategy on {symbol}/{timeframe}", "INFO")
        else:
            # Activate
            status_label.setText("ACTIVE")
            status_label.setStyleSheet("color: green;")
            toggle_btn.setText("Stop")
            toggle_btn.setStyleSheet("background-color: darkred; color: white;")
            
            # Disable input fields
            for col in range(6):
                widget = self.table.cellWidget(row, col)
                widget.setEnabled(False)
            
            # Log activation
            strategy_type = self.table.cellWidget(row, 0).currentText()
            symbol = self.table.cellWidget(row, 1).currentText()
            timeframe = self.table.cellWidget(row, 2).currentText()
            self.log_message.emit(f"Started {strategy_type} strategy on {symbol}/{timeframe}", "SUCCESS")
    
    def delete_strategy(self, row):
        """Delete a strategy row."""
        # Check if strategy is active
        status_label = self.table.cellWidget(row, 7)
        if status_label.text() == "ACTIVE":
            self.toggle_strategy(row)  # Deactivate first
        
        # Remove from parameters dictionary
        if row in self.strategy_parameters:
            del self.strategy_parameters[row]
        
        # Remove row from table
        self.table.removeRow(row)
        
        # Log deletion
        self.log_message.emit(f"Deleted strategy configuration (row {row+1})", "INFO")
    
    def _validate_strategy_inputs(self, row):
        """Validate strategy inputs before activation."""
        try:
            # Check balance percentage
            balance_pct = float(self.table.cellWidget(row, 3).text())
            if balance_pct <= 0 or balance_pct > 100:
                self.log_message.emit("Balance percentage must be between 0 and 100", "ERROR")
                return False
            
            # Check take profit
            tp_pct = float(self.table.cellWidget(row, 4).text())
            if tp_pct <= 0:
                self.log_message.emit("Take profit percentage must be greater than 0", "ERROR")
                return False
            
            # Check stop loss
            sl_pct = float(self.table.cellWidget(row, 5).text())
            if sl_pct <= 0:
                self.log_message.emit("Stop loss percentage must be greater than 0", "ERROR")
                return False
            
            # Check strategy parameters
            strategy_type = self.table.cellWidget(row, 0).currentText()
            if row not in self.strategy_parameters or not self.strategy_parameters[row]:
                self.log_message.emit(f"Strategy parameters not set for {strategy_type}", "ERROR")
                return False
            
            # Validate specific parameters based on strategy type
            params = self.strategy_parameters[row]
            if strategy_type == "Technical":
                required_params = ["ema_fast", "ema_slow", "ema_signal"]
                if not all(param in params for param in required_params):
                    self.log_message.emit("Missing required MACD parameters", "ERROR")
                    return False
            elif strategy_type == "Breakout":
                if "min_volume" not in params:
                    self.log_message.emit("Missing minimum volume parameter", "ERROR")
                    return False
            
            return True
        except ValueError:
            self.log_message.emit("Invalid numeric input", "ERROR")
            return False