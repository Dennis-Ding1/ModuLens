"""
Logging utilities for ModuLens.
"""

import logging
import os
import time
import json
from typing import Dict, Any, Optional

class Logger:
    """
    Logger class for ModuLens that handles both console and file logging.
    """
    
    def __init__(self, log_dir: str = "logs", level: str = "INFO"):
        """
        Initialize the logger.
        
        Args:
            log_dir: Directory to store log files
            level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        """
        self.log_dir = log_dir
        
        # Create log directory if it doesn't exist
        if not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)
        
        # Set up logging
        self.logger = logging.getLogger("modulens")
        numeric_level = getattr(logging, level.upper(), logging.INFO)
        self.logger.setLevel(numeric_level)
        
        # Clear existing handlers to avoid duplicate logging
        if self.logger.handlers:
            self.logger.handlers.clear()
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(numeric_level)
        console_format = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        console_handler.setFormatter(console_format)
        self.logger.addHandler(console_handler)
        
        # File handler
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        log_file = os.path.join(log_dir, f"modulens_{timestamp}.log")
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(numeric_level)
        file_format = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        file_handler.setFormatter(file_format)
        self.logger.addHandler(file_handler)
    
    def debug(self, message: str):
        """Log a debug message."""
        self.logger.debug(message)
    
    def info(self, message: str):
        """Log an info message."""
        self.logger.info(message)
    
    def warning(self, message: str):
        """Log a warning message."""
        self.logger.warning(message)
    
    def error(self, message: str):
        """Log an error message."""
        self.logger.error(message)
    
    def critical(self, message: str):
        """Log a critical message."""
        self.logger.critical(message)
    
    def log_strategy_attempt(self, strategy: str, prompt: str, result: Dict[str, Any], 
                            original_prompt: Optional[str] = None):
        """
        Log a strategy attempt to a structured log file.
        
        Args:
            strategy: Name of the strategy used
            prompt: Transformed prompt
            result: Result of the strategy attempt
            original_prompt: Original user prompt (optional)
        """
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        log_entry = {
            "timestamp": timestamp,
            "strategy": strategy,
            "original_prompt": original_prompt,
            "transformed_prompt": prompt,
            "result": result
        }
        
        # Create strategy log directory if it doesn't exist
        strategy_log_dir = os.path.join(self.log_dir, "strategies")
        if not os.path.exists(strategy_log_dir):
            os.makedirs(strategy_log_dir, exist_ok=True)
        
        # Write to strategy log file
        log_file = os.path.join(strategy_log_dir, f"{strategy}_{timestamp}.json")
        try:
            with open(log_file, 'w') as f:
                json.dump(log_entry, f, indent=2)
        except Exception as e:
            self.error(f"Failed to write strategy log: {str(e)}")
            
        # Log basic info to main logger
        success = not result.get("is_blocked", True)
        status = "SUCCESS" if success else "FAILED"
        self.info(f"Strategy {strategy} - {status}")
        
    def log_session(self, queries: list):
        """
        Log a full session of queries to a structured log file.
        
        Args:
            queries: List of query dictionaries
        """
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        log_entry = {
            "timestamp": timestamp,
            "session_id": f"session_{timestamp}",
            "queries": queries
        }
        
        # Create sessions log directory if it doesn't exist
        sessions_log_dir = os.path.join(self.log_dir, "sessions")
        if not os.path.exists(sessions_log_dir):
            os.makedirs(sessions_log_dir, exist_ok=True)
        
        # Write to session log file
        log_file = os.path.join(sessions_log_dir, f"session_{timestamp}.json")
        try:
            with open(log_file, 'w') as f:
                json.dump(log_entry, f, indent=2)
        except Exception as e:
            self.error(f"Failed to write session log: {str(e)}")
            
        self.info(f"Session logged with {len(queries)} queries") 