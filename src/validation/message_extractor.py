#!/usr/bin/env python3
"""
WHY: Extract error messages from validation results with varying structures
RESPONSIBILITY: Normalize validation result structures into consistent error message lists
PATTERNS: Strategy (multiple extractors for different structures), Dispatch Table

Message extractor handles different validation result formats:
- errors: [] list
- error: single error string
- message: single message string
- validation_errors: [] list
"""

from typing import Dict, List, Callable


class ValidationMessageExtractor:
    """
    Extracts error messages from validation results

    WHY: Validation results can have different structures (errors list, message field, etc.)
         This normalizes them into a consistent list.
    """

    def __init__(self):
        """Initialize message extractor"""
        # Strategy pattern: Different result structures (dictionary mapping)
        self._extractors: Dict[str, Callable[[Dict], List[str]]] = {
            'errors': lambda r: r.get('errors', []),
            'error': lambda r: [r.get('error')] if r.get('error') else [],
            'message': lambda r: [r.get('message')] if r.get('message') else [],
            'validation_errors': lambda r: r.get('validation_errors', []),
        }

    def extract(self, validation_results: Dict) -> List[str]:
        """
        Extract error messages from validation results

        Args:
            validation_results: Results from validation pipeline

        Returns:
            List of error messages
        """
        messages = []

        # Apply all extractors
        for key, extractor in self._extractors.items():
            extracted = extractor(validation_results)
            if extracted:
                messages.extend(extracted)

        # Filter out None values (list comprehension for performance)
        return [msg for msg in messages if msg]
