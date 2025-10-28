"""
Recovery subpackage - Modularized recovery engine components.

Part of: supervisor

WHY: Intelligent failure recovery through multiple strategies
RESPONSIBILITY: Crash recovery, hang recovery, error analysis, state restoration

This package contains the decomposed RecoveryEngine components:
- engine: Main RecoveryEngine orchestrator class
- strategy: Base RecoveryStrategy class
- strategies: Concrete recovery strategies (JSON, retry, defaults, skip)
- failure_analysis: Error parsing and categorization
- state_restoration: Stage restart and agent termination
- llm_auto_fix: LLM-powered intelligent error fixing

ARCHITECTURE:
- Strategy pattern for pluggable recovery approaches
- Chain of Responsibility for fallback sequence
- Facade pattern in RecoveryEngine for unified interface
- Template Method in base strategy class

RECOVERY CHAIN:
1. LLM auto-fix (intelligent analysis)
2. JSON parsing fix (markdown extraction)
3. Retry with backoff (transient errors)
4. Default values (missing keys)
5. Skip stage (non-critical stages)
6. Manual intervention (last resort)

INTEGRATION POINTS:
- LLM client for intelligent fixes
- RAG agent for known solutions
- Learning engine for solution storage
- State machine for stage transitions
- Messenger for alerts

DESIGN PHILOSOPHY:
"Fail gracefully, learn continuously"
- Automated recovery before manual intervention
- Learning from successful fixes
- Graceful degradation through fallback chain
- Statistics tracking for optimization
"""

# Export main RecoveryEngine class
from supervisor.recovery.engine import RecoveryEngine

# Export base strategy class
from supervisor.recovery.strategy import RecoveryStrategy

# Export concrete strategies
from supervisor.recovery.strategies import (
    JSONParsingStrategy,
    RetryStrategy,
    DefaultValueStrategy,
    SkipStageStrategy
)

# Export supporting components
from supervisor.recovery.failure_analysis import FailureAnalyzer
from supervisor.recovery.state_restoration import StateRestoration
from supervisor.recovery.llm_auto_fix import LLMAutoFix

__all__ = [
    # Main class
    "RecoveryEngine",

    # Base strategy
    "RecoveryStrategy",

    # Concrete strategies
    "JSONParsingStrategy",
    "RetryStrategy",
    "DefaultValueStrategy",
    "SkipStageStrategy",

    # Supporting components
    "FailureAnalyzer",
    "StateRestoration",
    "LLMAutoFix",
]
