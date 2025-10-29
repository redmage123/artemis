# Artemis Hyperparameter Audit

**Generated**: 2025-10-29
**Purpose**: Comprehensive list of all configurable parameters for Hydra config integration and adaptive optimization

## Overview

This document catalogs ALL hyperparameters found in the Artemis codebase that should be:
1. Moved to Hydra configuration
2. Made adaptive based on task complexity and platform capabilities
3. Tunable for different execution profiles (MINIMAL, BALANCED, AGGRESSIVE, CONSERVATIVE)

---

## 1. LLM Parameters

### Temperature
Controls randomness in LLM output (0.0 = deterministic, 1.0 = creative)

| Parameter | Default | File | Line | Adaptive? |
|-----------|---------|------|------|-----------|
| `temperature` | 0.3 | `project_analysis/analyzers/llm_powered.py` | 268, 281 | ✅ YES |
| `temperature` | 0.3 | `self_critique/critique_generator.py` | 253 | ✅ YES |
| `temperature` | 0.1 | `preflight_validator.py` | 291 | ✅ YES |
| `temperature` | 0.2 | `code_review/agent.py` | 340 | ✅ YES |
| `temperature` | 0.3 | `state_machine/artemis_state_machine_original.py` | 404 | ✅ YES |
| `temperature` | 0.3 | `state_machine/llm_workflow_generator.py` | 77 | ✅ YES |
| `temperature` | 0.3 | `ai_orchestration/ai_planner.py` | 97 | ✅ YES |
| `temperature` | 0.3 | `ai_query/ai_query_service_impl.py` | 118 | ✅ YES |
| `temperature` | 0.3 | `stages/architecture/adr_generator.py` | 143 | ✅ YES |
| `temperature` | 0.4 | `stages/architecture/user_story_generator.py` | 190 | ✅ YES |
| `temperature` | 0.3 | `stages/bdd_scenario/scenario_generator.py` | 72 | ✅ YES |
| `temperature` | 0.3 | `stages/sprint_planning/feature_extractor.py` | 142 | ✅ YES |
| `temperature` | 0.7 | `agents/developer/llm_client_wrapper.py` | 125, 370 | ✅ YES |
| `llm_temperature` | 0.3 | `agents/supervisor/supervisor.py` | 117 | ✅ YES |
| `llm_temperature` | 0.2 | `agents/supervisor/auto_fix.py` | 35 | ✅ YES |

**Adaptive Strategy**:
- MINIMAL profile: 0.1 (deterministic)
- BALANCED profile: 0.3 (default)
- AGGRESSIVE profile: 0.5 (more creative)
- CONSERVATIVE profile: 0.2 (cautious)

### Max Tokens
Controls maximum tokens in LLM response

| Parameter | Default | File | Line | Adaptive? |
|-----------|---------|------|------|-----------|
| `max_tokens` | 2000 | `project_analysis/analyzers/llm_powered.py` | 269, 282, 568 | ✅ YES |
| `max_tokens` | 1500 | `self_critique/critique_generator.py` | 254 | ✅ YES |
| `max_tokens` | 4000 | `preflight_validator.py` | 291 | ✅ YES |
| `max_tokens` | 1500 | `state_machine/artemis_state_machine_original.py` | 404 | ✅ YES |

**Adaptive Strategy**:
- Simple tasks: 1000 tokens
- Medium tasks: 2000 tokens
- Complex tasks: 4000 tokens

### Top-K / Top-P (RAG Retrieval)
Controls number of similar documents retrieved

| Parameter | Default | File | Line | Adaptive? |
|-----------|---------|------|------|-----------|
| `top_k` | 3 | `self_critique/improvement_suggester.py` | 343 | ✅ YES |
| `top_k` | 5 | `rag_agent.py` | 54 | ✅ YES |
| `top_k` | 5 | `research/repository.py` | 92 | ✅ YES |
| `top_k` | 3-5 | `stages/code_review_stage/refactoring_suggestions.py` | 210 | ✅ YES |
| `top_k` | 3-5 | `stages/content_generation_helper.py` | 50, 80 | ✅ YES |
| `top_k` | 5 | `validated_developer/validation_strategies.py` | 74 | ✅ YES |

**Adaptive Strategy**:
- Fast path: top_k=3 (quick retrieval)
- Medium path: top_k=5 (balanced)
- Full path: top_k=10 (comprehensive)

---

## 2. Timeout Parameters

Critical for preventing hangs and controlling execution time

| Parameter | Default (sec) | File | Line | Adaptive? |
|-----------|---------------|------|------|-----------|
| `timeout` | 300 | `workflows/handlers/dependency_handlers.py` | - | ✅ YES |
| `socket_timeout` | 5 | `redis_client.py` | - | ✅ YES |
| `socket_connect_timeout` | 5 | `redis_client.py` | - | ✅ YES |
| `timeout` | 600 | `build_manager_base.py` | - | ✅ YES |
| `timeout` | 300 | `build_manager_base.py` | - | ✅ YES |
| `timeout_seconds` | 300 | `messaging/agent/models.py` | - | ✅ YES |
| `timeout` | 1800 | `unreal_manager.py` | - | ✅ YES |

**Adaptive Strategy**:
- SSD systems: Reduce by 20% (faster I/O)
- HDD systems: Increase by 50% (slower I/O)
- Low memory: Increase by 30% (more swapping)
- High CPU: Reduce by 20% (faster execution)

---

## 3. Retry Parameters

Controls retry behavior for transient failures

### Max Retries

| Parameter | Default | File | Line | Adaptive? |
|-----------|---------|------|------|-----------|
| `max_retries` | 2 | `workflows/definitions/code_workflows.py` | 68, 101 | ✅ YES |
| `max_retries` | 3 | `workflows/definitions/dependency_workflows.py` | 68 | ✅ YES |
| `max_retries` | 2 | `workflows/definitions/dependency_workflows.py` | 105, 141 | ✅ YES |
| `max_retries` | 3 | `workflows/definitions/llm_workflows.py` | 70 | ✅ YES |
| `max_retries` | 2 | `workflows/definitions/llm_workflows.py` | 110, 185 | ✅ YES |
| `max_retries` | 2 | `workflows/definitions/stage_workflows.py` | 69, 170 | ✅ YES |
| `max_retries` | 2-3 | `workflows/definitions/infrastructure_workflows.py` | 77, 112, 221 | ✅ YES |

**Adaptive Strategy**:
- MINIMAL profile: max_retries=1 (fail fast)
- BALANCED profile: max_retries=2 (default)
- AGGRESSIVE profile: max_retries=3 (persistent)
- CONSERVATIVE profile: max_retries=5 (very persistent)

### Retry Delays

| Parameter | Default (sec) | File | Line | Adaptive? |
|-----------|---------------|------|------|-----------|
| `retry_delay` | 5 | `messaging/rabbitmq/models.py` | 74 | ✅ YES |
| `initial_delay` | 2 (5-3) | `utilities/retry_utilities.py` | 27 | ✅ YES |
| `max_delay` | 60.0 | `utilities/retry_utilities.py` | 28 | ✅ YES |
| `retry_delay_seconds` | 10 | `stages/development_stage.py` | 168 | ✅ YES |
| `retry_delay_seconds` | 5.0 | `agents/supervisor/models.py` | 112 | ✅ YES |
| `base_delay` | 1.0 | `two_pass/pipeline/retry.py` | 26 | ✅ YES |
| `max_delay` | 30.0 | `two_pass/pipeline/retry.py` | 27 | ✅ YES |

**Adaptive Strategy**:
- Fast networks: initial_delay=1s
- Slow networks: initial_delay=5s
- Cloud services: initial_delay=3s with exponential backoff

---

## 4. Parallelism Parameters

Controls concurrent execution

### Workers/Threads/Developers

| Parameter | Default | File | Line | Adaptive? |
|-----------|---------|------|------|-----------|
| `max_workers` | 4-8 | `workflows/strategies/parallel_strategy.py` | 54 | ✅ YES |
| `max_parallel_developers` | 3 | `hydra_config.py` | 76 | ✅ YES |
| `max_parallel_workers` | 4 | `advanced_pipeline/pipeline_config.py` | 60 | ✅ YES |
| `thread_pool_size` | 4-16 | `adaptive_config_generator.py` | 202, 231, 261, 287 | ✅ YES |
| `prefetch_count` | 1 | `messaging/rabbitmq/messenger_core.py` | 39 | ✅ YES |

**Adaptive Strategy**:
```python
# CPU-based
max_workers = min(cpu_count // 2, 8)

# Memory-based
if memory_gb >= 16:
    max_parallel_developers = 3
elif memory_gb >= 8:
    max_parallel_developers = 2
else:
    max_parallel_developers = 1

# Task complexity-based
if task_complexity == SIMPLE:
    max_parallel_developers = 1  # No need for parallel
elif task_complexity == MEDIUM:
    max_parallel_developers = 1-2
elif task_complexity == COMPLEX:
    max_parallel_developers = 2-3
```

---

## 5. Batch Size Parameters

Controls batch processing for better throughput

| Parameter | Default | File | Line | Adaptive? |
|-----------|---------|------|------|-----------|
| `batch_size` | 50 | `adaptive_config_generator.py` | 199 | ✅ YES |
| `batch_size` | 100 | `adaptive_config_generator.py` | 228 | ✅ YES |
| `batch_size` | 200 | `adaptive_config_generator.py` | 258 | ✅ YES |
| `batch_size` | 25 | `adaptive_config_generator.py` | 284 | ✅ YES |

**Adaptive Strategy (Memory-based)**:
```python
if memory_gb >= 16:
    batch_size = 100
elif memory_gb >= 8:
    batch_size = 50
else:
    batch_size = 25
```

---

## 6. Complexity Thresholds

Used for task classification and routing

| Parameter | Default | File | Line | Adaptive? |
|-----------|---------|------|------|-----------|
| `complexity_low_threshold` | 50 | `validation/orchestrator_config.py` | 57 | ✅ YES |
| `complexity_medium_threshold` | 200 | `validation/orchestrator_config.py` | 58 | ✅ YES |
| `complexity_high_threshold` | 500 | `validation/orchestrator_config.py` | 59 | ✅ YES |
| `max_complexity` | 10 | `stages/code_review_stage/review_coordinator.py` | 43 | ✅ YES |
| `max_complexity` | 8 | `stages/code_review_stage/code_review_stage_core.py` | 390 | ✅ YES |

**Adaptive Strategy**:
- Adjust thresholds based on project size and language
- Python: lower thresholds (more permissive)
- Java/C++: higher thresholds (naturally more complex)

---

## 7. Validation Parameters

### Thresholds

| Parameter | Default | File | Line | Adaptive? |
|-----------|---------|------|------|-----------|
| `pass_threshold` | 0.8 | `artifacts/quality/aggregator.py` | 24 | ✅ YES |
| `confidence_threshold` | 0.7 | `advanced_pipeline/pipeline_config.py` | 50 | ✅ YES |
| `min_similarity_threshold` | 0.3 | `rag_validation/rag_validator.py` | 51 | ✅ YES |
| `min_confidence_threshold` | 0.6 | `rag_validation/rag_validator.py` | 52 | ✅ YES |

**Adaptive Strategy**:
- Fast path: pass_threshold=0.6 (permissive)
- Medium path: pass_threshold=0.7 (balanced)
- Full path: pass_threshold=0.9 (strict)

### Dependencies Thresholds

| Parameter | Default | File | Line | Adaptive? |
|-----------|---------|------|------|-----------|
| `dependencies_medium_threshold` | 5 | `validation/orchestrator_config.py` | 60 | ✅ YES |
| `dependencies_high_threshold` | 10 | `validation/orchestrator_config.py` | 61 | ✅ YES |

---

## 8. Memory Parameters

Controls memory allocation

| Parameter | Default | File | Line | Adaptive? |
|-----------|---------|------|------|-----------|
| `max_memory_mb` | 512 | `security/sandbox/models.py` | 31 | ✅ YES |
| `memory_per_agent_gb` | 0.5-2.0 | `adaptive_config_generator.py` | 193, 222, 252, 278 | ✅ YES |
| `max_bytes` | 100MB | `artemis_logger.py` | 61 | ⚠️ MAYBE |
| `backup_count` | 10 | `artemis_logger.py` | 61 | ⚠️ MAYBE |

**Adaptive Strategy**:
```python
# Per-agent memory allocation
available_memory = total_memory_gb - reserved_memory_gb
memory_per_agent = available_memory / num_parallel_agents

# Sandbox limits
if task_trusted:
    max_memory_mb = 1024
else:
    max_memory_mb = 256  # Untrusted code gets less
```

---

## 9. Cache Parameters

Controls caching behavior

| Parameter | Default | File | Line | Adaptive? |
|-----------|---------|------|------|-----------|
| `maxsize` | 1-256 | Multiple `@lru_cache(maxsize=...)` | Various | ✅ YES |
| `max_size` | 100 | `ai_orchestration/plan_cache.py` | 40 | ✅ YES |
| `max_size` | 1000 | `rag_validation/query_cache.py` | 37 | ✅ YES |
| `ttl_seconds` | 3600 | `rag_validation/query_cache.py` | 37 | ✅ YES |

**Adaptive Strategy**:
```python
# Memory-based cache sizing
if memory_gb >= 16:
    lru_cache_maxsize = 512
    query_cache_max_size = 2000
elif memory_gb >= 8:
    lru_cache_maxsize = 256
    query_cache_max_size = 1000
else:
    lru_cache_maxsize = 64
    query_cache_max_size = 100
```

---

## 10. Window/Buffer Parameters

| Parameter | Default | File | Line | Adaptive? |
|-----------|---------|------|------|-----------|
| `window_size` | 100 | `advanced_pipeline/strategy/performance_tracker.py` | 38 | ✅ YES |
| `performance_metrics_window` | 10 | `advanced_pipeline/pipeline_config.py` | 76 | ✅ YES |
| `window_seconds` | 5-60 | `redis_rate_limiter.py` | Various | ✅ YES |
| `time_window_days` | 90 | `rag_agent.py` | 83 | ⚠️ MAYBE |

---

## 11. Feature Flags

Boolean parameters that enable/disable features

### Enable Flags

| Parameter | Default | File | Line | Adaptive? |
|-----------|---------|------|------|-----------|
| `enable_llm_analysis` | True | `project_analysis/engine.py` | 45 | ✅ YES |
| `enable_validation` | True | `validated_developer/factory.py` | 33 | ✅ YES |
| `enable_rag_validation` | True | `validated_developer/factory.py` | 34 | ✅ YES |
| `enable_self_critique` | True | `validated_developer/factory.py` | 35 | ✅ YES |
| `enable_dynamic_pipeline` | True | `advanced_pipeline/pipeline_config.py` | 44 | ✅ YES |
| `enable_thermodynamic` | True | `advanced_pipeline/pipeline_config.py` | 46 | ✅ YES |
| `enable_two_pass` | False | Various | - | ✅ YES |
| `enable_temperature_annealing` | True | `advanced_pipeline/pipeline_config.py` | 69 | ✅ YES |
| `enable_performance_tracking` | True | `advanced_pipeline/pipeline_config.py` | 75 | ✅ YES |
| `enable_type_checking` | True | `validation/static_analysis_validator.py` | 60 | ✅ YES |
| `enable_linting` | True | `validation/static_analysis_validator.py` | 61 | ✅ YES |
| `enable_complexity_check` | True | `validation/static_analysis_validator.py` | 62 | ✅ YES |
| `enable_intelligent_selection` | True | `validation/orchestrator_config.py` | 51 | ✅ YES |
| `enable_historical_learning` | True | `validation/orchestrator_config.py` | 79 | ✅ YES |
| `enable_code_standards` | True | `stages/code_review_stage/review_coordinator.py` | 38 | ✅ YES |
| `enable_advanced_validation` | True | `stages/code_review_stage/review_coordinator.py` | 40 | ✅ YES |
| `enable_static_analysis` | True | `stages/code_review_stage/code_review_stage_core.py` | 386, 398 | ✅ YES |
| `enable_property_tests` | True | `stages/code_review_stage/code_review_stage_core.py` | 387 | ✅ YES |

**Adaptive Strategy**:
- MINIMAL profile: Disable expensive features (two_pass, property_tests, thermodynamic)
- BALANCED profile: Enable core features, disable experimental
- AGGRESSIVE profile: Enable all features for maximum quality
- CONSERVATIVE profile: Enable all validation, disable experimental

### Skip Flags

| Parameter | Default | File | Line | Adaptive? |
|-----------|---------|------|------|-----------|
| `skip_sprint_planning` | False/True | `adaptive_config_generator.py` | 194, 223, 253, 279 | ✅ YES |
| `skip_project_analysis` | False/True | `adaptive_config_generator.py` | 195, 224, 254, 280 | ✅ YES |
| `skip_arbitration` | False/True | `adaptive_config_generator.py` | 196, 225, 255, 281 | ✅ YES |
| `skip_tests` | False | `build_manager_base.py` | 183 | ⚠️ MAYBE |

**Adaptive Strategy**:
- Simple tasks: Skip planning, analysis, arbitration
- Medium tasks: Skip planning and arbitration
- Complex tasks: Skip nothing

---

## 12. Rate Limiting Parameters

| Parameter | Default | File | Line | Adaptive? |
|-----------|---------|------|------|-----------|
| `limit` | 3-100 | Various | - | ✅ YES |
| `window_seconds` | 5-60 | Various | - | ✅ YES |
| `failure_threshold` | 3-5 | `protected/` circuits | - | ✅ YES |
| `success_threshold` | 2-3 | `protected/` circuits | - | ✅ YES |

---

## 13. Temperature Scheduling (Advanced)

| Parameter | Default | File | Line | Adaptive? |
|-----------|---------|------|------|-----------|
| `initial_temperature` | 1.0 | `advanced_pipeline/pipeline_config.py` | 71 | ✅ YES |
| `final_temperature` | 0.1 | `advanced_pipeline/pipeline_config.py` | 72 | ✅ YES |

---

## Implementation Plan

### Phase 1: Hydra Config Structure (Week 1)
1. Create comprehensive Hydra config with all parameters
2. Organize into logical sections (llm, timeouts, retry, validation, etc.)
3. Define profile templates (minimal, balanced, aggressive, conservative)

### Phase 2: Code Refactoring (Week 2-3)
1. Replace hardcoded values with `cfg.get()` calls
2. Add parameter injection through context
3. Test each module independently

### Phase 3: Adaptive Selection (Week 4)
1. Enhance `adaptive_config_generator.py` to select optimal values
2. Add platform-aware tuning (CPU, memory, disk)
3. Add task-aware tuning (complexity, size)

### Phase 4: Validation & Tuning (Week 5)
1. A/B test different profiles on real tasks
2. Collect metrics (duration, quality, cost)
3. Tune parameters based on empirical results

---

## Priority Matrix

### High Priority (Immediate Impact)
- ✅ LLM temperature (directly affects quality)
- ✅ max_tokens (affects cost)
- ✅ max_parallel_developers (affects speed)
- ✅ timeout values (prevents hangs)
- ✅ skip flags (affects speed dramatically)

### Medium Priority (Good to Have)
- ✅ Retry parameters (reliability)
- ✅ Batch sizes (throughput)
- ✅ Complexity thresholds (routing accuracy)
- ✅ Cache sizes (performance)

### Low Priority (Nice to Have)
- ⚠️ Window sizes (metrics collection)
- ⚠️ Backup counts (operational)
- ⚠️ Time windows (analytics)

---

## Example Hydra Config Structure

```yaml
# config/config.yaml

# LLM Configuration
llm:
  temperature: 0.3
  max_tokens: 2000
  top_k: 5

# Timeout Configuration (seconds)
timeouts:
  build: 600
  test: 300
  redis_socket: 5
  dependency_check: 300

# Retry Configuration
retry:
  max_retries: 2
  initial_delay: 2.0
  max_delay: 60.0
  backoff_multiplier: 2.0

# Parallelism Configuration
parallelism:
  max_parallel_developers: 3
  max_workers: 4
  thread_pool_size: 8
  prefetch_count: 1

# Batch Configuration
batch:
  default_size: 100
  rag_query_size: 50

# Complexity Thresholds
complexity:
  low_threshold: 50
  medium_threshold: 200
  high_threshold: 500
  max_cyclomatic: 10

# Validation Configuration
validation:
  pass_threshold: 0.8
  confidence_threshold: 0.7
  min_similarity: 0.3
  enable_type_checking: true
  enable_linting: true
  enable_complexity_check: true

# Memory Configuration (MB/GB)
memory:
  per_agent_gb: 1.0
  sandbox_max_mb: 512
  logger_max_mb: 100

# Cache Configuration
cache:
  lru_maxsize: 256
  plan_cache_size: 100
  query_cache_size: 1000
  ttl_seconds: 3600

# Feature Flags
features:
  enable_llm_analysis: true
  enable_rag_validation: true
  enable_self_critique: true
  enable_dynamic_pipeline: true
  enable_two_pass: false
  enable_thermodynamic: true
  enable_property_tests: true

# Skip Flags (Stage Optimization)
skip:
  sprint_planning: false
  project_analysis: false
  arbitration: false

# Rate Limiting
rate_limiting:
  default_limit: 100
  window_seconds: 60
  failure_threshold: 5
  success_threshold: 2
```

---

## Adaptive Profile Examples

### MINIMAL Profile
```yaml
profile: minimal
llm:
  temperature: 0.1
  max_tokens: 1000
parallelism:
  max_parallel_developers: 1
  max_workers: 2
skip:
  sprint_planning: true
  project_analysis: true
  arbitration: true
features:
  enable_two_pass: false
  enable_property_tests: false
validation:
  pass_threshold: 0.6
```

### BALANCED Profile
```yaml
profile: balanced
llm:
  temperature: 0.3
  max_tokens: 2000
parallelism:
  max_parallel_developers: 2
  max_workers: 4
skip:
  sprint_planning: false
  project_analysis: false
  arbitration: false
features:
  enable_two_pass: false
  enable_property_tests: true
validation:
  pass_threshold: 0.7
```

### AGGRESSIVE Profile
```yaml
profile: aggressive
llm:
  temperature: 0.5
  max_tokens: 4000
parallelism:
  max_parallel_developers: 3
  max_workers: 8
skip:
  sprint_planning: false
  project_analysis: false
  arbitration: false
features:
  enable_two_pass: true
  enable_property_tests: true
validation:
  pass_threshold: 0.9
```

---

## Next Steps

1. **Review this audit** with stakeholders
2. **Prioritize parameters** based on impact
3. **Create Hydra config templates** for each profile
4. **Refactor code** to use config instead of hardcoded values
5. **Implement adaptive selection** in `adaptive_config_generator.py`
6. **Validate and tune** with real-world tasks
7. **Monitor metrics** and iterate

---

## Metrics to Track

After implementation, track these metrics for each profile:
- ⏱️ Average pipeline duration
- 💰 Average cost (LLM tokens)
- ✅ Success rate
- 🐛 Bug detection rate
- 🔄 Retry frequency
- 💾 Memory usage
- 🖥️ CPU utilization

Use these metrics to continuously optimize parameter values.
