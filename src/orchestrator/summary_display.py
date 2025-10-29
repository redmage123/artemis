#!/usr/bin/env python3
"""
Summary Display - Clear, Concise UX for Artemis

WHY: Users want clarity like the demo, not overwhelming verbose logs.
RESPONSIBILITY: Display pipeline progress with clear reasoning and structure.
PATTERNS: Facade Pattern for clean display interface.

Combines:
- Demo's clarity: Clear sections, emoji, reasoning
- Artemis's capability: Real execution, comprehensive validation
"""

from typing import Dict, Any, Optional
from datetime import datetime


class SummaryDisplay:
    """
    Display pipeline execution with demo-like clarity.

    WHY: Balance information density with clarity
    FEATURES:
    - Structured sections with visual hierarchy
    - Clear reasoning for decisions
    - Progress indicators
    - Minimal noise, maximum signal
    """

    def __init__(self, logger, verbose: bool = False):
        """
        Initialize summary display.

        Args:
            logger: Logger instance
            verbose: Show detailed logs (default: False for summary mode)
        """
        self.logger = logger
        self.verbose = verbose
        self.start_time = None

    def show_header(self):
        """Display Artemis header."""
        self.logger.log("\n" + "=" * 70, "INFO")
        self.logger.log("🎯 ARTEMIS AUTONOMOUS DEVELOPMENT PIPELINE", "INFO")
        self.logger.log("=" * 70 + "\n", "INFO")

    def show_platform_summary(self, platform_info, resource_allocation):
        """
        Display platform detection summary.

        Args:
            platform_info: Detected platform information
            resource_allocation: Calculated resource limits
        """
        if not self.verbose:
            # Summary mode: Just key facts
            self.logger.log("🖥️  Platform Detected:", "INFO")
            self.logger.log(f"   CPU: {platform_info.cpu_count_physical} cores", "INFO")
            self.logger.log(f"   RAM: {platform_info.total_memory_gb:.1f}GB", "INFO")
            self.logger.log(f"   Disk: {platform_info.disk_type.upper()}", "INFO")
        else:
            # Verbose mode: Full details
            self.logger.log("\n" + "=" * 70, "INFO")
            self.logger.log("PLATFORM DETECTION", "INFO")
            self.logger.log("=" * 70, "INFO")
            self.logger.log(f"Operating System: {platform_info.os_name}", "INFO")
            self.logger.log(f"CPU: {platform_info.cpu_count_physical} physical, {platform_info.cpu_count_logical} logical", "INFO")
            self.logger.log(f"Memory: {platform_info.total_memory_gb:.1f}GB total, {platform_info.free_memory_gb:.1f}GB free", "INFO")
            self.logger.log(f"Disk: {platform_info.disk_type.upper()} ({platform_info.disk_free_gb:.1f}GB free)", "INFO")

    def show_adaptive_config(self, adaptive_config):
        """
        Display adaptive configuration with clear reasoning.

        Args:
            adaptive_config: Generated adaptive configuration
        """
        self.logger.log("\n" + "=" * 70, "INFO")
        self.logger.log("🔧 ADAPTIVE CONFIGURATION", "INFO")
        self.logger.log("=" * 70 + "\n", "INFO")

        self.logger.log(f"Profile: {adaptive_config.profile.upper()}", "INFO")
        self.logger.log("", "INFO")

        self.logger.log("📋 Pipeline Configuration:", "INFO")
        self.logger.log(f"   Parallel Developers: {adaptive_config.max_parallel_developers}", "INFO")
        self.logger.log(f"   Validation Level: {adaptive_config.validation_level}", "INFO")
        self.logger.log(f"   Code Review Depth: {adaptive_config.code_review_depth}", "INFO")
        self.logger.log("", "INFO")

        self.logger.log("⚡ Resource Allocation:", "INFO")
        self.logger.log(f"   Memory per Agent: {adaptive_config.memory_per_agent_gb}GB", "INFO")
        self.logger.log(f"   Max Parallel Stages: {adaptive_config.max_parallel_stages}", "INFO")
        self.logger.log(f"   Max Parallel Tests: {adaptive_config.max_parallel_tests}", "INFO")
        self.logger.log("", "INFO")

        self.logger.log("🎯 Optimizations:", "INFO")
        if adaptive_config.skip_sprint_planning:
            self.logger.log("   ✓ Skip Sprint Planning (simple task)", "INFO")
        if adaptive_config.skip_project_analysis:
            self.logger.log("   ✓ Skip Project Analysis (simple task)", "INFO")
        self.logger.log("", "INFO")

        self.logger.log("💡 Reasoning:", "INFO")
        self.logger.log(f"   {adaptive_config.reasoning}", "INFO")

        self.logger.log("\n" + "=" * 70 + "\n", "INFO")

    def show_stage_start(self, stage_number: int, total_stages: int, stage_name: str):
        """
        Display stage start.

        Args:
            stage_number: Current stage number (1-indexed)
            total_stages: Total number of stages
            stage_name: Name of the stage
        """
        if not self.verbose:
            # Summary mode: Clean progress indicator
            self.logger.log(f"\n▶️  Stage {stage_number}/{total_stages}: {stage_name}", "INFO")
        else:
            # Verbose mode: Full details
            self.logger.log(f"\n{'='*70}", "INFO")
            self.logger.log(f"STAGE {stage_number}/{total_stages}: {stage_name}", "INFO")
            self.logger.log(f"{'='*70}", "INFO")

    def show_stage_complete(self, stage_name: str, duration_seconds: float):
        """
        Display stage completion.

        Args:
            stage_name: Name of completed stage
            duration_seconds: Stage execution time
        """
        if not self.verbose:
            # Summary mode: Simple checkmark
            self.logger.log(f"   ✅ {stage_name} complete ({duration_seconds:.1f}s)", "SUCCESS")
        else:
            # Verbose mode: Full details
            self.logger.log(f"\n✅ STAGE COMPLETE: {stage_name}", "SUCCESS")
            self.logger.log(f"   Duration: {duration_seconds:.1f}s", "INFO")

    def show_stage_failed(self, stage_name: str, error: str, suggestion: Optional[str] = None):
        """
        Display stage failure with helpful guidance.

        Args:
            stage_name: Name of failed stage
            error: Error message
            suggestion: Optional suggestion for fixing
        """
        self.logger.log(f"\n❌ {stage_name} FAILED", "ERROR")
        self.logger.log(f"   Error: {error}", "ERROR")

        if suggestion:
            self.logger.log(f"\n💡 How to fix:", "INFO")
            self.logger.log(f"   {suggestion}", "INFO")

    def show_adaptive_decision(self, decision_type: str, value: Any, reasoning: str):
        """
        Show adaptive decision with reasoning.

        Args:
            decision_type: Type of decision (e.g., "Parallel Developers")
            value: Chosen value
            reasoning: Why this value was chosen
        """
        if not self.verbose:
            self.logger.log(f"   🔧 {decision_type}: {value}", "INFO")
            self.logger.log(f"      Why: {reasoning}", "INFO")

    def show_pipeline_start(self, strategy_name: str, num_stages: int):
        """
        Display pipeline start.

        Args:
            strategy_name: Execution strategy name
            num_stages: Number of stages to execute
        """
        self.start_time = datetime.now()

        self.logger.log("\n" + "=" * 70, "INFO")
        self.logger.log(f"▶️  STARTING PIPELINE EXECUTION", "INFO")
        self.logger.log("=" * 70, "INFO")
        self.logger.log(f"Strategy: {strategy_name}", "INFO")
        self.logger.log(f"Stages: {num_stages}", "INFO")
        self.logger.log("", "INFO")

    def show_pipeline_complete(self, status: str, stages_completed: int):
        """
        Display pipeline completion.

        Args:
            status: Pipeline status (SUCCESS/FAILED)
            stages_completed: Number of stages completed
        """
        duration = (datetime.now() - self.start_time).total_seconds() if self.start_time else 0

        self.logger.log("\n" + "=" * 70, "INFO")
        if status == "SUCCESS":
            self.logger.log("✅ PIPELINE COMPLETE", "SUCCESS")
        else:
            self.logger.log("❌ PIPELINE FAILED", "ERROR")
        self.logger.log("=" * 70, "INFO")

        self.logger.log(f"Stages Completed: {stages_completed}", "INFO")
        self.logger.log(f"Total Duration: {duration:.1f}s ({duration/60:.1f} minutes)", "INFO")
        self.logger.log("", "INFO")

    def show_validation_issue(self, file_path: str, issue_type: str, suggestion: str):
        """
        Display validation issue with clear guidance.

        Args:
            file_path: File with validation issue
            issue_type: Type of issue
            suggestion: How to fix
        """
        self.logger.log(f"   ⚠️  {file_path}: {issue_type}", "WARNING")
        self.logger.log(f"      Fix: {suggestion}", "INFO")


def create_summary_display(logger, verbose: bool = False) -> SummaryDisplay:
    """
    Factory function to create summary display.

    Args:
        logger: Logger instance
        verbose: Enable verbose mode

    Returns:
        SummaryDisplay instance
    """
    return SummaryDisplay(logger, verbose)
