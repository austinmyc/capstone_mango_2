import os
import logging
from logging.handlers import RotatingFileHandler
import sys
from datetime import datetime

def setup_logger(name='opensea_client', log_level=logging.INFO, log_file=None):
    """
    Set up and configure a logger with console and file handlers
    
    Args:
        name (str): Logger name
        log_level (int): Logging level (e.g., logging.INFO)
        log_file (str): Path to the log file (if None, a timestamped filename will be used)
        
    Returns:
        logger: Configured logger instance
    """
    # Create logs directory if it doesn't exist
    logs_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
    os.makedirs(logs_dir, exist_ok=True)
    
    # Generate timestamped log file name if not provided
    if log_file is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = f'opensea_client_{timestamp}.log'
    
    log_file_path = os.path.join(logs_dir, log_file)
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(log_level)
    
    # Only add handlers if they don't exist
    if not logger.handlers:
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Create console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        # Create file handler (rotating to keep log files from growing too large)
        file_handler = RotatingFileHandler(
            log_file_path, 
            maxBytes=5 * 1024 * 1024,  # 5 MB
            backupCount=5              # Keep 5 backup files
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    # Log the start of a new session
    logger.info(f"=== New logging session started with log file: {log_file} ===")
    
    return logger 