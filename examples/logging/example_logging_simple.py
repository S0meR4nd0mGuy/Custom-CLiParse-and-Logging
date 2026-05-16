"""
Simple examples demonstrating basic logging usage.
"""

import advanced_logging
from advanced_logging import get_logger, LogLevel, LogContext

# Example 1: One-line console logging
print("=" * 60)
print("Example 1: One-line Console Logging")
print("=" * 60)
logger = get_logger("myapp")
logger.info("Application started")
logger.debug("Debug message")
logger.warning("This is a warning")
logger.error("An error occurred")
logger.critical("Critical system failure!")

# Example 2: Console + File logging
print("\n" + "=" * 60)
print("Example 2: Console + File Logging")
print("=" * 60)
app_logger = get_logger("app", file="app.log", console=True)
app_logger.info("Starting data processing")
app_logger.debug("Processing started at background")
app_logger.info("Task completed successfully")

# Example 3: Hierarchical loggers
print("\n" + "=" * 60)
print("Example 3: Hierarchical Loggers (Different Components)")
print("=" * 60)
db_logger = get_logger("myapp.database")
api_logger = get_logger("myapp.api")
cache_logger = get_logger("myapp.cache")

db_logger.info("Connecting to PostgreSQL")
db_logger.debug("Connection pool initialized with 10 connections")

api_logger.info("Starting API server on port 8000")
api_logger.info("Registered 5 endpoints")

cache_logger.debug("Cache miss for key: user:123")
cache_logger.info("Cache populated with 100 entries")

# Example 4: Different log levels
print("\n" + "=" * 60)
print("Example 4: Different Log Levels")
print("=" * 60)
debug_logger = get_logger("debug_test", level=LogLevel.DEBUG)
info_logger = get_logger("info_test", level=LogLevel.INFO)
error_logger = get_logger("error_test", level=LogLevel.ERROR)

print("\n[DEBUG Level Logger - shows all]")
debug_logger.debug("Debug message")
debug_logger.info("Info message")
debug_logger.warning("Warning message")

print("\n[INFO Level Logger - shows info and above]")
info_logger.debug("Debug message (will not show)")
info_logger.info("Info message")
info_logger.warning("Warning message")

print("\n[ERROR Level Logger - shows errors and critical]")
error_logger.debug("Debug message (will not show)")
error_logger.info("Info message (will not show)")
error_logger.warning("Warning message (will not show)")
error_logger.error("Error message")

# Example 5: Format styles
print("\n" + "=" * 60)
print("Example 5: Different Format Styles")
print("=" * 60)
print("\n[Simple format]")
simple_logger = get_logger("simple", format_style="simple")
simple_logger.info("User logged in")

print("\n[Detailed format]")
detailed_logger = get_logger("detailed", format_style="detailed")
detailed_logger.info("Database query executed")

print("\n[Minimal format]")
minimal_logger = get_logger("minimal", format_style="minimal")
minimal_logger.warning("Rate limit approaching")

# Example 6: Exception logging
print("\n" + "=" * 60)
print("Example 6: Exception Logging")
print("=" * 60)
try:
    result = 10 / 0
except ZeroDivisionError:
    exc_logger = get_logger("error_handler")
    exc_logger.exception("Mathematical operation failed")

# Example 7: Extra context in logs
print("\n" + "=" * 60)
print("Example 7: Logging with Extra Data")
print("=" * 60)
user_logger = get_logger("user_service")
user_logger.info("User action", user_id=123, action="login", ip="192.168.1.1")
user_logger.warning("Suspicious activity", attempts=5, user_id=456)

# Example 8: Context manager for request tracking
print("\n" + "=" * 60)
print("Example 8: Context Manager (Request Tracking)")
print("=" * 60)
request_logger = get_logger("request_handler")

# Simulating different requests
request_logger.info("Request 1 started")
with LogContext(request_id="req-001", user="alice"):
    request_logger.info("Processing request for user alice")
    request_logger.debug("Validating parameters")
    request_logger.info("Request completed")

print()
request_logger.info("Request 2 started")
with LogContext(request_id="req-002", user="bob"):
    request_logger.info("Processing request for user bob")
    request_logger.warning("Rate limit check")
    request_logger.info("Request completed")

print("\n" + "=" * 60)
print("All examples completed! Check app.log for file output.")
print("=" * 60)
