"""
WHY: Provide consistent output formatting across all CLI commands
RESPONSIBILITY: Format and display command results, status, and messages
PATTERNS:
- Strategy pattern for different output formats
- Guard clauses for validation
- Single responsibility for each formatter function
"""

from typing import Dict, Any, List, Optional
from pathlib import Path
from cli.models import SystemStatus, LLMConfig


class OutputFormatter:
    """
    Formats CLI output for consistent user experience

    Responsibilities:
    - Format headers and sections
    - Display status information
    - Show error and success messages
    """

    SEPARATOR = "=" * 70

    @staticmethod
    def header(title: str) -> str:
        """
        Format a section header

        Args:
            title: Header title

        Returns:
            Formatted header string
        """
        return f"{OutputFormatter.SEPARATOR}\n{title}\n{OutputFormatter.SEPARATOR}"

    @staticmethod
    def success(message: str) -> str:
        """
        Format success message

        Args:
            message: Success message

        Returns:
            Formatted success string
        """
        return f"\n{OutputFormatter.SEPARATOR}\n{message}\n{OutputFormatter.SEPARATOR}"

    @staticmethod
    def error(message: str) -> str:
        """
        Format error message

        Args:
            message: Error message

        Returns:
            Formatted error string
        """
        return f"\nError: {message}"

    @staticmethod
    def section(title: str) -> str:
        """
        Format a section title

        Args:
            title: Section title

        Returns:
            Formatted section string
        """
        return f"\n{title}:"

    @staticmethod
    def bullet_item(text: str, level: int = 0) -> str:
        """
        Format a bullet point item

        Args:
            text: Item text
            level: Indentation level (0-based)

        Returns:
            Formatted bullet string
        """
        indent = "  " * level
        return f"{indent}  {text}"

    @staticmethod
    def path_status(name: str, path: str, exists: bool) -> str:
        """
        Format path with existence status

        Args:
            name: Path name/description
            path: Path value
            exists: Whether path exists

        Returns:
            Formatted path status string
        """
        status = "Exists" if exists else "Missing"
        return f"  [{status}] {name}: {path}"


class StatusFormatter:
    """Format system status information"""

    @staticmethod
    def format_storage_paths(paths: Dict[str, Dict[str, Any]]) -> str:
        """
        Format storage paths section

        Args:
            paths: Dictionary of path information

        Returns:
            Formatted storage paths string
        """
        if not paths:
            return "No storage paths configured"

        lines = [OutputFormatter.section("Storage Paths")]
        for name, info in paths.items():
            exists = info.get("exists", False)
            path = info.get("path", "")
            lines.append(OutputFormatter.path_status(name, path, exists))

        return "\n".join(lines)

    @staticmethod
    def format_llm_config(config: LLMConfig) -> str:
        """
        Format LLM configuration section

        Args:
            config: LLM configuration

        Returns:
            Formatted LLM config string
        """
        lines = [
            OutputFormatter.section("LLM Configuration"),
            OutputFormatter.bullet_item(f"Provider: {config.provider}"),
            OutputFormatter.bullet_item(f"Model: {config.model}")
        ]
        return "\n".join(lines)

    @staticmethod
    def format_kanban_stats(stats: Dict[str, Any]) -> str:
        """
        Format kanban board statistics

        Args:
            stats: Kanban statistics dictionary

        Returns:
            Formatted kanban stats string
        """
        if not stats:
            return f"{OutputFormatter.section('Kanban Board')}\n  Kanban board not found"

        lines = [OutputFormatter.section("Kanban Board")]

        total_cards = stats.get("total_cards", 0)
        lines.append(OutputFormatter.bullet_item(f"Total cards: {total_cards}"))

        columns = stats.get("columns", {})
        for col_name, count in columns.items():
            lines.append(OutputFormatter.bullet_item(f"{col_name}: {count} cards", level=1))

        return "\n".join(lines)

    @staticmethod
    def format_checkpoints(checkpoints: List[str]) -> str:
        """
        Format checkpoint list

        Args:
            checkpoints: List of checkpoint filenames

        Returns:
            Formatted checkpoints string
        """
        if not checkpoints:
            return f"{OutputFormatter.section('Recent Checkpoints')}\n  No checkpoints found"

        lines = [OutputFormatter.section("Recent Checkpoints")]
        for checkpoint in checkpoints:
            lines.append(OutputFormatter.bullet_item(checkpoint))

        return "\n".join(lines)


class PromptFormatter:
    """Format prompt management output"""

    @staticmethod
    def format_prompt_list(prompts_by_category: Dict[str, List[Any]]) -> str:
        """
        Format list of prompts by category

        Args:
            prompts_by_category: Dictionary of category -> prompts

        Returns:
            Formatted prompt list string
        """
        if not prompts_by_category:
            return "No prompts found"

        lines = ["\nAvailable Prompts:\n"]

        for category, prompts in prompts_by_category.items():
            if not prompts:
                continue

            lines.append(f"\n{category}:")
            for prompt in prompts:
                lines.append(OutputFormatter.bullet_item(f"{prompt.name} (v{prompt.version})"))
                lines.append(OutputFormatter.bullet_item(f"Tags: {', '.join(prompt.tags)}", level=1))
                lines.append(OutputFormatter.bullet_item(
                    f"Usage: {prompt.usage_count} | Score: {prompt.performance_score:.2f}",
                    level=1
                ))

        return "\n".join(lines)

    @staticmethod
    def format_prompt_details(prompt: Any) -> str:
        """
        Format detailed prompt information

        Args:
            prompt: Prompt object

        Returns:
            Formatted prompt details string
        """
        lines = [
            f"\nPrompt: {prompt.name} (v{prompt.version})",
            f"Category: {prompt.category}",
            f"Tags: {', '.join(prompt.tags)}",
            "\nPerspectives:"
        ]

        for perspective in prompt.perspectives:
            lines.append(OutputFormatter.bullet_item(perspective))

        lines.append("\nSuccess Metrics:")
        for metric in prompt.success_metrics:
            lines.append(OutputFormatter.bullet_item(metric))

        lines.append("\nTask Breakdown:")
        for i, task in enumerate(prompt.task_breakdown, 1):
            lines.append(OutputFormatter.bullet_item(f"{i}. {task}"))

        return "\n".join(lines)

    @staticmethod
    def format_search_results(results: List[Dict[str, Any]]) -> str:
        """
        Format search results

        Args:
            results: List of search result dictionaries

        Returns:
            Formatted search results string
        """
        if not results:
            return "No results found"

        lines = []
        for result in results:
            prompt_data = result.get("prompt_data", {})
            score = result.get("score", 0.0)

            lines.append(OutputFormatter.bullet_item(f"{prompt_data['name']} (v{prompt_data['version']})"))
            lines.append(OutputFormatter.bullet_item(f"Category: {prompt_data['category']}", level=1))
            lines.append(OutputFormatter.bullet_item(f"Score: {score:.3f}", level=1))
            lines.append("")

        return "\n".join(lines)
