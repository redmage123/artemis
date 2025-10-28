#!/usr/bin/env python3
"""
Anti-Hallucination Orchestrator

WHY: Intelligently select validation strategies based on task context
RESPONSIBILITY: Analyze task, assess risk, choose optimal validation combination
PATTERNS: Strategy pattern, Guard clauses, Decision tree

Reduces hallucinations by:
- Applying appropriate validation depth for task complexity
- Avoiding over-validation (waste) and under-validation (risk)
- Adapting to historical failure patterns
- Optimizing for time vs thoroughness tradeoffs
"""

from typing import Dict, List, Optional, Set, Any
from dataclasses import dataclass
from enum import Enum

from artemis_logger import get_logger


class ValidationProfile(Enum):
    """Validation thoroughness profiles."""
    MINIMAL = "minimal"           # Fast, basic checks only
    STANDARD = "standard"         # Balanced validation
    THOROUGH = "thorough"         # Comprehensive validation
    CRITICAL = "critical"         # Maximum validation for critical code


class RiskLevel(Enum):
    """Risk assessment levels."""
    LOW = "low"                   # Simple, non-critical code
    MEDIUM = "medium"             # Moderate complexity/importance
    HIGH = "high"                 # Complex or important code
    CRITICAL = "critical"         # Mission-critical infrastructure


class TaskType(Enum):
    """Type of development task."""
    CODE_GENERATION = "code_generation"
    CODE_REVIEW = "code_review"
    REFACTORING = "refactoring"
    BUG_FIX = "bug_fix"
    FEATURE_ADDITION = "feature_addition"
    DOCUMENTATION = "documentation"
    TESTING = "testing"


@dataclass
class ValidationTechnique:
    """A validation technique that can be applied."""
    name: str
    phase: int                    # 1, 2, or 3
    execution_time_ms: float      # Typical execution time
    hallucination_reduction: float  # 0.0-1.0 effectiveness
    applicable_to: Set[TaskType]  # Which tasks benefit most


@dataclass
class TaskContext:
    """Context about the task to be validated."""
    task_type: TaskType
    code_complexity: int          # Lines of code or complexity score
    is_critical: bool            # Is this critical infrastructure?
    has_tests: bool              # Does code have tests?
    dependencies_count: int      # Number of dependencies
    time_budget_ms: Optional[float] = None  # Optional time constraint


@dataclass
class ValidationStrategy:
    """Selected validation strategy."""
    profile: ValidationProfile
    risk_level: RiskLevel
    techniques: List[str]        # Names of techniques to apply
    estimated_time_ms: float
    expected_reduction: float    # Expected hallucination reduction
    rationale: str              # Why this strategy was chosen


# Available validation techniques
AVAILABLE_TECHNIQUES = {
    # Phase 1: Static Analysis & Property-Based Testing
    "static_analysis": ValidationTechnique(
        name="static_analysis",
        phase=1,
        execution_time_ms=500,
        hallucination_reduction=0.6,
        applicable_to={
            TaskType.CODE_GENERATION,
            TaskType.CODE_REVIEW,
            TaskType.REFACTORING,
            TaskType.BUG_FIX,
            TaskType.FEATURE_ADDITION
        }
    ),
    "property_tests": ValidationTechnique(
        name="property_tests",
        phase=1,
        execution_time_ms=300,
        hallucination_reduction=0.5,
        applicable_to={
            TaskType.CODE_GENERATION,
            TaskType.BUG_FIX,
            TaskType.FEATURE_ADDITION
        }
    ),

    # Phase 3: Symbolic Execution & Formal Specs
    "symbolic_execution": ValidationTechnique(
        name="symbolic_execution",
        phase=3,
        execution_time_ms=1000,
        hallucination_reduction=0.8,
        applicable_to={
            TaskType.CODE_GENERATION,
            TaskType.BUG_FIX,
            TaskType.FEATURE_ADDITION
        }
    ),
    "formal_specs": ValidationTechnique(
        name="formal_specs",
        phase=3,
        execution_time_ms=800,
        hallucination_reduction=0.75,
        applicable_to={
            TaskType.CODE_GENERATION,
            TaskType.CODE_REVIEW,
            TaskType.FEATURE_ADDITION
        }
    ),

    # Other Anti-Hallucination Techniques
    "rag_validation": ValidationTechnique(
        name="rag_validation",
        phase=2,
        execution_time_ms=400,
        hallucination_reduction=0.7,
        applicable_to={
            TaskType.CODE_GENERATION,
            TaskType.CODE_REVIEW,
            TaskType.REFACTORING,
            TaskType.BUG_FIX,
            TaskType.FEATURE_ADDITION
        }
    ),
    "two_pass": ValidationTechnique(
        name="two_pass",
        phase=2,
        execution_time_ms=2000,
        hallucination_reduction=0.85,
        applicable_to={
            TaskType.CODE_GENERATION,
            TaskType.BUG_FIX,
            TaskType.FEATURE_ADDITION
        }
    ),
    "self_consistency": ValidationTechnique(
        name="self_consistency",
        phase=2,
        execution_time_ms=1500,
        hallucination_reduction=0.8,
        applicable_to={
            TaskType.CODE_GENERATION,
            TaskType.BUG_FIX
        }
    ),
    "chain_of_thought": ValidationTechnique(
        name="chain_of_thought",
        phase=2,
        execution_time_ms=200,
        hallucination_reduction=0.4,
        applicable_to={
            TaskType.CODE_GENERATION,
            TaskType.CODE_REVIEW,
            TaskType.REFACTORING,
            TaskType.BUG_FIX,
            TaskType.FEATURE_ADDITION
        }
    ),
    "self_critique": ValidationTechnique(
        name="self_critique",
        phase=2,
        execution_time_ms=600,
        hallucination_reduction=0.65,
        applicable_to={
            TaskType.CODE_GENERATION,
            TaskType.CODE_REVIEW,
            TaskType.BUG_FIX
        }
    ),
}


class AntiHallucinationOrchestrator:
    """
    Intelligently orchestrate anti-hallucination validation strategies.

    WHY: Optimize validation for each specific task
    RESPONSIBILITY: Assess risk, select techniques, execute validation
    PATTERNS: Strategy pattern, Guard clauses, Decision tree
    """

    def __init__(self, logger: Optional[Any] = None):
        """
        Initialize orchestrator.

        Args:
            logger: Optional logger instance
        """
        self.logger = logger or get_logger("anti_hallucination_orchestrator")
        self.techniques = AVAILABLE_TECHNIQUES
        self.historical_failures = {}  # Track what failed before

    def select_strategy(
        self,
        context: TaskContext,
        profile: Optional[ValidationProfile] = None
    ) -> ValidationStrategy:
        """
        Select optimal validation strategy for task.

        WHY: Main entry point for strategy selection
        RESPONSIBILITY: Assess risk, choose techniques, create strategy

        Args:
            context: Task context information
            profile: Optional override for validation profile

        Returns:
            ValidationStrategy with selected techniques
        """
        self.logger.info(f"Selecting validation strategy for {context.task_type.value}")

        # Assess risk level
        risk_level = self._assess_risk(context)
        self.logger.info(f"  Risk level: {risk_level.value}")

        # Determine profile (if not overridden)
        if profile is None:
            profile = self._determine_profile(risk_level, context)

        self.logger.info(f"  Validation profile: {profile.value}")

        # Select techniques based on profile
        techniques = self._select_techniques(profile, risk_level, context)

        # Calculate metrics
        estimated_time = sum(self.techniques[t].execution_time_ms for t in techniques)
        expected_reduction = self._calculate_reduction(techniques)

        # Create rationale
        rationale = self._create_rationale(profile, risk_level, context, techniques)

        return ValidationStrategy(
            profile=profile,
            risk_level=risk_level,
            techniques=techniques,
            estimated_time_ms=estimated_time,
            expected_reduction=expected_reduction,
            rationale=rationale
        )

    def _assess_risk(self, context: TaskContext) -> RiskLevel:
        """
        Assess risk level for task.

        WHY: Risk determines validation depth
        RESPONSIBILITY: Analyze context, return risk level
        PATTERNS: Guard clauses, scoring system
        """
        risk_score = 0

        # Guard: Critical infrastructure
        if context.is_critical:
            return RiskLevel.CRITICAL

        # Complexity scoring - guard clauses from highest to lowest
        if context.code_complexity > 500:
            risk_score += 3
        if context.code_complexity > 200 and context.code_complexity <= 500:
            risk_score += 2
        if context.code_complexity > 50 and context.code_complexity <= 200:
            risk_score += 1

        # Dependency scoring
        if context.dependencies_count > 10:
            risk_score += 2
        elif context.dependencies_count > 5:
            risk_score += 1

        # Test coverage
        if not context.has_tests:
            risk_score += 2

        # Task type risk
        high_risk_tasks = {
            TaskType.BUG_FIX,
            TaskType.REFACTORING,
            TaskType.FEATURE_ADDITION
        }
        if context.task_type in high_risk_tasks:
            risk_score += 1

        # Map score to risk level
        if risk_score >= 6:
            return RiskLevel.HIGH
        if risk_score >= 3:
            return RiskLevel.MEDIUM
        return RiskLevel.LOW

    def _determine_profile(
        self,
        risk_level: RiskLevel,
        context: TaskContext
    ) -> ValidationProfile:
        """
        Determine validation profile based on risk and context.

        WHY: Profile determines validation thoroughness
        RESPONSIBILITY: Map risk to profile
        PATTERNS: Guard clauses, dispatch table
        """
        # Dispatch table for risk → profile mapping
        risk_to_profile = {
            RiskLevel.CRITICAL: ValidationProfile.CRITICAL,
            RiskLevel.HIGH: ValidationProfile.THOROUGH,
            RiskLevel.MEDIUM: ValidationProfile.STANDARD,
            RiskLevel.LOW: ValidationProfile.MINIMAL,
        }

        profile = risk_to_profile[risk_level]

        # Guard: Time budget constraint - downgrade if needed
        if not context.time_budget_ms or context.time_budget_ms >= 1000:
            return profile

        # Downgrade profile due to time constraint
        if profile == ValidationProfile.CRITICAL:
            return ValidationProfile.THOROUGH
        if profile == ValidationProfile.THOROUGH:
            return ValidationProfile.STANDARD

        return profile

    def _select_techniques(
        self,
        profile: ValidationProfile,
        risk_level: RiskLevel,
        context: TaskContext
    ) -> List[str]:
        """
        Select validation techniques for profile.

        WHY: Each profile uses different technique combinations
        RESPONSIBILITY: Return list of technique names
        PATTERNS: Guard clauses, dispatch table
        """
        # Guard: Critical profile - use everything applicable
        if profile == ValidationProfile.CRITICAL:
            return self._select_critical_techniques(context)

        # Guard: Thorough profile - comprehensive validation
        if profile == ValidationProfile.THOROUGH:
            return self._select_thorough_techniques(context)

        # Guard: Standard profile - balanced validation
        if profile == ValidationProfile.STANDARD:
            return self._select_standard_techniques(context)

        # Minimal profile - essential only
        return self._select_minimal_techniques(context)

    def _select_critical_techniques(self, context: TaskContext) -> List[str]:
        """Select techniques for CRITICAL profile."""
        techniques = []

        # Always include
        techniques.append("chain_of_thought")  # Always helpful
        techniques.append("static_analysis")   # Essential baseline

        # Add all applicable Phase 3 techniques
        if self._is_applicable("symbolic_execution", context):
            techniques.append("symbolic_execution")
        if self._is_applicable("formal_specs", context):
            techniques.append("formal_specs")

        # Add high-value Phase 2 techniques
        if self._is_applicable("two_pass", context):
            techniques.append("two_pass")
        if self._is_applicable("self_consistency", context):
            techniques.append("self_consistency")
        if self._is_applicable("rag_validation", context):
            techniques.append("rag_validation")

        # Add remaining applicable techniques
        if self._is_applicable("property_tests", context):
            techniques.append("property_tests")
        if self._is_applicable("self_critique", context):
            techniques.append("self_critique")

        return techniques

    def _select_thorough_techniques(self, context: TaskContext) -> List[str]:
        """Select techniques for THOROUGH profile."""
        techniques = []

        # Core techniques
        techniques.append("chain_of_thought")
        techniques.append("static_analysis")

        # Add Phase 3 if applicable
        if self._is_applicable("symbolic_execution", context):
            techniques.append("symbolic_execution")
        if self._is_applicable("formal_specs", context):
            techniques.append("formal_specs")

        # Add high-value Phase 2
        if self._is_applicable("rag_validation", context):
            techniques.append("rag_validation")
        if self._is_applicable("self_critique", context):
            techniques.append("self_critique")

        # Add Phase 1
        if self._is_applicable("property_tests", context):
            techniques.append("property_tests")

        return techniques

    def _select_standard_techniques(self, context: TaskContext) -> List[str]:
        """Select techniques for STANDARD profile."""
        techniques = []

        # Essential techniques
        techniques.append("chain_of_thought")
        techniques.append("static_analysis")

        # Add one Phase 3 technique if applicable
        if self._is_applicable("formal_specs", context):
            techniques.append("formal_specs")
        elif self._is_applicable("symbolic_execution", context):
            techniques.append("symbolic_execution")

        # Add RAG validation
        if self._is_applicable("rag_validation", context):
            techniques.append("rag_validation")

        # Add property tests for code generation
        if context.task_type == TaskType.CODE_GENERATION:
            if self._is_applicable("property_tests", context):
                techniques.append("property_tests")

        return techniques

    def _select_minimal_techniques(self, context: TaskContext) -> List[str]:
        """Select techniques for MINIMAL profile."""
        techniques = []

        # Essential only
        techniques.append("chain_of_thought")

        # Guard: Code tasks get static analysis
        if context.task_type in {
            TaskType.CODE_GENERATION,
            TaskType.CODE_REVIEW,
            TaskType.BUG_FIX
        }:
            techniques.append("static_analysis")

        return techniques

    def _is_applicable(self, technique_name: str, context: TaskContext) -> bool:
        """Check if technique is applicable to task."""
        technique = self.techniques.get(technique_name)
        # Guard: Technique not found
        if not technique:
            return False

        return context.task_type in technique.applicable_to

    def _calculate_reduction(self, techniques: List[str]) -> float:
        """
        Calculate expected hallucination reduction.

        WHY: Estimate effectiveness of strategy
        RESPONSIBILITY: Combine technique effectiveness scores
        PATTERNS: Probabilistic combination
        """
        # Guard: No techniques
        if not techniques:
            return 0.0

        # Combine using probabilistic independence
        # P(success) = 1 - P(all fail)
        # P(all fail) = product of (1 - P(each success))
        prob_all_fail = 1.0
        for name in techniques:
            technique = self.techniques.get(name)
            if technique:
                prob_all_fail *= (1.0 - technique.hallucination_reduction)

        return 1.0 - prob_all_fail

    def _create_rationale(
        self,
        profile: ValidationProfile,
        risk_level: RiskLevel,
        context: TaskContext,
        techniques: List[str]
    ) -> str:
        """Create human-readable rationale for strategy."""
        lines = []

        # Risk assessment
        lines.append(f"Risk: {risk_level.value.upper()}")

        # Risk factors
        factors = []
        if context.is_critical:
            factors.append("critical infrastructure")
        if context.code_complexity > 200:
            factors.append("high complexity")
        if context.dependencies_count > 5:
            factors.append("many dependencies")
        if not context.has_tests:
            factors.append("no tests")

        if factors:
            lines.append(f"Factors: {', '.join(factors)}")

        # Profile selection
        lines.append(f"Profile: {profile.value.upper()}")

        # Techniques
        lines.append(f"Techniques: {', '.join(techniques)}")

        # Time estimate
        estimated_time = sum(self.techniques[t].execution_time_ms for t in techniques)
        lines.append(f"Estimated time: {estimated_time:.0f}ms")

        return " | ".join(lines)

    def record_failure(
        self,
        task_type: TaskType,
        failed_technique: str,
        error_pattern: str
    ) -> None:
        """
        Record validation failure for future learning.

        WHY: Learn from failures to improve future selections
        RESPONSIBILITY: Store failure pattern
        """
        key = (task_type, error_pattern)
        if key not in self.historical_failures:
            self.historical_failures[key] = []

        self.historical_failures[key].append(failed_technique)
        self.logger.info(f"Recorded failure: {failed_technique} for {task_type.value}")

    def get_recommended_techniques(
        self,
        task_type: TaskType,
        error_pattern: Optional[str] = None
    ) -> List[str]:
        """
        Get recommended techniques based on historical data.

        WHY: Learn from past failures
        RESPONSIBILITY: Return techniques that caught similar issues
        """
        # Guard: No historical data
        if not error_pattern:
            return []

        key = (task_type, error_pattern)
        return self.historical_failures.get(key, [])
