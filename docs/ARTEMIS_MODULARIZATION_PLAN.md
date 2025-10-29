# Artemis Codebase Modularization Plan

## Executive Summary

**Current State:** 181 Python files in `/src` root directory
**Problem:** God classes, violation of Single Responsibility Principle, difficult maintenance
**Goal:** Modularize into logical packages with max 300-500 lines per module
**Timeline:** 4 phases over 6-8 weeks
**Risk Level:** Medium (requires careful dependency management)

---

## 1. Proposed Directory Structure

```
src/
├── core/                          # Core abstractions and interfaces
│   ├── __init__.py
│   ├── interfaces.py              # PipelineStage, LoggerInterface, etc.
│   ├── exceptions.py              # Exception hierarchy
│   ├── constants.py               # System constants
│   └── state_machine.py           # State management
│
├── agents/                        # All autonomous agents
│   ├── __init__.py
│   ├── base/
│   │   ├── __init__.py
│   │   ├── agent_interface.py     # Base agent interface
│   │   └── debug_mixin.py         # Debug functionality
│   ├── developer/
│   │   ├── __init__.py
│   │   ├── standalone_agent.py    # Main developer agent (400 lines)
│   │   ├── tdd_workflow.py        # TDD workflow logic (350 lines)
│   │   ├── code_generation.py     # Code generation strategies (400 lines)
│   │   ├── streaming_validator.py # Real-time validation (350 lines)
│   │   ├── retry_coordinator.py   # Retry logic (300 lines)
│   │   └── developer_invoker.py   # Developer invocation (existing, 200 lines)
│   ├── supervisor/
│   │   ├── __init__.py
│   │   ├── supervisor_agent.py    # Main supervisor (400 lines)
│   │   ├── health_monitor.py      # Health monitoring (350 lines)
│   │   ├── recovery_engine.py     # Recovery strategies (400 lines)
│   │   ├── circuit_breaker.py     # Circuit breaker (existing, 250 lines)
│   │   ├── learning_engine.py     # ML learning (existing, 400 lines)
│   │   └── health_observer.py     # Health event observers (250 lines)
│   ├── analysis/
│   │   ├── __init__.py
│   │   ├── project_analysis_agent.py  # Project analysis (existing, 400 lines)
│   │   ├── code_refactoring_agent.py  # Refactoring (existing, 350 lines)
│   │   └── requirements_parser_agent.py  # Requirements (existing, 300 lines)
│   ├── review/
│   │   ├── __init__.py
│   │   ├── code_review_agent.py   # Code review (existing, 350 lines)
│   │   └── retrospective_agent.py # Retrospectives (existing, 300 lines)
│   ├── rag_agent.py               # RAG agent (existing, < 500 lines)
│   ├── config_agent.py            # Configuration (existing, < 500 lines)
│   ├── git_agent.py               # Git operations (existing, < 500 lines)
│   └── chat_agent.py              # Chat agent (existing, < 500 lines)
│
├── pipelines/                     # Pipeline implementations
│   ├── __init__.py
│   ├── standard/
│   │   ├── __init__.py
│   │   ├── orchestrator.py        # Main orchestrator (400 lines)
│   │   ├── workflow_planner.py    # Workflow planning (300 lines)
│   │   ├── strategies.py          # Pipeline strategies (existing, 300 lines)
│   │   └── status_tracker.py      # Status tracking (existing, 300 lines)
│   ├── advanced/
│   │   ├── __init__.py
│   │   ├── dynamic/
│   │   │   ├── __init__.py
│   │   │   ├── pipeline.py        # Dynamic pipeline core (450 lines)
│   │   │   ├── builder.py         # Pipeline builder (350 lines)
│   │   │   ├── selectors.py       # Stage selection strategies (400 lines)
│   │   │   ├── executors.py       # Stage executors (350 lines)
│   │   │   └── factory.py         # Pipeline factory (250 lines)
│   │   ├── two_pass/
│   │   │   ├── __init__.py
│   │   │   ├── pipeline.py        # Two-pass core (400 lines)
│   │   │   ├── strategies.py      # Pass strategies (400 lines)
│   │   │   ├── memento.py         # State capture (350 lines)
│   │   │   ├── comparator.py      # Pass comparison (300 lines)
│   │   │   ├── rollback.py        # Rollback manager (300 lines)
│   │   │   └── factory.py         # Pipeline factory (200 lines)
│   │   ├── thermodynamic/
│   │   │   ├── __init__.py
│   │   │   ├── computing.py       # Main facade (400 lines)
│   │   │   ├── strategies.py      # Uncertainty strategies (450 lines)
│   │   │   ├── bayesian.py        # Bayesian inference (400 lines)
│   │   │   ├── monte_carlo.py     # MC simulation (350 lines)
│   │   │   ├── ensemble.py        # Ensemble methods (350 lines)
│   │   │   ├── temperature.py     # Temperature scheduling (300 lines)
│   │   │   └── confidence.py      # Confidence scoring (300 lines)
│   │   └── integration.py         # Advanced pipeline integration (500 lines)
│   ├── routing/
│   │   ├── __init__.py
│   │   ├── router.py              # Base intelligent router (400 lines)
│   │   ├── enhanced_router.py     # Enhanced router (450 lines)
│   │   ├── routing_decisions.py   # Decision models (300 lines)
│   │   └── risk_analysis.py       # Risk factor analysis (350 lines)
│   ├── observer.py                # Pipeline observer (existing, 400 lines)
│   └── persistence.py             # Pipeline persistence (existing, 300 lines)
│
├── stages/                        # Pipeline stages
│   ├── __init__.py
│   ├── base/
│   │   ├── __init__.py
│   │   ├── stage_interface.py     # Stage interface
│   │   └── supervised_mixin.py    # Supervision mixin
│   ├── analysis/
│   │   ├── __init__.py
│   │   ├── project_analysis.py    # Project analysis (400 lines)
│   │   ├── requirements.py        # Requirements parsing (existing, 400 lines)
│   │   └── research.py            # Research stage (existing, 450 lines)
│   ├── planning/
│   │   ├── __init__.py
│   │   ├── architecture.py        # Architecture stage (400 lines)
│   │   ├── sprint_planning.py     # Sprint planning (existing, 400 lines)
│   │   └── ssd_generation.py      # SSD generation (existing, 400 lines)
│   ├── development/
│   │   ├── __init__.py
│   │   ├── development.py         # Development stage (400 lines)
│   │   ├── notebook_generation.py # Notebook generation (existing, 400 lines)
│   │   └── bdd_test_generation.py # BDD test gen (existing, 350 lines)
│   ├── validation/
│   │   ├── __init__.py
│   │   ├── validation.py          # Validation stage (400 lines)
│   │   ├── dependency_validation.py # Dependency validation (350 lines)
│   │   ├── bdd_validation.py      # BDD validation (existing, 350 lines)
│   │   └── bdd_scenario_generation.py # BDD scenarios (existing, 300 lines)
│   ├── testing/
│   │   ├── __init__.py
│   │   ├── testing.py             # Testing stage (350 lines)
│   │   └── integration.py         # Integration stage (350 lines)
│   ├── review/
│   │   ├── __init__.py
│   │   ├── code_review.py         # Code review (existing, 400 lines)
│   │   ├── project_review.py      # Project review (existing, 400 lines)
│   │   └── arbitration.py         # Arbitration (existing, 350 lines)
│   └── uiux/
│       ├── __init__.py
│       └── uiux.py                # UI/UX stage (existing, 400 lines)
│
├── managers/                      # Build and resource managers
│   ├── __init__.py
│   ├── build/
│   │   ├── __init__.py
│   │   ├── factory.py             # Build manager factory (existing, 300 lines)
│   │   ├── universal_build.py     # Universal build system (existing, 400 lines)
│   │   ├── maven.py               # Maven (existing, < 500 lines)
│   │   ├── npm.py                 # NPM (existing, < 500 lines)
│   │   ├── gradle.py              # Gradle (existing, < 500 lines)
│   │   ├── poetry.py              # Poetry (existing, < 500 lines)
│   │   ├── cargo.py               # Cargo (existing, < 500 lines)
│   │   ├── go_mod.py              # Go (existing, < 500 lines)
│   │   ├── dotnet.py              # .NET (existing, < 500 lines)
│   │   ├── cmake.py               # CMake (existing, < 500 lines)
│   │   ├── composer.py            # Composer (existing, < 500 lines)
│   │   ├── bundler.py             # Bundler (existing, < 500 lines)
│   │   └── lua.py                 # Lua (existing, < 500 lines)
│   ├── git/
│   │   ├── __init__.py
│   │   └── git_manager.py         # Git operations (existing, < 500 lines)
│   ├── bash/
│   │   ├── __init__.py
│   │   └── bash_manager.py        # Bash execution (existing, < 500 lines)
│   ├── terraform/
│   │   ├── __init__.py
│   │   └── terraform_manager.py   # Terraform (existing, < 500 lines)
│   ├── kanban/
│   │   ├── __init__.py
│   │   └── kanban_manager.py      # Kanban board (existing, < 500 lines)
│   ├── checkpoint/
│   │   ├── __init__.py
│   │   └── checkpoint_manager.py  # Checkpoints (existing, < 500 lines)
│   └── prompt/
│       ├── __init__.py
│       └── prompt_manager.py      # Prompts (existing, < 500 lines)
│
├── services/                      # Shared services
│   ├── __init__.py
│   ├── llm/
│   │   ├── __init__.py
│   │   ├── client.py              # LLM client (existing, 450 lines)
│   │   ├── cache.py               # LLM caching (existing, 300 lines)
│   │   └── cost_tracker.py        # Cost tracking (existing, 300 lines)
│   ├── ai_query/
│   │   ├── __init__.py
│   │   └── service.py             # AI Query Service (existing, 450 lines)
│   ├── storage/
│   │   ├── __init__.py
│   │   ├── rag_storage.py         # RAG storage (existing, 400 lines)
│   │   ├── redis_client.py        # Redis (existing, 300 lines)
│   │   ├── redis_rate_limiter.py  # Rate limiting (existing, 250 lines)
│   │   ├── redis_pipeline_tracker.py # Pipeline tracking (existing, 300 lines)
│   │   └── redis_metrics.py       # Metrics (existing, 300 lines)
│   ├── knowledge/
│   │   ├── __init__.py
│   │   ├── graph.py               # Knowledge graph (existing, 400 lines)
│   │   └── factory.py             # KG factory (existing, 250 lines)
│   ├── messaging/
│   │   ├── __init__.py
│   │   ├── interface.py           # Messenger interface (existing, 200 lines)
│   │   ├── factory.py             # Messenger factory (existing, 200 lines)
│   │   ├── agent_messenger.py     # Agent messenger (existing, 300 lines)
│   │   └── rabbitmq_messenger.py  # RabbitMQ (existing, 350 lines)
│   ├── adr/
│   │   ├── __init__.py
│   │   ├── generator.py           # ADR generation (existing, 350 lines)
│   │   ├── numbering.py           # ADR numbering (existing, 250 lines)
│   │   └── storage.py             # ADR storage (existing, 300 lines)
│   ├── debug/
│   │   ├── __init__.py
│   │   └── service.py             # Debug service (existing, 300 lines)
│   ├── path_config.py             # Path configuration (existing, 250 lines)
│   ├── test_runner.py             # Test runner (existing, 400 lines)
│   ├── file_manager.py            # File operations (existing, 300 lines)
│   ├── environment_context.py     # Environment (existing, 250 lines)
│   └── artemis_services.py        # Service aggregation (existing, 400 lines)
│
├── validators/                    # Validation components
│   ├── __init__.py
│   ├── streaming_validator.py     # Streaming validation (existing, 400 lines)
│   ├── artifact_quality.py        # Artifact quality (existing, 350 lines)
│   ├── code_standards.py          # Code standards (existing, 350 lines)
│   ├── config_validator.py        # Config validation (existing, 300 lines)
│   ├── requirements_driven.py     # Requirements validation (existing, 350 lines)
│   ├── self_critique.py           # Self-critique (existing, 300 lines)
│   ├── signature_validator.py     # Signature validation (existing, 300 lines)
│   ├── preflight_validator.py     # Preflight checks (existing, 300 lines)
│   └── validation_failure_analyzer.py # Failure analysis (existing, 300 lines)
│
├── workflows/                     # Workflow orchestration
│   ├── __init__.py
│   ├── handlers.py                # Workflow handlers (existing, 400 lines)
│   ├── planner.py                 # Workflow planner (existing, 350 lines)
│   └── models.py                  # Workflow models (existing, 300 lines)
│
├── models/                        # Data models
│   ├── __init__.py
│   ├── requirements.py            # Requirements models (existing, 300 lines)
│   ├── sprint.py                  # Sprint models (existing, 250 lines)
│   ├── code_examples.py           # Code example types (existing, 250 lines)
│   └── user_stories.py            # User story generator (existing, 300 lines)
│
├── utilities/                     # Utility functions
│   ├── __init__.py
│   ├── retry.py                   # Retry strategies (300 lines)
│   ├── file_utils.py              # File utilities (300 lines)
│   ├── string_utils.py            # String utilities (250 lines)
│   └── validation_utils.py        # Validation helpers (250 lines)
│
├── config/                        # Configuration (existing directory)
│   ├── __init__.py
│   ├── hydra_config.py            # Hydra config (existing, 300 lines)
│   └── ...
│
├── platform/                      # Platform detection
│   ├── __init__.py
│   └── detector.py                # Platform detector (existing, 400 lines)
│
├── security/                      # Security components
│   ├── __init__.py
│   ├── sandbox_executor.py        # Sandbox (existing, 400 lines)
│   └── coding_standards.py        # Standards (existing, 300 lines)
│
├── data/                          # Data management
│   ├── __init__.py
│   ├── code_examples_database.py  # Examples DB (existing, 400 lines)
│   ├── research_repository.py     # Research repo (existing, 350 lines)
│   └── sprint_config_accessor.py  # Sprint config (existing, 300 lines)
│
├── integrations/                  # External integrations
│   ├── __init__.py
│   ├── jupyter/
│   │   ├── __init__.py
│   │   └── notebook_handler.py    # Jupyter (existing, 400 lines)
│   ├── java/
│   │   ├── __init__.py
│   │   └── ecosystem_integration.py # Java (existing, 400 lines)
│   └── downloader/
│       ├── __init__.py
│       └── code_examples_downloader.py # Downloader (existing, 400 lines)
│
├── cli/                           # Command-line interface
│   ├── __init__.py
│   └── artemis_cli.py             # CLI (existing, 400 lines)
│
├── tests/                         # Unit tests
│   ├── __init__.py
│   ├── test_advanced_features.py  # Advanced features tests
│   ├── test_agents/               # Agent tests
│   ├── test_pipelines/            # Pipeline tests
│   ├── test_stages/               # Stage tests
│   ├── test_managers/             # Manager tests
│   ├── test_services/             # Service tests
│   └── ...
│
├── scripts/                       # Utility scripts
│   ├── __init__.py
│   ├── upload_*.py                # RAG upload scripts
│   ├── fix_imports.py             # Import fixer (existing)
│   ├── generate_skills.py         # Skills generator (existing)
│   └── initialize_artemis_prompts.py # Prompt init (existing)
│
└── conf/                          # Hydra configuration (existing directory)
    └── ...

```

---

## 2. Detailed Module Breakdown for Top 10 Files

### 2.1 supervisor_agent.py (3,403 lines) → agents/supervisor/

**Current Structure:**
- Classes: AgentHealthEvent, AgentHealthObserver, SupervisorHealthObserver, HealthStatus, RecoveryAction, ProcessHealth, StageHealth, RecoveryStrategy, SupervisorAgent

**New Module Structure:**

#### `agents/supervisor/supervisor_agent.py` (400 lines)
**Responsibility:** Main supervisor orchestration and coordination
```python
# Classes:
- SupervisorAgent (main orchestrator)
  * Coordinates health monitoring, recovery, and learning
  * Delegates to specialized engines
  * Manages supervisor lifecycle

# Key Methods:
- __init__()
- monitor_stage()
- handle_health_event()
- coordinate_recovery()
- cleanup_resources()

# Dependencies:
- health_monitor.py (HealthMonitor)
- recovery_engine.py (RecoveryEngine)
- circuit_breaker.py (CircuitBreakerManager)
- learning_engine.py (LearningEngine)
- health_observer.py (SupervisorHealthObserver)
```

#### `agents/supervisor/health_monitor.py` (350 lines)
**Responsibility:** Health monitoring and detection
```python
# Classes:
- HealthStatus (Enum)
- ProcessHealth (dataclass)
- StageHealth (dataclass)
- HealthMonitor

# Key Methods:
- check_process_health()
- detect_hangs()
- detect_stalls()
- detect_memory_leaks()
- calculate_health_score()

# Dependencies:
- psutil (process monitoring)
- health_observer.py (event emission)
```

#### `agents/supervisor/recovery_engine.py` (400 lines)
**Responsibility:** Recovery strategy execution
```python
# Classes:
- RecoveryAction (Enum)
- RecoveryStrategy (dataclass)
- RecoveryEngine

# Key Methods:
- attempt_recovery()
- apply_retry_strategy()
- apply_restart_strategy()
- apply_failover_strategy()
- apply_degraded_mode_strategy()
- escalate_to_manual()

# Dependencies:
- health_monitor.py (HealthStatus)
- artemis_utilities.py (RetryStrategy)
```

#### `agents/supervisor/health_observer.py` (250 lines)
**Responsibility:** Health event observation and notification
```python
# Classes:
- AgentHealthEvent (Enum)
- AgentHealthObserver (ABC)
- SupervisorHealthObserver

# Key Methods:
- on_health_event()
- notify_observers()
- register_observer()
- unregister_observer()

# Dependencies:
- pipeline_observer.py (PipelineObservable)
- messaging/agent_messenger.py (alerting)
```

#### `agents/supervisor/circuit_breaker.py` (existing, 250 lines)
**Responsibility:** Circuit breaker pattern implementation
- Already properly sized, just move to new location

#### `agents/supervisor/learning_engine.py` (existing supervisor_learning.py, 400 lines)
**Responsibility:** ML-based learning from failures
- Already properly sized, just move to new location

**Migration Notes:**
- Extract health monitoring logic from SupervisorAgent → HealthMonitor
- Extract recovery strategies from SupervisorAgent → RecoveryEngine
- Extract observer pattern from SupervisorAgent → HealthObserver
- Keep existing circuit_breaker.py and supervisor_learning.py
- Update imports across all files

---

### 2.2 thermodynamic_computing.py (2,797 lines) → pipelines/advanced/thermodynamic/

**Current Structure:**
- Classes: ConfidenceScore, ThermodynamicEventType, UncertaintyStrategy (ABC), BayesianUncertaintyStrategy, MonteCarloUncertaintyStrategy, EnsembleUncertaintyStrategy, TemperatureScheduler, ThermodynamicComputing

**New Module Structure:**

#### `pipelines/advanced/thermodynamic/computing.py` (400 lines)
**Responsibility:** Main facade for thermodynamic computing
```python
# Classes:
- ThermodynamicComputing

# Key Methods:
- estimate_confidence()
- quantify_uncertainty()
- assess_risk()
- propagate_uncertainty()
- get_strategy()

# Dependencies:
- strategies.py (UncertaintyStrategy)
- bayesian.py (BayesianUncertaintyStrategy)
- monte_carlo.py (MonteCarloUncertaintyStrategy)
- ensemble.py (EnsembleUncertaintyStrategy)
- temperature.py (TemperatureScheduler)
- confidence.py (ConfidenceScore)
```

#### `pipelines/advanced/thermodynamic/strategies.py` (450 lines)
**Responsibility:** Abstract strategy and common strategy logic
```python
# Classes:
- UncertaintyStrategy (ABC)
- StrategyFactory
- StrategyRegistry

# Key Methods:
- estimate() [abstract]
- update_priors() [abstract]
- create_strategy()
- register_strategy()

# Dependencies:
- confidence.py (ConfidenceScore)
```

#### `pipelines/advanced/thermodynamic/bayesian.py` (400 lines)
**Responsibility:** Bayesian uncertainty estimation
```python
# Classes:
- BayesianPrior (dataclass)
- BayesianPosterior (dataclass)
- BayesianUncertaintyStrategy

# Key Methods:
- estimate()
- update_priors()
- calculate_posterior()
- calculate_likelihood()

# Dependencies:
- strategies.py (UncertaintyStrategy)
- confidence.py (ConfidenceScore)
```

#### `pipelines/advanced/thermodynamic/monte_carlo.py` (350 lines)
**Responsibility:** Monte Carlo simulation
```python
# Classes:
- MonteCarloSimulation (dataclass)
- SimulationResult (dataclass)
- MonteCarloUncertaintyStrategy

# Key Methods:
- estimate()
- run_simulation()
- calculate_statistics()
- sample_distributions()

# Dependencies:
- strategies.py (UncertaintyStrategy)
- confidence.py (ConfidenceScore)
```

#### `pipelines/advanced/thermodynamic/ensemble.py` (350 lines)
**Responsibility:** Ensemble methods and voting
```python
# Classes:
- EnsembleMethod (Enum)
- EnsembleResult (dataclass)
- EnsembleUncertaintyStrategy

# Key Methods:
- estimate()
- majority_vote()
- weighted_average()
- combine_predictions()

# Dependencies:
- strategies.py (UncertaintyStrategy)
- confidence.py (ConfidenceScore)
```

#### `pipelines/advanced/thermodynamic/temperature.py` (300 lines)
**Responsibility:** Temperature scheduling and annealing
```python
# Classes:
- AnnealingSchedule (Enum)
- TemperatureScheduler

# Key Methods:
- get_temperature()
- update_schedule()
- apply_annealing()
- exponential_decay()
- linear_decay()

# Dependencies:
- None (standalone)
```

#### `pipelines/advanced/thermodynamic/confidence.py` (300 lines)
**Responsibility:** Confidence scoring and tracking
```python
# Classes:
- ConfidenceScore (dataclass)
- ConfidenceHistory
- ConfidenceTracker

# Key Methods:
- calculate_confidence()
- track_confidence()
- get_confidence_history()
- aggregate_confidence()

# Dependencies:
- None (data model)
```

**Migration Notes:**
- Create separate modules for each strategy
- Extract temperature scheduling to separate module
- Extract confidence scoring to separate module
- Maintain strategy pattern with factory
- Update imports across all files

---

### 2.3 standalone_developer_agent.py (2,792 lines) → agents/developer/

**Current Structure:**
- Classes: StandaloneDeveloperAgent

**New Module Structure:**

#### `agents/developer/standalone_agent.py` (400 lines)
**Responsibility:** Main developer agent orchestration
```python
# Classes:
- StandaloneDeveloperAgent

# Key Methods:
- __init__()
- execute_task()
- coordinate_workflow()
- handle_response()

# Dependencies:
- tdd_workflow.py (TDDWorkflow)
- code_generation.py (CodeGenerator)
- streaming_validator.py (StreamingValidator)
- retry_coordinator.py (RetryCoordinator)
```

#### `agents/developer/tdd_workflow.py` (350 lines)
**Responsibility:** TDD workflow implementation
```python
# Classes:
- TDDWorkflowPhase (Enum)
- TDDWorkflow

# Key Methods:
- execute_red_phase()
- execute_green_phase()
- execute_refactor_phase()
- validate_tests()

# Dependencies:
- code_generation.py (CodeGenerator)
- services/test_runner.py (TestRunner)
```

#### `agents/developer/code_generation.py` (400 lines)
**Responsibility:** Code generation strategies
```python
# Classes:
- GenerationStrategy (Enum)
- CodeGenerationContext
- CodeGenerator

# Key Methods:
- generate_code()
- apply_conservative_strategy()
- apply_aggressive_strategy()
- validate_generated_code()

# Dependencies:
- services/llm/client.py (LLMClient)
- validators/streaming_validator.py
```

#### `agents/developer/streaming_validator.py` (350 lines)
**Responsibility:** Real-time validation during generation
```python
# Classes:
- StreamingValidatorFactory
- StreamingValidationResult
- StreamingValidator

# Key Methods:
- validate_stream()
- check_syntax()
- check_semantics()
- emit_validation_event()

# Dependencies:
- validators/code_standards.py
```

#### `agents/developer/retry_coordinator.py` (300 lines)
**Responsibility:** Retry logic with prompt refinement
```python
# Classes:
- RetryStrategy (Enum)
- RetryCoordinator

# Key Methods:
- coordinate_retry()
- refine_prompt()
- apply_backoff()
- check_retry_budget()

# Dependencies:
- utilities/retry.py
- services/prompt_manager.py
```

#### `agents/developer/developer_invoker.py` (existing, 200 lines)
**Responsibility:** Developer invocation
- Already properly sized, just move to new location

**Migration Notes:**
- Extract TDD workflow logic → tdd_workflow.py
- Extract code generation → code_generation.py
- Extract validation → streaming_validator.py
- Extract retry logic → retry_coordinator.py
- Keep main agent focused on orchestration

---

### 2.4 artemis_stages.py (2,690 lines) → stages/

**Current Structure:**
- Classes: ProjectAnalysisStage, ArchitectureStage, DependencyValidationStage, DevelopmentStage, ValidationStage, IntegrationStage, TestingStage

**New Module Structure:**

#### `stages/analysis/project_analysis.py` (400 lines)
**Responsibility:** Project analysis stage
```python
# Classes:
- ProjectAnalysisStage

# Key Methods:
- execute()
- analyze_requirements()
- analyze_architecture()
- analyze_security()
- get_user_approval()

# Dependencies:
- agents/analysis/project_analysis_agent.py
- stages/base/stage_interface.py
```

#### `stages/planning/architecture.py` (400 lines)
**Responsibility:** Architecture design stage
```python
# Classes:
- ArchitectureStage

# Key Methods:
- execute()
- generate_architecture()
- generate_adr()
- generate_user_stories()
- validate_architecture()

# Dependencies:
- services/adr/generator.py
- models/user_stories.py
```

#### `stages/validation/dependency_validation.py` (350 lines)
**Responsibility:** Dependency validation stage
```python
# Classes:
- DependencyValidationStage

# Key Methods:
- execute()
- validate_dependencies()
- check_versions()
- resolve_conflicts()

# Dependencies:
- managers/build/factory.py
```

#### `stages/development/development.py` (400 lines)
**Responsibility:** Development stage
```python
# Classes:
- DevelopmentStage

# Key Methods:
- execute()
- invoke_developers()
- manage_tdd_cycle()
- coordinate_developer_responses()

# Dependencies:
- agents/developer/developer_invoker.py
```

#### `stages/validation/validation.py` (400 lines)
**Responsibility:** Validation stage
```python
# Classes:
- ValidationStage

# Key Methods:
- execute()
- run_validations()
- check_code_quality()
- check_test_coverage()

# Dependencies:
- validators/*
```

#### `stages/testing/integration.py` (350 lines)
**Responsibility:** Integration testing stage
```python
# Classes:
- IntegrationStage

# Key Methods:
- execute()
- run_integration_tests()
- validate_integrations()

# Dependencies:
- services/test_runner.py
```

#### `stages/testing/testing.py` (350 lines)
**Responsibility:** Testing stage
```python
# Classes:
- TestingStage

# Key Methods:
- execute()
- run_unit_tests()
- run_integration_tests()
- generate_reports()

# Dependencies:
- services/test_runner.py
```

**Migration Notes:**
- Split each stage class into separate module
- Group by logical category (analysis, planning, development, validation, testing)
- Create base stage interface in stages/base/
- Update imports in orchestrator

---

### 2.5 artemis_orchestrator.py (2,349 lines) → pipelines/standard/

**Current Structure:**
- Classes: WorkflowPlanner, ArtemisOrchestrator

**New Module Structure:**

#### `pipelines/standard/orchestrator.py` (400 lines)
**Responsibility:** Main orchestration logic
```python
# Classes:
- ArtemisOrchestrator

# Key Methods:
- __init__()
- run()
- execute_stage()
- handle_stage_failure()
- cleanup()

# Dependencies:
- workflow_planner.py (WorkflowPlanner)
- stages/* (all stages)
- pipelines/observer.py
```

#### `pipelines/standard/workflow_planner.py` (300 lines)
**Responsibility:** Workflow planning
```python
# Classes:
- WorkflowPlanner

# Key Methods:
- plan_workflow()
- select_stages()
- optimize_execution_order()
- estimate_effort()

# Dependencies:
- pipelines/routing/router.py
```

#### `pipelines/standard/strategies.py` (existing pipeline_strategies.py, 300 lines)
**Responsibility:** Pipeline execution strategies
- Already properly sized, just move to new location

#### `pipelines/standard/status_tracker.py` (existing workflow_status_tracker.py, 300 lines)
**Responsibility:** Workflow status tracking
- Already properly sized, just move to new location

**Migration Notes:**
- Extract WorkflowPlanner to separate module
- Keep orchestrator focused on stage execution
- Move pipeline strategies to standard/ directory
- Update Hydra configuration paths

---

### 2.6 two_pass_pipeline.py (2,183 lines) → pipelines/advanced/two_pass/

**Current Structure:**
- Classes: TwoPassEventType, TwoPassPipelineException, FirstPassException, SecondPassException, PassComparisonException, RollbackException, MementoException, PassResult, PassDelta, PassMemento, PassStrategy, FirstPassStrategy, SecondPassStrategy, PassComparator, RollbackManager, TwoPassPipeline, TwoPassPipelineFactory

**New Module Structure:**

#### `pipelines/advanced/two_pass/pipeline.py` (400 lines)
**Responsibility:** Main two-pass pipeline orchestration
```python
# Classes:
- TwoPassPipeline

# Key Methods:
- execute()
- execute_first_pass()
- execute_second_pass()
- compare_passes()
- handle_rollback()

# Dependencies:
- strategies.py (FirstPassStrategy, SecondPassStrategy)
- memento.py (PassMemento)
- comparator.py (PassComparator)
- rollback.py (RollbackManager)
```

#### `pipelines/advanced/two_pass/strategies.py` (400 lines)
**Responsibility:** Pass strategies
```python
# Classes:
- PassStrategy (ABC)
- FirstPassStrategy
- SecondPassStrategy

# Key Methods:
- execute() [abstract]
- create_memento()
- apply_memento()

# Dependencies:
- memento.py (PassMemento, PassResult)
```

#### `pipelines/advanced/two_pass/memento.py` (350 lines)
**Responsibility:** State capture and restoration
```python
# Classes:
- PassResult (dataclass)
- PassDelta (dataclass)
- PassMemento

# Key Methods:
- capture_state()
- restore_state()
- calculate_delta()
- serialize()
- deserialize()

# Dependencies:
- None (data model)
```

#### `pipelines/advanced/two_pass/comparator.py` (300 lines)
**Responsibility:** Pass comparison
```python
# Classes:
- ComparisonMetric (Enum)
- PassComparator

# Key Methods:
- compare_passes()
- calculate_quality_score()
- detect_regression()
- calculate_improvement()

# Dependencies:
- memento.py (PassResult, PassDelta)
```

#### `pipelines/advanced/two_pass/rollback.py` (300 lines)
**Responsibility:** Rollback management
```python
# Classes:
- RollbackStrategy (Enum)
- RollbackManager

# Key Methods:
- should_rollback()
- execute_rollback()
- preserve_improvements()
- log_rollback()

# Dependencies:
- memento.py (PassMemento)
- comparator.py (PassComparator)
```

#### `pipelines/advanced/two_pass/factory.py` (200 lines)
**Responsibility:** Pipeline factory
```python
# Classes:
- TwoPassPipelineFactory

# Key Methods:
- create_pipeline()
- create_strategies()
- create_comparator()
- create_rollback_manager()

# Dependencies:
- All two_pass modules
```

#### `pipelines/advanced/two_pass/__init__.py` (100 lines)
**Responsibility:** Package initialization and exception definitions
```python
# Classes:
- TwoPassEventType (Enum)
- TwoPassPipelineException
- FirstPassException
- SecondPassException
- PassComparisonException
- RollbackException
- MementoException

# Re-exports from submodules
```

**Migration Notes:**
- Split strategies into separate module
- Extract memento pattern to separate module
- Extract comparison logic to separate module
- Extract rollback logic to separate module
- Move exceptions to __init__.py

---

### 2.7 dynamic_pipeline.py (2,081 lines) → pipelines/advanced/dynamic/

**Current Structure:**
- Classes: PipelineState, ProjectComplexity, StageResult, PipelineStage, StageSelectionStrategy, ComplexityBasedSelector, ResourceBasedSelector, ManualSelector, RetryPolicy, StageExecutor, ParallelStageExecutor, DynamicPipelineBuilder, DynamicPipeline, DynamicPipelineFactory

**New Module Structure:**

#### `pipelines/advanced/dynamic/pipeline.py` (450 lines)
**Responsibility:** Main dynamic pipeline
```python
# Classes:
- PipelineState (Enum)
- DynamicPipeline

# Key Methods:
- execute()
- add_stage()
- remove_stage()
- modify_stage()
- get_state()

# Dependencies:
- builder.py (DynamicPipelineBuilder)
- selectors.py (StageSelectionStrategy)
- executors.py (StageExecutor)
```

#### `pipelines/advanced/dynamic/builder.py` (350 lines)
**Responsibility:** Pipeline builder
```python
# Classes:
- DynamicPipelineBuilder

# Key Methods:
- with_stage()
- with_selector()
- with_executor()
- with_retry_policy()
- build()

# Dependencies:
- pipeline.py (DynamicPipeline)
- selectors.py
- executors.py
```

#### `pipelines/advanced/dynamic/selectors.py` (400 lines)
**Responsibility:** Stage selection strategies
```python
# Classes:
- ProjectComplexity (Enum)
- StageSelectionStrategy (ABC)
- ComplexityBasedSelector
- ResourceBasedSelector
- ManualSelector

# Key Methods:
- select_stages() [abstract]
- analyze_complexity()
- estimate_resources()

# Dependencies:
- None (standalone strategies)
```

#### `pipelines/advanced/dynamic/executors.py` (350 lines)
**Responsibility:** Stage execution
```python
# Classes:
- StageResult (dataclass)
- RetryPolicy (dataclass)
- StageExecutor
- ParallelStageExecutor

# Key Methods:
- execute_stage()
- execute_parallel()
- apply_retry()
- handle_failure()

# Dependencies:
- stages/base/stage_interface.py
```

#### `pipelines/advanced/dynamic/factory.py` (250 lines)
**Responsibility:** Pipeline factory
```python
# Classes:
- DynamicPipelineFactory

# Key Methods:
- create_simple_pipeline()
- create_moderate_pipeline()
- create_complex_pipeline()
- create_custom_pipeline()

# Dependencies:
- All dynamic modules
```

**Migration Notes:**
- Split builder into separate module
- Split selectors into separate module
- Split executors into separate module
- Create factory for common configurations
- Update imports

---

### 2.8 test_advanced_features.py (1,972 lines) → tests/

**Current Structure:**
- Comprehensive tests for Dynamic Pipelines, Two-Pass Pipelines, Thermodynamic Computing

**New Module Structure:**

#### `tests/test_pipelines/test_dynamic_pipeline.py` (500 lines)
**Responsibility:** Dynamic pipeline tests
```python
# Test Classes:
- TestDynamicPipeline
- TestDynamicPipelineBuilder
- TestStageSelectors
- TestStageExecutors

# Test Coverage:
- Stage selection strategies
- Parallel execution
- Retry logic
- Runtime modification
```

#### `tests/test_pipelines/test_two_pass_pipeline.py` (500 lines)
**Responsibility:** Two-pass pipeline tests
```python
# Test Classes:
- TestTwoPassPipeline
- TestPassStrategies
- TestPassMemento
- TestPassComparator
- TestRollbackManager

# Test Coverage:
- First/second pass execution
- Learning transfer
- Delta detection
- Rollback functionality
```

#### `tests/test_pipelines/test_thermodynamic_computing.py` (500 lines)
**Responsibility:** Thermodynamic computing tests
```python
# Test Classes:
- TestThermodynamicComputing
- TestBayesianStrategy
- TestMonteCarloStrategy
- TestEnsembleStrategy
- TestTemperatureScheduler

# Test Coverage:
- Uncertainty quantification
- Bayesian learning
- Monte Carlo simulation
- Temperature scheduling
```

#### `tests/test_pipelines/test_advanced_integration.py` (400 lines)
**Responsibility:** Integration tests
```python
# Test Classes:
- TestAdvancedPipelineIntegration
- TestEndToEnd

# Test Coverage:
- Feature integration
- Mode selection
- Performance metrics
```

**Migration Notes:**
- Split by feature area
- Maintain test coverage
- Update test imports
- Add integration tests

---

### 2.9 intelligent_router_enhanced.py (1,799 lines) → pipelines/routing/

**Current Structure:**
- Classes: RiskFactor, UncertaintyAnalysis, AdvancedFeatureRecommendation, EnhancedRoutingDecision, IntelligentRouterEnhanced

**New Module Structure:**

#### `pipelines/routing/enhanced_router.py` (450 lines)
**Responsibility:** Enhanced routing logic
```python
# Classes:
- IntelligentRouterEnhanced

# Key Methods:
- recommend_pipeline_mode()
- calculate_task_uncertainty()
- should_use_two_pass()
- create_advanced_pipeline_context()

# Dependencies:
- router.py (IntelligentRouter)
- routing_decisions.py
- risk_analysis.py
```

#### `pipelines/routing/router.py` (400 lines)
**Responsibility:** Base intelligent router
```python
# Classes:
- IntelligentRouter
- RoutingStrategy

# Key Methods:
- analyze_task_requirements()
- make_routing_decision()
- select_stages()

# Dependencies:
- routing_decisions.py
```

#### `pipelines/routing/routing_decisions.py` (300 lines)
**Responsibility:** Routing decision models
```python
# Classes:
- TaskRequirements (dataclass)
- RoutingDecision (dataclass)
- StageDecision (dataclass)
- EnhancedRoutingDecision
- AdvancedFeatureRecommendation

# Dependencies:
- None (data models)
```

#### `pipelines/routing/risk_analysis.py` (350 lines)
**Responsibility:** Risk factor analysis
```python
# Classes:
- RiskFactor (dataclass)
- UncertaintyAnalysis (dataclass)
- RiskAnalyzer

# Key Methods:
- identify_risk_factors()
- calculate_uncertainty()
- assess_risk_severity()
- recommend_mitigation()

# Dependencies:
- routing_decisions.py
```

**Migration Notes:**
- Extract base router to separate module
- Extract risk analysis to separate module
- Extract data models to separate module
- Maintain inheritance hierarchy

---

### 2.10 advanced_pipeline_integration.py (1,764 lines) → pipelines/advanced/

**Current Structure:**
- Classes: PipelineMode, AdvancedPipelineConfig, ConfigurationManager, ModeSelectionStrategy, ManualModeSelector, AutomaticModeSelector, ModeSelector, AdvancedPipelineStrategy, AdvancedPipelineIntegration

**New Module Structure:**

#### `pipelines/advanced/integration.py` (500 lines)
**Responsibility:** Main integration facade
```python
# Classes:
- AdvancedPipelineIntegration

# Key Methods:
- execute_with_mode()
- select_optimal_mode()
- coordinate_features()
- track_performance()

# Dependencies:
- dynamic/pipeline.py
- two_pass/pipeline.py
- thermodynamic/computing.py
- configuration.py
```

#### `pipelines/advanced/configuration.py` (350 lines)
**Responsibility:** Configuration management
```python
# Classes:
- PipelineMode (Enum)
- AdvancedPipelineConfig (dataclass)
- ConfigurationManager

# Key Methods:
- load_config()
- validate_config()
- enable_feature()
- disable_feature()

# Dependencies:
- None (configuration only)
```

#### `pipelines/advanced/mode_selection.py` (400 lines)
**Responsibility:** Mode selection strategies
```python
# Classes:
- ModeSelectionStrategy (ABC)
- ManualModeSelector
- AutomaticModeSelector
- ModeSelector

# Key Methods:
- select_mode() [abstract]
- analyze_task()
- recommend_mode()

# Dependencies:
- configuration.py (PipelineMode)
```

#### `pipelines/advanced/strategy.py` (400 lines)
**Responsibility:** Advanced pipeline strategy
```python
# Classes:
- AdvancedPipelineStrategy

# Key Methods:
- execute()
- select_features()
- coordinate_execution()
- monitor_performance()

# Dependencies:
- integration.py
- mode_selection.py
```

**Migration Notes:**
- Split configuration management
- Split mode selection strategies
- Keep integration as main facade
- Update orchestrator integration

---

## 3. Migration Strategy

### Phase 1: Foundation (Weeks 1-2)
**Goal:** Establish new directory structure and core interfaces

**Tasks:**
1. Create new directory structure
2. Move core interfaces:
   - `artemis_stage_interface.py` → `core/interfaces.py`
   - `artemis_exceptions.py` → `core/exceptions.py`
   - `artemis_constants.py` → `core/constants.py`
   - `artemis_state_machine.py` → `core/state_machine.py`
3. Create `__init__.py` files with proper re-exports
4. Update imports in test files
5. Run full test suite to verify no breakage

**Success Criteria:**
- All tests pass
- Core modules moved
- Imports working

**Risk Mitigation:**
- Keep original files until Phase 4
- Use symbolic links during transition
- Test after each module move

---

### Phase 2: Services and Utilities (Weeks 3-4)
**Goal:** Move stable, low-dependency modules

**Tasks:**
1. Move services:
   - LLM client, cache, cost tracker → `services/llm/`
   - Redis modules → `services/storage/`
   - Messaging modules → `services/messaging/`
   - Knowledge graph → `services/knowledge/`
   - ADR services → `services/adr/`
2. Move managers:
   - Build managers → `managers/build/`
   - Git, Bash, Terraform → `managers/*/`
   - Kanban, Checkpoint, Prompt → `managers/*/`
3. Move validators:
   - All validator files → `validators/`
4. Move utilities:
   - Extract from `artemis_utilities.py` → `utilities/*`
5. Update imports
6. Run tests

**Success Criteria:**
- All services/managers/validators moved
- No circular dependencies
- All tests pass

**Risk Mitigation:**
- Move in small batches
- Test after each batch
- Use dependency graph to order moves

---

### Phase 3: Agents and Stages (Weeks 5-6)
**Goal:** Refactor large agent and stage files

**Tasks:**
1. Refactor `supervisor_agent.py`:
   - Split into 6 modules (see section 2.1)
   - Update imports
   - Test supervisor functionality
2. Refactor `standalone_developer_agent.py`:
   - Split into 6 modules (see section 2.3)
   - Update imports
   - Test developer functionality
3. Refactor `artemis_stages.py`:
   - Split into 7 stage modules (see section 2.4)
   - Update imports
   - Test each stage
4. Move other agent files:
   - Group into `agents/analysis/`, `agents/review/`, etc.
5. Move other stage files:
   - Group into `stages/*/`

**Success Criteria:**
- All agents refactored and moved
- All stages refactored and moved
- Full test suite passes
- No file over 500 lines

**Risk Mitigation:**
- Refactor one agent at a time
- Test after each refactoring
- Keep backward compatibility wrappers

---

### Phase 4: Pipelines (Weeks 7-8)
**Goal:** Refactor pipeline implementations

**Tasks:**
1. Refactor `thermodynamic_computing.py`:
   - Split into 7 modules (see section 2.2)
   - Update imports
   - Test thermodynamic features
2. Refactor `dynamic_pipeline.py`:
   - Split into 5 modules (see section 2.7)
   - Update imports
   - Test dynamic features
3. Refactor `two_pass_pipeline.py`:
   - Split into 6 modules (see section 2.6)
   - Update imports
   - Test two-pass features
4. Refactor `intelligent_router_enhanced.py`:
   - Split into 4 modules (see section 2.9)
   - Update imports
   - Test routing
5. Refactor `advanced_pipeline_integration.py`:
   - Split into 4 modules (see section 2.10)
   - Update imports
   - Test integration
6. Refactor `artemis_orchestrator.py`:
   - Split into 4 modules (see section 2.5)
   - Update imports
   - Test orchestration

**Success Criteria:**
- All pipelines refactored
- All advanced features working
- Full test suite passes
- No circular dependencies

**Risk Mitigation:**
- Test each feature independently
- Use feature flags for rollback
- Maintain backward compatibility

---

### Phase 5: Cleanup and Documentation (Week 9)
**Goal:** Remove duplicates and update documentation

**Tasks:**
1. Remove original large files
2. Remove symbolic links
3. Update all documentation
4. Update README with new structure
5. Create migration guide
6. Update Hydra configuration paths
7. Run final test suite
8. Performance benchmarking

**Success Criteria:**
- No duplicate files
- All documentation updated
- All tests pass
- No performance regression

---

## 4. Backward Compatibility Strategy

### 4.1 Import Compatibility Wrappers

Create compatibility wrappers in original locations:

```python
# src/supervisor_agent.py
"""
DEPRECATED: This module has been refactored.
Please use: from agents.supervisor import SupervisorAgent

This compatibility wrapper will be removed in v2.0
"""
import warnings
from agents.supervisor import (
    SupervisorAgent,
    HealthMonitor,
    RecoveryEngine,
    CircuitBreakerManager,
    LearningEngine,
    # ... all exports
)

warnings.warn(
    "supervisor_agent.py is deprecated. Use agents.supervisor instead.",
    DeprecationWarning,
    stacklevel=2
)

__all__ = ['SupervisorAgent', 'HealthMonitor', ...]
```

### 4.2 Gradual Deprecation Timeline

- **Phase 1-4:** Both old and new imports work
- **Phase 5-6:** Deprecation warnings added
- **v1.1:** Warnings become errors in tests
- **v2.0:** Old imports removed completely

---

## 5. Validation Checklist

### 5.1 Per-Module Validation

For each refactored module:

- [ ] Module size < 500 lines
- [ ] Single Responsibility Principle followed
- [ ] No circular dependencies
- [ ] All imports working
- [ ] Docstrings complete
- [ ] Type hints present
- [ ] Unit tests passing
- [ ] Integration tests passing
- [ ] No pylint errors
- [ ] No mypy errors

### 5.2 Per-Phase Validation

At end of each phase:

- [ ] All tests pass (pytest)
- [ ] No import errors
- [ ] No circular dependencies (use `pydeps`)
- [ ] Code coverage maintained (>80%)
- [ ] Performance benchmarks unchanged (±5%)
- [ ] No memory leaks (run with memray)
- [ ] Documentation updated
- [ ] CHANGELOG.md updated

### 5.3 Integration Testing

After Phase 4 completion:

- [ ] Full orchestrator workflow runs
- [ ] All stages execute correctly
- [ ] Dynamic pipeline works
- [ ] Two-pass pipeline works
- [ ] Thermodynamic computing works
- [ ] Intelligent routing works
- [ ] Supervisor monitoring works
- [ ] Developer agents work
- [ ] All advanced features work together
- [ ] End-to-end tests pass

### 5.4 Dependency Validation

Tools to use:

```bash
# Check for circular dependencies
pydeps src --show-cycles

# Check import structure
pipdeptree

# Validate all imports resolve
python -m py_compile src/**/*.py

# Check type hints
mypy src/

# Check code quality
pylint src/

# Check test coverage
pytest --cov=src --cov-report=html
```

---

## 6. Risk Assessment and Mitigation

### 6.1 High-Risk Areas

#### Risk: Circular Dependencies
**Likelihood:** High
**Impact:** High
**Mitigation:**
- Use dependency injection
- Follow strict layering (core → services → agents → pipelines)
- Use interfaces to break cycles
- Run `pydeps` after each refactoring
- Create dependency graph before refactoring

#### Risk: Breaking Existing Functionality
**Likelihood:** Medium
**Impact:** Critical
**Mitigation:**
- Maintain compatibility wrappers
- Run tests after each change
- Use feature flags for new structure
- Gradual rollout (opt-in during Phase 1-3)
- Comprehensive integration testing

#### Risk: Import Path Changes
**Likelihood:** High
**Impact:** Medium
**Mitigation:**
- Update Hydra configuration
- Create automated import rewriter
- Use compatibility wrappers
- Update documentation immediately
- Grep for all import statements

### 6.2 Medium-Risk Areas

#### Risk: Test Breakage
**Likelihood:** Medium
**Impact:** Medium
**Mitigation:**
- Update tests alongside code
- Maintain test coverage metrics
- Run tests continuously during refactoring

#### Risk: Performance Degradation
**Likelihood:** Low
**Impact:** Medium
**Mitigation:**
- Benchmark before refactoring
- Benchmark after each phase
- Profile import times
- Optimize hot paths

---

## 7. Tooling and Automation

### 7.1 Automated Import Rewriter

Create script: `scripts/rewrite_imports.py`

```python
"""
Automatically rewrite old imports to new structure
"""
import re
import sys
from pathlib import Path

IMPORT_MAPPINGS = {
    'from supervisor_agent import': 'from agents.supervisor import',
    'from standalone_developer_agent import': 'from agents.developer import',
    'from artemis_stages import': 'from stages import',
    # ... all mappings
}

def rewrite_file(filepath: Path):
    content = filepath.read_text()
    for old, new in IMPORT_MAPPINGS.items():
        content = re.sub(old, new, content)
    filepath.write_text(content)

# Usage: python scripts/rewrite_imports.py src/**/*.py
```

### 7.2 Dependency Analyzer

Create script: `scripts/analyze_dependencies.py`

```python
"""
Analyze and visualize module dependencies
"""
import ast
from pathlib import Path
import networkx as nx
import matplotlib.pyplot as plt

def analyze_imports(filepath: Path):
    tree = ast.parse(filepath.read_text())
    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.append(node.module)
    return imports

def build_dependency_graph(src_dir: Path):
    graph = nx.DiGraph()
    for filepath in src_dir.rglob('*.py'):
        module = str(filepath.relative_to(src_dir).with_suffix(''))
        imports = analyze_imports(filepath)
        for imp in imports:
            if imp.startswith('src.'):
                graph.add_edge(module, imp)
    return graph

def find_cycles(graph):
    try:
        cycles = list(nx.find_cycle(graph))
        return cycles
    except nx.NetworkXNoCycle:
        return []

# Usage: python scripts/analyze_dependencies.py
```

### 7.3 Module Size Checker

Create script: `scripts/check_module_sizes.py`

```python
"""
Verify all modules are under size limit
"""
from pathlib import Path

MAX_LINES = 500

def check_file_size(filepath: Path, max_lines: int = MAX_LINES):
    lines = len(filepath.read_text().split('\n'))
    return lines, lines <= max_lines

def check_all_files(src_dir: Path):
    violations = []
    for filepath in src_dir.rglob('*.py'):
        if filepath.name.startswith('test_'):
            continue  # Skip test files
        lines, ok = check_file_size(filepath)
        if not ok:
            violations.append((filepath, lines))

    if violations:
        print("Files exceeding size limit:")
        for filepath, lines in sorted(violations, key=lambda x: x[1], reverse=True):
            print(f"  {filepath}: {lines} lines")
        return False
    return True

# Usage: python scripts/check_module_sizes.py
```

---

## 8. Documentation Updates Required

### 8.1 Update List

- [ ] README.md - New directory structure
- [ ] CONTRIBUTING.md - Import guidelines
- [ ] API_REFERENCE.md - New module paths
- [ ] ARCHITECTURE.md - New architecture diagram
- [ ] MIGRATION_GUIDE.md - For external users
- [ ] All docstrings - Update references
- [ ] Hydra configs - Update Python paths
- [ ] Type stubs - Update paths

### 8.2 New Documentation to Create

- [ ] `docs/MODULARIZATION.md` - This document
- [ ] `docs/DEPENDENCY_GRAPH.md` - Visual dependency graph
- [ ] `docs/MODULE_GUIDE.md` - What's in each module
- [ ] `docs/IMPORT_GUIDE.md` - Import best practices

---

## 9. Success Metrics

### 9.1 Quantitative Metrics

- **Module Count:** 181 files → ~120 files (consolidate utilities)
- **Average Module Size:** Current ~630 lines → Target ~350 lines
- **Max Module Size:** Current 3,403 lines → Target <500 lines
- **Circular Dependencies:** Current unknown → Target 0
- **Test Coverage:** Current unknown → Target >80%
- **Import Depth:** Target <5 levels

### 9.2 Qualitative Metrics

- Code is easier to navigate
- New developers onboard faster
- Bugs are easier to locate
- Changes are more localized
- Tests are faster to run
- Documentation is clearer

---

## 10. Post-Migration Checklist

### 10.1 Code Quality

- [ ] No files over 500 lines
- [ ] No circular dependencies
- [ ] All imports resolve
- [ ] No pylint errors
- [ ] No mypy errors
- [ ] Code coverage >80%
- [ ] All docstrings complete

### 10.2 Functionality

- [ ] All unit tests pass
- [ ] All integration tests pass
- [ ] End-to-end tests pass
- [ ] Performance benchmarks pass
- [ ] All features working
- [ ] No regressions

### 10.3 Documentation

- [ ] All docs updated
- [ ] Migration guide created
- [ ] Import guide created
- [ ] Architecture diagrams updated
- [ ] CHANGELOG updated

### 10.4 Cleanup

- [ ] Original files removed
- [ ] Compatibility wrappers documented
- [ ] Deprecation warnings added
- [ ] No duplicate code
- [ ] No unused imports

---

## 11. Example Refactoring: SupervisorAgent

### Before (supervisor_agent.py - 3,403 lines)

```python
# supervisor_agent.py
class AgentHealthEvent(Enum): ...
class AgentHealthObserver(ABC): ...
class SupervisorHealthObserver(AgentHealthObserver): ...
class HealthStatus(Enum): ...
class RecoveryAction(Enum): ...
class ProcessHealth: ...
class StageHealth: ...
class RecoveryStrategy: ...
class SupervisorAgent(DebugMixin):
    def __init__(...): ...
    def monitor_stage(...): ...
    def _check_process_health(...): ...  # 200 lines
    def _detect_hangs(...): ...  # 150 lines
    def _attempt_recovery(...): ...  # 300 lines
    def _apply_retry_strategy(...): ...  # 100 lines
    def _apply_restart_strategy(...): ...  # 100 lines
    def _cleanup_resources(...): ...  # 150 lines
    # ... 30+ more methods
```

### After (agents/supervisor/ - 6 files, ~2,200 lines total)

```python
# agents/supervisor/__init__.py
from .supervisor_agent import SupervisorAgent
from .health_monitor import HealthMonitor, HealthStatus, ProcessHealth
from .recovery_engine import RecoveryEngine, RecoveryAction, RecoveryStrategy
from .health_observer import AgentHealthObserver, SupervisorHealthObserver
from .circuit_breaker import CircuitBreakerManager
from .learning_engine import LearningEngine

__all__ = [
    'SupervisorAgent',
    'HealthMonitor',
    'RecoveryEngine',
    'AgentHealthObserver',
    'CircuitBreakerManager',
    'LearningEngine',
]

# agents/supervisor/supervisor_agent.py (400 lines)
from .health_monitor import HealthMonitor
from .recovery_engine import RecoveryEngine
from .health_observer import SupervisorHealthObserver

class SupervisorAgent(DebugMixin):
    """Main supervisor - orchestrates monitoring and recovery"""

    def __init__(self, ...):
        self.health_monitor = HealthMonitor(...)
        self.recovery_engine = RecoveryEngine(...)
        self.observer = SupervisorHealthObserver(...)

    def monitor_stage(self, stage):
        """Delegate to health monitor"""
        return self.health_monitor.check_stage_health(stage)

    def handle_health_event(self, event):
        """Coordinate recovery via recovery engine"""
        return self.recovery_engine.attempt_recovery(event)

# agents/supervisor/health_monitor.py (350 lines)
class HealthStatus(Enum): ...
class ProcessHealth: ...
class StageHealth: ...

class HealthMonitor:
    """Single Responsibility: Monitor health, detect issues"""

    def check_stage_health(self, stage): ...
    def check_process_health(self, pid): ...
    def detect_hangs(self, stage): ...
    def detect_stalls(self, stage): ...

# agents/supervisor/recovery_engine.py (400 lines)
class RecoveryAction(Enum): ...
class RecoveryStrategy: ...

class RecoveryEngine:
    """Single Responsibility: Execute recovery strategies"""

    def attempt_recovery(self, health_event): ...
    def apply_retry_strategy(self, stage): ...
    def apply_restart_strategy(self, stage): ...
    def apply_failover_strategy(self, stage): ...

# agents/supervisor/health_observer.py (250 lines)
class AgentHealthObserver(ABC): ...
class SupervisorHealthObserver(AgentHealthObserver): ...

# agents/supervisor/circuit_breaker.py (existing, 250 lines)
# agents/supervisor/learning_engine.py (existing, 400 lines)
```

### Usage After Refactoring

```python
# Old way (still works via compatibility wrapper)
from supervisor_agent import SupervisorAgent

# New way
from agents.supervisor import SupervisorAgent, HealthMonitor, RecoveryEngine

# Internal usage
supervisor = SupervisorAgent(...)
health = supervisor.health_monitor.check_stage_health(stage)
if health.status == HealthStatus.UNHEALTHY:
    supervisor.recovery_engine.attempt_recovery(health)
```

---

## 12. Dependency Graph Example

```
core/
  ↓
services/
  ↓
managers/
  ↓
agents/ ← stages/ → validators/
  ↓        ↓
  pipelines/
     ↓
   workflows/
     ↓
    cli/

Legend:
- core: No dependencies (foundation)
- services: Depends only on core
- managers: Depends on core + services
- agents: Depends on core + services + managers
- stages: Depends on core + services + agents
- validators: Depends on core only
- pipelines: Depends on all above
- workflows: Depends on pipelines
- cli: Depends on workflows (top-level)
```

---

## 13. Conclusion

This modularization plan provides:

1. **Clear structure:** 10 top-level packages with logical grouping
2. **Manageable modules:** All under 500 lines
3. **Phased approach:** 4 phases over 8 weeks
4. **Risk mitigation:** Backward compatibility, extensive testing
5. **Validation:** Automated checks, comprehensive testing
6. **Documentation:** Complete updates and migration guides

**Key Benefits:**
- Easier maintenance and debugging
- Faster onboarding for new developers
- Better code reusability
- Reduced coupling
- Improved testability
- Clear dependency structure

**Estimated Effort:**
- Phase 1 (Foundation): 40 hours
- Phase 2 (Services/Utilities): 60 hours
- Phase 3 (Agents/Stages): 80 hours
- Phase 4 (Pipelines): 80 hours
- Phase 5 (Cleanup): 20 hours
- **Total:** 280 hours (~7 weeks full-time)

**Success will be measured by:**
- Zero files over 500 lines
- Zero circular dependencies
- >80% test coverage maintained
- All functionality preserved
- No performance regression
- Complete documentation
