"""
Module: agents/developer/rag_integration.py

WHY: Centralize all RAG (Retrieval Augmented Generation) queries for the developer agent.
RESPONSIBILITY: Query RAG for code examples, feedback, refactoring patterns, and prompts.
PATTERNS: Strategy Pattern (query types), Template Method (formatting), Guard Clauses.

This module handles:
- Querying RAG for code review feedback
- Querying RAG for refactoring instructions
- Querying RAG for notebook/code examples
- Retrieving developer prompts from RAG (DEPTH framework)
- Formatting RAG results for LLM prompts

EXTRACTED FROM: standalone_developer_agent.py (lines 1050-1586)
"""

from typing import Optional, List, Dict
from artemis_stage_interface import LoggerInterface
from artemis_exceptions import RAGQueryError, create_wrapped_exception


class RAGIntegration:
    """
    Handles all RAG queries for developer agent

    WHY: Centralize RAG interactions with consistent error handling
    PATTERNS: Strategy Pattern, Template Method, Guard Clauses
    """

    def __init__(
        self,
        developer_name: str,
        developer_type: str,
        logger: Optional[LoggerInterface] = None,
        prompt_manager=None
    ):
        """
        Initialize RAG integration

        Args:
            developer_name: Name of developer (e.g., "developer-a")
            developer_type: Type of developer (e.g., "conservative")
            logger: Optional logger
            prompt_manager: Optional PromptManager for DEPTH prompts
        """
        self.developer_name = developer_name
        self.developer_type = developer_type
        self.logger = logger
        self.prompt_manager = prompt_manager

    def query_code_review_feedback(self, rag_agent, card_id: str) -> Optional[str]:
        """
        Query RAG for code review feedback from previous attempts

        This implements the proper DAO pattern:
        - Developer queries RAG Agent (not ChromaDB directly)
        - RAG Agent handles all database operations
        - Returns formatted feedback for LLM prompt

        Args:
            rag_agent: RAG Agent instance
            card_id: Card ID to query feedback for

        Returns:
            Formatted feedback string or None
        """
        try:
            self._log_info(f"🔍 Querying RAG for code review feedback (card: {card_id})...")

            # Query RAG for code review artifacts
            query_text = f"code review feedback for {card_id}"
            results = rag_agent.query_similar(
                query_text=query_text,
                artifact_type="code_review",
                top_k=3  # Get up to 3 most recent feedback items
            )

            # Guard: no results
            if not results or len(results) == 0:
                self._log_info("No code review feedback found in RAG")
                return None

            # Format feedback for LLM prompt
            feedback_text = self._format_code_review_feedback(results)
            self._log_info(f"✅ Found {len(results)} feedback item(s) from RAG")

            return feedback_text

        except Exception as e:
            return self._handle_rag_query_error(e, {"card_id": card_id}, "code review feedback")

    def query_refactoring_instructions(
        self,
        rag_agent,
        task_title: str = "",
        language: str = "python"
    ) -> Optional[str]:
        """
        Query RAG for refactoring instructions and best practices

        Retrieves multi-language refactoring patterns from RAG storage
        to guide developer in writing clean, maintainable code

        Args:
            rag_agent: RAG Agent instance
            task_title: Task title for context (optional)
            language: Programming language (python, java, javascript, etc.)

        Returns:
            Formatted refactoring instructions or None
        """
        # Guard: no RAG agent
        if not rag_agent:
            return None

        try:
            self._log_info(f"🔍 Querying RAG for refactoring instructions ({language})...")

            # Query RAG for refactoring artifacts
            query_text = f"refactoring best practices {language} code quality patterns"
            results = rag_agent.query_similar(
                query_text=query_text,
                artifact_type="architecture_decision",
                top_k=5  # Get top 5 most relevant refactoring patterns
            )

            # Guard: no results
            if not results or len(results) == 0:
                self._log_info("No refactoring instructions found in RAG")
                return None

            # Format refactoring instructions for LLM prompt
            instruction_text = self._format_refactoring_instructions(results, language)

            # Guard: no matching patterns
            if not instruction_text:
                return None

            self._log_info(f"✅ Found {len(results)} refactoring patterns from RAG")
            return instruction_text

        except Exception as e:
            return self._handle_rag_query_error(e, {"language": language}, "refactoring instructions")

    def query_rag_for_examples(
        self,
        rag_agent,
        task_title: str,
        task_description: str
    ) -> str:
        """
        Query RAG for relevant examples based on task characteristics.

        Uses Strategy Pattern to select appropriate query approach.

        Args:
            rag_agent: RAG Agent instance
            task_title: Title of the task
            task_description: Task description

        Returns:
            Formatted examples string to include in prompt

        Raises:
            RAGQueryError: If RAG query fails
        """
        # Guard: no RAG agent
        if not rag_agent:
            self._log_warning("RAG agent not available - returning empty string")
            return ""

        try:
            task_type = self._detect_task_type(task_title, task_description)
            self._log_debug(f"Detected task_type: {task_type}")

            result = self._query_by_task_type(rag_agent, task_type, task_title)
            self._log_debug(f"RAG query returned {len(result)} characters")

            return result

        except Exception as e:
            raise create_wrapped_exception(
                e,
                RAGQueryError,
                "Failed to query RAG for examples",
                {"task_title": task_title, "task_type": "unknown"}
            ) from e

    def get_developer_prompt_from_rag(
        self,
        task_title: str,
        adr_content: str,
        code_review_feedback: Optional[str],
        rag_agent
    ) -> str:
        """
        Get developer prompt from RAG database with DEPTH framework.

        WHY: Retrieves RAG-stored prompt templates for consistent developer guidance.
        PATTERNS: Early return pattern (guard clauses), Strategy pattern (developer type selection).
        PERFORMANCE: Caches prompt templates in PromptManager.

        Args:
            task_title: Title of the task
            adr_content: ADR architectural content
            code_review_feedback: Feedback from code review (if any)
            rag_agent: RAG agent instance

        Returns:
            Fully rendered prompt string
        """
        # Guard: no prompt manager
        if not self.prompt_manager:
            self._log_warning("Prompt manager not available - using default prompt")
            return self._get_default_developer_prompt()

        try:
            # Determine which prompt to use based on developer type
            prompt_name = (
                "developer_conservative_implementation"
                if self.developer_type == "conservative"
                else "developer_aggressive_implementation"
            )

            self._log_info(f"📝 Loading DEPTH prompt: {prompt_name}")

            # Retrieve prompt template from RAG
            prompt_template = self.prompt_manager.get_prompt(prompt_name)

            # Guard: prompt not found
            if not prompt_template:
                self._log_warning(f"Prompt '{prompt_name}' not found in RAG - using default")
                return self._get_default_developer_prompt()

            # Render prompt with task-specific variables
            rendered = self.prompt_manager.render_prompt(
                prompt=prompt_template,
                variables={
                    "developer_name": self.developer_name,
                    "task_title": task_title,
                    "adr_content": adr_content,
                    "code_review_feedback": code_review_feedback or "No previous feedback"
                }
            )

            # Combine system and user messages into one prompt
            full_prompt = f"""{rendered['system']}

{rendered['user']}"""

            self._log_info(f"✅ Loaded DEPTH prompt with {len(prompt_template.perspectives)} perspectives")
            return full_prompt

        except Exception as e:
            self._log_warning(f"Error loading RAG prompt: {e} - using default")
            return self._get_default_developer_prompt()

    # ========== Private Helper Methods ==========

    def _detect_task_type(self, task_title: str, task_description: str) -> str:
        """Detect task type from title and description."""
        combined_text = f"{task_title} {task_description}".lower()

        notebook_keywords = ['notebook', 'jupyter', 'ipynb', 'slide', 'presentation', 'demo']
        is_notebook = any(keyword in combined_text for keyword in notebook_keywords)

        return "notebook" if is_notebook else "code"

    def _query_by_task_type(self, rag_agent, task_type: str, task_title: str) -> str:
        """Query RAG based on task type - Strategy Pattern."""
        query_strategies = {
            "notebook": lambda: self._query_notebook_examples(rag_agent, task_title),
            "code": lambda: self._query_code_examples(rag_agent, task_title)
        }

        strategy = query_strategies.get(task_type, lambda: self._query_code_examples(rag_agent, task_title))
        return strategy()

    def _query_notebook_examples(self, rag_agent, task_title: str) -> str:
        """Query RAG for notebook examples - Template Method Pattern."""
        self._log_info("🔍 Querying RAG for notebook examples...")

        results = self._execute_rag_query(
            rag_agent,
            query_text=f"high-quality jupyter notebook example {task_title}",
            artifact_types=["notebook_example"],
            top_k=2
        )

        # Guard: no results
        if not results:
            self._log_warning("No notebook examples found in RAG")
            return ""

        self._log_info(f"✅ Found {len(results)} notebook examples from RAG")
        return self._format_notebook_examples(results)

    def _query_code_examples(self, rag_agent, task_title: str) -> str:
        """Query RAG for code examples - Template Method Pattern."""
        results = self._execute_rag_query(
            rag_agent,
            query_text=task_title,
            artifact_types=["code_example", "developer_solution"],
            top_k=3
        )

        # Guard: no results
        if not results:
            return ""

        return self._format_code_examples(results)

    def _execute_rag_query(
        self,
        rag_agent,
        query_text: str,
        artifact_types: list,
        top_k: int
    ) -> list:
        """Execute RAG query with error handling."""
        try:
            return rag_agent.query_similar(
                query_text=query_text,
                artifact_types=artifact_types,
                top_k=top_k
            )
        except Exception as e:
            raise create_wrapped_exception(
                e,
                RAGQueryError,
                "RAG query execution failed",
                {"query": query_text[:50], "artifact_types": artifact_types}
            ) from e

    def _format_code_review_feedback(self, results: List[Dict]) -> str:
        """Format code review feedback from RAG results"""
        feedback_lines = ["# PREVIOUS CODE REVIEW FEEDBACK\n"]
        feedback_lines.append("The following issues were found in previous implementation attempt(s):\n")

        for i, result in enumerate(results, 1):
            content = result.get('content', '')
            metadata = result.get('metadata', {})

            feedback_lines.append(f"\n## Feedback #{i} (Attempt {metadata.get('retry_count', 'N/A')})")
            feedback_lines.append(f"Score: {metadata.get('code_review_score', 'N/A')}")
            feedback_lines.append(f"Status: {metadata.get('status', 'FAILED')}")
            feedback_lines.append(f"\n{content}\n")

        return "\n".join(feedback_lines)

    def _format_refactoring_instructions(self, results: List[Dict], language: str) -> Optional[str]:
        """Format refactoring instructions from RAG results"""
        instruction_lines = ["# REFACTORING GUIDELINES AND BEST PRACTICES\n"]
        instruction_lines.append(f"Apply these refactoring patterns when writing {language} code:\n")

        for i, result in enumerate(results, 1):
            content = result.get('content', '')
            metadata = result.get('metadata', {})

            # Filter by language if metadata includes language info
            artifact_languages = metadata.get('language', '')
            if language not in artifact_languages and 'all_languages' not in artifact_languages:
                continue

            refactoring_type = metadata.get('refactoring_type', 'Unknown')
            priority = metadata.get('priority', 'medium')

            instruction_lines.append(f"\n## Pattern #{i}: {refactoring_type.upper()} (Priority: {priority})")
            instruction_lines.append(f"{content}\n")
            instruction_lines.append("---\n")

        # Only header and intro means no patterns found
        if len(instruction_lines) <= 2:
            return None

        return "\n".join(instruction_lines)

    def _format_notebook_examples(self, results: List[Dict]) -> str:
        """Format notebook examples for prompt - Builder Pattern."""
        builder = []
        builder.append("\n\n**📚 HIGH-QUALITY NOTEBOOK EXAMPLES FROM RAG:**\n")
        builder.append("Study these examples of excellent notebook structure and content:\n\n")

        for i, result in enumerate(results, 1):
            example_section = self._build_notebook_example_section(i, result)
            builder.append(example_section)

        builder.append(self._get_quality_indicators())
        return ''.join(builder)

    def _build_notebook_example_section(self, index: int, result: Dict) -> str:
        """Build individual example section - extracted method."""
        metadata = result.get('metadata', {})
        quality_score = metadata.get('quality_score', 'N/A')
        total_cells = metadata.get('total_cells', 'N/A')
        features = metadata.get('features', [])

        section = []
        section.append(f"**Example {index}** (Quality: {quality_score}, Cells: {total_cells}):\n")
        section.append(f"  Features: {', '.join(features[:5])}\n")

        content = result.get('content', '')[:1500]
        section.append(f"\n{content}\n")
        section.append("\n" + "="*70 + "\n\n")

        return ''.join(section)

    def _get_quality_indicators(self) -> str:
        """Get quality indicators text - extracted constant."""
        return """
**KEY QUALITY INDICATORS FROM EXAMPLES:**
- Comprehensive visualizations (matplotlib, seaborn, etc.)
- Working imports only (no placeholders like 'artemis_core')
- Rich narrative flow between sections
- Code cells with real data and examples
- Professional structure (intro → body → conclusion)
- Content depth (15+ cells minimum)
- Balance of code and markdown (ratio near 0.7)

**MANDATORY QUALITY REQUIREMENTS - YOU MUST MEET THESE:**
✓ Minimum 20 cells total (mix of code and markdown)
✓ Minimum 15,000 characters of total content
✓ Average cell length: 500+ characters (NOT empty shells!)
✓ NO placeholder imports (artemis_core, artemis_demo, DynamicPipeline, etc.)
✓ Working visualizations ONLY - use matplotlib, Chart.js with REAL data
✓ Rich, detailed explanations in every cell
✓ Professional presentation quality

**THESE ARE NOT SUGGESTIONS - THEY ARE REQUIREMENTS!**
If your output has fewer than 20 cells or less than 15,000 characters, it will be REJECTED.
"""

    def _format_code_examples(self, results: List[Dict]) -> str:
        """Format code examples for prompt - Builder Pattern."""
        builder = ["\n\n**📚 RELEVANT EXAMPLES FROM RAG:**\n\n"]

        for i, result in enumerate(results, 1):
            builder.append(f"**Example {i}:**\n")
            builder.append(f"{result.get('content', '')[:800]}\n\n")

        return ''.join(builder)

    def _handle_rag_query_error(self, error: Exception, context: Dict, query_type: str) -> None:
        """Handle RAG query error with consistent logging"""
        self._log_warning(f"Error querying RAG for {query_type}: {error}")

        wrapped_exception = create_wrapped_exception(
            error,
            RAGQueryError,
            f"Failed to query RAG for {query_type}",
            {**context, "developer_name": self.developer_name}
        )
        self._log_debug(f"Details: {wrapped_exception}")
        return None

    def _get_default_developer_prompt(self) -> str:
        """Get default developer prompt"""
        return """You are an expert software developer. Generate high-quality, production-ready code."""

    def _log_info(self, message: str):
        """Log info message"""
        if self.logger:
            self.logger.log(message, "INFO")

    def _log_warning(self, message: str):
        """Log warning message"""
        if self.logger:
            self.logger.log(message, "WARNING")

    def _log_debug(self, message: str):
        """Log debug message"""
        if self.logger:
            self.logger.log(message, "DEBUG")


__all__ = [
    "RAGIntegration"
]
