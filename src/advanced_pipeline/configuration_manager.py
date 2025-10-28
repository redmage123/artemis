#!/usr/bin/env python3
"""
Module: configuration_manager.py

WHY this module exists:
    Manages advanced pipeline configuration with runtime updates, validation,
    history tracking, and rollback capability.

RESPONSIBILITY:
    - Load and save configuration
    - Validate configuration changes
    - Track configuration history
    - Emit configuration change events
    - Enable configuration rollback

PATTERNS:
    - Singleton Pattern: Centralized configuration management
    - Memento Pattern: Configuration history for rollback
    - Observer Pattern: Event emission for configuration changes
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import copy

from pipeline_observer import PipelineObservable, PipelineEvent, EventType
from artemis_exceptions import PipelineException, wrap_exception
from artemis_services import PipelineLogger
from advanced_pipeline.pipeline_config import AdvancedPipelineConfig


class ConfigurationManager:
    """
    Manages advanced pipeline configuration.

    WHY: Centralized configuration management enables:
        - Runtime configuration updates
        - Configuration persistence
        - Validation before applying changes
        - Configuration history for rollback
        - A/B testing different configurations

    Design pattern: Singleton + Memento (for configuration history)

    Responsibilities:
        - Load/save configuration
        - Validate configuration changes
        - Track configuration history
        - Emit configuration change events
    """

    def __init__(
        self,
        config: Optional[AdvancedPipelineConfig] = None,
        observable: Optional[PipelineObservable] = None
    ):
        """
        Initialize configuration manager.

        Args:
            config: Initial configuration (creates default if None)
            observable: Pipeline observable for event emission
        """
        self.config = config or AdvancedPipelineConfig()
        self.observable = observable
        self.logger = PipelineLogger(verbose=True)

        # Configuration history for rollback
        self._config_history: List[AdvancedPipelineConfig] = [
            copy.deepcopy(self.config)
        ]

    @wrap_exception(PipelineException, "Configuration update failed")
    def update_config(self, **kwargs) -> None:
        """
        Update configuration with new values.

        WHAT: Updates configuration fields and validates new configuration.
        Stores old configuration in history for potential rollback.

        WHY: Enables runtime configuration changes while maintaining
        configuration validity and rollback capability.

        Args:
            **kwargs: Configuration fields to update

        Raises:
            PipelineException: If updated configuration invalid

        Usage:
            config_mgr.update_config(
                enable_two_pass=True,
                confidence_threshold=0.8
            )
        """
        # Store current configuration in history
        self._config_history.append(copy.deepcopy(self.config))

        # Create new configuration with updates
        config_dict = {
            field.name: getattr(self.config, field.name)
            for field in self.config.__dataclass_fields__.values()
        }
        config_dict.update(kwargs)

        # Create and validate new configuration
        try:
            new_config = AdvancedPipelineConfig(**config_dict)
        except Exception as e:
            # Rollback on validation failure
            self._config_history.pop()
            raise PipelineException(
                f"Invalid configuration update: {e}",
                context={"updates": kwargs}
            )

        # Apply new configuration
        old_config = self.config
        self.config = new_config

        # Emit configuration change event
        self._emit_config_change_event(old_config, new_config, kwargs)

        self.logger.log(f"Configuration updated: {kwargs}", "INFO")

    def rollback_config(self) -> bool:
        """
        Rollback to previous configuration.

        WHY: Allows reverting bad configuration changes without restart.
        Useful for A/B testing rollback or recovering from misconfigurations.

        Returns:
            True if rollback successful, False if no history
        """
        # Guard clause: need at least 2 configs (current + previous)
        if len(self._config_history) < 2:
            self.logger.log("No configuration history to rollback", "WARNING")
            return False

        # Remove current config
        self._config_history.pop()

        # Restore previous config
        self.config = copy.deepcopy(self._config_history[-1])

        self.logger.log("Configuration rolled back to previous state", "INFO")
        return True

    def get_config_dict(self) -> Dict[str, Any]:
        """
        Get configuration as dictionary for serialization.

        WHY: Enables configuration persistence, logging, and transmission.

        Returns:
            Dict with all configuration fields
        """
        return {
            field.name: getattr(self.config, field.name)
            for field in self.config.__dataclass_fields__.values()
        }

    def _emit_config_change_event(
        self,
        old_config: AdvancedPipelineConfig,
        new_config: AdvancedPipelineConfig,
        changes: Dict[str, Any]
    ) -> None:
        """
        Emit configuration change event.

        WHY: Allows monitoring of configuration changes for audit and debugging.

        Args:
            old_config: Configuration before change
            new_config: Configuration after change
            changes: Dict of changed fields
        """
        # Guard clause: check if observable configured
        if not self.observable:
            return

        event_data = {
            "event_type": "configuration_changed",
            "changes": changes,
            "timestamp": datetime.now().isoformat()
        }

        event = PipelineEvent(
            event_type=EventType.STAGE_PROGRESS,
            stage_name="ConfigurationManager",
            data=event_data
        )

        self.observable.notify(event)
