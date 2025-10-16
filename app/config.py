import os
import logging
from pydantic import BaseModel

class Config(BaseModel):
    # General
    APP_NAME                    : str   = "FastAPI WebSocket Service"
    ENV                         : str   = os.getenv("ENV", "dev")

    # Graceful shutdown
    FORCED_SHUTDOWN_AFTER_SEC   : int  = int(os.getenv("FORCED_SHUTDOWN_AFTER_SEC", 30 * 60))
    PROGRESS_LOG_EVERY_SEC      : int  = int(os.getenv("PROGRESS_LOG_EVERY_SEC", 5))

    # Logging
    LOG_LEVEL                   : str = os.getenv("LOG_LEVEL", "INFO")


# Global singleton
config = Config()

# Configure logging once
logging.basicConfig(
    level   = getattr(logging, config.LOG_LEVEL.upper(), logging.INFO),
    format  ="%(asctime)s [%(levelname)s] %(message)s",
)
log = logging.getLogger(config.APP_NAME)
