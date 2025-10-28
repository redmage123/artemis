# Artemis Modularization - Dependency Graph

This document visualizes the dependency relationships in the new modular structure.

---

## Layered Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                          CLI Layer                              │
│                                                                 │
│                    cli/artemis_cli.py                          │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                       Workflow Layer                            │
│                                                                 │
│          workflows/handlers.py, planner.py, models.py          │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                       Pipeline Layer                            │
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐        │
│  │   Standard   │  │   Advanced   │  │   Routing    │        │
│  │  orchestrator│  │   dynamic    │  │    router    │        │
│  │    planner   │  │   two_pass   │  │  decisions   │        │
│  │   strategies │  │  thermo      │  │  risk        │        │
│  └──────────────┘  └──────────────┘  └──────────────┘        │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                        Stage Layer                              │
│                                                                 │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐         │
│  │ Analysis │ │ Planning │ │ Develop  │ │ Testing  │         │
│  │ Research │ │Architecture│Development│Integration│         │
│  │Requirements│Sprint Plan│Notebook  │ Validation │         │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘         │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                        Agent Layer                              │
│                                                                 │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐         │
│  │Developer │ │Supervisor│ │ Analysis │ │  Review  │         │
│  │  TDD     │ │  Health  │ │ Project  │ │   Code   │         │
│  │  CodeGen │ │ Recovery │ │ Refactor │ │Retrospect│         │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘         │
│  ┌──────────┐ ┌──────────┐                                    │
│  │   RAG    │ │   Git    │                                    │
│  │  Config  │ │   Chat   │                                    │
│  └──────────┘ └──────────┘                                    │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                       Manager Layer                             │
│                                                                 │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐         │
│  │  Build   │ │   Git    │ │  Bash    │ │ Terraform│         │
│  │  Maven   │ │  NPM     │ │ Gradle   │ │  Kanban  │         │
│  │  Cargo   │ │  Poetry  │ │  GoMod   │ │Checkpoint│         │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘         │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                       Service Layer                             │
│                                                                 │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐         │
│  │   LLM    │ │  Storage │ │Knowledge │ │Messaging │         │
│  │  Client  │ │   Redis  │ │  Graph   │ │   RMQ    │         │
│  │  Cache   │ │   RAG    │ │ Factory  │ │  Agent   │         │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘         │
│  ┌──────────┐ ┌──────────┐                                    │
│  │   ADR    │ │  Debug   │                                    │
│  │Generator │ │ Service  │                                    │
│  └──────────┘ └──────────┘                                    │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                         Core Layer                              │
│                                                                 │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐         │
│  │Interfaces│ │Exceptions│ │Constants │ │  State   │         │
│  │  Stage   │ │  Wrapped │ │   Retry  │ │ Machine  │         │
│  │  Logger  │ │  Custom  │ │  Timeout │ │  Events  │         │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘         │
└─────────────────────────────────────────────────────────────────┘

                    ┌──────────────────┐
                    │   Validators     │
                    │  (Cross-cutting) │
                    └──────────────────┘
```

---

## Detailed Module Dependencies

### Core Layer (No Dependencies)
```
core/
├── interfaces.py          → No dependencies
├── exceptions.py          → No dependencies
├── constants.py           → No dependencies
└── state_machine.py       → exceptions.py
```

### Service Layer (Depends on Core)
```
services/
├── llm/
│   ├── client.py          → core/*, utilities/retry
│   ├── cache.py           → core/*, storage/redis_client
│   └── cost_tracker.py    → core/*
├── storage/
│   ├── rag_storage.py     → core/*, llm/client
│   ├── redis_client.py    → core/*
│   └── redis_*.py         → redis_client
├── knowledge/
│   ├── graph.py           → core/*, storage/rag_storage
│   └── factory.py         → graph
├── messaging/
│   ├── interface.py       → core/interfaces
│   ├── factory.py         → interface, agent_messenger, rabbitmq_messenger
│   ├── agent_messenger.py → interface, core/*
│   └── rabbitmq_messenger.py → interface, core/*
└── adr/
    ├── generator.py       → core/*, llm/client
    ├── numbering.py       → core/*
    └── storage.py         → core/*
```

### Manager Layer (Depends on Core + Services)
```
managers/
├── build/
│   ├── factory.py         → core/*, all build managers
│   ├── universal_build.py → core/*, factory
│   └── maven.py, npm.py... → core/*, services/bash
├── git/
│   └── git_manager.py     → core/*, services/bash
├── bash/
│   └── bash_manager.py    → core/*
└── kanban/
    └── kanban_manager.py  → core/*, storage/redis_client
```

### Agent Layer (Depends on Core + Services + Managers)
```
agents/
├── base/
│   ├── agent_interface.py → core/interfaces
│   └── debug_mixin.py     → core/*
├── developer/
│   ├── standalone_agent.py → base/*, services/llm, validators/*
│   ├── tdd_workflow.py     → services/test_runner
│   ├── code_generation.py  → services/llm, validators/*
│   └── retry_coordinator.py → utilities/retry
├── supervisor/
│   ├── supervisor_agent.py → base/*, health_monitor, recovery_engine
│   ├── health_monitor.py   → core/*, pipeline/observer
│   ├── recovery_engine.py  → core/*, utilities/retry
│   └── health_observer.py  → core/*, pipeline/observer
└── analysis/
    ├── project_analysis_agent.py → base/*, services/llm
    └── code_refactoring_agent.py → base/*, services/llm
```

### Stage Layer (Depends on Core + Services + Agents)
```
stages/
├── base/
│   ├── stage_interface.py → core/interfaces
│   └── supervised_mixin.py → agents/supervisor
├── analysis/
│   └── project_analysis.py → base/*, agents/analysis
├── planning/
│   ├── architecture.py     → base/*, services/adr
│   └── sprint_planning.py  → base/*, models/sprint
├── development/
│   └── development.py      → base/*, agents/developer
└── validation/
    └── validation.py       → base/*, validators/*
```

### Pipeline Layer (Depends on All Above)
```
pipelines/
├── standard/
│   ├── orchestrator.py    → stages/*, workflow_planner, strategies
│   ├── workflow_planner.py → routing/router
│   └── strategies.py      → stages/*
├── advanced/
│   ├── dynamic/
│   │   ├── pipeline.py    → builder, selectors, executors
│   │   ├── builder.py     → pipeline
│   │   ├── selectors.py   → stages/*
│   │   └── executors.py   → stages/*
│   ├── two_pass/
│   │   ├── pipeline.py    → strategies, memento, comparator
│   │   ├── strategies.py  → memento
│   │   └── memento.py     → No dependencies
│   └── thermodynamic/
│       ├── computing.py   → strategies, bayesian, monte_carlo
│       ├── strategies.py  → confidence
│       └── confidence.py  → No dependencies
└── routing/
    ├── router.py          → routing_decisions
    ├── enhanced_router.py → router, risk_analysis
    └── risk_analysis.py   → routing_decisions
```

### Workflow Layer (Depends on Pipelines)
```
workflows/
├── handlers.py            → pipelines/standard/orchestrator
├── planner.py             → pipelines/routing/router
└── models.py              → core/*
```

### CLI Layer (Depends on Workflows)
```
cli/
└── artemis_cli.py         → workflows/handlers, config/*
```

---

## Circular Dependency Prevention Rules

### Rule 1: Strict Layering
- Lower layers CANNOT import from higher layers
- Order: Core → Services → Managers → Agents → Stages → Pipelines → Workflows → CLI

### Rule 2: Use Interfaces
- When higher layer needs lower layer functionality, use interface
- Example: Agent doesn't import Stage directly, uses PipelineStage interface

### Rule 3: Dependency Injection
- Pass dependencies through constructors, not global imports
- Example:
  ```python
  # ✅ Good
  class DevelopmentStage:
      def __init__(self, developer_agent: DeveloperAgent):
          self.developer = developer_agent

  # ❌ Bad
  from agents.developer import DeveloperAgent
  class DevelopmentStage:
      def __init__(self):
          self.developer = DeveloperAgent()
  ```

### Rule 4: Observer Pattern for Cross-Cutting
- Use events for cross-cutting concerns
- Example: Pipeline observer broadcasts events, agents subscribe

### Rule 5: Factory Pattern for Complex Creation
- Use factories to break creation dependencies
- Example: BuildManagerFactory creates specific build managers

---

## Import Rules by Layer

### Core Layer
```python
# ✅ Allowed
import os, sys, typing, dataclasses, abc, enum

# ❌ Not allowed
from services import *
from agents import *
from pipelines import *
```

### Service Layer
```python
# ✅ Allowed
from core import *
from utilities import *

# ❌ Not allowed
from agents import *
from stages import *
from pipelines import *
```

### Manager Layer
```python
# ✅ Allowed
from core import *
from services import *
from utilities import *

# ❌ Not allowed
from agents import *
from stages import *
from pipelines import *
```

### Agent Layer
```python
# ✅ Allowed
from core import *
from services import *
from managers import *
from utilities import *
from validators import *

# ❌ Not allowed
from stages import *  # Use interfaces instead
from pipelines import *
```

### Stage Layer
```python
# ✅ Allowed
from core import *
from services import *
from managers import *
from agents import *
from validators import *

# ❌ Not allowed
from pipelines import *  # Stages don't know about pipelines
```

### Pipeline Layer
```python
# ✅ Allowed
from core import *
from services import *
from managers import *
from agents import *
from stages import *
from validators import *

# ❌ Not allowed
from workflows import *  # Pipelines don't know about workflows
```

---

## Example: Avoiding Circular Dependencies

### Problem: Agent ↔ Stage Circular Dependency

```python
# ❌ BAD: Circular dependency
# agents/developer/standalone_agent.py
from stages.development import DevelopmentStage  # ❌

class StandaloneDeveloperAgent:
    def execute(self):
        stage = DevelopmentStage()  # ❌ Agent knows about Stage

# stages/development/development.py
from agents.developer import StandaloneDeveloperAgent  # ❌

class DevelopmentStage:
    def __init__(self):
        self.agent = StandaloneDeveloperAgent()  # ❌ Stage knows about Agent
```

### Solution: Dependency Injection

```python
# ✅ GOOD: Dependency injection breaks cycle
# core/interfaces.py
class DeveloperAgentInterface(ABC):
    @abstractmethod
    def execute_task(self, task: str) -> str:
        pass

# agents/developer/standalone_agent.py
from core.interfaces import DeveloperAgentInterface

class StandaloneDeveloperAgent(DeveloperAgentInterface):
    def execute_task(self, task: str) -> str:
        # Implementation
        pass

# stages/development/development.py
from core.interfaces import DeveloperAgentInterface

class DevelopmentStage:
    def __init__(self, developer: DeveloperAgentInterface):
        self.developer = developer  # ✅ Depends on interface

# pipelines/standard/orchestrator.py
from agents.developer import StandaloneDeveloperAgent
from stages.development import DevelopmentStage

class ArtemisOrchestrator:
    def __init__(self):
        developer = StandaloneDeveloperAgent()
        self.dev_stage = DevelopmentStage(developer)  # ✅ Inject dependency
```

---

## Dependency Validation Commands

```bash
# 1. Check for circular dependencies
pydeps src --show-cycles

# 2. Visualize dependency graph
pydeps src --max-bacon=2 -o dependency_graph.svg

# 3. Check specific module dependencies
pydeps src/agents/supervisor --show-deps

# 4. Find all imports in a file
grep -E "^from |^import " src/agents/supervisor/supervisor_agent.py

# 5. Find who imports a module
grep -r "from agents.supervisor import" src/

# 6. Check layer violations
# Custom script: scripts/check_layer_violations.py
python scripts/check_layer_violations.py
```

---

## Module Dependency Matrix

| Layer       | Core | Services | Managers | Agents | Stages | Pipelines | Workflows | CLI |
|-------------|------|----------|----------|--------|--------|-----------|-----------|-----|
| Core        | ✓    | ✗        | ✗        | ✗      | ✗      | ✗         | ✗         | ✗   |
| Services    | ✓    | ✓        | ✗        | ✗      | ✗      | ✗         | ✗         | ✗   |
| Managers    | ✓    | ✓        | ✓        | ✗      | ✗      | ✗         | ✗         | ✗   |
| Agents      | ✓    | ✓        | ✓        | ✓      | ✗      | ✗         | ✗         | ✗   |
| Stages      | ✓    | ✓        | ✓        | ✓      | ✓      | ✗         | ✗         | ✗   |
| Pipelines   | ✓    | ✓        | ✓        | ✓      | ✓      | ✓         | ✗         | ✗   |
| Workflows   | ✓    | ✓        | ✓        | ✓      | ✓      | ✓         | ✓         | ✗   |
| CLI         | ✓    | ✓        | ✓        | ✓      | ✓      | ✓         | ✓         | ✓   |

Legend:
- ✓ = Can import from this layer
- ✗ = Cannot import from this layer

---

## Cross-Cutting Concerns

Some modules span multiple layers:

### Validators (Cross-Cutting)
```
validators/
├── streaming_validator.py  → Used by agents/developer
├── artifact_quality.py     → Used by stages/validation
├── code_standards.py       → Used by agents/developer, stages/validation
└── requirements_driven.py  → Used by stages/validation

Dependency: validators → core/* only
Usage: Any layer can import validators
```

### Utilities (Cross-Cutting)
```
utilities/
├── retry.py               → Used by services, agents, pipelines
├── file_utils.py          → Used by services, managers, agents
└── validation_utils.py    → Used by validators, stages

Dependency: utilities → core/* only
Usage: Any layer can import utilities
```

### Models (Cross-Cutting)
```
models/
├── requirements.py        → Used by stages/analysis, agents/analysis
├── sprint.py              → Used by stages/planning
└── user_stories.py        → Used by stages/planning

Dependency: models → core/* only
Usage: Any layer can import models
```

---

## Refactoring Impact Analysis

### Supervisor Agent Refactoring

**Before:**
```
supervisor_agent.py (3,403 lines)
  ↓
[All pipeline components depend on this one file]
```

**After:**
```
agents/supervisor/
├── supervisor_agent.py (400 lines)  ← Main orchestrator
├── health_monitor.py (350 lines)     ← Health monitoring
├── recovery_engine.py (400 lines)    ← Recovery strategies
├── health_observer.py (250 lines)    ← Event observers
├── circuit_breaker.py (250 lines)    ← Circuit breaker
└── learning_engine.py (400 lines)    ← ML learning

Dependencies flow clearly:
supervisor_agent → health_monitor, recovery_engine, health_observer
health_monitor → health_observer
recovery_engine → health_monitor
```

**Benefits:**
- Each module has clear responsibility
- Easy to test each component independently
- Changes to recovery don't affect monitoring
- New recovery strategies easy to add

---

## Summary

This dependency graph ensures:

1. **No circular dependencies** - Strict layering prevents cycles
2. **Clear dependency flow** - Always bottom-up, never top-down
3. **Easy testing** - Each layer can be tested independently
4. **Maintainability** - Changes localized to specific layers
5. **Extensibility** - New features added without modifying existing layers

The key to maintaining this structure is:
- **Use interfaces** to break direct dependencies
- **Use dependency injection** to wire components
- **Use observer pattern** for cross-cutting concerns
- **Validate regularly** with `pydeps` and custom scripts
- **Enforce in CI/CD** to prevent regressions
