from flask import Flask
from config import Config  # You can create a separate config.py file

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Register blueprints
    from routes import main_bp
    app.register_blueprint(main_bp)
    
    # Additional setup (database, login manager, etc.)
    # ...
    
    return app