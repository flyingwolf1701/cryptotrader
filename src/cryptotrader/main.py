
import uvicorn
from app import app
from config import Secrets, get_logger

# Get logger for this module
logger = get_logger(__name__)

# Get port from Secrets or use default
port = int(getattr(Secrets, 'PORT', 8000))
debug = Secrets.DEBUG

if __name__ == "__main__":
    logger.info(f"Starting FastAPI server on port {port} (debug={debug})")
    
    # Run the application with uvicorn
    uvicorn.run(
        "app:app", 
        host="0.0.0.0", 
        port=port, 
        reload=debug,
        log_level="info"
    )