# Artemis Modularization - Quick Start Guide

This guide helps you get started with the modularization effort immediately.

---

## Prerequisites

### 1. Install Dependencies
```bash
# Install development tools
pip install pydeps pipdeptree pylint mypy black isort

# Install visualization tools (optional)
pip install graphviz matplotlib networkx
```

### 2. Backup Current State
```bash
# Create backup branch
git checkout -b backup/pre-modularization
git push origin backup/pre-modularization

# Create feature branch for work
git checkout master
git checkout -b feature/modularization-phase1
```

### 3. Run Baseline Tests
```bash
# Run full test suite and save results
pytest --cov=src --cov-report=html --cov-report=term > baseline_tests.txt

# Save baseline metrics
python scripts/check_module_sizes.py > baseline_sizes.txt
pydeps src --show-cycles > baseline_deps.txt 2>&1
```

---

## Phase 1: Foundation Setup (Day 1)

### Step 1: Create Directory Structure (30 minutes)

```bash
# Create all directories
mkdir -p src/{core,agents,pipelines,stages,managers,services,validators}
mkdir -p src/{workflows,models,utilities,config,platform,security,data}
mkdir -p src/{integrations,cli,tests,scripts}

# Create subdirectories
mkdir -p src/agents/{base,developer,supervisor,analysis,review}
mkdir -p src/pipelines/{standard,advanced,routing}
mkdir -p src/pipelines/advanced/{dynamic,two_pass,thermodynamic}
mkdir -p src/stages/{base,analysis,planning,development,validation,testing,review,uiux}
mkdir -p src/managers/{build,git,bash,terraform,kanban,checkpoint,prompt}
mkdir -p src/services/{llm,ai_query,storage,knowledge,messaging,adr,debug}
mkdir -p src/tests/{test_agents,test_pipelines,test_stages,test_managers,test_services}

# Create __init__.py files
find src -type d -exec touch {}/__init__.py \;
```

### Step 2: Move Core Modules (1 hour)

```bash
# Create automated migration script
cat > scripts/migrate_core.sh << 'EOF'
#!/bin/bash
set -e

# Move core files
cp src/artemis_stage_interface.py src/core/interfaces.py
cp src/artemis_exceptions.py src/core/exceptions.py
cp src/artemis_constants.py src/core/constants.py
cp src/artemis_state_machine.py src/core/state_machine.py

# Create __init__.py with re-exports
cat > src/core/__init__.py << 'PYEOF'
"""
Artemis Core - Interfaces, Exceptions, Constants, State Machine

This package contains the foundational abstractions that all other
modules depend on. No dependencies on other Artemis packages.
"""

from .interfaces import PipelineStage, LoggerInterface
from .exceptions import (
    ArtemisException,
    PipelineException,
    PipelineStageError,
    wrap_exception
)
from .constants import (
    MAX_RETRY_ATTEMPTS,
    DEFAULT_RETRY_INTERVAL_SECONDS,
    RETRY_BACKOFF_FACTOR
)
from .state_machine import (
    ArtemisStateMachine,
    PipelineState,
    StageState,
    EventType
)

__all__ = [
    'PipelineStage',
    'LoggerInterface',
    'ArtemisException',
    'PipelineException',
    'PipelineStageError',
    'wrap_exception',
    'MAX_RETRY_ATTEMPTS',
    'DEFAULT_RETRY_INTERVAL_SECONDS',
    'RETRY_BACKOFF_FACTOR',
    'ArtemisStateMachine',
    'PipelineState',
    'StageState',
    'EventType',
]
PYEOF

echo "Core modules migrated successfully!"
EOF

chmod +x scripts/migrate_core.sh
./scripts/migrate_core.sh
```

### Step 3: Create Compatibility Wrappers (30 minutes)

```python
# src/artemis_stage_interface.py
"""
DEPRECATED: Use core.interfaces instead

This compatibility wrapper will be removed in v2.0
"""
import warnings

warnings.warn(
    "artemis_stage_interface is deprecated. Use 'from core.interfaces import ...' instead.",
    DeprecationWarning,
    stacklevel=2
)

# Re-export everything from new location
from core.interfaces import *

__all__ = ['PipelineStage', 'LoggerInterface']
```

### Step 4: Update Imports in Test Files (30 minutes)

```bash
# Create automated import rewriter
cat > scripts/rewrite_test_imports.py << 'EOF'
#!/usr/bin/env python3
"""
Rewrite imports in test files to use new structure
"""
import re
from pathlib import Path

REPLACEMENTS = {
    'from artemis_stage_interface import': 'from core.interfaces import',
    'from artemis_exceptions import': 'from core.exceptions import',
    'from artemis_constants import': 'from core.constants import',
    'from artemis_state_machine import': 'from core.state_machine import',
}

def rewrite_file(filepath: Path):
    content = filepath.read_text()
    original = content

    for old, new in REPLACEMENTS.items():
        content = content.replace(old, new)

    if content != original:
        filepath.write_text(content)
        print(f"Updated: {filepath}")

# Update all test files
for test_file in Path('src').rglob('test_*.py'):
    rewrite_file(test_file)

print("\nTest imports updated!")
EOF

chmod +x scripts/rewrite_test_imports.py
python scripts/rewrite_test_imports.py
```

### Step 5: Verify Phase 1 (30 minutes)

```bash
# Run tests
pytest

# Check imports
python -c "from core.interfaces import PipelineStage; print('✓ Core imports work')"
python -c "from core.exceptions import ArtemisException; print('✓ Exception imports work')"
python -c "from core.constants import MAX_RETRY_ATTEMPTS; print('✓ Constant imports work')"

# Check backward compatibility
python -c "from artemis_stage_interface import PipelineStage; print('✓ Backward compat works')"

# Commit Phase 1
git add src/core/ scripts/
git commit -m "Phase 1: Migrate core modules to core/ package"
```

---

## Phase 2: Services Migration (Days 2-3)

### Step 1: Move Service Modules (2 hours)

```bash
# Create migration script
cat > scripts/migrate_services.sh << 'EOF'
#!/bin/bash
set -e

# LLM services
cp src/llm_client.py src/services/llm/client.py
cp src/llm_cache.py src/services/llm/cache.py
cp src/cost_tracker.py src/services/llm/cost_tracker.py

# Storage services
cp src/rag_storage_helper.py src/services/storage/rag_storage.py
cp src/redis_client.py src/services/storage/redis_client.py
cp src/redis_rate_limiter.py src/services/storage/redis_rate_limiter.py
cp src/redis_pipeline_tracker.py src/services/storage/redis_pipeline_tracker.py
cp src/redis_metrics.py src/services/storage/redis_metrics.py

# Knowledge services
cp src/knowledge_graph.py src/services/knowledge/graph.py
cp src/knowledge_graph_factory.py src/services/knowledge/factory.py

# Messaging services
cp src/messenger_interface.py src/services/messaging/interface.py
cp src/messenger_factory.py src/services/messaging/factory.py
cp src/agent_messenger.py src/services/messaging/agent_messenger.py
cp src/rabbitmq_messenger.py src/services/messaging/rabbitmq_messenger.py

# ADR services
cp src/adr_generator.py src/services/adr/generator.py
cp src/adr_numbering_service.py src/services/adr/numbering.py
cp src/adr_storage_service.py src/services/adr/storage.py

# AI Query Service
cp src/ai_query_service.py src/services/ai_query/service.py

# Debug service
cp src/debug_service.py src/services/debug/service.py

# Path config
cp src/path_config_service.py src/services/path_config.py

echo "Services migrated!"
EOF

chmod +x scripts/migrate_services.sh
./scripts/migrate_services.sh
```

### Step 2: Update Service Imports

```bash
# Rewrite imports in service files
python scripts/rewrite_imports.py src/services/
```

### Step 3: Create Service __init__.py Files

```python
# src/services/__init__.py
"""
Artemis Services - Shared service layer

Services depend only on core and utilities.
All higher layers can use services.
"""

from .llm.client import create_llm_client, LLMClient
from .storage.rag_storage import RAGStorageHelper
from .knowledge.graph import KnowledgeGraph
from .messaging.factory import MessengerFactory

__all__ = [
    'create_llm_client',
    'LLMClient',
    'RAGStorageHelper',
    'KnowledgeGraph',
    'MessengerFactory',
]
```

### Step 4: Verify Phase 2

```bash
# Test imports
python -c "from services.llm import LLMClient; print('✓ LLM services work')"
python -c "from services.storage import RAGStorageHelper; print('✓ Storage services work')"

# Run tests
pytest src/tests/test_llm* src/tests/test_redis*

# Commit
git add src/services/
git commit -m "Phase 2: Migrate services to services/ package"
```

---

## Phase 3: Refactor Supervisor Agent (Days 4-5)

### Step 1: Create Module Structure

```bash
mkdir -p src/agents/supervisor
touch src/agents/supervisor/{__init__.py,supervisor_agent.py,health_monitor.py,recovery_engine.py,health_observer.py}
```

### Step 2: Extract Health Monitor (2 hours)

```python
# src/agents/supervisor/health_monitor.py
"""
Health Monitor - Detects crashes, hangs, stalls

Single Responsibility: Monitor health and detect issues
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional
import psutil

from core.interfaces import LoggerInterface
from core.exceptions import wrap_exception


class HealthStatus(Enum):
    """Health status levels"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    CRITICAL = "critical"


@dataclass
class ProcessHealth:
    """Process health metrics"""
    pid: int
    cpu_percent: float
    memory_percent: float
    status: str
    health_status: HealthStatus


@dataclass
class StageHealth:
    """Stage health metrics"""
    stage_name: str
    is_running: bool
    duration_seconds: float
    process_health: Optional[ProcessHealth]
    health_status: HealthStatus


class HealthMonitor:
    """
    Monitors health of stages and processes

    Single Responsibility: Detect health issues
    """

    def __init__(self, logger: LoggerInterface):
        self.logger = logger

    @wrap_exception
    def check_stage_health(self, stage_name: str, pid: int) -> StageHealth:
        """Check health of a stage"""
        # Extract logic from SupervisorAgent._check_process_health
        # ... implementation ...

    @wrap_exception
    def detect_hangs(self, stage_name: str, last_activity: float) -> bool:
        """Detect if stage has hung"""
        # Extract logic from SupervisorAgent._detect_hangs
        # ... implementation ...

    @wrap_exception
    def detect_stalls(self, stage_name: str, progress: float) -> bool:
        """Detect if stage has stalled"""
        # Extract logic from SupervisorAgent._detect_stalls
        # ... implementation ...
```

### Step 3: Extract Recovery Engine (2 hours)

```python
# src/agents/supervisor/recovery_engine.py
"""
Recovery Engine - Executes recovery strategies

Single Responsibility: Attempt recovery from failures
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional

from core.interfaces import LoggerInterface
from core.exceptions import wrap_exception
from utilities.retry import RetryStrategy


class RecoveryAction(Enum):
    """Recovery action types"""
    RETRY = "retry"
    RESTART = "restart"
    FAILOVER = "failover"
    DEGRADE = "degrade"
    MANUAL = "manual"


@dataclass
class RecoveryStrategy:
    """Recovery strategy configuration"""
    action: RecoveryAction
    max_attempts: int
    backoff_factor: float


class RecoveryEngine:
    """
    Executes recovery strategies

    Single Responsibility: Recover from failures
    """

    def __init__(self, logger: LoggerInterface):
        self.logger = logger

    @wrap_exception
    def attempt_recovery(self, health_event) -> bool:
        """Attempt recovery based on event"""
        # Extract logic from SupervisorAgent._attempt_recovery
        # ... implementation ...

    @wrap_exception
    def apply_retry_strategy(self, stage_name: str) -> bool:
        """Apply retry recovery strategy"""
        # Extract logic from SupervisorAgent._apply_retry_strategy
        # ... implementation ...
```

### Step 4: Update Main Supervisor Agent (1 hour)

```python
# src/agents/supervisor/supervisor_agent.py
"""
Supervisor Agent - Orchestrates monitoring and recovery

Single Responsibility: Coordinate supervision (delegate actual work)
"""

from typing import Optional

from core.interfaces import LoggerInterface
from core.exceptions import wrap_exception
from agents.base.debug_mixin import DebugMixin
from .health_monitor import HealthMonitor, StageHealth
from .recovery_engine import RecoveryEngine, RecoveryAction
from .health_observer import SupervisorHealthObserver


class SupervisorAgent(DebugMixin):
    """
    Main supervisor agent - orchestrates monitoring and recovery

    Single Responsibility: Orchestrate (don't implement)
    """

    def __init__(self, logger: LoggerInterface):
        DebugMixin.__init__(self, component_name="supervisor")
        self.logger = logger

        # Delegate to specialized components
        self.health_monitor = HealthMonitor(logger)
        self.recovery_engine = RecoveryEngine(logger)
        self.observer = SupervisorHealthObserver(logger)

    @wrap_exception
    def monitor_stage(self, stage_name: str, pid: int) -> StageHealth:
        """Monitor a stage (delegate to health monitor)"""
        health = self.health_monitor.check_stage_health(stage_name, pid)

        if health.health_status != HealthStatus.HEALTHY:
            self.handle_unhealthy_stage(health)

        return health

    @wrap_exception
    def handle_unhealthy_stage(self, health: StageHealth):
        """Handle unhealthy stage (coordinate recovery)"""
        self.observer.notify_health_event(health)
        success = self.recovery_engine.attempt_recovery(health)

        if not success:
            self.escalate_to_manual(health)
```

### Step 5: Verify Refactoring

```bash
# Test supervisor agent
pytest src/tests/test_supervisor*

# Check module sizes
python scripts/check_module_sizes.py src/agents/supervisor/

# Verify no circular deps
pydeps src/agents/supervisor --show-cycles

# Commit
git add src/agents/supervisor/
git commit -m "Phase 3: Refactor supervisor agent into 6 modules"
```

---

## Quick Commands Reference

### Daily Workflow

```bash
# 1. Start work session
git pull origin feature/modularization-phase1
git checkout -b feature/modularization-phase1-day-X

# 2. Make changes
# ... edit files ...

# 3. Validate changes
pytest                                    # Run tests
python scripts/check_module_sizes.py      # Check sizes
pydeps src --show-cycles                  # Check deps
pylint src/path/to/changed/files          # Check quality

# 4. Commit if all pass
git add .
git commit -m "Descriptive message"
git push origin feature/modularization-phase1-day-X

# 5. Create PR for review
gh pr create --title "Phase 1 Day X: ..." --body "..."
```

### Validation Commands

```bash
# Run all tests
pytest -v

# Run specific test file
pytest src/tests/test_supervisor_agent.py -v

# Check test coverage
pytest --cov=src --cov-report=html
open htmlcov/index.html

# Check module sizes (must be < 500 lines)
python scripts/check_module_sizes.py

# Check circular dependencies (must be 0)
pydeps src --show-cycles

# Check code quality
pylint src/agents/supervisor/

# Check type hints
mypy src/agents/supervisor/

# Format code
black src/agents/supervisor/
isort src/agents/supervisor/
```

### Troubleshooting

```bash
# Import error?
python -c "import sys; sys.path.insert(0, 'src'); from core.interfaces import PipelineStage"

# Circular dependency?
pydeps src/agents/supervisor --show-deps --max-bacon=2

# Test failing?
pytest src/tests/test_supervisor_agent.py -v -s  # Show print statements

# Module too large?
wc -l src/agents/supervisor/supervisor_agent.py  # Should be < 500
```

---

## Checklist for Each Module

When refactoring a module, use this checklist:

```markdown
## Module: agents/supervisor/health_monitor.py

- [ ] Module created in correct location
- [ ] Module size < 500 lines (current: ___ lines)
- [ ] Imports updated to use new structure
- [ ] Single Responsibility Principle followed
- [ ] Docstrings complete (module, class, methods)
- [ ] Type hints on all method signatures
- [ ] All methods use @wrap_exception
- [ ] No circular dependencies (verified with pydeps)
- [ ] Unit tests created/updated
- [ ] Unit tests pass (pytest)
- [ ] No pylint errors
- [ ] No mypy errors
- [ ] Code formatted (black, isort)
- [ ] __init__.py updated with exports
- [ ] Compatibility wrapper created (if needed)
- [ ] Documentation updated
- [ ] Changes committed to git
```

---

## Getting Help

### Resources

1. **Main Plan:** ARTEMIS_MODULARIZATION_PLAN.md - Complete refactoring plan
2. **Dependency Graph:** MODULARIZATION_DEPENDENCY_GRAPH.md - Dependency rules
3. **Summary:** MODULARIZATION_SUMMARY.md - Quick overview
4. **This Guide:** MIGRATION_QUICK_START.md - Step-by-step instructions

### Common Issues

**Issue:** Import error after moving module
**Solution:** Update both the module's imports AND create compatibility wrapper in old location

**Issue:** Circular dependency detected
**Solution:** Use interface/abstract base class to break cycle, inject dependency

**Issue:** Tests failing after refactoring
**Solution:** Update test imports, verify all components still accessible

**Issue:** Module still too large (> 500 lines)
**Solution:** Extract helper classes/functions to separate module, apply SRP

---

## Success Metrics

Track progress with these metrics:

```bash
# Number of files > 500 lines (target: 0)
find src -name "*.py" -exec wc -l {} + | awk '$1 > 500 {print}' | wc -l

# Largest file size (target: < 500)
find src -name "*.py" -exec wc -l {} + | sort -rn | head -1

# Circular dependencies (target: 0)
pydeps src --show-cycles | grep "Cycle detected" | wc -l

# Test coverage (target: > 80%)
pytest --cov=src --cov-report=term | grep "TOTAL"

# Average module size
find src -name "*.py" -exec wc -l {} + | awk '{sum+=$1; count++} END {print sum/count}'
```

---

## Next Steps

1. Complete Phase 1 (Foundation) - Days 1-2
2. Complete Phase 2 (Services) - Days 3-4
3. Complete Phase 3 (Agents) - Days 5-10
4. Complete Phase 4 (Pipelines) - Days 11-20
5. Final cleanup and documentation - Days 21-25

**Good luck with the modularization effort!**
