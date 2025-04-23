"""
Strategy Panel Component

Allows users to configure and execute trading strategies.
"""

import tkinter as tk
from tkinter import ttk
from functools import partial

from config import get_logger
from src.cryptotrader.gui.components.styles import Colors, create_table

logger = get_logger(__name__)

class StrategyParametersDialog(tk.Toplevel):
    """Dialog for configuring strategy parameters."""
    
    def __init__(self, parent, strategy_type, parameters=None):
        super().__init__(parent)
        
        self.strategy_type = strategy_type
        self.parameters = parameters or {}
        self.result = None
        
        self.title(f"{strategy_type} Strategy Parameters")
        self.geometry("400x250")
        self.configure(background=Colors.BACKGROUND)
        
        # Make dialog modal
        self.transient(parent)
        self.grab_set()
        
        self.init_ui()
        
        # Center the dialog
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry('{}x{}+{}+{}'.format(width, height, x, y))
        
        # Wait for window to be closed
        self.wait_window(self)
    
    def init_ui(self):
        """Initialize the UI components."""
        # Main frame
        main_frame = ttk.Frame(self, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Form frame for parameters
        form_frame = ttk.LabelFrame(main_frame, text="Parameters", padding=10)
        form_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Parameter input widgets
        self.param_widgets = {}
        
        # Add different parameters based on strategy type
        row = 0
        if self.strategy_type == "Technical":
            # MACD Parameters
            ttk.Label(form_frame, text="MACD Fast Length:").grid(row=row, column=0, sticky="w", padx=5, pady=5)
            self.param_widgets["ema_fast"] = ttk.Spinbox(form_frame, from_=3, to=50, width=10)
            self.param_widgets["ema_fast"].set(self.parameters.get("ema_fast", 12))
            self.param_widgets["ema_fast"].grid(row=row, column=1, sticky="w", padx=5, pady=5)
            row += 1
            
            ttk.Label(form_frame, text="MACD Slow Length:").grid(row=row, column=0, sticky="w", padx=5, pady=5)
            self.param_widgets["ema_slow"] = ttk.Spinbox(form_frame, from_=10, to=100, width=10)
            self.param_widgets["ema_slow"].set(self.parameters.get("ema_slow", 26))
            self.param_widgets["ema_slow"].grid(row=row, column=1, sticky="w", padx=5, pady=5)
            row += 1
            
            ttk.Label(form_frame, text="MACD Signal Length:").grid(row=row, column=0, sticky="w", padx=5, pady=5)
            self.param_widgets["ema_signal"] = ttk.Spinbox(form_frame, from_=2, to=20, width=10)
            self.param_widgets["ema_signal"].set(self.parameters.get("ema_signal", 9))
            self.param_widgets["ema_signal"].grid(row=row, column=1, sticky="w", padx=5, pady=5)
            row += 1
            
        elif self.strategy_type == "Breakout":
            # Breakout Parameters
            ttk.Label(form_frame, text="Minimum Volume:").grid(row=row, column=0, sticky="w", padx=5, pady=5)
            self.param_widgets["min_volume"] = ttk.Spinbox(form_frame, from_=0, to=100000, increment=10, width=10)
            self.param_widgets["min_volume"].set(self.parameters.get("min_volume", 100))
            self.param_widgets["min_volume"].grid(row=row, column=1, sticky="w", padx=5, pady=5)
            row += 1
        
        # Button box
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(button_frame, text="OK", command=self.on_ok).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.on_cancel).pack(side=tk.RIGHT, padx=5)
    
    def on_ok(self):
        """Handle OK button click."""
        # Get values from parameter widgets
        self.result = self.get_parameters()
        self.destroy()
    
    def on_cancel(self):
        """Handle Cancel button click."""
        self.result = None
        self.destroy()
    
    def get_parameters(self):
        """Get the configured parameters."""
        result = {}
        
        for name, widget in self.param_widgets.items():
            try:
                # Try to get value as float first
                result[name] = float(widget.get())
            except ValueError:
                # If not a float, get as string
                result[name] = widget.get()
        
        return result


class StrategyPanel(ttk.Frame):
    """Widget for configuring and running trading strategies."""
    
    def __init__(self, parent, market_client):
        super().__init__(parent)
        
        self.market_client = market_client
        self.available_symbols = []
        self.active_strategies = {}
        self.strategy_parameters = {}
        self.log_callback = None  # Callback for logging messages
        
        # Available strategy types
        self.strategy_types = ["Technical", "Breakout"]
        
        # Available timeframes
        self.timeframes = ["1m", "5m", "15m", "30m", "1h", "4h", "1d"]
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize the UI components."""
        # Configure grid layout
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        
        # Create control panel at the top
        controls_frame = ttk.Frame(self)
        controls_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        
        # Add strategy button
        self.add_btn = ttk.Button(controls_frame, text="Add Strategy", command=self.add_strategy_row)
        self.add_btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Create table for strategy data
        columns = [
            "Strategy", "Symbol", "Timeframe", "Balance %", "TP %", "SL %", 
            "Parameters", "Status", "Actions"
        ]
        table_frame, self.table = create_table(self, columns, height=10)
        table_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
    
    def set_available_symbols(self, symbols):
        """Set the list of available trading symbols."""
        self.available_symbols = sorted(symbols)
    
    def add_strategy_row(self):
        """Add a new strategy configuration row to the table."""
        # Create a unique identifier for this row
        row_id = len(self.strategy_parameters)
        
        # Create cells for the row
        strategy_var = tk.StringVar(value=self.strategy_types[0])
        symbol_var = tk.StringVar(value=self.available_symbols[0] if self.available_symbols else "BTCUSDT")
        timeframe_var = tk.StringVar(value="1h")
        balance_var = tk.StringVar(value="10")
        tp_var = tk.StringVar(value="2")
        sl_var = tk.StringVar(value="1")
        status_var = tk.StringVar(value="INACTIVE")
        
        # Store variables for this row
        self.active_strategies[row_id] = {
            "strategy_var": strategy_var,
            "symbol_var": symbol_var,
            "timeframe_var": timeframe_var,
            "balance_var": balance_var,
            "tp_var": tp_var,
            "sl_var": sl_var,
            "status_var": status_var,
            "is_active": False
        }
        
        # Initialize parameters dictionary for this row
        self.strategy_parameters[row_id] = {}
        
        # Create the table row
        values = [
            strategy_var.get(),
            symbol_var.get(),
            timeframe_var.get(),
            balance_var.get(),
            tp_var.get(),
            sl_var.get(),
            "Not Set",
            status_var.get(),
            ""  # Actions column will be populated with buttons
        ]
        item_id = self.table.insert("", "end", values=values, tags=(f"row_{row_id}",))
        
        # Add dropdown cells
        self._add_combo_to_cell(item_id, 0, strategy_var, self.strategy_types)
        self._add_combo_to_cell(item_id, 1, symbol_var, self.available_symbols or ["BTCUSDT", "ETHUSDT", "BNBUSDT"])
        self._add_combo_to_cell(item_id, 2, timeframe_var, self.timeframes)
        
        # Add parameters button
        self._add_button_to_cell(item_id, 6, "Set Params", 
                               lambda rid=row_id: self.show_parameters_dialog(rid))
        
        # Add action buttons
        self._add_action_buttons(item_id, row_id)
        
        # Log the addition
        if self.log_callback:
            self.log_callback(f"Added new strategy configuration (row {row_id+1})", "INFO")
    
    def _add_combo_to_cell(self, item_id, column, variable, values):
        """Add a combobox to a cell in the table."""
        # Place a combobox in the cell
        bbox = self.table.bbox(item_id, f"#{column}")
        if not bbox:
            self.update_idletasks()
            bbox = self.table.bbox(item_id, f"#{column}")
        
        if bbox:
            x, y, width, height = bbox
            
            # Create the combo
            combo = ttk.Combobox(self.table, textvariable=variable, values=values, width=10)
            combo.place(x=x, y=y, width=width, height=height)
            
            # Bind change event
            combo.bind("<<ComboboxSelected>>", 
                      lambda e, iid=item_id: self._update_table_row_values(iid))
    
    def _add_button_to_cell(self, item_id, column, text, command):
        """Add a button to a cell in the table."""
        # Place a button in the cell
        bbox = self.table.bbox(item_id, f"#{column}")
        if not bbox:
            self.update_idletasks()
            bbox = self.table.bbox(item_id, f"#{column}")
        
        if bbox:
            x, y, width, height = bbox
            
            # Create the button
            button = ttk.Button(self.table, text=text, command=command)
            button.place(x=x, y=y, width=width, height=height)
    
    def _add_action_buttons(self, item_id, row_id):
        """Add action buttons to the last cell."""
        # Place buttons in the cell
        bbox = self.table.bbox(item_id, "#8")  # Actions column
        if not bbox:
            self.update_idletasks()
            bbox = self.table.bbox(item_id, "#8")
        
        if bbox:
            x, y, width, height = bbox
            
            # Create a frame to hold the buttons
            button_frame = ttk.Frame(self.table)
            button_frame.place(x=x, y=y, width=width, height=height)
            
            # Create toggle button
            toggle_btn = ttk.Button(button_frame, text="Start",
                                  command=lambda: self.toggle_strategy(row_id))
            toggle_btn.pack(side=tk.LEFT, padx=2, fill=tk.Y)
            
            # Create delete button
            delete_btn = ttk.Button(button_frame, text="Delete",
                                  command=lambda: self.delete_strategy(row_id))
            delete_btn.pack(side=tk.LEFT, padx=2, fill=tk.Y)
            
            # Store buttons in the strategy data
            self.active_strategies[row_id]["toggle_btn"] = toggle_btn
            self.active_strategies[row_id]["delete_btn"] = delete_btn
    
    def _update_table_row_values(self, item_id):
        """Update the values in a table row from the variables."""
        for row_id, strategy_data in self.active_strategies.items():
            # Find if this item belongs to this row
            for check_id in self.table.get_children():
                if check_id == item_id:
                    # Update values from variables
                    self.table.item(item_id, values=(
                        strategy_data["strategy_var"].get(),
                        strategy_data["symbol_var"].get(),
                        strategy_data["timeframe_var"].get(),
                        strategy_data["balance_var"].get(),
                        strategy_data["tp_var"].get(),
                        strategy_data["sl_var"].get(),
                        "Set" if self.strategy_parameters.get(row_id) else "Not Set",
                        strategy_data["status_var"].get(),
                        ""  # Actions column has widgets
                    ))
                    break
    
    def show_parameters_dialog(self, row_id):
        """Show the parameters dialog for a strategy."""
        strategy_type = self.active_strategies[row_id]["strategy_var"].get()
        
        # Get existing parameters if any
        existing_params = self.strategy_parameters.get(row_id, {})
        
        # Show dialog
        dialog = StrategyParametersDialog(self, strategy_type, existing_params)
        
        # Process result
        if dialog.result:
            # Save parameters
            self.strategy_parameters[row_id] = dialog.result
            
            # Update the table to show params are set
            for item_id in self.table.get_children():
                values = self.table.item(item_id)["values"]
                if values and values[0] == strategy_type:
                    values_list = list(values)
                    values_list[6] = "Set"
                    self.table.item(item_id, values=tuple(values_list))
                    break
            
            if self.log_callback:
                self.log_callback(f"Updated parameters for {strategy_type} strategy", "INFO")
    
    def toggle_strategy(self, row_id):
        """Toggle a strategy between active and inactive states."""
        if row_id not in self.active_strategies:
            return
        
        strategy_data = self.active_strategies[row_id]
        is_active = strategy_data["is_active"]
        
        # Validate inputs before activating
        if not is_active:
            if not self._validate_strategy_inputs(row_id):
                return
        
        # Toggle status
        if is_active:
            # Deactivate
            strategy_data["status_var"].set("INACTIVE")
            strategy_data["toggle_btn"].configure(text="Start")
            strategy_data["is_active"] = False
            
            # Log deactivation
            strategy_type = strategy_data["strategy_var"].get()
            symbol = strategy_data["symbol_var"].get()
            timeframe = strategy_data["timeframe_var"].get()
            if self.log_callback:
                self.log_callback(f"Stopped {strategy_type} strategy on {symbol}/{timeframe}", "INFO")
        else:
            # Activate
            strategy_data["status_var"].set("ACTIVE")
            strategy_data["toggle_btn"].configure(text="Stop")
            strategy_data["is_active"] = True
            
            # Log activation
            strategy_type = strategy_data["strategy_var"].get()
            symbol = strategy_data["symbol_var"].get()
            timeframe = strategy_data["timeframe_var"].get()
            if self.log_callback:
                self.log_callback(f"Started {strategy_type} strategy on {symbol}/{timeframe}", "SUCCESS")
        
        # Update table
        self._update_strategies_table()
    
    def delete_strategy(self, row_id):
        """Delete a strategy row."""
        if row_id not in self.active_strategies:
            return
        
        # Check if strategy is active
        strategy_data = self.active_strategies[row_id]
        if strategy_data["is_active"]:
            self.toggle_strategy(row_id)  # Deactivate first
        
        # Remove from parameters dictionary
        if row_id in self.strategy_parameters:
            del self.strategy_parameters[row_id]
        
        # Remove row from table
        for item_id in self.table.get_children():
            values = self.table.item(item_id)["values"]
            strat_type = strategy_data["strategy_var"].get()
            symbol = strategy_data["symbol_var"].get()
            
            if (values and values[0] == strat_type and values[1] == symbol and
                values[7] == strategy_data["status_var"].get()):
                self.table.delete(item_id)
                break
        
        # Remove from active strategies
        del self.active_strategies[row_id]
        
        # Log deletion
        if self.log_callback:
            self.log_callback(f"Deleted strategy configuration (row {row_id+1})", "INFO")
    
    def _update_strategies_table(self):
        """Update the table with current strategy data."""
        for row_id, strategy_data in self.active_strategies.items():
            for item_id in self.table.get_children():
                values = self.table.item(item_id)["values"]
                strat_type = strategy_data["strategy_var"].get()
                symbol = strategy_data["symbol_var"].get()
                
                if (values and values[0] == strat_type and values[1] == symbol):
                    values_list = list(values)
                    values_list[7] = strategy_data["status_var"].get()
                    self.table.item(item_id, values=tuple(values_list))
                    
                    # Apply color based on status
                    if strategy_data["status_var"].get() == "ACTIVE":
                        self.table.tag_configure(f"active_{row_id}", foreground=Colors.SUCCESS)
                        self.table.item(item_id, tags=(f"active_{row_id}",))
                    else:
                        self.table.tag_configure(f"inactive_{row_id}", foreground=Colors.FOREGROUND)
                        self.table.item(item_id, tags=(f"inactive_{row_id}",))
                    break
    
    def _validate_strategy_inputs(self, row_id):
        """Validate strategy inputs before activation."""
        strategy_data = self.active_strategies[row_id]
        
        try:
            # Check balance percentage
            balance_pct = float(strategy_data["balance_var"].get())
            if balance_pct <= 0 or balance_pct > 100:
                if self.log_callback:
                    self.log_callback("Balance percentage must be between 0 and 100", "ERROR")
                return False
            
            # Check take profit
            tp_pct = float(strategy_data["tp_var"].get())
            if tp_pct <= 0:
                if self.log_callback:
                    self.log_callback("Take profit percentage must be greater than 0", "ERROR")
                return False
            
            # Check stop loss
            sl_pct = float(strategy_data["sl_var"].get())
            if sl_pct <= 0:
                if self.log_callback:
                    self.log_callback("Stop loss percentage must be greater than 0", "ERROR")
                return False
            
            # Check strategy parameters
            strategy_type = strategy_data["strategy_var"].get()
            if row_id not in self.strategy_parameters or not self.strategy_parameters[row_id]:
                if self.log_callback:
                    self.log_callback(f"Strategy parameters not set for {strategy_type}", "ERROR")
                return False
            
            # Validate specific parameters based on strategy type
            params = self.strategy_parameters[row_id]
            if strategy_type == "Technical":
                required_params = ["ema_fast", "ema_slow", "ema_signal"]
                if not all(param in params for param in required_params):
                    if self.log_callback:
                        self.log_callback("Missing required MACD parameters", "ERROR")
                    return False
            elif strategy_type == "Breakout":
                if "min_volume" not in params:
                    if self.log_callback:
                        self.log_callback("Missing minimum volume parameter", "ERROR")
                    return False
            
            return True
        except ValueError:
            if self.log_callback:
                self.log_callback("Invalid numeric input", "ERROR")
            return False