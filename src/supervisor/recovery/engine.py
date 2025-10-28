#!/usr/bin/env python3
"""
Module: supervisor/recovery/engine.py

WHY: Main orchestrator for failure recovery across all strategies
RESPONSIBILITY: Coordinate recovery strategies, track statistics, handle crashes and hangs
PATTERNS: Facade (unified recovery interface), Strategy (pluggable recovery), Chain of Responsibility (fallback)

Design Philosophy:
- Unified interface for all recovery operations
- Chain of responsibility through multiple strategies
- Statistics tracking for monitoring and optimization
- Learning from successful recoveries
"""

from typing import Dict, List, Optional, Any

from artemis_stage_interface import LoggerInterface
from supervisor.recovery.strategies import (
    JSONParsingStrategy,
    RetryStrategy,
    DefaultValueStrategy,
    SkipStageStrategy
)
from supervisor.recovery.failure_analysis import FailureAnalyzer
from supervisor.recovery.state_restoration import StateRestoration
from supervisor.recovery.llm_auto_fix import LLMAutoFix


class RecoveryEngine:
    """
    Main orchestrator for failure recovery.

    WHY: Provides intelligent, multi-strategy recovery from failures,
    maximizing pipeline resilience through automated fixes before falling back
    to manual intervention.

    RESPONSIBILITY:
    - Recover crashed agents via error analysis and code fixes
    - Recover hung agents via termination and restart
    - Handle unexpected states via learning engine
    - Apply recovery strategies in fallback chain
    - Track recovery statistics and success rates

    PATTERNS:
    - Facade: Unified interface for recovery operations
    - Strategy: Pluggable recovery strategies
    - Chain of Responsibility: Fallback through strategy sequence

    Recovery Strategy Chain:
    1. LLM auto-fix: Analyze error, extract file/line, suggest fix
    2. JSON parsing fix: Extract JSON from markdown, clean formatting
    3. Fallback retry: Exponential backoff (2^n seconds)
    4. Default values: Substitute sensible defaults for missing keys
    5. Skip stage: Skip non-critical stages (ui_ux, docs, etc.)
    6. Manual intervention: Request human assistance

    Integration points:
    - LLM client: For intelligent error analysis and fixes
    - RAG agent: For querying similar past issues
    - Learning engine: For storing successful solutions
    - State machine: For state rollback and restart
    - Messenger: For manual intervention alerts

    Thread-safety: Not thread-safe (assumes single-threaded supervisor)
    """

    def __init__(
        self,
        logger: Optional[LoggerInterface] = None,
        verbose: bool = True,
        llm_client: Optional[Any] = None,
        rag: Optional[Any] = None,
        learning_engine: Optional[Any] = None,
        state_machine: Optional[Any] = None,
        messenger: Optional[Any] = None
    ):
        """
        Initialize Recovery Engine.

        Args:
            logger: Logger for recording events
            verbose: Enable verbose logging
            llm_client: LLM client for auto-fix
            rag: RAG agent for querying similar issues
            learning_engine: Learning engine for solution learning
            state_machine: State machine for rollback
            messenger: Messenger for alerts
        """
        self.logger = logger
        self.verbose = verbose

        # Component initialization
        self.failure_analyzer = FailureAnalyzer()
        self.state_restoration = StateRestoration(state_machine, messenger)
        self.llm_auto_fix = LLMAutoFix(llm_client, rag, learning_engine)

        # Recovery strategies (in order of preference)
        self.strategies = [
            JSONParsingStrategy(),
            RetryStrategy(),
            DefaultValueStrategy(),
            SkipStageStrategy()
        ]

        # External services
        self.learning_engine = learning_engine

        # Statistics
        self.stats = {
            "crashes_recovered": 0,
            "hangs_recovered": 0,
            "json_fixes": 0,
            "retries": 0,
            "defaults_used": 0,
            "stages_skipped": 0,
            "llm_fixes": 0,
            "manual_interventions": 0
        }

    def recover_crashed_agent(
        self,
        crash_info: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Recover a crashed agent by fixing the error and restarting.

        WHY: Automated crash recovery minimizes pipeline downtime
        RESPONSIBILITY: Analyze crash, apply fix, restart agent
        PERFORMANCE: O(1) dictionary lookups, O(n) file reading for context

        Args:
            crash_info: Information about the crash
            context: Execution context

        Returns:
            Recovery result dict
        """
        self._log(f"🚑 Recovering crashed agent...")
        self._log(f"   Agent: {crash_info.get('agent_name')}")
        self._log(f"   Error: {crash_info.get('error')}")

        try:
            # Analyze crash
            analysis = self.failure_analyzer.analyze_crash(crash_info)

            # Merge analysis into context
            context.update(analysis)

            # Try LLM-powered auto-fix
            fix_result = self.llm_auto_fix.analyze_and_fix(
                analysis["exception"],
                analysis["traceback"],
                context
            )

            # Guard clause: Auto-fix failed
            if not fix_result or not fix_result.get("success"):
                self._log("⚠️  Auto-fix failed, cannot recover automatically", "WARNING")
                self.stats["manual_interventions"] += 1

                return {
                    "success": False,
                    "recovery_strategy": "manual_intervention_required",
                    "message": "Auto-fix failed, manual intervention required"
                }

            # Auto-fix succeeded, restart agent
            self._log("✅ Error fixed, restarting agent...")

            # Update stats based on fix type
            self._update_stats_for_fix(fix_result)

            # Apply fix to context
            context = self.state_restoration.apply_context_fix(context, fix_result)

            # Restart stage
            restart_result = self.state_restoration.restart_stage(context, fix_result)
            self.stats["crashes_recovered"] += 1

            return {
                "success": True,
                "recovery_strategy": "auto_fix_and_restart",
                "fix_result": fix_result,
                "restart_result": restart_result,
                "message": "Successfully recovered crashed agent using auto-fix and restart"
            }

        except Exception as e:
            self._log(f"❌ Recovery failed: {e}", "ERROR")

            return {
                "success": False,
                "error": str(e),
                "message": f"Recovery failed: {e}"
            }

    def recover_hung_agent(
        self,
        agent_name: str,
        timeout_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Recover a hung agent by terminating and restarting it.

        WHY: Hung agents block pipeline progress, need forced termination
        RESPONSIBILITY: Terminate hung agent, restart with increased timeout
        PERFORMANCE: O(1) dictionary lookups, external process termination

        Args:
            agent_name: Name of the hung agent
            timeout_info: Information about the timeout

        Returns:
            Recovery result dict
        """
        self._log(f"⏰ Recovering hung agent '{agent_name}'...")

        try:
            timeout_seconds = timeout_info.get("timeout_seconds", 300)
            elapsed_time = timeout_info.get("elapsed_time", 0)

            self._log(f"   Timeout: {timeout_seconds}s, Elapsed: {elapsed_time}s")

            # Terminate the agent
            termination_result = self.state_restoration.terminate_agent(agent_name)

            # Guard clause: Termination failed
            if not termination_result.get("success"):
                self._log("⚠️  Failed to terminate hung agent", "WARNING")
                self.stats["manual_interventions"] += 1

                return {
                    "success": False,
                    "recovery_strategy": "manual_intervention_required",
                    "message": "Failed to terminate hung agent, manual intervention required"
                }

            # Termination succeeded, restart with longer timeout
            self._log(f"✅ Terminated hung agent '{agent_name}'")

            restart_result = self.state_restoration.restart_with_timeout(
                agent_name,
                timeout_info
            )
            self.stats["hangs_recovered"] += 1

            return {
                "success": True,
                "recovery_strategy": "terminate_and_restart",
                "termination_result": termination_result,
                "restart_result": restart_result,
                "new_timeout": restart_result.get("new_timeout"),
                "message": restart_result.get("message")
            }

        except Exception as e:
            self._log(f"❌ Recovery failed: {e}", "ERROR")

            return {
                "success": False,
                "error": str(e),
                "message": f"Recovery failed: {e}"
            }

    def handle_unexpected_state(
        self,
        current_state: str,
        expected_states: List[str],
        context: Dict[str, Any],
        auto_learn: bool = True
    ) -> Optional[Dict[str, Any]]:
        """
        Handle an unexpected state using learning engine and fallback strategies.

        WHY: Learning from unexpected states improves pipeline robustness over time
        RESPONSIBILITY: Detect unexpected state, learn solution, apply fix
        PERFORMANCE: O(1) dictionary lookups, O(n) LLM consultation if needed

        Args:
            current_state: Current state
            expected_states: List of expected states
            context: Context information
            auto_learn: Automatically learn and apply solution

        Returns:
            Solution result if handled, None otherwise
        """
        # Guard clause: No learning engine available
        if not self.learning_engine:
            self._log("⚠️  Learning engine not enabled, trying fallback strategies", "WARNING")
            return self._try_fallback_strategies(context)

        # Detect unexpected state
        unexpected = self.learning_engine.detect_unexpected_state(
            card_id=context.get("card_id", "unknown"),
            current_state=current_state,
            expected_states=expected_states,
            context=context
        )

        # Guard clause: State is actually expected
        if not unexpected:
            return None

        # Guard clause: Detection only mode
        if not auto_learn:
            return {
                "unexpected_state": unexpected,
                "action": "detected_only"
            }

        # Learn solution
        self._log("🧠 Learning solution for unexpected state...")

        from supervisor_learning import LearningStrategy
        solution = self.learning_engine.learn_solution(
            unexpected,
            strategy=LearningStrategy.LLM_CONSULTATION
        )

        # Guard clause: Could not learn solution
        if not solution:
            self._log("❌ Could not learn solution - trying fallback strategies...", "WARNING")
            return self._try_fallback_strategies(context)

        # Apply learned solution
        self._log("🔧 Applying learned solution...")
        success = self.learning_engine.apply_learned_solution(solution, context)

        return {
            "unexpected_state": unexpected,
            "solution": solution,
            "success": success,
            "action": "learned_and_applied"
        }

    def _try_fallback_strategies(self, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Try all fallback recovery strategies in sequence.

        WHY: Chain of Responsibility pattern provides graceful degradation
        RESPONSIBILITY: Try each strategy until one succeeds
        PERFORMANCE: O(n) where n = number of strategies, stops at first success

        Args:
            context: Execution context

        Returns:
            Recovery result if any strategy succeeds, None otherwise
        """
        exception = context.get("exception")

        # Guard clause: No exception in context
        if not exception:
            return None

        # Try each strategy in order until one succeeds
        for strategy in self.strategies:
            # Check if strategy can handle this error
            if not strategy.can_handle(exception, context):
                continue

            # Try recovery with this strategy
            result = strategy.recover(exception, context)
            if result and result.get("success"):
                # Update stats for this strategy
                self._update_stats_for_fix(result)
                return result

        # All strategies failed - request manual intervention
        self._log("🚨 All recovery strategies failed - requesting manual intervention", "ERROR")
        self.stats["manual_interventions"] += 1

        return {
            "action": "manual_intervention_required",
            "message": "All automated recovery strategies failed. Manual intervention needed."
        }

    def _update_stats_for_fix(self, fix_result: Dict[str, Any]) -> None:
        """
        Update statistics based on fix type.

        WHY: Track which recovery strategies are most effective
        RESPONSIBILITY: Increment appropriate stat counters
        PERFORMANCE: O(1) dictionary lookup and increment

        Args:
            fix_result: Fix result with strategy name
        """
        strategy = fix_result.get("strategy", "")

        # Dispatch table for stat updates (avoid if/elif)
        stat_mapping = {
            "json_parsing_fix": "json_fixes",
            "json_extraction": "json_fixes",
            "retry_with_backoff": "retries",
            "default_values": "defaults_used",
            "skip_stage": "stages_skipped"
        }

        stat_key = stat_mapping.get(strategy)
        if stat_key:
            self.stats[stat_key] += 1

        # Check for LLM fix
        if "llm" in strategy.lower() or fix_result.get("file_path"):
            self.stats["llm_fixes"] += 1

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get recovery statistics.

        WHY: Track recovery metrics for monitoring and optimization
        RESPONSIBILITY: Calculate and return recovery stats
        PERFORMANCE: O(1) dictionary operations and arithmetic

        Returns:
            Dict with statistics including success rate
        """
        total_recoveries = self.stats["crashes_recovered"] + self.stats["hangs_recovered"]

        return {
            **self.stats,
            "total_recoveries": total_recoveries,
            "success_rate": self._calculate_success_rate()
        }

    def _calculate_success_rate(self) -> float:
        """
        Calculate overall success rate.

        WHY: Measure effectiveness of automated recovery strategies
        RESPONSIBILITY: Calculate percentage of successful recoveries
        PERFORMANCE: O(1) arithmetic operations

        Returns:
            Success rate as percentage (0-100)
        """
        total = self.stats["crashes_recovered"] + self.stats["hangs_recovered"]
        manual = self.stats["manual_interventions"]

        # Guard clause: No recoveries attempted yet
        if total + manual == 0:
            return 0.0

        return (total / (total + manual)) * 100

    def _log(self, message: str, level: str = "INFO") -> None:
        """
        Log a message.

        WHY: Centralized logging for debugging and monitoring
        RESPONSIBILITY: Route messages to logger or stdout
        PERFORMANCE: O(1) conditional checks

        Args:
            message: Message to log
            level: Log level (INFO, WARNING, ERROR)
        """
        if self.logger:
            self.logger.log(message, level)
        elif self.verbose:
            prefix = "[RecoveryEngine]"
            print(f"{prefix} {message}")
