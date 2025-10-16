"""Logging configuration and utilities for the cybersecurity firm game.

This module provides centralized logging setup with different levels for
game events, debugging, and performance metrics.
"""

import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional


# Log level mapping
LOG_LEVELS = {
    'DEBUG': logging.DEBUG,
    'INFO': logging.INFO,
    'WARNING': logging.WARNING,
    'ERROR': logging.ERROR,
    'CRITICAL': logging.CRITICAL
}


def setup_logging(
    log_level: str = 'INFO',
    log_file: Optional[str] = None,
    log_to_console: bool = True,
    log_format: Optional[str] = None
) -> logging.Logger:
    """Setup logging configuration for the game.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file (optional). If None, only console logging
        log_to_console: Whether to output logs to console
        log_format: Custom log format string (optional)
        
    Returns:
        Configured root logger
    """
    # Get log level from environment or use provided
    level_str = os.getenv('LOG_LEVEL', log_level).upper()
    level = LOG_LEVELS.get(level_str, logging.INFO)
    
    # Default log format
    if log_format is None:
        log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # Create formatter
    formatter = logging.Formatter(log_format, datefmt='%Y-%m-%d %H:%M:%S')
    
    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    
    # Remove any existing handlers
    root_logger.handlers.clear()
    
    # Add console handler if requested
    if log_to_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)
    
    # Add file handler if log file specified
    if log_file:
        # Create logs directory if it doesn't exist
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file, mode='a', encoding='utf-8')
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
        
        root_logger.info(f"Logging to file: {log_file}")
    
    root_logger.info(f"Logging initialized at level: {level_str}")
    return root_logger


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance with the specified name.
    
    Args:
        name: Name for the logger (typically __name__)
        
    Returns:
        Logger instance
    """
    return logging.getLogger(name)


def log_game_event(logger: logging.Logger, event_type: str, message: str, **kwargs):
    """Log a game event with structured data.
    
    Args:
        logger: Logger instance to use
        event_type: Type of event (e.g., 'INCIDENT_SPAWN', 'ASSIGNMENT', 'RESOLUTION')
        message: Event message
        **kwargs: Additional structured data to log
    """
    extra_data = ', '.join(f"{k}={v}" for k, v in kwargs.items())
    log_message = f"[{event_type}] {message}"
    
    if extra_data:
        log_message += f" | {extra_data}"
    
    logger.info(log_message)


def log_performance(logger: logging.Logger, operation: str, duration_ms: float, **kwargs):
    """Log performance metrics for an operation.
    
    Args:
        logger: Logger instance to use
        operation: Name of the operation
        duration_ms: Duration in milliseconds
        **kwargs: Additional metrics
    """
    extra_data = ', '.join(f"{k}={v}" for k, v in kwargs.items())
    log_message = f"[PERFORMANCE] {operation}: {duration_ms:.2f}ms"
    
    if extra_data:
        log_message += f" | {extra_data}"
    
    logger.debug(log_message)


class GameLogger:
    """Convenience wrapper for game-specific logging."""
    
    def __init__(self, name: str):
        """Initialize game logger.
        
        Args:
            name: Name for the logger
        """
        self.logger = get_logger(name)
    
    def incident_spawned(self, incident_id: str, incident_type: str, difficulty: int, 
                        client_id: str):
        """Log incident spawn event."""
        log_game_event(
            self.logger,
            'INCIDENT_SPAWN',
            f"Incident {incident_id} spawned",
            type=incident_type,
            difficulty=difficulty,
            client=client_id
        )
    
    def incident_assigned(self, incident_id: str, specialist_id: str):
        """Log incident assignment event."""
        log_game_event(
            self.logger,
            'ASSIGNMENT',
            f"Incident {incident_id} assigned to {specialist_id}",
            incident=incident_id,
            specialist=specialist_id
        )
    
    def incident_resolved(self, incident_id: str, specialist_id: str, success: bool,
                         sla_met: bool, reward: int, xp: int):
        """Log incident resolution event."""
        log_game_event(
            self.logger,
            'RESOLUTION',
            f"Incident {incident_id} resolved by {specialist_id}",
            success=success,
            sla_met=sla_met,
            reward=reward,
            xp=xp
        )
    
    def specialist_leveled(self, specialist_id: str, old_level: int, new_level: int,
                          new_xp: int):
        """Log specialist level-up event."""
        log_game_event(
            self.logger,
            'LEVEL_UP',
            f"Specialist {specialist_id} leveled up",
            old_level=old_level,
            new_level=new_level,
            xp=new_xp
        )
    
    def automation_unlocked(self, specialist_id: str, script_id: str, level: int):
        """Log automation script unlock event."""
        log_game_event(
            self.logger,
            'AUTOMATION_UNLOCK',
            f"Specialist {specialist_id} unlocked automation {script_id}",
            specialist=specialist_id,
            script=script_id,
            level=level
        )
    
    def automation_triggered(self, script_id: str, incident_id: str, specialist_id: str):
        """Log automation script trigger event."""
        log_game_event(
            self.logger,
            'AUTOMATION_TRIGGER',
            f"Automation {script_id} assigned {incident_id} to {specialist_id}",
            script=script_id,
            incident=incident_id,
            specialist=specialist_id
        )
