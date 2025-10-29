from artemis_logger import get_logger
logger = get_logger('agent_core')
'\nConfiguration Agent Core Module\n\nWHY: Main configuration agent that coordinates loading, validation, and reporting.\nProvides high-level API for configuration management.\n\nRESPONSIBILITY: Coordinate configuration operations and provide unified interface\n\nPATTERNS:\n- Facade pattern - simplifies interaction with loader, validator, generator\n- Singleton pattern - single configuration instance\n- Guard clauses for validation\n'
from typing import Dict, Any, Optional
from debug_mixin import DebugMixin
from agents.config.models import ConfigValidationResult
from agents.config.loader import ConfigLoader
from agents.config.validator import ConfigValidator
from agents.config.generator import ConfigGenerator

class ConfigurationAgent(DebugMixin):
    """
    Configuration Agent - Main Configuration Manager

    WHY: Provides unified interface for all configuration operations.
    Coordinates loader, validator, and generator components.

    RESPONSIBILITY:
    1. Initialize and manage configuration lifecycle
    2. Coordinate loading, validation, and reporting
    3. Provide simple API for configuration access
    4. Maintain configuration state

    PATTERNS:
    - Facade pattern: Simplifies complex subsystem interactions
    - Composition over inheritance: Uses loader, validator, generator
    """

    def __init__(self, verbose: bool=True):
        """
        Initialize Configuration Agent

        Args:
            verbose: Enable verbose logging
        """
        DebugMixin.__init__(self, component_name='config')
        self.verbose = verbose
        self.config: Dict[str, Any] = {}
        self.load_configuration()
        self.debug_log('ConfigurationAgent initialized', verbose=verbose)

    def load_configuration(self) -> None:
        """
        Load all configuration from environment

        WHY: Entry point for configuration loading.
        Delegates to ConfigLoader for actual loading.
        """
        self.debug_trace('load_configuration', verbose=self.verbose)
        self.config = ConfigLoader.load_configuration(load_env_file=True, verbose=self.verbose)
        if self.verbose:
            
            logger.log('Configuration loaded from environment', 'INFO')

    def validate_configuration(self, require_llm_key: bool=True) -> ConfigValidationResult:
        """
        Validate current configuration

        WHY: Entry point for validation. Delegates to ConfigValidator.

        Args:
            require_llm_key: Require LLM API key based on provider

        Returns:
            ConfigValidationResult with validation status
        """
        self.debug_trace('validate_configuration', require_llm_key=require_llm_key)
        result = ConfigValidator.validate_configuration(self.config, require_llm_key=require_llm_key)
        self.debug_if_enabled('validation_results', 'Configuration validation completed', is_valid=result.is_valid, missing=len(result.missing_keys), invalid=len(result.invalid_keys), warnings=len(result.warnings))
        return result

    def get(self, key: str, default: Any=None) -> Any:
        """
        Get configuration value

        Args:
            key: Configuration key
            default: Default value if key not found

        Returns:
            Configuration value
        """
        return ConfigLoader.get_value(self.config, key, default)

    def get_masked(self, key: str) -> str:
        """
        Get configuration value with sensitive data masked

        WHY: Safely retrieve configuration for logging without
        exposing sensitive data.

        Args:
            key: Configuration key

        Returns:
            Masked value (e.g., "sk-XYZ...ABC")
        """
        value = self.config.get(key)
        return ConfigLoader.mask_sensitive_value(key, value)

    def print_configuration_report(self) -> None:
        """
        Print comprehensive configuration report

        WHY: Entry point for report generation.
        Delegates to ConfigGenerator.
        """
        validation = self.validate_configuration(require_llm_key=False)
        ConfigGenerator.print_configuration_report(self.config, validation)

    def export_to_dict(self, mask_sensitive: bool=True) -> Dict[str, Any]:
        """
        Export configuration as dictionary

        WHY: Provides configuration export for logging and debugging.
        Delegates to ConfigLoader for export logic.

        Args:
            mask_sensitive: Mask sensitive values

        Returns:
            Configuration dictionary
        """
        return ConfigLoader.export_config(self.config, mask_sensitive)

    def export_to_json(self, mask_sensitive: bool=True) -> str:
        """
        Export configuration as JSON string

        WHY: Provides JSON export for integration and debugging.

        Args:
            mask_sensitive: Mask sensitive values

        Returns:
            JSON string
        """
        return ConfigGenerator.export_to_json(self.config, mask_sensitive)

    def set_defaults_for_testing(self) -> None:
        """
        Set safe defaults for testing

        WHY: Provides predictable test configuration without API calls.
        """
        ConfigLoader.set_test_defaults(self.config)
        if self.verbose:
            
            logger.log('Test mode enabled - using mock LLM provider', 'INFO')

    def reload_configuration(self) -> None:
        """
        Reload configuration from environment

        WHY: Allows configuration refresh without recreating agent.
        Useful for testing and dynamic configuration updates.
        """
        self.debug_trace('reload_configuration', verbose=self.verbose)
        self.load_configuration()
_config_instance: Optional[ConfigurationAgent] = None

def get_config(verbose: bool=True) -> ConfigurationAgent:
    """
    Get singleton configuration agent instance

    WHY: Provides single source of truth for configuration.
    Avoids multiple loads and inconsistent state.

    Args:
        verbose: Enable verbose logging

    Returns:
        ConfigurationAgent instance
    """
    global _config_instance
    if _config_instance is not None:
        return _config_instance
    _config_instance = ConfigurationAgent(verbose=verbose)
    return _config_instance

def reset_config() -> None:
    """
    Reset singleton configuration instance

    WHY: Useful for testing to ensure clean state.
    """
    global _config_instance
    _config_instance = None