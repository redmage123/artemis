#!/usr/bin/env python3
"""
Module: template_selector.py

WHY: Determines which notebook template/type to use based on card content.
     Separates type inference logic from cell generation.

RESPONSIBILITY:
- Analyze card title and description to infer notebook type
- Map explicit notebook types from card metadata
- Apply keyword-based heuristics for type detection
- Provide default fallback type

PATTERNS:
- Strategy Pattern: Different inference strategies for type detection
- Dispatch Table: O(1) lookup for type mapping
- Guard Clauses: Early returns for explicit type specifications
"""

from typing import Dict, Any, List, Optional


class TemplateSelector:
    """
    Select appropriate notebook template based on card content

    WHY: Centralizes notebook type determination logic
    RESPONSIBILITY: Infer or extract notebook type from card data
    """

    # Dispatch table for O(1) type mapping
    NOTEBOOK_TYPE_MAPPING: Dict[str, str] = {
        'data_analysis': 'data_analysis',
        'machine_learning': 'machine_learning',
        'ml': 'machine_learning',
        'api_demo': 'api_demo',
        'documentation': 'documentation',
        'test_visualization': 'test_visualization',
        'general': 'general'
    }

    # Keyword sets for type inference
    ML_KEYWORDS: List[str] = [
        'ml', 'machine learning', 'model', 'train', 'predict',
        'classification', 'regression', 'neural network', 'deep learning'
    ]

    DATA_KEYWORDS: List[str] = [
        'data analysis', 'analyze data', 'visualization', 'pandas',
        'statistics', 'explore data', 'dataframe'
    ]

    API_KEYWORDS: List[str] = [
        'api', 'endpoint', 'demo', 'example', 'rest',
        'request', 'response', 'http'
    ]

    TEST_KEYWORDS: List[str] = [
        'test', 'testing', 'results', 'coverage',
        'unit test', 'integration test', 'test report'
    ]

    DOC_KEYWORDS: List[str] = [
        'documentation', 'docs', 'guide', 'tutorial',
        'how to', 'usage', 'examples'
    ]

    def determine_notebook_type(
        self,
        card: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Determine appropriate notebook type from card and context

        Time Complexity: O(n) where n = text length for keyword matching
        Space Complexity: O(1) constant space

        Args:
            card: Kanban card with task information
            context: Optional additional context

        Returns:
            Notebook type string (data_analysis, machine_learning, etc.)
        """
        # Guard clause: check explicit type in card metadata
        metadata = card.get('metadata', {})
        if 'notebook_type' in metadata:
            nb_type = metadata['notebook_type'].lower()
            if nb_type in self.NOTEBOOK_TYPE_MAPPING:
                return self.NOTEBOOK_TYPE_MAPPING[nb_type]

        # Guard clause: check explicit type in context
        if context and 'notebook_type' in context:
            nb_type = context['notebook_type'].lower()
            if nb_type in self.NOTEBOOK_TYPE_MAPPING:
                return self.NOTEBOOK_TYPE_MAPPING[nb_type]

        # Infer from content
        return self._infer_type_from_content(card)

    def _infer_type_from_content(self, card: Dict[str, Any]) -> str:
        """
        Infer notebook type from card content using keywords

        Time Complexity: O(n) where n = combined text length
        Space Complexity: O(1) constant space

        Args:
            card: Kanban card with title and description

        Returns:
            Inferred notebook type string
        """
        # Combine title and description for analysis
        title = card.get('title', '').lower()
        description = card.get('description', '').lower()
        combined_text = f"{title} {description}"

        # Guard clause: empty content
        if not combined_text.strip():
            return 'general'

        # Check keywords in priority order (most specific first)
        # Early exit on first match
        if self._contains_keywords(combined_text, self.ML_KEYWORDS):
            return 'machine_learning'

        if self._contains_keywords(combined_text, self.DATA_KEYWORDS):
            return 'data_analysis'

        if self._contains_keywords(combined_text, self.API_KEYWORDS):
            return 'api_demo'

        if self._contains_keywords(combined_text, self.TEST_KEYWORDS):
            return 'test_visualization'

        if self._contains_keywords(combined_text, self.DOC_KEYWORDS):
            return 'documentation'

        # Default fallback
        return 'general'

    def _contains_keywords(self, text: str, keywords: List[str]) -> bool:
        """
        Check if text contains any of the specified keywords

        Time Complexity: O(n*m) where n = text length, m = keywords
        Space Complexity: O(1) constant space

        Args:
            text: Text to search
            keywords: List of keywords to find

        Returns:
            True if any keyword found, False otherwise
        """
        # Generator expression for early exit (short-circuit evaluation)
        return any(keyword in text for keyword in keywords)

    def get_supported_types(self) -> List[str]:
        """
        Get list of supported notebook types

        Returns:
            List of supported type strings
        """
        return list(set(self.NOTEBOOK_TYPE_MAPPING.values()))

    def is_valid_type(self, notebook_type: str) -> bool:
        """
        Check if notebook type is valid/supported

        Time Complexity: O(1) - set membership check
        Space Complexity: O(1) constant space

        Args:
            notebook_type: Type to validate

        Returns:
            True if valid, False otherwise
        """
        return notebook_type in set(self.NOTEBOOK_TYPE_MAPPING.values())
