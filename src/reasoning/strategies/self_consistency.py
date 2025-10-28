#!/usr/bin/env python3
"""
Self-Consistency Reasoning Strategy

WHY: Generates multiple independent reasoning paths and selects the most
     consistent answer through majority voting, improving reliability.

RESPONSIBILITY:
    - Generate prompts for multiple reasoning samples
    - Collect and track multiple independent responses
    - Analyze consistency across samples
    - Select most frequent answer with confidence scoring

PATTERNS:
    - Strategy Pattern: Concrete reasoning strategy implementation
    - Ensemble Method: Multiple samples for robustness
    - Guard Clauses: Validation and edge case handling
    - Dispatch Table: Answer frequency counting
"""

from typing import Dict, List, Optional, Any
from collections import Counter
import logging

from .models import ReasoningStrategyBase


class SelfConsistencyStrategy(ReasoningStrategyBase):
    """
    Self-Consistency reasoning strategy.

    Generates multiple reasoning paths and selects the most consistent answer.

    WHY: Multiple samples reduce variance and improve answer reliability
    RESPONSIBILITY: Manage sample collection and consistency analysis

    Example:
        sc = SelfConsistencyStrategy(num_samples=5)
        prompt = sc.generate_prompt("What is the capital of France?")

        # Collect multiple responses
        for response in llm_responses:
            sc.parse_response(response)

        # Get consensus
        result = sc.get_consistent_answer()
    """

    def __init__(
        self,
        num_samples: int = 5,
        logger: Optional[logging.Logger] = None
    ):
        """
        Initialize Self-Consistency strategy.

        Args:
            num_samples: Number of samples to collect
            logger: Optional logger instance
        """
        super().__init__(logger)
        self.num_samples = num_samples
        self.samples: List[str] = []

    def generate_prompt(
        self,
        task: str,
        context: Optional[str] = None
    ) -> str:
        """
        Generate prompt for self-consistency sampling.

        WHY: Simple prompt encourages independent reasoning paths
        PATTERNS: Guard clause for context

        Args:
            task: The task to solve
            context: Optional additional context

        Returns:
            Formatted prompt string
        """
        prompt = f"Task: {task}\n\n"

        # Guard clause: Add context if provided
        if context:
            prompt += f"Context: {context}\n\n"

        prompt += "Please solve this problem and show your reasoning."
        return prompt

    def parse_response(self, response: str) -> Dict[str, Any]:
        """
        Parse response and add to sample collection.

        WHY: Accumulate multiple independent responses
        PATTERNS: Guard clause for empty response

        Args:
            response: LLM response with reasoning

        Returns:
            Current collection status
        """
        # Guard clause: Skip empty responses
        if not response or not response.strip():
            self.logger.warning("Skipping empty response")
            return {
                "strategy": "self_consistency",
                "samples_collected": len(self.samples),
                "target_samples": self.num_samples,
                "warning": "empty_response_skipped"
            }

        self.samples.append(response)

        return {
            "strategy": "self_consistency",
            "samples_collected": len(self.samples),
            "target_samples": self.num_samples,
            "complete": len(self.samples) >= self.num_samples
        }

    def get_consistent_answer(self) -> Dict[str, Any]:
        """
        Analyze samples and return most consistent answer.

        WHY: Majority voting provides robust answer selection
        RESPONSIBILITY: Find most frequent answer with confidence
        PATTERNS: Guard clauses for validation

        Returns:
            Most frequent answer with confidence metrics
        """
        # Guard clause: No samples collected
        if not self.samples:
            return {
                "answer": None,
                "error": "no_samples_collected",
                "confidence": 0.0
            }

        # Extract answers from samples
        answers = self._extract_answers()

        # Guard clause: No answers extracted
        if not answers:
            return {
                "answer": None,
                "error": "no_answers_extracted",
                "total_samples": len(self.samples),
                "confidence": 0.0
            }

        # Find most common answer
        answer_counts = Counter(answers)
        best_answer, frequency = answer_counts.most_common(1)[0]

        return {
            "answer": best_answer,
            "frequency": frequency,
            "confidence": frequency / len(self.samples),
            "total_samples": len(self.samples),
            "unique_answers": len(answer_counts),
            "distribution": dict(answer_counts)
        }

    def _extract_answers(self) -> List[str]:
        """
        Extract final answers from all samples.

        WHY: Parse answers from potentially verbose responses
        RESPONSIBILITY: Extract answer strings from each sample
        PATTERNS: Guard clauses for extraction patterns

        Returns:
            List of extracted answer strings
        """
        answers = []

        for sample in self.samples:
            answer = self._extract_single_answer(sample)
            # Guard clause: Skip if no answer found
            if answer:
                answers.append(answer)

        return answers

    def _extract_single_answer(self, sample: str) -> Optional[str]:
        """
        Extract answer from a single sample.

        WHY: Centralized answer extraction logic
        RESPONSIBILITY: Parse answer from various formats
        PATTERNS: Guard clauses for different answer markers

        Args:
            sample: Sample text to extract from

        Returns:
            Extracted answer or None
        """
        lower_sample = sample.lower()

        # Guard clause: Check for explicit "answer:" marker
        if "answer:" in lower_sample:
            return self._extract_after_marker(sample, "answer:")

        # Guard clause: Check for "the answer is" pattern
        if "the answer is" in lower_sample:
            return self._extract_after_marker(sample, "the answer is")

        # Guard clause: Check for "conclusion:" marker
        if "conclusion:" in lower_sample:
            return self._extract_after_marker(sample, "conclusion:")

        # Default: Use last non-empty line as answer
        return self._extract_last_line(sample)

    def _extract_after_marker(self, text: str, marker: str) -> str:
        """
        Extract text after a specific marker.

        WHY: Common extraction pattern for answer markers
        RESPONSIBILITY: Split and clean text after marker

        Args:
            text: Text to extract from
            marker: Marker string to split on

        Returns:
            Extracted text after marker
        """
        parts = text.lower().split(marker)
        # Guard clause: Marker not found or nothing after it
        if len(parts) < 2:
            return ""

        # Take text after marker, strip whitespace
        answer = parts[-1].strip()

        # Further clean: take first sentence/line
        answer = answer.split('\n')[0].split('.')[0].strip()

        return answer

    def _extract_last_line(self, text: str) -> str:
        """
        Extract last non-empty line from text.

        WHY: Fallback extraction when no marker found
        RESPONSIBILITY: Get final statement as answer

        Args:
            text: Text to extract from

        Returns:
            Last non-empty line
        """
        lines = [line.strip() for line in text.strip().split('\n')]
        # Filter empty lines and return last one
        non_empty_lines = [line for line in lines if line]

        # Guard clause: No non-empty lines
        if not non_empty_lines:
            return ""

        return non_empty_lines[-1]

    def get_confidence_breakdown(self) -> Dict[str, Any]:
        """
        Get detailed breakdown of answer confidence.

        WHY: Provide transparency into consensus strength
        RESPONSIBILITY: Calculate various confidence metrics

        Returns:
            Detailed confidence analysis
        """
        # Guard clause: No samples
        if not self.samples:
            return {
                "error": "no_samples",
                "metrics": {}
            }

        answers = self._extract_answers()

        # Guard clause: No answers
        if not answers:
            return {
                "error": "no_answers_extracted",
                "total_samples": len(self.samples),
                "metrics": {}
            }

        answer_counts = Counter(answers)
        total_answers = len(answers)
        unique_answers = len(answer_counts)

        # Calculate metrics
        most_common_count = answer_counts.most_common(1)[0][1]
        majority_confidence = most_common_count / total_answers

        # Calculate entropy (measure of disagreement)
        entropy = self._calculate_entropy(answer_counts, total_answers)

        return {
            "total_samples": len(self.samples),
            "extracted_answers": total_answers,
            "unique_answers": unique_answers,
            "majority_confidence": majority_confidence,
            "majority_count": most_common_count,
            "entropy": entropy,
            "agreement_strength": "high" if majority_confidence > 0.7 else "medium" if majority_confidence > 0.5 else "low"
        }

    def _calculate_entropy(
        self,
        counts: Counter,
        total: int
    ) -> float:
        """
        Calculate Shannon entropy of answer distribution.

        WHY: Measure uncertainty/disagreement in answers
        RESPONSIBILITY: Compute entropy metric

        Args:
            counts: Counter of answer frequencies
            total: Total number of answers

        Returns:
            Entropy value (higher = more disagreement)
        """
        import math

        # Guard clause: Avoid division by zero
        if total == 0:
            return 0.0

        entropy = 0.0
        for count in counts.values():
            probability = count / total
            # Guard clause: Skip zero probabilities
            if probability > 0:
                entropy -= probability * math.log2(probability)

        return entropy
