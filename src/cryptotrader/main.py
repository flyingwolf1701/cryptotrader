import uvicorn
import os
# Import the FastAPI app
from app import app

from config import Config, get_logger

# Get logger for this module
logger = get_logger(__name__)

# Load environment variables if dotenv is available
try:
    from dotenv import load_dotenv
    load_dotenv()
    logger.info("Environment variables loaded from .env file")
except ImportError:
    logger.info("python-dotenv not installed, using system environment variables")

# Get port from environment or use default
port = int(os.getenv("PORT", 8000))
debug = os.getenv("DEBUG", "false").lower() == "true"

if __name__ == "__main__":
    logger.info(f"Starting FastAPI server on port {port} (debug={debug})")
    # Run the application with uvicorn
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=port, 
        reload=debug,
        log_level="info"
    )






