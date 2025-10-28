#!/usr/bin/env python3
"""
WHY: Provide top-level messaging package exports.
RESPONSIBILITY: Expose messaging subpackages.

Package: messaging
Purpose: Messaging systems for Artemis pipeline
"""

# Currently only agent messaging is implemented
# Future: Add other messaging systems here (queue, events, etc.)

__all__ = ["agent", "rabbitmq"]
