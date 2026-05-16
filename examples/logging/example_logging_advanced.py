"""
Advanced logging examples demonstrating all features.
"""
import advanced_logging
from advanced_logging import (
    get_logger, get_logger, LogLevel, LogContext, Handler, Formatter,
    FileHandler, RotatingFileHandler, ConsoleHandler, LoggerManager, LogRecord
)

# Example 1: Rotating file handler for log files that grow large
print("=" * 70)
print("Example 1: Rotating File Handler (Auto Backup when Size Exceeded)")
print("=" * 70)
app_logger = get_logger("rotating_example", console=False)
formatter = Formatter("detailed", use_colors=False)

# Add rotating file handler (rotate after 1MB, keep 3 backups)
rotating_handler = RotatingFileHandler(
    "rotating_app.log",
    level=LogLevel.DEBUG,
    formatter=formatter,
    max_bytes=1_000_000,  # 1MB
    backup_count=3
)
app_logger.add_handler(rotating_handler)

# Simulate log writing
for i in range(10):
    app_logger.info(f"Processing batch {i+1}: " + "x" * 100)

print("[OK] Rotating log files created (check rotating_app.log*)")

# Example 2: Multiple handlers with different levels
print("\n" + "=" * 70)
print("Example 2: Multiple Handlers with Different Levels")
print("=" * 70)
multi_logger = get_logger("multi_handler", console=False)

# Console handler: only errors and above
console_formatter = Formatter("simple", use_colors=True)
console_handler = ConsoleHandler(LogLevel.ERROR, console_formatter)
multi_logger.add_handler(console_handler)

# File handler: all levels (DEBUG and above)
file_formatter = Formatter("detailed", use_colors=False)
file_handler = FileHandler("all_levels.log", LogLevel.DEBUG, file_formatter)
multi_logger.add_handler(file_handler)

print("\nLogging messages (only ERROR shown in console, all in file):")
multi_logger.debug("Debug info (file only)")
multi_logger.info("Info message (file only)")
multi_logger.warning("Warning message (file only)")
multi_logger.error("Error message (console + file)")
multi_logger.critical("Critical message (console + file)")

print("[OK] Check 'all_levels.log' to see all messages")

# Example 3: Custom formatter
print("\n" + "=" * 70)
print("Example 3: Custom Format Styles")
print("=" * 70)
custom_logger = get_logger("custom_formats", console=False)

formats = {
    "SHORT": "{level_name} | {message}",
    "WITH_THREAD": "[{thread_name}] {level_name} - {message}",
    "WITH_PROCESS": "[PID:{process_id}] {level_name} - {message}",
    "FULL_CONTEXT": "({thread_name}:{thread_id}) [{timestamp}] {level_name} - {logger_name} - {message}",
}

for format_name, format_str in formats.items():
    formatter = Formatter(format_str, use_colors=True)
    handler = ConsoleHandler(LogLevel.INFO, formatter)
    custom_logger.add_handler(handler)

print(f"\nUsing 4 different custom formats:")
custom_logger.info("This message shown in 4 different formats")

# Example 4: Filtering logs
print("\n" + "=" * 70)
print("Example 4: Log Filtering")
print("=" * 70)
filter_logger = get_logger("filtered_logging", console=False)

# Create handler
handler = ConsoleHandler(LogLevel.DEBUG, Formatter("standard"))

# Add filter: only log messages containing "important"
def important_filter(record: LogRecord) -> bool:
    return "important" in record.message.lower()

handler.add_filter(important_filter)
filter_logger.add_handler(handler)

print("\nLogging with filter (only 'important' messages shown):")
filter_logger.info("Regular log message")
filter_logger.info("This is important!")
filter_logger.debug("Another regular message")
filter_logger.warning("Important warning!")
filter_logger.info("Another normal log")

# Example 5: Structured JSON logging
print("\n" + "=" * 70)
print("Example 5: Structured JSON Logging")
print("=" * 70)
json_logger = get_logger("json_service", console=False)
json_logger.add_json_handler("structured.json", LogLevel.DEBUG)

print("Writing structured logs to structured.json...")
json_logger.info("Service started", service="auth", port=3000)
json_logger.debug("Database connected", db="postgres", pool_size=10)
json_logger.error("Authentication failed", user_id=123, reason="invalid_token")

print("[OK] Check 'structured.json' for JSON-formatted logs")

# Example 6: Hierarchical logging with context
print("\n" + "=" * 70)
print("Example 6: Hierarchical Logging with Context")
print("=" * 70)
root_logger = get_logger("myapp")
db_logger = get_logger("myapp.database")
api_logger = get_logger("myapp.api")

print("\nSimulating multi-component system:")

# Main application context
with LogContext(session_id="sess-001", user="john"):
    root_logger.info("User session started")
    
    # Database operations
    with LogContext(operation="query"):
        db_logger.info("Executing SELECT query")
        db_logger.debug("Query: SELECT * FROM users")
    
    # API operations
    with LogContext(endpoint="/api/users"):
        api_logger.info("API request received")
        api_logger.debug("Headers processed")

# Example 7: Global logger manager
print("\n" + "=" * 70)
print("Example 7: Global Logger Manager")
print("=" * 70)

# Set global level for all loggers
LoggerManager.set_global_level(LogLevel.INFO)
print("[OK] All loggers set to INFO level globally")

# List all loggers
all_loggers = LoggerManager.list_loggers()
print(f"\nAll active loggers ({len(all_loggers)} total):")
for logger_name in all_loggers[:10]:  # Show first 10
    print(f"  • {logger_name}")

if len(all_loggers) > 10:
    print(f"  ... and {len(all_loggers) - 10} more")

# Example 8: Performance logging
print("\n" + "=" * 70)
print("Example 8: Performance Logging")
print("=" * 70)
import time

perf_logger = get_logger("performance")

operations = [
    ("Database Query", 0.45),
    ("Cache Lookup", 0.02),
    ("JSON Serialization", 0.08),
    ("Network Request", 1.23),
    ("Image Processing", 2.15),
]

print("\nPerformance metrics:")
for operation, duration in operations:
    perf_logger.info(f"{operation} completed in {duration:.2f}s", 
                    operation=operation, duration_ms=int(duration*1000))

# Example 9: Error handling with different detail levels
print("\n" + "=" * 70)
print("Example 9: Comprehensive Error Logging")
print("=" * 70)
error_logger = get_logger("error_handler")

# Example different error scenarios
try:
    # Simulated database error
    raise ValueError("Connection timeout after 30 seconds")
except ValueError as e:
    error_logger.exception("Database operation failed", 
                          operation="connect", timeout=30)

try:
    # Simulated file error
    with open("/nonexistent/path/file.txt") as f:
        pass
except FileNotFoundError:
    error_logger.exception("Configuration file not found", 
                          file="/nonexistent/path/file.txt")

# Example 10: Mixed configuration
print("\n" + "=" * 70)
print("Example 10: Production-like Configuration")
print("=" * 70)

# Create a production logger with all handlers
prod_logger = get_logger("production_app", console=False)

# Console: only warnings and errors
console_handler = ConsoleHandler(LogLevel.WARNING, Formatter("simple"))
prod_logger.add_handler(console_handler)

# General log file
general_handler = FileHandler("general.log", LogLevel.INFO, Formatter("standard", use_colors=False))
prod_logger.add_handler(general_handler)

# Error log file (only errors)
error_handler = FileHandler("errors.log", LogLevel.ERROR, Formatter("detailed", use_colors=False))
prod_logger.add_handler(error_handler)

# JSON log file (structured)
prod_logger.add_json_handler("app.json", LogLevel.DEBUG)

print("Production logger configured with:")
print("  • Console handler (WARNING+)")
print("  • General log file (all messages)")
print("  • Error log file (errors only)")
print("  • JSON structured logs")

prod_logger.info("Production environment initialized")
prod_logger.warning("Cache warmer running in background")
prod_logger.error("Failed to connect to secondary database")

print("\n" + "=" * 70)
print("All advanced examples completed!")
print("Check these files for output:")
print("  • rotating_app.log, rotating_app.log.1, etc.")
print("  • all_levels.log")
print("  • structured.json")
print("  • general.log, errors.log, app.json")
print("=" * 70)
