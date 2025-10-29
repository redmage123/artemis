from artemis_logger import get_logger
logger = get_logger('config_validation')
'\nConfig Validation - Configuration validation and display utilities\n\nWHAT:\nConfiguration validation utilities for checking required keys,\ndisplaying validation errors with helpful hints, and determining\nHydra config paths.\n\nWHY:\nSeparates config validation from entry points, enabling:\n- Focused testing of validation logic\n- Reusable validation utilities\n- Clear error messages with actionable hints\n- Clean separation of concerns\n\nRESPONSIBILITY:\n- Validate configuration and exit if invalid\n- Display validation errors with helpful hints\n- Provide hints for common configuration issues (API keys, etc.)\n- Determine Hydra config directory path\n\nPATTERNS:\n- Guard Clause: Early returns for valid config\n- Template Method: Consistent error display format\n- Facade Pattern: Simplifies validation logic\n\nEXTRACTED FROM: artemis_orchestrator.py lines 1287-1394\n'
import sys
from typing import Any
from pathlib import Path

def display_validation_errors(config: Any, validation: Any) -> None:
    """
    Display configuration validation errors with helpful hints.

    WHAT:
    Formats and displays configuration validation errors with
    descriptions and helpful hints for common issues.

    WHY:
    Makes configuration errors actionable by providing:
    - Clear error messages
    - Descriptions of missing/invalid keys
    - Hints for setting API keys
    - Instructions for next steps

    Args:
        config: Configuration object with schema
        validation: Validation result object

    PATTERNS:
        - Template Method: Consistent error display format
        - Guard Clause: Handles optional error types
    """
    
    logger.log('\n' + '=' * 80, 'INFO')
    
    logger.log('❌ CONFIGURATION ERROR', 'INFO')
    
    logger.log('=' * 80, 'INFO')
    
    logger.log('\nThe pipeline cannot run due to invalid configuration.\n', 'INFO')
    if validation.missing_keys:
        
        logger.log('Missing Required Keys:', 'INFO')
        [
        logger.log(f"  ❌ {key}\n     Description: {config.CONFIG_SCHEMA.get(key, {}).get('description', 'N/A')}", 'INFO') for key in validation.missing_keys]
        if 'OPENAI_API_KEY' in validation.missing_keys:
            
            logger.log(f'\n💡 Set your OpenAI API key:', 'INFO')
            
            logger.log(f"   export OPENAI_API_KEY='your-key-here'", 'INFO')
        if 'ANTHROPIC_API_KEY' in validation.missing_keys:
            
            logger.log(f'\n💡 Set your Anthropic API key:', 'INFO')
            
            logger.log(f"   export ANTHROPIC_API_KEY='your-key-here'", 'INFO')
    if validation.invalid_keys:
        
        logger.log('\nInvalid Configuration Values:', 'INFO')
        [
        logger.log(f'  ❌ {key}', 'INFO') for key in validation.invalid_keys]
    
    logger.log('\n' + '=' * 80, 'INFO')
    
    logger.log('\n💡 Run with --config-report to see full configuration', 'INFO')
    
    logger.log('💡 Run with --skip-validation to bypass (NOT RECOMMENDED)\n', 'INFO')

def validate_config_or_exit(config: Any, skip_validation: bool) -> None:
    """
    Validate configuration and exit if invalid.

    WHAT:
    Validates configuration against schema and exits with error
    message if validation fails (unless skip_validation is True).

    WHY:
    Ensures pipeline doesn't run with invalid configuration,
    preventing cryptic errors later. Provides immediate feedback
    about configuration issues.

    Args:
        config: Configuration object to validate
        skip_validation: If True, skip validation

    PATTERNS:
        - Guard Clause: Early returns for skipped/valid config
        - Fail Fast: Exits immediately on invalid config
    """
    if skip_validation:
        return
    validation = config.validate_configuration(require_llm_key=True)
    if validation.is_valid:
        return
    display_validation_errors(config, validation)
    sys.exit(1)

def get_config_path() -> str:
    """
    Get absolute path to Hydra config directory.

    WHAT:
    Determines the absolute path to the Hydra configuration
    directory relative to this file's location.

    WHY:
    This allows the orchestrator to be run from any directory,
    not just from .agents/agile. Hydra requires absolute or
    relative-to-module paths for config directories.

    Returns:
        Absolute path to the conf directory

    PATTERNS:
        - Path Resolution: Uses __file__ for relative path
    """
    script_dir = Path(__file__).parent.parent
    return str(script_dir / 'conf')