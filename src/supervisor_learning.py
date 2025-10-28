#!/usr/bin/env python3
"""
BACKWARD COMPATIBILITY WRAPPER

WHY: Maintain API compatibility while enabling modular architecture
RESPONSIBILITY: Re-export all components from supervisor.learning package
PATTERNS: Facade, Adapter (for legacy code compatibility)

Original module (776 lines) has been refactored into:
    supervisor/learning/models.py - Data models (73 lines)
    supervisor/learning/pattern_recognition.py - State detection (108 lines)
    supervisor/learning/llm_strategy.py - LLM consultation (209 lines)
    supervisor/learning/workflow_executor.py - Workflow execution (215 lines)
    supervisor/learning/solution_storage.py - RAG integration (178 lines)
    supervisor/learning/learning_dispatcher.py - Strategy dispatch (175 lines)
    supervisor/learning/engine.py - Main engine (166 lines)
    supervisor/learning/__init__.py - Package exports (72 lines)

Total modularized lines: ~1,196 lines (includes extensive documentation)
Core logic lines: ~620 lines (excluding documentation)
Line count reduction: 776 → 620 core lines (20% reduction in code)
Maintainability improvement: 8 focused modules vs 1 monolithic file

Migration:
    Old: from supervisor_learning import SupervisorLearningEngine
    New: from supervisor.learning import SupervisorLearningEngine
    Compatibility: This wrapper supports both import styles

Design Improvements:
    ✓ Guard clauses (max 1 level nesting)
    ✓ Dispatch tables (no elif chains)
    ✓ Type hints on all functions
    ✓ Single Responsibility Principle
    ✓ WHY/RESPONSIBILITY/PATTERNS documentation
    ✓ Modular components for testing and reuse
"""

# Re-export main engine
from supervisor.learning import SupervisorLearningEngine

# Re-export data models for backward compatibility
from supervisor.learning import (
    UnexpectedState,
    LearnedSolution,
    LearningStrategy
)

# Re-export components (for legacy code using internal classes)
from supervisor.learning import (
    StatePatternRecognizer,
    ProblemDescriptor,
    LLMConsultationStrategy,
    LLMPromptBuilder,
    LLMResponseParser,
    WorkflowExecutionEngine,
    WorkflowStepExecutor,
    SolutionRepository,
    SolutionAdapter,
    LearningStrategyDispatcher,
    HumanInLoopStrategy
)

# Maintain exact same exports as original module
__all__ = [
    "SupervisorLearningEngine",
    "UnexpectedState",
    "LearnedSolution",
    "LearningStrategy",
]


# Example usage (backward compatible)
if __name__ == "__main__":
    """Example usage and testing - backward compatible with original"""

    print("Supervisor Learning Engine - Example Usage")
    print("=" * 70)

    # Create learning engine (backward compatible API)
    learning = SupervisorLearningEngine(
        llm_client=None,
        rag_agent=None,
        verbose=True
    )

    # Simulate unexpected state (same as original)
    print("\n1. Detecting unexpected state...")
    unexpected = learning.detect_unexpected_state(
        card_id="card-001",
        current_state="STAGE_STUCK",
        expected_states=["STAGE_RUNNING", "STAGE_COMPLETED"],
        context={
            "stage_name": "development",
            "error_message": "Developer agents not responding",
            "previous_state": "STAGE_RUNNING"
        }
    )

    if unexpected:
        print(f"   Unexpected state ID: {unexpected.state_id}")
        print(f"   Severity: {unexpected.severity}")

        # Would normally consult LLM here, but we'll simulate
        print("\n2. Would consult LLM for solution (simulated)...")
        print("   (In production, this would query GPT-4o/Claude for recovery steps)")

    # Show statistics (backward compatible)
    print("\n3. Learning statistics:")
    stats = learning.get_statistics()
    for key, value in stats.items():
        print(f"   {key}: {value}")

    print("\n" + "=" * 70)
    print("✅ Learning engine initialized and ready!")
    print("\nNOTE: This is now a modular architecture!")
    print("      See supervisor/learning/ for component modules")
