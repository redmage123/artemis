"""
WHY: Provide backward compatibility wrapper for existing code.
RESPONSIBILITY: Redirect to new modular prompt_management package.
PATTERNS: Facade pattern, deprecation wrapper.

BACKWARD COMPATIBILITY WRAPPER
================================

This module maintains backward compatibility with existing code that
imports from prompt_manager.py. All functionality has been moved to
the modular prompt_management/ package.

Usage (Legacy - Still Supported):
    from prompt_manager import PromptManager, PromptTemplate

Usage (New - Recommended):
    from prompt_management import PromptManager, PromptTemplate

The legacy imports will continue to work, but new code should use
the prompt_management package directly.

DEPTH Framework:
- D: Define Multiple Perspectives
- E: Establish Clear Success Metrics
- P: Provide Context Layers
- T: Task Breakdown
- H: Human Feedback Loop (Self-Critique)
"""

# Import shared coding standards for create_default_prompts function
from coding_standards import CODING_STANDARDS_ALL_LANGUAGES

# Re-export everything from prompt_management package
from prompt_management import (
    # Main facade
    PromptManager,

    # Data models
    PromptTemplate,
    PromptContext,
    RenderedPrompt,
    ReasoningStrategyType,

    # Components (for advanced usage)
    TemplateLoader,
    VariableSubstitutor,
    PromptFormatter,
    PromptBuilder,
    PromptBuilderFactory,
    PromptRepository,
)

# Re-export types
from typing import Dict, List, Optional, Any


# ============================================================================
# EXAMPLE PROMPTS WITH DEPTH FRAMEWORK
# ============================================================================

def create_default_prompts(prompt_manager: PromptManager):
    """
    WHY: Create default prompts for Artemis agents with DEPTH framework.
    RESPONSIBILITY: Initialize system with standard prompt templates.
    PATTERNS: Factory function for default data.

    Create default prompts for Artemis agents with DEPTH framework applied.
    This function is preserved for backward compatibility.

    Args:
        prompt_manager: PromptManager instance
    """

    # 1. Developer Agent - Conservative Implementation
    prompt_manager.store_prompt(
        name="developer_conservative_implementation",
        category="developer_agent",
        perspectives=[
            "Senior Software Engineer with 15+ years focusing on reliability and maintainability",
            "QA Engineer who prioritizes testability and edge case handling",
            "Tech Lead who reviews code for SOLID principles and best practices"
        ],
        success_metrics=[
            "Code compiles without syntax errors",
            "Returns valid JSON matching expected schema",
            "Includes comprehensive unit tests (85%+ coverage)",
            "Follows SOLID principles (validated against checklist)",
            "No generic AI clichés like 'robust', 'delve into', 'leverage'",
            "Clear, production-ready implementation (not placeholder code)"
        ],
        context_layers={
            "developer_type": "conservative",
            "approach": "Proven patterns, stability over innovation",
            "code_quality": "Production-ready, battle-tested solutions",
            "testing": "TDD with comprehensive test coverage",
            "principles": "SOLID, DRY, KISS, YAGNI"
        },
        task_breakdown=[
            "Analyze the task requirements and ADR architectural decisions",
            "Identify all edge cases and error conditions that need handling",
            "Design the solution using proven design patterns",
            "Write failing tests first (TDD approach)",
            "Implement the solution to make tests pass",
            "Refactor for SOLID principles and code clarity",
            "Self-validate: Check JSON format, test coverage, and code quality"
        ],
        self_critique="""Before responding, validate your implementation:
1. Does the JSON parse without errors?
2. Are all required fields present in the JSON response?
3. Is test coverage >= 85%?
4. Did you avoid AI clichés and generic language?
5. Is this production-ready code (not TODO placeholders)?
6. Does it follow SOLID principles?

If any answer is NO, revise your implementation.""",
        system_message=f"""You are {{developer_name}}, a conservative senior software developer with 15+ years of experience.

Your core principles:
- Stability and reliability over clever tricks
- Proven patterns over experimental approaches
- Comprehensive testing and error handling
- SOLID principles strictly applied
- Production-ready code (no TODOs or placeholders)

{CODING_STANDARDS_ALL_LANGUAGES}

**NOTEBOOK TASKS:**
If the task requires creating Jupyter notebooks (.ipynb files):
- Create notebooks in notebooks/ directory
- Focus on content quality, visualizations, and narrative
- Do NOT create pytest tests for notebook tasks
- Validation checks notebook structure only (valid JSON, cells exist)
- Optional: Create src/ directory only if notebook needs helper modules
- Tests field can be null or minimal for notebook deliverables

You MUST respond with valid JSON only - no explanations, no markdown, just pure JSON.""",
        user_template="""Implement the following task:

**Task:** {task_title}

**Architecture Decision (ADR):**
{adr_content}

**Code Review Feedback (if available):**
{code_review_feedback}

**Response Format:**
Return a JSON object with this exact structure:
{{
  "approach": "Brief description of your approach",
  "implementation": {{
    "filename": "your_solution.py",
    "content": "Complete implementation code"
  }},
  "tests": {{
    "filename": "test_your_solution.py",
    "content": "Complete test code"
  }},
  "explanation": "Brief explanation of key decisions"
}}""",
        tags=["developer", "conservative", "production-ready", "TDD"],
        version="1.0"
    )

    print("[PromptManager] Created default prompts with DEPTH framework")


# ============================================================================
# EXAMPLE USAGE (for backward compatibility)
# ============================================================================

if __name__ == "__main__":
    # Example usage - demonstrates backward compatibility
    from rag_agent import RAGAgent

    rag = RAGAgent(db_path="db", verbose=True)
    pm = PromptManager(rag, verbose=True)

    # Create default prompts
    create_default_prompts(pm)

    # Retrieve and render a prompt
    prompt = pm.get_prompt("developer_conservative_implementation")
    if prompt:
        rendered = pm.render_prompt(prompt, {
            "developer_name": "developer-a",
            "task_title": "Create user authentication module",
            "adr_content": "Use JWT tokens with RS256 signing...",
            "code_review_feedback": "No previous feedback"
        })

        print("\n" + "=" * 70)
        print("RENDERED PROMPT:")
        print("=" * 70)
        print("\nSYSTEM MESSAGE:")
        print(rendered["system"])
        print("\nUSER MESSAGE:")
        print(rendered["user"][:500] + "...")


# Export all public symbols
__all__ = [
    # Main facade
    'PromptManager',

    # Data models
    'PromptTemplate',
    'PromptContext',
    'RenderedPrompt',
    'ReasoningStrategyType',

    # Components
    'TemplateLoader',
    'VariableSubstitutor',
    'PromptFormatter',
    'PromptBuilder',
    'PromptBuilderFactory',
    'PromptRepository',

    # Helper functions
    'create_default_prompts',
]
