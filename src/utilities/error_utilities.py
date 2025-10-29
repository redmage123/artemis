from artemis_logger import get_logger
logger = get_logger('error_utilities')
'\nModule: utilities/error_utilities.py\n\nWHY: Provides standardized error handling and exception wrapping.\n     Eliminates 144+ duplicate try/except blocks across the codebase,\n     ensuring consistent error logging and handling patterns.\n\nRESPONSIBILITY:\n- Execute operations with standardized error handling\n- Wrap exceptions with additional context\n- Provide both exception-raising and default-value-returning variants\n- Log errors consistently for debugging\n- Support workflow handler patterns (bool returns)\n\nPATTERNS:\n- Template Method Pattern: handle_with_logging defines error handling algorithm\n- Strategy Pattern: Configurable error handling behavior (raise vs return default)\n- Facade Pattern: Simplifies error handling by hiding try/except complexity\n\nBenefits:\n- Consistent error messages across entire codebase\n- Centralized error logging configuration\n- Reduces boilerplate from 5+ lines to 1 function call\n- Makes error handling testable\n\nIntegration: Used by all pipeline stages, agents, and orchestrator components\n             for consistent error handling.\n'
from typing import Callable, Optional, TypeVar
from artemis_exceptions import wrap_exception, PipelineStageError
T = TypeVar('T')

class ErrorHandler:
    """
    Standardized error handling and wrapping

    WHY: Eliminates 144+ duplicate try/except blocks.
         Before this class, every operation had custom error handling
         leading to inconsistent logging and error messages.

    RESPONSIBILITY:
    - Execute operations with standardized error handling
    - Wrap exceptions with additional context
    - Log errors consistently
    - Support both raise and return-default behaviors
    """

    def __init__(self, verbose: bool=True):
        """
        Initialize error handler

        Args:
            verbose: Whether to print error messages for debugging
        """
        self.verbose = verbose

    def handle_with_logging(self, operation: Callable[[], T], operation_name: str, error_message: str='Operation failed', default_return: Optional[T]=None, raise_on_error: bool=False) -> Optional[T]:
        """
        Execute operation with standardized error handling

        WHY: Provides consistent error handling pattern across all operations.
             Single place to enhance error handling (add metrics, alerts, etc).

        Args:
            operation: Callable to execute
            operation_name: Name for logging
            error_message: Message to show on error
            default_return: Value to return on error (if not raising)
            raise_on_error: Whether to raise or return default

        Returns:
            Result from operation, or default_return on error

        Raises:
            Wrapped exception if raise_on_error=True
        """
        try:
            return operation()
        except Exception as e:
            self._log_error(operation_name, e)
            if raise_on_error:
                raise wrap_exception(e, PipelineStageError, error_message, context={'operation': operation_name})
            return default_return

    def _log_error(self, operation_name: str, error: Exception) -> None:
        """Log error if verbose mode enabled (guard clause pattern)"""
        if not self.verbose:
            return
        
        logger.log(f'[ErrorHandler] {operation_name} failed: {error}', 'INFO')

    def wrap_operation(self, operation: Callable[[], bool], operation_name: str, success_message: Optional[str]=None, error_message: Optional[str]=None) -> bool:
        """
        Wrap operation that returns bool, with logging

        WHY: Common pattern for workflow handlers that return True/False
             instead of raising exceptions. Provides consistent logging.

        Args:
            operation: Callable returning bool
            operation_name: Name for logging
            success_message: Message on success
            error_message: Message on error

        Returns:
            True if succeeded, False if failed
        """
        try:
            result = operation()
            self._log_result(operation_name, result, success_message, error_message)
            return result
        except Exception as e:
            self._log_exception(operation_name, e)
            return False

    def _log_result(self, operation_name: str, result: bool, success_message: Optional[str], error_message: Optional[str]) -> None:
        """Log operation result if verbose mode enabled (guard clause pattern)"""
        if not self.verbose:
            return
        if result and success_message:
            
            logger.log(f'[{operation_name}] {success_message}', 'INFO')
        elif not result and error_message:
            
            logger.log(f'[{operation_name}] {error_message}', 'INFO')

    def _log_exception(self, operation_name: str, error: Exception) -> None:
        """Log exception if verbose mode enabled (guard clause pattern)"""
        if not self.verbose:
            return
        
        logger.log(f'[{operation_name}] Failed with exception: {error}', 'INFO')
_default_error_handler = ErrorHandler()

def safe_execute(operation: Callable[[], T], operation_name: str, default: Optional[T]=None) -> Optional[T]:
    """
    Convenience function for safe execution with error handling

    WHY: Simplifies one-off safe execution calls without creating ErrorHandler instance.
         Common pattern for optional operations that shouldn't crash entire pipeline.

    Args:
        operation: Callable to execute
        operation_name: Name for logging
        default: Default value to return on error

    Returns:
        Result from operation, or default on error
    """
    return _default_error_handler.handle_with_logging(operation, operation_name, default_return=default, raise_on_error=False)