#!/usr/bin/env python3
"""
Adaptive Config Generator

WHY: Generate optimal Artemis configuration based on task requirements AND platform capabilities
RESPONSIBILITY: Analyze task + platform → produce optimal config for pipeline execution
PATTERNS: Builder pattern, Strategy pattern, Configuration as Code

DESIGN DECISION:
Instead of one-size-fits-all config, generate task-specific and platform-aware config:
- Simple HTML task on laptop → minimal resources, fast execution
- Complex backend on server → full resources, parallel execution
- Database-heavy task with low memory → sequential processing with checkpoints
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum
from artemis_logger import get_logger
from platform_detector import PlatformDetector, PlatformInfo
from adaptive_pipeline_builder import TaskComplexityDetector, TaskComplexity

logger = get_logger(__name__)


class ExecutionProfile(Enum):
    """Execution profiles based on task + platform."""
    MINIMAL = "minimal"          # Lightweight, single developer, minimal stages
    BALANCED = "balanced"        # Standard config, moderate parallelism
    AGGRESSIVE = "aggressive"    # Maximum parallelism, full resources
    CONSERVATIVE = "conservative"  # Safe mode, checkpoints, sequential


@dataclass
class AdaptiveConfig:
    """Task-aware and platform-aware configuration."""

    # Execution profile
    profile: str

    # Resource allocation
    max_parallel_developers: int
    max_parallel_stages: int
    max_parallel_tests: int
    memory_per_agent_gb: float

    # Pipeline configuration
    skip_sprint_planning: bool
    skip_project_analysis: bool
    skip_arbitration: bool
    enable_checkpoints: bool
    checkpoint_frequency: str  # 'never', 'per_stage', 'frequent'

    # Performance tuning
    batch_size: int
    async_io_enabled: bool
    caching_enabled: bool
    thread_pool_size: int

    # Quality vs Speed tradeoffs
    code_review_depth: str  # 'quick', 'standard', 'thorough'
    validation_level: str    # 'basic', 'standard', 'comprehensive'
    test_coverage_target: int  # percentage

    # LLM configuration
    llm_temperature: float
    llm_max_tokens: int
    llm_timeout_seconds: int

    # Reasoning
    reasoning: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


class AdaptiveConfigGenerator:
    """
    Generate optimal Artemis config based on task requirements and platform info.

    WHY: One-size-fits-all config wastes resources on simple tasks and
         underutilizes resources on complex tasks.
    """

    def __init__(self):
        """Initialize config generator."""
        self.task_detector = TaskComplexityDetector()
        self.platform_detector = PlatformDetector()

    def generate_config(
        self,
        requirements: Dict[str, Any],
        card: Dict[str, Any],
        platform_info: Optional[PlatformInfo] = None
    ) -> AdaptiveConfig:
        """
        Generate optimal config based on task and platform.

        Args:
            requirements: Parsed requirements
            card: Task card
            platform_info: Platform information (auto-detected if not provided)

        Returns:
            AdaptiveConfig with optimal settings
        """
        logger.log("🔧 Generating adaptive configuration...", "INFO")

        # Detect task complexity
        task_complexity = self.task_detector.detect(requirements, card)
        logger.log(f"   Task complexity: {task_complexity.value}", "INFO")

        # Get platform info
        if platform_info is None:
            platform_info = self.platform_detector.detect_platform()

        logger.log(f"   Platform: {platform_info.cpu_count_physical} cores, {platform_info.total_memory_gb:.1f}GB RAM", "INFO")

        # Determine execution profile
        profile = self._select_execution_profile(task_complexity, platform_info)
        logger.log(f"   Execution profile: {profile.value}", "INFO")

        # Generate config based on profile
        config = self._build_config(profile, task_complexity, platform_info, requirements)

        logger.log(f"✅ Config generated: {config.max_parallel_developers} devs, {config.max_parallel_stages} stages", "INFO")

        return config

    def _select_execution_profile(
        self,
        complexity: TaskComplexity,
        platform: PlatformInfo
    ) -> ExecutionProfile:
        """
        Select execution profile based on task complexity and platform capabilities.

        Decision matrix:
        - SIMPLE task + High resources → MINIMAL (don't waste resources)
        - SIMPLE task + Low resources → MINIMAL
        - MEDIUM task + High resources → BALANCED
        - MEDIUM task + Low resources → CONSERVATIVE (safe mode)
        - COMPLEX task + High resources → AGGRESSIVE (full power)
        - COMPLEX task + Low resources → CONSERVATIVE (prevent OOM)
        """
        # Define resource thresholds
        high_cpu = platform.cpu_count_physical >= 4
        high_memory = platform.total_memory_gb >= 8
        high_resources = high_cpu and high_memory

        # Decision matrix: complexity → (high_resources → profile, low_resources → profile)
        profile_matrix = {
            TaskComplexity.SIMPLE: (ExecutionProfile.MINIMAL, ExecutionProfile.MINIMAL),
            TaskComplexity.MEDIUM: (ExecutionProfile.BALANCED, ExecutionProfile.CONSERVATIVE),
            TaskComplexity.COMPLEX: (ExecutionProfile.AGGRESSIVE, ExecutionProfile.CONSERVATIVE)
        }

        high_res_profile, low_res_profile = profile_matrix.get(complexity, (ExecutionProfile.BALANCED, ExecutionProfile.CONSERVATIVE))
        return high_res_profile if high_resources else low_res_profile

    def _build_config(
        self,
        profile: ExecutionProfile,
        complexity: TaskComplexity,
        platform: PlatformInfo,
        requirements: Dict[str, Any]
    ) -> AdaptiveConfig:
        """Build config for the selected profile."""

        # Strategy pattern: profile → builder method
        profile_builders = {
            ExecutionProfile.MINIMAL: self._build_minimal_config,
            ExecutionProfile.BALANCED: self._build_balanced_config,
            ExecutionProfile.AGGRESSIVE: self._build_aggressive_config,
            ExecutionProfile.CONSERVATIVE: self._build_conservative_config
        }

        builder = profile_builders.get(profile, self._build_balanced_config)
        return builder(complexity, platform)

    def _build_minimal_config(self, complexity: TaskComplexity, platform: PlatformInfo) -> AdaptiveConfig:
        """Minimal config for simple tasks - loads from Hydra."""
        from hydra_config_loader import load_profile
        params = load_profile("minimal")

        return AdaptiveConfig(
            profile="minimal",
            max_parallel_developers=params["parallelism"]["max_parallel_developers"],
            max_parallel_stages=params["parallelism"]["max_parallel_stages"],
            max_parallel_tests=params["parallelism"]["max_parallel_tests"],
            memory_per_agent_gb=params["memory"]["per_agent_gb"],
            skip_sprint_planning=params["skip_flags"]["skip_sprint_planning"],
            skip_project_analysis=params["skip_flags"]["skip_project_analysis"],
            skip_arbitration=params["skip_flags"]["skip_arbitration"],
            enable_checkpoints=False,
            checkpoint_frequency='never',
            batch_size=params["batch"]["default_size"],
            async_io_enabled=True,
            caching_enabled=True,
            thread_pool_size=params["parallelism"]["thread_pool_size"],
            code_review_depth='quick',
            validation_level='basic',
            test_coverage_target=70,
            llm_temperature=0.3,
            llm_max_tokens=2000,
            llm_timeout_seconds=params["timeouts"]["default"],
            reasoning="Simple task: minimal resources, fast execution, skip unnecessary stages"
        )

    def _build_balanced_config(self, complexity: TaskComplexity, platform: PlatformInfo) -> AdaptiveConfig:
        """Balanced config for medium tasks - loads from Hydra."""
        from hydra_config_loader import load_profile
        params = load_profile("balanced")

        parallel_devs = min(params["parallelism"]["max_parallel_developers"], platform.cpu_count_physical // 2)
        parallel_tests = min(params["parallelism"]["max_parallel_tests"], platform.cpu_count_physical)

        return AdaptiveConfig(
            profile="balanced",
            max_parallel_developers=parallel_devs,
            max_parallel_stages=params["parallelism"]["max_parallel_stages"],
            max_parallel_tests=parallel_tests,
            memory_per_agent_gb=params["memory"]["per_agent_gb"],
            skip_sprint_planning=params["skip_flags"]["skip_sprint_planning"],
            skip_project_analysis=params["skip_flags"]["skip_project_analysis"],
            skip_arbitration=params["skip_flags"]["skip_arbitration"],
            enable_checkpoints=True,
            checkpoint_frequency='per_stage',
            batch_size=params["batch"]["default_size"],
            async_io_enabled=True,
            caching_enabled=True,
            thread_pool_size=params["parallelism"]["thread_pool_size"],
            code_review_depth='standard',
            validation_level='standard',
            test_coverage_target=80,
            llm_temperature=0.3,
            llm_max_tokens=2000,
            llm_timeout_seconds=params["timeouts"]["default"],
            reasoning=f"Medium task with good resources: {parallel_devs} devs, standard quality gates"
        )

    def _build_aggressive_config(self, complexity: TaskComplexity, platform: PlatformInfo) -> AdaptiveConfig:
        """Aggressive config for complex tasks - loads from Hydra."""
        from hydra_config_loader import load_profile
        params = load_profile("aggressive")

        parallel_devs = min(params["parallelism"]["max_parallel_developers"], platform.cpu_count_physical // 2)
        parallel_tests = min(params["parallelism"]["max_parallel_tests"], platform.cpu_count_physical)
        parallel_stages = min(params["parallelism"]["max_parallel_stages"], platform.cpu_count_physical // 2)

        return AdaptiveConfig(
            profile="aggressive",
            max_parallel_developers=parallel_devs,
            max_parallel_stages=parallel_stages,
            max_parallel_tests=parallel_tests,
            memory_per_agent_gb=params["memory"]["per_agent_gb"],
            skip_sprint_planning=params["skip_flags"]["skip_sprint_planning"],
            skip_project_analysis=params["skip_flags"]["skip_project_analysis"],
            skip_arbitration=params["skip_flags"]["skip_arbitration"],
            enable_checkpoints=True,
            checkpoint_frequency='per_stage',
            batch_size=params["batch"]["default_size"],
            async_io_enabled=True,
            caching_enabled=True,
            thread_pool_size=params["parallelism"]["thread_pool_size"],
            code_review_depth='thorough',
            validation_level='comprehensive',
            test_coverage_target=90,
            llm_temperature=0.5,
            llm_max_tokens=4000,
            llm_timeout_seconds=params["timeouts"]["default"],
            reasoning=f"Complex task with high resources: {parallel_devs} devs, maximum parallelism, thorough quality"
        )

    def _build_conservative_config(self, complexity: TaskComplexity, platform: PlatformInfo) -> AdaptiveConfig:
        """Conservative config for resource-constrained environments - loads from Hydra."""
        from hydra_config_loader import load_profile
        params = load_profile("conservative")

        return AdaptiveConfig(
            profile="conservative",
            max_parallel_developers=params["parallelism"]["max_parallel_developers"],
            max_parallel_stages=params["parallelism"]["max_parallel_stages"],
            max_parallel_tests=params["parallelism"]["max_parallel_tests"],
            memory_per_agent_gb=params["memory"]["per_agent_gb"],
            skip_sprint_planning=params["skip_flags"]["skip_sprint_planning"],
            skip_project_analysis=params["skip_flags"]["skip_project_analysis"],
            skip_arbitration=params["skip_flags"]["skip_arbitration"],
            enable_checkpoints=True,
            checkpoint_frequency='frequent',
            batch_size=params["batch"]["default_size"],
            async_io_enabled=True,
            caching_enabled=True,
            thread_pool_size=params["parallelism"]["thread_pool_size"],
            code_review_depth='standard',
            validation_level='standard',
            test_coverage_target=80,
            llm_temperature=0.3,
            llm_max_tokens=2000,
            llm_timeout_seconds=params["timeouts"]["default"],
            reasoning="Resource-constrained: sequential execution, frequent checkpoints, prevent OOM"
        )


def generate_adaptive_config(
    requirements: Dict[str, Any],
    card: Dict[str, Any],
    platform_info: Optional[PlatformInfo] = None
) -> AdaptiveConfig:
    """
    Convenience function to generate adaptive config.

    Args:
        requirements: Parsed requirements
        card: Task card
        platform_info: Optional platform info

    Returns:
        AdaptiveConfig
    """
    generator = AdaptiveConfigGenerator()
    return generator.generate_config(requirements, card, platform_info)


if __name__ == '__main__':
    """Test adaptive config generation."""
    logger.log("🧪 Testing Adaptive Config Generator", "INFO")

    # Test case 1: Simple HTML task
    logger.log("\n" + "=" * 70, "INFO")
    logger.log("Test 1: Simple HTML task", "INFO")
    logger.log("=" * 70, "INFO")

    simple_reqs = {
        'functional': [
            {'id': 'FR-1', 'description': 'Create single HTML page with CSS styling'}
        ]
    }
    simple_card = {'title': 'HTML Demo Page', 'task_type': 'feature'}

    config1 = generate_adaptive_config(simple_reqs, simple_card)
    logger.log(f"\n✅ Profile: {config1.profile}", "INFO")
    logger.log(f"   Developers: {config1.max_parallel_developers}", "INFO")
    logger.log(f"   Skip planning: {config1.skip_sprint_planning}", "INFO")
    logger.log(f"   Code review: {config1.code_review_depth}", "INFO")
    logger.log(f"   Reasoning: {config1.reasoning}", "INFO")

    # Test case 2: Complex backend task
    logger.log("\n" + "=" * 70, "INFO")
    logger.log("Test 2: Complex backend task", "INFO")
    logger.log("=" * 70, "INFO")

    complex_reqs = {
        'functional': [
            {'id': 'FR-1', 'description': 'Build microservice with PostgreSQL database'},
            {'id': 'FR-2', 'description': 'Implement authentication and authorization'},
            {'id': 'FR-3', 'description': 'Add Redis caching layer'},
            {'id': 'FR-4', 'description': 'Create REST API with 20+ endpoints'},
        ]
    }
    complex_card = {'title': 'Backend Service', 'task_type': 'feature'}

    config2 = generate_adaptive_config(complex_reqs, complex_card)
    logger.log(f"\n✅ Profile: {config2.profile}", "INFO")
    logger.log(f"   Developers: {config2.max_parallel_developers}", "INFO")
    logger.log(f"   Parallel stages: {config2.max_parallel_stages}", "INFO")
    logger.log(f"   Code review: {config2.code_review_depth}", "INFO")
    logger.log(f"   Validation: {config2.validation_level}", "INFO")
    logger.log(f"   Reasoning: {config2.reasoning}", "INFO")

    logger.log("\n" + "=" * 70, "INFO")
    logger.log("✅ All tests passed!", "INFO")
    logger.log("=" * 70 + "\n", "INFO")
