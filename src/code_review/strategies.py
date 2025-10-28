#!/usr/bin/env python3
"""
WHY: Code Review Strategy Management
RESPONSIBILITY: Build prompts and context for different review types
PATTERNS: Strategy pattern, builder pattern, dispatch tables
"""

from typing import Dict, List, Any, Optional
from pathlib import Path

from llm_client import LLMMessage
from review_request_builder import ImplementationFile
from environment_context import get_environment_context_short
from artemis_exceptions import FileReadError, wrap_exception


def build_base_review_prompt(
    review_prompt: str,
    implementation_files: List[ImplementationFile],
    task_title: str,
    task_description: str
) -> str:
    """
    Build base review prompt without KG context (AIQueryService will add it).

    WHY: Separate base prompt construction from AI service enhancement.
    RESPONSIBILITY: Assemble all context into prompt format.
    PATTERN: Template method.

    Args:
        review_prompt: System prompt for code review
        implementation_files: List of ImplementationFile objects
        task_title: Task title
        task_description: Task description

    Returns:
        Complete base prompt string
    """
    files_content = "\n\n".join(
        f"## File: {file.path}\n```{file.language}\n{file.content}\n```"
        for file in implementation_files
    )

    return f"""{review_prompt}

**Task**: {task_title}
**Description**: {task_description}

{get_environment_context_short()}

**Implementation Files**:
{files_content}

Perform a comprehensive code review and return results in JSON format."""


def build_review_request_legacy(prompt: str) -> List[LLMMessage]:
    """
    Legacy review request builder for fallback.

    WHY: Backward compatibility when AI service unavailable.
    RESPONSIBILITY: Create simple message structure.
    PATTERN: Fallback strategy.

    Args:
        prompt: Complete prompt text

    Returns:
        List of LLM messages
    """
    return [
        LLMMessage(role="system", content="You are an expert code reviewer."),
        LLMMessage(role="user", content=prompt)
    ]


def extract_file_types(implementation_files: List[ImplementationFile]) -> List[str]:
    """
    Extract file types for KG query.

    WHY: Knowledge graph needs language types for pattern matching.
    RESPONSIBILITY: Map file extensions to language types.
    PATTERN: Dispatch table for extension mapping.

    Args:
        implementation_files: List of implementation files

    Returns:
        List of unique language types
    """
    # Dispatch table: Map file extensions to language types
    extension_map = {
        '.py': 'python',
        '.js': 'javascript',
        '.jsx': 'javascript',
        '.ts': 'javascript',
        '.tsx': 'javascript',
        '.java': 'java',
        '.go': 'go',
        '.rb': 'ruby',
        '.php': 'php',
        '.cs': 'csharp',
        '.cpp': 'cpp',
        '.c': 'c',
        '.rs': 'rust'
    }

    # Use set comprehension to extract unique file types
    file_types = {
        extension_map[ext]
        for file in implementation_files
        for ext in extension_map
        if file.path.endswith(ext)
    }

    return list(file_types)


def enhance_messages_with_kg_context(
    messages: List[LLMMessage],
    kg_context: Dict[str, Any]
) -> None:
    """
    Enhance messages with Knowledge Graph context.

    WHY: Extracted to avoid nested if in build_review_request.
    RESPONSIBILITY: Add KG hints to user message.
    PATTERN: Message mutation (in-place enhancement).

    Args:
        messages: List of LLM messages to enhance (modified in place)
        kg_context: Knowledge Graph context with common issues
    """
    if not messages or len(messages) <= 1:
        return

    if not kg_context.get('common_issues'):
        return

    kg_hints = build_kg_hints_section(kg_context)

    # Append KG hints to user message
    messages[-1] = LLMMessage(
        role="user",
        content=messages[-1].content + kg_hints
    )


def build_kg_hints_section(kg_context: Dict[str, Any]) -> str:
    """
    Build KG hints section for prompt enhancement.

    WHY: Extracted to avoid string concatenation in enhance_messages_with_kg_context.
    RESPONSIBILITY: Format KG patterns as markdown hints.
    PATTERN: Template method.

    Args:
        kg_context: Knowledge Graph context with common issues

    Returns:
        Formatted KG hints section
    """
    kg_hints = "\n\n**Knowledge Graph Context - Known Issue Patterns:**\n"
    kg_hints += f"Based on {kg_context['similar_reviews_count']} similar reviews, focus on:\n"

    for issue in kg_context['common_issues'][:5]:
        kg_hints += f"- {issue['category']}: {issue['pattern']}\n"

    kg_hints += "\nPrioritize these patterns in your review.\n"

    return kg_hints


def read_review_prompt(
    prompt_manager: Optional[Any],
    logger: Optional[Any] = None
) -> str:
    """
    Read the code review agent prompt from RAG or fallback to file.

    WHY: Centralized prompt loading with RAG fallback.
    RESPONSIBILITY: Try RAG first, then file system.
    PATTERN: Chain of responsibility.

    Args:
        prompt_manager: PromptManager instance (optional)
        logger: Logger instance (optional)

    Returns:
        Code review prompt string

    Raises:
        FileReadError: If prompt cannot be loaded
    """
    # Try to get prompt from RAG first
    if prompt_manager:
        rag_prompt = try_load_rag_prompt(prompt_manager, logger)
        if rag_prompt:
            return rag_prompt

    # Fallback to reading from file
    return load_prompt_from_file(logger)


def try_load_rag_prompt(prompt_manager: Any, logger: Optional[Any]) -> Optional[str]:
    """
    Try to load prompt from RAG.

    WHY: Extracted to avoid nested if in read_review_prompt.
    RESPONSIBILITY: RAG prompt loading with error handling.
    PATTERN: Try-except with early return.

    Args:
        prompt_manager: PromptManager instance
        logger: Optional logger

    Returns:
        Prompt string if successful, None otherwise
    """
    try:
        if logger:
            logger.info("📝 Loading code review prompt from RAG")

        prompt_template = prompt_manager.get_prompt("code_review_analysis")

        if not prompt_template:
            return None

        # Render the prompt (no variables needed for system message)
        rendered = prompt_manager.render_prompt(
            prompt=prompt_template,
            variables={}
        )

        if logger:
            logger.info(f"✅ Loaded RAG prompt with {len(prompt_template.perspectives)} perspectives")

        # Return combined system and user template
        return f"{rendered['system']}\n\n{rendered['user']}"

    except Exception as e:
        if logger:
            logger.warning(f"⚠️  Error loading RAG prompt: {e} - falling back to file")
        return None


def load_prompt_from_file(logger: Optional[Any] = None) -> str:
    """
    Load prompt from file system.

    WHY: Extracted to avoid nested if in read_review_prompt.
    RESPONSIBILITY: File-based prompt loading.
    PATTERN: Guard clauses for validation.

    Args:
        logger: Optional logger

    Returns:
        Prompt string from file

    Raises:
        FileReadError: If prompt file cannot be read
    """
    prompt_file = Path(__file__).parent.parent / "prompts" / "code_review_agent_prompt.md"

    if not prompt_file.exists():
        raise FileReadError(
            f"Code review prompt not found: {prompt_file}",
            context={"prompt_file": str(prompt_file)}
        )

    try:
        if logger:
            logger.info("📝 Loading code review prompt from file (fallback)")

        with open(prompt_file, 'r', encoding='utf-8') as f:
            return f.read()

    except Exception as e:
        raise wrap_exception(
            e,
            FileReadError,
            "Failed to read code review prompt",
            context={"prompt_file": str(prompt_file)}
        )
