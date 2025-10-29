from artemis_logger import get_logger
logger = get_logger('generator')
'\nConfiguration Report Generator Module\n\nWHY: Handles generation of configuration reports and summaries.\nSeparates presentation logic from business logic.\n\nRESPONSIBILITY: Generate human-readable configuration reports and exports\n\nPATTERNS:\n- Guard clauses for conditional output\n- Single Responsibility - only generates reports\n- Strategy pattern for different output formats\n'
from typing import Dict, Any, Callable
from agents.config.models import ConfigValidationResult
from agents.config.loader import ConfigLoader

class ConfigGenerator:
    """
    Configuration Report Generator

    WHY: Centralizes report generation logic. Makes it easy to add
    new report formats (JSON, YAML, HTML, etc.)

    RESPONSIBILITY: Generate configuration reports and summaries
    """

    @staticmethod
    def print_section_header(title: str, symbol: str='=') -> None:
        """
        Print section header for reports

        Args:
            title: Section title
            symbol: Symbol to use for border
        """
        
        logger.log(f'\n{title}:', 'INFO')

    @staticmethod
    def print_config_item(label: str, value: Any, indent: int=2) -> None:
        """
        Print configuration item with indentation

        Args:
            label: Item label
            value: Item value
            indent: Number of spaces to indent
        """
        spaces = ' ' * indent
        
        logger.log(f'{spaces}{label}: {value}', 'INFO')

    @staticmethod
    def print_provider_section(config: Dict[str, Any]) -> None:
        """
        Print LLM provider configuration section

        WHY: Extracted to reduce complexity of main report function.

        Args:
            config: Configuration dictionary
        """
        ConfigGenerator.print_section_header('LLM Provider Configuration')
        ConfigGenerator.print_config_item('Provider', config.get('ARTEMIS_LLM_PROVIDER', 'openai'))
        ConfigGenerator.print_config_item('Model', config.get('ARTEMIS_LLM_MODEL', 'default (provider-specific)'))
        ConfigGenerator.print_config_item('OpenAI API Key', ConfigLoader.mask_sensitive_value('OPENAI_API_KEY', config.get('OPENAI_API_KEY')))
        ConfigGenerator.print_config_item('Anthropic API Key', ConfigLoader.mask_sensitive_value('ANTHROPIC_API_KEY', config.get('ANTHROPIC_API_KEY')))

    @staticmethod
    def print_storage_section(config: Dict[str, Any]) -> None:
        """
        Print storage configuration section

        WHY: Extracted to reduce complexity of main report function.

        Args:
            config: Configuration dictionary
        """
        ConfigGenerator.print_section_header('Storage Configuration')
        ConfigGenerator.print_config_item('RAG Database', config.get('ARTEMIS_RAG_DB_PATH'))
        ConfigGenerator.print_config_item('Temp Directory', config.get('ARTEMIS_TEMP_DIR'))

    @staticmethod
    def print_pipeline_section(config: Dict[str, Any]) -> None:
        """
        Print pipeline configuration section

        WHY: Extracted to reduce complexity of main report function.

        Args:
            config: Configuration dictionary
        """
        ConfigGenerator.print_section_header('Pipeline Configuration')
        ConfigGenerator.print_config_item('Max Parallel Developers', config.get('ARTEMIS_MAX_PARALLEL_DEVELOPERS'))
        ConfigGenerator.print_config_item('Code Review Enabled', config.get('ARTEMIS_ENABLE_CODE_REVIEW'))
        ConfigGenerator.print_config_item('Auto-Approve Analysis', config.get('ARTEMIS_AUTO_APPROVE_PROJECT_ANALYSIS'))

    @staticmethod
    def print_security_section(config: Dict[str, Any]) -> None:
        """
        Print security and compliance section

        WHY: Extracted to reduce complexity of main report function.

        Args:
            config: Configuration dictionary
        """
        ConfigGenerator.print_section_header('Security & Compliance')
        ConfigGenerator.print_config_item('GDPR Enforcement', config.get('ARTEMIS_ENFORCE_GDPR'))
        ConfigGenerator.print_config_item('WCAG Enforcement', config.get('ARTEMIS_ENFORCE_WCAG'))

    @staticmethod
    def print_logging_section(config: Dict[str, Any]) -> None:
        """
        Print logging configuration section

        WHY: Extracted to reduce complexity of main report function.

        Args:
            config: Configuration dictionary
        """
        ConfigGenerator.print_section_header('Logging')
        ConfigGenerator.print_config_item('Verbose', config.get('ARTEMIS_VERBOSE'))
        ConfigGenerator.print_config_item('Log Level', config.get('ARTEMIS_LOG_LEVEL'))

    @staticmethod
    def print_cost_section(config: Dict[str, Any]) -> None:
        """
        Print cost controls section

        WHY: Extracted to reduce complexity of main report function.

        Args:
            config: Configuration dictionary
        """
        ConfigGenerator.print_section_header('Cost Controls')
        ConfigGenerator.print_config_item('Max Tokens/Request', config.get('ARTEMIS_MAX_TOKENS_PER_REQUEST'))
        cost_limit = config.get('ARTEMIS_COST_LIMIT_USD')
        cost_display = f'${cost_limit}/day' if cost_limit else 'Not set'
        ConfigGenerator.print_config_item('Cost Limit', cost_display)

    @staticmethod
    def print_validation_section(validation: ConfigValidationResult) -> None:
        """
        Print validation results section

        WHY: Extracted to reduce complexity and handle validation display.

        Args:
            validation: Validation result
        """
        ConfigGenerator.print_section_header('Validation Results')
        status = 'VALID' if validation.is_valid else 'INVALID'
        ConfigGenerator.print_config_item('Status', status)
        if validation.missing_keys:
            
            logger.log('\n  Missing Required Keys:', 'INFO')
            for key in validation.missing_keys:
                
                logger.log(f'     - {key}', 'INFO')
        if validation.invalid_keys:
            
            logger.log('\n  Invalid Values:', 'INFO')
            for key in validation.invalid_keys:
                
                logger.log(f'     - {key}', 'INFO')
        if validation.warnings:
            
            logger.log('\n  Warnings:', 'INFO')
            for warning in validation.warnings:
                
                logger.log(f'     - {warning}', 'INFO')

    @staticmethod
    def print_configuration_report(config: Dict[str, Any], validation: ConfigValidationResult) -> None:
        """
        Print comprehensive configuration report

        WHY: Main report generation function. Coordinates all sections.
        Uses dispatch table pattern for section generation.

        Args:
            config: Configuration dictionary
            validation: Validation result
        """
        
        logger.log('\n' + '=' * 80, 'INFO')
        
        logger.log('ARTEMIS CONFIGURATION REPORT', 'INFO')
        
        logger.log('=' * 80, 'INFO')
        section_generators: list[Callable[[Dict[str, Any]], None]] = [ConfigGenerator.print_provider_section, ConfigGenerator.print_storage_section, ConfigGenerator.print_pipeline_section, ConfigGenerator.print_security_section, ConfigGenerator.print_logging_section, ConfigGenerator.print_cost_section]
        for generator in section_generators:
            generator(config)
        ConfigGenerator.print_validation_section(validation)
        
        logger.log('\n' + '=' * 80, 'INFO')

    @staticmethod
    def export_to_json(config: Dict[str, Any], mask_sensitive: bool=True) -> str:
        """
        Export configuration as JSON string

        WHY: Provides JSON export for integration with other tools.

        Args:
            config: Configuration dictionary
            mask_sensitive: Mask sensitive values

        Returns:
            JSON string
        """
        import json
        export_config = ConfigLoader.export_config(config, mask_sensitive)
        return json.dumps(export_config, indent=2)

    @staticmethod
    def generate_summary(config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate concise configuration summary

        WHY: Provides quick overview without full details.

        Args:
            config: Configuration dictionary

        Returns:
            Summary dictionary
        """
        return {'provider': config.get('ARTEMIS_LLM_PROVIDER', 'openai'), 'model': config.get('ARTEMIS_LLM_MODEL', 'default'), 'code_review': config.get('ARTEMIS_ENABLE_CODE_REVIEW', True), 'max_developers': config.get('ARTEMIS_MAX_PARALLEL_DEVELOPERS', 3), 'has_api_key': bool(config.get('OPENAI_API_KEY') or config.get('ANTHROPIC_API_KEY'))}