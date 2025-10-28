#!/usr/bin/env python3
"""
Module: stages/bdd_scenario/models.py

WHY: Provides type-safe data structures for BDD scenario generation, ensuring
     consistent representation of Gherkin elements throughout the pipeline.

RESPONSIBILITY: Define immutable data models for BDD scenarios, features, and steps.
                Encapsulates Gherkin structure (Feature/Scenario/Given-When-Then)
                in Python objects for type safety and validation.

PATTERNS:
- Value Object Pattern: Immutable scenario/feature representations
- Data Transfer Object: Carries BDD data between generation and formatting
- Single Responsibility: Only defines data structures, no business logic

Integration:
- Used by ScenarioGenerator to structure LLM output
- Used by GherkinFormatter to format scenarios
- Used by FeatureExtractor to structure requirements
"""

from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field


@dataclass(frozen=True)
class Step:
    """
    Represents a single Gherkin step (Given/When/Then/And/But).

    WHY: Value Object Pattern - immutable representation of test step
         ensures steps cannot be modified after creation, preventing
         accidental state mutations during scenario generation.

    Attributes:
        keyword: Gherkin keyword (Given, When, Then, And, But)
        text: Step description (e.g., "the user is logged in")
        data_table: Optional data table for step (list of dicts)
        doc_string: Optional multiline string for step
    """
    keyword: str
    text: str
    data_table: Optional[List[Dict[str, str]]] = None
    doc_string: Optional[str] = None

    def __post_init__(self):
        """Validate step keyword."""
        valid_keywords = {'Given', 'When', 'Then', 'And', 'But'}
        if self.keyword not in valid_keywords:
            raise ValueError(f"Invalid keyword: {self.keyword}. Must be one of {valid_keywords}")


@dataclass(frozen=True)
class Scenario:
    """
    Represents a single Gherkin scenario.

    WHY: Encapsulates scenario structure for type-safe manipulation.
         Immutable design prevents accidental modifications during
         multi-stage processing (generation -> validation -> formatting).

    Attributes:
        name: Scenario name/description
        steps: List of Gherkin steps (Given/When/Then sequence)
        tags: Optional scenario tags (@smoke, @integration, etc.)
        description: Optional scenario description
        is_outline: Whether this is a Scenario Outline (data-driven)
        examples: Optional examples table for Scenario Outlines
    """
    name: str
    steps: List[Step]
    tags: List[str] = field(default_factory=list)
    description: Optional[str] = None
    is_outline: bool = False
    examples: Optional[List[Dict[str, Any]]] = None

    def __post_init__(self):
        """Validate scenario structure."""
        if not self.name:
            raise ValueError("Scenario name cannot be empty")

        if not self.steps:
            raise ValueError("Scenario must have at least one step")

        if self.is_outline and not self.examples:
            raise ValueError("Scenario Outline must have examples table")

    @property
    def has_given_step(self) -> bool:
        """Check if scenario has Given step (setup)."""
        return any(step.keyword == 'Given' for step in self.steps)

    @property
    def has_when_step(self) -> bool:
        """Check if scenario has When step (action)."""
        return any(step.keyword == 'When' for step in self.steps)

    @property
    def has_then_step(self) -> bool:
        """Check if scenario has Then step (assertion)."""
        return any(step.keyword == 'Then' for step in self.steps)


@dataclass(frozen=True)
class Feature:
    """
    Represents a complete Gherkin feature file.

    WHY: Top-level container for BDD scenarios. Feature represents
         a cohesive set of related scenarios testing a specific
         business capability.

    Attributes:
        name: Feature name/title
        description: Feature description (As a/I want/So that format)
        scenarios: List of scenarios in this feature
        tags: Optional feature-level tags
        background: Optional background steps (run before each scenario)
    """
    name: str
    description: str
    scenarios: List[Scenario]
    tags: List[str] = field(default_factory=list)
    background: Optional[List[Step]] = None

    def __post_init__(self):
        """Validate feature structure."""
        if not self.name:
            raise ValueError("Feature name cannot be empty")

        if not self.scenarios:
            raise ValueError("Feature must have at least one scenario")

    @property
    def scenario_count(self) -> int:
        """Count of scenarios in feature."""
        return len(self.scenarios)

    @property
    def total_steps(self) -> int:
        """Total step count across all scenarios."""
        step_count = sum(len(scenario.steps) for scenario in self.scenarios)
        if self.background:
            step_count += len(self.background)
        return step_count


@dataclass(frozen=True)
class ValidationResult:
    """
    Represents Gherkin validation result.

    WHY: Type-safe validation result prevents boolean blindness.
         Carries both validation status and detailed error information
         for debugging and reporting.

    Attributes:
        valid: Whether validation passed
        errors: List of validation error messages
        warnings: List of validation warnings (non-critical)
    """
    valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    @property
    def has_errors(self) -> bool:
        """Check if validation has errors."""
        return len(self.errors) > 0

    @property
    def has_warnings(self) -> bool:
        """Check if validation has warnings."""
        return len(self.warnings) > 0

    @property
    def error_count(self) -> int:
        """Count of validation errors."""
        return len(self.errors)

    @property
    def warning_count(self) -> int:
        """Count of validation warnings."""
        return len(self.warnings)


@dataclass
class GenerationRequest:
    """
    Request object for scenario generation.

    WHY: Encapsulates all inputs needed for scenario generation
         in single object, reducing parameter count and improving
         testability.

    Attributes:
        card_id: Kanban card identifier
        title: Feature title
        requirements: Structured requirements dictionary
        temperature: LLM temperature (0.0-1.0, default 0.3)
        max_tokens: Maximum tokens for LLM response (default 2000)
        include_examples: Whether to generate Scenario Outlines
        include_edge_cases: Whether to include edge case scenarios
    """
    card_id: str
    title: str
    requirements: Dict[str, Any]
    temperature: float = 0.3
    max_tokens: int = 2000
    include_examples: bool = True
    include_edge_cases: bool = True

    def __post_init__(self):
        """Validate generation request."""
        if not self.card_id:
            raise ValueError("card_id cannot be empty")

        if not self.title:
            raise ValueError("title cannot be empty")

        if not (0.0 <= self.temperature <= 1.0):
            raise ValueError("temperature must be between 0.0 and 1.0")

        if self.max_tokens < 100:
            raise ValueError("max_tokens must be at least 100")


@dataclass
class GenerationResult:
    """
    Result object for scenario generation.

    WHY: Type-safe result object prevents ambiguous return types.
         Encapsulates both success and failure states with detailed
         information for error handling.

    Attributes:
        success: Whether generation succeeded
        content: Generated Gherkin content (if successful)
        feature_path: Path to stored feature file (if successful)
        scenario_count: Number of scenarios generated
        validation: Validation result
        error: Error message (if failed)
    """
    success: bool
    content: Optional[str] = None
    feature_path: Optional[str] = None
    scenario_count: int = 0
    validation: Optional[ValidationResult] = None
    error: Optional[str] = None

    @property
    def is_valid(self) -> bool:
        """Check if generation succeeded and validation passed."""
        return self.success and self.validation is not None and self.validation.valid
