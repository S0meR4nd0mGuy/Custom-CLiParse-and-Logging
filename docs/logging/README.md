# Advanced Logging - Complete Guide

**A production-ready logging system that's easier to use than Python's stdlib logging, with powerful features and zero external dependencies.**

## 🎯 Why Advanced Logging?

Python's `logging` module is powerful but complex. Advanced Logging is simple:

```python
# stdlib logging - 5 lines just to get started
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
logger.info("Hello")

# Advanced Logging - one line!
from advanced_logging import get_logger
logger = get_logger("myapp")
logger.info("Hello")
```

## ✨ Key Features

✅ **One-line setup** - Get started instantly  
✅ **Hierarchical loggers** - Organize by component/module  
✅ **Multiple handlers** - Console, file, rotating, JSON, custom  
✅ **Rich formatting** - 5 predefined styles + custom formats  
✅ **Advanced features** - Context injection, filtering, structured logging  
✅ **Zero dependencies** - Pure Python stdlib only  
✅ **Thread-safe** - Safe for multi-threaded applications  
✅ **Production-ready** - Used in real-world applications  

## 🚀 Quick Start

### Installation
```python
from advanced_logging import get_logger
```

### One-Line Logging
```python
logger = get_logger("myapp")
logger.info("Hello, world!")
logger.debug("Debug message")
logger.error("Error occurred")
```

### With File Logging
```python
logger = get_logger("myapp", file="app.log")
logger.info("This goes to console AND file")
```

### Hierarchical Loggers
```python
db_logger = get_logger("myapp.database")
api_logger = get_logger("myapp.api")
cache_logger = get_logger("myapp.cache")

db_logger.info("Connected to database")
api_logger.info("API server started")
```

## 📚 Complete API Reference

### get_logger() - Main Entry Point

```python
logger = get_logger(
    name="myapp",                  # Logger name (use hierarchical names)
    level=LogLevel.DEBUG,          # Minimum log level
    console=True,                  # Add console handler
    file=None,                     # Optional log file path
    format_style="standard"        # Format style
)
```

Examples:
```python
# Basic
logger = get_logger("app")

# With file
logger = get_logger("app", file="app.log")

# Different level
logger = get_logger("app", level=LogLevel.WARNING)

# Different format
logger = get_logger("app", format_style="detailed")
```

### Logger Class Methods

#### Logging Methods
```python
logger.debug(message, **extra_data)        # Debug level
logger.info(message, **extra_data)         # Info level
logger.warning(message, **extra_data)      # Warning level
logger.error(message, **extra_data)        # Error level
logger.critical(message, **extra_data)     # Critical level
logger.exception(message, **extra_data)    # Error + traceback
```

Examples:
```python
logger.info("User logged in")
logger.debug("Processing item 123", item_id=123)
logger.warning("Cache miss", key="user:456")
logger.error("Connection failed", host="db.example.com")
logger.exception("Operation crashed")
```

#### Handler Methods
```python
logger.add_handler(handler)                            # Custom handler
logger.add_console_handler(level, format_style)       # Console output
logger.add_file_handler(filename, level, format)      # File output
logger.add_rotating_file_handler(filename, max_bytes, backup_count)
logger.add_json_handler(filename, level)              # JSON structured
logger.set_level(level)                               # Change level
logger.add_filter(filter_func)                        # Add filter
```

Examples:
```python
# Add console with error level only
logger.add_console_handler(LogLevel.ERROR)

# Add file
logger.add_file_handler("app.log")

# Rotating file
logger.add_rotating_file_handler("app_detail.log", max_bytes=10_000_000, backup_count=5)

# JSON
logger.add_json_handler("app.json")

# Change level
logger.set_level(LogLevel.WARNING)

# Add filter
def errors_only(record):
    return record.level >= LogLevel.ERROR
logger.add_filter(errors_only)
```

### LogLevel Enum

```python
from advanced_logging import LogLevel

LogLevel.DEBUG = 10       # Detailed diagnostic info
LogLevel.INFO = 20        # Confirmation that things work
LogLevel.WARNING = 30     # Warning, something unexpected
LogLevel.ERROR = 40       # Error, serious problem
LogLevel.CRITICAL = 50    # Critical, system may fail
```

### Formatter Class

```python
from advanced_logging import Formatter

# Predefined styles
fmt = Formatter("simple")       # "DEBUG - Message"
fmt = Formatter("standard")     # "[2026-05-16 10:30:45] DEBUG - app - Message"
fmt = Formatter("detailed")     # Includes function and line
fmt = Formatter("full")         # Includes module info
fmt = Formatter("minimal")      # "DEBUG | Message"

# Custom format
fmt = Formatter("{level_name} | {logger_name} - {message}")

# Without colors (for files)
fmt = Formatter("standard", use_colors=False)

# Custom format fields available:
# {timestamp}      - ISO timestamp
# {level_name}     - DEBUG, INFO, etc.
# {logger_name}    - Logger name
# {message}        - Log message
# {function_name}  - Function name
# {line_number}    - Line number
# {thread_name}    - Thread name
# {thread_id}      - Thread ID
# {process_id}     - Process ID
```

### Handlers

**ConsoleHandler** - Output to stdout/stderr
```python
from advanced_logging import ConsoleHandler, Formatter

handler = ConsoleHandler(
    level=LogLevel.DEBUG,
    formatter=Formatter("standard"),
    use_stderr_for_errors=True
)
logger.add_handler(handler)
```

**FileHandler** - Simple file output
```python
from advanced_logging import FileHandler

handler = FileHandler(
    filename="app.log",
    level=LogLevel.DEBUG,
    formatter=Formatter("standard", use_colors=False)
)
logger.add_handler(handler)
```

**RotatingFileHandler** - Auto-rotate by size
```python
from advanced_logging import RotatingFileHandler

handler = RotatingFileHandler(
    filename="app.log",
    level=LogLevel.DEBUG,
    max_bytes=10_000_000,  # 10MB
    backup_count=5         # Keep 5 backups
)
logger.add_handler(handler)
# Creates: app.log, app.log.1, app.log.2, etc.
```

### Context Injection

```python
from advanced_logging import LogContext

# Track request through multiple functions
with LogContext(request_id="req-001", user="alice"):
    logger.info("Processing request")      # Includes request_id and user
    logger.debug("Validating input")       # Also includes context

# Context automatically removed
logger.info("Request finished")            # No context
```

### LoggerManager

```python
from advanced_logging import LoggerManager

LoggerManager.set_global_level(LogLevel.WARNING)    # All loggers
LoggerManager.disable_colors()                      # No ANSI codes
LoggerManager.list_loggers()                        # All logger names
```

## 🔴 Common Patterns

### Application-Wide Setup
```python
def setup_logging(debug=False):
    level = LogLevel.DEBUG if debug else LogLevel.INFO
    
    app_logger = get_logger(
        "myapp",
        level=level,
        console=True,
        file="logs/app.log",
        format_style="detailed"
    )
    
    app_logger.add_rotating_file_handler(
        "logs/app_detailed.log",
        max_bytes=10_000_000,
        backup_count=5
    )
    
    app_logger.add_json_handler("logs/app.json")
    
    return app_logger

logger = setup_logging(debug=True)
```

### Module-Level Loggers
```python
# database.py
db_logger = get_logger("myapp.database")

def connect():
    db_logger.info("Connecting to database")
    # ...
    db_logger.debug("Connection established", pool_size=10)

# api.py
api_logger = get_logger("myapp.api")

def start_server(port):
    api_logger.info(f"Starting server on port {port}")
```

### Request Tracking
```python
logger = get_logger("web_app")

def handle_request(request):
    with LogContext(request_id=request.id, user=request.user):
        logger.info("Request received")
        
        try:
            result = process_request()
            logger.info("Request processed")
            return result
        except Exception:
            logger.exception("Request failed")
            raise
```

### Error Separation
```python
app_logger = get_logger("app", console=False)

# General log
app_logger.add_file_handler("logs/app.log", LogLevel.INFO)

# Error-only log
error_handler = FileHandler("logs/errors.log", LogLevel.ERROR)
app_logger.add_handler(error_handler)

# Usage
app_logger.info("Processing")    # → logs/app.log
app_logger.error("Failed")       # → logs/app.log + logs/errors.log
```

### Conditional Logging
```python
import os

if os.getenv("ENV") == "production":
    logger = get_logger("app", console=False)
    logger.set_level(LogLevel.WARNING)
    logger.add_file_handler("logs/prod.log")
else:
    logger = get_logger("app", console=True, format_style="detailed")
    logger.set_level(LogLevel.DEBUG)
```

### JSON for Analysis
```python
logger = get_logger("service", console=False)
logger.add_json_handler("logs/service.json")

# JSON format for log aggregation/analysis
logger.info("User login", user_id=123, ip="192.168.1.1", status="success")

# Generates JSON: {"timestamp": "...", "level": "INFO", "message": "User login", "extra": {...}}
```

### Performance Monitoring
```python
import time

perf_logger = get_logger("performance")
perf_logger.add_json_handler("logs/perf.json")

start = time.time()
result = expensive_operation()
duration = time.time() - start

perf_logger.info("Operation completed", 
                operation="expensive_op",
                duration_ms=int(duration * 1000))
```

## 📊 Format Styles

| Style | Output |
|-------|--------|
| **simple** | `DEBUG - Starting process` |
| **standard** | `[2026-05-16 10:30:45] DEBUG - myapp - Starting process` |
| **detailed** | `[2026-05-16 10:30:45] DEBUG - myapp - main:45 - Starting process` |
| **full** | `[2026-05-16 10:30:45] DEBUG - myapp - app.py:main:45 - Starting process` |
| **minimal** | `DEBUG \| Starting process` |

## 🔴 Comparison: Advanced Logging vs stdlib

| Feature | stdlib | Advanced |
|---------|--------|----------|
| **Setup** | 5+ lines | 1 line |
| **One-liner** | ❌ | ✅ |
| **Hierarchical** | Complex | Automatic |
| **Multiple Handlers** | Limited | ✅ |
| **Rotating Files** | Complex | Simple |
| **Colors** | ❌ | ✅ |
| **JSON Output** | ❌ | ✅ |
| **Filtering** | Limited | Advanced |
| **Context Injection** | ❌ | ✅ |
| **Thread-safe** | ✅ | ✅ |
| **Dependencies** | 0 | 0 |

## 📈 Project Stats

- **Core Module**: 600+ lines
- **Examples**: 18 working examples
- **Features**: 25+
- **Dependencies**: 0 (pure stdlib)
- **Python**: 3.6+

## 🎓 Quick Links

- **Example Files**: `example_logging_simple.py`, `example_logging_advanced.py`
- **Source Code**: `advanced_logging.py` (main module)
- **Learn Patterns**: See example files for real-world usage

## 🚀 Getting Started

1. Copy `advanced_logging.py` to your project
2. Import: `from advanced_logging import get_logger`
3. Create logger: `logger = get_logger("myapp")`
4. Log: `logger.info("Hello!")`
5. Add handlers as needed

---

**Advanced Logging** - Making Python logging simple.