#!/usr/bin/env python3
"""
WHY: Orchestrate self-critique validation workflow.

RESPONSIBILITY:
- Coordinate all validation components (generator, analyzer, checker, processor)
- Execute validation workflow in correct sequence
- Aggregate results into CritiqueResult
- Provide factory for configured validators

PATTERNS:
- Facade Pattern: Unified interface to complex subsystem
- Strategy Pattern: Configurable critique levels and modes
- Factory Pattern: Create configured validators
- Template Method: Fixed workflow with pluggable strategies
"""

import logging
from typing import Dict, Any, Optional

from .models import CritiqueLevel, CritiqueResult
from .critique_generator import CritiqueGenerator
from .validation_checker import ValidationChecker
from .feedback_processor import FeedbackProcessor
from .improvement_suggester import UncertaintyAnalyzer, CitationTracker


class SelfCritiqueValidator:
    """
    WHY: Main self-critique validator orchestrating validation workflow.

    RESPONSIBILITY:
    - Coordinate critique generation, analysis, and validation
    - Execute validation steps in proper sequence
    - Aggregate all results into CritiqueResult
    - Provide clean API for validation clients
    """

    def __init__(
        self,
        llm_client: Any,
        level: CritiqueLevel = CritiqueLevel.BALANCED,
        strict_mode: bool = False,
        rag_agent: Optional[Any] = None,
        logger: Optional[logging.Logger] = None
    ):
        """
        Initialize self-critique validator.

        Args:
            llm_client: LLM client for generating critiques
            level: Depth of critique analysis
            strict_mode: If True, fail on warnings; if False, only fail on errors
            rag_agent: Optional RAG agent for citation verification
            logger: Optional logger
        """
        self.llm_client = llm_client
        self.level = level
        self.strict_mode = strict_mode
        self.logger = logger or logging.getLogger(__name__)

        # Initialize components
        self.critique_generator = CritiqueGenerator(llm_client, level, self.logger)
        self.validation_checker = ValidationChecker(strict_mode, self.logger)
        self.feedback_processor = FeedbackProcessor(strict_mode, self.logger)
        self.uncertainty_analyzer = UncertaintyAnalyzer(self.logger)
        self.citation_tracker = CitationTracker(rag_agent, self.logger)

    def validate_code(
        self,
        code: str,
        context: Dict[str, Any],
        original_prompt: str = ""
    ) -> CritiqueResult:
        """
        Validate code using self-critique workflow.

        Args:
            code: Generated code to validate
            context: Context (language, framework, requirements)
            original_prompt: Original prompt that generated this code

        Returns:
            CritiqueResult with validation results
        """
        self.logger.info(f"Starting self-critique validation (level={self.level.value})")

        # Step 1: Generate self-critique from LLM
        raw_critique = self.critique_generator.generate_critique(code, context, original_prompt)

        # Step 2: Parse critique into structured findings
        findings = self.critique_generator.parse_critique(raw_critique)

        # Step 3: Extract confidence score
        confidence_score = self.critique_generator.extract_confidence_score(raw_critique)

        # Step 4: Analyze code uncertainty
        uncertainty_metrics = self.uncertainty_analyzer.analyze(code)

        # Step 5: Extract code citations
        citations = self.citation_tracker.extract_citations(code, context)

        # Step 6: Determine if regeneration is needed
        regeneration_needed, feedback = self.feedback_processor.should_regenerate(
            findings, uncertainty_metrics, confidence_score
        )

        # Step 7: Determine pass/fail status
        passed = self.validation_checker.determine_pass_fail(findings, regeneration_needed)

        # Step 8: Create and return result
        return CritiqueResult(
            passed=passed,
            confidence_score=confidence_score,
            findings=findings,
            uncertainty_metrics=uncertainty_metrics,
            citations=citations,
            raw_critique=raw_critique,
            regeneration_needed=regeneration_needed,
            feedback=feedback
        )


class SelfCritiqueFactory:
    """
    WHY: Create configured self-critique validators for different environments.

    RESPONSIBILITY:
    - Map environment names to critique levels
    - Create validators with appropriate configurations
    - Provide sensible defaults per environment
    """

    # Dispatch table for environment configurations
    _LEVEL_CONFIGS: Dict[str, CritiqueLevel] = {
        'development': CritiqueLevel.BALANCED,
        'testing': CritiqueLevel.THOROUGH,
        'production': CritiqueLevel.THOROUGH,
        'prototype': CritiqueLevel.QUICK
    }

    @staticmethod
    def create_validator(
        llm_client: Any,
        environment: str = 'development',
        strict_mode: bool = False,
        rag_agent: Optional[Any] = None,
        logger: Optional[logging.Logger] = None
    ) -> SelfCritiqueValidator:
        """
        Create configured self-critique validator.

        Args:
            llm_client: LLM client
            environment: 'development', 'testing', 'production', 'prototype'
            strict_mode: Fail on warnings
            rag_agent: Optional RAG agent
            logger: Optional logger

        Returns:
            Configured SelfCritiqueValidator
        """
        # Guard clause: Use default level if environment not recognized
        level = SelfCritiqueFactory._LEVEL_CONFIGS.get(
            environment,
            CritiqueLevel.BALANCED
        )

        return SelfCritiqueValidator(
            llm_client=llm_client,
            level=level,
            strict_mode=strict_mode,
            rag_agent=rag_agent,
            logger=logger
        )
