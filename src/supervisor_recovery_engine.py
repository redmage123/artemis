#!/usr/bin/env python3
"""
Module: supervisor_recovery_engine.py

BACKWARD COMPATIBILITY WRAPPER

WHY: Maintain backward compatibility while code migrates to modular structure
RESPONSIBILITY: Re-export all components from supervisor/recovery/ package
MIGRATION PATH: Import from supervisor.recovery directly for new code

This file preserves the original import structure:
    from supervisor_recovery_engine import RecoveryEngine, RecoveryStrategy

New code should import from the modular package:
    from supervisor.recovery import RecoveryEngine, RecoveryStrategy
    from supervisor.recovery.strategies import JSONParsingStrategy, RetryStrategy
    from supervisor.recovery.llm_auto_fix import LLMAutoFix
    from supervisor.recovery.failure_analysis import FailureAnalyzer
    from supervisor.recovery.state_restoration import StateRestoration

DEPRECATION TIMELINE:
- Phase 1: This wrapper maintains compatibility (current)
- Phase 2: Add deprecation warnings
- Phase 3: Remove wrapper after all imports updated

Original module location: /home/bbrelin/src/repos/artemis/src/supervisor_recovery_engine.py
New module location: /home/bbrelin/src/repos/artemis/src/supervisor/recovery/
Lines reduced: 941 -> ~150 (main engine) + 5 support modules
"""

# Re-export main classes for backward compatibility
from supervisor.recovery.engine import RecoveryEngine
from supervisor.recovery.strategy import RecoveryStrategy

# Re-export concrete strategies
from supervisor.recovery.strategies import (
    JSONParsingStrategy,
    RetryStrategy,
    DefaultValueStrategy,
    SkipStageStrategy
)

# Re-export supporting classes
from supervisor.recovery.failure_analysis import FailureAnalyzer
from supervisor.recovery.state_restoration import StateRestoration
from supervisor.recovery.llm_auto_fix import LLMAutoFix


# Maintain module-level exports
__all__ = [
    # Main classes
    "RecoveryEngine",
    "RecoveryStrategy",

    # Concrete strategies
    "JSONParsingStrategy",
    "RetryStrategy",
    "DefaultValueStrategy",
    "SkipStageStrategy",

    # Supporting classes
    "FailureAnalyzer",
    "StateRestoration",
    "LLMAutoFix",
]


# ============================================================================
# CLI INTERFACE (preserved for backward compatibility)
# ============================================================================

def _run_demo():
    """Run recovery engine demo"""
    import json

    print("=" * 70)
    print("RECOVERY ENGINE DEMO")
    print("=" * 70)

    # Create engine
    engine = RecoveryEngine(verbose=True)

    # Simulate crash recovery
    print("\n--- Simulating Crash Recovery ---")
    crash_info = {
        "agent_name": "test-agent",
        "error_type": "KeyError",
        "error": "'missing_key'",
        "traceback": ""
    }
    context = {}
    result = engine.recover_crashed_agent(crash_info, context)
    print(f"Result: {result.get('message')}")

    # Simulate hung agent recovery
    print("\n--- Simulating Hung Agent Recovery ---")
    timeout_info = {
        "timeout_seconds": 300,
        "elapsed_time": 350
    }
    result = engine.recover_hung_agent("hung-agent", timeout_info)
    print(f"Result: {result.get('message')}")

    # Show stats
    print("\n--- Statistics ---")
    stats = engine.get_statistics()
    print(json.dumps(stats, indent=2))


def _show_stats():
    """Show recovery engine statistics"""
    import json

    engine = RecoveryEngine(verbose=False)
    stats = engine.get_statistics()
    print(json.dumps(stats, indent=2))


if __name__ == "__main__":
    import argparse
    import sys

    parser = argparse.ArgumentParser(description="Recovery Engine Demo")
    parser.add_argument("--demo", action="store_true", help="Run demo")
    parser.add_argument("--stats", action="store_true", help="Show statistics")

    args = parser.parse_args()

    # Guard clause: No command specified, show help and exit
    if not args.demo and not args.stats:
        parser.print_help()
        sys.exit(0)

    # Execute commands based on args (no nesting, independent checks)
    if args.demo:
        _run_demo()

    if args.stats:
        _show_stats()
