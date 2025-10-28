#!/usr/bin/env python3
"""
WHY: Generate self-critique prompts and parse LLM responses.

RESPONSIBILITY:
- Build critique prompts based on critique level
- Query LLM for self-critique analysis
- Parse structured critique responses into findings
- Extract confidence scores from critique text

PATTERNS:
- Strategy Pattern: Different critique templates per level
- Template Method: Consistent critique format with customizable depth
- Dispatch Table: Level-to-template mapping for O(1) lookup
"""

import re
import logging
from functools import lru_cache
from typing import Dict, List, Any, Optional

from .models import CritiqueLevel, CritiqueSeverity, CritiqueFinding


class CritiqueGenerator:
    """
    WHY: Generate and parse LLM self-critique responses.

    RESPONSIBILITY:
    - Build level-appropriate critique prompts
    - Execute LLM queries for critique generation
    - Parse critique text into structured findings
    - Extract confidence scores
    """

    # Dispatch table for critique templates
    _CRITIQUE_TEMPLATES: Dict[CritiqueLevel, str] = {
        CritiqueLevel.QUICK: """
Review for:
1. Obvious logical errors
2. Missing edge cases
3. Placeholder code (TODO, FIXME, etc.)
4. Hallucinated APIs (methods that don't exist)
""",
        CritiqueLevel.BALANCED: """
Review for:
1. Logical errors and edge cases
2. Performance issues (O(n²) where O(n) possible)
3. Security vulnerabilities (SQL injection, XSS, etc.)
4. Error handling gaps
5. Hallucinated or non-existent APIs
6. Violations of framework best practices
7. Missing input validation
""",
        CritiqueLevel.THOROUGH: """
Review for:
1. Logical errors and all edge cases
2. Performance and scalability issues
3. Security vulnerabilities (comprehensive)
4. Concurrency/threading issues
5. Error handling and recovery
6. Resource leaks (connections, files, memory)
7. Hallucinated or deprecated APIs
8. Framework best practices
9. Code maintainability and readability
10. Test coverage gaps
11. Documentation completeness
12. Accessibility considerations
13. Internationalization support
"""
    }

    def __init__(self, llm_client: Any, level: CritiqueLevel, logger: Optional[logging.Logger] = None):
        """
        Initialize critique generator.

        Args:
            llm_client: LLM client for generating critiques
            level: Depth of critique analysis
            logger: Optional logger
        """
        self.llm_client = llm_client
        self.level = level
        self.logger = logger or logging.getLogger(__name__)

    def generate_critique(self, code: str, context: Dict[str, Any], original_prompt: str = "") -> str:
        """
        Generate self-critique from LLM.

        Args:
            code: Generated code to critique
            context: Context (language, framework, requirements)
            original_prompt: Original prompt that generated this code

        Returns:
            Raw critique text from LLM
        """
        # Guard clause: Empty code
        if not code or not code.strip():
            return "ERROR: Cannot critique empty code"

        critique_prompt = self._build_critique_prompt(code, context, original_prompt)
        return self._get_llm_critique(critique_prompt)

    def parse_critique(self, raw_critique: str) -> List[CritiqueFinding]:
        """
        Parse critique response into structured findings.

        Args:
            raw_critique: Raw critique text from LLM

        Returns:
            List of CritiqueFinding objects
        """
        # Guard clause: Empty critique
        if not raw_critique or not raw_critique.strip():
            return []

        findings = []

        # Extract FINDINGS section
        findings_section = re.search(
            r'FINDINGS:(.*?)(?:OVERALL ASSESSMENT:|$)',
            raw_critique,
            re.DOTALL
        )

        # Guard clause: No findings section
        if not findings_section:
            return findings

        findings_text = findings_section.group(1)

        # Parse individual findings
        # Format: - [SEVERITY] Category: Description
        finding_pattern = re.compile(
            r'-\s*\[(ERROR|WARNING|INFO|CRITICAL)\]\s*(\w+):\s*(.+?)(?=\n\s*(?:Line:|Suggestion:|-\s*\[|$))',
            re.DOTALL
        )

        for match in finding_pattern.finditer(findings_text):
            severity_str = match.group(1)
            category = match.group(2).lower()
            message = match.group(3).strip()

            # Extract line number if present
            line_match = re.search(r'Line:\s*(\d+)', findings_text[match.end():match.end()+100])
            line_number = int(line_match.group(1)) if line_match else None

            # Extract suggestion if present
            suggestion_match = re.search(
                r'Suggestion:\s*(.+?)(?=\n-|\n\n|$)',
                findings_text[match.end():],
                re.DOTALL
            )
            suggestion = suggestion_match.group(1).strip() if suggestion_match else None

            findings.append(CritiqueFinding(
                severity=CritiqueSeverity[severity_str],
                category=category,
                message=message,
                line_number=line_number,
                suggestion=suggestion
            ))

        return findings

    def extract_confidence_score(self, raw_critique: str) -> float:
        """
        Extract confidence score from critique.

        Args:
            raw_critique: Raw critique text

        Returns:
            Confidence score (0-10), defaults to 5.0 if not found
        """
        # Guard clause: Empty critique
        if not raw_critique:
            return 5.0

        # Look for CONFIDENCE: [score]
        match = re.search(r'CONFIDENCE:\s*(\d+(?:\.\d+)?)', raw_critique)
        if match:
            return float(match.group(1))

        # Default to medium confidence
        return 5.0

    def _build_critique_prompt(self, code: str, context: Dict[str, Any], original_prompt: str) -> str:
        """
        Build self-critique prompt.

        Args:
            code: Code to critique
            context: Context dictionary
            original_prompt: Original generation prompt

        Returns:
            Complete critique prompt
        """
        critique_template = self._get_critique_template()

        prompt = f"""You are reviewing code that you just generated. Be critical and thorough.

ORIGINAL REQUEST:
{original_prompt or 'N/A'}

GENERATED CODE:
```
{code}
```

{critique_template}

Provide your critique in this format:

CONFIDENCE: [0-10 score]

FINDINGS:
- [SEVERITY] Category: Description
  Line: [line number or N/A]
  Suggestion: [how to fix]

OVERALL ASSESSMENT:
[Summary of code quality and concerns]
"""
        return prompt

    def _get_critique_template(self) -> str:
        """
        Get critique template based on level using dispatch table.

        Returns:
            Template string for current critique level
        """
        return self._CRITIQUE_TEMPLATES.get(self.level, self._CRITIQUE_TEMPLATES[CritiqueLevel.BALANCED])

    def _get_llm_critique(self, prompt: str) -> str:
        """
        Get critique from LLM.

        Args:
            prompt: Critique prompt

        Returns:
            LLM response text
        """
        try:
            # Use LLM client to generate critique
            response = self.llm_client.query(
                prompt=prompt,
                temperature=0.3,  # Lower temperature for more consistent critiques
                max_tokens=1500
            )
            return response
        except Exception as e:
            self.logger.error(f"LLM critique failed: {e}")
            return f"ERROR: Could not generate critique: {e}"
