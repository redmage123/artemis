"""
Module: agents/supervisor/supervisor.py

WHY: Main orchestrator for pipeline supervision using composition of specialized components.
RESPONSIBILITY: Coordinate health monitoring, recovery, and pipeline execution.
PATTERNS: Facade Pattern (unified interface), Composition (delegates to specialized engines).

This is the new modular supervisor that replaces the monolithic SupervisorAgent class.

Architecture:
- Composes specialized components (AutoFixEngine, HeartbeatManager, CircuitBreakerManager)
- Delegates work to specialized engines (SRP compliance)
- Provides unified facade for pipeline supervision
- Minimal orchestration logic (most work done by components)

REPLACES: supervisor_agent.py SupervisorAgent class (will become backward compatibility wrapper)
"""

from typing import Dict, List, Optional, Any
from datetime import datetime

from artemis_stage_interface import LoggerInterface
from agents.supervisor.models import HealthStatus, RecoveryStrategy, StageHealth
from agents.supervisor.auto_fix import AutoFixEngine
from agents.supervisor.heartbeat import HeartbeatManager, AgentHealthEvent
from agents.supervisor.circuit_breaker import CircuitBreakerManager


class Supervisor:
    """
    Modular supervisor for Artemis pipeline

    WHY: Clean composition-based architecture replacing monolithic SupervisorAgent
    PATTERNS: Facade, Composition, Delegation
    """

    def __init__(
        self,
        logger: Optional[LoggerInterface] = None,
        messenger: Optional[Any] = None,
        card_id: Optional[str] = None,
        rag: Optional[Any] = None,
        verbose: bool = True,
        enable_cost_tracking: bool = True,
        enable_config_validation: bool = True,
        enable_sandboxing: bool = True,
        daily_budget: Optional[float] = None,
        monthly_budget: Optional[float] = None,
        hydra_config: Optional[Any] = None
    ):
        """
        Initialize modular supervisor

        Args:
            logger: Logger for recording events
            messenger: AgentMessenger for alerts
            card_id: Optional card ID for state machine
            rag: Optional RAG agent for learning from history
            verbose: Enable verbose logging
            enable_cost_tracking: Enable LLM cost tracking
            enable_config_validation: Enable startup config validation
            enable_sandboxing: Enable security sandboxing for code execution
            daily_budget: Daily LLM budget (None = unlimited)
            monthly_budget: Monthly LLM budget (None = unlimited)
            hydra_config: Hydra configuration object (for LLM settings)
        """
        # Basic attributes
        self.logger = logger
        self.messenger = messenger
        self.verbose = verbose
        self.rag = rag
        self.card_id = card_id
        self.hydra_config = hydra_config

        # LLM configuration
        self._init_llm_config()

        # Initialize specialized components (Composition Pattern)
        self.auto_fix_engine = AutoFixEngine(
            llm_client=None,  # Will be set when needed
            verbose=verbose,
            llm_model=self.llm_model,
            llm_temperature=self.llm_temperature
        )

        self.heartbeat_manager = HeartbeatManager(
            verbose=verbose,
            state_machine=None,  # Will be set later
            stage_health={}
        )

        self.circuit_breaker = CircuitBreakerManager(
            verbose=verbose,
            messenger=messenger,
            state_machine=None,  # Will be set later
            logger=logger
        )

        # Run validation if enabled
        if enable_config_validation:
            self._run_config_validation()
            self._run_preflight_validation()

        # Initialize optional subsystems
        self._init_cost_tracking(enable_cost_tracking, card_id, daily_budget, monthly_budget)
        self._init_security_sandbox(enable_sandboxing)
        self._init_learning_engine()
        self._init_state_machine(card_id, verbose)
        self._init_statistics()

        if self.verbose and self.logger:
            self.logger.log("[Supervisor] Initialized modular supervisor with composition-based architecture", "INFO")

    def _init_llm_config(self) -> None:
        """Initialize LLM configuration from Hydra config"""
        self.llm_model = "gpt-4"
        self.llm_temperature = 0.3
        self.llm_max_tokens = 4000

        # Guard: no hydra config
        if not self.hydra_config or not hasattr(self.hydra_config, 'llm'):
            return

        # Use supervisor-specific settings if available
        if hasattr(self.hydra_config.llm, 'supervisor'):
            self.llm_model = self.hydra_config.llm.supervisor.model
            self.llm_temperature = self.hydra_config.llm.supervisor.temperature
            self.llm_max_tokens = self.hydra_config.llm.supervisor.max_tokens
        else:
            self.llm_model = self.hydra_config.llm.model
            self.llm_temperature = getattr(self.hydra_config.llm, 'temperature', 0.7)
            self.llm_max_tokens = getattr(self.hydra_config.llm, 'max_tokens_per_request', 4000)

        if self.verbose and self.llm_model and self.logger:
            self.logger.log(f"[Supervisor] Using LLM model: {self.llm_model} (temp={self.llm_temperature})", "INFO")

    def _run_config_validation(self) -> None:
        """Run startup configuration validation"""
        if self.verbose and self.logger:
            self.logger.log("[Supervisor] Running startup configuration validation...", "INFO")

        from config_validator import ConfigValidator

        validator = ConfigValidator(verbose=self.verbose)
        report = validator.validate_all()

        # Guard: validation failed
        if report.overall_status == "fail":
            raise RuntimeError(f"Configuration validation failed: {report.errors} errors")

        # Guard: warnings only
        if report.overall_status == "warning" and self.verbose and self.logger:
            self.logger.log(f"[Supervisor] ⚠️  Configuration warnings: {report.warnings} warnings", "WARNING")

    def _run_preflight_validation(self) -> None:
        """Run preflight validation (syntax checks with auto-fix)"""
        if self.verbose and self.logger:
            self.logger.log("[Supervisor] Running preflight validation (syntax checks)...", "INFO")

        try:
            from preflight_validator import PreflightValidator
            import os

            # Setup LLM for auto-fixing
            llm_client, auto_fix_enabled = self.auto_fix_engine.setup_llm_for_autofix()

            preflight = PreflightValidator(
                verbose=self.verbose,
                llm_client=llm_client,
                auto_fix=auto_fix_enabled
            )

            # Validate src directory (where main modules are located)
            supervisor_dir = os.path.dirname(os.path.abspath(__file__))
            src_dir = os.path.dirname(os.path.dirname(supervisor_dir))  # Go up from agents/supervisor/ to src/
            preflight_results = preflight.validate_all(src_dir)

            # Handle results (may auto-fix and restart)
            self.auto_fix_engine.handle_preflight_results(preflight, preflight_results, auto_fix_enabled)

        except ImportError as e:
            if self.verbose and self.logger:
                self.logger.log(f"[Supervisor] ⚠️  Preflight validator not available - skipping syntax checks: {e}", "WARNING")

    def _init_cost_tracking(
        self,
        enable_cost_tracking: bool,
        card_id: Optional[str],
        daily_budget: Optional[float],
        monthly_budget: Optional[float]
    ) -> None:
        """Initialize LLM cost tracking"""
        self.cost_tracker = None

        # Guard: cost tracking disabled
        if not enable_cost_tracking:
            return

        import os
        from cost_tracker import CostTracker

        # Get cost tracking directory
        cost_dir = os.getenv("ARTEMIS_COST_DIR", "../../.artemis_data/cost_tracking")
        if not os.path.isabs(cost_dir):
            script_dir = os.path.dirname(os.path.abspath(__file__))
            cost_dir = os.path.join(script_dir, cost_dir)

        # Create cost tracker
        cost_filename = f"artemis_costs_{card_id}.json" if card_id else "artemis_costs.json"
        storage_path = os.path.join(cost_dir, cost_filename)

        self.cost_tracker = CostTracker(
            storage_path=storage_path,
            daily_budget=daily_budget,
            monthly_budget=monthly_budget
        )

        if self.verbose and self.logger:
            self.logger.log(f"[Supervisor] Cost tracking enabled: {storage_path}", "INFO")

    def _init_security_sandbox(self, enable_sandboxing: bool) -> None:
        """Initialize security sandbox for code execution"""
        self.sandbox_executor = None

        # Guard: sandboxing disabled
        if not enable_sandboxing:
            return

        from sandbox_executor import SandboxExecutor, SandboxConfig

        self.sandbox_executor = SandboxExecutor(
            config=SandboxConfig()
        )

        if self.verbose and self.logger:
            self.logger.log("[Supervisor] Security sandbox enabled", "INFO")

    def _init_learning_engine(self) -> None:
        """Initialize learning engine for unexpected state handling"""
        self.learning_engine = None

        try:
            from supervisor_learning import SupervisorLearningEngine

            self.learning_engine = SupervisorLearningEngine(
                rag_agent=self.rag,
                verbose=self.verbose
            )

            if self.verbose and self.logger:
                self.logger.log("[Supervisor] Learning engine initialized", "INFO")

        except ImportError:
            if self.verbose and self.logger:
                self.logger.log("[Supervisor] Learning engine not available", "WARNING")

    def _init_state_machine(self, card_id: Optional[str], verbose: bool) -> None:
        """Initialize state machine for pipeline tracking"""
        self.state_machine = None

        # Guard: no card_id
        if not card_id:
            return

        from artemis_state_machine import ArtemisStateMachine

        self.state_machine = ArtemisStateMachine(card_id=card_id, verbose=verbose)

        # Share state machine with components
        self.heartbeat_manager.state_machine = self.state_machine
        self.circuit_breaker.state_machine = self.state_machine

        if self.verbose and self.logger:
            self.logger.log(f"[Supervisor] State machine initialized for card: {card_id}", "INFO")

    def _init_statistics(self) -> None:
        """Initialize statistics tracking"""
        self.statistics = {
            "start_time": datetime.now().isoformat(),
            "stages_executed": 0,
            "stages_failed": 0,
            "stages_recovered": 0,
            "auto_fixes_applied": 0,
            "circuit_breakers_opened": 0,
        }

    # ========== Public API - Delegation to Components ==========

    def register_stage(
        self,
        stage_name: str,
        recovery_strategy: Optional[RecoveryStrategy] = None
    ) -> None:
        """Delegate to circuit breaker manager"""
        self.circuit_breaker.register_stage(stage_name, recovery_strategy)

    def check_circuit_breaker(self, stage_name: str) -> bool:
        """Delegate to circuit breaker manager"""
        return self.circuit_breaker.check_circuit_breaker(stage_name)

    def open_circuit_breaker(self, stage_name: str) -> None:
        """Delegate to circuit breaker manager"""
        self.circuit_breaker.open_circuit_breaker(stage_name)
        self.statistics["circuit_breakers_opened"] += 1

    def register_agent(
        self,
        agent_name: str,
        agent_type: str = "stage",
        metadata: Optional[Dict[str, Any]] = None,
        heartbeat_interval: float = 15.0
    ) -> None:
        """Delegate to heartbeat manager"""
        self.heartbeat_manager.register_agent(agent_name, agent_type, metadata, heartbeat_interval)

    def unregister_agent(self, agent_name: str) -> None:
        """Delegate to heartbeat manager"""
        self.heartbeat_manager.unregister_agent(agent_name)

    def agent_heartbeat(
        self,
        agent_name: str,
        progress_data: Optional[Dict[str, Any]] = None
    ) -> None:
        """Delegate to heartbeat manager"""
        self.heartbeat_manager.agent_heartbeat(agent_name, progress_data)

    def auto_fix_error(
        self,
        error: Exception,
        traceback_info: str,
        context: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Delegate to auto-fix engine"""
        result = self.auto_fix_engine.auto_fix_error(error, traceback_info, context)

        if result and result.get("success"):
            self.statistics["auto_fixes_applied"] += 1

        return result

    def get_health_status(self) -> HealthStatus:
        """Get overall health status"""
        # Check all registered stages
        all_health = self.circuit_breaker.get_all_stage_health()

        # Guard: no stages registered
        if not all_health:
            return HealthStatus.HEALTHY

        # Count failures
        open_circuits = sum(1 for h in all_health.values() if h.circuit_open)
        total_failures = sum(h.failure_count for h in all_health.values())

        # Determine health status
        if open_circuits > 0:
            return HealthStatus.CRITICAL
        if total_failures > 5:
            return HealthStatus.DEGRADED

        return HealthStatus.HEALTHY

    def get_statistics(self) -> Dict[str, Any]:
        """Get supervisor statistics"""
        return {
            **self.statistics,
            "health_status": self.get_health_status().value,
            "registered_agents": len(self.heartbeat_manager.get_all_agents()),
            "registered_stages": len(self.circuit_breaker.get_all_stage_health()),
        }

    def log_health_report(self) -> None:
        """Log supervisor health report (renamed from print_health_report)"""
        if not self.logger:
            return

        self.logger.log("="*70, "INFO")
        self.logger.log("SUPERVISOR HEALTH REPORT", "INFO")
        self.logger.log("="*70, "INFO")

        # Health status
        health_status = self.get_health_status()
        status_emoji = {
            HealthStatus.HEALTHY: "✅",
            HealthStatus.DEGRADED: "⚠️",
            HealthStatus.CRITICAL: "❌"
        }
        self.logger.log(f"Overall Health: {status_emoji.get(health_status, '?')} {health_status.value.upper()}", "INFO")

        # Statistics
        stats = self.get_statistics()
        self.logger.log(f"Registered Agents: {stats['registered_agents']}", "INFO")
        self.logger.log(f"Registered Stages: {stats['registered_stages']}", "INFO")

        # Stage health
        all_health = self.circuit_breaker.get_all_stage_health()
        if all_health:
            self.logger.log("Stage Health:", "INFO")
            for stage_name, health in all_health.items():
                circuit_status = "🚨 OPEN" if health.circuit_open else "✅ CLOSED"
                self.logger.log(f"  - {stage_name}: {circuit_status} (failures: {health.failure_count}, executions: {health.execution_count})", "INFO")

        self.logger.log("="*70, "INFO")

    def print_health_report(self) -> None:
        """Deprecated: Use log_health_report() instead. This method is kept for backward compatibility."""
        self.log_health_report()

    def cleanup_zombie_processes(self) -> int:
        """
        Clean up zombie processes

        Returns:
            Number of processes cleaned up
        """
        # Guard: no heartbeat manager
        if not hasattr(self, 'heartbeat_manager'):
            return 0

        try:
            import psutil
            cleaned = 0

            # Get all hanging processes from heartbeat manager
            hanging_processes = self.heartbeat_manager.detect_hanging_processes()

            for proc_health in hanging_processes:
                try:
                    process = psutil.Process(proc_health.pid)
                    process.terminate()
                    process.wait(timeout=3)
                    cleaned += 1
                    if self.verbose and self.logger:
                        self.logger.log(f"[Supervisor] Terminated hanging process: {proc_health.name} (PID: {proc_health.pid})", "INFO")
                except (psutil.NoSuchProcess, psutil.TimeoutExpired):
                    pass

            return cleaned
        except Exception as e:
            if self.verbose and self.logger:
                self.logger.log(f"[Supervisor] Error cleaning up processes: {e}", "ERROR")
            return 0


__all__ = [
    "Supervisor"
]
