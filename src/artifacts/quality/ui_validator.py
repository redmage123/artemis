#!/usr/bin/env python3
"""
WHY: Validate UI components for accessibility and responsive design
RESPONSIBILITY: Check UI for ARIA labels and responsive patterns
PATTERNS: Template Method (extends base), Functional composition (checks)

UI validator ensures accessible, responsive components.
"""

from typing import Dict, List, Optional
from pathlib import Path

from artifacts.quality.base import ArtifactQualityValidator
from artifacts.quality.models import ValidationResult
from artifacts.quality.aggregator import ResultAggregator


class UIQualityValidator(ArtifactQualityValidator):
    """
    Validates UI components using functional checks.

    WHY: UI needs accessibility and responsive design validation.
    RESPONSIBILITY: Execute accessibility and responsive checks.
    PATTERNS: Template Method, Functional composition.
    """

    def validate(self, artifact_path: Path) -> ValidationResult:
        """
        Validate UI quality using functional composition.

        WHY: Composition of check functions enables easy extension.

        Args:
            artifact_path: Path to UI component file

        Returns:
            ValidationResult with aggregated check results
        """
        content = self._load_content(artifact_path)

        checks = [
            self._check_accessibility(content),
            self._check_responsive_design(content)
        ]

        # Filter out None values (checks that don't apply)
        active_checks = [c for c in checks if c is not None]

        return ResultAggregator.aggregate(active_checks)

    def generate_validation_prompt(self, requirements: str) -> str:
        """
        Generate comprehensive prompt for UI creation.

        WHY: Quality prompts produce quality UI.

        Args:
            requirements: User requirements

        Returns:
            Comprehensive UI creation prompt
        """
        accessibility = self.quality_criteria.get('accessibility_required')
        responsive = self.quality_criteria.get('responsive_required')

        prompt = f"""Create a production-quality UI component.

Requirements:
{requirements}

Quality Criteria:
- Clean, semantic HTML
- Modern CSS (flexbox/grid)
{"- WCAG 2.1 AA accessibility (ARIA labels, keyboard navigation)" if accessibility else ""}
{"- Fully responsive design (mobile, tablet, desktop)" if responsive else ""}
- Cross-browser compatible
- Well-documented

Return JSON format:
{{{{
    "files": [
        {{{{"path": "filename.html", "content": "file content here"}}}},
        {{{{"path": "filename.css", "content": "file content here"}}}}
    ]
}}}}
"""
        return prompt

    def _load_content(self, path: Path) -> str:
        """Load UI component content"""
        with open(path, 'r') as f:
            return f.read()

    def _check_accessibility(self, content: str) -> Optional[Dict]:
        """Check accessibility features"""
        accessibility_required = self.quality_criteria.get('accessibility_required')

        # Guard clause - accessibility not required
        if not accessibility_required:
            return None

        return self._validate_accessibility(content)

    def _validate_accessibility(self, content: str) -> Dict:
        """Validate ARIA/accessibility attributes"""
        has_aria = 'aria-' in content or 'role=' in content

        return {
            'name': 'accessibility',
            'passed': has_aria,
            'feedback': None if has_aria else "Missing ARIA labels/roles for accessibility"
        }

    def _check_responsive_design(self, content: str) -> Optional[Dict]:
        """Check responsive design patterns"""
        responsive_required = self.quality_criteria.get('responsive_required')

        # Guard clause - responsive not required
        if not responsive_required:
            return None

        return self._validate_responsive(content)

    def _validate_responsive(self, content: str) -> Dict:
        """Validate responsive design patterns"""
        responsive_keywords = ['@media', 'flex', 'grid', 'responsive']
        has_responsive = any(kw in content.lower() for kw in responsive_keywords)

        return {
            'name': 'responsive',
            'passed': has_responsive,
            'feedback': None if has_responsive else "Missing responsive design patterns"
        }
