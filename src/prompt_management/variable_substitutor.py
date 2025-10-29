from artemis_logger import get_logger
logger = get_logger('variable_substitutor')
'\nWHY: Handle variable substitution in prompt templates.\nRESPONSIBILITY: Replace template placeholders with actual values.\nPATTERNS: Strategy pattern for substitution methods, guard clauses.\n\nThis module provides robust variable substitution with validation\nand error handling for missing or invalid variables.\n'
from typing import Dict, List, Any, Optional

class VariableSubstitutor:
    """
    WHY: Perform template variable substitution.
    RESPONSIBILITY: Replace {placeholders} with actual values safely.
    PATTERNS: Guard clauses, explicit error handling.
    """

    def __init__(self, strict: bool=False, verbose: bool=False):
        """
        WHY: Initialize substitutor with configuration.
        RESPONSIBILITY: Set up substitution behavior.
        PATTERNS: Configuration injection.

        Args:
            strict: Raise error on missing variables
            verbose: Enable verbose logging
        """
        self.strict = strict
        self.verbose = verbose

    def substitute(self, template: str, variables: Dict[str, Any]) -> str:
        """
        WHY: Replace all placeholders in template with variable values.
        RESPONSIBILITY: Perform substitution with error handling.
        PATTERNS: Guard clause for empty template.

        Args:
            template: Template string with {placeholders}
            variables: Dictionary of variable values

        Returns:
            Template with substituted values

        Raises:
            ValueError: If strict mode and missing variables
        """
        if not template:
            return ''
        result = template
        if not variables:
            if self.strict and self._has_placeholders(template):
                raise ValueError('Template has placeholders but no variables provided')
            return result
        for key, value in variables.items():
            placeholder = '{' + key + '}'
            result = result.replace(placeholder, str(value))
        if self.strict:
            remaining = self._find_placeholders(result)
            if remaining:
                raise ValueError(f'Missing variables for placeholders: {remaining}')
        if self.verbose and self._has_placeholders(result):
            remaining = self._find_placeholders(result)
            
            logger.log(f'[VariableSubstitutor] Warning: Unsubstituted placeholders: {remaining}', 'INFO')
        return result

    def substitute_multiple(self, templates: Dict[str, str], variables: Dict[str, Any]) -> Dict[str, str]:
        """
        WHY: Substitute variables in multiple templates efficiently.
        RESPONSIBILITY: Batch substitution with consistent variable set.
        PATTERNS: Guard clause for empty inputs.

        Args:
            templates: Dictionary of template_name -> template_string
            variables: Variables to substitute

        Returns:
            Dictionary of template_name -> substituted_string
        """
        if not templates:
            return {}
        result = {}
        for name, template in templates.items():
            result[name] = self.substitute(template, variables)
        return result

    def extract_placeholders(self, template: str) -> List[str]:
        """
        WHY: Extract all placeholder names from template.
        RESPONSIBILITY: Parse template for {placeholder} patterns.
        PATTERNS: Guard clause for empty template.

        Args:
            template: Template string

        Returns:
            List of placeholder names (without braces)
        """
        if not template:
            return []
        return self._find_placeholders(template)

    def validate_variables(self, template: str, variables: Dict[str, Any]) -> Dict[str, Any]:
        """
        WHY: Validate that all required variables are provided.
        RESPONSIBILITY: Check variables against template requirements.
        PATTERNS: Guard clause pattern, explicit validation result.

        Args:
            template: Template string
            variables: Variables to validate

        Returns:
            Validation result with 'valid', 'missing', 'extra' keys
        """
        placeholders = self.extract_placeholders(template)
        if not placeholders:
            return {'valid': True, 'missing': [], 'extra': list(variables.keys()) if variables else []}
        provided = set(variables.keys()) if variables else set()
        required = set(placeholders)
        missing = required - provided
        extra = provided - required
        return {'valid': len(missing) == 0, 'missing': list(missing), 'extra': list(extra)}

    def _has_placeholders(self, text: str) -> bool:
        """
        WHY: Check if text contains any placeholders.
        RESPONSIBILITY: Quick placeholder detection.
        PATTERNS: Simple boolean check.

        Args:
            text: Text to check

        Returns:
            True if placeholders found
        """
        return '{' in text and '}' in text

    def _find_placeholders(self, text: str) -> List[str]:
        """
        WHY: Find all placeholder names in text.
        RESPONSIBILITY: Parse and extract placeholder names.
        PATTERNS: Guard clause for no placeholders.

        Args:
            text: Text to parse

        Returns:
            List of placeholder names
        """
        if not self._has_placeholders(text):
            return []
        placeholders = []
        i = 0
        while i < len(text):
            start = text.find('{', i)
            if start == -1:
                break
            end = text.find('}', start)
            if end == -1:
                break
            name = text[start + 1:end]
            if name:
                placeholders.append(name)
            i = end + 1
        return placeholders