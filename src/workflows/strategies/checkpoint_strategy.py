#!/usr/bin/env python3
"""
Checkpoint-Based Pipeline Execution Strategy.

WHY: Enable pipeline resume from failures for long-running operations.
RESPONSIBILITY: Execute pipeline with automatic checkpointing and resume.
PATTERNS: Strategy Pattern, Memento Pattern (checkpointing).

Dependencies: base_strategy, execution_context, pathlib, json, os
"""

from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from pathlib import Path
import json
import os

from artemis_stage_interface import PipelineStage
from pipeline_observer import PipelineObservable

from .base_strategy import PipelineStrategy
from .execution_context import ExecutionContextManager


class CheckpointPipelineStrategy(PipelineStrategy):
    """
    Checkpoint-based execution strategy - resume from failures.

    WHY: Avoid re-running expensive operations after failures.
    RESPONSIBILITY: Save progress and resume from last successful checkpoint.
    PATTERNS: Strategy Pattern + Memento Pattern.

    Features:
    - Automatic checkpointing after each stage
    - Resume from last successful stage
    - LLM response caching (avoid re-running expensive operations)
    - Progress tracking

    Use Cases:
    - Long-running pipelines
    - Unreliable environments
    - Development/testing (iterate on single stage)
    - Cost optimization (don't re-run LLM calls)
    """

    def __init__(
        self,
        checkpoint_dir: str = "../../.artemis_data/checkpoints",
        verbose: bool = True,
        observable: Optional[PipelineObservable] = None
    ):
        """
        Initialize checkpoint strategy.

        Args:
            checkpoint_dir: Directory to store checkpoints (relative to .agents/agile)
            verbose: Enable verbose logging
            observable: Optional PipelineObservable for event broadcasting
        """
        super().__init__(verbose, observable)
        self.checkpoint_dir = self._resolve_checkpoint_dir(checkpoint_dir)
        self.context_manager = ExecutionContextManager()

    def execute(self, stages: List[PipelineStage], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute pipeline with checkpointing.

        WHY: Enable resume capability for failed pipelines.
        RESPONSIBILITY: Save state after each stage, resume from failures.

        Args:
            stages: List of pipeline stages to execute
            context: Execution context (card info, config, etc.)

        Returns:
            Execution result dict with status, results, duration, resume info
        """
        start_time = datetime.now()

        card_id = self.context_manager.get_card_id(context)
        checkpoint_file = self.checkpoint_dir / f"{card_id}_checkpoint.json"

        # Check for existing checkpoint
        last_completed_idx, checkpoint_data = self._load_checkpoint(checkpoint_file)

        # Determine start point and initial state
        start_idx, results, resumed = self._determine_start_state(
            last_completed_idx,
            checkpoint_data,
            len(stages)
        )

        # Execute remaining stages
        for i in range(start_idx, len(stages)):
            stage = stages[i]
            stage_name = stage.__class__.__name__

            self._log(f"▶️  Stage {i + 1}/{len(stages)}: {stage_name}", "STAGE")

            # Execute stage
            stage_result = self._execute_stage(stage, context, stage_name)

            # Guard: Check for execution failure
            if stage_result is None:
                self._save_checkpoint(checkpoint_file, i - 1, results)
                return self._build_exception_result(i, stage_name, "Stage execution returned None", results, resumed, start_time)

            # Store result
            results[stage_name] = stage_result

            # Update context with stage result
            self.context_manager.update_context_from_result(context, stage_result)

            # Check if stage succeeded
            if not self.context_manager.is_stage_successful(stage_result):
                self._save_checkpoint(checkpoint_file, i - 1, results)
                return self._handle_stage_failure(i, stage_name, stage_result, results, resumed, start_time)

            # Save checkpoint after successful stage
            self._save_checkpoint(checkpoint_file, i, results)

            self._log(f"✅ Stage COMPLETE: {stage_name} (checkpoint saved)", "SUCCESS")

        # All stages completed - clear checkpoint
        self._clear_checkpoint(checkpoint_file)

        return self._build_success_result(len(stages), results, resumed, start_time)

    def _resolve_checkpoint_dir(self, checkpoint_dir: str) -> Path:
        """
        Resolve checkpoint directory path.

        WHY: Handle relative paths consistently.
        RESPONSIBILITY: Convert relative to absolute path and create directory.

        Args:
            checkpoint_dir: Checkpoint directory path

        Returns:
            Resolved Path object
        """
        # Convert relative path to absolute
        if not os.path.isabs(checkpoint_dir):
            script_dir = os.path.dirname(os.path.abspath(__file__))
            checkpoint_dir = os.path.join(script_dir, checkpoint_dir)

        checkpoint_path = Path(checkpoint_dir)
        checkpoint_path.mkdir(parents=True, exist_ok=True)

        return checkpoint_path

    def _determine_start_state(
        self,
        last_completed_idx: int,
        checkpoint_data: Dict[str, Any],
        total_stages: int
    ) -> Tuple[int, Dict[str, Any], bool]:
        """
        Determine pipeline start state from checkpoint.

        WHY: Handle both fresh start and resume scenarios.
        RESPONSIBILITY: Calculate start index, results, and resume status.

        Args:
            last_completed_idx: Index of last completed stage (-1 if none)
            checkpoint_data: Loaded checkpoint data
            total_stages: Total number of stages

        Returns:
            Tuple of (start_index, initial_results, resumed)
        """
        if last_completed_idx >= 0:
            self._log(f"💾 Found checkpoint - resuming from stage {last_completed_idx + 2}/{total_stages}")
            return (
                last_completed_idx + 1,
                checkpoint_data.get("results", {}),
                True
            )

        self._log("💾 Starting CHECKPOINT pipeline execution (no existing checkpoint)")
        return (0, {}, False)

    def _execute_stage(
        self,
        stage: PipelineStage,
        context: Dict[str, Any],
        stage_name: str
    ) -> Optional[Dict[str, Any]]:
        """
        Execute a single stage with exception handling.

        WHY: Isolate stage execution logic.
        RESPONSIBILITY: Run stage and catch exceptions.

        Args:
            stage: Pipeline stage to execute
            context: Execution context
            stage_name: Stage name for logging

        Returns:
            Stage result dict or None on exception
        """
        try:
            card = self.context_manager.get_card(context)
            return stage.execute(card, context)
        except Exception as e:
            self._log(f"❌ Stage EXCEPTION: {stage_name} - {e}", "ERROR")
            return None

    def _load_checkpoint(self, checkpoint_file: Path) -> Tuple[int, Dict[str, Any]]:
        """
        Load checkpoint from file.

        WHY: Restore pipeline state from disk.
        RESPONSIBILITY: Read and parse checkpoint file safely.

        Args:
            checkpoint_file: Path to checkpoint file

        Returns:
            Tuple of (last_completed_stage_index, checkpoint_data)
            Returns (-1, {}) if no checkpoint exists
        """
        if not checkpoint_file.exists():
            return -1, {}

        try:
            with open(checkpoint_file) as f:
                data = json.load(f)

            last_stage = data.get("last_completed_stage", -1)

            self._log(f"   Loaded checkpoint: {checkpoint_file.name}")
            self._log(f"   Last completed stage: {last_stage + 1}")

            return last_stage, data

        except Exception as e:
            self._log(f"   ⚠️  Failed to load checkpoint: {e}", "WARNING")
            return -1, {}

    def _save_checkpoint(self, checkpoint_file: Path, stage_index: int, results: Dict[str, Any]):
        """
        Save checkpoint to file.

        WHY: Persist pipeline state for resume capability.
        RESPONSIBILITY: Write checkpoint data to disk.

        Args:
            checkpoint_file: Path to checkpoint file
            stage_index: Index of last completed stage
            results: Accumulated results to save
        """
        try:
            checkpoint_data = {
                "last_completed_stage": stage_index,
                "timestamp": datetime.now().isoformat(),
                "results": results
            }

            with open(checkpoint_file, 'w') as f:
                json.dump(checkpoint_data, f, indent=2)

            self._log(f"   💾 Checkpoint saved (stage {stage_index + 1})")

        except Exception as e:
            self._log(f"   ⚠️  Failed to save checkpoint: {e}", "WARNING")

    def _clear_checkpoint(self, checkpoint_file: Path):
        """
        Clear checkpoint file after successful completion.

        WHY: Remove stale checkpoints after pipeline completes.
        RESPONSIBILITY: Delete checkpoint file safely.

        Args:
            checkpoint_file: Path to checkpoint file
        """
        try:
            if checkpoint_file.exists():
                checkpoint_file.unlink()
                self._log("   🗑️  Checkpoint cleared")
        except Exception as e:
            self._log(f"   ⚠️  Failed to clear checkpoint: {e}", "WARNING")

    def _handle_stage_failure(
        self,
        stage_index: int,
        stage_name: str,
        stage_result: Dict[str, Any],
        results: Dict[str, Any],
        resumed: bool,
        start_time: datetime
    ) -> Dict[str, Any]:
        """
        Handle stage failure.

        WHY: Centralize failure handling logic.
        RESPONSIBILITY: Log and return failure result.

        Args:
            stage_index: Current stage index (1-based)
            stage_name: Name of failed stage
            stage_result: Stage execution result
            results: Accumulated results
            resumed: Whether execution was resumed
            start_time: Execution start time

        Returns:
            Failure result dict
        """
        self._log(f"❌ Stage FAILED: {stage_name}", "ERROR")

        return self.context_manager.build_failure_result(
            stages_completed=stage_index,
            failed_stage=stage_name,
            error=stage_result.get("error", "Unknown error"),
            results=results,
            duration=(datetime.now() - start_time).total_seconds(),
            strategy="checkpoint",
            resumed=resumed,
            checkpoint_saved=True
        )

    def _build_exception_result(
        self,
        stage_index: int,
        stage_name: str,
        error: str,
        results: Dict[str, Any],
        resumed: bool,
        start_time: datetime
    ) -> Dict[str, Any]:
        """
        Build result for stage exception.

        WHY: Consistent exception result structure.
        RESPONSIBILITY: Create exception result dict.

        Args:
            stage_index: Current stage index (1-based)
            stage_name: Name of failed stage
            error: Error message
            results: Accumulated results
            resumed: Whether execution was resumed
            start_time: Execution start time

        Returns:
            Failure result dict
        """
        return self.context_manager.build_failure_result(
            stages_completed=stage_index,
            failed_stage=stage_name,
            error=error,
            results=results,
            duration=(datetime.now() - start_time).total_seconds(),
            strategy="checkpoint",
            resumed=resumed,
            checkpoint_saved=True
        )

    def _build_success_result(
        self,
        total_stages: int,
        results: Dict[str, Any],
        resumed: bool,
        start_time: datetime
    ) -> Dict[str, Any]:
        """
        Build result for successful pipeline completion.

        WHY: Consistent success result structure.
        RESPONSIBILITY: Create success result dict.

        Args:
            total_stages: Total number of stages executed
            results: All stage results
            resumed: Whether execution was resumed
            start_time: Execution start time

        Returns:
            Success result dict
        """
        duration = (datetime.now() - start_time).total_seconds()

        self._log(f"💾 CHECKPOINT pipeline COMPLETE! ({duration:.1f}s, resumed: {resumed})", "SUCCESS")

        return self.context_manager.build_success_result(
            stages_completed=total_stages,
            results=results,
            duration=duration,
            strategy="checkpoint",
            resumed=resumed,
            checkpoint_cleared=True
        )
