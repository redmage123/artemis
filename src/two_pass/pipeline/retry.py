from artemis_logger import get_logger
logger = get_logger('retry')
'\nModule: two_pass/pipeline/retry.py\n\nWHY: Encapsulates retry logic for pass execution resilience.\nRESPONSIBILITY: Retry strategies, configuration, and failure handling.\nPATTERNS: Strategy Pattern, Guard Clauses.\n\nThis module handles:\n- Retry configuration and policy\n- Execution with exponential backoff\n- Transient failure detection\n- Retry state tracking\n'
from typing import Callable, TypeVar, Any
from dataclasses import dataclass
import time
from artemis_exceptions import wrap_exception
from two_pass.exceptions import TwoPassPipelineException
T = TypeVar('T')

@dataclass
class RetryConfig:
    """
    Configuration for retry behavior.

    Why: Centralizes retry policy configuration. Immutable by default.

    Attributes:
        max_retries: Maximum number of retry attempts (default: 3)
        base_delay: Base delay in seconds between retries (default: 1.0)
        max_delay: Maximum delay cap for exponential backoff (default: 30.0)
        exponential_base: Base for exponential backoff calculation (default: 2.0)
        verbose: Enable detailed retry logging (default: False)
    """
    max_retries: int = 3
    base_delay: float = 1.0
    max_delay: float = 30.0
    exponential_base: float = 2.0
    verbose: bool = False

class RetryStrategy:
    """
    Implements retry logic with exponential backoff.

    Why it exists: Encapsulates retry behavior for transient failures.
    Makes pass execution more resilient without cluttering orchestrator.

    Design pattern: Strategy Pattern
    Why this design:
    - Strategy: Pluggable retry behavior (could swap for linear, fibonacci, etc.)
    - Separates retry concerns from business logic

    Responsibilities:
    - Execute callable with retry on failure
    - Calculate backoff delays (exponential)
    - Track retry attempts
    - Log retry attempts if verbose

    Thread-safety: Not thread-safe (assumes single-threaded execution per instance)
    """

    def __init__(self, config: RetryConfig):
        """
        Initialize retry strategy with configuration.

        Args:
            config: Retry configuration policy
        """
        self.config = config
        self.retry_count = 0

    @wrap_exception(TwoPassPipelineException, 'Retry execution failed')
    def retry(self, func: Callable[[], T]) -> T:
        """
        Execute callable with retry on failure.

        What it does:
        1. Attempt execution
        2. On failure, calculate backoff delay
        3. Wait and retry up to max_retries times
        4. Return result if successful
        5. Raise exception if all retries exhausted

        Args:
            func: Callable to execute with retry

        Returns:
            Result from successful execution

        Raises:
            TwoPassPipelineException: If all retries exhausted

        Design notes:
        - Uses exponential backoff to avoid overwhelming failing services
        - Caps delay at max_delay to prevent excessive waiting
        - Logs retry attempts for debugging
        """
        last_exception = None
        for attempt in range(self.config.max_retries + 1):
            try:
                if attempt == 0:
                    return func()
                delay = self._calculate_backoff_delay(attempt)
                if self.config.verbose:
                    
                    logger.log(f'Retry attempt {attempt}/{self.config.max_retries} after {delay:.2f}s delay', 'INFO')
                time.sleep(delay)
                return func()
            except Exception as e:
                last_exception = e
                if attempt == self.config.max_retries:
                    break
                continue
        raise TwoPassPipelineException(f'Failed after {self.config.max_retries} retries: {last_exception}') from last_exception

    def _calculate_backoff_delay(self, attempt: int) -> float:
        """
        Calculate exponential backoff delay.

        Why extracted: Isolates backoff calculation logic. Makes it easy to
        change backoff strategy (linear, fibonacci, etc.).

        Formula: min(base_delay * (exponential_base ^ attempt), max_delay)

        Args:
            attempt: Current retry attempt number (1-indexed)

        Returns:
            Delay in seconds, capped at max_delay
        """
        if attempt == 0:
            return 0.0
        delay = self.config.base_delay * self.config.exponential_base ** (attempt - 1)
        return min(delay, self.config.max_delay)

    def reset(self) -> None:
        """
        Reset retry counter.

        Why: Allows reusing strategy instance for multiple operations.
        """
        self.retry_count = 0
__all__ = ['RetryStrategy', 'RetryConfig']