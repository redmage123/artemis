#!/usr/bin/env python3
"""
BACKWARD COMPATIBILITY WRAPPER

This module maintains backward compatibility while the codebase migrates
to the new modular structure in redis/.

All functionality has been refactored into:
- redis/models.py - StageStatus, PipelineStatus enums
- redis/tracker.py - RedisPipelineTracker class

To migrate your code:
    OLD: from redis_pipeline_tracker import RedisPipelineTracker
    NEW: from redis import RedisPipelineTracker

No breaking changes - all imports remain identical.
"""

# Re-export all public APIs from the modular package
from redis import (
    StageStatus,
    PipelineStatus,
    RedisPipelineTracker
)

__all__ = [
    'StageStatus',
    'PipelineStatus',
    'RedisPipelineTracker'
]


# ============================================================================
# MAIN - TESTING (maintained for backward compatibility)
# ============================================================================

if __name__ == "__main__":
    import time

    print("Testing Redis pipeline tracker...")

    try:
        # Create tracker
        tracker = RedisPipelineTracker()

        if not tracker.enabled:
            print("❌ Redis not available. Start Redis with:")
            print("   docker run -d -p 6379:6379 redis")
            exit(1)

        card_id = "test-card-001"

        # Start pipeline
        print(f"\n1. Starting pipeline {card_id}...")
        tracker.start_pipeline(
            card_id,
            total_stages=3,
            metadata={"title": "Test Pipeline", "priority": "high"}
        )

        # Update stages
        print("\n2. Updating stage 1...")
        tracker.update_stage_status(
            card_id,
            "stage_1",
            StageStatus.RUNNING,
            progress_percent=50,
            message="Processing data..."
        )

        time.sleep(1)

        tracker.update_stage_status(
            card_id,
            "stage_1",
            StageStatus.COMPLETED,
            progress_percent=100,
            message="Stage 1 complete"
        )

        print("\n3. Updating stage 2...")
        tracker.update_stage_status(
            card_id,
            "stage_2",
            StageStatus.RUNNING,
            progress_percent=30,
            message="Running tests..."
        )

        # Get status
        print("\n4. Getting pipeline status...")
        status = tracker.get_pipeline_status(card_id)
        print(f"   Status: {status['status']}")
        print(f"   Completed: {status['completed_stages']}/{status['total_stages']}")
        print(f"   Current: {status['current_stage']}")

        # Complete pipeline
        print("\n5. Completing pipeline...")
        tracker.complete_pipeline(card_id, PipelineStatus.COMPLETED, "All stages complete")

        final_status = tracker.get_pipeline_status(card_id)
        print(f"   Final status: {final_status['status']}")
        print(f"   Duration: {final_status['duration_seconds']:.2f} seconds")

        # Get all stage statuses
        print("\n6. Getting all stage statuses...")
        all_stages = tracker.get_all_stage_statuses(card_id)
        for stage in all_stages:
            print(f"   {stage['stage_name']}: {stage['status']}")

        print("\n✅ All pipeline tracker tests passed!")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
