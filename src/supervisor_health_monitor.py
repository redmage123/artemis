#!/usr/bin/env python3
"""
BACKWARD COMPATIBILITY WRAPPER

WHY: Maintain compatibility with existing code using supervisor_health_monitor
RESPONSIBILITY: Re-export all components from new modular structure
PATTERNS: Facade (backward compatibility), Deprecation wrapper

DEPRECATED: This module is provided for backward compatibility only.
New code should import from: supervisor.health

Migration examples:
    OLD: from supervisor_health_monitor import HealthMonitor, AgentHealthEvent
    NEW: from supervisor.health import HealthMonitor, AgentHealthEvent

    OLD: from supervisor_health_monitor import ProcessHealth, HealthStatus
    NEW: from supervisor.health import ProcessHealth, HealthStatus

Package structure:
    supervisor/health/
    ├── __init__.py              # Package exports
    ├── event_types.py           # AgentHealthEvent, HealthStatus, ProcessHealth (71 lines)
    ├── agent_registry.py        # AgentRegistry (147 lines)
    ├── process_monitor.py       # ProcessMonitor (187 lines)
    ├── crash_detector.py        # CrashDetector (109 lines)
    ├── progress_tracker.py      # ProgressTracker (169 lines)
    ├── health_calculator.py     # HealthCalculator (95 lines)
    ├── event_observer.py        # EventObserver (119 lines)
    ├── watchdog.py              # Watchdog (182 lines)
    └── health_monitor.py        # HealthMonitor (394 lines)

Total: ~1,473 lines (modular) vs 927 lines (original)
Modularization adds documentation and separation but reduces complexity per file.
"""

import json
import time
from datetime import datetime
from typing import Any, Dict, List, Optional

# Re-export all components from new modular structure
from supervisor.health import (
    AgentHealthEvent,
    AgentRegistry,
    CrashDetector,
    CrashInfo,
    EventObserver,
    HealthCalculator,
    HealthEventData,
    HealthMonitor,
    HealthStatus,
    ProcessHealth,
    ProcessMonitor,
    ProgressTracker,
    Watchdog,
)

# Re-export main class and types for backward compatibility
__all__ = [
    # Main interface
    "HealthMonitor",
    # Event types
    "AgentHealthEvent",
    "HealthStatus",
    "ProcessHealth",
    "CrashInfo",
    "HealthEventData",
    # Components (for advanced usage)
    "AgentRegistry",
    "ProcessMonitor",
    "CrashDetector",
    "ProgressTracker",
    "HealthCalculator",
    "EventObserver",
    "Watchdog",
]


# ============================================================================
# CLI INTERFACE (preserved for backward compatibility)
# ============================================================================

def _run_demo() -> None:
    """Run health monitor demo"""
    print("=" * 70)
    print("HEALTH MONITOR DEMO")
    print("=" * 70)

    # Create monitor
    monitor = HealthMonitor(verbose=True)

    # Register agents
    print("\n--- Registering agents ---")
    monitor.register_agent("agent1", "stage", heartbeat_interval=10.0)
    monitor.register_agent("agent2", "worker", heartbeat_interval=15.0)

    # Simulate heartbeats
    print("\n--- Simulating heartbeats ---")
    monitor.agent_heartbeat("agent1", {"progress": 50})
    monitor.agent_heartbeat("agent2", {"progress": 75})

    # Get health status
    print("\n--- Health Status ---")
    status = monitor.get_health_status()
    print(f"Overall Health: {status.value}")

    # Show stats
    print("\n--- Statistics ---")
    stats = monitor.get_statistics()
    print(json.dumps(stats, indent=2))

    # Unregister agents
    print("\n--- Unregistering agents ---")
    monitor.unregister_agent("agent1")
    monitor.unregister_agent("agent2")


def _show_stats() -> None:
    """Show health monitor statistics"""
    monitor = HealthMonitor(verbose=False)
    stats = monitor.get_statistics()
    print(json.dumps(stats, indent=2))


def _main() -> None:
    """Main entry point for CLI"""
    import argparse

    parser = argparse.ArgumentParser(description="Health Monitor Demo")
    parser.add_argument("--demo", action="store_true", help="Run demo")
    parser.add_argument("--stats", action="store_true", help="Show statistics")

    args = parser.parse_args()

    if args.demo:
        _run_demo()
        return

    if args.stats:
        _show_stats()
        return

    parser.print_help()


if __name__ == "__main__":
    _main()
