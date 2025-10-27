#!/usr/bin/env python3
"""
Module: dynamic_pipeline.py

Purpose: Implements Dynamic Pipelines system for adaptive, runtime-configurable pipeline execution
Why: Traditional static pipelines can't adapt to varying project complexity, resource constraints,
     or runtime conditions. This module enables intelligent pipeline construction and execution
     that adjusts stages, parallelism, and resources based on real-time analysis and feedback.

Patterns:
    - Strategy Pattern: Stage selection strategies based on complexity/conditions
    - Builder Pattern: Fluent pipeline construction with validation
    - Chain of Responsibility: Stage execution with skip/retry/fallback logic
    - Observer Pattern: Event broadcasting for all pipeline operations
    - State Pattern: Pipeline lifecycle state management
    - Factory Pattern: Strategy and stage factory creation

Integration:
    - pipeline_observer.py: Event broadcasting (PipelineObservable, EventType)
    - artemis_exceptions.py: Exception hierarchy (@wrap_exception decorator)
    - artemis_services.py: Logging (PipelineLogger)
    - artemis_stages.py: Stage interface and implementations

Architecture:
    DynamicPipelineBuilder -> DynamicPipeline -> StageExecutor -> Individual Stages
                  ↓                    ↓              ↓
            StageSelector      PipelineObservable  RetryPolicy
                  ↓                    ↓              ↓
         SelectionStrategy      Event Emission   ErrorHandler

Key Features:
    - Dynamic stage selection based on project complexity analysis
    - Conditional stage execution with runtime predicates
    - Parallel stage execution with dependency resolution
    - Stage skip/retry logic with configurable policies
    - Dynamic resource allocation per stage
    - Runtime pipeline modification (add/remove/reorder stages)
    - Comprehensive event emission for monitoring

Design Decisions:
    - NO elif chains: Use dispatch tables and Strategy pattern
    - NO nested loops: Extract to helper methods
    - NO nested ifs: Use guard clauses and early returns
    - NO sequential ifs: Use dispatch tables
    - ALL methods use @wrap_exception for consistent error handling
    - ALL operations emit events via Observer pattern

Performance Optimizations:
    - Parallel stage execution where dependencies allow (concurrent.futures)
    - Stage result caching to avoid redundant work
    - Lazy strategy evaluation (only compute when needed)
    - Set-based dependency tracking (O(1) lookups)

Thread Safety:
    - Pipeline state is single-threaded (assumes orchestrator serialization)
    - Parallel stage execution uses ThreadPoolExecutor with proper locking
    - Event broadcasting is not thread-safe (observers assumed fast)
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Set, Callable, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import functools

from pipeline_observer import (
    PipelineObservable, PipelineEvent, EventType, PipelineObserver
)
from artemis_exceptions import (
    ArtemisException, PipelineException, wrap_exception
)
from artemis_services import PipelineLogger
from advanced_features_ai_mixin import AdvancedFeaturesAIMixin


# ============================================================================
# PIPELINE STATE ENUM
# ============================================================================

class PipelineState(Enum):
    """
    Pipeline lifecycle states.

    Why needed: Enforces valid state transitions and enables State pattern
    implementation for lifecycle management.

    State transitions:
        CREATED -> BUILDING -> READY -> RUNNING -> (PAUSED <-> RUNNING)* -> COMPLETED/FAILED

    Design decision: Single enum ensures consistent state tracking across
    all pipeline instances and enables state-based behavior selection.
    """
    CREATED = "created"          # Pipeline object created, not configured
    BUILDING = "building"        # Builder is configuring pipeline
    READY = "ready"              # Built and validated, ready to execute
    RUNNING = "running"          # Currently executing stages
    PAUSED = "paused"           # Execution paused (can resume)
    COMPLETED = "completed"     # Successfully completed all stages
    FAILED = "failed"           # Failed with unrecoverable error
    CANCELLED = "cancelled"     # Cancelled by supervisor/user


# ============================================================================
# STAGE COMPLEXITY ENUM
# ============================================================================

class ProjectComplexity(Enum):
    """
    Project complexity levels for stage selection.

    Why needed: Determines which stages to include and how much validation
    to perform. Simple projects skip expensive validation, complex projects
    include all quality gates.

    Complexity indicators:
        SIMPLE: <100 LOC, no dependencies, single file
        MODERATE: <1000 LOC, few dependencies, multiple files
        COMPLEX: >1000 LOC, many dependencies, microservices
        ENTERPRISE: >10K LOC, multiple repos, infrastructure
    """
    SIMPLE = "simple"
    MODERATE = "moderate"
    COMPLEX = "complex"
    ENTERPRISE = "enterprise"


# ============================================================================
# STAGE EXECUTION RESULT
# ============================================================================

@dataclass
class StageResult:
    """
    Result of stage execution.

    Why it exists: Encapsulates all stage execution data in single immutable
    object for passing between pipeline components and caching.

    Design pattern: Value Object (immutable result holder)

    Responsibilities:
    - Store stage execution success/failure status
    - Preserve stage output data for next stage
    - Track execution duration for metrics
    - Indicate if stage was skipped/retried
    - Provide optional error information
    """
    stage_name: str
    success: bool
    data: Dict[str, Any] = field(default_factory=dict)
    duration: float = 0.0
    skipped: bool = False
    retry_count: int = 0
    error: Optional[Exception] = None

    def is_success(self) -> bool:
        """Check if stage succeeded (not failed, not skipped)"""
        return self.success and not self.skipped


# ============================================================================
# STAGE INTERFACE
# ============================================================================

class PipelineStage(ABC):
    """
    Abstract base for all pipeline stages.

    Why it exists: Defines contract for all pipeline stages, enabling
    polymorphic execution and consistent error handling.

    Design pattern: Template Method + Strategy

    Responsibilities:
    - Define execution contract via execute()
    - Declare dependencies for ordering
    - Support conditional execution via should_execute()
    - Provide stage metadata (name, description)
    """

    def __init__(self, name: str):
        self.name = name
        self.logger = PipelineLogger(verbose=True)

    @abstractmethod
    def execute(self, context: Dict[str, Any]) -> StageResult:
        """
        Execute stage logic.

        Why needed: Core stage execution method. Context contains all data
        from previous stages. Returns result for next stage.

        Args:
            context: Execution context with previous stage results

        Returns:
            StageResult with execution outcome and data

        Raises:
            PipelineException: On stage execution failure
        """
        pass

    def get_dependencies(self) -> List[str]:
        """
        Get list of stage names this stage depends on.

        Why needed: Enables dependency resolution for parallel execution
        and proper stage ordering.

        Returns:
            List of stage names that must complete before this stage
        """
        return []

    def should_execute(self, context: Dict[str, Any]) -> bool:
        """
        Determine if stage should execute based on context.

        Why needed: Enables conditional stage execution. For example,
        testing stage skips if no tests found, deployment skips in
        development mode.

        Args:
            context: Execution context with previous results

        Returns:
            True if stage should execute, False to skip
        """
        return True

    def get_description(self) -> str:
        """Get human-readable stage description"""
        return f"Stage: {self.name}"


# ============================================================================
# SELECTION STRATEGY INTERFACE
# ============================================================================

class StageSelectionStrategy(ABC):
    """
    Strategy for selecting which stages to include in pipeline.

    Why it exists: Encapsulates stage selection logic, allowing different
    selection algorithms (complexity-based, resource-based, user-defined).

    Design pattern: Strategy Pattern

    Responsibilities:
    - Analyze project/context to select appropriate stages
    - Return ordered list of stages to execute
    - Provide rationale for selections (logging/debugging)
    """

    @abstractmethod
    def select_stages(
        self,
        available_stages: List[PipelineStage],
        context: Dict[str, Any]
    ) -> List[PipelineStage]:
        """
        Select which stages to include based on strategy.

        Why needed: Core strategy method. Different implementations provide
        different selection logic (complexity, resources, manual).

        Args:
            available_stages: All possible stages
            context: Decision context (complexity, resources, config)

        Returns:
            Ordered list of selected stages
        """
        pass


# ============================================================================
# CONCRETE SELECTION STRATEGIES
# ============================================================================

class ComplexityBasedSelector(StageSelectionStrategy):
    """
    Selects stages based on project complexity analysis.

    Why it exists: Simple projects don't need extensive validation,
    complex projects need all quality gates. Adapts pipeline to project.

    Design pattern: Strategy implementation

    Selection rules:
        SIMPLE: Basic stages only (requirements, development, basic tests)
        MODERATE: + code review, integration tests
        COMPLEX: + architecture review, performance tests, security scan
        ENTERPRISE: + compliance, multi-environment deployment
    """

    def __init__(self, logger: Optional[PipelineLogger] = None):
        self.logger = logger or PipelineLogger(verbose=True)
        # Dispatch table maps complexity to stage filter predicate
        # Why dispatch table: Eliminates elif chain, declarative configuration
        self._stage_filters = {
            ProjectComplexity.SIMPLE: self._simple_stages,
            ProjectComplexity.MODERATE: self._moderate_stages,
            ProjectComplexity.COMPLEX: self._complex_stages,
            ProjectComplexity.ENTERPRISE: self._enterprise_stages
        }

    @wrap_exception(PipelineException, "Failed to select stages")
    def select_stages(
        self,
        available_stages: List[PipelineStage],
        context: Dict[str, Any]
    ) -> List[PipelineStage]:
        """Select stages based on project complexity"""

        complexity = context.get("complexity", ProjectComplexity.MODERATE)

        # Guard clause: Validate complexity type
        if not isinstance(complexity, ProjectComplexity):
            self.logger.log(
                f"Invalid complexity type: {type(complexity)}, defaulting to MODERATE",
                "WARNING"
            )
            complexity = ProjectComplexity.MODERATE

        # Dispatch to appropriate filter using strategy map
        # Why dispatch table: No elif chain, O(1) lookup, easy to extend
        filter_func = self._stage_filters.get(complexity)

        # Guard clause: Handle unknown complexity
        if not filter_func:
            self.logger.log(
                f"No filter for complexity {complexity}, using all stages",
                "WARNING"
            )
            return available_stages

        # Apply filter strategy
        selected = [stage for stage in available_stages if filter_func(stage)]

        self.logger.log(
            f"Selected {len(selected)}/{len(available_stages)} stages for {complexity.value}",
            "INFO"
        )

        return selected

    def _simple_stages(self, stage: PipelineStage) -> bool:
        """Filter for simple projects - basic stages only"""
        basic_stages = {
            "requirements", "development", "unit_tests", "integration"
        }
        return any(name in stage.name.lower() for name in basic_stages)

    def _moderate_stages(self, stage: PipelineStage) -> bool:
        """Filter for moderate projects - includes code review"""
        # Moderate includes all simple stages plus code review
        moderate_stages = {
            "requirements", "development", "unit_tests",
            "integration", "code_review", "validation"
        }
        return any(name in stage.name.lower() for name in moderate_stages)

    def _complex_stages(self, stage: PipelineStage) -> bool:
        """Filter for complex projects - includes architecture and security"""
        complex_stages = {
            "requirements", "architecture", "development", "code_review",
            "unit_tests", "integration", "security", "performance", "validation"
        }
        return any(name in stage.name.lower() for name in complex_stages)

    def _enterprise_stages(self, stage: PipelineStage) -> bool:
        """Filter for enterprise projects - all stages"""
        # Enterprise projects use all available stages
        return True


class ResourceBasedSelector(StageSelectionStrategy):
    """
    Selects stages based on available resources (time, CPU, memory).

    Why it exists: Resource-constrained environments can't run all stages.
    Prioritizes critical stages when resources limited.

    Design pattern: Strategy implementation

    Selection rules:
        HIGH resources: All stages
        MEDIUM resources: Skip performance tests, detailed security scans
        LOW resources: Only critical stages (requirements, basic tests)
    """

    def __init__(self, logger: Optional[PipelineLogger] = None):
        self.logger = logger or PipelineLogger(verbose=True)
        # Resource thresholds (arbitrary units for demo)
        self._resource_profiles = {
            "high": {"cpu": 8, "memory_gb": 16, "time_minutes": 120},
            "medium": {"cpu": 4, "memory_gb": 8, "time_minutes": 60},
            "low": {"cpu": 2, "memory_gb": 4, "time_minutes": 30}
        }

    @wrap_exception(PipelineException, "Failed to select stages based on resources")
    def select_stages(
        self,
        available_stages: List[PipelineStage],
        context: Dict[str, Any]
    ) -> List[PipelineStage]:
        """Select stages based on available resources"""

        # Extract resource constraints from context
        available_cpu = context.get("cpu_cores", 4)
        available_memory = context.get("memory_gb", 8)
        available_time = context.get("time_budget_minutes", 60)

        # Determine resource profile using helper method
        profile = self._determine_profile(available_cpu, available_memory, available_time)

        self.logger.log(
            f"Resource profile: {profile} (CPU={available_cpu}, MEM={available_memory}GB, TIME={available_time}min)",
            "INFO"
        )

        # Filter stages based on resource profile
        # Why dispatch table: Avoids elif chain, declarative
        profile_filters = {
            "high": lambda s: True,  # All stages
            "medium": lambda s: not self._is_expensive_stage(s),
            "low": lambda s: self._is_critical_stage(s)
        }

        filter_func = profile_filters.get(profile, lambda s: True)
        selected = [stage for stage in available_stages if filter_func(stage)]

        self.logger.log(
            f"Selected {len(selected)}/{len(available_stages)} stages for {profile} resources",
            "INFO"
        )

        return selected

    def _determine_profile(self, cpu: int, memory: int, time: int) -> str:
        """
        Determine resource profile based on available resources.

        Why helper method: Extracts complex nested if logic into named,
        testable method. Uses guard clauses instead of nested ifs.
        """
        # Guard clause: Low resources
        if cpu <= 2 or memory <= 4 or time <= 30:
            return "low"

        # Guard clause: High resources
        if cpu >= 8 and memory >= 16 and time >= 120:
            return "high"

        # Default: Medium resources
        return "medium"

    def _is_expensive_stage(self, stage: PipelineStage) -> bool:
        """Check if stage is resource-intensive"""
        expensive_stages = {"performance", "load_test", "security_scan", "ui_test"}
        return any(name in stage.name.lower() for name in expensive_stages)

    def _is_critical_stage(self, stage: PipelineStage) -> bool:
        """Check if stage is critical (must run even with low resources)"""
        critical_stages = {"requirements", "development", "unit_tests"}
        return any(name in stage.name.lower() for name in critical_stages)


class ManualSelector(StageSelectionStrategy):
    """
    Selects stages based on explicit user configuration.

    Why it exists: Users may want specific stage combinations for
    debugging, testing, or custom workflows.

    Design pattern: Strategy implementation
    """

    def __init__(self, selected_stage_names: List[str], logger: Optional[PipelineLogger] = None):
        self.selected_stage_names = set(selected_stage_names)  # O(1) lookup
        self.logger = logger or PipelineLogger(verbose=True)

    @wrap_exception(PipelineException, "Failed to select stages manually")
    def select_stages(
        self,
        available_stages: List[PipelineStage],
        context: Dict[str, Any]
    ) -> List[PipelineStage]:
        """Select stages matching configured names"""

        # Filter stages by name using set membership (O(1) per check)
        selected = [
            stage for stage in available_stages
            if stage.name in self.selected_stage_names
        ]

        # Warn about missing stages using set difference
        available_names = {stage.name for stage in available_stages}
        missing = self.selected_stage_names - available_names

        if missing:
            self.logger.log(
                f"Warning: Requested stages not found: {missing}",
                "WARNING"
            )

        self.logger.log(
            f"Manually selected {len(selected)}/{len(available_stages)} stages",
            "INFO"
        )

        return selected


# ============================================================================
# RETRY POLICY
# ============================================================================

@dataclass
class RetryPolicy:
    """
    Configuration for stage retry behavior.

    Why it exists: Transient failures (network, rate limits) should retry,
    permanent failures (syntax errors) should not. Encapsulates retry logic.

    Design pattern: Configuration Object

    Retry strategy:
    - Retries only specified exception types
    - Exponential backoff between attempts
    - Maximum retry limit
    - Per-stage override capability
    """
    max_retries: int = 3
    retryable_exceptions: Set[type] = field(default_factory=lambda: {
        # Examples of retryable exception types
        # In real system, import actual exception classes
        Exception  # Placeholder - replace with actual retryable types
    })
    backoff_multiplier: float = 2.0
    initial_delay: float = 1.0

    def should_retry(self, exception: Exception, attempt: int) -> bool:
        """
        Determine if exception should trigger retry.

        Why needed: Centralizes retry decision logic. Checks both exception
        type and attempt count.

        Args:
            exception: Exception that occurred
            attempt: Current attempt number (0-indexed)

        Returns:
            True if should retry, False if should fail
        """
        # Guard clause: Exceeded max retries
        if attempt >= self.max_retries:
            return False

        # Check if exception type is retryable
        return any(isinstance(exception, exc_type) for exc_type in self.retryable_exceptions)

    def get_delay(self, attempt: int) -> float:
        """
        Calculate delay before next retry (exponential backoff).

        Why needed: Exponential backoff prevents thundering herd and
        gives transient issues time to resolve.

        Args:
            attempt: Attempt number (0-indexed)

        Returns:
            Delay in seconds before next retry
        """
        return self.initial_delay * (self.backoff_multiplier ** attempt)


# ============================================================================
# STAGE EXECUTOR
# ============================================================================

class StageExecutor:
    """
    Executes pipeline stages with retry, skip, and error handling.

    Why it exists: Centralizes stage execution logic including retry policies,
    conditional execution, error handling, and event emission.

    Design pattern: Chain of Responsibility + Decorator

    Responsibilities:
    - Execute individual stages
    - Handle retries according to policy
    - Skip stages based on conditions
    - Emit events for all operations
    - Catch and wrap exceptions
    - Track execution metrics (duration, retry count)

    Execution flow:
    1. Check if should execute (conditional)
    2. Execute stage
    3. On failure, check retry policy
    4. Retry with backoff if allowed
    5. Emit events for all outcomes
    """

    def __init__(
        self,
        observable: PipelineObservable,
        retry_policy: Optional[RetryPolicy] = None,
        logger: Optional[PipelineLogger] = None
    ):
        self.observable = observable
        self.retry_policy = retry_policy or RetryPolicy()
        self.logger = logger or PipelineLogger(verbose=True)

    @wrap_exception(PipelineException, "Failed to execute stage")
    def execute_stage(
        self,
        stage: PipelineStage,
        context: Dict[str, Any],
        card_id: str
    ) -> StageResult:
        """
        Execute single stage with retry and error handling.

        Why needed: Core stage execution with full error handling, retry
        logic, and event emission. Provides consistent execution behavior.

        Args:
            stage: Stage to execute
            context: Execution context from previous stages
            card_id: Card ID for event tracking

        Returns:
            StageResult with execution outcome

        Raises:
            PipelineException: If stage fails after all retries
        """
        # Guard clause: Check if stage should execute
        if not stage.should_execute(context):
            return self._handle_skip(stage, context, card_id)

        # Execute with retry loop
        # Why loop extraction: Separates retry logic into helper method
        return self._execute_with_retry(stage, context, card_id)

    def _handle_skip(
        self,
        stage: PipelineStage,
        context: Dict[str, Any],
        card_id: str
    ) -> StageResult:
        """
        Handle stage skip (conditional execution returned False).

        Why helper method: Extracts skip handling logic, avoids nested if.
        """
        self.logger.log(f"Skipping stage: {stage.name}", "INFO")

        # Emit skip event
        self.observable.notify(PipelineEvent(
            event_type=EventType.STAGE_SKIPPED,
            card_id=card_id,
            stage_name=stage.name,
            data={"reason": "conditional_execution"}
        ))

        return StageResult(
            stage_name=stage.name,
            success=True,
            skipped=True
        )

    def _execute_with_retry(
        self,
        stage: PipelineStage,
        context: Dict[str, Any],
        card_id: str
    ) -> StageResult:
        """
        Execute stage with retry logic.

        Why helper method: Extracts retry loop from main execute method,
        avoiding nested loops and improving testability.
        """
        attempt = 0
        last_exception = None

        # Retry loop - extracted to avoid nesting in main method
        while attempt <= self.retry_policy.max_retries:
            try:
                # Attempt execution
                result = self._attempt_execution(stage, context, card_id, attempt)

                # Success - return result
                return result

            except Exception as e:
                last_exception = e

                # Check if should retry
                if not self.retry_policy.should_retry(e, attempt):
                    break

                # Handle retry with backoff
                self._handle_retry(stage, card_id, attempt, e)
                attempt += 1

        # All retries exhausted - fail
        return self._handle_failure(stage, card_id, last_exception, attempt)

    def _attempt_execution(
        self,
        stage: PipelineStage,
        context: Dict[str, Any],
        card_id: str,
        attempt: int
    ) -> StageResult:
        """
        Attempt single stage execution.

        Why helper method: Separates single execution attempt from retry
        logic, enables clean event emission and timing.
        """
        # Emit start event
        self.observable.notify(PipelineEvent(
            event_type=EventType.STAGE_STARTED,
            card_id=card_id,
            stage_name=stage.name,
            data={"attempt": attempt}
        ))

        # Execute stage and time it
        start_time = datetime.now()
        result = stage.execute(context)
        duration = (datetime.now() - start_time).total_seconds()

        # Update result with metadata
        result.duration = duration
        result.retry_count = attempt

        # Emit completion event
        self.observable.notify(PipelineEvent(
            event_type=EventType.STAGE_COMPLETED,
            card_id=card_id,
            stage_name=stage.name,
            data={
                "duration": duration,
                "retry_count": attempt,
                "result": result.data
            }
        ))

        return result

    def _handle_retry(
        self,
        stage: PipelineStage,
        card_id: str,
        attempt: int,
        error: Exception
    ) -> None:
        """
        Handle retry preparation (logging, events, backoff).

        Why helper method: Extracts retry handling logic, avoids nesting.
        """
        delay = self.retry_policy.get_delay(attempt)

        self.logger.log(
            f"Stage {stage.name} failed (attempt {attempt + 1}), "
            f"retrying in {delay:.1f}s: {error}",
            "WARNING"
        )

        # Emit retry event
        self.observable.notify(PipelineEvent(
            event_type=EventType.STAGE_RETRYING,
            card_id=card_id,
            stage_name=stage.name,
            data={
                "attempt": attempt + 1,
                "delay": delay,
                "error": str(error)
            }
        ))

        # Backoff delay
        import time
        time.sleep(delay)

    def _handle_failure(
        self,
        stage: PipelineStage,
        card_id: str,
        error: Exception,
        attempts: int
    ) -> StageResult:
        """
        Handle final stage failure after all retries.

        Why helper method: Separates failure handling, enables clean
        event emission and error wrapping.
        """
        self.logger.log(
            f"Stage {stage.name} failed after {attempts} attempts: {error}",
            "ERROR"
        )

        # Emit failure event
        self.observable.notify(PipelineEvent(
            event_type=EventType.STAGE_FAILED,
            card_id=card_id,
            stage_name=stage.name,
            error=error,
            data={"attempts": attempts}
        ))

        return StageResult(
            stage_name=stage.name,
            success=False,
            error=error,
            retry_count=attempts
        )


# ============================================================================
# PARALLEL EXECUTOR
# ============================================================================

class ParallelStageExecutor:
    """
    Executes stages in parallel where dependencies allow.

    Why it exists: Sequential execution wastes time when stages are independent.
    Parallel execution can dramatically reduce pipeline duration.

    Design pattern: Executor + Dependency Resolution

    Responsibilities:
    - Build dependency graph from stage dependencies
    - Identify parallelizable stage groups
    - Execute independent stages concurrently
    - Wait for dependencies before starting dependent stages
    - Aggregate results from parallel executions

    Execution algorithm:
    1. Build dependency graph (directed acyclic graph)
    2. Identify stages with no dependencies (level 0)
    3. Execute level 0 stages in parallel
    4. Once complete, identify next level (dependencies met)
    5. Repeat until all stages executed

    Thread safety: Uses ThreadPoolExecutor for parallel execution with
    proper result aggregation. Stage execution must be thread-safe.
    """

    def __init__(
        self,
        executor: StageExecutor,
        max_workers: int = 4,
        logger: Optional[PipelineLogger] = None
    ):
        self.executor = executor
        self.max_workers = max_workers
        self.logger = logger or PipelineLogger(verbose=True)

    @wrap_exception(PipelineException, "Failed to execute stages in parallel")
    def execute_stages_parallel(
        self,
        stages: List[PipelineStage],
        context: Dict[str, Any],
        card_id: str
    ) -> Dict[str, StageResult]:
        """
        Execute stages in parallel respecting dependencies.

        Why needed: Reduces pipeline duration by running independent stages
        concurrently while ensuring dependency order is preserved.

        Args:
            stages: Stages to execute
            context: Shared execution context
            card_id: Card ID for tracking

        Returns:
            Dict mapping stage name to StageResult

        Raises:
            PipelineException: If dependency cycle detected or stage fails
        """
        # Build dependency graph using helper method
        dep_graph = self._build_dependency_graph(stages)

        # Detect cycles using helper method
        if self._has_cycle(dep_graph):
            raise PipelineException(
                "Dependency cycle detected in pipeline stages",
                context={"stages": [s.name for s in stages]}
            )

        # Execute stages level by level
        return self._execute_by_levels(stages, dep_graph, context, card_id)

    def _build_dependency_graph(
        self,
        stages: List[PipelineStage]
    ) -> Dict[str, Set[str]]:
        """
        Build dependency graph from stage dependencies.

        Why helper method: Separates graph building logic, makes it testable.
        Uses set for O(1) dependency lookups.

        Args:
            stages: List of pipeline stages

        Returns:
            Dict mapping stage name to set of dependency names
        """
        return {
            stage.name: set(stage.get_dependencies())
            for stage in stages
        }

    def _has_cycle(self, dep_graph: Dict[str, Set[str]]) -> bool:
        """
        Detect cycles in dependency graph using DFS.

        Why helper method: Separates cycle detection logic, improves
        readability and testability. Uses standard DFS algorithm.

        Args:
            dep_graph: Dependency graph (adjacency list)

        Returns:
            True if cycle exists, False otherwise
        """
        visited = set()
        rec_stack = set()

        def has_cycle_dfs(node: str) -> bool:
            """DFS helper for cycle detection"""
            # Guard clause: Already processed
            if node in visited:
                return False

            # Guard clause: In recursion stack (cycle!)
            if node in rec_stack:
                return True

            # Mark as visiting
            rec_stack.add(node)

            # Visit dependencies
            for dep in dep_graph.get(node, set()):
                if has_cycle_dfs(dep):
                    return True

            # Mark as visited
            rec_stack.remove(node)
            visited.add(node)
            return False

        # Check each node
        return any(has_cycle_dfs(node) for node in dep_graph if node not in visited)

    def _execute_by_levels(
        self,
        stages: List[PipelineStage],
        dep_graph: Dict[str, Set[str]],
        context: Dict[str, Any],
        card_id: str
    ) -> Dict[str, StageResult]:
        """
        Execute stages level by level based on dependencies.

        Why helper method: Extracts level-based execution logic from main
        method. Avoids nested loops by extracting level processing.

        Args:
            stages: Stages to execute
            dep_graph: Dependency graph
            context: Execution context
            card_id: Card ID for tracking

        Returns:
            Dict of stage results
        """
        stage_map = {stage.name: stage for stage in stages}
        results: Dict[str, StageResult] = {}
        completed = set()

        # Process stages level by level
        while len(completed) < len(stages):
            # Find next level (stages with all dependencies met)
            next_level = self._find_next_level(dep_graph, completed)

            # Guard clause: No progress (shouldn't happen if no cycles)
            if not next_level:
                break

            # Execute level in parallel
            level_results = self._execute_level(
                [stage_map[name] for name in next_level],
                context,
                card_id
            )

            # Update results and completed set
            results.update(level_results)
            completed.update(next_level)

            # Guard clause: Any stage failed
            if any(not r.is_success() for r in level_results.values()):
                self.logger.log(
                    "Stage failure in parallel execution, stopping pipeline",
                    "ERROR"
                )
                break

        return results

    def _find_next_level(
        self,
        dep_graph: Dict[str, Set[str]],
        completed: Set[str]
    ) -> List[str]:
        """
        Find stages ready to execute (all dependencies completed).

        Why helper method: Extracts next level finding logic, avoids
        nested loops in main execution method.

        Args:
            dep_graph: Dependency graph
            completed: Set of completed stage names

        Returns:
            List of stage names ready to execute
        """
        return [
            stage_name
            for stage_name, deps in dep_graph.items()
            if stage_name not in completed and deps.issubset(completed)
        ]

    def _execute_level(
        self,
        stages: List[PipelineStage],
        context: Dict[str, Any],
        card_id: str
    ) -> Dict[str, StageResult]:
        """
        Execute single level of stages in parallel.

        Why helper method: Separates parallel execution logic from level
        iteration. Encapsulates ThreadPoolExecutor usage.

        Args:
            stages: Stages to execute in parallel
            context: Execution context
            card_id: Card ID for tracking

        Returns:
            Dict of stage results
        """
        # Guard clause: Single stage (no parallelism needed)
        if len(stages) == 1:
            stage = stages[0]
            result = self.executor.execute_stage(stage, context, card_id)
            return {stage.name: result}

        # Parallel execution using ThreadPoolExecutor
        self.logger.log(
            f"Executing {len(stages)} stages in parallel: {[s.name for s in stages]}",
            "INFO"
        )

        results = {}
        with ThreadPoolExecutor(max_workers=self.max_workers) as pool:
            # Submit all stages
            future_to_stage = {
                pool.submit(self.executor.execute_stage, stage, context, card_id): stage
                for stage in stages
            }

            # Collect results as they complete
            for future in as_completed(future_to_stage):
                stage = future_to_stage[future]
                result = future.result()
                results[stage.name] = result

        return results


# ============================================================================
# DYNAMIC PIPELINE BUILDER
# ============================================================================

class DynamicPipelineBuilder:
    """
    Builder for constructing dynamic pipelines with fluent API.

    Why it exists: Pipeline construction involves many configuration options.
    Builder pattern provides clear, fluent API and validates configuration
    before creating pipeline.

    Design pattern: Builder Pattern

    Responsibilities:
    - Collect pipeline configuration (stages, strategies, policies)
    - Validate configuration (no duplicates, dependencies exist)
    - Create configured DynamicPipeline instance
    - Provide fluent interface for ergonomic construction

    Usage example:
        pipeline = (DynamicPipelineBuilder()
            .with_name("feature-123")
            .with_strategy(ComplexityBasedSelector())
            .add_stages([stage1, stage2, stage3])
            .with_retry_policy(RetryPolicy(max_retries=5))
            .with_parallelism(enabled=True, max_workers=4)
            .build())
    """

    def __init__(self):
        self._name: Optional[str] = None
        self._stages: List[PipelineStage] = []
        self._strategy: Optional[StageSelectionStrategy] = None
        self._retry_policy: RetryPolicy = RetryPolicy()
        self._observable: PipelineObservable = PipelineObservable(verbose=True)
        self._parallel_enabled: bool = False
        self._max_workers: int = 4
        self._context: Dict[str, Any] = {}
        self.logger = PipelineLogger(verbose=True)

    def with_name(self, name: str) -> 'DynamicPipelineBuilder':
        """
        Set pipeline name.

        Why needed: Name used for logging, metrics, and identification.

        Args:
            name: Pipeline name (usually card ID or feature name)

        Returns:
            Self for method chaining
        """
        self._name = name
        return self

    def add_stage(self, stage: PipelineStage) -> 'DynamicPipelineBuilder':
        """
        Add single stage to pipeline.

        Args:
            stage: Stage to add

        Returns:
            Self for method chaining
        """
        self._stages.append(stage)
        return self

    def add_stages(self, stages: List[PipelineStage]) -> 'DynamicPipelineBuilder':
        """
        Add multiple stages to pipeline.

        Args:
            stages: Stages to add

        Returns:
            Self for method chaining
        """
        self._stages.extend(stages)
        return self

    def with_strategy(self, strategy: StageSelectionStrategy) -> 'DynamicPipelineBuilder':
        """
        Set stage selection strategy.

        Args:
            strategy: Selection strategy (complexity, resource, manual)

        Returns:
            Self for method chaining
        """
        self._strategy = strategy
        return self

    def with_retry_policy(self, policy: RetryPolicy) -> 'DynamicPipelineBuilder':
        """
        Set retry policy for stage failures.

        Args:
            policy: Retry policy configuration

        Returns:
            Self for method chaining
        """
        self._retry_policy = policy
        return self

    def with_observable(self, observable: PipelineObservable) -> 'DynamicPipelineBuilder':
        """
        Set pipeline observable for event broadcasting.

        Args:
            observable: Observable with attached observers

        Returns:
            Self for method chaining
        """
        self._observable = observable
        return self

    def with_parallelism(
        self,
        enabled: bool,
        max_workers: int = 4
    ) -> 'DynamicPipelineBuilder':
        """
        Configure parallel stage execution.

        Args:
            enabled: Enable parallel execution
            max_workers: Maximum parallel workers

        Returns:
            Self for method chaining
        """
        self._parallel_enabled = enabled
        self._max_workers = max_workers
        return self

    def with_context(self, context: Dict[str, Any]) -> 'DynamicPipelineBuilder':
        """
        Set initial pipeline context.

        Args:
            context: Initial context data (complexity, resources, config)

        Returns:
            Self for method chaining
        """
        self._context = context
        return self

    @wrap_exception(PipelineException, "Failed to build dynamic pipeline")
    def build(self) -> 'DynamicPipeline':
        """
        Build and validate pipeline.

        Why needed: Final validation before creating pipeline. Ensures
        all required configuration present and valid.

        Returns:
            Configured DynamicPipeline instance

        Raises:
            PipelineException: If configuration invalid
        """
        # Validate configuration using helper method
        self._validate()

        # Create executor
        executor = StageExecutor(
            observable=self._observable,
            retry_policy=self._retry_policy,
            logger=self.logger
        )

        # Create parallel executor if enabled
        parallel_executor = None
        if self._parallel_enabled:
            parallel_executor = ParallelStageExecutor(
                executor=executor,
                max_workers=self._max_workers,
                logger=self.logger
            )

        # Build pipeline
        pipeline = DynamicPipeline(
            name=self._name or "unnamed-pipeline",
            stages=self._stages,
            strategy=self._strategy,
            executor=executor,
            parallel_executor=parallel_executor,
            observable=self._observable,
            initial_context=self._context,
            logger=self.logger
        )

        self.logger.log(
            f"Built pipeline '{pipeline.name}' with {len(self._stages)} stages",
            "SUCCESS"
        )

        return pipeline

    def _validate(self) -> None:
        """
        Validate builder configuration.

        Why helper method: Extracts validation logic from build(), uses
        guard clauses to avoid nested ifs.

        Raises:
            PipelineException: If configuration invalid
        """
        # Guard clause: No stages
        if not self._stages:
            raise PipelineException(
                "Pipeline must have at least one stage",
                context={"name": self._name}
            )

        # Guard clause: Duplicate stage names
        stage_names = [s.name for s in self._stages]
        duplicates = {name for name in stage_names if stage_names.count(name) > 1}
        if duplicates:
            raise PipelineException(
                "Pipeline has duplicate stage names",
                context={"duplicates": list(duplicates)}
            )

        # Guard clause: Invalid dependencies
        stage_name_set = set(stage_names)
        for stage in self._stages:
            invalid_deps = set(stage.get_dependencies()) - stage_name_set
            if invalid_deps:
                raise PipelineException(
                    f"Stage '{stage.name}' has invalid dependencies",
                    context={"invalid_dependencies": list(invalid_deps)}
                )


# ============================================================================
# DYNAMIC PIPELINE
# ============================================================================

class DynamicPipeline(AdvancedFeaturesAIMixin):
    """
    Dynamic pipeline with runtime adaptability.

    Why it exists: Core pipeline execution engine that orchestrates stages,
    applies selection strategies, handles errors, and emits events.

    Design pattern: Facade + State Pattern + Mixin (for DRY AI calls)

    NEW: Hybrid AI Approach:
    - Receives initial analysis from router (intensity, suggested workers, etc.)
    - Uses AI service from context for adaptive calls (when needed)
    - Inherits DRY AI query methods from AdvancedFeaturesAIMixin

    Responsibilities:
    - Manage pipeline lifecycle (created -> running -> completed/failed)
    - Apply stage selection strategy
    - Execute stages sequentially or in parallel
    - Maintain execution context
    - Emit lifecycle events
    - Support runtime modifications (add/remove stages)
    - Cache stage results
    - Make adaptive AI calls for optimization decisions

    State transitions:
        CREATED -> READY -> RUNNING -> (PAUSED <-> RUNNING)* -> COMPLETED/FAILED

    Thread safety: Not thread-safe (assumes single-threaded orchestrator)
    """

    def __init__(
        self,
        name: str,
        stages: List[PipelineStage],
        strategy: Optional[StageSelectionStrategy],
        executor: StageExecutor,
        parallel_executor: Optional[ParallelStageExecutor],
        observable: PipelineObservable,
        initial_context: Dict[str, Any],
        logger: PipelineLogger
    ):
        self.name = name
        self.available_stages = stages
        self.strategy = strategy
        self.executor = executor
        self.parallel_executor = parallel_executor
        self.observable = observable
        self.context = initial_context.copy()
        self.logger = logger

        # NEW: Extract router context for hybrid AI approach
        self.ai_service = initial_context.get('ai_service')  # For adaptive calls
        self.router_intensity = initial_context.get('intensity', 0.5)
        self.router_guidance = initial_context.get('prompt', '')
        self.suggested_workers = initial_context.get('suggested_max_workers', 4)
        self.priority_stages = initial_context.get('stages_to_prioritize', [])
        self.optional_stages = initial_context.get('stages_optional', [])

        # Pipeline state
        self.state = PipelineState.CREATED
        self.selected_stages: List[PipelineStage] = []
        self.results: Dict[str, StageResult] = {}
        self.result_cache: Dict[str, StageResult] = {}

        # Transition to ready state
        self._transition_to_ready()

    def _transition_to_ready(self) -> None:
        """
        Transition pipeline to READY state.

        Why helper method: Separates state transition logic, ensures
        proper state validation before execution.
        """
        # Apply selection strategy if configured
        if self.strategy:
            self.selected_stages = self.strategy.select_stages(
                self.available_stages,
                self.context
            )
        else:
            # No strategy - use all stages
            self.selected_stages = self.available_stages

        self.state = PipelineState.READY

        self.logger.log(
            f"Pipeline '{self.name}' ready with {len(self.selected_stages)} selected stages",
            "INFO"
        )

    @wrap_exception(PipelineException, "Failed to execute pipeline")
    def execute(self, card_id: str) -> Dict[str, StageResult]:
        """
        Execute pipeline for given card.

        Why needed: Main pipeline execution method. Orchestrates stage
        execution, handles errors, emits events, manages state.

        Args:
            card_id: Card ID for tracking and events

        Returns:
            Dict mapping stage name to StageResult

        Raises:
            PipelineException: If pipeline not ready or execution fails
        """
        # Guard clause: Validate state
        if self.state != PipelineState.READY:
            raise PipelineException(
                f"Pipeline not ready for execution (state: {self.state})",
                context={"pipeline": self.name, "card_id": card_id}
            )

        # Transition to running
        self.state = PipelineState.RUNNING
        self.context["card_id"] = card_id

        # Emit start event
        self.observable.notify(PipelineEvent(
            event_type=EventType.PIPELINE_STARTED,
            card_id=card_id,
            data={
                "pipeline": self.name,
                "stage_count": len(self.selected_stages)
            }
        ))

        try:
            # Execute stages (parallel or sequential)
            if self.parallel_executor:
                self.results = self.parallel_executor.execute_stages_parallel(
                    self.selected_stages,
                    self.context,
                    card_id
                )
            else:
                self.results = self._execute_sequential(card_id)

            # Check for failures
            failures = [r for r in self.results.values() if not r.is_success()]

            if failures:
                # Pipeline failed
                self._handle_pipeline_failure(card_id, failures)
            else:
                # Pipeline succeeded
                self._handle_pipeline_success(card_id)

            return self.results

        except Exception as e:
            # Unexpected error
            self._handle_pipeline_error(card_id, e)
            raise

    def _execute_sequential(self, card_id: str) -> Dict[str, StageResult]:
        """
        Execute stages sequentially.

        Why helper method: Separates sequential execution logic from main
        execute method. Avoids nested loops.

        Args:
            card_id: Card ID for tracking

        Returns:
            Dict of stage results
        """
        results = {}

        for stage in self.selected_stages:
            # Check cache first
            if stage.name in self.result_cache:
                self.logger.log(f"Using cached result for {stage.name}", "DEBUG")
                results[stage.name] = self.result_cache[stage.name]
                continue

            # Execute stage
            result = self.executor.execute_stage(stage, self.context, card_id)
            results[stage.name] = result

            # Cache successful results
            if result.is_success():
                self.result_cache[stage.name] = result
                # Update context with stage results
                self.context[f"{stage.name}_result"] = result.data

            # Guard clause: Stage failed
            if not result.is_success():
                self.logger.log(
                    f"Stage {stage.name} failed, stopping pipeline",
                    "ERROR"
                )
                break

        return results

    def _handle_pipeline_success(self, card_id: str) -> None:
        """
        Handle successful pipeline completion.

        Why helper method: Extracts success handling, avoids nested if.
        """
        self.state = PipelineState.COMPLETED

        self.logger.log(f"Pipeline '{self.name}' completed successfully", "SUCCESS")

        self.observable.notify(PipelineEvent(
            event_type=EventType.PIPELINE_COMPLETED,
            card_id=card_id,
            data={
                "pipeline": self.name,
                "stage_count": len(self.results)
            }
        ))

    def _handle_pipeline_failure(
        self,
        card_id: str,
        failures: List[StageResult]
    ) -> None:
        """
        Handle pipeline failure due to stage failures.

        Why helper method: Extracts failure handling logic, enables
        clean error aggregation and event emission.
        """
        self.state = PipelineState.FAILED

        failure_info = [
            f"{r.stage_name}: {r.error}"
            for r in failures
        ]

        self.logger.log(
            f"Pipeline '{self.name}' failed: {failure_info}",
            "ERROR"
        )

        self.observable.notify(PipelineEvent(
            event_type=EventType.PIPELINE_FAILED,
            card_id=card_id,
            data={
                "pipeline": self.name,
                "failures": failure_info
            }
        ))

    def _handle_pipeline_error(self, card_id: str, error: Exception) -> None:
        """
        Handle unexpected pipeline error.

        Why helper method: Separates error handling from main flow,
        ensures consistent event emission.
        """
        self.state = PipelineState.FAILED

        self.logger.log(
            f"Pipeline '{self.name}' encountered error: {error}",
            "ERROR"
        )

        self.observable.notify(PipelineEvent(
            event_type=EventType.PIPELINE_FAILED,
            card_id=card_id,
            error=error,
            data={"pipeline": self.name}
        ))

    @wrap_exception(PipelineException, "Failed to pause pipeline")
    def pause(self) -> None:
        """
        Pause pipeline execution.

        Why needed: Enables supervisor to pause long-running pipelines
        for resource management or debugging.

        Note: Currently marks state as paused. Full implementation would
        need to coordinate with executor to stop after current stage.
        """
        # Guard clause: Not running
        if self.state != PipelineState.RUNNING:
            raise PipelineException(
                "Cannot pause pipeline that is not running",
                context={"state": self.state.value}
            )

        self.state = PipelineState.PAUSED
        self.logger.log("Pipeline paused", "INFO")

        self.observable.notify(PipelineEvent(
            event_type=EventType.PIPELINE_PAUSED,
            card_id=self.context.get("card_id"),
            data={"pipeline": self.name}
        ))

    @wrap_exception(PipelineException, "Failed to resume pipeline")
    def resume(self) -> None:
        """
        Resume paused pipeline execution.

        Why needed: Enables resuming after pause for debugging or
        resource availability.
        """
        # Guard clause: Not paused
        if self.state != PipelineState.PAUSED:
            raise PipelineException(
                "Cannot resume pipeline that is not paused",
                context={"state": self.state.value}
            )

        self.state = PipelineState.RUNNING
        self.logger.log("Pipeline resumed", "INFO")

        self.observable.notify(PipelineEvent(
            event_type=EventType.PIPELINE_RESUMED,
            card_id=self.context.get("card_id"),
            data={"pipeline": self.name}
        ))

    @wrap_exception(PipelineException, "Failed to add stage at runtime")
    def add_stage_runtime(self, stage: PipelineStage) -> None:
        """
        Add stage to pipeline at runtime.

        Why needed: Enables dynamic pipeline modification based on
        intermediate results or supervisor commands.

        Args:
            stage: Stage to add

        Raises:
            PipelineException: If pipeline is running
        """
        # Guard clause: Cannot modify running pipeline
        if self.state == PipelineState.RUNNING:
            raise PipelineException(
                "Cannot add stage to running pipeline",
                context={"stage": stage.name}
            )

        self.available_stages.append(stage)
        self.selected_stages.append(stage)

        self.logger.log(f"Added stage at runtime: {stage.name}", "INFO")

    @wrap_exception(PipelineException, "Failed to remove stage at runtime")
    def remove_stage_runtime(self, stage_name: str) -> None:
        """
        Remove stage from pipeline at runtime.

        Why needed: Enables skipping stages based on conditions or
        supervisor override.

        Args:
            stage_name: Name of stage to remove

        Raises:
            PipelineException: If pipeline is running
        """
        # Guard clause: Cannot modify running pipeline
        if self.state == PipelineState.RUNNING:
            raise PipelineException(
                "Cannot remove stage from running pipeline",
                context={"stage": stage_name}
            )

        self.selected_stages = [
            s for s in self.selected_stages
            if s.name != stage_name
        ]

        self.logger.log(f"Removed stage at runtime: {stage_name}", "INFO")

    def get_state(self) -> PipelineState:
        """Get current pipeline state"""
        return self.state

    def get_results(self) -> Dict[str, StageResult]:
        """Get all stage results"""
        return self.results.copy()

    def get_context(self) -> Dict[str, Any]:
        """Get current execution context"""
        return self.context.copy()

    def clear_cache(self) -> None:
        """Clear result cache"""
        self.result_cache.clear()
        self.logger.log("Result cache cleared", "DEBUG")

    # ========================================================================
    # HYBRID AI METHODS (Using Mixin)
    # ========================================================================

    @wrap_exception(PipelineException, "AI-enhanced stage optimization failed")
    def optimize_stage_execution_with_ai(
        self,
        stages: List[PipelineStage],
        context: Dict[str, Any],
        use_initial_analysis: bool = True
    ) -> Dict[str, Any]:
        """
        Optimize stage execution using hybrid AI approach.

        NEW: Demonstrates hybrid pattern for DynamicPipeline:
        1. Start with router's pre-computed intensity and priority stages (free!)
        2. Make adaptive AI call if more optimization needed (via mixin)
        3. Return optimized execution plan

        WHY: Shows integration of router context + adaptive AI calls for pipeline optimization.

        Args:
            stages: Stages to optimize
            context: Execution context
            use_initial_analysis: If True, uses router's pre-computed analysis first

        Returns:
            Dict with optimized execution plan including:
                - execution_order: List[str] - Optimized stage order
                - parallel_groups: List[List[str]] - Stages that can run in parallel
                - max_workers: int - Suggested parallelization
                - skip_optional: List[str] - Optional stages that can be skipped
                - intensity: float - Execution intensity
                - source: str - Where optimization came from

        Usage:
            # Uses hybrid approach
            plan = pipeline.optimize_stage_execution_with_ai(
                stages=available_stages,
                context=execution_context
            )
        """
        # HYBRID STEP 1: Use router's pre-computed analysis (FREE!)
        if use_initial_analysis and self.router_intensity is not None:
            # Router already provided optimization guidance
            initial_intensity = self.router_intensity

            # If intensity is low (< 0.5), use simple execution plan
            if initial_intensity < 0.5:
                return {
                    'execution_order': [s.name for s in stages],
                    'parallel_groups': [],  # Sequential execution
                    'max_workers': self.suggested_workers,
                    'skip_optional': self.optional_stages,
                    'intensity': initial_intensity,
                    'source': 'router_precomputed',
                    'cost': 0.0  # Free!
                }

        # HYBRID STEP 2: Higher intensity or no initial analysis - make adaptive AI call
        if not self.ai_service:
            # Fallback: No AI service available, use router's guidance
            fallback_intensity = self.router_intensity if self.router_intensity else 0.5
            return {
                'execution_order': [s.name for s in stages],
                'parallel_groups': [[s.name for s in stages[:self.suggested_workers]]],
                'max_workers': self.suggested_workers,
                'skip_optional': self.optional_stages,
                'intensity': fallback_intensity,
                'source': 'fallback_no_ai_service',
                'warning': 'No AI service available'
            }

        # Make AI call via mixin method for complexity analysis (DRY!)
        stage_descriptions = "\n".join([
            f"- {s.name}: {s.get_description()}" for s in stages
        ])

        complexity_level, estimated_duration, analysis = self.query_for_complexity(
            requirements=stage_descriptions,
            context=f"Initial intensity: {self.router_intensity:.0%}. "
                   f"Priority stages: {', '.join(self.priority_stages)}. "
                   f"Router guidance: {self.router_guidance[:200]}..."
        )

        # Build optimized execution plan based on AI analysis
        complexity_to_workers = {
            'simple': 2,
            'moderate': 4,
            'complex': 6,
            'very_complex': 8
        }

        ai_suggested_workers = complexity_to_workers.get(complexity_level, self.suggested_workers)

        # Prioritize based on router + AI analysis
        priority_set = set(self.priority_stages)
        optional_set = set(self.optional_stages)

        priority_stages_list = [s for s in stages if s.name in priority_set]
        normal_stages_list = [s for s in stages if s.name not in priority_set and s.name not in optional_set]
        optional_stages_list = [s for s in stages if s.name in optional_set]

        execution_order = (
            [s.name for s in priority_stages_list] +
            [s.name for s in normal_stages_list] +
            [s.name for s in optional_stages_list]
        )

        # Create parallel groups (stages that can run together)
        parallel_groups = []
        if ai_suggested_workers > 1:
            # Group non-dependent stages
            for i in range(0, len(execution_order), ai_suggested_workers):
                group = execution_order[i:i + ai_suggested_workers]
                if len(group) > 1:
                    parallel_groups.append(group)

        return {
            'execution_order': execution_order,
            'parallel_groups': parallel_groups,
            'max_workers': ai_suggested_workers,
            'skip_optional': [s.name for s in optional_stages_list],
            'intensity': self.router_intensity,
            'source': 'ai_optimized',
            'complexity_level': complexity_level,
            'estimated_duration': estimated_duration,
            'ai_analysis': analysis,
            'initial_intensity': self.router_intensity,
            'improvement': 'adaptive_optimization_applied'
        }

    @wrap_exception(PipelineException, "AI-enhanced parallelization assessment failed")
    def assess_parallelization_with_ai(
        self,
        stages: List[PipelineStage],
        context: Dict[str, Any],
        use_initial_analysis: bool = True
    ) -> Dict[str, Any]:
        """
        Assess parallelization strategy using hybrid AI approach.

        NEW: Uses mixin's complexity query to refine parallelization (DRY!).

        Args:
            stages: Stages to assess for parallelization
            context: Execution context
            use_initial_analysis: If True, uses router's suggested workers first

        Returns:
            Dict with parallelization assessment:
                - recommended_workers: int - Number of parallel workers
                - can_parallelize: List[str] - Stages safe to parallelize
                - must_serialize: List[str] - Stages requiring sequential execution
                - safety_score: float - Confidence in parallelization safety
                - source: str - Where assessment came from

        Usage:
            assessment = pipeline.assess_parallelization_with_ai(
                stages=selected_stages,
                context=execution_context
            )
        """
        # HYBRID STEP 1: Use router's pre-computed workers (FREE!)
        if use_initial_analysis and self.suggested_workers is not None:
            # Router already suggested worker count based on intensity
            if self.suggested_workers <= 2:
                # Low parallelization, simple assessment sufficient
                return {
                    'recommended_workers': self.suggested_workers,
                    'can_parallelize': [],
                    'must_serialize': [s.name for s in stages],
                    'safety_score': 1.0,  # Conservative = safe
                    'source': 'router_precomputed',
                    'cost': 0.0  # Free!
                }

        # HYBRID STEP 2: Higher parallelization - make adaptive AI call
        if not self.ai_service:
            # Fallback: Use router's guidance conservatively
            return {
                'recommended_workers': self.suggested_workers if self.suggested_workers else 2,
                'can_parallelize': [],
                'must_serialize': [s.name for s in stages],
                'safety_score': 0.8,
                'source': 'fallback_no_ai_service',
                'warning': 'No AI service available, conservative parallelization'
            }

        # Make AI call via mixin for complexity (DRY!)
        stage_info = "\n".join([
            f"- {s.name}: deps={s.get_dependencies()}" for s in stages
        ])

        complexity_level, estimated_duration, analysis = self.query_for_complexity(
            requirements=f"Parallelization assessment for stages:\n{stage_info}",
            context=f"Suggested workers: {self.suggested_workers}. "
                   f"Need to assess parallelization safety and dependencies."
        )

        # Build dependency graph to identify serialization requirements
        dep_graph = {s.name: set(s.get_dependencies()) for s in stages}

        # Find stages with no dependencies (can parallelize)
        can_parallelize = [
            s.name for s in stages
            if not s.get_dependencies() or all(
                dep not in [stage.name for stage in stages]
                for dep in s.get_dependencies()
            )
        ]

        # Find stages with dependencies (must serialize)
        must_serialize = [s.name for s in stages if s.get_dependencies()]

        # Adjust worker count based on AI complexity analysis
        complexity_to_safety = {
            'simple': (self.suggested_workers, 0.95),
            'moderate': (max(2, self.suggested_workers - 1), 0.85),
            'complex': (max(2, self.suggested_workers - 2), 0.70),
            'very_complex': (2, 0.60)  # Conservative for very complex
        }

        recommended_workers, safety_score = complexity_to_safety.get(
            complexity_level,
            (self.suggested_workers, 0.75)
        )

        return {
            'recommended_workers': recommended_workers,
            'can_parallelize': can_parallelize,
            'must_serialize': must_serialize,
            'safety_score': safety_score,
            'source': 'ai_assessed',
            'complexity_level': complexity_level,
            'estimated_duration': estimated_duration,
            'ai_analysis': analysis,
            'initial_suggested_workers': self.suggested_workers,
            'adjustment': recommended_workers - self.suggested_workers
        }


# ============================================================================
# CONVENIENCE FACTORY
# ============================================================================

class DynamicPipelineFactory:
    """
    Factory for creating common pipeline configurations.

    Why it exists: Provides convenient preset configurations for common
    use cases without needing to manually configure builder.

    Design pattern: Factory Pattern
    """

    @staticmethod
    def create_simple_pipeline(
        name: str,
        stages: List[PipelineStage],
        observable: Optional[PipelineObservable] = None
    ) -> DynamicPipeline:
        """
        Create simple sequential pipeline.

        Args:
            name: Pipeline name
            stages: Stages to execute
            observable: Optional observable (creates default if None)

        Returns:
            Configured pipeline
        """
        return (DynamicPipelineBuilder()
            .with_name(name)
            .add_stages(stages)
            .with_observable(observable or PipelineObservable())
            .build())

    @staticmethod
    def create_parallel_pipeline(
        name: str,
        stages: List[PipelineStage],
        max_workers: int = 4,
        observable: Optional[PipelineObservable] = None
    ) -> DynamicPipeline:
        """
        Create pipeline with parallel execution.

        Args:
            name: Pipeline name
            stages: Stages to execute
            max_workers: Maximum parallel workers
            observable: Optional observable

        Returns:
            Configured pipeline with parallelism
        """
        return (DynamicPipelineBuilder()
            .with_name(name)
            .add_stages(stages)
            .with_parallelism(enabled=True, max_workers=max_workers)
            .with_observable(observable or PipelineObservable())
            .build())

    @staticmethod
    def create_adaptive_pipeline(
        name: str,
        stages: List[PipelineStage],
        complexity: ProjectComplexity,
        enable_parallel: bool = True,
        observable: Optional[PipelineObservable] = None
    ) -> DynamicPipeline:
        """
        Create adaptive pipeline with complexity-based selection.

        Args:
            name: Pipeline name
            stages: Available stages
            complexity: Project complexity level
            enable_parallel: Enable parallel execution
            observable: Optional observable

        Returns:
            Configured adaptive pipeline
        """
        builder = (DynamicPipelineBuilder()
            .with_name(name)
            .add_stages(stages)
            .with_strategy(ComplexityBasedSelector())
            .with_context({"complexity": complexity})
            .with_observable(observable or PipelineObservable()))

        if enable_parallel:
            builder.with_parallelism(enabled=True, max_workers=4)

        return builder.build()
