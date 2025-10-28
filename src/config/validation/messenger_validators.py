#!/usr/bin/env python3
"""
Messenger Validators - Messaging backend validation

WHY: Validates messenger backend availability before pipeline runs to prevent
     runtime failures when agents try to communicate.

RESPONSIBILITY: Validate messenger backend configuration and connectivity.

PATTERNS: Strategy pattern for messenger-specific validation, guard clauses.
"""

import os
from pathlib import Path
from typing import Callable, Dict
from config.validation.models import ValidationResult


class MessengerValidator:
    """
    Validates messenger backend availability.

    WHY: Ensures messaging system is available before pipeline runs.
    RESPONSIBILITY: Orchestrate messenger-specific validators.
    PATTERNS: Strategy pattern via dictionary mapping to validators.
    """

    # Strategy pattern: Map messenger types to validator functions
    # WHY: Makes it easy to add new messenger types without modifying code
    MESSENGER_VALIDATORS: Dict[str, Callable[[], ValidationResult]] = {}

    @classmethod
    def register_validator(cls, messenger_type: str, validator_func: Callable[[], ValidationResult]) -> None:
        """
        Register a messenger validator.

        WHY: Open/Closed principle - add new validators without modifying class.
        PERFORMANCE: O(1) dictionary insertion.

        Args:
            messenger_type: Type of messenger (file, rabbitmq, etc.)
            validator_func: Validator function to register
        """
        cls.MESSENGER_VALIDATORS[messenger_type] = validator_func

    @staticmethod
    def validate() -> ValidationResult:
        """
        Validate messenger backend based on configured type.

        WHY: Dispatches to appropriate validator based on configuration.
        PERFORMANCE: O(1) dictionary lookup.

        Returns:
            ValidationResult for messenger access
        """
        messenger_type = os.getenv("ARTEMIS_MESSENGER_TYPE", "file")

        # Guard clause: Unknown messenger type
        validator_func = MessengerValidator.MESSENGER_VALIDATORS.get(messenger_type)
        if not validator_func:
            return ValidationResult(
                check_name="Messenger",
                passed=False,
                message=f"Unknown messenger type: {messenger_type}",
                fix_suggestion="Set ARTEMIS_MESSENGER_TYPE to 'file', 'rabbitmq', or 'mock'"
            )

        # Delegate to specific validator
        return validator_func()


class FileMessengerValidator:
    """
    Validates file-based messenger.

    WHY: File-based messenger is the default, must be accessible.
    RESPONSIBILITY: Validate file messenger directory access only.
    """

    @staticmethod
    def validate() -> ValidationResult:
        """
        Validate file-based messenger directory.

        WHY: Ensures message directory is writable before pipeline runs.
        PERFORMANCE: O(1) directory creation check.

        Returns:
            ValidationResult for file messenger access
        """
        message_dir = os.getenv("ARTEMIS_MESSAGE_DIR", "/tmp/agent_messages")

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


class RabbitMQMessengerValidator:
    """
    Validates RabbitMQ messenger.

    WHY: RabbitMQ may be used for production deployments.
    RESPONSIBILITY: Validate RabbitMQ connectivity only.
    """

    @staticmethod
    def validate() -> ValidationResult:
        """
        Validate RabbitMQ messenger connectivity.

        WHY: Ensures RabbitMQ is running before pipeline starts.
        PERFORMANCE: O(n) network connection with 1 retry (short timeout).

        Returns:
            ValidationResult for RabbitMQ access
        """
        try:
            import pika
            rabbitmq_url = os.getenv("ARTEMIS_RABBITMQ_URL", "amqp://localhost")

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


class MockMessengerValidator:
    """
    Validates mock messenger.

    WHY: Mock messenger is used for testing.
    RESPONSIBILITY: Always pass validation for mock messenger.
    """

    @staticmethod
    def validate() -> ValidationResult:
        """
        Validate mock messenger (always passes).

        WHY: Mock messenger requires no external dependencies.
        PERFORMANCE: O(1) - no actual check needed.

        Returns:
            ValidationResult indicating mock messenger is ready
        """
        return ValidationResult(
            check_name="Mock Messenger",
            passed=True,
            message="Using mock messenger (testing mode)",
            severity="warning"
        )


# Register validators using strategy pattern
# WHY: Decouples validator registration from MessengerValidator class
MessengerValidator.register_validator("file", FileMessengerValidator.validate)
MessengerValidator.register_validator("rabbitmq", RabbitMQMessengerValidator.validate)
MessengerValidator.register_validator("mock", MockMessengerValidator.validate)
