#!/usr/bin/env python3
"""
WHY: Manage individual stage states with timing and metadata tracking
RESPONSIBILITY: Track state, duration, retries, and metadata for all pipeline stages
PATTERNS: Repository pattern for stage state storage, value object for stage info
"""

from datetime import datetime
from typing import Dict, Optional

from state_machine.stage_state import StageState
from state_machine.stage_state_info import StageStateInfo


class StageStateManager:
    """
    Manages state for individual pipeline stages

    Features:
    - Stage state tracking
    - Automatic timing calculation
    - Retry count tracking
    - Metadata storage
    """

    def __init__(self, verbose: bool = True) -> None:
        """
        Initialize stage state manager

        Args:
            verbose: Enable verbose logging
        """
        self.verbose = verbose
        self.stage_states: Dict[str, StageStateInfo] = {}
        self.active_stage: Optional[str] = None

    def update_stage_state(
        self,
        stage_name: str,
        state: StageState,
        **metadata
    ) -> None:
        """
        Update state of a specific stage

        Args:
            stage_name: Stage name
            state: New stage state
            **metadata: Additional metadata
        """
        # Guard: Check if stage exists
        if stage_name not in self.stage_states:
            self._create_new_stage(stage_name, state)
        else:
            self._update_existing_stage(stage_name, state)

        # Update metadata
        self.stage_states[stage_name].metadata.update(metadata)

        if self.verbose:
            print(f"[StageStateManager] Stage '{stage_name}' → {state.value}")

    def _create_new_stage(self, stage_name: str, state: StageState) -> None:
        """Create new stage state info"""
        self.stage_states[stage_name] = StageStateInfo(
            stage_name=stage_name,
            state=state,
            start_time=datetime.now()
        )

    def _update_existing_stage(self, stage_name: str, state: StageState) -> None:
        """Update existing stage state"""
        stage_info = self.stage_states[stage_name]
        stage_info.state = state

        # Update timing for terminal states
        is_terminal_state = state == StageState.COMPLETED or state == StageState.FAILED
        if is_terminal_state:
            self._update_stage_timing(stage_info)

    def _update_stage_timing(self, stage_info: StageStateInfo) -> None:
        """Update timing information for stage"""
        stage_info.end_time = datetime.now()

        # Guard: Check start time exists
        if not stage_info.start_time:
            return

        stage_info.duration_seconds = (
            stage_info.end_time - stage_info.start_time
        ).total_seconds()

    def set_active_stage(self, stage_name: Optional[str]) -> None:
        """
        Set the currently active stage

        Args:
            stage_name: Stage name or None to clear
        """
        self.active_stage = stage_name
        if self.verbose and stage_name:
            print(f"[StageStateManager] Active stage: {stage_name}")

    def get_active_stage(self) -> Optional[str]:
        """Get currently active stage"""
        return self.active_stage

    def get_stage_state(self, stage_name: str) -> Optional[StageStateInfo]:
        """
        Get state info for a specific stage

        Args:
            stage_name: Stage name

        Returns:
            Stage state info or None if not found
        """
        return self.stage_states.get(stage_name)

    def get_all_stages(self) -> Dict[str, StageStateInfo]:
        """Get all stage states"""
        return self.stage_states.copy()

    def get_circuit_breakers_open(self) -> list:
        """Get list of stages with open circuit breakers"""
        return [
            name for name, info in self.stage_states.items()
            if info.state == StageState.CIRCUIT_OPEN
        ]
