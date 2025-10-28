#!/usr/bin/env python3
"""
WHY: Provide convenient factory function for creating state machines
RESPONSIBILITY: Simplify state machine instantiation with sensible defaults
PATTERNS: Factory pattern, convenience interface
"""

from state_machine.artemis_state_machine import ArtemisStateMachine


def create_state_machine(card_id: str, verbose: bool = True) -> ArtemisStateMachine:
    """
    Create state machine for a card

    Args:
        card_id: Kanban card ID
        verbose: Enable verbose logging

    Returns:
        ArtemisStateMachine instance
    """
    return ArtemisStateMachine(card_id=card_id, verbose=verbose)
