#!/usr/bin/env python3
"""
Module: stages/bdd_scenario/gherkin_formatter.py

WHY: Converts structured BDD models (Feature/Scenario/Step) into valid
     Gherkin syntax for pytest-bdd execution and human readability.

RESPONSIBILITY: Format Feature objects as Gherkin .feature file content.
                Handles proper indentation, keyword formatting, and
                Gherkin syntax requirements.

PATTERNS:
- Strategy Pattern: Different formatting strategies for Scenario vs Scenario Outline
- Template Method: Feature formatting follows consistent structure
- Single Responsibility: Only handles formatting, no validation or generation

Integration:
- Receives Feature objects from ScenarioGenerator
- Outputs Gherkin text for storage in developer workspace
- Used by StageCore to format LLM-generated scenarios
"""

from typing import List, Dict, Any
from .models import Feature, Scenario, Step


class GherkinFormatter:
    """
    Formats Feature objects as Gherkin syntax.

    WHY: Separates formatting concerns from generation logic.
         Single responsibility for producing valid Gherkin text
         from structured data models.

    Responsibilities:
    - Format Feature declarations with tags and description
    - Format Scenario declarations with proper indentation
    - Format Given/When/Then steps with consistent spacing
    - Format Scenario Outlines with examples tables
    - Handle background steps (run before each scenario)

    Design: Stateless formatter - all methods are pure functions
            operating on Feature/Scenario/Step objects.
    """

    def __init__(self, indent_spaces: int = 2):
        """
        Initialize Gherkin formatter.

        Args:
            indent_spaces: Number of spaces for indentation (default 2)

        WHY: Configurable indentation allows adaptation to project
             coding standards while maintaining Gherkin readability.
        """
        self.indent_spaces = indent_spaces
        self.indent = ' ' * indent_spaces

    def format_feature(self, feature: Feature) -> str:
        """
        Format complete feature as Gherkin text.

        WHY: Template Method - consistent feature structure ensures
             valid Gherkin syntax and pytest-bdd compatibility.

        Args:
            feature: Feature object to format

        Returns:
            Complete Gherkin .feature file content

        Structure:
        1. Feature tags (if present)
        2. Feature: declaration
        3. Feature description (indented)
        4. Background steps (if present)
        5. Scenarios (separated by blank lines)
        """
        lines = []

        # Format feature-level tags
        if feature.tags:
            lines.append(self._format_tags(feature.tags))

        # Format feature declaration
        lines.append(f"Feature: {feature.name}")

        # Format feature description (indented)
        if feature.description:
            for line in feature.description.strip().split('\n'):
                lines.append(f"{self.indent}{line}")

        lines.append("")  # Blank line after feature description

        # Format background steps (run before each scenario)
        if feature.background:
            lines.extend(self._format_background(feature.background))
            lines.append("")

        # Format scenarios
        for scenario in feature.scenarios:
            lines.extend(self._format_scenario(scenario))
            lines.append("")  # Blank line between scenarios

        return '\n'.join(lines)

    def _format_scenario(self, scenario: Scenario) -> List[str]:
        """
        Format single scenario as Gherkin text.

        WHY: Strategy Pattern - different formatting for regular
             scenarios vs scenario outlines (data-driven tests).

        Args:
            scenario: Scenario object to format

        Returns:
            List of formatted lines for scenario
        """
        if scenario.is_outline:
            return self._format_scenario_outline(scenario)

        return self._format_regular_scenario(scenario)

    def _format_regular_scenario(self, scenario: Scenario) -> List[str]:
        """
        Format regular scenario (not outline).

        Args:
            scenario: Scenario object

        Returns:
            Formatted scenario lines
        """
        lines = []

        # Format scenario tags
        if scenario.tags:
            lines.append(self._format_tags(scenario.tags))

        # Format scenario declaration
        lines.append(f"{self.indent}Scenario: {scenario.name}")

        # Format scenario description
        if scenario.description:
            for line in scenario.description.strip().split('\n'):
                lines.append(f"{self.indent * 2}{line}")

        # Format steps
        lines.extend(self._format_steps(scenario.steps))

        return lines

    def _format_scenario_outline(self, scenario: Scenario) -> List[str]:
        """
        Format scenario outline (data-driven test).

        WHY: Scenario Outlines enable data-driven testing by
             parameterizing scenarios with examples tables.

        Args:
            scenario: Scenario outline object

        Returns:
            Formatted scenario outline lines
        """
        lines = []

        # Format scenario tags
        if scenario.tags:
            lines.append(self._format_tags(scenario.tags))

        # Format scenario outline declaration
        lines.append(f"{self.indent}Scenario Outline: {scenario.name}")

        # Format scenario description
        if scenario.description:
            for line in scenario.description.strip().split('\n'):
                lines.append(f"{self.indent * 2}{line}")

        # Format steps (may contain <placeholders>)
        lines.extend(self._format_steps(scenario.steps))

        # Format examples table
        if scenario.examples:
            lines.append("")
            lines.extend(self._format_examples_table(scenario.examples))

        return lines

    def _format_steps(self, steps: List[Step]) -> List[str]:
        """
        Format list of steps as Gherkin text.

        WHY: Guard clauses eliminate nested conditionals for cleaner
             step formatting logic.

        Args:
            steps: List of Step objects

        Returns:
            Formatted step lines
        """
        lines = []

        for step in steps:
            # Format step line
            step_line = f"{self.indent * 2}{step.keyword} {step.text}"
            lines.append(step_line)

            # Format data table if present
            if step.data_table:
                lines.extend(self._format_data_table(step.data_table))

            # Format doc string if present
            if step.doc_string:
                lines.extend(self._format_doc_string(step.doc_string))

        return lines

    def _format_background(self, steps: List[Step]) -> List[str]:
        """
        Format background steps.

        WHY: Background steps run before each scenario in the feature,
             reducing duplication of common setup steps.

        Args:
            steps: List of background steps

        Returns:
            Formatted background lines
        """
        lines = [f"{self.indent}Background:"]
        lines.extend(self._format_steps(steps))
        return lines

    def _format_tags(self, tags: List[str]) -> str:
        """
        Format tags as Gherkin text.

        WHY: Tags enable selective test execution (@smoke, @integration)
             and categorization of scenarios.

        Args:
            tags: List of tag names (without @ prefix)

        Returns:
            Formatted tag line (e.g., "@smoke @integration")
        """
        # Ensure tags have @ prefix
        formatted_tags = [f"@{tag}" if not tag.startswith('@') else tag for tag in tags]
        return ' '.join(formatted_tags)

    def _format_data_table(self, data_table: List[Dict[str, str]]) -> List[str]:
        """
        Format data table for step.

        WHY: Data tables provide structured input data for steps,
             common in Given steps for setting up test data.

        Args:
            data_table: List of dictionaries (each dict is a row)

        Returns:
            Formatted table lines with proper alignment
        """
        if not data_table:
            return []

        lines = []

        # Get column headers from first row
        headers = list(data_table[0].keys())

        # Calculate column widths for alignment
        widths = {header: len(header) for header in headers}
        for row in data_table:
            for header in headers:
                widths[header] = max(widths[header], len(str(row.get(header, ''))))

        # Format header row
        header_cells = [f"{header:<{widths[header]}}" for header in headers]
        lines.append(f"{self.indent * 3}| {' | '.join(header_cells)} |")

        # Format data rows
        for row in data_table:
            cells = [f"{str(row.get(header, '')):<{widths[header]}}" for header in headers]
            lines.append(f"{self.indent * 3}| {' | '.join(cells)} |")

        return lines

    def _format_doc_string(self, doc_string: str) -> List[str]:
        """
        Format doc string (multiline text) for step.

        WHY: Doc strings provide large text input for steps,
             common for JSON payloads or expected output.

        Args:
            doc_string: Multiline text content

        Returns:
            Formatted doc string lines with delimiters
        """
        lines = [f"{self.indent * 3}\"\"\""]

        for line in doc_string.strip().split('\n'):
            lines.append(f"{self.indent * 3}{line}")

        lines.append(f"{self.indent * 3}\"\"\"")

        return lines

    def _format_examples_table(self, examples: List[Dict[str, Any]]) -> List[str]:
        """
        Format examples table for scenario outline.

        WHY: Examples tables drive data-driven tests by providing
             multiple input/output combinations for same scenario.

        Args:
            examples: List of example data dictionaries

        Returns:
            Formatted examples table lines
        """
        if not examples:
            return []

        lines = [f"{self.indent * 2}Examples:"]

        # Get column headers from first example
        headers = list(examples[0].keys())

        # Calculate column widths for alignment
        widths = {header: len(header) for header in headers}
        for example in examples:
            for header in headers:
                widths[header] = max(widths[header], len(str(example.get(header, ''))))

        # Format header row
        header_cells = [f"{header:<{widths[header]}}" for header in headers]
        lines.append(f"{self.indent * 3}| {' | '.join(header_cells)} |")

        # Format data rows
        for example in examples:
            cells = [f"{str(example.get(header, '')):<{widths[header]}}" for header in headers]
            lines.append(f"{self.indent * 3}| {' | '.join(cells)} |")

        return lines
