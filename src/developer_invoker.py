#!/usr/bin/env python3
"""
BACKWARD COMPATIBILITY WRAPPER

This module maintains backward compatibility while the codebase migrates
to the new modular structure in developer_invoker/.

All functionality has been refactored into:
- developer_invoker/invoker.py - Main DeveloperInvoker class
- developer_invoker/prompt_builder.py - Prompt construction
- developer_invoker/event_notifier.py - Event notification
- developer_invoker/execution_strategy.py - Parallel/sequential execution

To migrate your code:
    OLD: from developer_invoker import DeveloperInvoker
    NEW: from developer_invoker import DeveloperInvoker  # Same import works!

No breaking changes - all imports remain identical.
"""

# Re-export main class from the modular package
from developer_invoker import DeveloperInvoker

__all__ = ['DeveloperInvoker']
