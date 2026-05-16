# Advanced Logging - Usage Patterns & Recipes

Practical patterns, recipes, and real-world examples for using Advanced Logging effectively.

## 📋 Table of Contents

1. [Common Patterns](#common-patterns)
2. [Real-World Scenarios](#real-world-scenarios)
3. [Advanced Recipes](#advanced-recipes)
4. [Best Practices](#best-practices)
5. [Performance Tips](#performance-tips)
6. [Integration Guides](#integration-guides)
7. [FAQ & Troubleshooting](#faq--troubleshooting)

---

## Common Patterns

### Pattern 1: Application-Wide Logger Setup

**Scenario**: Initialize logging for your entire application in one place.

```python
# config.py
from advanced_logging import get_logger, LogLevel

def setup_logging(debug=False):
    """Setup application-wide logging."""
    level = LogLevel.DEBUG if debug else LogLevel.INFO
    
    # Root logger for general messages
    app_logger = get_logger(
        "myapp",
        level=level,
        console=True,
        file="logs/app.log",
        format_style="detailed"
    )
    
    # Add rotating file for long-running apps
    app_logger.add_rotating_file_handler(
        "logs/app_detailed.log",
        max_bytes=10_000_000,
        backup_count=5
    )
    
    # JSON logging for analysis
    app_logger.add_json_handler("logs/app.json")
    
    return app_logger

# main.py
from config import setup_logging

logger = setup_logging(debug=True)
logger.info("Application started")
```

### Pattern 2: Module-Level Loggers

**Scenario**: Different log streams for different components.

```python
# database.py
from advanced_logging import get_logger

db_logger = get_logger("myapp.database")

def connect():
    db_logger.info("Connecting to database")
    # connection logic
    db_logger.debug("Connection established", pool_size=10)

# api.py
api_logger = get_logger("myapp.api")

def start_server(port):
    api_logger.info(f"Starting server on port {port}")
    # server logic
    api_logger.info("Server ready")

# cache.py
cache_logger = get_logger("myapp.cache")

def initialize():
    cache_logger.debug("Initializing cache layer")
    cache_logger.info("Cache initialized with 1000 entries")
```

### Pattern 3: Request Tracking with Context

**Scenario**: Track a single request through multiple functions.

```python
from advanced_logging import get_logger, LogContext

logger = get_logger("web_app")

def handle_request(request):
    # Inject request ID into all logs
    with LogContext(
        request_id=request.id,
        user=request.user,
        method=request.method,
        path=request.path
    ):
        logger.info("Request received")
        
        try:
            result = process_request(request)
            logger.info("Request processed", status=200)
            return result
        except Exception as e:
            logger.exception("Request failed", status=500)
            raise

def process_request(request):
    logger.debug("Validating request")
    # validation
    
    logger.debug("Processing data")
    # processing - all logs include request_id and user automatically
    
    return result
```

### Pattern 4: Conditional Logging

**Scenario**: Different logging behavior for different modes.

```python
import os
from advanced_logging import get_logger, LogLevel

def configure_logger():
    if os.getenv("ENV") == "production":
        # Production: minimal console, comprehensive files
        logger = get_logger("app", console=False)
        logger.set_level(LogLevel.WARNING)
        logger.add_file_handler("logs/app.log")
        logger.add_rotating_file_handler("logs/app_detail.log", max_bytes=50_000_000)
        
    elif os.getenv("ENV") == "staging":
        # Staging: detailed logging
        logger = get_logger("app", console=True, file="logs/staging.log", 
                           format_style="detailed")
        logger.set_level(LogLevel.DEBUG)
        
    else:
        # Development: debug mode
        logger = get_logger("app", console=True, format_style="detailed")
        logger.set_level(LogLevel.DEBUG)
    
    return logger

logger = configure_logger()
```

### Pattern 5: Error Tracking

**Scenario**: Separate error logs from general logs.

```python
from advanced_logging import get_logger, ConsoleHandler, FileHandler, LogLevel, Formatter

app_logger = get_logger("app", console=False)

# General log file
app_logger.add_file_handler(
    "logs/app.log",
    level=LogLevel.INFO,
    format_style="standard"
)

# Error-only log file
error_handler = FileHandler(
    "logs/errors.log",
    level=LogLevel.ERROR,
    formatter=Formatter("detailed", use_colors=False)
)
app_logger.add_handler(error_handler)

# Critical errors to console immediately
critical_handler = ConsoleHandler(
    level=LogLevel.CRITICAL,
    formatter=Formatter("simple")
)
app_logger.add_handler(critical_handler)

# Usage
app_logger.debug("Processing")      # → logs/app.log
app_logger.info("Completed")        # → logs/app.log
app_logger.error("Failed")          # → logs/app.log + logs/errors.log
app_logger.critical("System down")  # → console + logs/errors.log
```

---

## Real-World Scenarios

### Scenario 1: Web Application

```python
# app/logging_config.py
from advanced_logging import get_logger, LogLevel, LogContext

def create_app_logger():
    logger = get_logger(
        "webapp",
        level=LogLevel.DEBUG,
        file="logs/app.log"
    )
    
    # Rotating file for production
    logger.add_rotating_file_handler(
        "logs/webapp.log",
        max_bytes=50_000_000,
        backup_count=10
    )
    
    # JSON for analysis
    logger.add_json_handler("logs/app.json")
    
    return logger

# app/middleware.py
logger = create_app_logger()

def logging_middleware(request, call_next):
    with LogContext(
        request_id=request.headers.get("X-Request-ID"),
        client_ip=request.client.host,
        method=request.method,
        path=request.url.path
    ):
        logger.debug("Request started")
        response = call_next(request)
        logger.info(f"Response sent", status_code=response.status_code)
        return response

# app/routes.py
api_logger = get_logger("webapp.api")

@app.get("/api/users/{user_id}")
async def get_user(user_id: int):
    api_logger.debug(f"Fetching user {user_id}")
    try:
        user = await db.get_user(user_id)
        api_logger.info(f"User retrieved", user_id=user_id)
        return user
    except Exception as e:
        api_logger.exception("Failed to retrieve user", user_id=user_id)
        raise
```

### Scenario 2: Data Processing Pipeline

```python
from advanced_logging import get_logger, LogContext

logger = get_logger("pipeline")
pipeline_logger = get_logger("pipeline.etl")

def process_batch(batch_id, data):
    with LogContext(batch_id=batch_id, size=len(data)):
        logger.info("Starting batch processing")
        
        try:
            # Extract
            with LogContext(stage="extract"):
                logger.debug("Extracting data")
                extracted = extract(data)
                logger.info("Data extracted", records=len(extracted))
            
            # Transform
            with LogContext(stage="transform"):
                logger.debug("Transforming data")
                transformed = transform(extracted)
                logger.info("Data transformed", records=len(transformed))
            
            # Load
            with LogContext(stage="load"):
                logger.debug("Loading data")
                loaded = load(transformed)
                logger.info("Data loaded", records=loaded)
            
            logger.info("Batch completed successfully")
            return loaded
            
        except Exception as e:
            logger.exception("Batch failed")
            raise
```

### Scenario 3: Microservice

```python
# service.py
from advanced_logging import get_logger, LogLevel

class MicroService:
    def __init__(self, name, port):
        self.name = name
        self.port = port
        self.logger = get_logger(f"service.{name}")
        
        # Main log
        self.logger.add_file_handler(
            f"logs/{name}.log",
            format_style="detailed"
        )
        
        # Metrics log
        self.metrics_logger = get_logger(f"service.{name}.metrics")
        self.metrics_logger.add_json_handler(f"logs/{name}_metrics.json")
    
    def start(self):
        self.logger.info(f"Starting {self.name} service", port=self.port)
        
        # Start server
        server.run(self.port)
        
        self.logger.info(f"Service {self.name} stopped")
    
    def log_metric(self, metric_name, value):
        self.metrics_logger.info(
            f"Metric: {metric_name}",
            metric=metric_name,
            value=value,
            timestamp=time.time()
        )

# main.py
service = MicroService("user-service", 8001)
service.start()
```

### Scenario 4: Database Operations

```python
from advanced_logging import get_logger, LogContext

db_logger = get_logger("database")

class Database:
    def __init__(self, connection_string):
        self.conn_string = connection_string
        self.connection = None
        db_logger.debug(f"Initializing database: {connection_string}")
    
    def execute_query(self, query, params=None):
        query_hash = hash(query)
        
        with LogContext(query_id=query_hash, params=str(params)):
            db_logger.debug("Executing query")
            
            try:
                start_time = time.time()
                result = self.connection.execute(query, params or [])
                elapsed = time.time() - start_time
                
                db_logger.info(
                    "Query executed",
                    rows=len(result),
                    duration_ms=elapsed * 1000
                )
                
                return result
                
            except Exception as e:
                db_logger.error(f"Query failed: {e}", exc_info=True)
                raise
    
    def bulk_insert(self, table, records):
        with LogContext(table=table, count=len(records)):
            db_logger.info("Starting bulk insert")
            
            try:
                # Insert logic
                db_logger.info("Bulk insert completed", inserted=len(records))
            except Exception as e:
                db_logger.exception("Bulk insert failed")
                raise
```

---

## Advanced Recipes

### Recipe 1: Custom Handler for Alerts

```python
from advanced_logging import Handler, LogRecord
import smtplib
from email.mime.text import MIMEText

class EmailAlertHandler(Handler):
    """Send critical errors via email."""
    
    def __init__(self, email_to, email_from, smtp_server):
        super().__init__()
        self.email_to = email_to
        self.email_from = email_from
        self.smtp_server = smtp_server
    
    def emit(self, record: LogRecord):
        if record.level >= LogLevel.CRITICAL:
            self._send_email(record)
    
    def _send_email(self, record):
        msg = MIMEText(f"Critical Error: {record.message}")
        msg["Subject"] = f"Alert: {record.logger_name}"
        msg["From"] = self.email_from
        msg["To"] = self.email_to
        
        # Send via SMTP
        with smtplib.SMTP(self.smtp_server) as server:
            server.send_message(msg)

# Usage
alert_handler = EmailAlertHandler(
    "admin@example.com",
    "app@example.com",
    "smtp.gmail.com"
)
logger.add_handler(alert_handler)
```

### Recipe 2: Performance Monitoring Logger

```python
from advanced_logging import get_logger
import time

perf_logger = get_logger("performance")
perf_logger.add_json_handler("logs/performance.json")

class PerformanceMonitor:
    def __init__(self, name):
        self.name = name
        self.start_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, *args):
        elapsed = time.time() - self.start_time
        perf_logger.info(
            f"Completed: {self.name}",
            operation=self.name,
            duration_ms=int(elapsed * 1000)
        )

# Usage
with PerformanceMonitor("database_query"):
    result = db.query("SELECT * FROM users")

with PerformanceMonitor("api_request"):
    response = requests.get("https://api.example.com/data")
```

### Recipe 3: Hierarchical Component Logging

```python
from advanced_logging import get_logger, LogContext

class Component:
    def __init__(self, name, parent_context=None):
        self.name = name
        self.logger = get_logger(f"app.component.{name}")
        self.parent_context = parent_context
    
    def execute(self, task_id, **options):
        with LogContext(
            component=self.name,
            task_id=task_id,
            **options
        ):
            self.logger.info("Executing task")
            
            # Sub-task
            sub_component = Component("subtask", task_id)
            sub_component.execute(f"{task_id}.1")
            
            self.logger.info("Task completed")

# Usage
app = Component("main")
app.execute("task-001", priority="high", retry=3)
```

### Recipe 4: Structured Error Tracking

```python
from advanced_logging import get_logger, Formatter, FileHandler
import json

error_logger = get_logger("errors")

# JSON error log for centralized processing
error_handler = FileHandler(
    "logs/errors.json",
    formatter=Formatter(""),  # Use custom
)

class ErrorTracker:
    def __init__(self, logger):
        self.logger = logger
    
    def track(self, error_type, error_msg, context=None):
        error_data = {
            "type": error_type,
            "message": error_msg,
            "context": context or {},
            "timestamp": time.time()
        }
        
        with open("logs/errors.json", "a") as f:
            f.write(json.dumps(error_data) + "\n")
        
        self.logger.error(error_msg, error_type=error_type, **context)

tracker = ErrorTracker(error_logger)
tracker.track("auth_failed", "Invalid credentials", {"user_id": 123})
```

### Recipe 5: Async Task Logging

```python
from advanced_logging import get_logger, LogContext
import asyncio

task_logger = get_logger("tasks")

async def async_task(task_id, work_items):
    with LogContext(task_id=task_id):
        task_logger.info("Starting async task", items=len(work_items))
        
        try:
            tasks = [
                process_item(item, f"{task_id}.{i}")
                for i, item in enumerate(work_items)
            ]
            
            results = await asyncio.gather(*tasks)
            task_logger.info("All tasks completed", completed=len(results))
            
            return results
            
        except Exception as e:
            task_logger.exception("Task failed")
            raise

async def process_item(item, item_id):
    with LogContext(item_id=item_id):
        task_logger.debug(f"Processing item")
        await asyncio.sleep(1)  # Simulate work
        task_logger.debug(f"Item processed")

# Usage
asyncio.run(async_task("batch-001", [1, 2, 3, 4, 5]))
```

---

## Best Practices

### 1. **Use Hierarchical Logger Names**
```python
# Good - creates hierarchy
db_logger = get_logger("app.database")
cache_logger = get_logger("app.cache")
api_logger = get_logger("app.api.v1")

# Avoid - no organization
logger1 = get_logger("db")
logger2 = get_logger("cache")
```

### 2. **Log at Appropriate Levels**
```python
# Good
logger.debug("Processing item 123")           # Internal details
logger.info("User login successful")          # Notable events
logger.warning("Cache hit rate low")          # Potential issues
logger.error("Database connection failed")    # Problems
logger.critical("Out of memory")              # Severe issues

# Avoid
logger.info("User login successful")  # Wrong level
logger.debug("User login successful")  # Too verbose
```

### 3. **Include Context**
```python
# Good - provides context
logger.error(
    "Transaction failed",
    user_id=123,
    amount=99.99,
    reason="insufficient_funds"
)

# Avoid - vague
logger.error("Transaction failed")
```

### 4. **Use Exception Logging**
```python
# Good - includes traceback
try:
    risky_operation()
except Exception:
    logger.exception("Operation failed")

# Avoid - loses traceback
try:
    risky_operation()
except Exception as e:
    logger.error(f"Operation failed: {e}")
```

### 5. **Create Module-Level Loggers**
```python
# Good - module-level logger
# database.py
logger = get_logger("app.database")

def query():
    logger.debug("Querying database")

# Avoid - creating logger in each function
def query():
    logger = get_logger("query")
    logger.debug("Querying database")
```

---

## Performance Tips

### Tip 1: Lazy Formatting
```python
# Good - only formats if debug level
logger.debug("Processing %d items", len(items))

# Avoid - always formats
logger.debug(f"Processing {len(items)} items")

# In this case both work fine, but be careful with expensive operations
```

### Tip 2: File I/O Batching
```python
# For high-volume logging, consider
logger.add_rotating_file_handler(
    "app.log",
    max_bytes=50_000_000,  # Large size to reduce rotations
    backup_count=10        # Keep many backups
)
```

### Tip 3: Level Filtering
```python
# Reduce logging in production
if production:
    logger.set_level(LogLevel.WARNING)
else:
    logger.set_level(LogLevel.DEBUG)
```

---

## Integration Guides

### Integration with Web Framework (Flask)

```python
from flask import Flask, request, g
from advanced_logging import get_logger, LogContext

app = Flask(__name__)
logger = get_logger("flask_app", file="logs/app.log")

@app.before_request
def before_request():
    g.request_id = request.headers.get("X-Request-ID", "unknown")
    g.start_time = time.time()

@app.after_request
def after_request(response):
    elapsed = time.time() - g.start_time
    with LogContext(request_id=g.request_id):
        logger.info(
            f"Request: {request.method} {request.path}",
            status=response.status_code,
            duration_ms=int(elapsed * 1000)
        )
    return response

@app.route("/api/users/<int:user_id>")
def get_user(user_id):
    with LogContext(request_id=g.request_id, user_id=user_id):
        logger.debug("Fetching user")
        user = User.query.get(user_id)
        logger.info("User fetched")
        return user.to_dict()
```

### Integration with Celery

```python
from celery import Celery
from advanced_logging import get_logger, LogContext

app = Celery()
task_logger = get_logger("celery_tasks")

@app.task
def long_running_task(task_id, data):
    with LogContext(task_id=task_id):
        task_logger.info("Starting task")
        
        try:
            result = process_data(data)
            task_logger.info("Task completed")
            return result
        except Exception:
            task_logger.exception("Task failed")
            raise
```

---

## FAQ & Troubleshooting

### Q: Why aren't my logs showing?
**A:** Check log levels:
```python
logger.set_level(LogLevel.DEBUG)  # Show all messages
logger.debug("This should appear")
```

### Q: How to disable logs from other libraries?
**A:** Create a filter:
```python
def only_my_app(record):
    return record.logger_name.startswith("myapp")

logger.add_filter(only_my_app)
```

### Q: How to log large objects without overwhelming output?
**A:** Use JSON handler or custom formatter:
```python
logger.add_json_handler("large_data.json")
logger.info("Large object", data=large_dict)  # Goes to JSON file
```

### Q: Performance impact of logging?
**A:** Minimal (~1-5% overhead) for reasonable log volumes. Use appropriate levels to reduce I/O.

### Q: How to rotate logs by time (daily)?
**A:** Extend `RotatingFileHandler`:
```python
# Currently: size-based rotation
# For time-based: implement custom handler
```

---

## Summary

Advanced Logging provides:
- ✅ Simple one-line setup
- ✅ Powerful customization when needed
- ✅ Zero dependencies
- ✅ Production-ready
- ✅ Extensible architecture

**Start simple, grow complex** - that's the philosophy!
