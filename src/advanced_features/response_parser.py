#!/usr/bin/env python3
"""
Advanced Features Response Parser

WHY: Centralizes parsing of AI responses into structured data models.
Separates parsing logic from query logic to handle variations in AI
response formats consistently.

RESPONSIBILITY:
- Parse confidence estimation responses
- Parse risk assessment responses
- Parse quality evaluation responses
- Parse complexity estimation responses
- Handle JSON extraction from markdown/mixed content
- Provide robust error handling for malformed responses

PATTERNS:
- Parser Pattern: Converts unstructured text to structured data
- Strategy Pattern: Different parsing strategies via dispatch table
- Guard Clauses: Early returns for invalid inputs
- Single Responsibility: Only handles response parsing

USAGE:
    from advanced_features.response_parser import ResponseParser
    from advanced_features.models import ConfidenceEstimate

    parser = ResponseParser()
    estimate = parser.parse_confidence_response(
        response='{"confidence_score": 0.85, ...}',
        model="sonnet"
    )
"""

import json
import re
from typing import Dict, Any, List, Tuple, Callable

from artemis_exceptions import LLMError
from advanced_features.models import (
    ConfidenceEstimate,
    RiskAssessment,
    QualityEvaluation,
    ComplexityEstimate
)


class ResponseParser:
    """
    Parses AI responses into structured data models.

    WHY: AI responses may vary in format. Centralized parsing ensures
    consistent handling and makes it easy to adapt to format changes.
    """

    def __init__(self):
        """Initialize parser with dispatch table"""
        self._parsers: Dict[str, Callable] = {
            'confidence': self.parse_confidence_response,
            'risk': self.parse_risk_response,
            'quality': self.parse_quality_response,
            'complexity': self.parse_complexity_response,
            'batch_confidence': self.parse_batch_confidence_response
        }

    def parse_response(self, response_type: str, response: str, **kwargs) -> Any:
        """
        Parse response using dispatch table.

        WHY: Dispatch table eliminates elif chains and makes adding
        new parsers straightforward.

        Args:
            response_type: Type of response to parse
            response: Raw response string
            **kwargs: Additional arguments for specific parser

        Returns:
            Parsed data model

        Raises:
            ValueError: If response type is not supported
            LLMError: If parsing fails
        """
        parser = self._parsers.get(response_type)
        if not parser:
            raise ValueError(f"Unknown response type: {response_type}")

        return parser(response, **kwargs)

    def extract_json(self, response: str) -> Dict[str, Any]:
        """
        Extract JSON from AI response.

        WHY: AI responses may include JSON in markdown code blocks
        or mixed with explanatory text. This method robustly extracts
        the JSON content.

        Args:
            response: Raw response string

        Returns:
            Parsed JSON data

        Raises:
            LLMError: If JSON extraction or parsing fails
        """
        # Guard clause: empty response
        if not response or not response.strip():
            raise LLMError("Empty response provided")

        # Try to find JSON in code blocks first
        code_block_pattern = r'```(?:json)?\s*(\{.*?\})\s*```'
        code_block_match = re.search(code_block_pattern, response, re.DOTALL)
        if code_block_match:
            json_str = code_block_match.group(1)
        else:
            # Try to find raw JSON
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if not json_match:
                raise LLMError(f"Could not extract JSON from response: {response[:200]}")
            json_str = json_match.group(0)

        # Parse JSON
        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            raise LLMError(f"Failed to parse JSON: {e}. Content: {json_str[:200]}")

    def extract_json_array(self, response: str) -> List[Dict[str, Any]]:
        """
        Extract JSON array from AI response.

        WHY: Batch operations return arrays. This method handles
        array extraction with similar robustness to extract_json.

        Args:
            response: Raw response string

        Returns:
            Parsed JSON array

        Raises:
            LLMError: If JSON extraction or parsing fails
        """
        # Guard clause: empty response
        if not response or not response.strip():
            raise LLMError("Empty response provided")

        # Try to find JSON array in code blocks first
        code_block_pattern = r'```(?:json)?\s*(\[.*?\])\s*```'
        code_block_match = re.search(code_block_pattern, response, re.DOTALL)
        if code_block_match:
            json_str = code_block_match.group(1)
        else:
            # Try to find raw JSON array
            json_match = re.search(r'\[.*\]', response, re.DOTALL)
            if not json_match:
                raise LLMError(f"Could not extract JSON array from response: {response[:200]}")
            json_str = json_match.group(0)

        # Parse JSON array
        try:
            result = json.loads(json_str)
            if not isinstance(result, list):
                raise LLMError(f"Expected JSON array, got {type(result)}")
            return result
        except json.JSONDecodeError as e:
            raise LLMError(f"Failed to parse JSON array: {e}. Content: {json_str[:200]}")

    def parse_confidence_response(
        self,
        response: str,
        model: str = "unknown"
    ) -> ConfidenceEstimate:
        """
        Parse AI response into ConfidenceEstimate.

        WHY: Centralized parsing ensures consistent handling across features.

        Args:
            response: Raw response string
            model: Name of model that generated response

        Returns:
            ConfidenceEstimate object

        Raises:
            LLMError: If parsing fails
        """
        try:
            data = self.extract_json(response)
            return ConfidenceEstimate(
                score=float(data.get('confidence_score', 0.5)),
                reasoning=data.get('reasoning', ''),
                uncertainty_sources=data.get('uncertainty_sources', []),
                suggestions=data.get('suggestions', []),
                model_used=model
            )
        except (KeyError, ValueError, TypeError) as e:
            raise LLMError(f"Failed to parse confidence estimate: {e}")

    def parse_risk_response(
        self,
        response: str,
        model: str = "unknown"
    ) -> RiskAssessment:
        """
        Parse AI response into RiskAssessment.

        Args:
            response: Raw response string
            model: Name of model that generated response

        Returns:
            RiskAssessment object

        Raises:
            LLMError: If parsing fails
        """
        try:
            data = self.extract_json(response)
            return RiskAssessment(
                risk_level=data.get('risk_level', 'unknown'),
                probability=float(data.get('probability', 0.5)),
                impact=data.get('impact', ''),
                mitigations=data.get('mitigations', []),
                model_used=model
            )
        except (KeyError, ValueError, TypeError) as e:
            raise LLMError(f"Failed to parse risk assessment: {e}")

    def parse_quality_response(
        self,
        response: str,
        model: str = "unknown"
    ) -> QualityEvaluation:
        """
        Parse AI response into QualityEvaluation.

        Args:
            response: Raw response string
            model: Name of model that generated response

        Returns:
            QualityEvaluation object

        Raises:
            LLMError: If parsing fails
        """
        try:
            data = self.extract_json(response)
            return QualityEvaluation(
                quality_score=float(data.get('quality_score', 0.5)),
                issues=data.get('issues', []),
                strengths=data.get('strengths', []),
                improvement_suggestions=data.get('improvement_suggestions', []),
                model_used=model
            )
        except (KeyError, ValueError, TypeError) as e:
            raise LLMError(f"Failed to parse quality evaluation: {e}")

    def parse_complexity_response(self, response: str) -> ComplexityEstimate:
        """
        Parse AI response into ComplexityEstimate.

        Args:
            response: Raw response string

        Returns:
            ComplexityEstimate object

        Raises:
            LLMError: If parsing fails
        """
        try:
            data = self.extract_json(response)
            return ComplexityEstimate(
                complexity_level=data.get('complexity', 'medium'),
                story_points=int(data.get('story_points', 5)),
                reasoning=data.get('reasoning', ''),
                breakdown=data.get('breakdown', {}),
                parallelization_potential=data.get('parallelization_potential', 'low'),
                suggested_workers=int(data.get('suggested_workers', 1))
            )
        except (KeyError, ValueError, TypeError) as e:
            raise LLMError(f"Failed to parse complexity estimate: {e}")

    def parse_batch_confidence_response(
        self,
        response: str,
        model: str = "unknown"
    ) -> List[ConfidenceEstimate]:
        """
        Parse batch response into list of ConfidenceEstimate.

        Args:
            response: Raw response string
            model: Name of model that generated response

        Returns:
            List of ConfidenceEstimate objects

        Raises:
            LLMError: If parsing fails
        """
        try:
            data_list = self.extract_json_array(response)
            return [
                ConfidenceEstimate(
                    score=float(item.get('confidence_score', 0.5)),
                    reasoning=item.get('reasoning', ''),
                    uncertainty_sources=item.get('uncertainty_sources', []),
                    suggestions=item.get('suggestions', []),
                    model_used=model
                )
                for item in data_list
            ]
        except (KeyError, ValueError, TypeError) as e:
            raise LLMError(f"Failed to parse batch confidence estimates: {e}")

    def get_available_parsers(self) -> List[str]:
        """Get list of available parser types"""
        return list(self._parsers.keys())
