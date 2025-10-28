#!/usr/bin/env python3
"""
Messenger Validation Module

WHY: Validates messenger backend availability before pipeline execution

RESPONSIBILITY: Validate messaging system connectivity for agent communication

PATTERNS: Strategy pattern via dispatch table for different messenger types
"""

import os
from pathlib import Path
from typing import Callable, Dict
from ..models import ValidationResult
from ..constants import DEFAULT_MESSENGER_TYPE, DEFAULT_MESSAGE_DIR, DEFAULT_RABBITMQ_URL


class MessengerValidator:
    """
    Validates messenger backend availability

    WHY: Single Responsibility - handles only messenger validation

    PATTERNS: Strategy pattern for different messenger types
    """

    def validate_messenger(self) -> ValidationResult:
        """
        Check messenger backend availability

        WHY: Validates messaging system before pipeline runs
        PATTERNS: Strategy pattern via dictionary mapping
        PERFORMANCE: O(1) for file check, O(n) for network check (RabbitMQ)

        Returns:
            ValidationResult for messenger check
        """
        messenger_type = os.getenv("ARTEMIS_MESSENGER_TYPE", DEFAULT_MESSENGER_TYPE)

        # Strategy pattern: Dictionary mapping instead of if/elif chain
        # WHY: Makes it easy to add new messenger types without modifying code structure
        messenger_checks: Dict[str, Callable[[], ValidationResult]] = {
            "file": self._check_file_messenger,
            "rabbitmq": self._check_rabbitmq_messenger,
            "mock": self._check_mock_messenger
        }

        check_func = messenger_checks.get(messenger_type)
        if not check_func:
            return ValidationResult(
                check_name="Messenger",
                passed=False,
                message=f"Unknown messenger type: {messenger_type}",
                fix_suggestion="Set ARTEMIS_MESSENGER_TYPE to 'file', 'rabbitmq', or 'mock'"
            )

        return check_func()

    def _check_file_messenger(self) -> ValidationResult:
        """
        Check file-based messenger

        WHY: Extracted to avoid nested if statements
        PERFORMANCE: O(1) directory creation check

        Returns:
            ValidationResult for file messenger check
        """
        message_dir = os.getenv("ARTEMIS_MESSAGE_DIR", DEFAULT_MESSAGE_DIR)
        try:
            Path(message_dir).mkdir(parents=True, exist_ok=True)
            return ValidationResult(
                check_name="File Messenger",
                passed=True,
                message=f"Message directory accessible: {message_dir}"
            )
        except Exception as e:
            return ValidationResult(
                check_name="File Messenger",
                passed=False,
                message=f"Cannot create message directory: {e}",
                fix_suggestion=f"Ensure {message_dir} is writable"
            )

    def _check_rabbitmq_messenger(self) -> ValidationResult:
        """
        Check RabbitMQ messenger

        WHY: Extracted to avoid nested if statements
        PERFORMANCE: O(n) network connection with 1 retry (short timeout)

        Returns:
            ValidationResult for RabbitMQ messenger check
        """
        try:
            import pika
            rabbitmq_url = os.getenv("ARTEMIS_RABBITMQ_URL", DEFAULT_RABBITMQ_URL)
            # Try to connect (with short timeout)
            params = pika.URLParameters(rabbitmq_url)
            params.connection_attempts = 1
            params.retry_delay = 1
            conn = pika.BlockingConnection(params)
            conn.close()

            return ValidationResult(
                check_name="RabbitMQ Messenger",
                passed=True,
                message=f"Connected to RabbitMQ at {rabbitmq_url}"
            )
        except ImportError:
            return ValidationResult(
                check_name="RabbitMQ Messenger",
                passed=False,
                message="pika library not installed",
                fix_suggestion="pip install pika"
            )
        except Exception as e:
            return ValidationResult(
                check_name="RabbitMQ Messenger",
                passed=False,
                message=f"Cannot connect to RabbitMQ: {e}",
                fix_suggestion="Ensure RabbitMQ is running: docker run -d -p 5672:5672 rabbitmq"
            )

    def _check_mock_messenger(self) -> ValidationResult:
        """
        Check mock messenger

        WHY: Extracted for consistency with other messenger checks
        PERFORMANCE: O(1) - no actual check needed

        Returns:
            ValidationResult for mock messenger check
        """
        return ValidationResult(
            check_name="Mock Messenger",
            passed=True,
            message="Using mock messenger (testing mode)",
            severity="warning"
        )
