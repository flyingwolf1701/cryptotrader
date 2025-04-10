from flask import Flask
from config import Config

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Register blueprints
    from routes.api import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # Add main route
    @app.route('/')
    def index():
        from flask import jsonify
        return jsonify({"status": "success", "message": "Binance API is running"})
    
    # Initialize binance client if keys are provided
    if app.config.get('BINANCE_API_KEY') and app.config.get('BINANCE_API_SECRET'):
        from services.binance_client import Client
        app.binance_client = Client(
            app.config['BINANCE_API_KEY'],
            app.config['BINANCE_API_SECRET']
        )
    
    return app