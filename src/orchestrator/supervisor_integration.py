"""
Module: orchestrator/supervisor_integration.py

WHY: Configure supervisor with stage-specific recovery strategies.
RESPONSIBILITY: Register stages with supervisor, define retry/timeout policies.
PATTERNS: Strategy Pattern (per-stage recovery), Guard Clauses.

This module handles:
- Stage registration with supervisor
- Recovery strategy configuration per stage
- Timeout and retry policy customization

EXTRACTED FROM: artemis_orchestrator.py (lines 601-744, 140 lines)
"""

from supervisor_agent import SupervisorAgent, RecoveryStrategy, RecoveryAction
from artemis_constants import (
    MAX_RETRY_ATTEMPTS,
    DEFAULT_RETRY_INTERVAL_SECONDS,
    RETRY_BACKOFF_FACTOR,
    STAGE_TIMEOUT_SECONDS,
    DEVELOPER_AGENT_TIMEOUT_SECONDS,
    CODE_REVIEW_TIMEOUT_SECONDS
)


def register_stages_with_supervisor(supervisor: SupervisorAgent) -> None:
    """
    Register all stages with supervisor agent for monitoring

    WHAT:
    Configures supervisor with stage-specific recovery strategies including
    max retries, timeouts, and backoff factors.

    WHY:
    Different stages have different failure characteristics:
    - Development is critical and expensive → more retries, longer timeout
    - Project analysis is fast and cheap → fewer retries, short timeout
    - Code review can take time → moderate timeout, moderate retries
    - Arbitration should be quick → short timeout, minimal retries

    Custom strategies per stage optimize recovery while preventing infinite loops
    and resource exhaustion.

    RECOVERY STRATEGIES:
    - requirements_parsing: 2 retries, 240s timeout (LLM-heavy)
    - project_analysis: 2 retries, 120s timeout (fast)
    - architecture: 2 retries, 180s timeout (important)
    - dependencies: 2 retries, 60s timeout (fast validation)
    - development: 3 retries, 600s timeout (most critical)
    - arbitration: 2 retries, 120s timeout (fast decision)
    - code_review: 2 retries, 180s timeout (moderate)
    - validation: 2 retries, 120s timeout (fast)
    - integration: 2 retries, 180s timeout (important)
    - testing: 2 retries, 300s timeout (can take time)

    INTEGRATION:
    - Called by: ArtemisOrchestrator.__init__() during initialization
    - Uses: SupervisorAgent.register_stage() to configure monitoring

    Args:
        supervisor: SupervisorAgent instance to configure
    """
    # Requirements Parsing: LLM-heavy, needs more time
    supervisor.register_stage(
        "requirements_parsing",
        RecoveryStrategy(
            action=RecoveryAction.RETRY,
            max_retries=MAX_RETRY_ATTEMPTS - 1,  # 2 retries
            retry_delay_seconds=DEFAULT_RETRY_INTERVAL_SECONDS,  # 5s
            backoff_factor=RETRY_BACKOFF_FACTOR,
            timeout_seconds=STAGE_TIMEOUT_SECONDS / 15  # 240s (4 min)
        )
    )

    # Project Analysis: Fast, can retry quickly
    supervisor.register_stage(
        "project_analysis",
        RecoveryStrategy(
            action=RecoveryAction.RETRY,
            max_retries=MAX_RETRY_ATTEMPTS - 1,  # 2 retries
            retry_delay_seconds=DEFAULT_RETRY_INTERVAL_SECONDS - 3.0,  # 2s
            backoff_factor=RETRY_BACKOFF_FACTOR,
            timeout_seconds=STAGE_TIMEOUT_SECONDS / 30  # 120s
        )
    )

    # Architecture: Important, give more time
    supervisor.register_stage(
        "architecture",
        RecoveryStrategy(
            action=RecoveryAction.RETRY,
            max_retries=MAX_RETRY_ATTEMPTS - 1,  # 2 retries
            retry_delay_seconds=DEFAULT_RETRY_INTERVAL_SECONDS,  # 5s
            backoff_factor=RETRY_BACKOFF_FACTOR,
            timeout_seconds=STAGE_TIMEOUT_SECONDS / 20  # 180s
        )
    )

    # Dependencies: Fast validation
    supervisor.register_stage(
        "dependencies",
        RecoveryStrategy(
            action=RecoveryAction.RETRY,
            max_retries=MAX_RETRY_ATTEMPTS - 1,  # 2 retries
            retry_delay_seconds=DEFAULT_RETRY_INTERVAL_SECONDS - 3.0,  # 2s
            backoff_factor=RETRY_BACKOFF_FACTOR,
            timeout_seconds=STAGE_TIMEOUT_SECONDS / 60  # 60s
        )
    )

    # Development: Most critical, longer timeout
    supervisor.register_stage(
        "development",
        RecoveryStrategy(
            action=RecoveryAction.RETRY,
            max_retries=MAX_RETRY_ATTEMPTS,  # 3 retries
            retry_delay_seconds=DEFAULT_RETRY_INTERVAL_SECONDS * 2,  # 10s
            backoff_factor=RETRY_BACKOFF_FACTOR,  # 2.0
            timeout_seconds=DEVELOPER_AGENT_TIMEOUT_SECONDS / 6  # 600s (10 min)
        )
    )

    # Arbitration: Fast decision making, minimal retries
    supervisor.register_stage(
        "arbitration",
        RecoveryStrategy(
            action=RecoveryAction.RETRY,
            max_retries=MAX_RETRY_ATTEMPTS - 1,  # 2 retries
            retry_delay_seconds=DEFAULT_RETRY_INTERVAL_SECONDS - 2.0,  # 3s
            backoff_factor=RETRY_BACKOFF_FACTOR,
            timeout_seconds=STAGE_TIMEOUT_SECONDS / 30  # 120s (2 min)
        )
    )

    # Code Review: Can retry, moderate timeout
    supervisor.register_stage(
        "code_review",
        RecoveryStrategy(
            action=RecoveryAction.RETRY,
            max_retries=MAX_RETRY_ATTEMPTS - 1,  # 2 retries
            retry_delay_seconds=DEFAULT_RETRY_INTERVAL_SECONDS,  # 5s
            backoff_factor=RETRY_BACKOFF_FACTOR,
            timeout_seconds=CODE_REVIEW_TIMEOUT_SECONDS / 10  # 180s
        )
    )

    # Validation: Fast, can retry
    supervisor.register_stage(
        "validation",
        RecoveryStrategy(
            action=RecoveryAction.RETRY,
            max_retries=MAX_RETRY_ATTEMPTS - 1,  # 2 retries
            retry_delay_seconds=DEFAULT_RETRY_INTERVAL_SECONDS - 2.0,  # 3s
            backoff_factor=RETRY_BACKOFF_FACTOR,
            timeout_seconds=STAGE_TIMEOUT_SECONDS / 30  # 120s
        )
    )

    # Integration: Important, moderate retry
    supervisor.register_stage(
        "integration",
        RecoveryStrategy(
            action=RecoveryAction.RETRY,
            max_retries=MAX_RETRY_ATTEMPTS - 1,  # 2 retries
            retry_delay_seconds=DEFAULT_RETRY_INTERVAL_SECONDS,  # 5s
            backoff_factor=RETRY_BACKOFF_FACTOR,
            timeout_seconds=STAGE_TIMEOUT_SECONDS / 20  # 180s
        )
    )

    # Testing: Can take time, longer timeout
    supervisor.register_stage(
        "testing",
        RecoveryStrategy(
            action=RecoveryAction.RETRY,
            max_retries=MAX_RETRY_ATTEMPTS - 1,  # 2 retries
            retry_delay_seconds=DEFAULT_RETRY_INTERVAL_SECONDS,  # 5s
            backoff_factor=RETRY_BACKOFF_FACTOR,
            timeout_seconds=STAGE_TIMEOUT_SECONDS / 12  # 300s (5 min)
        )
    )


__all__ = [
    "register_stages_with_supervisor"
]
