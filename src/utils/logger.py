"""
Logging configuration for GutachtenAssist
"""

import sys
from pathlib import Path
from loguru import logger


def setup_logger(log_level: str = "INFO") -> logger:
    """
    Setup application logger with file and console output
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        
    Returns:
        Configured logger instance
    """
    
    # Remove default handler
    logger.remove()
    
    # Add console handler with color
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=log_level,
        colorize=True
    )
    
    # Add file handler
    log_file = Path(__file__).parent.parent.parent / "logs" / "gutachten_assist.log"
    log_file.parent.mkdir(exist_ok=True)
    
    logger.add(
        log_file,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level=log_level,
        rotation="10 MB",
        retention="30 days",
        compression="zip"
    )
    
    return logger


def get_logger(name: str | None = None) -> logger:
    """
    Get logger instance for a specific module
    
    Args:
        name: Module name
        
    Returns:
        Logger instance
    """
    if name:
        return logger.bind(name=name)
    return logger 