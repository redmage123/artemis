"""
Module: services.core.pipeline_logger

WHY: Separates logging concerns from business logic and provides consistent,
     readable output format across all pipeline stages. Enables easy testing
     by allowing log suppression and output capture.

RESPONSIBILITY: Provide formatted console logging with timestamps and visual indicators.

PATTERNS:
- Single Responsibility: Only handles logging and output formatting
- Singleton (optional): Can be configured as single instance across pipeline
- Strategy Pattern: Log format can be customized via formatters
- Interface Segregation: Implements LoggerInterface for standard logging API

DESIGN DECISIONS:
- Emoji indicators (quick visual scanning of logs)
- UTC timestamps (consistency across timezones in distributed systems)
- Verbosity control (silence during testing)
- Standard library compatibility (drop-in replacement for logging.Logger)
- Dispatch table for log levels (avoids if/elif chains)

Dependencies: core.interfaces
"""
from datetime import datetime
from typing import Any, Callable, Dict, Optional
from core.interfaces import LoggerInterface
from artemis_logger import get_logger

class PipelineLogger(LoggerInterface):
    """
    Formatted console logging service for pipeline operations.

    WHAT: Provides formatted console logging with timestamps and emoji indicators.
    WHY: Consistent, readable output format makes debugging and monitoring easier.

    Attributes:
        verbose: Whether to output log messages (False = silent mode)
        formatter: Custom formatter function (optional)

    Example:
        >>> logger = PipelineLogger(verbose=True)
        >>> logger.info("Processing started")
        [12:34:56] ℹ️ Processing started
        >>> logger.success("Processing completed")
        [12:34:57] ✅ Processing completed
    """
    EMOJI_MAP: Dict[str, str] = {'DEBUG': '🔍', 'INFO': 'ℹ️', 'SUCCESS': '✅', 'WARNING': '⚠️', 'ERROR': '❌', 'CRITICAL': '🔥', 'STAGE': '🔄', 'PIPELINE': '⚙️', 'TEST': '🧪', 'DEPLOY': '🚀'}
    DEFAULT_EMOJI: str = '•'
    TIMESTAMP_FORMAT: str = '%H:%M:%S'

    def __init__(self, verbose: bool=True, formatter: Optional[Callable[[str, str, str], str]]=None) -> None:
        """
        Initialize pipeline logger.

        Args:
            verbose: Enable/disable log output (default: True)
            formatter: Optional custom formatter function

        WHY: Allows silencing logs during testing or batch operations.
             Custom formatter enables different output formats (JSON, CSV, etc).

        Example:
            >>> logger = PipelineLogger(verbose=False)  # Silent mode
            >>> logger = PipelineLogger(formatter=json_formatter)  # Custom format
        """
        self.verbose: bool = verbose
        self.formatter: Optional[Callable[[str, str, str], str]] = formatter
        self._logger = get_logger('pipeline')

    def log(self, message: str, level: str='INFO', **kwargs: Any) -> None:
        """
        Log message with timestamp and emoji indicator.

        WHAT: Formats and prints log message with UTC timestamp and level-specific emoji.
        WHY: Timestamps help trace execution order, emojis make scanning logs easier.

        Args:
            message: Message to log
            level: Log level (INFO, WARNING, ERROR, etc.)
            **kwargs: Additional context (ignored for console output, available for custom formatters)

        Example:
            >>> logger.log("Test started", level="TEST")
            [12:34:56] 🧪 Test started
        """
        if not self.verbose:
            return
        timestamp = self._get_timestamp()
        emoji = self._get_emoji(level)
        formatted_message = self._format_message(timestamp, emoji, message)

        self._logger.log(formatted_message, 'INFO')

    def _get_timestamp(self) -> str:
        """
        Get current UTC timestamp.

        Returns:
            Formatted timestamp string (HH:MM:SS)

        WHY: UTC avoids timezone confusion in distributed systems.
        """
        return datetime.utcnow().strftime(self.TIMESTAMP_FORMAT)

    def _get_emoji(self, level: str) -> str:
        """
        Get emoji for log level using dispatch table.

        Args:
            level: Log level string

        Returns:
            Emoji character for level

        WHY: Dispatch table avoids if/elif chain and is easily extensible.
        """
        return self.EMOJI_MAP.get(level.upper(), self.DEFAULT_EMOJI)

    def _format_message(self, timestamp: str, emoji: str, message: str) -> str:
        """
        Format log message with timestamp and emoji.

        Args:
            timestamp: Timestamp string
            emoji: Emoji indicator
            message: Log message

        Returns:
            Formatted message string

        WHY: Separates formatting logic for easier testing and customization.
        """
        if self.formatter:
            return self.formatter(timestamp, emoji, message)
        return f'[{timestamp}] {emoji} {message}'

    def debug(self, message: str, **kwargs: Any) -> None:
        """
        Log debug message.

        WHAT: Standard logging interface method mapping to log() with DEBUG level.
        WHY: Enables drop-in replacement of Python's standard logger.

        Args:
            message: Debug message
            **kwargs: Additional context (ignored for compatibility)
        """
        self.log(message, 'DEBUG', **kwargs)

    def info(self, message: str, **kwargs: Any) -> None:
        """
        Log info message.

        WHAT: Standard logging interface method mapping to log() with INFO level.
        WHY: Enables drop-in replacement of Python's standard logger.

        Args:
            message: Info message
            **kwargs: Additional context (ignored for compatibility)
        """
        self.log(message, 'INFO', **kwargs)

    def warning(self, message: str, **kwargs: Any) -> None:
        """
        Log warning message.

        WHAT: Standard logging interface method mapping to log() with WARNING level.
        WHY: Enables drop-in replacement of Python's standard logger.

        Args:
            message: Warning message
            **kwargs: Additional context (ignored for compatibility)
        """
        self.log(message, 'WARNING', **kwargs)

    def error(self, message: str, **kwargs: Any) -> None:
        """
        Log error message.

        WHAT: Standard logging interface method mapping to log() with ERROR level.
        WHY: Enables drop-in replacement of Python's standard logger.

        Args:
            message: Error message
            **kwargs: Additional context (ignored for compatibility)
        """
        self.log(message, 'ERROR', **kwargs)

    def critical(self, message: str, **kwargs: Any) -> None:
        """
        Log critical message.

        WHAT: Standard logging interface method mapping to log() with CRITICAL level.
        WHY: Enables drop-in replacement of Python's standard logger.

        Args:
            message: Critical message
            **kwargs: Additional context (ignored for compatibility)
        """
        self.log(message, 'CRITICAL', **kwargs)

    def success(self, message: str, **kwargs: Any) -> None:
        """
        Log success message with green checkmark.

        WHY: Pipeline operations need clear success indicators.

        Args:
            message: Success message
            **kwargs: Additional context
        """
        self.log(message, 'SUCCESS', **kwargs)

    def stage(self, message: str, **kwargs: Any) -> None:
        """
        Log stage transition message.

        WHY: Pipeline stage transitions need clear visual separation.

        Args:
            message: Stage message
            **kwargs: Additional context
        """
        self.log(message, 'STAGE', **kwargs)

    def pipeline(self, message: str, **kwargs: Any) -> None:
        """
        Log pipeline-level message.

        WHY: Distinguish pipeline-wide events from stage-specific events.

        Args:
            message: Pipeline message
            **kwargs: Additional context
        """
        self.log(message, 'PIPELINE', **kwargs)

    def set_verbose(self, verbose: bool) -> None:
        """
        Enable or disable verbose logging.

        Args:
            verbose: New verbosity setting

        WHY: Allows runtime control of log output (useful for testing).

        Example:
            >>> logger.set_verbose(False)  # Silence logs
            >>> run_tests()
            >>> logger.set_verbose(True)   # Re-enable logs
        """
        self.verbose = verbose

    def is_verbose(self) -> bool:
        """
        Check if verbose logging is enabled.

        Returns:
            Current verbosity setting

        WHY: Allows conditional logging in performance-critical sections.
        """
        return self.verbose

def create_logger(verbose: bool=True) -> PipelineLogger:
    """
    Factory function to create PipelineLogger instance.

    WHY: Enables dependency injection and easier testing/mocking.
    PATTERN: Factory Method pattern

    Args:
        verbose: Enable verbose output

    Returns:
        Configured PipelineLogger instance

    Example:
        >>> logger = create_logger(verbose=False)
    """
    return PipelineLogger(verbose=verbose)

def create_silent_logger() -> PipelineLogger:
    """
    Factory function to create silent logger (for testing).

    WHY: Common pattern in tests - makes intent explicit.

    Returns:
        PipelineLogger with verbose=False

    Example:
        >>> logger = create_silent_logger()
        >>> logger.info("This won't print")
    """
    return PipelineLogger(verbose=False)
__all__ = ['PipelineLogger', 'create_logger', 'create_silent_logger']