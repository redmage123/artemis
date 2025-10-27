#!/usr/bin/env python3
"""
Streaming Validator (Layer 3.6: Real-time Validation During Generation)

WHY: Catches hallucinations DURING code generation, not after.
     Saves tokens and time by stopping generation early.

Example:
    LLM generates: "from kafka import KafkaProducer"
    Streaming validator: Detects Kafka not in requirements, STOPS generation immediately.
    Standard validator: Waits for complete code, then fails (wastes tokens).

PERFORMANCE: Validates every 50 tokens (configurable), low overhead.
SOLID: Single Responsibility - only validates during streaming.
"""

from typing import Dict, List, Optional, Callable, Tuple
from dataclasses import dataclass
import re
from datetime import datetime

from artemis_stage_interface import LoggerInterface


@dataclass
class StreamingValidationResult:
    """
    Result of streaming validation check.

    Attributes:
        should_continue: True to continue generation, False to stop
        reason: Why generation was stopped (if stopped)
        validated_tokens: Number of tokens validated so far
        warnings: Non-fatal issues detected
    """
    should_continue: bool
    reason: Optional[str] = None
    validated_tokens: int = 0
    warnings: List[str] = None

    def __post_init__(self):
        if self.warnings is None:
            self.warnings = []


class StreamingValidator:
    """
    Validates code during LLM streaming generation (real-time).

    WHY: Stops hallucinations early:
         - Placeholder detection: "# TODO", "pass", "..."
         - Invalid imports: Imports not in requirements
         - Forbidden patterns: eval(), exec(), os.system()

    Single Responsibility: ONLY streaming validation.
    No standard validation logic - delegates to validation_pipeline for that.
    """

    # Validation check intervals (avoid nested ifs - use constants)
    VALIDATION_INTERVALS = {
        'lightweight': 25,   # Check every 25 tokens (fast checks only)
        'standard': 50,      # Check every 50 tokens (default)
        'thorough': 100      # Check every 100 tokens (all checks)
    }

    # Placeholder patterns that indicate incomplete code
    PLACEHOLDER_PATTERNS = [
        r'#\s*TODO',
        r'#\s*FIXME',
        r'#\s*XXX',
        r'\.\.\.',  # Ellipsis
        r'pass\s*$',  # Pass at end of line
        r'raise\s+NotImplementedError',
    ]

    # Forbidden patterns (security/hallucination risks)
    FORBIDDEN_PATTERNS = {
        'eval': r'\beval\s*\(',
        'exec': r'\bexec\s*\(',
        'os.system': r'os\.system\s*\(',
        '__import__': r'__import__\s*\(',
    }

    def __init__(
        self,
        logger: Optional[LoggerInterface] = None,
        validation_mode: str = 'standard',
        allowed_imports: Optional[List[str]] = None,
        stop_on_placeholder: bool = True,
        stop_on_forbidden: bool = True
    ):
        """
        Initialize streaming validator.

        Args:
            logger: Optional logger
            validation_mode: 'lightweight', 'standard', or 'thorough'
            allowed_imports: List of allowed import modules (from requirements)
            stop_on_placeholder: Stop generation if placeholder detected
            stop_on_forbidden: Stop generation if forbidden pattern detected
        """
        self.logger = logger
        self.validation_mode = validation_mode
        self.allowed_imports = allowed_imports or []
        self.stop_on_placeholder = stop_on_placeholder
        self.stop_on_forbidden = stop_on_forbidden

        # Streaming state
        self.buffer = ""
        self.token_count = 0
        self.last_validation_at = 0
        self.validation_count = 0
        self.stop_events = []  # History of stop events

        # Compile patterns once (performance optimization)
        self.placeholder_regex = re.compile(
            '|'.join(self.PLACEHOLDER_PATTERNS),
            re.IGNORECASE | re.MULTILINE
        )

        self.forbidden_regex = {
            name: re.compile(pattern)
            for name, pattern in self.FORBIDDEN_PATTERNS.items()
        }

        if self.logger:
            self.logger.log(
                f"🌊 Streaming validator initialized (mode: {validation_mode})",
                "DEBUG"
            )

    def on_token(self, token: str) -> StreamingValidationResult:
        """
        Called for each streamed token from LLM.

        Args:
            token: Single token from LLM stream

        Returns:
            StreamingValidationResult with should_continue flag

        WHY: This is the core streaming validation hook.
             Called thousands of times during generation.
             MUST be fast (< 1ms per token).
        """
        self.buffer += token
        self.token_count += 1

        # Check if we should validate at this token count
        interval = self.VALIDATION_INTERVALS[self.validation_mode]
        tokens_since_last = self.token_count - self.last_validation_at

        if tokens_since_last < interval:
            # Not time to validate yet, continue generation
            return StreamingValidationResult(should_continue=True)

        # Time to validate - run lightweight checks
        result = self._validate_buffer()

        # Handle validation failure (avoid nested ifs - extract to helper)
        if not result.should_continue:
            self._handle_validation_failure(result)

        # Update validation state
        self.last_validation_at = self.token_count
        self.validation_count += 1
        result.validated_tokens = self.token_count

        return result

    def _handle_validation_failure(self, result: StreamingValidationResult):
        """
        Handle validation failure.

        WHY: Extracted from on_token() to avoid nested ifs.
        PERFORMANCE: Early return pattern for optional logging.
        """
        self._record_stop_event(result.reason)

        # Early return if no logger (avoid nested if)
        if not self.logger:
            return

        self.logger.log(
            f"⚠️  Streaming validation STOPPED generation: {result.reason}",
            "WARNING"
        )

    def _validate_buffer(self) -> StreamingValidationResult:
        """
        Validate current buffer content.

        Returns:
            StreamingValidationResult

        WHY: Runs lightweight validation checks on buffered tokens.
        PATTERNS: Strategy pattern with validation strategies (no sequential ifs).
        PERFORMANCE: Stops at first failure (early return pattern).
        """
        # Strategy pattern: List of (enabled, validator_func) tuples
        # This replaces sequential ifs with a clean iteration pattern
        validation_strategies = [
            (self.stop_on_placeholder, self._check_placeholders),
            (self.stop_on_forbidden, self._check_forbidden_patterns),
            (bool(self.allowed_imports), self._check_imports)
        ]

        warnings = []

        # Run each enabled validation strategy
        for is_enabled, validator_func in validation_strategies:
            if not is_enabled:
                continue

            result = validator_func()

            # Early return on first failure (performance optimization)
            if not result.should_continue:
                return result

            warnings.extend(result.warnings)

        # All checks passed
        return StreamingValidationResult(
            should_continue=True,
            validated_tokens=self.token_count,
            warnings=warnings
        )

    def _check_placeholders(self) -> StreamingValidationResult:
        """
        Check for placeholder patterns.

        WHY: Placeholders indicate incomplete/hallucinated code.
             Example: "# TODO: Implement Kafka connection"
        """
        match = self.placeholder_regex.search(self.buffer)

        if match:
            placeholder = match.group(0)
            return StreamingValidationResult(
                should_continue=False,
                reason=f"Placeholder detected: '{placeholder}'",
                validated_tokens=self.token_count
            )

        return StreamingValidationResult(should_continue=True)

    def _check_forbidden_patterns(self) -> StreamingValidationResult:
        """
        Check for forbidden patterns (security/hallucination risks).

        WHY: Patterns like eval(), exec() are hallucination indicators.
             Real code rarely uses these (and shouldn't).
        """
        # Use dictionary mapping instead of if/elif chain (SOLID)
        for pattern_name, pattern_regex in self.forbidden_regex.items():
            match = pattern_regex.search(self.buffer)
            if match:
                return StreamingValidationResult(
                    should_continue=False,
                    reason=f"Forbidden pattern detected: {pattern_name}()",
                    validated_tokens=self.token_count
                )

        return StreamingValidationResult(should_continue=True)

    def _check_imports(self) -> StreamingValidationResult:
        """
        Check imports against allowed list.

        WHY: LLMs hallucinate imports for libraries not in requirements.
             Example: "from kafka import KafkaProducer" when Kafka not required.
        """
        # Extract imports from buffer
        import_pattern = r'(?:from|import)\s+(\w+)'
        imports = re.findall(import_pattern, self.buffer)

        # Check each import against allowed list
        for imported_module in imports:
            if not self._is_import_allowed(imported_module):
                return StreamingValidationResult(
                    should_continue=False,
                    reason=f"Hallucinated import detected: '{imported_module}' not in requirements",
                    validated_tokens=self.token_count
                )

        return StreamingValidationResult(should_continue=True)

    def _is_import_allowed(self, module_name: str) -> bool:
        """
        Check if import is allowed (early return pattern).

        WHY: Avoids nested ifs by using early returns.
        """
        # Standard library modules are always allowed
        stdlib_modules = {
            'os', 'sys', 'json', 'datetime', 'typing', 'pathlib',
            'unittest', 'pytest', 'mock', 're', 'collections',
            'itertools', 'functools', 'dataclasses', 'enum',
            'abc', 'asyncio', 'concurrent', 'threading', 'multiprocessing'
        }

        if module_name in stdlib_modules:
            return True

        # Check against allowed imports list
        if module_name in self.allowed_imports:
            return True

        # Check partial matches (e.g., "django.db" matches "django")
        for allowed in self.allowed_imports:
            if module_name.startswith(f"{allowed}."):
                return True

        return False

    def _record_stop_event(self, reason: str):
        """
        Record when generation was stopped.

        WHY: Enables learning from streaming validation patterns.
             Supervisor can analyze: What patterns trigger stops?
        """
        self.stop_events.append({
            'timestamp': datetime.now().isoformat(),
            'reason': reason,
            'token_count': self.token_count,
            'buffer_snippet': self.buffer[-100:] if len(self.buffer) > 100 else self.buffer
        })

    def reset(self):
        """
        Reset validator state for new generation.

        WHY: Reuse validator across multiple generations.
        """
        self.buffer = ""
        self.token_count = 0
        self.last_validation_at = 0
        self.validation_count = 0
        # Keep stop_events for learning

    def get_stats(self) -> Dict:
        """
        Get validation statistics.

        WHY: Enables monitoring and optimization:
             - How often do we stop generation?
             - What patterns trigger stops?
             - Is validation overhead acceptable?
        """
        return {
            'token_count': self.token_count,
            'validation_count': self.validation_count,
            'stop_events': len(self.stop_events),
            'validation_mode': self.validation_mode,
            'validation_interval': self.VALIDATION_INTERVALS[self.validation_mode],
            'avg_tokens_per_validation': (
                self.token_count / self.validation_count
                if self.validation_count > 0 else 0
            )
        }


class StreamingValidatorFactory:
    """
    Factory for creating streaming validators.

    WHY: Centralized configuration for different validation modes.
         SOLID: Open/Closed - add new modes without changing existing code.
    """

    # Pre-configured validation modes (avoid if/elif chain)
    MODES = {
        'lightweight': {
            'validation_mode': 'lightweight',
            'stop_on_placeholder': False,  # Allow placeholders
            'stop_on_forbidden': True,     # Stop on security issues
        },
        'standard': {
            'validation_mode': 'standard',
            'stop_on_placeholder': True,   # Stop on placeholders
            'stop_on_forbidden': True,     # Stop on security issues
        },
        'thorough': {
            'validation_mode': 'thorough',
            'stop_on_placeholder': True,   # Stop on placeholders
            'stop_on_forbidden': True,     # Stop on security issues
        }
    }

    @staticmethod
    def create_validator(
        mode: str = 'standard',
        allowed_imports: Optional[List[str]] = None,
        logger: Optional[LoggerInterface] = None
    ) -> StreamingValidator:
        """
        Create streaming validator with pre-configured mode.

        Args:
            mode: 'lightweight', 'standard', or 'thorough'
            allowed_imports: List of allowed import modules
            logger: Optional logger

        Returns:
            Configured StreamingValidator
        """
        config = StreamingValidatorFactory.MODES.get(mode, StreamingValidatorFactory.MODES['standard'])

        return StreamingValidator(
            logger=logger,
            allowed_imports=allowed_imports,
            **config
        )
