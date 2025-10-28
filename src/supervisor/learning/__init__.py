"""
WHY: Supervisor learning package - modularized learning components
RESPONSIBILITY: Export public API for supervisor learning system
PATTERNS: Facade (package-level interface)

Package Structure:
    - models: Data structures (UnexpectedState, LearnedSolution, LearningStrategy)
    - pattern_recognition: State detection and severity assessment
    - llm_strategy: LLM-based solution generation
    - workflow_executor: Recovery workflow execution
    - solution_storage: RAG integration and solution persistence
    - learning_dispatcher: Strategy routing and coordination
    - engine: Main learning engine facade

Design:
    - Each module has single responsibility
    - Guard clauses prevent deep nesting
    - Dispatch tables replace elif chains
    - Type hints on all public APIs
    - Comprehensive WHY/RESPONSIBILITY documentation
"""

# Core engine
from .engine import SupervisorLearningEngine

# Data models
from .models import (
    UnexpectedState,
    LearnedSolution,
    LearningStrategy
)

# Components (for advanced usage)
from .pattern_recognition import (
    StatePatternRecognizer,
    ProblemDescriptor
)

from .llm_strategy import (
    LLMConsultationStrategy,
    LLMPromptBuilder,
    LLMResponseParser
)

from .workflow_executor import (
    WorkflowExecutionEngine,
    WorkflowStepExecutor
)

from .solution_storage import (
    SolutionRepository,
    SolutionAdapter
)

from .learning_dispatcher import (
    LearningStrategyDispatcher,
    HumanInLoopStrategy
)

__all__ = [
    # Main engine
    "SupervisorLearningEngine",

    # Data models
    "UnexpectedState",
    "LearnedSolution",
    "LearningStrategy",

    # Pattern recognition
    "StatePatternRecognizer",
    "ProblemDescriptor",

    # LLM strategy
    "LLMConsultationStrategy",
    "LLMPromptBuilder",
    "LLMResponseParser",

    # Workflow execution
    "WorkflowExecutionEngine",
    "WorkflowStepExecutor",

    # Solution storage
    "SolutionRepository",
    "SolutionAdapter",

    # Learning dispatcher
    "LearningStrategyDispatcher",
    "HumanInLoopStrategy",
]
