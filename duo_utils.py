"""
Utility functions
"""
from __future__ import annotations, print_function

import logging
import os
from logging.handlers import RotatingFileHandler
from typing import LiteralString

DEFAULT_LOG_NAME = __name__

LOGGERS = {}


class LoggingFormatter(logging.Formatter):
    """Custom logging formatter class with colored output"""

    # Colors
    black = "\x1b[30m"
    white = "\x1b[37m"
    red = "\x1b[31m"
    green = "\x1b[32m"
    yellow = "\x1b[33m"
    blue = "\x1b[34m"
    gray = "\x1b[38m"
    # Styles
    reset = "\x1b[0m"
    bold = "\x1b[1m"

    # ANSI color reference https://gist.github.com/fnky/458719343aabd01cfb17a3a4f7296797

    COLORS = {
            logging.DEBUG:    gray + bold,
            logging.INFO:     blue + bold,
            logging.WARNING:  yellow + bold,
            logging.ERROR:    red,
            logging.CRITICAL: '\x1b[1;31;43m'  # Bold (1) Red (31) with Yellow (43) background
    }

    def format(self, record):
        """Method to dynamically color log messages for console output based on message severity"""
        log_color = self.COLORS[record.levelno]
        time_color = '\x1b[1;30;47m'
        format_str = ("(black){asctime}(reset) | (lvl_color){levelname:8}(reset) | " +
                      "(green){name} | {filename} | " +
                      "(green){module}(reset) | (green){funcName}:{lineno:<4}(reset) | {message}")
        format_str = format_str.replace("(black)", time_color)
        format_str = format_str.replace("(reset)", self.reset)
        format_str = format_str.replace("(lvl_color)", log_color)
        format_str = format_str.replace("(green)", self.green + self.bold)
        formatter = logging.Formatter(format_str, "%Y-%m-%d %H:%M:%S", style="{")
        return formatter.format(record)


def get_logger(
        logger_name: str = None,
        /,
        *,
        log_level: str = 'INFO',
        log_to_console: bool = True,
        log_to_file: bool = True,
        logfile_name: str = None,
        log_message_format: LiteralString = None) -> logging.Logger:
    """Create a logging instance and return a logger"""
    if logfile_name is None:
        logger_name = DEFAULT_LOG_NAME
    if logger_name in LOGGERS:
        logger = LOGGERS[logger_name]
        logger.info("Existing logger instance found.")
    else:
        logger = logging.getLogger(logger_name)
    logger.setLevel(logging.getLevelName(log_level))
    logger.propagate = False

    if log_message_format is None:
        # log_message_format = "[{asctime}] [{levelname:<8}] {name}: {message}"
        log_message_format = ("{asctime} | {levelname:8} | {name:<10} | {filename:<15} | " +
                              "{module:<12} | {funcName:>15}():{lineno:_^4} | {message}")

    # Console handler
    if log_to_console:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(LoggingFormatter())
        logger.addHandler(console_handler)

    # File handler
    if log_to_file:
        if logfile_name is None:
            logfile_name = logger_name + '.log'
        log_path = os.path.join(os.getcwd(), 'logs', logfile_name)
        file_handler = RotatingFileHandler(filename=log_path, encoding="utf-8")
        file_handler_formatter = logging.Formatter(log_message_format, "%Y-%m-%d %H:%M:%S", style="{")
        file_handler.setFormatter(file_handler_formatter)
        logger.addHandler(file_handler)
    logger.info(" --- [ Logging started for %s ] ---", logger_name)
    LOGGERS[logger_name] = logger
    return logger
