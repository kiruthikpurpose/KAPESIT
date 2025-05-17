import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional, Union, Dict, Any
from logging.handlers import RotatingFileHandler

def setup_logger(
    name: str = "kapesit",
    level: Union[int, str] = logging.INFO,
    log_file: Optional[Union[str, Path]] = None,
    log_format: str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    max_bytes: int = 10 * 1024 * 1024,
    backup_count: int = 5
) -> logging.Logger:
    if isinstance(level, str):
        try:
            level = getattr(logging, level.upper())
        except AttributeError:
            raise ValueError(f"Invalid log level: {level}")
    
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger
        
    logger.setLevel(level)
    formatter = logging.Formatter(log_format)
    
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    if log_file is None:
        log_file = Path("logs") / f"kapesit_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    else:
        log_file = Path(log_file)
    
    try:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except Exception as e:
        logger.error(f"Failed to setup file handler: {str(e)}")
    
    return logger

def get_logger(name: str = "kapesit") -> logging.Logger:
    return logging.getLogger(name)

def set_log_level(logger: logging.Logger, level: Union[int, str]) -> None:
    if isinstance(level, str):
        try:
            level = getattr(logging, level.upper())
        except AttributeError:
            raise ValueError(f"Invalid log level: {level}")
    logger.setLevel(level)

def add_file_handler(logger: logging.Logger, log_file: Union[str, Path], 
                    max_bytes: int = 10 * 1024 * 1024, backup_count: int = 5) -> None:
    log_file = Path(log_file)
    try:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        )
        file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
        logger.addHandler(file_handler)
    except Exception as e:
        logger.error(f"Failed to add file handler: {str(e)}")

def remove_handlers(logger: logging.Logger) -> None:
    for handler in logger.handlers[:]:
        handler.close()
        logger.removeHandler(handler) 