#!/usr/bin/env python3
"""
Logic of Thoughts (LoT) Reasoning Strategy

WHY: Applies formal logical reasoning (deduction, induction, abduction) to ensure
     sound conclusions based on explicit premises and logical rules.

RESPONSIBILITY:
    - Generate prompts with formal logic instructions
    - Parse logical rules and deductions from responses
    - Extract premise-conclusion pairs
    - Track logical inference chains

PATTERNS:
    - Strategy Pattern: Concrete reasoning strategy implementation
    - Guard Clauses: Input validation and edge case handling
    - Single Responsibility: Focused on formal logic reasoning
"""

from typing import Dict, List, Optional, Any
import logging

from .models import ReasoningStrategyBase, LogicRule


class LogicOfThoughtsStrategy(ReasoningStrategyBase):
    """
    Logic of Thoughts (LoT) prompting strategy.

    Uses formal logical rules and deductions for sound reasoning.

    WHY: Formal logic ensures valid conclusions from premises
    RESPONSIBILITY: Generate logic-based prompts and parse logical inferences

    Example:
        lot = LogicOfThoughtsStrategy()
        prompt = lot.generate_prompt(
            "If all programmers are problem solvers...",
            axioms=["All programmers write code", "All code has bugs"]
        )
        result = lot.parse_response(llm_response)
    """

    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        Initialize LoT strategy.

        Args:
            logger: Optional logger instance
        """
        super().__init__(logger)
        self.rules: List[LogicRule] = []

    def generate_prompt(
        self,
        task: str,
        context: Optional[str] = None,
        axioms: Optional[List[str]] = None
    ) -> str:
        """
        Generate LoT prompt with logical reasoning instructions.

        WHY: Structured prompts guide LLM to use formal logic
        PATTERNS: Guard clauses for optional parameters

        Args:
            task: The task to solve
            context: Additional context information
            axioms: Known facts/axioms to use as premises

        Returns:
            Formatted prompt with logical reasoning instructions
        """
        prompt = "Let's solve this using logical reasoning and formal deduction.\n\n"

        # Guard clause: Add context if provided
        if context:
            prompt += f"Context:\n{context}\n\n"

        # Guard clause: Add axioms if provided
        if axioms:
            prompt += self._format_axioms(axioms)

        prompt += f"Task: {task}\n\n"
        prompt += self._get_logic_instructions()

        return prompt

    def _format_axioms(self, axioms: List[str]) -> str:
        """
        Format axioms as numbered list.

        WHY: Separate formatting for better maintainability
        RESPONSIBILITY: Convert axioms to formatted string

        Args:
            axioms: List of known facts

        Returns:
            Formatted axioms string
        """
        result = "Known Facts (Axioms):\n"
        for i, axiom in enumerate(axioms, 1):
            result += f"{i}. {axiom}\n"
        return result + "\n"

    def _get_logic_instructions(self) -> str:
        """
        Get formal logic reasoning instructions.

        WHY: Centralized logic rules for consistency
        RESPONSIBILITY: Provide standard logical reasoning instructions

        Returns:
            Logic instruction text with common inference rules
        """
        return (
            "Please reason through this using formal logic:\n\n"
            "1. Identify all given premises\n"
            "2. State any assumptions clearly\n"
            "3. Apply logical rules step by step:\n"
            "   - Modus Ponens: If P then Q, P is true, therefore Q is true\n"
            "   - Modus Tollens: If P then Q, Q is false, therefore P is false\n"
            "   - Syllogism: If P then Q, Q then R, therefore P then R\n"
            "   - Contrapositive: If P then Q is equivalent to If not Q then not P\n"
            "4. Show each deduction explicitly\n"
            "5. State your conclusion and verify it follows logically\n\n"
            "Your logical reasoning:"
        )

    def parse_response(self, response: str) -> Dict[str, Any]:
        """
        Parse LoT response into logical rules and deductions.

        WHY: Extract structured logic from natural language reasoning
        PATTERNS: Guard clauses for empty input

        Args:
            response: LLM response with logical reasoning

        Returns:
            Structured logical reasoning with rules
        """
        # Guard clause: Handle empty response
        if not response or not response.strip():
            return {
                "strategy": "logic_of_thoughts",
                "rules": [],
                "total_rules": 0,
                "error": "empty_response"
            }

        rules = self._extract_logical_rules(response)
        self.rules = rules

        return {
            "strategy": "logic_of_thoughts",
            "rules": [r.to_dict() for r in rules],
            "total_rules": len(rules)
        }

    def _extract_logical_rules(self, response: str) -> List[LogicRule]:
        """
        Extract logical rules from response text.

        WHY: Parse natural language into structured logic rules
        RESPONSIBILITY: Identify premise-conclusion pairs
        PATTERNS: Guard clauses for line validation

        Args:
            response: Response text with logical reasoning

        Returns:
            List of extracted logical rules
        """
        rules = []
        lines = response.strip().split('\n')

        for line in lines:
            # Guard clause: Skip empty lines
            if not line.strip():
                continue

            # Check for logical implication markers
            rule = self._parse_logical_implication(line)
            if rule:
                rules.append(rule)

        return rules

    def _parse_logical_implication(self, line: str) -> Optional[LogicRule]:
        """
        Parse a logical implication from a line of text.

        WHY: Centralized logic for identifying implications
        RESPONSIBILITY: Extract premise and conclusion from implication
        PATTERNS: Guard clauses for different implication formats

        Args:
            line: Text line to parse

        Returns:
            LogicRule if implication found, None otherwise
        """
        lower_line = line.lower()

        # Guard clause: Check for 'therefore' marker
        if 'therefore' in lower_line:
            return self._parse_therefore_rule(line)

        # Guard clause: Check for '=>' marker
        if '=>' in line:
            return self._parse_arrow_rule(line, '=>')

        # Guard clause: Check for '→' marker
        if '→' in line:
            return self._parse_arrow_rule(line, '→')

        return None

    def _parse_therefore_rule(self, line: str) -> Optional[LogicRule]:
        """
        Parse rule with 'therefore' keyword.

        WHY: Handle natural language implication format
        RESPONSIBILITY: Split on 'therefore' and create rule

        Args:
            line: Line containing 'therefore'

        Returns:
            LogicRule or None if parsing fails
        """
        parts = line.split('therefore')

        # Guard clause: Must have exactly 2 parts
        if len(parts) != 2:
            return None

        return LogicRule(
            premise=parts[0].strip(),
            conclusion=parts[1].strip(),
            rule_type="deduction"
        )

    def _parse_arrow_rule(self, line: str, arrow: str) -> Optional[LogicRule]:
        """
        Parse rule with arrow notation (=> or →).

        WHY: Handle symbolic implication format
        RESPONSIBILITY: Split on arrow and create rule

        Args:
            line: Line containing arrow
            arrow: Arrow symbol to split on

        Returns:
            LogicRule or None if parsing fails
        """
        parts = line.split(arrow)

        # Guard clause: Must have exactly 2 parts
        if len(parts) != 2:
            return None

        return LogicRule(
            premise=parts[0].strip(),
            conclusion=parts[1].strip(),
            rule_type="deduction"
        )

    def get_inference_chain(self) -> List[str]:
        """
        Get the chain of logical inferences.

        WHY: Provide sequence of deductions for analysis
        RESPONSIBILITY: Build ordered list of conclusions

        Returns:
            List of conclusion strings in order
        """
        return [rule.conclusion for rule in self.rules]

    def validate_logical_consistency(self) -> Dict[str, Any]:
        """
        Validate logical consistency of extracted rules.

        WHY: Check for contradictions in reasoning
        RESPONSIBILITY: Detect inconsistent conclusions
        PATTERNS: Guard clause for empty rules

        Returns:
            Dictionary with consistency analysis
        """
        # Guard clause: No rules to validate
        if not self.rules:
            return {
                "consistent": True,
                "warnings": [],
                "note": "No rules to validate"
            }

        conclusions = [rule.conclusion.lower() for rule in self.rules]
        warnings = []

        # Check for contradictory conclusions (simple heuristic)
        for i, conclusion in enumerate(conclusions):
            # Look for negations in other conclusions
            for j, other in enumerate(conclusions):
                if i != j and self._are_contradictory(conclusion, other):
                    warnings.append(
                        f"Potential contradiction: '{conclusion}' vs '{other}'"
                    )

        return {
            "consistent": len(warnings) == 0,
            "warnings": warnings,
            "total_rules": len(self.rules)
        }

    def _are_contradictory(self, conclusion1: str, conclusion2: str) -> bool:
        """
        Check if two conclusions are contradictory.

        WHY: Simple contradiction detection (can be enhanced)
        RESPONSIBILITY: Detect basic negation patterns

        Args:
            conclusion1: First conclusion
            conclusion2: Second conclusion

        Returns:
            True if likely contradictory
        """
        # Simple check for "not" patterns
        return (
            ("not" in conclusion1 and conclusion1.replace("not", "").strip() in conclusion2) or
            ("not" in conclusion2 and conclusion2.replace("not", "").strip() in conclusion1)
        )
