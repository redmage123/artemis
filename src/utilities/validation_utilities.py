from artemis_logger import get_logger
logger = get_logger('validation_utilities')
'\nModule: utilities/validation_utilities.py\n\nWHY: Provides reusable validation utilities with informative error context.\n     Before this module, 15+ files had duplicate validation code leading to\n     inconsistent error messages and maintenance burden.\n\nRESPONSIBILITY:\n- Validate required fields exist in dictionaries\n- Validate values are not None\n- Validate types match expected types\n- Validate numeric ranges\n- Validate non-empty strings/lists/dicts\n- Provide both exception-throwing and boolean-returning variants\n\nPATTERNS:\n- Utility/Helper Class: All static methods, no state needed\n- Guard Clause Pattern: Early returns for invalid states\n- Fail-Fast Pattern: Detect errors at validation boundary, not deep in call stack\n\nBenefits:\n- Consistent error messages across entire codebase\n- Automatic context injection (field names, data name, present fields)\n- Single point to enhance validation logic\n- Reduces 5+ lines of validation to 1 function call\n\nIntegration: Used by all pipeline stages before calling LLM, writing files, or\n             performing operations to ensure required data is present.\n'
from typing import Dict, Any, List, Union, Optional
from artemis_exceptions import PipelineValidationError as ValidationError

class Validator:
    """
    Reusable validation utilities with informative error context

    WHY: Consolidation provides consistent error messages and debugging context.
         Before this class, duplicate validation code was scattered across 15+ files.

    RESPONSIBILITY:
    - Validate required fields exist in dictionaries
    - Validate values are not None
    - Validate types match expected types
    - Validate numeric ranges
    - Validate non-empty collections
    """

    @staticmethod
    def validate_required_fields(data: Dict[str, Any], required_fields: List[str], data_name: str='data') -> None:
        """
        Validate all required fields exist in dictionary (raises on failure)

        WHY: Prevents cryptic KeyError exceptions downstream. Better to fail fast
             with clear message about which field is missing.

        Args:
            data: Dictionary to validate
            required_fields: List of required field names (e.g., ["prompt", "card_id"])
            data_name: Human-readable name for error message (e.g., "LLM request")

        Raises:
            ValidationError: If any required fields are missing, includes context with:
                           - data_name
                           - missing_fields list
                           - required_fields list
                           - present_fields list
        """
        missing_fields = [field for field in required_fields if field not in data]
        if not missing_fields:
            return
        raise ValidationError(f"Missing required fields in {data_name}: {', '.join(missing_fields)}", context={'data_name': data_name, 'missing_fields': missing_fields, 'required_fields': required_fields, 'present_fields': list(data.keys())})

    @staticmethod
    def validate_required_fields_bool(data: Dict[str, Any], required_fields: List[str], data_name: str='data', verbose: bool=True) -> bool:
        """
        Validate required fields, return bool instead of raising

        WHY: Useful for workflow handlers that return True/False
             instead of raising exceptions.

        Args:
            data: Dictionary to validate
            required_fields: List of required field names
            data_name: Name for logging
            verbose: Whether to print error messages

        Returns:
            True if valid, False if missing fields
        """
        missing_fields = [field for field in required_fields if field not in data]
        if not missing_fields:
            return True
        if verbose:
            
            logger.log(f"[Validation] Missing required fields in {data_name}: {', '.join(missing_fields)}", 'INFO')
        return False

    @staticmethod
    def validate_not_none(value: Any, field_name: str) -> None:
        """
        Validate that value is not None

        WHY: Guard clause pattern - early detection of None values
             before they cause AttributeError deep in call stack.

        Args:
            value: Value to check
            field_name: Field name for error message

        Raises:
            ValidationError: If value is None
        """
        if value is None:
            raise ValidationError(f'{field_name} cannot be None', context={'field_name': field_name})

    @staticmethod
    def validate_type(value: Any, expected_type: type, field_name: str) -> None:
        """
        Validate that value is of expected type

        WHY: Detects type mismatches early before they cause TypeErrors
             in operations that assume correct type.

        Args:
            value: Value to check
            expected_type: Expected type
            field_name: Field name for error message

        Raises:
            ValidationError: If value is wrong type
        """
        if isinstance(value, expected_type):
            return
        raise ValidationError(f'{field_name} must be {expected_type.__name__}, got {type(value).__name__}', context={'field_name': field_name, 'expected_type': expected_type.__name__, 'actual_type': type(value).__name__})

    @staticmethod
    def validate_in_range(value: Union[int, float], min_value: Optional[Union[int, float]]=None, max_value: Optional[Union[int, float]]=None, field_name: str='value') -> None:
        """
        Validate that numeric value is in range

        WHY: Detects out-of-range values early before they cause issues
             in calculations or API calls with range constraints.

        Args:
            value: Value to check
            min_value: Minimum allowed value (inclusive)
            max_value: Maximum allowed value (inclusive)
            field_name: Field name for error message

        Raises:
            ValidationError: If value is out of range
        """
        if min_value is not None and value < min_value:
            raise ValidationError(f'{field_name} must be >= {min_value}, got {value}', context={'field_name': field_name, 'value': value, 'min': min_value})
        if max_value is not None and value > max_value:
            raise ValidationError(f'{field_name} must be <= {max_value}, got {value}', context={'field_name': field_name, 'value': value, 'max': max_value})

    @staticmethod
    def validate_non_empty(value: Union[str, List, Dict], field_name: str) -> None:
        """
        Validate that string/list/dict is not empty

        WHY: Detects empty collections early before they cause issues
             in operations that assume non-empty input.

        Args:
            value: Value to check
            field_name: Field name for error message

        Raises:
            ValidationError: If value is empty
        """
        if value:
            return
        raise ValidationError(f'{field_name} cannot be empty', context={'field_name': field_name, 'type': type(value).__name__})

def validate_required(data: Dict, fields: List[str], name: str='data') -> None:
    """
    Convenience function for validating required fields

    WHY: Shorter function name for common validation pattern.

    Args:
        data: Dictionary to validate
        fields: List of required field names
        name: Name for error messages
    """
    Validator.validate_required_fields(data, fields, name)