#!/usr/bin/env python3
"""
WHY: Main learning engine orchestrating all learning components
RESPONSIBILITY: Coordinate state detection, learning, and solution application
PATTERNS: Facade (unified interface), Composition (component assembly)
"""

from typing import Dict, List, Optional, Any

from .models import UnexpectedState, LearnedSolution, LearningStrategy
from .pattern_recognition import StatePatternRecognizer
from .learning_dispatcher import LearningStrategyDispatcher
from .workflow_executor import WorkflowExecutionEngine
from .solution_storage import SolutionRepository


class SupervisorLearningEngine:
    """
    WHY: Provide unified interface for supervisor learning capabilities
    RESPONSIBILITY: Orchestrate detection, learning, and recovery workflows
    PATTERNS: Facade pattern, Composition, Single Responsibility

    Architecture:
        - StatePatternRecognizer: Detects unexpected states
        - LearningStrategyDispatcher: Routes to learning strategies
        - WorkflowExecutionEngine: Executes recovery workflows
        - SolutionRepository: Manages solution persistence

    Integration: Used by RecoveryEngine to handle novel failure modes
    """

    def __init__(
        self,
        llm_client: Optional[Any] = None,
        rag_agent: Optional[Any] = None,
        verbose: bool = True
    ):
        """
        WHY: Initialize learning engine with external dependencies
        RESPONSIBILITY: Setup all component subsystems
        PATTERNS: Dependency Injection, Composition

        Args:
            llm_client: LLM client for querying solutions
            rag_agent: RAG agent for storing/retrieving learned solutions
            verbose: Enable verbose logging
        """
        self.verbose = verbose

        # Initialize components
        self.pattern_recognizer = StatePatternRecognizer(verbose=verbose)
        self.learning_dispatcher = LearningStrategyDispatcher(
            llm_client=llm_client,
            rag_agent=rag_agent,
            verbose=verbose
        )
        self.workflow_engine = WorkflowExecutionEngine(verbose=verbose)
        self.solution_repository = SolutionRepository(
            rag_agent=rag_agent,
            verbose=verbose
        )

        # Statistics
        self.stats = {
            "unexpected_states_detected": 0,
            "solutions_learned": 0,
            "solutions_applied": 0,
            "llm_consultations": 0,
            "successful_applications": 0,
            "failed_applications": 0
        }

    def detect_unexpected_state(
        self,
        card_id: str,
        current_state: str,
        expected_states: List[str],
        context: Dict[str, Any]
    ) -> Optional[UnexpectedState]:
        """
        WHY: Identify when system enters unexpected states
        RESPONSIBILITY: Delegate to pattern recognizer, update stats
        PATTERNS: Facade (delegate to component)

        Args:
            card_id: Card ID
            current_state: Current pipeline state
            expected_states: List of expected states
            context: Context information

        Returns:
            UnexpectedState if detected, None otherwise
        """
        unexpected = self.pattern_recognizer.detect_unexpected_state(
            card_id=card_id,
            current_state=current_state,
            expected_states=expected_states,
            context=context
        )

        if unexpected:
            self.stats["unexpected_states_detected"] += 1

        return unexpected

    def learn_solution(
        self,
        unexpected_state: UnexpectedState,
        strategy: LearningStrategy = LearningStrategy.LLM_CONSULTATION
    ) -> Optional[LearnedSolution]:
        """
        WHY: Generate solution for unexpected state using specified strategy
        RESPONSIBILITY: Delegate to learning dispatcher, update stats
        PATTERNS: Facade (delegate to component)

        Args:
            unexpected_state: The unexpected state
            strategy: Learning strategy to use

        Returns:
            LearnedSolution if generated, None otherwise
        """
        solution = self.learning_dispatcher.learn_solution(
            unexpected_state=unexpected_state,
            strategy=strategy
        )

        if solution:
            self.stats["solutions_learned"] += 1
            # Track LLM consultations
            if solution.learning_strategy == LearningStrategy.LLM_CONSULTATION.value:
                self.stats["llm_consultations"] += 1

        return solution

    def apply_learned_solution(
        self,
        solution: LearnedSolution,
        context: Dict[str, Any]
    ) -> bool:
        """
        WHY: Execute learned solution workflow
        RESPONSIBILITY: Delegate to workflow engine, update stats and repository
        PATTERNS: Facade (delegate to component)

        Args:
            solution: The learned solution
            context: Execution context

        Returns:
            True if solution succeeded
        """
        self.stats["solutions_applied"] += 1

        # Execute workflow
        success = self.workflow_engine.apply_solution(solution, context)

        # Update statistics
        if success:
            self.stats["successful_applications"] += 1
        else:
            self.stats["failed_applications"] += 1

        # Update solution in repository
        self.solution_repository.update_solution(solution)

        return success

    def get_statistics(self) -> Dict[str, Any]:
        """
        WHY: Provide visibility into learning system performance
        RESPONSIBILITY: Aggregate statistics from all components
        PATTERNS: Facade (aggregate from components)

        Returns:
            Dictionary of learning statistics
        """
        return {
            **self.stats,
            "total_learned_solutions": len(self.solution_repository.get_all_solutions()),
            "average_success_rate": self._calculate_average_success_rate(),
            "strategy_usage": self.learning_dispatcher.get_strategy_stats(),
            "workflow_execution": self.workflow_engine.get_stats()
        }

    def _calculate_average_success_rate(self) -> float:
        """
        WHY: Assess overall learning effectiveness
        RESPONSIBILITY: Calculate average success rate across all solutions
        """
        solutions = self.solution_repository.get_all_solutions()

        # Guard: No solutions
        if not solutions:
            return 0.0

        total_rate = sum(s.success_rate for s in solutions)
        return total_rate / len(solutions)

    # Convenience properties for backward compatibility
    @property
    def learned_solutions(self) -> Dict[str, LearnedSolution]:
        """
        WHY: Provide backward-compatible access to solutions
        RESPONSIBILITY: Return solutions as dict
        """
        return self.solution_repository.learned_solutions

    @property
    def llm_client(self) -> Optional[Any]:
        """
        WHY: Provide backward-compatible access to LLM client
        RESPONSIBILITY: Return LLM client reference
        """
        return self.learning_dispatcher.llm_strategy.llm_client

    @property
    def rag_agent(self) -> Optional[Any]:
        """
        WHY: Provide backward-compatible access to RAG agent
        RESPONSIBILITY: Return RAG agent reference
        """
        return self.solution_repository.rag_agent
