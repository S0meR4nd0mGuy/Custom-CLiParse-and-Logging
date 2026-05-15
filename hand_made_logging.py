"""
An advanced hand-made logging module, that provides easy to use logging functionality with support for multiple log levels, log formatting and so much more!

"""
__version__ = "0.1.0"
__author__ = "S0meR4nd0mGuy"
__all__ = [
    "Logger"
]
import sys
import pathlib


class Logger:
    """A simple hand made logger! [WiP; Adding Example later]"""
    def __init__(
        self,
        logging_level: str,
        logging_format: str,
        log_file: str | None = None,
        log_to_console: bool = False,       
    ):
        self.logging_level = logging_level
        self.logging_format = logging_format
        self.log_to_console = log_to_console
        self.log_file = log_file
        levels = ["DEBUG", "INFO", "WARNING", "ERROR"]
        self.levels = levels

    def set_log_file(self, log_file_path: str):
        """Sets the log file path."""
        ex = self._check_log_file_exists(pathlib.Path(log_file_path))
        if ex == False:
            print(f"Log file {log_file_path} does not exist. Please create the log file or verify that the path name is correct.")
        else: 
            self.log_file = log_file_path

    def _check_log_file_exists(self, p: pathlib.Path) -> bool:
        """Checks if the log file exists."""
        if p.exists():
            return True
        else:
            return False
    
    def log(self, level: str, message: str):
        """Logs a message with the specified level."""
        if level not in self.levels:
            raise ValueError(f"Invalid logging level: {level}. Valid levels are: {', '.join(self.levels)}")
        formatted_message = self.logging_format.format(level=level, message=message)
        if self.log_to_console:
            print(formatted_message)
        if self.log_file:
            with open(self.log_file, "a") as f:
                f.write(formatted_message + "\n")
        else: 
            raise ValueError("No log file specified. Please set a log file using set_log_file() method or enable console logging.")
    
    def set_console_logging(self, enable: bool):
        """Enables or disables console logging."""
        if enable == True:
            self.log_to_console = True
        else: 
            self.log_to_console = False

    def set_logging_format(self, logging_format: int):
        """Sets the logging format. The logging formats are below.\n
    1: [{level}] - {message}\n
    2: [{timestamp}] - [{level}] - {message}\n
    3: [{timestamp}] - [{level}] - {message} (Logged from {file}:{line})\n
    4: [{timestamp}] - [{level}] - {message} (Logged from {file}:{line}) (function: {function if not None else 'N/A'})\n
        """
        formats = {
            1: "[{level}] - {message}",
            2: "[{timestamp}] - [{level}] - {message}",
            3: "[{timestamp}] - [{level}] - {message} (Logged from {file}:{line})",
            4: "[{timestamp}] - [{level}] - {message} (Logged from {file}:{line}) (function: {function if not None else 'N/A'})"
        }
        if logging_format in formats:
            self.logging_format = formats[logging_format]
        else:
            raise ValueError(f"Invalid logging format: {logging_format}. Valid formats are: {', '.join(formats.keys())}")