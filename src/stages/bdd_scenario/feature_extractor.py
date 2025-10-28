#!/usr/bin/env python3
"""
Module: stages/bdd_scenario/feature_extractor.py

WHY: Extracts feature-level information from requirements and prepares
     structured data for scenario generation.

RESPONSIBILITY: Parse requirements into feature components (name, description,
                acceptance criteria). Prepares clean, structured data for
                LLM scenario generation.

PATTERNS:
- Strategy Pattern: Multiple extraction strategies for different requirement formats
- Single Responsibility: Only extracts feature data, no generation or validation

Integration:
- Receives requirements from RequirementsRetriever
- Outputs structured feature data to ScenarioGenerator
- Used by StageCore to prepare generation inputs
"""

from typing import Dict, Any, List, Optional


class FeatureExtractor:
    """
    Extracts feature information from requirements.

    WHY: Requirements come in various formats (dict, string, structured).
         Extractor normalizes these into consistent feature data for
         reliable scenario generation.

    Responsibilities:
    - Extract feature name from requirements or title
    - Extract feature description (user story format)
    - Extract acceptance criteria for scenario hints
    - Normalize requirement formats
    """

    def extract(
        self,
        title: str,
        requirements: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Extract feature data from requirements.

        WHY: Dispatch table pattern eliminates elif chains for
             handling different requirement formats.

        Args:
            title: Feature title
            requirements: Requirements dictionary

        Returns:
            Normalized feature data dictionary:
            - name: Feature name
            - description: Feature description (user story)
            - acceptance_criteria: List of acceptance criteria
            - functional_reqs: List of functional requirements
            - non_functional_reqs: List of non-functional requirements
        """
        # Guard: Empty requirements
        if not requirements:
            return self._extract_from_title(title)

        # Dispatch table for extraction strategies
        extraction_strategies = {
            'structured': self._is_structured_requirements,
            'user_story': self._is_user_story_format,
            'simple': lambda r: True  # Default fallback
        }

        # Find matching strategy
        for strategy_name, check_func in extraction_strategies.items():
            if check_func(requirements):
                return self._extract_with_strategy(
                    strategy_name,
                    title,
                    requirements
                )

        # Fallback to title extraction
        return self._extract_from_title(title)

    def _extract_with_strategy(
        self,
        strategy_name: str,
        title: str,
        requirements: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Extract feature data using specific strategy.

        WHY: Dispatch table eliminates elif chain for strategy selection.

        Args:
            strategy_name: Name of extraction strategy
            title: Feature title
            requirements: Requirements data

        Returns:
            Extracted feature data
        """
        strategies = {
            'structured': self._extract_structured,
            'user_story': self._extract_user_story,
            'simple': self._extract_simple
        }

        extract_func = strategies.get(strategy_name, self._extract_simple)
        return extract_func(title, requirements)

    def _is_structured_requirements(self, requirements: Dict[str, Any]) -> bool:
        """
        Check if requirements are in structured format.

        WHY: Structured requirements have explicit fields (description,
             acceptance_criteria, functional_requirements).

        Args:
            requirements: Requirements data

        Returns:
            True if structured format detected
        """
        if not isinstance(requirements, dict):
            return False

        structured_keys = {'description', 'acceptance_criteria', 'functional_requirements'}
        return any(key in requirements for key in structured_keys)

    def _is_user_story_format(self, requirements: Dict[str, Any]) -> bool:
        """
        Check if requirements are in user story format.

        WHY: User story format contains "As a", "I want", "So that" phrases.

        Args:
            requirements: Requirements data

        Returns:
            True if user story format detected
        """
        if isinstance(requirements, str):
            content = requirements
        elif isinstance(requirements, dict):
            content = str(requirements.get('description', ''))
        else:
            return False

        user_story_markers = ['As a', 'I want', 'So that']
        return any(marker in content for marker in user_story_markers)

    def _extract_structured(
        self,
        title: str,
        requirements: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Extract from structured requirements format.

        WHY: Structured format provides explicit fields that map
             directly to feature components.

        Args:
            title: Feature title
            requirements: Structured requirements dict

        Returns:
            Extracted feature data
        """
        return {
            'name': requirements.get('feature_name', title),
            'description': requirements.get('description', ''),
            'acceptance_criteria': requirements.get('acceptance_criteria', []),
            'functional_reqs': requirements.get('functional_requirements', []),
            'non_functional_reqs': requirements.get('non_functional_requirements', [])
        }

    def _extract_user_story(
        self,
        title: str,
        requirements: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Extract from user story format.

        WHY: User stories provide business context but require
             parsing to extract feature components.

        Args:
            title: Feature title
            requirements: User story requirements

        Returns:
            Extracted feature data
        """
        if isinstance(requirements, str):
            description = requirements
        else:
            description = requirements.get('description', str(requirements))

        # Extract acceptance criteria if present
        acceptance_criteria = self._parse_acceptance_criteria(description)

        return {
            'name': title,
            'description': description,
            'acceptance_criteria': acceptance_criteria,
            'functional_reqs': [],
            'non_functional_reqs': []
        }

    def _extract_simple(
        self,
        title: str,
        requirements: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Extract from simple requirements format.

        WHY: Fallback for unstructured requirements - uses title
             and converts dict to description text.

        Args:
            title: Feature title
            requirements: Simple requirements

        Returns:
            Extracted feature data
        """
        # Convert requirements to description text
        if isinstance(requirements, str):
            description = requirements
        elif isinstance(requirements, dict):
            description = '\n'.join(f"{k}: {v}" for k, v in requirements.items())
        else:
            description = str(requirements)

        return {
            'name': title,
            'description': description,
            'acceptance_criteria': [],
            'functional_reqs': [],
            'non_functional_reqs': []
        }

    def _extract_from_title(self, title: str) -> Dict[str, Any]:
        """
        Extract minimal feature data from title only.

        WHY: Fallback when no requirements available - provides
             minimal data structure for generation.

        Args:
            title: Feature title

        Returns:
            Minimal feature data
        """
        return {
            'name': title,
            'description': f"Feature: {title}",
            'acceptance_criteria': [],
            'functional_reqs': [],
            'non_functional_reqs': []
        }

    def _parse_acceptance_criteria(self, text: str) -> List[str]:
        """
        Parse acceptance criteria from text.

        WHY: Acceptance criteria provide scenario hints and
             should be extracted for generation context.

        Args:
            text: Text containing potential acceptance criteria

        Returns:
            List of acceptance criteria strings
        """
        criteria = []

        # Common acceptance criteria markers
        markers = [
            'Acceptance Criteria:',
            'AC:',
            'Given that',
            'When the user',
            'Then the system'
        ]

        lines = text.split('\n')
        in_criteria_section = False

        for line in lines:
            # Check for criteria section start
            if any(marker in line for marker in markers):
                in_criteria_section = True
                continue

            # Extract criteria lines
            if in_criteria_section:
                # Stop at empty line or new section
                if not line.strip() or line.strip().startswith('#'):
                    in_criteria_section = False
                    continue

                # Add criteria line
                criteria.append(line.strip())

        return criteria


class FeatureFileStorage:
    """
    Stores feature files in developer workspace.

    WHY: Single Responsibility - separates file I/O from generation logic.
         Developers need feature files in workspace for pytest-bdd execution.

    Responsibilities:
    - Create developer workspace directories
    - Write feature files with proper naming
    - Return file paths for tracking
    """

    def __init__(self, logger: Any):
        """
        Initialize feature file storage.

        Args:
            logger: Logger for tracking file operations
        """
        self.logger = logger

    def store(
        self,
        developer: str,
        title: str,
        content: str,
        base_path: str = "/tmp"
    ) -> str:
        """
        Store feature file in developer workspace.

        WHY: pytest-bdd auto-discovers *.feature files in features/
             directory. Consistent naming and location enables
             automatic test execution.

        Args:
            developer: Developer identifier (e.g., "developer-a")
            title: Feature title (sanitized for filename)
            content: Gherkin feature content
            base_path: Base path for developer workspaces

        Returns:
            Path to created feature file
        """
        from pathlib import Path

        # Create features directory
        feature_dir = Path(base_path) / developer / "features"
        feature_dir.mkdir(parents=True, exist_ok=True)

        # Sanitize filename
        filename = self._sanitize_filename(title)
        feature_path = feature_dir / f"{filename}.feature"

        # Write feature file
        with open(feature_path, 'w') as f:
            f.write(content)

        self.logger.log(f"📝 Stored feature file: {feature_path}", "INFO")

        return str(feature_path)

    def _sanitize_filename(self, title: str) -> str:
        """
        Sanitize title for filename.

        WHY: Removes characters invalid for filenames and follows
             Python naming conventions (lowercase, underscores).

        Args:
            title: Feature title

        Returns:
            Sanitized filename (without .feature extension)
        """
        # Convert to lowercase
        filename = title.lower()

        # Replace invalid characters with underscores
        invalid_chars = ' /-\\:*?"<>|'
        for char in invalid_chars:
            filename = filename.replace(char, '_')

        # Remove consecutive underscores
        while '__' in filename:
            filename = filename.replace('__', '_')

        # Remove leading/trailing underscores
        filename = filename.strip('_')

        return filename
