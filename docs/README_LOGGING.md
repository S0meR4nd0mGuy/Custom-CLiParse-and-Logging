# Advanced Logging - Complete Guide

**A production-ready logging system that's easier to use than Python's stdlib logging, with powerful features and zero external dependencies.**

## 🎯 Why Advanced Logging?

Python's `logging` module is powerful but complex:

```python
# stdlib logging - 5 lines just to get started
import logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
logger.info("Hello")

# Advanced Logging - one line!
from advanced_logging import get_logger
logger = get_logger("myapp")
logger.info("Hello")
```

## ⚡ Quick Start

### Basic Console Logging
```python
from advanced_logging import get_logger

logger = get_logger("myapp")
logger.info("Application started")
logger.debug("Debug message")
logger.warning("Warning!")
logger.error("Error occurred")
logger.critical("Critical issue!")
```

### Console + File Logging
```python
logger = get_logger("myapp", file="app.log")
logger.info("This goes to both console and file")
```

### Hierarchical Loggers
```python
# Different modules, different loggers
db_logger = get_logger("myapp.database")
api_logger = get_logger("myapp.api")
cache_logger = get_logger("myapp.cache")

db_logger.info("Connected to database")
api_logger.info("API server started")
cache_logger.debug("Cache initialized")
```

## 📚 Core Concepts

### Log Levels
```python
from advanced_logging import LogLevel

LogLevel.DEBUG = 10      # Detailed diagnostic info
LogLevel.INFO = 20       # Confirmation that things work
LogLevel.WARNING = 30    # Warning, something unexpected
LogLevel.ERROR = 40      # Error, serious problem
LogLevel.CRITICAL = 50   # Critical, system may fail
```

### Handlers
Different ways to output logs:

| Handler | Purpose | Example |
|---------|---------|---------|
| **ConsoleHandler** | Output to stdout/stderr | Real-time monitoring |
| **FileHandler** | Simple file output | Persistent storage |
| **RotatingFileHandler** | Auto-rotate by size | Long-running apps |
| **StructuredFormatter** | JSON output | Machine parsing |

### Formatters
Built-in format styles:

| Style | Output |
|-------|--------|
| `simple` | `DEBUG - Starting process` |
| `standard` | `[2024-01-15 10:30:45] DEBUG - myapp - Starting process` |
| `detailed` | `[2024-01-15 10:30:45] DEBUG - myapp - main:45 - Starting process` |
| `full` | `[2024-01-15 10:30:45] DEBUG - myapp - app.py:main:45 - Starting process` |
| `minimal` | `DEBUG \| Starting process` |

Or create custom formats:
```python
custom_format = "[{thread_name}] {level_name}: {message}"
```

## 🚀 Advanced Features

### 1. Multiple Handlers
```python
logger = get_logger("app", console=False)

# Console: only errors
from advanced_logging import ConsoleHandler, Formatter, LogLevel
console = ConsoleHandler(LogLevel.ERROR, Formatter("simple"))
logger.add_handler(console)

# File: everything
from advanced_logging import FileHandler
file_handler = FileHandler("app.log", LogLevel.DEBUG)
logger.add_handler(file_handler)

# Now errors go to console AND file, debug only to file
```

### 2. Rotating Files
```python
logger.add_rotating_file_handler(
    "app.log",
    max_bytes=10_000_000,  # 10MB
    backup_count=5         # Keep 5 backups
)
# Auto-creates: app.log, app.log.1, app.log.2, etc.
```

### 3. Structured JSON Logging
```python
logger.add_json_handler("app.json")
logger.info("User login", user_id=123, ip="192.168.1.1")
# JSON file: {"timestamp": "...", "level": "INFO", "message": "User login", "extra": {...}}
```

### 4. Log Filtering
```python
from advanced_logging import LogRecord

def important_only(record: LogRecord) -> bool:
    return "important" in record.message.lower()

logger.add_filter(important_only)
# Now only logs with "important" are output
```

### 5. Context Injection
```python
from advanced_logging import LogContext

# Request tracking
with LogContext(request_id="req-001", user="alice"):
    logger.info("Processing request")      # Contains request_id and user
    logger.debug("Validating input")       # Also contains context

# Context is automatically removed
logger.info("Request finished")            # No context
```

### 6. Exception Logging
```python
try:
    risky_operation()
except Exception:
    logger.exception("Operation failed")  # Includes traceback
```

### 7. Extra Data in Logs
```python
logger.info("User action", user_id=123, action="login", ip="192.168.1.1")
# Output: ... User action | {'user_id': 123, 'action': 'login', 'ip': '192.168.1.1'}
```

## 📖 API Reference

### `get_logger(name, level, console, file, format_style)`
Main entry point for creating loggers.

```python
logger = get_logger(
    name="myapp.database",           # Logger name
    level=LogLevel.DEBUG,            # Minimum log level
    console=True,                    # Add console output
    file="db.log",                   # Optional file path
    format_style="detailed"          # Format style
)
```

### Logger Methods

#### Basic Logging
```python
logger.debug(message, **extra_data)      # Debug level
logger.info(message, **extra_data)       # Info level
logger.warning(message, **extra_data)    # Warning level
logger.error(message, **extra_data)      # Error level
logger.critical(message, **extra_data)   # Critical level
```

#### Exception Logging
```python
try:
    something()
except:
    logger.exception("Message", **extra_data)  # Auto includes traceback
```

#### Add Handlers
```python
logger.add_handler(handler)                    # Custom handler
logger.add_console_handler(level, format)      # Console output
logger.add_file_handler(filename, level, fmt)  # File output
logger.add_rotating_file_handler(filename, max_bytes, backup_count)  # Rotating
logger.add_json_handler(filename, level)       # JSON structured
```

#### Configuration
```python
logger.set_level(LogLevel.WARNING)     # Change level
logger.add_filter(filter_function)     # Add filter
```

### Formatter
```python
from advanced_logging import Formatter

# Predefined
fmt = Formatter("detailed")

# Custom
fmt = Formatter("{level_name} | {logger_name} - {message}")

# Without colors (for files)
fmt = Formatter("standard", use_colors=False)

# Custom format fields available:
# - {timestamp}     : ISO timestamp
# - {level_name}    : DEBUG, INFO, WARNING, etc.
# - {logger_name}   : Logger name
# - {message}       : Log message
# - {function_name} : Function name
# - {line_number}   : Line number
# - {thread_name}   : Thread name
# - {thread_id}     : Thread ID
# - {process_id}    : Process ID
```

### LoggerManager
```python
from advanced_logging import LoggerManager

LoggerManager.set_global_level(LogLevel.WARNING)    # Set all loggers
LoggerManager.disable_colors()                      # No ANSI codes
LoggerManager.list_loggers()                        # All logger names
```

## 🎨 Customization

### Custom Formatters
```python
from advanced_logging import Formatter

class MyFormatter(Formatter):
    def format(self, record):
        # Custom formatting logic
        return f"🔔 {record.level_name}: {record.message}"

handler = ConsoleHandler(formatter=MyFormatter())
logger.add_handler(handler)
```

### Custom Handlers
```python
from advanced_logging import Handler

class DatabaseHandler(Handler):
    def emit(self, record):
        # Write to database
        db.insert("logs", {
            "timestamp": record.timestamp,
            "level": record.level_name,
            "message": record.message
        })

logger.add_handler(DatabaseHandler())
```

### Custom Filters
```python
def production_errors_only(record):
    return (
        record.level >= LogLevel.ERROR and
        "prod" in record.logger_name
    )

logger.add_filter(production_errors_only)
```

## 🔴 Common Patterns

### Pattern 1: App + Module Hierarchy
```python
# main.py
app_logger = get_logger("myapp", file="app.log")

# database.py
db_logger = get_logger("myapp.database")

# api.py
api_logger = get_logger("myapp.api")

# They're separate but related
# Use "myapp" root for app-level events
# Use "myapp.database" for DB-specific events
```

### Pattern 2: Development vs Production
```python
import sys

if "--prod" in sys.argv:
    logger = get_logger("app", level=LogLevel.WARNING, 
                       file="prod.log", console=False)
else:
    logger = get_logger("app", level=LogLevel.DEBUG, 
                       console=True)
```

### Pattern 3: Request Tracking
```python
from advanced_logging import LogContext

def handle_request(request):
    with LogContext(request_id=request.id, user=request.user):
        logger.info("Processing request")
        process_data()
        logger.info("Request completed")
        # Context automatically injected into all logs
```

### Pattern 4: Error Alerting
```python
error_logger = get_logger("alerts", console=False)

# Only log errors to alert handler
from advanced_logging import LogRecord
def errors_only(record: LogRecord):
    return record.level >= LogLevel.ERROR

alert_handler = ConsoleHandler(LogLevel.ERROR)
alert_handler.add_filter(errors_only)
error_logger.add_handler(alert_handler)

error_logger.error("Critical issue!")  # Goes to alert
```

## ⚙️ Configuration Examples

### Minimal (one-liner)
```python
from advanced_logging import get_logger
logger = get_logger("app")
```

### Development
```python
logger = get_logger(
    "app",
    level=LogLevel.DEBUG,
    console=True,
    format_style="detailed"
)
```

### Production
```python
logger = get_logger("app", console=False)
logger.add_file_handler("app.log", format_style="standard")
logger.add_rotating_file_handler("app_detailed.log", max_bytes=10_000_000)
logger.add_json_handler("app.json")

# Errors to console
from advanced_logging import ConsoleHandler, Formatter
console = ConsoleHandler(LogLevel.ERROR, Formatter("simple"))
logger.add_handler(console)
```

### Microservice
```python
logger = get_logger(
    "service-name",
    file="logs/service.log"
)

# JSON for central logging system
logger.add_json_handler("logs/service.json")

# Metrics logging
metrics_logger = get_logger("service-name.metrics")
```

## 🔍 Troubleshooting

### Q: Logs not appearing?
A: Check log level. Use `logger.set_level(LogLevel.DEBUG)` to see debug messages.

### Q: How to disable colors?
A: `LoggerManager.disable_colors()` or `Formatter(..., use_colors=False)`

### Q: How to log to multiple files?
A: Add multiple handlers:
```python
logger.add_file_handler("general.log")
logger.add_file_handler("errors.log")  # Different file
```

### Q: Performance impact?
A: Minimal - uses thread-safe locks only when needed. File I/O is synchronous (consider async for high-volume).

### Q: Thread-safe?
A: Yes! All operations use locks. Safe for multi-threaded applications.

## 📊 Comparison: Advanced Logging vs stdlib

| Feature | stdlib | Advanced |
|---------|--------|----------|
| **Setup** | 5+ lines | 1 line |
| **Hierarchical** | ✅ Complex API | ✅ Automatic |
| **Handlers** | ✅ Limited | ✅ Extensible |
| **Colors** | ❌ | ✅ |
| **JSON** | ❌ | ✅ |
| **Rotating** | ✅ Complex | ✅ Simple |
| **Filtering** | ✅ | ✅ |
| **Async** | ⚠️ Limited | ✅ Planned |
| **Learning Curve** | Steep | Gentle |
| **Dependencies** | None | None |

## 📁 Files

- **`advanced_logging.py`** - Main module (600+ lines)
- **`example_logging_simple.py`** - Basic usage examples
- **`example_logging_advanced.py`** - Advanced features showcase
- **`README_LOGGING.md`** - This file
- **`LOGGING_USAGE.md`** - Practical patterns and recipes

## 🎓 Examples

### Run simple examples
```bash
python example_logging_simple.py
```

### Run advanced examples
```bash
python example_logging_advanced.py
```

### Check generated log files
```bash
cat app.log
cat structured.json
```

## 🔧 Technical Details

- **Thread-safe**: All handlers use threading locks
- **No dependencies**: Pure Python stdlib only
- **Python 3.6+**: Uses f-strings and type hints
- **Memory efficient**: No buffering overhead
- **Extensible**: Custom handlers, formatters, filters

## 📝 License

Free to use and modify - educational and production-ready.

## 🚀 Next Steps

1. Read `LOGGING_USAGE.md` for patterns and recipes
2. Run `example_logging_simple.py` to see it in action
3. Try the advanced example: `example_logging_advanced.py`
4. Integrate into your project!

---

**Advanced Logging** - Making Python logging simple. 🎯
