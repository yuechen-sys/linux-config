"""Logging utilities for the configuration manager."""

import logging
import sys
from pathlib import Path
from datetime import datetime


def setup_logger(verbose: bool = False, log_file: str = None) -> logging.Logger:
    """Set up logger with appropriate formatting and levels."""
    
    # Create logger
    logger = logging.getLogger('config_manager')
    logger.setLevel(logging.DEBUG if verbose else logging.INFO)
    
    # Clear any existing handlers
    logger.handlers.clear()
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG if verbose else logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler if log file is specified
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_path)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    # Prevent duplicate logs
    logger.propagate = False
    
    return logger


def get_default_log_path() -> Path:
    """Get default log file path."""
    home = Path.home()
    log_dir = home / '.local' / 'share' / 'config-manager'
    log_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d')
    return log_dir / f'config-manager-{timestamp}.log'