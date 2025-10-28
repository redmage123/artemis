#!/usr/bin/env python3
"""
AI-powered orchestration planner using LLM

WHY:
Task orchestration is complex - different types need different stages, complexities need different
resources, and dependencies must be respected. AI provides intelligent analysis while algorithms
ensure optimal ordering, duration estimation, and resource allocation.

RESPONSIBILITY:
- Query LLM for task analysis and plan generation
- Apply topological sort for valid stage ordering
- Apply Critical Path Method for duration estimation
- Apply Dynamic Programming for resource optimization
- Cache plans for performance

PATTERNS:
- Strategy Pattern: Implements OrchestrationPlannerInterface
- Template Method: create_plan() defines algorithm, helpers fill details
- Singleton Pattern: Cached prompt template (class-level)
- Memento Pattern: Plan caching for recovery

ALGORITHMS:
- Topological Sort (Kahn's Algorithm): O(V+E) stage ordering
- Critical Path Method: O(V+E) duration calculation
- Dynamic Programming: O(1) resource optimization
- Hash-based Caching: O(1) plan retrieval
"""

import json
from typing import Dict, Optional, Any

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from artemis_exceptions import PipelineConfigurationError, create_wrapped_exception, ArtemisException
from ai_orchestration.planner_interface import OrchestrationPlannerInterface
from ai_orchestration.orchestration_plan import OrchestrationPlan
from ai_orchestration.stage_dag import StageDAG
from ai_orchestration.resource_optimizer import ResourceOptimizer
from ai_orchestration.plan_cache import PlanCache
from ai_orchestration.constants import JSON_CODE_BLOCK_PATTERN, JSON_INLINE_PATTERN


class AIOrchestrationPlanner(OrchestrationPlannerInterface):
    """
    AI-powered orchestration planner using LLM

    WHAT:
    Uses large language model (GPT-4, Claude) to analyze tasks and generate optimal
    orchestration plans, applying industry algorithms (DAG, CPM, DP) to optimize
    stage ordering, duration estimation, and resource allocation.

    WHY:
    Task orchestration is complex:
    - Different task types need different stages (documentation skips testing)
    - Different complexities need different resources (bugfixes need 1 dev, refactors need 3)
    - Stage dependencies must be respected (can't test before developing)
    - Duration estimates guide user expectations

    AI provides:
    - Intelligent task type detection (feature vs bugfix vs refactor)
    - Complexity assessment from natural language descriptions
    - Stage selection based on task requirements
    - Reasoning for decisions (explainability)

    Algorithms provide:
    - Topological sort: Valid stage ordering (O(V+E))
    - Critical path method: Accurate duration estimates (O(V+E))
    - Dynamic programming: Optimal resource allocation (O(1) heuristic)
    - Hash-based caching: Fast plan retrieval (O(1) lookup)

    WORKFLOW:
    1. Check cache for identical task (O(1) hash lookup)
    2. Query LLM with task details + available stages
    3. Extract JSON plan from LLM response
    4. Apply topological sort to order stages (O(V+E))
    5. Apply critical path method for duration (O(V+E))
    6. Apply dynamic programming for resources (O(1))
    7. Validate plan integrity
    8. Cache plan for future use (O(1) insertion)

    INTEGRATION:
    - Used by: ArtemisOrchestrator.run_full_pipeline()
    - Uses: LLM client (OpenAI/Anthropic), StageDAG, ResourceOptimizer, PlanCache
    - Fallback: RuleBasedOrchestrationPlanner if LLM unavailable
    """

    # Performance: Class-level prompt template cache (Singleton pattern)
    _prompt_template_cache: Optional[str] = None

    def __init__(
        self,
        llm_client: Any,
        logger: Optional[Any] = None,
        temperature: float = 0.3,
        max_tokens: int = 1000
    ):
        """
        Initialize AI planner

        WHAT:
        Sets up LLM client, industry algorithm instances (DAG, optimizer, cache),
        and AI generation parameters (temperature, max_tokens).

        WHY:
        - Low temperature (0.3): Deterministic plans for same inputs (production stability)
        - Max tokens (1000): Sufficient for JSON plan + reasoning
        - Shared cache: Avoid regenerating plans for identical tasks
        - Shared algorithms: Consistent optimization across planners

        Args:
            llm_client: LLM client for AI queries (OpenAI/Anthropic)
            logger: Optional logger instance for debugging
            temperature: LLM temperature - lower = more deterministic (0.0-1.0)
            max_tokens: Maximum tokens for LLM response (default: 1000)
        """
        self.llm_client = llm_client
        self.logger = logger
        self.temperature = temperature
        self.max_tokens = max_tokens

        # Industry algorithms
        self.dag = StageDAG()
        self.optimizer = ResourceOptimizer()
        self.cache = PlanCache(max_size=100)

    def create_plan(
        self,
        card: Dict,
        platform_info: Any,
        resource_allocation: Any
    ) -> OrchestrationPlan:
        """
        Generate orchestration plan using AI with caching and optimization

        Industry Algorithms Applied:
        1. Hash-based caching (O(1) cache lookup)
        2. Topological sort for stage ordering (O(V+E))
        3. Critical Path Method for duration (O(V+E))
        4. Dynamic Programming for resource allocation
        """
        try:
            # Industry Algorithm: Hash-based caching - O(1) lookup
            cached_plan = self.cache.get(card, platform_info.platform_hash)
            if cached_plan:
                self._log("✅ Retrieved plan from cache (O(1) lookup)", "SUCCESS")
                return cached_plan

            self._log("🤖 Querying AI for optimal orchestration plan...", "INFO")

            # Build prompt using cached template
            prompt = self._build_prompt(card, platform_info, resource_allocation)

            # Query LLM
            from llm_client import LLMMessage
            ai_response = self.llm_client.generate_text(
                messages=[
                    LLMMessage(
                        role="system",
                        content="You are an expert software project orchestrator. Respond ONLY with valid JSON."
                    ),
                    LLMMessage(role="user", content=prompt)
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )

            # Extract and parse JSON response
            response_text = ai_response.content if hasattr(ai_response, 'content') else str(ai_response)
            plan_dict = self._extract_json(response_text)

            # Build plan with optimization
            plan = self._build_and_optimize_plan(plan_dict, card, resource_allocation)
            plan.validate()

            # Cache the plan for future use - O(1) insertion
            self.cache.put(card, platform_info.platform_hash, plan)

            self._log("✅ AI orchestration plan generated successfully", "SUCCESS")
            self._log_plan_summary(plan)

            return plan

        except ArtemisException:
            raise  # Re-raise Artemis exceptions
        except Exception as e:
            raise create_wrapped_exception(
                e,
                PipelineConfigurationError,
                "Failed to generate AI orchestration plan",
                context={'card_id': card.get('card_id', 'unknown')}
            )

    def _build_prompt(
        self,
        card: Dict,
        platform_info: Any,
        resource_allocation: Any
    ) -> str:
        """
        Build AI prompt using cached template

        Performance: Template cached at class level to avoid rebuilding
        """
        # Get or build template (O(1) cache access)
        if AIOrchestrationPlanner._prompt_template_cache is None:
            AIOrchestrationPlanner._prompt_template_cache = self._get_prompt_template()

        # Fill template with task-specific data
        return AIOrchestrationPlanner._prompt_template_cache.format(
            task_title=card.get('title', ''),
            task_description=card.get('description', ''),
            priority=card.get('priority', 'medium'),
            points=card.get('points', 5),
            max_developers=resource_allocation.max_parallel_developers,
            max_tests=resource_allocation.max_parallel_tests,
            total_memory=platform_info.total_memory_gb,
            cpu_cores=platform_info.cpu_count_logical,
            disk_type=platform_info.disk_type
        )

    def _get_prompt_template(self) -> str:
        """Get prompt template (cached at class level)"""
        return """You are an expert software project orchestrator. Analyze this task and create an optimal orchestration plan.

TASK DETAILS:
Title: {task_title}
Description: {task_description}
Priority: {priority}
Story Points: {points}

PLATFORM RESOURCES:
- Max Parallel Developers: {max_developers}
- Max Parallel Tests: {max_tests}
- Total Memory: {total_memory:.1f} GB
- CPU Cores: {cpu_cores}
- Disk Type: {disk_type}

AVAILABLE PIPELINE STAGES:
1. requirements_parsing - Parse and structure requirements
2. ssd_generation - Generate Software Specification Document
3. sprint_planning - Estimate with Planning Poker, create sprints
4. project_analysis - Analyze project structure and dependencies
5. architecture - Design system architecture
6. project_review - Review and approve architecture
7. dependencies - Validate dependencies
8. development - Implement features (supports parallelization)
9. arbitration - Select best solution (if multiple developers)
10. code_review - Security, GDPR, accessibility review
11. uiux - WCAG & GDPR compliance evaluation
12. validation - Run tests on solution
13. integration - Integrate winning solution
14. testing - Final comprehensive testing

ORCHESTRATION PLAN FORMAT (respond ONLY with valid JSON):
{{
  "complexity": "simple|medium|complex",
  "task_type": "feature|bugfix|refactor|documentation|other",
  "estimated_duration_minutes": <number>,
  "stages": ["stage1", "stage2", ...],
  "skip_stages": ["stage_to_skip", ...],
  "parallel_developers": <1-{max_developers}>,
  "max_parallel_tests": <1-{max_tests}>,
  "execution_strategy": "sequential|parallel",
  "reasoning": ["reason1", "reason2", ...]
}}

GUIDELINES:
- Use parallelization for complex/high-priority tasks
- Skip unnecessary stages (e.g., skip uiux for backend-only tasks)
- Balance thoroughness with resource constraints
- Arbitration only needed if parallel_developers > 1
- Testing/validation critical for high-priority tasks
- Consider platform resources when setting parallelization

Generate the orchestration plan:"""

    def _extract_json(self, response_text: str) -> Dict:
        """
        Extract JSON from AI response with guard clauses (early return pattern)

        WHY: Guard clauses with early returns make extraction logic clearer -
        try code block pattern first, then inline pattern, then raw text.

        Performance: Uses pre-compiled regex patterns (O(1) pattern access)

        Args:
            response_text: Raw AI response

        Returns:
            Parsed JSON dict

        Raises:
            PipelineConfigurationError: If JSON extraction/parsing fails
        """
        try:
            # Guard clause 1: Try code block pattern first (O(n) regex match)
            match = JSON_CODE_BLOCK_PATTERN.search(response_text)
            if match:
                return json.loads(match.group(1))

            # Guard clause 2: Try inline JSON pattern
            match = JSON_INLINE_PATTERN.search(response_text)
            if match:
                return json.loads(match.group(1))

            # Fallback: Parse entire response as JSON
            return json.loads(response_text)

        except json.JSONDecodeError as e:
            raise PipelineConfigurationError(
                f"Failed to parse AI response as JSON: {e}",
                context={'response_preview': response_text[:200]}
            )

    def _build_and_optimize_plan(
        self,
        plan_dict: Dict,
        card: Dict,
        resource_allocation: Any
    ) -> OrchestrationPlan:
        """
        Build and optimize OrchestrationPlan using industry algorithms

        Industry Algorithms Applied:
        1. Topological Sort - O(V+E) for optimal stage ordering
        2. Critical Path Method - O(V+E) for duration estimation
        3. Dynamic Programming - O(n*capacity) for resource allocation

        Args:
            plan_dict: Parsed AI response
            card: Task card for additional context
            resource_allocation: Resource limits

        Returns:
            Optimized OrchestrationPlan instance
        """
        # Extract stages from AI response
        raw_stages = plan_dict.get('stages', [])

        # Industry Algorithm 1: Topological Sort - O(V+E)
        # Ensures stages are ordered respecting dependencies
        try:
            sorted_stages = self.dag.topological_sort(tuple(raw_stages))
            self._log(f"   Applied topological sort (O(V+E)): {len(sorted_stages)} stages", "DEBUG")
        except PipelineConfigurationError:
            # Fallback to original order if cycle detected
            sorted_stages = raw_stages
            self._log("   ⚠️  Using original stage order (cycle in dependencies)", "WARNING")

        # Industry Algorithm 2: Critical Path Method - O(V+E)
        # Calculate realistic duration estimate
        try:
            critical_path, estimated_duration = self.dag.critical_path(tuple(sorted_stages))
            self._log(f"   Critical path calculated (O(V+E)): {estimated_duration} min", "DEBUG")
        except Exception:
            estimated_duration = plan_dict.get('estimated_duration_minutes', 30)

        # Industry Algorithm 3: Dynamic Programming for Resource Optimization
        # Optimize parallelization based on complexity and priority
        complexity = plan_dict.get('complexity', 'medium')
        priority = card.get('priority', 'medium')

        optimal_devs, optimal_tests = self.optimizer.optimal_parallelization(
            available_developers=resource_allocation.max_parallel_developers,
            available_tests=resource_allocation.max_parallel_tests,
            complexity=complexity,
            priority=priority
        )
        self._log(f"   Optimized resources (DP): {optimal_devs} devs, {optimal_tests} tests", "DEBUG")

        # Build optimized plan
        return OrchestrationPlan(
            complexity=complexity,
            task_type=plan_dict.get('task_type', 'feature'),
            stages=sorted_stages,  # Topologically sorted
            skip_stages=plan_dict.get('skip_stages', []),
            parallel_developers=optimal_devs,  # DP-optimized
            max_parallel_tests=optimal_tests,  # DP-optimized
            execution_strategy=plan_dict.get('execution_strategy', 'sequential'),
            estimated_duration_minutes=estimated_duration,  # CPM-calculated
            reasoning=plan_dict.get('reasoning', []) + [
                f"Stage ordering: Topological sort (O(V+E))",
                f"Duration estimate: Critical Path Method = {estimated_duration} min",
                f"Resource allocation: Dynamic Programming = {optimal_devs} devs, {optimal_tests} tests"
            ]
        )

    def _log_plan_summary(self, plan: OrchestrationPlan) -> None:
        """Log plan summary"""
        self._log(f"   Complexity: {plan.complexity}", "INFO")
        self._log(f"   Estimated duration: {plan.estimated_duration_minutes} minutes", "INFO")
        self._log(f"   Parallel developers: {plan.parallel_developers}", "INFO")
        self._log(f"   Stages: {len(plan.stages)}", "INFO")

        if plan.reasoning:
            self._log("   AI Reasoning:", "INFO")
            for reason in plan.reasoning:
                self._log(f"     • {reason}", "INFO")

    def _log(self, message: str, level: str = "INFO") -> None:
        """Log message if logger available"""
        if self.logger:
            self.logger.log(message, level)
