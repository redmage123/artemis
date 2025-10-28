#!/usr/bin/env python3
"""
Module: artemis_logger.py

Purpose: Centralized logging system for the Artemis autonomous development pipeline
Why: Provides unified logging across all pipeline components with proper rotation,
     structured formatting, and fallback mechanisms for permission issues
Patterns: Singleton (via get_logger), Strategy (configurable formatters),
          Factory (logger creation)
Integration: Used by all Artemis modules for consistent logging behavior

Architecture:
    - Main log directory: /var/log/artemis (configurable via ARTEMIS_LOG_DIR)
    - Separate log files per component (main, supervisor, developers, etc.)
    - Error aggregation in artemis_errors.log for monitoring
    - Automatic fallback to /tmp if permission denied
    - Thread-safe logger creation and configuration

Design Decisions:
    - Centralized logging prevents log sprawl across the system
    - Rotation prevents disk space exhaustion
    - Separate error log allows easy monitoring of critical issues
    - Console output provides immediate feedback during development
    - Environment variable configuration allows deployment flexibility
"""

import os
import sys
import logging
import logging.handlers
from pathlib import Path
from datetime import datetime
from typing import Optional


class ArtemisLogger:
    """
    Centralized logging system for Artemis autonomous development pipeline.

    Why it exists: Provides a unified, consistent logging interface across all
    Artemis components, preventing log fragmentation and ensuring all events
    are properly captured for debugging and monitoring.

    Design pattern: Singleton-like behavior via get_logger() factory function

    Responsibilities:
    - Configure and manage rotating file handlers
    - Separate component logs (main, supervisor, developers)
    - Aggregate errors into dedicated error log
    - Provide console output for development
    - Handle permission failures gracefully with fallback
    - Support environment-based configuration

    Architecture notes:
    - Uses Python's logging.handlers.RotatingFileHandler for automatic rotation
    - Each component gets its own log file to prevent log interleaving
    - Error log aggregates ERROR+ from all components for monitoring
    - Console handler provides immediate feedback
    - Fallback to /tmp prevents startup failures in restricted environments

    Thread-safety: Thread-safe (Python's logging module handles locking)
    """

    def __init__(
        self,
        component: str = "main",
        log_dir: Optional[str] = None,
        log_level: str = "INFO",
        max_bytes: int = 100 * 1024 * 1024,  # 100MB
        backup_count: int = 10
    ):
        """
        Initialize Artemis logger for a specific component.

        Why needed: Creates isolated logging for each Artemis component while
        maintaining centralized log directory structure. Prevents components
        from interfering with each other's logs.

        Args:
            component: Component name (main, supervisor, developers, etc.)
                      Used to create component-specific log files
            log_dir: Log directory path (default: /var/log/artemis or ARTEMIS_LOG_DIR)
                    Allows deployment-specific configuration
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
                      Controls verbosity, can be overridden by ARTEMIS_LOG_LEVEL env var
            max_bytes: Max log file size before rotation (default 100MB)
                      Prevents unbounded disk usage, triggers rotation
            backup_count: Number of rotated log files to keep (default 10)
                         Balances disk usage vs historical log retention

        Environment variables:
            ARTEMIS_LOG_DIR: Override default log directory
            ARTEMIS_LOG_LEVEL: Override default log level
            ARTEMIS_LOG_MAX_SIZE_MB: Override max log file size in MB
            ARTEMIS_LOG_BACKUP_COUNT: Override backup file count

        Raises:
            None - Fallback mechanisms prevent initialization failures

        Side effects:
            - Creates log directory if it doesn't exist
            - Falls back to /tmp/artemis_logs if permission denied
            - Creates component-specific log file
            - Creates shared error log file
        """
        self.component = component

        # Get log directory from environment or default
        if log_dir is None:
            log_dir = os.getenv("ARTEMIS_LOG_DIR", "/var/log/artemis")

        self.log_dir = Path(log_dir)

        # Get log level from environment or parameter
        env_log_level = os.getenv("ARTEMIS_LOG_LEVEL", log_level)
        self.log_level = getattr(logging, env_log_level.upper(), logging.INFO)

        # Get rotation settings from environment
        env_max_size = os.getenv("ARTEMIS_LOG_MAX_SIZE_MB")
        if env_max_size:
            max_bytes = int(env_max_size) * 1024 * 1024

        env_backup = os.getenv("ARTEMIS_LOG_BACKUP_COUNT")
        if env_backup:
            backup_count = int(env_backup)

        self.max_bytes = max_bytes
        self.backup_count = backup_count

        # Create logger
        self.logger = self._setup_logger()

    def _setup_logger(self) -> logging.Logger:
        """
        Set up the logger with file handlers and rotation.

        Why needed: Configures the Python logging infrastructure with proper
        handlers, formatters, and rotation. Handles permission failures gracefully.

        Returns:
            Configured logging.Logger instance

        Side effects:
            - Creates log directory with 755 permissions
            - Falls back to /tmp if permission denied
            - Creates RotatingFileHandler for component log
            - Creates RotatingFileHandler for error log
            - Creates StreamHandler for console output
            - Removes any existing handlers to prevent duplicates

        Design decisions:
            - Three handlers provide flexibility: component log, error log, console
            - Rotation prevents disk space exhaustion
            - Permission fallback prevents startup failures
            - Detailed format in files, simple format on console
        """
        # Create log directory with proper permissions
        try:
            self.log_dir.mkdir(parents=True, exist_ok=True)
            # Try to set permissions to 755 (rwxr-xr-x)
            os.chmod(self.log_dir, 0o755)
        except PermissionError:
            # If we can't create /var/log/artemis, fall back to /tmp
            print(f"WARNING: Cannot create {self.log_dir}, falling back to /tmp/artemis_logs", file=sys.stderr)
            self.log_dir = Path("/tmp/artemis_logs")
            self.log_dir.mkdir(parents=True, exist_ok=True)

        # Create logger
        logger = logging.getLogger(f"artemis.{self.component}")
        logger.setLevel(self.log_level)

        # Remove existing handlers
        logger.handlers = []

        # Create formatters
        detailed_formatter = logging.Formatter(
            fmt='%(asctime)s [%(levelname)s] [%(name)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        # Main log file (with rotation)
        main_log_file = self.log_dir / f"artemis_{self.component}.log"
        main_handler = logging.handlers.RotatingFileHandler(
            main_log_file,
            maxBytes=self.max_bytes,
            backupCount=self.backup_count
        )
        main_handler.setLevel(self.log_level)
        main_handler.setFormatter(detailed_formatter)
        logger.addHandler(main_handler)

        # Error-only log file (for monitoring)
        error_log_file = self.log_dir / "artemis_errors.log"
        error_handler = logging.handlers.RotatingFileHandler(
            error_log_file,
            maxBytes=self.max_bytes,
            backupCount=self.backup_count
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(detailed_formatter)
        logger.addHandler(error_handler)

        # Console handler (for immediate feedback)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(self.log_level)
        console_formatter = logging.Formatter(
            fmt='[%(levelname)s] %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)

        return logger

    def debug(self, message: str):
        """
        Log debug message.

        Why needed: Provides detailed diagnostic information for development
        and troubleshooting. Only visible when log level is DEBUG.

        Args:
            message: Debug message to log
        """
        self.logger.debug(message)

    def info(self, message: str):
        """
        Log info message.

        Why needed: Records normal operational events (stage start/complete,
        pipeline progress, configuration changes).

        Args:
            message: Informational message to log
        """
        self.logger.info(message)

    def warning(self, message: str):
        """
        Log warning message.

        Why needed: Alerts about potential issues that don't prevent execution
        but may require attention (fallback usage, deprecated features, retries).

        Args:
            message: Warning message to log
        """
        self.logger.warning(message)

    def error(self, message: str):
        """
        Log error message.

        Why needed: Records errors that affect functionality but allow pipeline
        to continue (stage failures, recovery attempts, resource issues).
        Also written to artemis_errors.log for monitoring.

        Args:
            message: Error message to log
        """
        self.logger.error(message)

    def critical(self, message: str):
        """
        Log critical message.

        Why needed: Records catastrophic failures that prevent pipeline execution
        (missing config, system resource exhaustion, fatal exceptions).
        Also written to artemis_errors.log for immediate attention.

        Args:
            message: Critical error message to log
        """
        self.logger.critical(message)

    def log(self, message: str, level: str = "INFO"):
        """
        Log message at specified level (for compatibility with existing code).

        Why needed: Provides backwards compatibility with legacy Artemis code that
        used custom log levels (SUCCESS, STAGE). Maps custom levels to standard
        Python logging levels.

        Args:
            message: Message to log
            level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL, SUCCESS, STAGE)
                  Custom levels (SUCCESS, STAGE) are mapped to INFO

        Design decision: Map custom levels instead of extending logging module
        to maintain compatibility with standard Python logging infrastructure.
        """
        # Map custom levels to standard ones
        level_map = {
            "SUCCESS": "INFO",
            "STAGE": "INFO",
            "WARNING": "WARNING",
            "ERROR": "ERROR",
            "CRITICAL": "CRITICAL",
            "DEBUG": "DEBUG"
        }

        standard_level = level_map.get(level.upper(), "INFO")

        if standard_level == "DEBUG":
            self.debug(message)
            return

        if standard_level == "INFO":
            self.info(message)
            return

        if standard_level == "WARNING":
            self.warning(message)
            return

        if standard_level == "ERROR":
            self.error(message)
            return

        if standard_level == "CRITICAL":
            self.critical(message)
            return

        # Default case
        self.info(message)

    def get_log_path(self) -> Path:
        """
        Get the path to the main log file.

        Why needed: Allows external tools to locate log files for monitoring,
        analysis, or log shipping to centralized logging systems.

        Returns:
            Path to component-specific log file
        """
        return self.log_dir / f"artemis_{self.component}.log"

    def get_error_log_path(self) -> Path:
        """
        Get the path to the error log file.

        Why needed: Allows monitoring systems to watch the shared error log
        for alerts and notifications across all components.

        Returns:
            Path to shared error log file (artemis_errors.log)
        """
        return self.log_dir / "artemis_errors.log"


# Global logger instance (Singleton pattern for default logger)
# Why: Prevents multiple logger instances from being created unnecessarily,
# reducing resource usage and ensuring consistent configuration
_default_logger: Optional[ArtemisLogger] = None


def get_logger(component: str = "main") -> ArtemisLogger:
    """
    Get or create the global Artemis logger (Factory function).

    Why needed: Provides convenient access to logger without requiring explicit
    initialization. Implements lazy initialization pattern.

    Args:
        component: Component name for logging (main, supervisor, developers, etc.)
                  Creates new logger if component changes

    Returns:
        ArtemisLogger instance (reused if component matches, new if changed)

    Design pattern: Factory + Singleton hybrid
        - Factory: Creates logger instances on demand
        - Singleton: Reuses logger for same component

    Thread-safety: Not thread-safe (assumes single-threaded initialization)
    """
    global _default_logger
    if _default_logger is None or _default_logger.component != component:
        _default_logger = ArtemisLogger(component=component)
    return _default_logger


def setup_logging(component: str = "main", log_level: str = "INFO"):
    """
    Setup Artemis logging system with explicit configuration.

    Why needed: Provides explicit logger initialization with custom log level,
    typically called at application startup before other modules initialize.

    Args:
        component: Component name (main, supervisor, developers, etc.)
        log_level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
                  Overrides default INFO level

    Returns:
        ArtemisLogger instance (stored as global default)

    Usage:
        Called once at application startup:
        logger = setup_logging("main", "DEBUG")

    Side effects:
        Sets global _default_logger variable
    """
    global _default_logger
    _default_logger = ArtemisLogger(component=component, log_level=log_level)
    return _default_logger


if __name__ == "__main__":
    # Test the logger
    logger = ArtemisLogger(component="test")

    logger.info("Testing Artemis logger")
    logger.debug("This is a debug message")
    logger.warning("This is a warning")
    logger.error("This is an error")

    print(f"\nLog file: {logger.get_log_path()}")
    print(f"Error log: {logger.get_error_log_path()}")
