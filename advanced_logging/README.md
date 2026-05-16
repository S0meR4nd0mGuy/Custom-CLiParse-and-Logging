# Advanced Logging

An advanced hand-made logging module providing easy-to-use logging functionality with support for multiple log levels, colored output, file rotation, structured logging, and extensive customization.

## Features

- 🎨 **Colored Console Output** - Auto-detects terminal support with ANSI colors
- 📝 **Multiple Log Levels** - DEBUG, INFO, WARNING, ERROR, CRITICAL
- 🔄 **File Rotation** - Automatic log file rotation by size
- 📊 **Structured Logging** - JSON output support via StructuredFormatter
- 🧵 **Thread-Safe** - Safe for multi-threaded applications
- 🎯 **Context Managers** - Inject contextual data into logs with LogContext
- 🎨 **Flexible Formatting** - 5 built-in formats (simple, standard, detailed, full, minimal) + custom support
- 🚀 **Zero Dependencies** - Pure Python stdlib

## Installation

```bash
pip install -e .
```

## Quick Start

```python
from advanced_logging import get_logger

# One-line setup
logger = get_logger("myapp")
logger.info("Hello, world!")

# With file logging
logger = get_logger("myapp", file="app.log")
logger.error("Something went wrong!")

# Different format styles
logger = get_logger("myapp", format_style="detailed")
logger.debug("Debug information")
```

## Usage Examples

### Basic Logging

```python
from advanced_logging import get_logger

logger = get_logger("myapp")

logger.debug("Debug message")
logger.info("Info message")
logger.warning("Warning message")
logger.error("Error message")
logger.critical("Critical message")
```

### Logging with Extra Data

```python
logger = get_logger("myapp")

# Extra data is appended to message
logger.info("User logged in", user_id=123, ip="192.168.1.1")
# Output: "User logged in | {'user_id': 123, 'ip': '192.168.1.1'}"
```

### File Logging with Rotation

```python
from advanced_logging import get_logger

logger = get_logger("myapp")
logger.add_rotating_file_handler(
    "app.log",
    max_bytes=10_000_000,  # 10MB
    backup_count=5
)
logger.info("This will rotate when file reaches 10MB")
```

### Structured JSON Logging

```python
from advanced_logging import get_logger

logger = get_logger("myapp")
logger.add_json_handler("structured.json")
logger.info("User login", user_id=123, ip="192.168.1.1")
```

### Context Managers for Request Tracking

```python
from advanced_logging import get_logger, LogContext

logger = get_logger("myapp")

with LogContext(request_id="req-001", user="alice"):
    logger.info("Processing request")  # Automatically includes context
    logger.debug("Validation passed")
```

### Exception Logging

```python
logger = get_logger("myapp")

try:
    result = 10 / 0
except ZeroDivisionError:
    logger.exception("Mathematical operation failed")
    # Automatically includes full traceback
```

## Format Styles

Five built-in format styles:

- **simple**: `INFO - Message`
- **standard**: `[2026-05-16 10:30:45.123] INFO     - myapp - Message`
- **detailed**: `[2026-05-16 10:30:45.123] INFO     - myapp - script.py:42 - Message`
- **full**: `[2026-05-16 10:30:45.123] INFO     - myapp - script.py:function_name:42 - Message`
  - If called from top-level (not inside a function), shows `N/A` instead of function name
- **minimal**: `INFO | Message`

```python
# Use predefined styles
logger = get_logger("app", format_style="detailed")

# Or create custom format
from advanced_logging import Formatter
fmt = Formatter("{timestamp} [{level_name}] {message}")
```

## API Reference

### get_logger()

```python
get_logger(
    name: str,                          # Logger name (hierarchical: "app.database")
    level: LogLevel = LogLevel.DEBUG,   # Minimum log level
    console: bool = True,               # Add console handler
    file: Optional[str] = None,         # Optional log file path
    format_style: str = "standard"      # Format style name
) -> Logger
```

### Logger Methods

**Logging methods:**
- `logger.debug(message, **kwargs)` - Debug level
- `logger.info(message, **kwargs)` - Info level
- `logger.warning(message, **kwargs)` - Warning level
- `logger.error(message, exc_info=False, **kwargs)` - Error level
- `logger.critical(message, exc_info=False, **kwargs)` - Critical level
- `logger.exception(message, **kwargs)` - Error with automatic traceback

**Handler methods:**
- `logger.add_handler(handler)` - Add custom handler
- `logger.add_console_handler(level, format_style, use_colors)` - Add console output
- `logger.add_file_handler(filename, level, format_style)` - Add file output
- `logger.add_rotating_file_handler(filename, level, format_style, max_bytes, backup_count)`
- `logger.add_json_handler(filename, level)` - Add JSON structured output
- `logger.set_level(level)` - Change logging level
- `logger.add_filter(filter_func)` - Add filter to all handlers

### LogLevel

```python
from advanced_logging import LogLevel

LogLevel.DEBUG      # 10 - Detailed diagnostic info
LogLevel.INFO       # 20 - Confirmation messages
LogLevel.WARNING    # 30 - Warning messages
LogLevel.ERROR      # 40 - Error messages
LogLevel.CRITICAL   # 50 - Critical failures
```

### LogContext

```python
from advanced_logging import LogContext

with LogContext(request_id="123", user="alice"):
    logger.info("Processing")  # Includes context data
```

### LoggerManager

Global logger management:

```python
from advanced_logging import LoggerManager

LoggerManager.set_global_level(LogLevel.WARNING)  # Set level for all loggers
LoggerManager.disable_colors()                    # Disable ANSI colors globally
LoggerManager.list_loggers()                      # List all logger names
```

## Advanced Features

### Hierarchical Loggers

```python
# Create related loggers
db_logger = get_logger("myapp.database")
api_logger = get_logger("myapp.api")
cache_logger = get_logger("myapp.cache")

db_logger.info("Connected to database")
api_logger.info("API server started")
```

### Multiple Handlers

```python
logger = get_logger("app", console=True)

# Add file handler
logger.add_file_handler("app.log")

# Add rotating handler
logger.add_rotating_file_handler("app_rotating.log", max_bytes=10_000_000, backup_count=5)

# Add JSON handler
logger.add_json_handler("app.json")

# All handlers receive all log messages at their configured level
```

### Custom Handlers

```python
from advanced_logging import Handler, LogRecord

class MyCustomHandler(Handler):
    def emit(self, record: LogRecord) -> None:
        # Custom handling logic
        formatted = self.formatter.format(record)
        # Send to external service, database, etc.
        pass

logger = get_logger("app")
logger.add_handler(MyCustomHandler())
```

### Filtering

```python
def errors_only(record):
    return record.level >= LogLevel.ERROR

logger = get_logger("app")
logger.add_filter(errors_only)
```

### Custom Formatting

```python
from advanced_logging import Formatter

# Custom format string
custom_fmt = Formatter(
    "{timestamp} | {level_name:8} | {logger_name} | {message}",
    use_colors=True
)

# Available format fields:
# {timestamp}, {level_name}, {logger_name}, {message}
# {file_name}, {function_name}, {function_display}, {line_number}
# {module_name}, {thread_name}, {thread_id}, {process_id}
```

## Common Patterns

### Application Setup

```python
def setup_logging(debug=False):
    level = LogLevel.DEBUG if debug else LogLevel.INFO
    
    logger = get_logger("myapp", level=level, console=True)
    logger.add_rotating_file_handler("logs/app.log", max_bytes=10_000_000, backup_count=5)
    
    if debug:
        logger.add_file_handler("logs/debug.log", level=LogLevel.DEBUG, format_style="full")
    
    return logger

logger = setup_logging(debug=True)
```

### Request Tracking

```python
logger = get_logger("web_app")

def handle_request(request):
    with LogContext(request_id=request.id, user=request.user):
        logger.info("Request received")
        
        try:
            result = process_request()
            logger.info("Request processed successfully")
            return result
        except Exception:
            logger.exception("Request processing failed")
            raise
```

### Separate Error Logs

```python
from advanced_logging import FileHandler, LogLevel, Formatter

logger = get_logger("app", console=False)

# General log
logger.add_file_handler("logs/app.log", LogLevel.INFO)

# Error-only log
error_handler = FileHandler(
    "logs/errors.log",
    level=LogLevel.ERROR,
    formatter=Formatter("full", use_colors=False)
)
logger.add_handler(error_handler)
```

## Notes

- **Extra kwargs**: When you pass `**kwargs` to logging methods, they're formatted as `" | {dict}"` and appended to the message
- **Function names**: Top-level code (not in a function) shows `N/A` in `full` format instead of `<module>`
- **Colors**: Automatically disabled for file handlers; colors only appear in console output
- **Thread-safety**: All handlers use threading locks for safe concurrent logging

## License

Custom License - See LICENSE file for details.

## Author

S0meR4nd0mGuy

Version: 1.0.0