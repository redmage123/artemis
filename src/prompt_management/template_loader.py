"""
WHY: Handle loading and parsing of prompt templates from various sources.
RESPONSIBILITY: Load templates from RAG storage, files, or strings.
PATTERNS: Repository pattern, guard clauses, dispatch table for sources.

This module abstracts the complexity of template loading from different
sources, providing a unified interface for template retrieval.
"""

from typing import Dict, List, Optional, Any
import json
from .models import PromptTemplate, ReasoningStrategyType


class TemplateLoader:
    """
    WHY: Load prompt templates from various sources.
    RESPONSIBILITY: Abstract template loading logic.
    PATTERNS: Repository pattern, dependency injection.
    """

    def __init__(self, rag_agent, verbose: bool = False):
        """
        WHY: Initialize with RAG agent dependency.
        RESPONSIBILITY: Set up loader with required dependencies.
        PATTERNS: Dependency injection.

        Args:
            rag_agent: RAG agent for storage access
            verbose: Enable verbose logging
        """
        self.rag = rag_agent
        self.verbose = verbose

    def load_by_name(
        self,
        name: str,
        version: Optional[str] = None
    ) -> Optional[PromptTemplate]:
        """
        WHY: Load a template by name from RAG storage.
        RESPONSIBILITY: Query RAG and deserialize template.
        PATTERNS: Guard clause for not found, early returns.

        Args:
            name: Template name
            version: Specific version or None for latest

        Returns:
            PromptTemplate or None if not found
        """
        # Build query filters
        filters = {"task_title": name}
        if version:
            filters["version"] = version

        # Query RAG for template
        results = self.rag.query_similar(
            query_text=name,
            artifact_types=["prompt_template"],
            top_k=1,
            filters=filters
        )

        # Guard clause: Early return if not found
        if not results:
            if self.verbose:
                print(f"[TemplateLoader] Template not found: {name}")
            return None

        # Deserialize and return template
        prompt_data = self._extract_prompt_data(results[0])
        return self._dict_to_template(prompt_data)

    def load_by_category(
        self,
        category: str,
        top_k: int = 5
    ) -> List[PromptTemplate]:
        """
        WHY: Load multiple templates by category.
        RESPONSIBILITY: Query and deserialize templates by category.
        PATTERNS: Guard clause for empty results.

        Args:
            category: Template category
            top_k: Maximum number of templates to return

        Returns:
            List of PromptTemplates
        """
        filters = {"category": category}

        results = self.rag.query_similar(
            query_text=category,
            artifact_types=["prompt_template"],
            top_k=top_k,
            filters=filters
        )

        # Guard clause: Early return if no results
        if not results:
            return []

        # Deserialize all templates
        templates = []
        for result in results:
            prompt_data = self._extract_prompt_data(result)
            template = self._dict_to_template(prompt_data)
            templates.append(template)

        return templates

    def load_by_tags(
        self,
        tags: List[str],
        top_k: int = 5
    ) -> List[PromptTemplate]:
        """
        WHY: Load templates matching specific tags.
        RESPONSIBILITY: Query by tags and deserialize results.
        PATTERNS: Guard clause for empty tags.

        Args:
            tags: List of tags to match
            top_k: Maximum number of templates

        Returns:
            List of PromptTemplates
        """
        # Guard clause: Early return for empty tags
        if not tags:
            return []

        query_text = " ".join(tags)

        results = self.rag.query_similar(
            query_text=query_text,
            artifact_types=["prompt_template"],
            top_k=top_k
        )

        # Guard clause: Early return if no results
        if not results:
            return []

        # Deserialize all templates
        templates = []
        for result in results:
            prompt_data = self._extract_prompt_data(result)
            template = self._dict_to_template(prompt_data)
            templates.append(template)

        return templates

    def _extract_prompt_data(self, result: Dict) -> Dict:
        """
        WHY: Extract prompt data from RAG query result.
        RESPONSIBILITY: Parse prompt_data from metadata.
        PATTERNS: Guard clause for string vs dict.

        Args:
            result: RAG query result

        Returns:
            Prompt data dictionary
        """
        prompt_data = result["metadata"]["prompt_data"]

        # Guard clause: Parse if string, otherwise return as-is
        if isinstance(prompt_data, str):
            return json.loads(prompt_data)

        return prompt_data

    def _dict_to_template(self, data: Dict) -> PromptTemplate:
        """
        WHY: Convert dictionary to PromptTemplate object.
        RESPONSIBILITY: Deserialize template with type safety.
        PATTERNS: Explicit deserialization, handling optional fields.

        Args:
            data: Template data dictionary

        Returns:
            PromptTemplate instance
        """
        # Handle optional fields with defaults
        reasoning_strategy_value = data.get(
            "reasoning_strategy",
            ReasoningStrategyType.NONE.value
        )

        # Guard clause: Handle string enum values
        if isinstance(reasoning_strategy_value, str):
            reasoning_strategy = ReasoningStrategyType(reasoning_strategy_value)
        else:
            reasoning_strategy = reasoning_strategy_value

        return PromptTemplate(
            prompt_id=data["prompt_id"],
            name=data["name"],
            category=data["category"],
            version=data["version"],
            perspectives=data["perspectives"],
            success_metrics=data["success_metrics"],
            context_layers=data["context_layers"],
            task_breakdown=data["task_breakdown"],
            self_critique=data["self_critique"],
            system_message=data["system_message"],
            user_template=data["user_template"],
            tags=data["tags"],
            created_at=data["created_at"],
            updated_at=data["updated_at"],
            performance_score=data["performance_score"],
            usage_count=data["usage_count"],
            success_rate=data["success_rate"],
            reasoning_strategy=reasoning_strategy,
            reasoning_config=data.get("reasoning_config")
        )
