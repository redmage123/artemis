from artemis_logger import get_logger
logger = get_logger('loader')
'\nConfiguration Loader Module\n\nWHY: Handles loading configuration from environment variables and files.\nSeparates loading logic from validation and generation.\n\nRESPONSIBILITY: Load configuration from various sources (env, .env files, etc.)\n\nPATTERNS:\n- Strategy pattern for different loading sources\n- Guard clauses for early returns\n- Type conversion using dispatch tables\n'
import os
from typing import Dict, Any, Optional
try:
    from dotenv import load_dotenv
    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False
from agents.config.models import ConfigSchema, BOOL_STRING_MAP

class ConfigLoader:
    """
    Configuration Loader

    WHY: Centralizes configuration loading logic from multiple sources.
    Makes it easy to add new configuration sources (files, cloud, etc.)

    RESPONSIBILITY: Load and parse configuration from environment
    """

    @staticmethod
    def load_dotenv(override: bool=True) -> bool:
        """
        Load .env file if dotenv is available

        Args:
            override: Override existing environment variables

        Returns:
            True if loaded successfully, False otherwise
        """
        if not DOTENV_AVAILABLE:
            return False
        try:
            load_dotenv(override=override)
            return True
        except Exception:
            return False

    @staticmethod
    def convert_boolean_string(value: Any) -> Any:
        """
        Convert boolean string to actual boolean

        WHY: Centralized boolean conversion using strategy pattern.
        Avoids if/elif chains.

        Args:
            value: Value to convert

        Returns:
            Boolean if string matches map, original value otherwise
        """
        if not isinstance(value, str):
            return value
        return BOOL_STRING_MAP.get(value, value)

    @staticmethod
    def load_from_environment(schema: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Load configuration from environment variables

        WHY: Primary configuration source. Uses schema to determine
        which keys to load and apply defaults.

        Args:
            schema: Configuration schema

        Returns:
            Configuration dictionary
        """
        config: Dict[str, Any] = {}
        for key, key_schema in schema.items():
            value = os.getenv(key, key_schema.get('default'))
            value = ConfigLoader.convert_boolean_string(value)
            config[key] = value
        return config

    @staticmethod
    def load_configuration(load_env_file: bool=True, verbose: bool=False) -> Dict[str, Any]:
        """
        Load complete configuration

        WHY: Main entry point for configuration loading.
        Coordinates loading from multiple sources.

        Args:
            load_env_file: Load .env file if available
            verbose: Enable verbose output

        Returns:
            Complete configuration dictionary
        """
        if load_env_file:
            loaded = ConfigLoader.load_dotenv(override=True)
            if verbose and loaded:
                
                logger.log('Loaded configuration from .env file', 'INFO')
        schema = ConfigSchema.get_schema()
        config = ConfigLoader.load_from_environment(schema)
        if verbose:
            
            logger.log('Configuration loaded from environment', 'INFO')
        return config

    @staticmethod
    def get_value(config: Dict[str, Any], key: str, default: Any=None) -> Any:
        """
        Get configuration value with optional default

        Args:
            config: Configuration dictionary
            key: Configuration key
            default: Default value if key not found

        Returns:
            Configuration value or default
        """
        return config.get(key, default)

    @staticmethod
    def mask_sensitive_value(key: str, value: Any) -> str:
        """
        Mask sensitive configuration value for logging

        WHY: Prevents sensitive data leakage in logs.
        Uses schema to determine if value should be masked.

        Args:
            key: Configuration key
            value: Configuration value

        Returns:
            Masked value string
        """
        if not value:
            return 'NOT_SET'
        if not ConfigSchema.is_sensitive(key):
            return str(value)
        value_str = str(value)
        if len(value_str) > 10:
            return f'{value_str[:6]}...{value_str[-4:]}'
        return '***'

    @staticmethod
    def export_config(config: Dict[str, Any], mask_sensitive: bool=True) -> Dict[str, Any]:
        """
        Export configuration with optional masking

        WHY: Provides safe configuration export for logging/debugging.
        Guards against exposing sensitive data.

        Args:
            config: Configuration dictionary
            mask_sensitive: Mask sensitive values

        Returns:
            Exported configuration dictionary
        """
        if not mask_sensitive:
            return config.copy()
        return {key: ConfigLoader.mask_sensitive_value(key, value) for key, value in config.items()}

    @staticmethod
    def set_test_defaults(config: Dict[str, Any]) -> None:
        """
        Set safe defaults for testing

        WHY: Provides predictable test configuration without API calls.

        Args:
            config: Configuration dictionary to modify
        """
        config['ARTEMIS_LLM_PROVIDER'] = 'mock'
        config['OPENAI_API_KEY'] = 'sk-test-key'
        config['ARTEMIS_RAG_DB_PATH'] = 'db_test'
        config['ARTEMIS_ENABLE_CODE_REVIEW'] = False