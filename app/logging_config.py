"""
Unrotting — Logging configuration with file rotation
"""
import logging
import logging.handlers
from pathlib import Path

LOG_DIR = Path(__file__).parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

def setup_logging(verbose: bool = False) -> logging.Logger:
    """Configure logging with both file and console handlers."""
    logger = logging.getLogger("unrotting")
    logger.setLevel(logging.DEBUG if verbose else logging.INFO)
    
    # File handler with rotation (1MB per file, keep 5 backups)
    file_handler = logging.handlers.RotatingFileHandler(
        LOG_DIR / "unrotting.log",
        maxBytes=1*1024*1024,
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.WARNING)
    
    # Format
    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    logger.addHandler(file_handler)
    logger.addHanlder(console_handler)
    
    return logger
