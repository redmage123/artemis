#!/usr/bin/env python3
"""
WHY: Route learning requests to appropriate strategies
RESPONSIBILITY: Dispatch to LLM, similar case, or human-in-loop strategies
PATTERNS: Strategy pattern, Dispatch Table, Chain of Responsibility
"""

from typing import Dict, Optional, Any, Callable

from .models import UnexpectedState, LearnedSolution, LearningStrategy
from .llm_strategy import LLMConsultationStrategy
from .solution_storage import SolutionRepository, SolutionAdapter


class HumanInLoopStrategy:
    """
    WHY: Handle cases requiring human intervention
    RESPONSIBILITY: Request and process human guidance
    PATTERNS: Strategy pattern
    """

    def __init__(self, verbose: bool = True):
        self.verbose = verbose

    def request_human_guidance(
        self,
        unexpected_state: UnexpectedState
    ) -> Optional[LearnedSolution]:
        """
        WHY: Escalate to human when automated learning fails
        RESPONSIBILITY: Log human intervention request
        PATTERNS: Guard Clause

        Args:
            unexpected_state: State requiring human guidance

        Returns:
            None (human intervention required)
        """
        if self.verbose:
            print(f"[Learning] 👤 Requesting human guidance...")
            print(f"[Learning]    Problem: {self._describe_problem(unexpected_state)}")

        # In production, would integrate with human-in-the-loop system
        return None

    def _describe_problem(self, unexpected_state: UnexpectedState) -> str:
        """Generate problem description"""
        from .pattern_recognition import ProblemDescriptor
        return ProblemDescriptor.describe_problem(unexpected_state)


class LearningStrategyDispatcher:
    """
    WHY: Route learning requests to appropriate strategies
    RESPONSIBILITY: Select and execute best learning strategy for each case
    PATTERNS: Strategy pattern, Dispatch Table, Chain of Responsibility
    """

    def __init__(
        self,
        llm_client: Optional[Any] = None,
        rag_agent: Optional[Any] = None,
        verbose: bool = True
    ):
        self.verbose = verbose

        # Initialize strategy components
        self.llm_strategy = LLMConsultationStrategy(llm_client=llm_client, verbose=verbose)
        self.solution_repository = SolutionRepository(rag_agent=rag_agent, verbose=verbose)
        self.solution_adapter = SolutionAdapter(verbose=verbose)
        self.human_strategy = HumanInLoopStrategy(verbose=verbose)

        # Build strategy dispatch table
        self._strategy_handlers = self._build_strategy_handlers()

        # Statistics
        self.strategy_usage = {
            LearningStrategy.LLM_CONSULTATION.value: 0,
            LearningStrategy.SIMILAR_CASE_ADAPTATION.value: 0,
            LearningStrategy.HUMAN_IN_LOOP.value: 0,
            LearningStrategy.EXPERIMENTAL_TRIAL.value: 0,
        }

    def _build_strategy_handlers(self) -> Dict[LearningStrategy, Callable]:
        """
        WHY: Avoid elif chains for strategy selection
        RESPONSIBILITY: Map strategy types to handler methods
        PATTERNS: Dispatch Table
        """
        return {
            LearningStrategy.LLM_CONSULTATION: self._handle_llm_consultation,
            LearningStrategy.SIMILAR_CASE_ADAPTATION: self._handle_similar_case,
            LearningStrategy.HUMAN_IN_LOOP: self._handle_human_in_loop,
            LearningStrategy.EXPERIMENTAL_TRIAL: self._handle_experimental,
        }

    def learn_solution(
        self,
        unexpected_state: UnexpectedState,
        strategy: LearningStrategy = LearningStrategy.LLM_CONSULTATION
    ) -> Optional[LearnedSolution]:
        """
        WHY: Generate solutions using specified learning strategy
        RESPONSIBILITY: Route to appropriate strategy handler
        PATTERNS: Dispatch Table, Strategy pattern

        Args:
            unexpected_state: The unexpected state
            strategy: Learning strategy to use

        Returns:
            LearnedSolution if found, None otherwise
        """
        if self.verbose:
            print(f"[Learning] 🧠 Learning solution using strategy: {strategy.value}")

        # Update statistics
        self.strategy_usage[strategy.value] += 1

        # Get handler from dispatch table
        handler = self._strategy_handlers.get(strategy, self._handle_llm_consultation)

        # Execute strategy
        return handler(unexpected_state)

    def _handle_llm_consultation(
        self,
        unexpected_state: UnexpectedState
    ) -> Optional[LearnedSolution]:
        """
        WHY: Generate novel solutions using LLM
        RESPONSIBILITY: Consult LLM and store solution
        PATTERNS: Strategy pattern
        """
        solution = self.llm_strategy.consult_llm_for_solution(unexpected_state)

        # Guard: LLM consultation failed
        if not solution:
            return None

        # Store in repository
        self.solution_repository.store_solution(solution, unexpected_state)

        return solution

    def _handle_similar_case(
        self,
        unexpected_state: UnexpectedState
    ) -> Optional[LearnedSolution]:
        """
        WHY: Adapt from similar past solutions
        RESPONSIBILITY: Find and adapt similar cases
        PATTERNS: Strategy pattern, Guard Clause
        """
        # Find similar solutions
        similar_solutions = self.solution_repository.find_similar_solutions(unexpected_state)

        # Guard: No similar solutions found
        if not similar_solutions:
            if self.verbose:
                print(f"[Learning] ℹ️  No similar cases found, falling back to LLM")
            # Fallback to LLM consultation
            return self._handle_llm_consultation(unexpected_state)

        # Adapt from most similar solution
        solution = self.solution_adapter.adapt_from_similar(
            unexpected_state,
            similar_solutions[0]
        )

        # Store adapted solution
        self.solution_repository.store_solution(solution, unexpected_state)

        return solution

    def _handle_human_in_loop(
        self,
        unexpected_state: UnexpectedState
    ) -> Optional[LearnedSolution]:
        """
        WHY: Escalate complex cases to humans
        RESPONSIBILITY: Request human guidance
        PATTERNS: Strategy pattern
        """
        return self.human_strategy.request_human_guidance(unexpected_state)

    def _handle_experimental(
        self,
        unexpected_state: UnexpectedState
    ) -> Optional[LearnedSolution]:
        """
        WHY: Try experimental recovery approaches
        RESPONSIBILITY: Placeholder for experimental strategies
        PATTERNS: Strategy pattern
        """
        if self.verbose:
            print(f"[Learning] 🧪 Experimental strategy not yet implemented")
        # Fallback to LLM
        return self._handle_llm_consultation(unexpected_state)

    def get_strategy_stats(self) -> Dict[str, int]:
        """
        WHY: Track which strategies are most used
        RESPONSIBILITY: Return strategy usage statistics
        """
        return self.strategy_usage.copy()
