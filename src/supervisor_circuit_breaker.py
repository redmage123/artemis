#!/usr/bin/env python3
"""
BACKWARD COMPATIBILITY WRAPPER

This module maintains backward compatibility while the codebase migrates
to the new modular structure in supervisor/circuit_breaker/.

All functionality has been refactored into:
- supervisor/circuit_breaker/models.py - StageHealth, RecoveryStrategy, CircuitState
- supervisor/circuit_breaker/manager.py - CircuitBreakerManager

To migrate your code:
    OLD: from supervisor_circuit_breaker import CircuitBreakerManager
    NEW: from supervisor.circuit_breaker import CircuitBreakerManager

No breaking changes - all imports remain identical.
"""

# Re-export all public APIs from the modular package
from supervisor.circuit_breaker import (
    StageHealth,
    RecoveryStrategy,
    CircuitState,
    CircuitBreakerManager
)

__all__ = [
    'StageHealth',
    'RecoveryStrategy',
    'CircuitState',
    'CircuitBreakerManager'
]


# ============================================================================
# CLI INTERFACE (maintained for backward compatibility)
# ============================================================================

if __name__ == "__main__":
    import argparse
    import json
    import sys

    parser = argparse.ArgumentParser(description="Circuit Breaker Manager Demo")
    parser.add_argument("--demo", action="store_true", help="Run demo")
    parser.add_argument("--stats", action="store_true", help="Show statistics")

    args = parser.parse_args()

    # Guard clause - handle demo command
    if args.demo:
        print("=" * 70)
        print("CIRCUIT BREAKER MANAGER DEMO")
        print("=" * 70)

        # Create manager
        manager = CircuitBreakerManager(verbose=True)

        # Register stages
        manager.register_stage("stage1", RecoveryStrategy(circuit_breaker_threshold=3))
        manager.register_stage("stage2")

        # Simulate failures
        print("\n--- Simulating stage1 failures ---")
        for i in range(5):
            manager.record_failure("stage1")
            is_open = manager.check_circuit("stage1")
            print(f"Attempt {i+1}: Circuit open = {is_open}")

        # Simulate success
        print("\n--- Simulating stage1 success ---")
        manager.record_success("stage1", duration=1.5)
        is_open = manager.check_circuit("stage1")
        print(f"After success: Circuit open = {is_open}")

        # Show stats
        print("\n--- Statistics ---")
        stats = manager.get_statistics()
        print(json.dumps(stats, indent=2))
        sys.exit(0)

    # Guard clause - handle stats command
    if args.stats:
        manager = CircuitBreakerManager(verbose=False)
        stats = manager.get_statistics()
        print(json.dumps(stats, indent=2))
        sys.exit(0)

    # No command specified
    parser.print_help()
