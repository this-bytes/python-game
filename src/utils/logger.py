"""Logging configuration and utilities for the cybersecurity firm game.

This module provides centralized logging setup with different levels for
game events, debugging, and performance metrics. Features include:
- Color-coded console output for visual debugging
- Rotating file handlers to prevent log bloat
- Structured logging with context
- Exception tracking with full stack traces
- Performance monitoring
"""

import logging
import os
import sys
import traceback
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
from logging.handlers import RotatingFileHandler
import threading


# ANSI color codes for console output
class Colors:
    """ANSI color codes for terminal output."""
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    
    # Foreground colors
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    
    # Bright foreground colors
    BRIGHT_BLACK = '\033[90m'
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'
    BRIGHT_WHITE = '\033[97m'
    
    # Background colors
    BG_BLACK = '\033[40m'
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'
    BG_BLUE = '\033[44m'


# Log level mapping
LOG_LEVELS = {
    'DEBUG': logging.DEBUG,
    'INFO': logging.INFO,
    'WARNING': logging.WARNING,
    'ERROR': logging.ERROR,
    'CRITICAL': logging.CRITICAL
}


class ColoredFormatter(logging.Formatter):
    """Custom formatter with color-coded output for console."""
    
    # Color mapping for log levels
    LEVEL_COLORS = {
        logging.DEBUG: Colors.BRIGHT_BLACK,
        logging.INFO: Colors.BRIGHT_BLUE,
        logging.WARNING: Colors.BRIGHT_YELLOW,
        logging.ERROR: Colors.BRIGHT_RED,
        logging.CRITICAL: f"{Colors.BG_RED}{Colors.BRIGHT_WHITE}{Colors.BOLD}",
    }
    
    # Component color mapping (can be extended)
    COMPONENT_COLORS = {
        'GAME': Colors.BRIGHT_MAGENTA,
        'UI': Colors.BRIGHT_CYAN,
        'SYSTEM': Colors.BRIGHT_GREEN,
        'PLUGIN': Colors.GREEN,
        'BACKEND': Colors.YELLOW,
        'SAVE': Colors.BLUE,
        'EVENT': Colors.MAGENTA,
        'PERFORMANCE': Colors.CYAN,
    }
    
    def __init__(self, *args, use_colors=True, **kwargs):
        """Initialize colored formatter.
        
        Args:
            use_colors: Whether to use ANSI colors in output
        """
        super().__init__(*args, **kwargs)
        self.use_colors = use_colors
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record with colors.
        
        Args:
            record: Log record to format
            
        Returns:
            Formatted log string with ANSI colors
        """
        if not self.use_colors:
            return super().format(record)
        
        # Get level color
        level_color = self.LEVEL_COLORS.get(record.levelno, '')
        
        # Extract component from message if present [COMPONENT]
        message = record.getMessage()
        component_color = ''
        
        for component, color in self.COMPONENT_COLORS.items():
            if f"[{component}]" in message:
                component_color = color
                break
        
        # Format the record
        record_copy = logging.makeLogRecord(record.__dict__)
        
        # Add colors
        original_levelname = record_copy.levelname
        record_copy.levelname = f"{level_color}{original_levelname:8}{Colors.RESET}"
        
        # Apply component color to message if found
        if component_color:
            record_copy.msg = f"{component_color}{record.msg}{Colors.RESET}"
        
        formatted = super().format(record_copy)
        
        return formatted


def setup_logging(
    log_level: str = 'INFO',
    log_file: Optional[str] = None,
    log_to_console: bool = True,
    log_format: Optional[str] = None,
    use_colors: bool = True,
    max_file_size: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5
) -> logging.Logger:
    """Setup logging configuration for the game.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file (optional). If None, only console logging
        log_to_console: Whether to output logs to console
        log_format: Custom log format string (optional)
        use_colors: Whether to use colored output in console
        max_file_size: Maximum size of log file before rotation (bytes)
        backup_count: Number of backup log files to keep
        
    Returns:
        Configured root logger
    """
    # Get log level from environment or use provided
    level_str = os.getenv('LOG_LEVEL', log_level).upper()
    level = LOG_LEVELS.get(level_str, logging.INFO)
    
    # Default log format with more detail
    if log_format is None:
        log_format = '%(asctime)s | %(levelname)s | %(name)s | %(message)s'
    
    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    
    # Remove any existing handlers
    root_logger.handlers.clear()
    
    # Add console handler if requested
    if log_to_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        
        # Use colored formatter for console
        console_formatter = ColoredFormatter(
            log_format, 
            datefmt='%H:%M:%S',
            use_colors=use_colors
        )
        console_handler.setFormatter(console_formatter)
        root_logger.addHandler(console_handler)
    
    # Add rotating file handler if log file specified
    if log_file:
        # Create logs directory if it doesn't exist
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Use rotating file handler to prevent log bloat
        file_handler = RotatingFileHandler(
            log_file, 
            mode='a', 
            maxBytes=max_file_size,
            backupCount=backup_count,
            encoding='utf-8'
        )
        file_handler.setLevel(level)
        
        # File logs don't need colors
        file_formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(name)-20s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)
        
        root_logger.info(f"[SYSTEM] Logging to file: {log_file}")
    
    root_logger.info(f"[SYSTEM] Logging initialized at level: {level_str}")
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
    log_message = f"[EVENT] [{event_type}] {message}"
    
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


def log_exception(logger: logging.Logger, operation: str, exception: Exception, 
                 context: Optional[Dict[str, Any]] = None):
    """Log an exception with full context and stack trace.
    
    Args:
        logger: Logger instance to use
        operation: What operation was being performed when exception occurred
        exception: The exception that was raised
        context: Additional context dictionary (optional)
    """
    # Get exception info
    exc_type, exc_value, exc_traceback = sys.exc_info()
    
    # Format stack trace
    stack_trace = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
    
    # Build context string
    context_str = ""
    if context:
        context_str = "\nContext:\n" + '\n'.join(f"  {k}: {v}" for k, v in context.items())
    
    log_message = (
        f"[ERROR] Exception during {operation}\n"
        f"Exception Type: {type(exception).__name__}\n"
        f"Exception Message: {str(exception)}"
        f"{context_str}\n"
        f"Stack Trace:\n{stack_trace}"
    )
    
    logger.error(log_message)


class ContextLogger:
    """Context manager for logging operations with timing and exception handling."""
    
    def __init__(self, logger: logging.Logger, operation: str, 
                 log_start: bool = True, log_end: bool = True,
                 level: int = logging.INFO):
        """Initialize context logger.
        
        Args:
            logger: Logger instance to use
            operation: Name of the operation being logged
            log_start: Whether to log when entering context
            log_end: Whether to log when exiting context
            level: Logging level to use
        """
        self.logger = logger
        self.operation = operation
        self.log_start = log_start
        self.log_end = log_end
        self.level = level
        self.start_time = None
        self.context_data: Dict[str, Any] = {}
    
    def __enter__(self):
        """Enter the context."""
        if self.log_start:
            self.logger.log(self.level, f"[SYSTEM] Starting: {self.operation}")
        self.start_time = datetime.now()
        return self
    
    def __exit__(self, exc_type, exc_value, exc_traceback):
        """Exit the context, logging duration and any exceptions."""
        if self.start_time is None:
            self.start_time = datetime.now()
        duration_ms = (datetime.now() - self.start_time).total_seconds() * 1000
        
        if exc_type is not None:
            # Exception occurred
            log_exception(
                self.logger, 
                self.operation, 
                exc_value,
                context={
                    'duration_ms': f"{duration_ms:.2f}",
                    **self.context_data
                }
            )
            return False  # Don't suppress exception
        
        if self.log_end:
            self.logger.log(
                self.level, 
                f"[SYSTEM] Completed: {self.operation} ({duration_ms:.2f}ms)"
            )
        
        return False
    
    def add_context(self, key: str, value: Any):
        """Add context data to be logged on exit.
        
        Args:
            key: Context key
            value: Context value
        """
        self.context_data[key] = value


class GameLogger:
    """Convenience wrapper for game-specific logging with enhanced features."""
    
    def __init__(self, name: str):
        """Initialize game logger.
        
        Args:
            name: Name for the logger
        """
        self.logger = get_logger(name)
        self._operation_stack = []  # Track nested operations
    
    def debug(self, message: str, **kwargs):
        """Log debug message with optional context.
        
        Args:
            message: Debug message
            **kwargs: Additional context
        """
        if kwargs:
            context_str = ' | ' + ', '.join(f"{k}={v}" for k, v in kwargs.items())
            message += context_str
        self.logger.debug(message)
    
    def info(self, message: str, **kwargs):
        """Log info message with optional context.
        
        Args:
            message: Info message
            **kwargs: Additional context
        """
        if kwargs:
            context_str = ' | ' + ', '.join(f"{k}={v}" for k, v in kwargs.items())
            message += context_str
        self.logger.info(message)
    
    def warning(self, message: str, **kwargs):
        """Log warning message with optional context.
        
        Args:
            message: Warning message
            **kwargs: Additional context
        """
        if kwargs:
            context_str = ' | ' + ', '.join(f"{k}={v}" for k, v in kwargs.items())
            message += context_str
        self.logger.warning(message)
    
    def error(self, message: str, exception: Optional[Exception] = None, **kwargs):
        """Log error message with optional exception and context.
        
        Args:
            message: Error message
            exception: Optional exception to log
            **kwargs: Additional context
        """
        if kwargs:
            context_str = ' | ' + ', '.join(f"{k}={v}" for k, v in kwargs.items())
            message += context_str
        
        if exception:
            log_exception(self.logger, message, exception, context=kwargs)
        else:
            self.logger.error(message)
    
    def critical(self, message: str, exception: Optional[Exception] = None, **kwargs):
        """Log critical message with optional exception and context.
        
        Args:
            message: Critical message
            exception: Optional exception to log
            **kwargs: Additional context
        """
        if kwargs:
            context_str = ' | ' + ', '.join(f"{k}={v}" for k, v in kwargs.items())
            message += context_str
        
        if exception:
            log_exception(self.logger, message, exception, context=kwargs)
        else:
            self.logger.critical(message)
    
    def operation(self, operation_name: str, log_start: bool = True, 
                 log_end: bool = True) -> ContextLogger:
        """Create a context manager for logging an operation.
        
        Args:
            operation_name: Name of the operation
            log_start: Whether to log when starting operation
            log_end: Whether to log when completing operation
            
        Returns:
            ContextLogger instance for use with 'with' statement
            
        Example:
            with logger.operation("Loading game data"):
                # Do work
                pass
        """
        return ContextLogger(self.logger, operation_name, log_start, log_end)
    
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

    def __getattr__(self, name: str):
        """Delegate attribute access to the underlying stdlib logger.

        This allows callers to use either the convenience wrapper methods
        (e.g., game_logger.info(...)) or to access standard Logger
        attributes/methods when necessary (e.g., game_logger.setLevel).
        """
        # Fallback to underlying logger for any unknown attribute
        return getattr(self.logger, name)
