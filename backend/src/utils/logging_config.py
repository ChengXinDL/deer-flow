import logging
import sys
from datetime import datetime
from logging.handlers import RotatingFileHandler
from pathlib import Path


# Get the backend directory (parent of src)
BACKEND_DIR = Path(__file__).parent.parent.parent.resolve()


def setup_logging(
    log_dir: str = "logs",
    log_level: int = logging.INFO,
    max_bytes: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5,
    console_output: bool = True,
) -> logging.Logger:
    """Setup unified logging configuration for the application.
    
    Args:
        log_dir: Directory to store log files (relative to backend directory).
        log_level: Logging level (default: INFO).
        max_bytes: Maximum size of each log file before rotation.
        backup_count: Number of backup files to keep.
        console_output: Whether to also output logs to console.
    
    Returns:
        Root logger with configured handlers.
    """
    # Create logs directory with absolute path
    log_path = BACKEND_DIR / log_dir
    log_path.mkdir(parents=True, exist_ok=True)
    
    # Generate log filename with date
    today = datetime.now().strftime("%Y-%m-%d")
    log_file = log_path / f"app_{today}.log"
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    simple_formatter = logging.Formatter(
        fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # File handler with rotation
    file_handler = RotatingFileHandler(
        filename=str(log_file),
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding="utf-8"
    )
    file_handler.setLevel(log_level)
    file_handler.setFormatter(detailed_formatter)
    root_logger.addHandler(file_handler)
    
    # Console handler (optional)
    if console_output:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(log_level)
        console_handler.setFormatter(simple_formatter)
        root_logger.addHandler(console_handler)
    
    # Create separate log file for SQL agent
    sql_log_file = log_path / f"sql_agent_{today}.log"
    sql_handler = RotatingFileHandler(
        filename=str(sql_log_file),
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding="utf-8"
    )
    sql_handler.setLevel(logging.DEBUG)
    sql_handler.setFormatter(detailed_formatter)
    
    sql_logger = logging.getLogger("src.agents.sql_agent")
    sql_logger.addHandler(sql_handler)
    sql_logger.setLevel(logging.DEBUG)
    
    # Create separate log file for LangGraph API
    langgraph_log_file = log_path / f"langgraph_{today}.log"
    langgraph_handler = RotatingFileHandler(
        filename=str(langgraph_log_file),
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding="utf-8"
    )
    langgraph_handler.setLevel(logging.DEBUG)
    langgraph_handler.setFormatter(detailed_formatter)
    
    langgraph_logger = logging.getLogger("langgraph_api")
    langgraph_logger.addHandler(langgraph_handler)
    langgraph_logger.setLevel(logging.DEBUG)
    
    # Log startup message
    root_logger.info(f"Logging initialized. Log files: {log_path}")
    
    return root_logger


def get_logger(name: str) -> logging.Logger:
    """Get a logger with the given name.
    
    Args:
        name: Logger name (usually __name__).
    
    Returns:
        Configured logger instance.
    """
    return logging.getLogger(name)
