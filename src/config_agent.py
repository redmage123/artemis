from artemis_logger import get_logger
logger = get_logger('config_agent')
'\nConfiguration Agent - Backward Compatibility Wrapper\n\nWHY: Maintains backward compatibility with existing code while using\nthe new modular agents/config package structure.\n\nRESPONSIBILITY: Re-export all public APIs from agents.config package\n\nPATTERNS:\n- Facade pattern: Provides same interface as before\n- Deprecation wrapper: Allows gradual migration\n\nMIGRATION: Code using this module will continue to work unchanged.\nNew code should import from agents.config directly.\n\nExample:\n    Old: from config_agent import ConfigurationAgent, get_config\n    New: from agents.config import ConfigurationAgent, get_config\n'
from agents.config import ConfigurationAgent, get_config, reset_config, ConfigValidationResult, ConfigSchema, BOOL_STRING_MAP, PROVIDER_KEY_MAP, ConfigLoader, ConfigValidator, ConfigGenerator

def _run_validate(config: ConfigurationAgent) -> None:
    """
    Run validation action (CLI helper)

    WHY: Maintains CLI compatibility with original implementation.
    """
    result = config.validate_configuration()
    if not result.is_valid:
        
        logger.log('\nConfiguration is INVALID', 'INFO')
        exit(1)
    
    logger.log('\nConfiguration is VALID', 'INFO')
    exit(0)

def _run_export(config: ConfigurationAgent) -> None:
    """
    Run export action (CLI helper)

    WHY: Maintains CLI compatibility with original implementation.
    """
    
    logger.log(config.export_to_json(), 'INFO')

def _run_report(config: ConfigurationAgent) -> None:
    """
    Run report action (CLI helper)

    WHY: Maintains CLI compatibility with original implementation.
    """
    config.print_configuration_report()
if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Artemis Configuration Agent')
    parser.add_argument('--validate', action='store_true', help='Validate configuration')
    parser.add_argument('--report', action='store_true', help='Print configuration report')
    parser.add_argument('--export', action='store_true', help='Export configuration as JSON')
    args = parser.parse_args()
    config = ConfigurationAgent(verbose=True)
    if args.validate:
        _run_validate(config)
    if args.export:
        _run_export(config)
        exit(0)
    _run_report(config)