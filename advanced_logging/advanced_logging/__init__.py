"""
An advanced hand-made logging module providing easy-to-use logging functionality
with support for multiple log levels, multiple loggers, rich formatting, colored output,
rotating files, structured logging, context injection, and extensive customization.

Designed to be simple for basic use but powerful for advanced scenarios.
No external dependencies - pure Python stdlib.

Quick Start:
    from advanced_logging import get_logger
    
    # One-line setup for console logging
    logger = get_logger("myapp")
    logger.info("Hello, world!")
    
    # Add file logging
    logger.add_file_handler("app.log")
    
    # Hierarchical loggers
    db_logger = get_logger("myapp.database")
    api_logger = get_logger("myapp.api")
"""

__version__ = "1.0.0"
__author__ = "S0meR4nd0mGuy"
__all__ = [
    "get_logger",
    "Logger",
    "LoggerManager",
    "LogLevel",
    "Handler",
    "ConsoleHandler",
    "FileHandler",
    "RotatingFileHandler",
    "Formatter",
    "LogContext",
]

import sys
import os
import time
import json
import traceback
import threading
from pathlib import Path
from datetime import datetime
from enum import IntEnum
from typing import Optional, Any, Dict, List, Callable, Union
from dataclasses import dataclass, asdict
from collections import defaultdict
import queue


class LogLevel(IntEnum):
    """Log level enumeration."""
    DEBUG = 10
    INFO = 20
    WARNING = 30
    ERROR = 40
    CRITICAL = 50


class Color:
    """ANSI color codes for terminal output."""
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    ITALIC = "\033[3m"
    UNDERLINE = "\033[4m"
    
    # Foreground colors
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    
    # Background colors
    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_YELLOW = "\033[43m"
    BG_BLUE = "\033[44m"
    
    @staticmethod
    def disable():
        """Disable all colors."""
        Color.RESET = ""
        Color.BOLD = ""
        Color.DIM = ""
        Color.RED = ""
        Color.GREEN = ""
        Color.YELLOW = ""
        Color.BLUE = ""
        Color.MAGENTA = ""
        Color.CYAN = ""
        Color.WHITE = ""
        Color.BG_RED = ""
        Color.BG_GREEN = ""
        Color.BG_YELLOW = ""


@dataclass
class LogRecord:
    """A single log record containing all log information."""
    timestamp: float
    level: int
    level_name: str
    logger_name: str
    message: str
    module_name: str
    file_name: str
    function_name: Optional[str]
    line_number: int
    thread_name: str
    thread_id: int
    process_id: int
    extra: Dict[str, Any]
    exception_info: Optional[tuple] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert record to dictionary for JSON serialization."""
        data = asdict(self)
        data["timestamp"] = datetime.fromtimestamp(self.timestamp).isoformat()
        data["exception_info"] = str(self.exception_info) if self.exception_info else None
        return data


class Formatter:
    """Formats log records into readable strings."""
    
    # Predefined format strings
    FORMATS = {
        "simple": "{level_name} - {message}",
        "standard": "[{timestamp}] {level_name:8} - {logger_name} - {message}",
        "detailed": "[{timestamp}] {level_name:8} - {logger_name} - {file_name}:{line_number} - {message}",
        "full": "[{timestamp}] {level_name:8} - {logger_name} - {file_name}:{function_display}:{line_number} - {message}",
        "minimal": "{level_name} | {message}",
    }
    
    def __init__(self, fmt: str = "standard", use_colors: bool = True):
        """
        Initialize formatter.
        
        Args:
            fmt: Format string (predefined name or custom format)
            use_colors: Whether to use ANSI colors in output
        """
        self.fmt = self.FORMATS.get(fmt, fmt)
        self.use_colors = use_colors
        self.level_colors = {
            "DEBUG": Color.CYAN,
            "INFO": Color.GREEN,
            "WARNING": Color.YELLOW,
            "ERROR": Color.RED,
            "CRITICAL": Color.BG_RED + Color.WHITE,
        }
    
    def format(self, record: LogRecord) -> str:
        """Format a log record."""
        timestamp = datetime.fromtimestamp(record.timestamp).strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        
        level_name = record.level_name
        if self.use_colors:
            level_name = f"{self.level_colors.get(record.level_name, '')}{level_name}{Color.RESET}"
        
        # Determine function display: use function name if available, otherwise "N/A"
        function_display = record.function_name if record.function_name else "N/A"
        
        try:
            formatted = self.fmt.format(
                timestamp=timestamp,
                level_name=level_name,
                logger_name=record.logger_name,
                message=record.message,
                module_name=record.module_name,
                file_name=record.file_name,
                function_name=record.function_name or "N/A",
                function_display=function_display,
                line_number=record.line_number,
                thread_name=record.thread_name,
                thread_id=record.thread_id,
                process_id=record.process_id,
            )
        except KeyError as e:
            formatted = f"Format Error: {e} - {record.message}"
        
        # Append exception info if present
        if record.exception_info:
            exc_text = "".join(traceback.format_exception(*record.exception_info))
            formatted += f"\n{exc_text}"
        
        return formatted


class Handler:
    """Base class for log handlers."""
    
    def __init__(self, level: LogLevel = LogLevel.DEBUG, formatter: Optional[Formatter] = None):
        self.level = level
        self.formatter = formatter or Formatter()
        self.filters: List[Callable[[LogRecord], bool]] = []
    
    def handle(self, record: LogRecord) -> None:
        """Handle a log record."""
        if record.level < self.level:
            return
        
        # Apply filters
        for filter_func in self.filters:
            if not filter_func(record):
                return
        
        self.emit(record)
    
    def emit(self, record: LogRecord) -> None:
        """Emit the log record (to be overridden by subclasses)."""
        raise NotImplementedError
    
    def add_filter(self, filter_func: Callable[[LogRecord], bool]) -> None:
        """Add a filter function."""
        self.filters.append(filter_func)
    
    def set_formatter(self, formatter: Formatter) -> None:
        """Set the formatter."""
        self.formatter = formatter


class ConsoleHandler(Handler):
    """Handler that outputs to console (stdout/stderr)."""
    
    def __init__(self, level: LogLevel = LogLevel.DEBUG, formatter: Optional[Formatter] = None,
                 use_stderr_for_errors: bool = True):
        super().__init__(level, formatter)
        self.use_stderr_for_errors = use_stderr_for_errors
    
    def emit(self, record: LogRecord) -> None:
        """Output to console."""
        msg = self.formatter.format(record)
        stream = sys.stderr if (self.use_stderr_for_errors and record.level >= LogLevel.ERROR) else sys.stdout
        print(msg, file=stream)


class FileHandler(Handler):
    """Handler that outputs to a file."""
    
    def __init__(self, filename: str, level: LogLevel = LogLevel.DEBUG,
                 formatter: Optional[Formatter] = None, mode: str = "a"):
        super().__init__(level, formatter)
        self.filename = Path(filename)
        self.filename.parent.mkdir(parents=True, exist_ok=True)
        self.mode = mode
        self._lock = threading.Lock()
    
    def emit(self, record: LogRecord) -> None:
        """Write to file."""
        msg = self.formatter.format(record)
        with self._lock:
            with open(self.filename, self.mode, encoding="utf-8") as f:
                f.write(msg + "\n")


class RotatingFileHandler(Handler):
    """Handler that rotates log files by size or time."""
    
    def __init__(self, filename: str, level: LogLevel = LogLevel.DEBUG,
                 formatter: Optional[Formatter] = None, max_bytes: int = 10_000_000,
                 backup_count: int = 5):
        super().__init__(level, formatter)
        self.filename = Path(filename)
        self.filename.parent.mkdir(parents=True, exist_ok=True)
        self.max_bytes = max_bytes
        self.backup_count = backup_count
        self._lock = threading.Lock()
    
    def emit(self, record: LogRecord) -> None:
        """Write to file with rotation."""
        msg = self.formatter.format(record)
        with self._lock:
            # Check if rotation needed
            if self.filename.exists() and self.filename.stat().st_size >= self.max_bytes:
                self._rotate()
            
            with open(self.filename, "a", encoding="utf-8") as f:
                f.write(msg + "\n")
    
    def _rotate(self) -> None:
        """Rotate log files."""
        # Remove oldest backup if backup_count exceeded
        for i in range(self.backup_count, 0, -1):
            sfn = f"{self.filename}.{i}"
            dfn = f"{self.filename}.{i + 1}"
            if Path(sfn).exists():
                if Path(dfn).exists():
                    Path(dfn).unlink()
                Path(sfn).rename(dfn)
        
        # Rename current file to .1
        dfn = f"{self.filename}.1"
        if self.filename.exists():
            self.filename.rename(dfn)


class StructuredFormatter(Formatter):
    """Formatter that outputs JSON-structured logs."""
    
    def format(self, record: LogRecord) -> str:
        """Format record as JSON."""
        data = record.to_dict()
        return json.dumps(data, default=str)


@dataclass
class LogContext:
    """Context for injecting extra data into log records."""
    
    def __init__(self, **kwargs):
        self.data = kwargs
    
    def __enter__(self):
        LoggerManager.push_context(self)
        return self
    
    def __exit__(self, *args):
        LoggerManager.pop_context()
    
    def update(self, **kwargs):
        """Update context data."""
        self.data.update(kwargs)


class Logger:
    """A logger instance for logging messages."""
    
    def __init__(self, name: str, level: LogLevel = LogLevel.DEBUG):
        self.name = name
        self.level = level
        self.handlers: List[Handler] = []
        self._lock = threading.Lock()
    
    def _make_record(self, level: int, message: str, exc_info: Optional[tuple] = None) -> LogRecord:
        """Create a log record."""
        import inspect
        
        frame = inspect.currentframe()
        # Skip internal frames (frames from this logging module)
        while frame and frame.f_code.co_filename == __file__:
            frame = frame.f_back
        
        if frame:
            module_name = frame.f_globals.get("__name__", "unknown")
            raw_function_name = frame.f_code.co_name
            # If it's top-level module code, set function_name to None so formatter shows N/A
            function_name = raw_function_name if raw_function_name != "<module>" else None
            line_number = frame.f_lineno
            try:
                file_name = Path(frame.f_code.co_filename).name
            except Exception:
                file_name = "<unknown>"
        else:
            module_name = "unknown"
            function_name = None
            line_number = 0
            file_name = "<unknown>"
        
        # Collect extra context
        extra = {}
        for context in LoggerManager.context_stack:
            extra.update(context.data)
        
        record = LogRecord(
            timestamp=time.time(),
            level=level,
            level_name=LogLevel(level).name,
            logger_name=self.name,
            message=str(message),
            module_name=module_name,
            file_name=file_name,
            function_name=function_name,
            line_number=line_number,
            thread_name=threading.current_thread().name,
            thread_id=threading.current_thread().ident or 0,
            process_id=os.getpid(),
            extra=extra,
            exception_info=exc_info,
        )
        
        return record
    
    def _log(self, level: int, message: str, exc_info: bool = False) -> None:
        """Internal logging method."""
        if level < self.level:
            return
        
        exc_info_tuple = None
        if exc_info:
            import sys
            exc_info_tuple = sys.exc_info()
        
        record = self._make_record(level, message, exc_info_tuple)
        
        with self._lock:
            for handler in self.handlers:
                handler.handle(record)
    
    def debug(self, message: str, **kwargs) -> None:
        """Log debug message."""
        if kwargs:
            message = f"{message} | {kwargs}"
        self._log(LogLevel.DEBUG, message)
    
    def info(self, message: str, **kwargs) -> None:
        """Log info message."""
        if kwargs:
            message = f"{message} | {kwargs}"
        self._log(LogLevel.INFO, message)
    
    def warning(self, message: str, **kwargs) -> None:
        """Log warning message."""
        if kwargs:
            message = f"{message} | {kwargs}"
        self._log(LogLevel.WARNING, message)
    
    def error(self, message: str, exc_info: bool = False, **kwargs) -> None:
        """Log error message."""
        if kwargs:
            message = f"{message} | {kwargs}"
        self._log(LogLevel.ERROR, message, exc_info=exc_info)
    
    def critical(self, message: str, exc_info: bool = False, **kwargs) -> None:
        """Log critical message."""
        if kwargs:
            message = f"{message} | {kwargs}"
        self._log(LogLevel.CRITICAL, message, exc_info=exc_info)
    
    def exception(self, message: str, **kwargs) -> None:
        """Log an exception with traceback."""
        if kwargs:
            message = f"{message} | {kwargs}"
        self._log(LogLevel.ERROR, message, exc_info=True)
    
    def add_handler(self, handler: Handler) -> "Logger":
        """Add a handler to this logger."""
        self.handlers.append(handler)
        return self
    
    def add_console_handler(self, level: LogLevel = LogLevel.DEBUG,
                           format_style: str = "standard", use_colors: bool = True) -> "Logger":
        """Add a console handler."""
        formatter = Formatter(format_style, use_colors)
        handler = ConsoleHandler(level, formatter)
        return self.add_handler(handler)
    
    def add_file_handler(self, filename: str, level: LogLevel = LogLevel.DEBUG,
                        format_style: str = "standard") -> "Logger":
        """Add a file handler."""
        formatter = Formatter(format_style, use_colors=False)
        handler = FileHandler(filename, level, formatter)
        return self.add_handler(handler)
    
    def add_rotating_file_handler(self, filename: str, level: LogLevel = LogLevel.DEBUG,
                                 format_style: str = "standard", max_bytes: int = 10_000_000,
                                 backup_count: int = 5) -> "Logger":
        """Add a rotating file handler."""
        formatter = Formatter(format_style, use_colors=False)
        handler = RotatingFileHandler(filename, level, formatter, max_bytes, backup_count)
        return self.add_handler(handler)
    
    def add_json_handler(self, filename: str, level: LogLevel = LogLevel.DEBUG) -> "Logger":
        """Add a JSON structured log handler."""
        handler = FileHandler(filename, level, StructuredFormatter())
        return self.add_handler(handler)
    
    def set_level(self, level: LogLevel) -> "Logger":
        """Set the logging level."""
        self.level = level
        return self
    
    def add_filter(self, filter_func: Callable[[LogRecord], bool]) -> "Logger":
        """Add a filter to all handlers."""
        for handler in self.handlers:
            handler.add_filter(filter_func)
        return self


class LoggerManager:
    """Manages all logger instances globally."""
    
    _loggers: Dict[str, Logger] = {}
    _lock = threading.Lock()
    context_stack: List[LogContext] = []
    
    @classmethod
    def get_logger(cls, name: str, level: LogLevel = LogLevel.DEBUG) -> Logger:
        """Get or create a logger with the given name."""
        with cls._lock:
            if name not in cls._loggers:
                cls._loggers[name] = Logger(name, level)
            return cls._loggers[name]
    
    @classmethod
    def set_global_level(cls, level: LogLevel) -> None:
        """Set level for all loggers."""
        for logger in cls._loggers.values():
            logger.set_level(level)
    
    @classmethod
    def set_global_handler(cls, handler: Handler) -> None:
        """Add a handler to all existing loggers."""
        for logger in cls._loggers.values():
            logger.add_handler(handler)
    
    @classmethod
    def disable_colors(cls) -> None:
        """Disable ANSI colors globally."""
        Color.disable()
    
    @classmethod
    def push_context(cls, context: LogContext) -> None:
        """Push context onto stack."""
        cls.context_stack.append(context)
    
    @classmethod
    def pop_context(cls) -> Optional[LogContext]:
        """Pop context from stack."""
        if cls.context_stack:
            return cls.context_stack.pop()
        return None
    
    @classmethod
    def list_loggers(cls) -> List[str]:
        """List all logger names."""
        return sorted(cls._loggers.keys())


def get_logger(name: str, level: Union[int, LogLevel] = LogLevel.DEBUG,
              console: bool = True, file: Optional[str] = None,
              format_style: str = "standard") -> Logger:
    """
    Get a logger with optional handlers configured.
    
    This is the main entry point for creating loggers.
    
    Args:
        name: Logger name (use hierarchical names like "myapp.database")
        level: Minimum log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        console: Add console handler (default: True)
        file: Optional log file path (adds file handler)
        format_style: Format style name (simple, standard, detailed, full, minimal)
    
    Returns:
        Configured Logger instance
    
    Examples:
        # Basic console logging
        logger = get_logger("myapp")
        
        # With file logging
        logger = get_logger("myapp", file="app.log")
        
        # Advanced
        logger = get_logger("myapp.database", file="db.log", format_style="detailed")
    """
    if isinstance(level, int):
        level = LogLevel(level)
    
    logger = LoggerManager.get_logger(name, level)
    
    # Clear existing handlers to avoid duplicates
    if not logger.handlers:
        if console == True:
            logger.add_console_handler(level, format_style)
        
        if file:
            logger.add_file_handler(file, level, format_style)
    
    return logger


# Convenience aliases for compatibility
debug = lambda msg, **kw: get_logger("root").debug(msg, **kw)
info = lambda msg, **kw: get_logger("root").info(msg, **kw)
warning = lambda msg, **kw: get_logger("root").warning(msg, **kw)
error = lambda msg, exc=False, **kw: get_logger("root").error(msg, exc_info=exc, **kw)
critical = lambda msg, exc=False, **kw: get_logger("root").critical(msg, exc_info=exc, **kw)