#!/usr/bin/env python3
"""
Module: test_advanced_features/mock_classes.py

WHY: Provides reusable mock classes for testing pipeline components without
     real implementation complexity.

RESPONSIBILITY:
- MockStage: Controllable pipeline stage with configurable success/failure
- MockObserver: Event capture for testing observable components

PATTERNS:
- Test Double Pattern: Mock implementations for isolated testing
- Guard clauses for early returns
"""

from typing import Dict, Any, List
from dynamic_pipeline import PipelineStage, StageResult
from pipeline_observer import PipelineObserver, PipelineEvent, EventType


class MockStage(PipelineStage):
    """
    Mock pipeline stage for testing.

    Why needed: Provides controllable stage behavior for testing dynamic pipeline
    execution without real stage implementation complexity.
    """

    def __init__(self, name: str, should_fail: bool = False, dependencies: List[str] = None):
        super().__init__(name)
        self.should_fail = should_fail
        self._dependencies = dependencies or []
        self.execution_count = 0
        self.last_context = None

    def execute(self, context: Dict[str, Any]) -> StageResult:
        """Execute mock stage with controllable success/failure"""
        self.execution_count += 1
        self.last_context = context

        if self.should_fail:
            return StageResult(
                stage_name=self.name,
                success=False,
                error=Exception(f"{self.name} failed intentionally")
            )

        return StageResult(
            stage_name=self.name,
            success=True,
            data={"result": f"{self.name} completed"},
            duration=0.1
        )

    def get_dependencies(self) -> List[str]:
        """Return configured dependencies"""
        return self._dependencies

    def should_execute(self, context: Dict[str, Any]) -> bool:
        """Check if should execute based on context"""
        skip_flag = context.get(f"skip_{self.name}", False)
        return not skip_flag


class MockObserver(PipelineObserver):
    """
    Mock observer for testing event emission.

    Why needed: Captures emitted events for verification without real observer
    implementation overhead.
    """

    def __init__(self):
        self.events = []

    def on_event(self, event: PipelineEvent) -> None:
        """Record event"""
        self.events.append(event)

    def get_events_by_type(self, event_type: EventType) -> List[PipelineEvent]:
        """Get events filtered by type"""
        return [e for e in self.events if e.event_type == event_type]
