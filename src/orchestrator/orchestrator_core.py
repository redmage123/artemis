"""
Orchestrator Core - ArtemisOrchestrator class initialization and properties

WHAT:
Core orchestrator class with dependency injection, initialization logic,
and helper methods for platform detection and supervisor integration.

WHY:
Separates orchestrator initialization from execution logic, enabling:
- Clear dependency injection patterns
- Isolated testing of initialization
- Easy platform detection and resource allocation
- Clean supervisor integration

RESPONSIBILITY:
- Initialize orchestrator with all dependencies
- Detect platform capabilities and resource limits
- Set up observer pattern and execution strategy
- Register stages with supervisor
- Validate configuration

PATTERNS:
- Dependency Injection: All dependencies passed via constructor
- Strategy Pattern: Pluggable execution strategy
- Observer Pattern: Event broadcasting setup
- Factory Pattern: Creates default instances if not provided

EXTRACTED FROM: artemis_orchestrator.py lines 120-404
"""
from typing import Dict, List, Optional, Any
from pathlib import Path
from omegaconf import DictConfig
from artemis_stage_interface import PipelineStage, LoggerInterface
from artemis_services import PipelineLogger, TestRunner
from artemis_exceptions import PipelineConfigurationError
from kanban_manager import KanbanBoard
from messenger_interface import MessengerInterface
from rag_agent import RAGAgent
from config_agent import ConfigurationAgent, get_config
from supervisor_agent import SupervisorAgent
from pipeline_strategies import PipelineStrategy, StandardPipelineStrategy
from platform_detector import PlatformDetector, PlatformInfo, ResourceAllocation, get_platform_summary
from ai_orchestration_planner import OrchestrationPlannerFactory
from pipeline_observer import PipelineObservable, ObserverFactory
from orchestrator.supervisor_integration import register_stages_with_supervisor
from orchestrator.helpers import store_and_validate_platform_info

class ArtemisOrchestrator:
    """
    Artemis Orchestrator - SOLID Refactored

    WHAT:
    Central coordinator for the Artemis autonomous development pipeline. Orchestrates
    execution of 14+ pipeline stages from requirements parsing through final testing,
    managing resources, monitoring health, and coordinating multi-agent collaboration.

    WHY:
    The pipeline has complex coordination requirements:
    - 14+ specialized stages with dependencies
    - Multi-agent development (up to 3 parallel developers)
    - Resource management (CPU, memory, LLM budget)
    - Failure recovery and retry logic
    - Event broadcasting and observability
    - Sprint retrospectives and continuous learning

    A dedicated orchestrator separates coordination from execution, enabling:
    - Clean separation of concerns (orchestration vs stage logic)
    - Pluggable execution strategies (sequential, parallel, distributed)
    - Easy testing and monitoring
    - Graceful failure handling

    PATTERNS:
    - Dependency Injection: All dependencies injected via constructor
    - Strategy Pattern: Pluggable execution strategies (StandardPipelineStrategy, etc.)
    - Observer Pattern: Event broadcasting to multiple observers (metrics, logging, state)
    - Factory Pattern: Creates default stages if not injected
    - Template Method: run_full_pipeline defines algorithm, strategy fills in details

    SOLID COMPLIANCE:
    - Single Responsibility: ONLY orchestrates - delegates work to stages/services
    - Open/Closed: Can add new stages without modifying orchestrator
    - Liskov Substitution: All stages implement PipelineStage interface
    - Interface Segregation: Minimal interfaces (PipelineStage, TestRunner, etc.)
    - Dependency Inversion: Depends on abstractions (interfaces), not concretions

    INTEGRATION:
    - Used by: CLI entry points (main_hydra, main_legacy)
    - Uses: KanbanBoard, MessengerInterface, RAGAgent, SupervisorAgent
    - Creates: Pipeline stages, observers, execution strategy
    - Coordinates: Multi-agent development, code review, testing, retrospectives

    KEY FLOWS:
    1. Initialize: Set up dependencies, platform detection, supervisor, observers
    2. Plan: Generate orchestration plan (AI or rule-based)
    3. Execute: Run stages via strategy (sequential/parallel)
    4. Monitor: Track progress via observers, enforce budgets via supervisor
    5. Recover: Handle failures via supervisor recovery workflows
    6. Learn: Conduct retrospective, store learnings in RAG

    ATTRIBUTES:
        card_id: Kanban card being processed
        board: Kanban board with task queue
        messenger: Agent communication bus
        rag: RAG agent for learning/retrieval
        logger: Logging service
        test_runner: Test execution service
        supervisor: Health monitoring and recovery
        strategy: Pipeline execution strategy
        observable: Event broadcaster for observers
        stages: List of pipeline stage instances
        platform_info: Detected platform characteristics
        resource_allocation: Computed resource limits
    """

    def __init__(self, card_id: str, board: KanbanBoard, messenger: MessengerInterface, rag: RAGAgent, config: Optional[ConfigurationAgent]=None, hydra_config: Optional[DictConfig]=None, logger: Optional[LoggerInterface]=None, test_runner: Optional[TestRunner]=None, stages: Optional[List[PipelineStage]]=None, supervisor: Optional[SupervisorAgent]=None, enable_supervision: bool=True, strategy: Optional[PipelineStrategy]=None, enable_observers: bool=True, resume: bool=False, git_agent: Optional[Any]=None, adaptive_config: Optional[Any]=None):
        """
        Initialize orchestrator with dependency injection

        WHAT:
        Sets up all pipeline dependencies, detects platform capabilities, initializes
        monitoring and recovery systems, and creates default stages if needed.

        WHY:
        Dependency injection enables:
        - Easy testing (mock dependencies)
        - Flexible configuration (swap implementations)
        - Clear dependency graph
        - Independent component evolution

        Platform detection ensures resource allocation respects hardware limits.
        Supervisor enables autonomous recovery from failures.
        Observers provide real-time pipeline monitoring.

        INITIALIZATION SEQUENCE:
        1. Store injected dependencies (card_id, board, messenger, rag)
        2. Set up observer pattern (create observable, attach default observers)
        3. Create execution strategy (uses observable for event broadcasting)
        4. Determine configuration source (Hydra vs legacy ConfigAgent)
        5. Create supervisor if enabled (with LLM learning capability)
        6. Initialize LLM client for sprint workflow stages
        7. Validate configuration (only for legacy ConfigAgent)
        8. Detect platform and calculate resource allocation
        9. Store platform info in RAG for future reference
        10. Initialize AI orchestration planner (AI or rule-based fallback)
        11. Create pipeline stages if not injected
        12. Register stages with supervisor for monitoring

        Args:
            card_id: Kanban card ID
            board: Kanban board instance
            messenger: Agent messenger for communication
            rag: RAG agent for learning
            config: Configuration agent (backward compatibility - deprecated)
            hydra_config: Hydra DictConfig (preferred configuration method)
            logger: Logger implementation (default: PipelineLogger)
            test_runner: Test runner (default: TestRunner)
            stages: List of pipeline stages (default: create standard stages)
            supervisor: Supervisor agent (default: create new SupervisorAgent)
            enable_supervision: Enable pipeline supervision (default: True)
            strategy: Pipeline execution strategy (default: StandardPipelineStrategy)
            enable_observers: Enable pipeline observers (default: True)
            resume: Resume from checkpoint (default: False)
            git_agent: Git Agent for repository management (default: None)
            adaptive_config: Adaptive configuration based on task + platform (default: None)

        RAISES:
            PipelineConfigurationError: If configuration validation fails
        """
        self.card_id = card_id
        self.board = board
        self.messenger = messenger
        self.rag = rag
        self.resume = resume
        self.git_agent = git_agent
        self.adaptive_config = adaptive_config
        self.enable_observers = enable_observers
        self.observable = PipelineObservable(verbose=True) if enable_observers else None
        if self.enable_observers:
            for observer in ObserverFactory.create_default_observers(verbose=True):
                self.observable.attach(observer)
        # Pass adaptive_config to strategy if available
        self.strategy = strategy or StandardPipelineStrategy(
            verbose=True,
            observable=self.observable if enable_observers else None,
            adaptive_config=adaptive_config
        )
        if hydra_config is not None:
            self.hydra_config = hydra_config
            self.config = None
            verbose = hydra_config.logging.verbose
        else:
            self.config = config or get_config(verbose=True)
            self.hydra_config = None
            verbose = True
        self.verbose = verbose
        self.logger = logger or PipelineLogger(verbose=verbose)
        self.test_runner = test_runner or TestRunner()
        if hydra_config is not None:
            self.enable_supervision = hydra_config.pipeline.enable_supervision
        else:
            self.enable_supervision = enable_supervision
        self.supervisor = supervisor or (SupervisorAgent(logger=self.logger, messenger=self.messenger, card_id=self.card_id, rag=self.rag, verbose=verbose, enable_cost_tracking=True, enable_config_validation=True, enable_sandboxing=True, daily_budget=10.0, monthly_budget=200.0) if self.enable_supervision else None)
        if self.supervisor:
            try:
                from llm_client import LLMClientFactory
                llm = LLMClientFactory.create_from_env()
                self.supervisor.enable_learning(llm)
                self.logger.log('✅ Supervisor learning enabled', 'INFO')
            except ImportError:
                self.logger.log('⚠️  LLM client not available - supervisor learning disabled', 'WARNING')
            except Exception as e:
                self.logger.log(f'⚠️  Could not enable supervisor learning: {e}', 'WARNING')
        if self.git_agent:
            self.git_agent.observable = self.observable
            self.git_agent.supervisor = self.supervisor
            self.logger.log('✅ Git Agent integrated with observer pattern and supervisor', 'INFO')
        try:
            from llm_client import LLMClient
            self.llm_client = LLMClient.create_from_env()
            self.logger.log('✅ LLM client initialized for sprint workflow', 'INFO')
        except Exception as e:
            self.logger.log(f'⚠️  LLM client initialization failed: {e}', 'WARNING')
            self.llm_client = None
        if self.config is not None:
            validation = self.config.validate_configuration(require_llm_key=True)
            if not validation.is_valid:
                self.logger.log('❌ Invalid configuration detected', 'ERROR')
                [self.logger.log(f'  Missing: {key}', 'ERROR') for key in validation.missing_keys]
                [self.logger.log(f'  Invalid: {key}', 'ERROR') for key in validation.invalid_keys]
                raise PipelineConfigurationError(f'Invalid Artemis configuration', context={'missing_keys': validation.missing_keys, 'invalid_keys': validation.invalid_keys})
        self.platform_detector = PlatformDetector(logger=self.logger)
        self.platform_info = self.platform_detector.detect_platform()
        self.resource_allocation = self.platform_detector.calculate_resource_allocation(self.platform_info)
        self._store_and_validate_platform_info()
        if self.verbose:
            summary = get_platform_summary(self.platform_info, self.resource_allocation)

            self.logger.log(summary, 'INFO')
        self.orchestration_planner = OrchestrationPlannerFactory.create_planner(llm_client=self.llm_client, logger=self.logger, prefer_ai=True)
        self.logger.log('✅ Orchestration planner initialized', 'INFO')
        if self.adaptive_config:
            self._apply_adaptive_config()
        if stages is None:
            from orchestrator.stage_creation import create_default_stages
            self.stages = create_default_stages(self)
        else:
            self.stages = stages
        if self.enable_supervision and self.supervisor:
            self._register_stages_with_supervisor()

    def _register_stages_with_supervisor(self) -> None:
        """Register all stages with supervisor agent for monitoring (delegated to orchestrator.supervisor_integration)"""
        register_stages_with_supervisor(self.supervisor)

    def _store_and_validate_platform_info(self) -> None:
        """Store platform information in RAG (delegated to orchestrator.helpers)"""
        store_and_validate_platform_info(self.platform_info, self.resource_allocation, self.rag, self.logger, self.verbose)

    def _apply_adaptive_config(self) -> None:
        """
        Apply adaptive configuration settings to orchestrator

        WHY: Adaptive config optimizes resource allocation and pipeline behavior
        based on task complexity and platform capabilities.

        WHAT: Override default config values with adaptive config recommendations:
        - Resource allocation (parallel developers, stages, tests)
        - Pipeline stage selection (skip planning/analysis for simple tasks)
        - Quality vs speed tradeoffs (review depth, validation level)
        - Checkpoint frequency (more frequent in resource-constrained environments)
        """
        if not self.adaptive_config:
            return

        if self.verbose:
            self.logger.log('\n🔧 Applying Adaptive Configuration...', 'INFO')
            self.logger.log(f'   Profile: {self.adaptive_config.profile}', 'INFO')

        # Store adaptive config in RAG for future reference
        try:
            from datetime import datetime
            config_record = {
                'timestamp': datetime.now().isoformat(),
                'card_id': self.card_id,
                'profile': self.adaptive_config.profile,
                'config': self.adaptive_config.to_dict(),
                'reasoning': self.adaptive_config.reasoning
            }
            self.rag.store_data(
                'adaptive_configs',
                f'config_{self.card_id}',
                config_record
            )
            if self.verbose:
                self.logger.log('   ✅ Adaptive config stored in RAG', 'INFO')
        except Exception as e:
            self.logger.log(f'   ⚠️  Could not store adaptive config in RAG: {e}', 'WARNING')

        if self.verbose:
            self.logger.log('   ✅ Adaptive config applied\n', 'INFO')