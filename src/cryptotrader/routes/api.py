from flask import Blueprint, jsonify, request, current_app
import logging

logger = logging.getLogger(__name__)

api_bp = Blueprint('api', __name__)

@api_bp.route('/symbols', methods=['GET'])
def get_symbols():
    try:
        from services.binance_client import Client
        contracts = Client.get_contracts_binance()
        return jsonify({"status": "success", "symbols": contracts})
    except Exception as e:
        logger.error(f"Error fetching symbols: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@api_bp.route('/price', methods=['GET'])
def get_price():
    symbol = request.args.get('symbol', 'BTCUSDT')
    try:
        if not hasattr(current_app, 'binance_client'):
            return jsonify({"status": "error", "message": "Binance client not initialized"}), 500
        
        price_data = current_app.binance_client.get_bid_ask(symbol)
        if price_data:
            # Convert dataclass to dict for JSON serialization
            data = {
                "bid": price_data.bid,
                "ask": price_data.ask
            }
            return jsonify({"status": "success", "symbol": symbol, "data": data})
        else:
            return jsonify({"status": "error", "message": f"No price data available for {symbol}"}), 404
    except Exception as e:
        logger.error(f"Error fetching price for {symbol}: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@api_bp.route('/balance', methods=['GET'])
def get_balance():
    try:
        if not hasattr(current_app, 'binance_client'):
            return jsonify({"status": "error", "message": "Binance client not initialized"}), 500
        
        balance = current_app.binance_client.get_balance()
        return jsonify({"status": "success", "balance": balance})
    except Exception as e:
        logger.error(f"Error fetching balance: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@api_bp.route('/order', methods=['POST'])
def place_order():
    try:
        if not hasattr(current_app, 'binance_client'):
            return jsonify({"status": "error", "message": "Binance client not initialized"}), 500
        
        data = request.json
        required_fields = ['symbol', 'side', 'quantity', 'type']
        
        for field in required_fields:
            if field not in data:
                return jsonify({"status": "error", "message": f"Missing required field: {field}"}), 400
        
        # Import here to avoid circular imports
        from models.binance_models import OrderRequest
        
        # Create OrderRequest dataclass instance
        order_request = OrderRequest(
            symbol=data['symbol'],
            side=data['side'],
            quantity=float(data['quantity']),
            order_type=data['type'],
            price=float(data['price']) if 'price' in data and data['price'] is not None else None,
            time_in_force=data.get('timeInForce')
        )
        
        order_status = current_app.binance_client.place_order(order_request)
        
        if order_status:
            return jsonify({"status": "success", "order": order_status})
        else:
            return jsonify({"status": "error", "message": "Failed to place order"}), 500
    except Exception as e:
        logger.error(f"Error placing order: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500