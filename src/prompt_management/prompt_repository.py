"""
WHY: Manage storage and retrieval of prompt templates.
RESPONSIBILITY: Provide repository pattern for prompt persistence.
PATTERNS: Repository pattern, guard clauses, CQRS (command-query separation).

This module implements the repository pattern for prompt template
storage, providing a clean abstraction over RAG storage.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
import json
import hashlib
from .models import PromptTemplate, ReasoningStrategyType
from debug_mixin import DebugMixin


class PromptRepository(DebugMixin):
    """
    WHY: Persist and retrieve prompt templates.
    RESPONSIBILITY: Abstract RAG storage operations for prompts.
    PATTERNS: Repository pattern, CQRS.
    """

    PROMPT_CATEGORIES = [
        "developer_agent",
        "supervisor_agent",
        "project_analysis_stage",
        "architecture_stage",
        "code_review_stage",
        "testing_stage",
        "learning_engine",
        "arbitration",
        "recovery_workflow"
    ]

    def __init__(self, rag_agent, verbose: bool = False):
        """
        WHY: Initialize repository with RAG agent.
        RESPONSIBILITY: Set up storage backend.
        PATTERNS: Dependency injection.

        Args:
            rag_agent: RAG agent for storage
            verbose: Enable verbose logging
        """
        DebugMixin.__init__(self, component_name="prompt_repo")
        self.rag = rag_agent
        self.verbose = verbose

        self._ensure_prompt_artifact_type()

    def save(
        self,
        name: str,
        category: str,
        perspectives: List[str],
        success_metrics: List[str],
        context_layers: Dict[str, Any],
        task_breakdown: List[str],
        self_critique: str,
        system_message: str,
        user_template: str,
        tags: Optional[List[str]] = None,
        version: str = "1.0",
        reasoning_strategy: ReasoningStrategyType = ReasoningStrategyType.NONE,
        reasoning_config: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        WHY: Save a prompt template to storage.
        RESPONSIBILITY: Persist template with all metadata.
        PATTERNS: Command method, guard clause for validation.

        Args:
            name: Prompt name
            category: Prompt category
            perspectives: Expert perspectives
            success_metrics: Success criteria
            context_layers: Context information
            task_breakdown: Task steps
            self_critique: Self-validation instructions
            system_message: System role message
            user_template: User prompt template
            tags: Optional tags
            version: Version string
            reasoning_strategy: Reasoning strategy
            reasoning_config: Strategy configuration

        Returns:
            Prompt ID
        """
        self.debug_log(
            "Saving prompt",
            name=name,
            category=category,
            version=version,
            strategy=reasoning_strategy.value
        )

        # Guard clause: Warn if unknown category
        if category not in self.PROMPT_CATEGORIES and self.verbose:
            print(f"[PromptRepository] Warning: Unknown category: {category}")

        # Generate prompt ID
        prompt_id = self._generate_prompt_id(name, version)

        # Create template
        prompt = PromptTemplate(
            prompt_id=prompt_id,
            name=name,
            category=category,
            version=version,
            perspectives=perspectives,
            success_metrics=success_metrics,
            context_layers=context_layers,
            task_breakdown=task_breakdown,
            self_critique=self_critique,
            system_message=system_message,
            user_template=user_template,
            reasoning_strategy=reasoning_strategy,
            reasoning_config=reasoning_config or {},
            tags=tags or [],
            created_at=datetime.utcnow().isoformat() + 'Z',
            updated_at=datetime.utcnow().isoformat() + 'Z',
            performance_score=0.0,
            usage_count=0,
            success_rate=0.0
        )

        # Convert to dict for storage
        prompt_dict = self._template_to_dict(prompt)

        # Build searchable content
        content = self._build_searchable_content(prompt)

        # Prepare metadata
        metadata = {
            "category": category,
            "version": version,
            "tags": json.dumps(tags or []),
            "performance_score": 0.0,
            "prompt_data": json.dumps(prompt_dict)
        }

        # Store in RAG
        self.rag.store_artifact(
            artifact_type="prompt_template",
            card_id="system",
            task_title=name,
            content=content,
            metadata=metadata
        )

        if self.verbose:
            print(f"[PromptRepository] Saved prompt: {name} (v{version})")

        return prompt_id

    def find_by_name(
        self,
        name: str,
        version: Optional[str] = None
    ) -> Optional[PromptTemplate]:
        """
        WHY: Retrieve template by name.
        RESPONSIBILITY: Query storage for specific template.
        PATTERNS: Query method, guard clause for not found.

        Args:
            name: Template name
            version: Specific version or None for latest

        Returns:
            PromptTemplate or None
        """
        # Build filters
        filters = {"task_title": name}
        if version:
            filters["version"] = version

        # Query RAG
        results = self.rag.query_similar(
            query_text=name,
            artifact_types=["prompt_template"],
            top_k=1,
            filters=filters
        )

        # Guard clause: Early return if not found
        if not results:
            self.debug_log("Template not found", name=name)
            if self.verbose:
                print(f"[PromptRepository] Template not found: {name}")
            return None

        # Deserialize and return
        prompt_data = self._extract_prompt_data(results[0])
        template = self._dict_to_template(prompt_data)

        # Increment usage count
        self._increment_usage(template.prompt_id)

        if self.verbose:
            print(f"[PromptRepository] Retrieved: {name} (v{template.version})")

        return template

    def find_by_category(
        self,
        category: str,
        top_k: int = 5
    ) -> List[PromptTemplate]:
        """
        WHY: Retrieve templates by category.
        RESPONSIBILITY: Query storage for category.
        PATTERNS: Query method, guard clause for empty results.

        Args:
            category: Category to search
            top_k: Maximum results

        Returns:
            List of templates
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

        return self._deserialize_results(results)

    def find_by_tags(
        self,
        tags: List[str],
        top_k: int = 5
    ) -> List[PromptTemplate]:
        """
        WHY: Retrieve templates matching tags.
        RESPONSIBILITY: Query storage by tags.
        PATTERNS: Query method, guard clauses.

        Args:
            tags: Tags to match
            top_k: Maximum results

        Returns:
            List of templates
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

        return self._deserialize_results(results)

    def find_by_performance(
        self,
        min_score: float = 0.0,
        top_k: int = 5
    ) -> List[PromptTemplate]:
        """
        WHY: Retrieve high-performing templates.
        RESPONSIBILITY: Query by performance metric.
        PATTERNS: Query method with filtering.

        Args:
            min_score: Minimum performance score
            top_k: Maximum results

        Returns:
            List of templates meeting criteria
        """
        # Query all templates
        results = self.rag.query_similar(
            query_text="prompt template",
            artifact_types=["prompt_template"],
            top_k=top_k * 2  # Query more to filter
        )

        # Deserialize and filter by performance
        templates = []
        for result in results:
            prompt_data = self._extract_prompt_data(result)
            template = self._dict_to_template(prompt_data)

            # Guard clause: Skip if below threshold
            if template.performance_score < min_score:
                continue

            templates.append(template)

            # Guard clause: Stop if we have enough
            if len(templates) >= top_k:
                break

        return templates

    def update_performance(self, prompt_id: str, success: bool):
        """
        WHY: Update template performance metrics.
        RESPONSIBILITY: Track template effectiveness.
        PATTERNS: Command method.

        Args:
            prompt_id: Template ID
            success: Whether usage was successful
        """
        # Note: Full implementation would update RAG entry
        if self.verbose:
            outcome = "Success" if success else "Failure"
            print(f"[PromptRepository] {outcome} for: {prompt_id}")

    def _ensure_prompt_artifact_type(self):
        """
        WHY: Ensure prompt_template type exists in RAG.
        RESPONSIBILITY: Initialize RAG with prompt type.
        PATTERNS: Guard clause for existing type.
        """
        # Guard clause: Skip if already exists
        if "prompt_template" in self.rag.ARTIFACT_TYPES:
            return

        # Add prompt_template type
        self.rag.ARTIFACT_TYPES.append("prompt_template")

        # Reinitialize collections
        if hasattr(self.rag, 'client') and self.rag.client:
            self.rag._initialize_collections()

    def _generate_prompt_id(self, name: str, version: str) -> str:
        """Generate unique prompt ID"""
        content = f"{name}-{version}-{datetime.utcnow().isoformat()}"
        return f"prompt-{hashlib.md5(content.encode()).hexdigest()[:8]}"

    def _build_searchable_content(self, prompt: PromptTemplate) -> str:
        """Build searchable content from template"""
        parts = [
            f"Name: {prompt.name}",
            f"Category: {prompt.category}",
            f"Perspectives: {', '.join(prompt.perspectives)}",
            f"Success Metrics: {', '.join(prompt.success_metrics)}",
            f"System Message: {prompt.system_message}",
            f"User Template: {prompt.user_template}",
            f"Tags: {', '.join(prompt.tags)}"
        ]
        return "\n\n".join(parts)

    def _template_to_dict(self, template: PromptTemplate) -> Dict:
        """Convert template to dictionary"""
        return {
            "prompt_id": template.prompt_id,
            "name": template.name,
            "category": template.category,
            "version": template.version,
            "perspectives": template.perspectives,
            "success_metrics": template.success_metrics,
            "context_layers": template.context_layers,
            "task_breakdown": template.task_breakdown,
            "self_critique": template.self_critique,
            "system_message": template.system_message,
            "user_template": template.user_template,
            "tags": template.tags,
            "created_at": template.created_at,
            "updated_at": template.updated_at,
            "performance_score": template.performance_score,
            "usage_count": template.usage_count,
            "success_rate": template.success_rate,
            "reasoning_strategy": template.reasoning_strategy.value,
            "reasoning_config": template.reasoning_config
        }

    def _dict_to_template(self, data: Dict) -> PromptTemplate:
        """Convert dictionary to template"""
        # Handle reasoning strategy enum
        strategy_value = data.get("reasoning_strategy", "none")
        if isinstance(strategy_value, str):
            strategy = ReasoningStrategyType(strategy_value)
        else:
            strategy = strategy_value

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
            reasoning_strategy=strategy,
            reasoning_config=data.get("reasoning_config")
        )

    def _extract_prompt_data(self, result: Dict) -> Dict:
        """Extract prompt data from RAG result"""
        prompt_data = result["metadata"]["prompt_data"]

        # Guard clause: Parse if string
        if isinstance(prompt_data, str):
            return json.loads(prompt_data)

        return prompt_data

    def _deserialize_results(self, results: List[Dict]) -> List[PromptTemplate]:
        """Deserialize multiple results"""
        templates = []
        for result in results:
            prompt_data = self._extract_prompt_data(result)
            template = self._dict_to_template(prompt_data)
            templates.append(template)

        return templates

    def _increment_usage(self, prompt_id: str):
        """Increment usage count for template"""
        # Note: Full implementation would update RAG entry
        pass
