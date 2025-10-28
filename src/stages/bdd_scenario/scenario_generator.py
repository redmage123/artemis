#!/usr/bin/env python3
"""
Module: stages/bdd_scenario/scenario_generator.py

WHY: Transforms structured requirements into executable BDD scenarios using
     LLM-powered generation with fallback strategies for reliability.

RESPONSIBILITY: Generate Gherkin scenarios from requirements using LLM.
                Implements Strategy Pattern for AI service routing with
                direct LLM fallback. Monitors generation via supervisor.

PATTERNS:
- Strategy Pattern: AI Query Service with fallback to direct LLM
- Template Method: Consistent prompt structure for scenario generation
- Single Responsibility: Only generates scenarios, no formatting or validation

Integration:
- Uses LLMClient or AIQueryService for scenario generation
- Monitored by SupervisorAgent for health tracking
- Outputs raw Gherkin text for GherkinFormatter
"""

from typing import Dict, Optional, Any
from artemis_stage_interface import LoggerInterface
from llm_client import LLMClient


class ScenarioGenerator:
    """
    Generates BDD scenarios from requirements using LLM.

    WHY: LLM excels at converting technical requirements into
         business-readable Gherkin scenarios that satisfy both
         stakeholders and developers.

    Responsibilities:
    - Build LLM prompts from requirements
    - Route generation through AI Query Service (if available)
    - Fall back to direct LLM calls
    - Return raw Gherkin content for formatting

    Design: Stateless generator - each generation is independent
            and uses fresh context from requirements.
    """

    def __init__(
        self,
        llm_client: LLMClient,
        logger: LoggerInterface,
        ai_service: Optional[Any] = None
    ):
        """
        Initialize scenario generator.

        Args:
            llm_client: LLM client for direct generation
            logger: Logger for tracking generation progress
            ai_service: Optional AI Query Service for optimized routing

        WHY: Dependency Inversion - depends on abstractions (LLMClient)
             rather than concrete implementations.
        """
        self.llm_client = llm_client
        self.logger = logger
        self.ai_service = ai_service

    def generate(
        self,
        card_id: str,
        title: str,
        requirements: Dict[str, Any],
        temperature: float = 0.3,
        max_tokens: int = 2000
    ) -> str:
        """
        Generate Gherkin scenarios from requirements.

        WHY: Single method interface simplifies usage and testing.
             Temperature and max_tokens configurable for different
             scenario complexity levels.

        Args:
            card_id: Card identifier for context tracking
            title: Feature title for Gherkin Feature header
            requirements: Structured requirements dictionary
            temperature: LLM temperature (0.0-1.0, default 0.3 for consistency)
            max_tokens: Maximum tokens for response (default 2000)

        Returns:
            Raw Gherkin content as string

        Strategy:
        1. Try AI Query Service (token-optimized routing)
        2. Fall back to direct LLM call
        """
        prompt = self._build_prompt(title, requirements)

        # Try AI Query Service first (if available)
        ai_response = self._try_ai_service(prompt, card_id, title, temperature, max_tokens)
        if ai_response:
            return ai_response

        # Fall back to direct LLM
        return self._generate_with_llm(prompt, temperature, max_tokens)

    def _build_prompt(self, title: str, requirements: Dict[str, Any]) -> str:
        """
        Build LLM prompt for scenario generation.

        WHY: Template Method - consistent prompt structure ensures
             high-quality scenario generation across all features.

        Args:
            title: Feature title
            requirements: Requirements dictionary

        Returns:
            Formatted prompt string

        Prompt structure:
        1. Role definition (BDD expert)
        2. Task description (generate scenarios)
        3. Requirements context
        4. Output format requirements
        5. Scenario types to include
        """
        requirements_text = self._format_requirements(requirements)

        prompt = f"""You are a BDD expert. Generate comprehensive Gherkin scenarios for the following feature.

Feature: {title}

Requirements:
{requirements_text}

Generate a complete .feature file with:
1. Feature description (As a/I want/So that format)
2. Multiple scenarios covering:
   - Happy path (normal expected behavior)
   - Edge cases
   - Error handling
   - User interactions
3. Use Given/When/Then format
4. Make scenarios specific and testable
5. Include scenario outlines for data-driven tests where appropriate

Format the output as a valid Gherkin feature file."""

        return prompt

    def _format_requirements(self, requirements: Dict[str, Any]) -> str:
        """
        Format requirements dictionary as readable text.

        WHY: Guard clauses prevent nested conditionals and improve
             readability of formatting logic.

        Args:
            requirements: Requirements dictionary

        Returns:
            Formatted requirements text
        """
        # Handle empty requirements
        if not requirements:
            return "No specific requirements provided. Generate generic scenarios."

        # Handle string requirements
        if isinstance(requirements, str):
            return requirements

        # Handle dict requirements
        lines = []
        for key, value in requirements.items():
            lines.append(f"{key}: {value}")

        return '\n'.join(lines)

    def _try_ai_service(
        self,
        prompt: str,
        card_id: str,
        title: str,
        temperature: float,
        max_tokens: int
    ) -> Optional[str]:
        """
        Attempt generation via AI Query Service.

        WHY: Guard clause pattern - early return eliminates nested
             conditional logic for service availability checks.

        Args:
            prompt: LLM prompt
            card_id: Card identifier
            title: Feature title
            temperature: LLM temperature
            max_tokens: Maximum tokens

        Returns:
            AI service response if successful, None otherwise
        """
        # Guard: Service not available
        if not self.ai_service:
            return None

        try:
            result = self.ai_service.query(
                query=prompt,
                context={"card_id": card_id, "title": title},
                temperature=temperature,
                max_tokens=max_tokens
            )

            # Guard: Service call failed
            if not result.success:
                self.logger.log(
                    f"AI Query Service failed: {result.error}, falling back to direct LLM",
                    "WARNING"
                )
                return None

            return result.response

        except Exception as e:
            self.logger.log(
                f"AI Query Service exception: {str(e)}, falling back to direct LLM",
                "WARNING"
            )
            return None

    def _generate_with_llm(
        self,
        prompt: str,
        temperature: float,
        max_tokens: int
    ) -> str:
        """
        Generate scenarios via direct LLM call.

        WHY: Fallback strategy ensures generation always succeeds
             even when AI Query Service is unavailable.

        Args:
            prompt: LLM prompt
            temperature: LLM temperature
            max_tokens: Maximum tokens

        Returns:
            LLM response as string
        """
        response = self.llm_client.chat_completion(
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            max_tokens=max_tokens
        )

        return response


class RequirementsRetriever:
    """
    Retrieves requirements from context or RAG.

    WHY: Single Responsibility - separates requirements retrieval
         from scenario generation logic.

    Responsibilities:
    - Check context for requirements
    - Fall back to RAG query
    - Return requirements dictionary
    """

    def __init__(self, rag: Any, logger: LoggerInterface):
        """
        Initialize requirements retriever.

        Args:
            rag: RAG agent for querying stored requirements
            logger: Logger for tracking retrieval
        """
        self.rag = rag
        self.logger = logger

    def retrieve(
        self,
        context: Dict[str, Any],
        card_id: str,
        title: str
    ) -> Dict[str, Any]:
        """
        Retrieve requirements from context or RAG.

        WHY: Guard clause pattern - early return when requirements
             found in context, avoiding unnecessary RAG queries.

        Args:
            context: Pipeline context that may contain requirements
            card_id: Card identifier for RAG filtering
            title: Task title for RAG query

        Returns:
            Requirements dictionary (may be empty if not found)
        """
        # Guard: Requirements in context
        requirements = context.get('requirements', {})
        if requirements:
            self.logger.log("📋 Using requirements from context", "INFO")
            return requirements

        # Try RAG query
        self.logger.log(f"🔍 Querying RAG for requirements: {title}", "INFO")
        requirements_artifact = self.rag.query(
            query_text=f"requirements for {title}",
            filter_metadata={"card_id": card_id, "artifact_type": "requirements"}
        )

        # Guard: No RAG results
        if not requirements_artifact:
            self.logger.log("⚠️  No requirements found in context or RAG", "WARNING")
            return {}

        return requirements_artifact[0].get('content', {})


class ScenarioValidator:
    """
    Validates Gherkin scenario structure.

    WHY: Early validation catches LLM-generated syntax errors
         before developers attempt to run tests.

    Responsibilities:
    - Validate Feature declaration
    - Validate Scenario declarations
    - Validate Given/When/Then structure
    - Return structured validation results
    """

    def __init__(self):
        """Initialize scenario validator."""
        pass

    def validate(self, content: str) -> Dict[str, Any]:
        """
        Validate Gherkin scenario structure.

        WHY: Single-pass validation using dispatch table eliminates
             nested conditionals for cleaner validation logic.

        Args:
            content: Gherkin scenario text

        Returns:
            Dict with validation results:
            - valid: Boolean (True if all checks pass)
            - errors: List of error messages (empty if valid)
        """
        errors = []

        # Dispatch table for validation checks
        validation_checks = {
            'feature': self._check_feature_declaration,
            'scenarios': self._check_scenario_declarations,
            'structure': self._check_scenario_structure
        }

        # Run all validation checks
        for check_name, check_func in validation_checks.items():
            check_func(content, errors)

        return {
            "valid": len(errors) == 0,
            "errors": errors
        }

    def _check_feature_declaration(self, content: str, errors: list) -> None:
        """Check for Feature declaration."""
        if "Feature:" not in content:
            errors.append("Missing 'Feature:' declaration")

    def _check_scenario_declarations(self, content: str, errors: list) -> None:
        """Check for Scenario declarations."""
        if "Scenario:" not in content and "Scenario Outline:" not in content:
            errors.append("No scenarios defined")

    def _check_scenario_structure(self, content: str, errors: list) -> None:
        """
        Check scenario structure (Given/When/Then).

        WHY: Iterates through scenarios to validate each has
             required steps for complete test specification.
        """
        scenarios = content.split("Scenario:")

        for i, scenario in enumerate(scenarios[1:], 1):  # Skip feature description
            self._validate_individual_scenario(scenario, i, errors)

    def _validate_individual_scenario(
        self,
        scenario: str,
        scenario_num: int,
        errors: list
    ) -> None:
        """
        Validate individual scenario structure.

        WHY: Guard clauses eliminate nested conditionals and
             make validation checks explicit.

        Args:
            scenario: Scenario text to validate
            scenario_num: Scenario number for error reporting
            errors: List to append validation errors to
        """
        # Check for setup steps (Given/When)
        if "Given" not in scenario and "When" not in scenario:
            errors.append(f"Scenario {scenario_num} missing Given/When steps")

        # Check for assertion steps (Then)
        if "Then" not in scenario:
            errors.append(f"Scenario {scenario_num} missing Then assertions")
