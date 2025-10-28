#!/usr/bin/env python3
"""
Signature Validation Package

WHY: Modular signature and type validation system
RESPONSIBILITY: Export public API for signature validation
PATTERNS: Facade pattern for simplified imports

This package provides comprehensive validation for:
- Function signature mismatches
- Type hint validation
- Return type checking
- Dynamic call analysis (*args, **kwargs)
- Method resolution order (MRO) checking

USAGE:
    from signature_validation import EnhancedSignatureValidator, SignatureIssue

    validator = EnhancedSignatureValidator()
    issues = validator.validate_file("src/my_module.py")

    for issue in issues:
        print(f"{issue.file_path}:{issue.line_number} - {issue.message}")
"""

from signature_validation.models import SignatureIssue, FunctionInfo
from signature_validation.validator_core import EnhancedSignatureValidator
from signature_validation.type_validator import TypeChecker, TypeInferrer
from signature_validation.signature_extractor import SignatureExtractor
from signature_validation.parameter_validator import ParameterValidator, ReturnTypeValidator

__all__ = [
    'EnhancedSignatureValidator',
    'SignatureIssue',
    'FunctionInfo',
    'TypeChecker',
    'TypeInferrer',
    'SignatureExtractor',
    'ParameterValidator',
    'ReturnTypeValidator',
]

__version__ = '1.0.0'
