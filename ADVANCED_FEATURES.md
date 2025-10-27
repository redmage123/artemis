# Artemis Advanced Features Documentation

**Version:** 1.0
**Date:** October 26, 2025
**Last Updated:** October 26, 2025

---

## Table of Contents

1. [Overview](#overview)
2. [Dynamic Pipelines](#dynamic-pipelines)
3. [Two-Pass Pipelines](#two-pass-pipelines)
4. [Thermodynamic Computing](#thermodynamic-computing)
5. [Integration Guide](#integration-guide)
6. [Architecture Diagrams](#architecture-diagrams)
7. [Troubleshooting](#troubleshooting)
8. [API Reference](#api-reference)

---

## Overview

Artemis includes three advanced features that enable adaptive, intelligent, and probabilistic pipeline execution:

1. **Dynamic Pipelines**: Runtime-configurable pipelines that adapt to project complexity, resource constraints, and execution conditions
2. **Two-Pass Pipelines**: Fast analysis followed by refined execution with learning and rollback capabilities
3. **Thermodynamic Computing**: Probabilistic reasoning inspired by statistical thermodynamics for uncertainty quantification

These features are designed to work independently or together, providing flexibility in how you execute and optimize your development workflows.

### Key Benefits

- **Adaptability**: Pipelines adjust to varying project needs automatically
- **Efficiency**: Two-pass approach provides fast feedback while avoiding wasted compute
- **Intelligence**: Bayesian learning improves predictions over time
- **Reliability**: Built-in rollback and error handling maintain system stability
- **Observability**: Comprehensive event emission for monitoring and metrics

---

## Dynamic Pipelines

### What It Is and Why

Dynamic Pipelines allow runtime construction and modification of pipeline execution. Unlike traditional static pipelines that always execute the same stages in the same order, Dynamic Pipelines intelligently select and order stages based on:

- **Project Complexity**: Simple projects skip expensive validation; complex projects include all quality gates
- **Resource Constraints**: Limited CPU/memory environments skip resource-intensive stages
- **Manual Control**: Developers can explicitly select which stages to run
- **Runtime Conditions**: Stages can be added, removed, or reordered during execution

**Why it's needed**: Traditional static pipelines waste time on unnecessary stages for simple projects and lack flexibility for varying requirements. Dynamic Pipelines optimize execution time while maintaining quality.

### Design Patterns Used

1. **Strategy Pattern**: Different stage selection strategies (complexity-based, resource-based, manual)
2. **Builder Pattern**: Fluent API for pipeline construction with validation
3. **Chain of Responsibility**: Stage execution with skip/retry/fallback logic
4. **Observer Pattern**: Event broadcasting for all pipeline operations
5. **State Pattern**: Pipeline lifecycle state management (CREATED → BUILDING → READY → RUNNING → COMPLETED/FAILED)
6. **Factory Pattern**: Convenience factory for common pipeline configurations

### Usage Examples

#### Basic Sequential Pipeline

```python
from dynamic_pipeline import DynamicPipelineBuilder, DynamicPipelineFactory
from pipeline_observer import PipelineObservable

# Create observable for event tracking
observable = PipelineObservable(verbose=True)

# Create simple sequential pipeline
pipeline = DynamicPipelineFactory.create_simple_pipeline(
    name="feature-123",
    stages=[requirements_stage, development_stage, testing_stage],
    observable=observable
)

# Execute
result = pipeline.execute(card_id="TASK-123")
```

#### Adaptive Pipeline with Complexity-Based Selection

```python
from dynamic_pipeline import (
    DynamicPipelineBuilder,
    ComplexityBasedSelector,
    ProjectComplexity
)

# Build adaptive pipeline
pipeline = (DynamicPipelineBuilder()
    .with_name("adaptive-pipeline")
    .add_stages([
        requirements_stage,
        architecture_stage,
        development_stage,
        code_review_stage,
        security_stage,
        performance_stage,
        validation_stage
    ])
    .with_strategy(ComplexityBasedSelector())
    .with_context({"complexity": ProjectComplexity.MODERATE})
    .build())

# Execute - only stages appropriate for MODERATE complexity will run
result = pipeline.execute(card_id="TASK-456")
```

#### Resource-Constrained Pipeline

```python
from dynamic_pipeline import ResourceBasedSelector

# Select stages based on available resources
pipeline = (DynamicPipelineBuilder()
    .with_name("resource-constrained")
    .add_stages(all_stages)
    .with_strategy(ResourceBasedSelector())
    .with_context({
        "cpu_cores": 2,        # Low CPU
        "memory_gb": 4,        # Low memory
        "time_budget_minutes": 30  # Limited time
    })
    .build())

# Only critical stages will execute
result = pipeline.execute(card_id="TASK-789")
```

#### Parallel Execution Pipeline

```python
# Create pipeline with parallel execution
pipeline = DynamicPipelineFactory.create_parallel_pipeline(
    name="parallel-execution",
    stages=all_stages,
    max_workers=4,
    observable=observable
)

# Stages with no dependencies execute concurrently
result = pipeline.execute(card_id="TASK-999")
```

#### Manual Stage Selection

```python
from dynamic_pipeline import ManualSelector

# Explicitly select which stages to run
pipeline = (DynamicPipelineBuilder()
    .with_name("custom-pipeline")
    .add_stages(all_stages)
    .with_strategy(ManualSelector([
        "requirements",
        "development",
        "unit_tests"
    ]))
    .build())

# Only selected stages execute
result = pipeline.execute(card_id="TASK-111")
```

#### Runtime Stage Modification

```python
# Add stage at runtime
pipeline.add_stage_runtime(new_security_stage)

# Remove stage at runtime
pipeline.remove_stage_runtime("performance_tests")

# Pause and resume
pipeline.pause()
# ... do other work ...
pipeline.resume()
```

### Configuration Options

#### Retry Policy

```python
from dynamic_pipeline import RetryPolicy

retry_policy = RetryPolicy(
    max_retries=3,
    retryable_exceptions={NetworkException, RateLimitException},
    backoff_multiplier=2.0,
    initial_delay=1.0
)

pipeline = (DynamicPipelineBuilder()
    .with_name("resilient-pipeline")
    .add_stages(stages)
    .with_retry_policy(retry_policy)
    .build())
```

#### Complexity Levels

| Complexity | LOC Range | Dependencies | Stages Included |
|------------|-----------|--------------|-----------------|
| SIMPLE | <100 | None/Few | Requirements, Development, Basic Tests |
| MODERATE | <1000 | Some | + Code Review, Integration Tests |
| COMPLEX | >1000 | Many | + Architecture, Performance, Security |
| ENTERPRISE | >10K | Extensive | All stages including compliance |

#### Resource Profiles

| Profile | CPU Cores | Memory (GB) | Time (min) | Stages |
|---------|-----------|-------------|------------|--------|
| LOW | ≤2 | ≤4 | ≤30 | Critical only |
| MEDIUM | 4 | 8 | 60 | Skip expensive tests |
| HIGH | ≥8 | ≥16 | ≥120 | All stages |

### Performance Characteristics

- **Parallel Execution**: Reduces pipeline duration by 20-30% when stages are independent
- **Stage Caching**: Avoids redundant work by caching successful stage results
- **Dependency Resolution**: O(1) lookups using set-based tracking
- **Strategy Selection**: O(1) lookup via dispatch tables (no if/elif chains)

**Memory Usage**: Moderate (maintains stage results cache and execution context)

**Thread Safety**: Not thread-safe (assumes single-threaded orchestrator). Parallel stage execution uses ThreadPoolExecutor with proper locking.

---

## Two-Pass Pipelines

### What It Is and Why

Two-Pass Pipelines execute in two phases:

1. **First Pass (Fast Analysis)**: Quick validation and planning (seconds, not minutes)
2. **Second Pass (Refined Execution)**: Full implementation using first pass insights

**Why it's needed**:
- **Fast Feedback**: Identify fatal flaws in seconds instead of minutes
- **Resource Efficiency**: Don't waste expensive compute on bad approaches
- **Learning**: Second pass benefits from first pass discoveries
- **Rollback Safety**: Can revert to first pass if second pass degrades quality

This is analogous to how humans work: quick sketch → detailed implementation.

### Design Patterns Used

1. **Template Method Pattern**: BasePipelinePass defines pass structure
2. **Strategy Pattern**: FirstPassStrategy vs SecondPassStrategy for pass-specific behavior
3. **Memento Pattern**: PassMemento captures state between passes
4. **Observer Pattern**: Event broadcasting for monitoring
5. **Decorator Pattern**: @wrap_exception for error handling
6. **Command Pattern**: Pass operations as commands with undo

### Usage Examples

#### Basic Two-Pass Execution

```python
from two_pass_pipeline import (
    TwoPassPipelineFactory,
    FirstPassStrategy,
    SecondPassStrategy
)

# Create default two-pass pipeline
pipeline = TwoPassPipelineFactory.create_default_pipeline(
    observable=observable,
    verbose=True
)

# Execute both passes
context = {
    "inputs": {"requirements": "Build REST API"},
    "config": {"analysis_type": "validation"},
    "card_id": "TASK-123"
}

result = pipeline.execute(context)

# result.pass_name will be "FirstPass" if rolled back, "SecondPass" if successful
```

#### Custom Pass Strategies

```python
# Create custom first pass
class QuickSyntaxCheck(FirstPassStrategy):
    def _analyze(self, inputs, config):
        # Quick syntax validation only
        return {
            "syntax_valid": True,
            "imports_valid": True,
            "quick_checks": ["syntax", "imports"]
        }

# Create custom second pass
class DeepSemanticAnalysis(SecondPassStrategy):
    def _implement(self, inputs, config, learnings, insights):
        # Full semantic analysis with context from first pass
        return {
            "semantic_valid": True,
            "type_safety": True,
            "learnings_applied": len(learnings),
            "refinements": []
        }

# Build pipeline with custom strategies
pipeline = TwoPassPipeline(
    first_pass_strategy=QuickSyntaxCheck(observable),
    second_pass_strategy=DeepSemanticAnalysis(observable),
    auto_rollback=True,
    rollback_threshold=-0.1
)
```

#### Disable Auto-Rollback

```python
# Create pipeline that always keeps second pass
pipeline = TwoPassPipelineFactory.create_no_rollback_pipeline(
    observable=observable
)

# Second pass result is always returned, even if quality degraded
result = pipeline.execute(context)
```

### Learning Mechanisms

#### First Pass Learnings

First pass extracts insights for second pass:

```python
# Example learnings extracted from first pass
learnings = [
    "Validated 10 inputs successfully",
    "Found 2 validation failures to address",
    "Schema validation passed for 8/10 fields"
]

# These become context for second pass
insights = {
    "analysis_type": "fast",
    "inputs_count": 10,
    "validation_passed": True
}
```

#### Second Pass Refinements

Second pass applies first pass learnings:

```python
# Second pass uses learnings to improve implementation
def _apply_learnings_to_implementation(self, inputs, learnings, insights):
    refinements = []

    for learning in learnings:
        if "validation" in learning.lower():
            refinements.append({
                "type": "validation_improvement",
                "learning": learning
            })

    return refinements
```

#### Quality Tracking

Passes are compared via quality scores:

```python
# First pass quality: 0.75 (quick analysis)
# Second pass quality: 0.85 (thorough implementation)
# Quality delta: +0.10 (improvement)

delta = PassDelta(first_pass=first_result, second_pass=second_result)

print(f"Quality improved: {delta.quality_improved}")  # True
print(f"Quality delta: {delta.quality_delta}")  # +0.10
print(f"New learnings: {delta.new_learnings}")  # List of new insights
```

### Rollback Scenarios

#### Automatic Rollback

```python
# Rollback triggers when quality degrades significantly
pipeline = TwoPassPipeline(
    first_pass_strategy=FirstPassStrategy(observable),
    second_pass_strategy=SecondPassStrategy(observable),
    auto_rollback=True,
    rollback_threshold=-0.1  # Rollback if quality drops by 10%+
)

# Scenario: Second pass quality = 0.60, First pass quality = 0.75
# Quality delta: -0.15 (degradation of 15%)
# Automatic rollback to first pass result
```

#### Manual Rollback

```python
# Manually trigger rollback to first pass
memento = pipeline.first_pass_memento
restored_state = pipeline.rollback_manager.rollback_to_memento(
    memento,
    reason="Manual rollback requested by user"
)
```

#### Rollback History

```python
# Check rollback history
history = pipeline.get_rollback_history()

for entry in history:
    print(f"Rollback at {entry['timestamp']}")
    print(f"  Reason: {entry['reason']}")
    print(f"  Quality score: {entry['quality_score']}")
```

### When to Use Two-Pass

**Use Two-Pass When:**
- Running expensive operations (LLM calls, complex computations)
- Need fast feedback before full execution
- Quality can be incrementally improved
- Rollback safety is important
- Learning from quick analysis helps full implementation

**Avoid Two-Pass When:**
- Stages are already fast (<5 seconds)
- No incremental learning possible
- Rollback is not needed
- Overhead of two passes exceeds benefit

### Event Emission

```python
# Two-pass emits detailed events for monitoring
from two_pass_pipeline import TwoPassEventType

# First pass events
TwoPassEventType.FIRST_PASS_STARTED
TwoPassEventType.FIRST_PASS_COMPLETED
TwoPassEventType.FIRST_PASS_FAILED

# Second pass events
TwoPassEventType.SECOND_PASS_STARTED
TwoPassEventType.SECOND_PASS_COMPLETED
TwoPassEventType.PASS_QUALITY_IMPROVED

# Memento events
TwoPassEventType.MEMENTO_CREATED
TwoPassEventType.MEMENTO_APPLIED

# Rollback events
TwoPassEventType.ROLLBACK_INITIATED
TwoPassEventType.ROLLBACK_COMPLETED

# Learning events
TwoPassEventType.LEARNING_CAPTURED
TwoPassEventType.INCREMENTAL_IMPROVEMENT
```

---

## Thermodynamic Computing

### What It Is and Why (Software Implementation)

Thermodynamic Computing applies concepts from statistical thermodynamics to software engineering, specifically for **uncertainty quantification** and **probabilistic decision making**.

**Key Analogy:**

| Classical Computing | Thermodynamic Computing |
|---------------------|------------------------|
| Deterministic | Probabilistic |
| Single solution | Ensemble of solutions |
| Binary (works/fails) | Confidence distribution |
| Fixed strategy | Temperature-based exploration |
| No learning | Bayesian prior updates |
| Ignore uncertainty | Quantify & propagate uncertainty |

**Why it's needed**:
- LLMs are inherently probabilistic - we should measure confidence
- Multiple solutions often better than single solution (wisdom of crowds)
- Uncertainty quantification enables better risk assessment
- Bayesian learning improves estimates over time
- Temperature-based sampling balances exploration vs exploitation

**Software Implementation**: This is NOT physical thermodynamics or quantum computing. It's a software framework inspired by thermodynamic concepts (entropy, ensembles, temperature) applied to probabilistic reasoning about code generation, effort estimation, and decision making.

### Mathematical Foundations

#### Bayesian Inference

**Bayes' Theorem**: P(θ|D) = P(D|θ)P(θ) / P(D)

For binary outcomes (success/failure), uses Beta distribution:
- **Prior**: Beta(α, β) where α=successes+1, β=failures+1
- **Posterior mean**: α / (α + β)
- **Posterior variance**: αβ / [(α+β)²(α+β+1)]

**Example**:
```
Prior: Beta(1, 1) = Uniform[0,1] (no knowledge)
Observe: 8 successes, 2 failures
Posterior: Beta(9, 3)
Confidence: 9/(9+3) = 0.75 (75%)
```

#### Monte Carlo Simulation

**Expectation**: E[X] ≈ (1/N)Σx_i

Run N simulations, aggregate results:
```python
confidence = successes / N
variance = p(1-p) / N
standard_error = sqrt(variance)
```

#### Confidence Intervals

**95% CI**: μ ± 1.96*σ/√n

Provides bounds on true value:
```python
lower, upper = score.confidence_interval(z_score=1.96)
# "95% confident true value is between [lower, upper]"
```

#### Entropy

**Binary Entropy**: H(p) = -p*log(p) - (1-p)*log(1-p)

Quantifies uncertainty:
- p=0.5: Maximum entropy (1.0) - most uncertain
- p=0 or p=1: Minimum entropy (0.0) - certain
- High entropy → need more data

#### Temperature Sampling

**Boltzmann Distribution**: P(x) ∝ exp(-E(x)/T)

Controls exploration vs exploitation:
- High T → random (explore)
- Low T → greedy (exploit)

```python
# Temperature-based sampling
P(option_i) = exp(score_i / T) / Σexp(score_j / T)
```

#### Ensemble Averaging

**Variance Reduction**: Var(average) = σ²/N

Multiple models have lower variance than single model:
```
Single model: variance = σ²
Ensemble (N models): variance = σ²/N
```

### Uncertainty Quantification Examples

#### Example 1: Quantify LLM Output Confidence

```python
from thermodynamic_computing import ThermodynamicComputing

# Initialize
tc = ThermodynamicComputing(observable=pipeline_observable)

# Get LLM output
llm_output = llm_client.call("Generate REST API code")

# Quantify uncertainty using Bayesian strategy
score = tc.quantify_uncertainty(
    prediction=llm_output,
    context={
        "stage": "development",
        "card_id": "TASK-123",
        "prediction_type": "code_quality"
    },
    strategy="bayesian"
)

# Check confidence
print(f"Confidence: {score.confidence:.2%}")  # 85%
print(f"Variance: {score.variance:.4f}")      # 0.0234
print(f"Entropy: {score.entropy:.4f}")        # 0.456

# Get confidence interval
lower, upper = score.confidence_interval(z_score=1.96)
print(f"95% CI: [{lower:.2%}, {upper:.2%}]")  # [78%, 92%]

# Decision based on confidence
if score.confidence < 0.7:
    request_human_review(llm_output, score)
else:
    proceed_with_output(llm_output)
```

#### Example 2: Monte Carlo Effort Estimation

```python
import random

def estimate_effort_probabilistically(task_description):
    # Define simulator that samples from effort distribution
    def effort_simulator(prediction, context):
        # Sample duration from normal distribution
        mean_duration = 5  # days (historical average)
        std_duration = 2   # days (historical std dev)
        sample = random.normalvariate(mean_duration, std_duration)

        # Return if sample close to prediction
        return abs(sample - prediction) < 1.0

    # Run Monte Carlo estimation (1000 simulations)
    score = tc.quantify_uncertainty(
        prediction=5,  # Predicted 5 days
        context={
            "simulator_fn": effort_simulator,
            "n_simulations": 1000,
            "stage": "estimation"
        },
        strategy="monte_carlo"
    )

    # Get probabilistic estimate
    lower, upper = score.confidence_interval(z_score=1.96)

    return {
        "mean_estimate": 5,
        "confidence": score.confidence,
        "95_percent_ci": (lower, upper),
        "message": f"Estimated effort: 5 days (95% CI: [{lower:.1f}, {upper:.1f}])"
    }

result = estimate_effort_probabilistically("Build user authentication")
print(result["message"])
# Output: "Estimated effort: 5 days (95% CI: [3.2, 6.8])"
```

#### Example 3: Ensemble Code Generation

```python
def generate_code_with_ensemble(requirement):
    # Define multiple code generators
    generators = [
        lambda req, ctx: generate_with_gpt4(req),
        lambda req, ctx: generate_with_claude(req),
        lambda req, ctx: generate_with_codex(req)
    ]

    # Create ensemble strategy
    from thermodynamic_computing import EnsembleUncertaintyStrategy

    ensemble = EnsembleUncertaintyStrategy(
        model_generators=generators,
        observable=pipeline_observable
    )

    # Register with thermodynamic computing
    tc._strategies["code_ensemble"] = ensemble

    # Generate code with all models
    code_options = [gen(requirement, {}) for gen in generators]

    # Get uncertainty score (how much do models agree?)
    score = tc.quantify_uncertainty(
        prediction=code_options[0],  # Reference
        context={
            "stage": "development",
            "comparison_type": "code_similarity"
        },
        strategy="code_ensemble"
    )

    # High confidence (models agree) → use any option
    # Low confidence (models disagree) → request human selection
    if score.confidence > 0.7:
        print(f"Models agree ({score.confidence:.0%} consensus)")
        return code_options[0]
    else:
        print(f"Models disagree ({score.confidence:.0%} consensus)")
        return request_human_code_selection(code_options, score)
```

### Bayesian Learning Examples

#### Example 4: Learn from Sprint Outcomes

```python
def process_sprint_retrospective(task_id):
    # Get prediction from planning
    prediction = get_planning_estimate(task_id)  # e.g., "5 days"

    # Get actual outcome
    actual = get_actual_duration(task_id)  # e.g., "7 days"

    # Update Bayesian priors
    tc.learn_from_outcome(
        prediction=prediction,
        actual=actual,
        context={
            "stage": "estimation",
            "prediction_type": "effort",
            "comparison_type": "threshold",
            "threshold_percent": 0.2  # Within 20% is "correct"
        },
        strategy="bayesian"
    )

    # Future estimates will use updated priors
    # If we consistently overestimate, priors adjust downward

# Process multiple sprints
for task_id in completed_tasks:
    process_sprint_retrospective(task_id)

# Check learned priors
bayesian = tc.get_strategy("bayesian")
priors = bayesian.get_priors()

print("Learned priors:")
for (stage, pred_type), params in priors.items():
    alpha, beta = params["alpha"], params["beta"]
    confidence = alpha / (alpha + beta)
    print(f"  {stage}/{pred_type}: {confidence:.2%} (α={alpha:.1f}, β={beta:.1f})")

# Output:
# Learned priors:
#   estimation/effort: 68% (α=15.0, β=7.0)
#   estimation/complexity: 75% (α=9.0, β=3.0)
```

### Probabilistic Planning Examples

#### Example 5: Temperature-Based Developer Selection

```python
def select_developer_with_annealing(iteration, total_iterations):
    developers = ["dev-a", "dev-b", "dev-c"]

    # Scores based on past performance
    scores = [0.85, 0.75, 0.65]

    # Early iterations (high temp): explore all developers
    # Late iterations (low temp): exploit best developer
    selected = tc.sample_with_temperature(
        options=developers,
        scores=scores,
        step=iteration,
        max_steps=total_iterations
    )

    return selected

# Iteration 1/10 (high temp=0.9): Random selection, all developers likely
dev = select_developer_with_annealing(1, 10)

# Iteration 10/10 (low temp=0.1): Greedy selection, best developer very likely
dev = select_developer_with_annealing(10, 10)
```

#### Example 6: Risk-Aware Architecture Decisions

```python
from thermodynamic_computing import assess_risk

def make_architecture_decision(options):
    scores = []

    # Evaluate each option
    for option in options:
        score = tc.quantify_uncertainty(
            prediction=option,
            context={"stage": "architecture"},
            strategy="bayesian"
        )
        scores.append(score)

    # Assess risk for each option
    risks = [assess_risk(score) for score in scores]

    # Filter out high-risk options
    safe_options = [
        (opt, score) for opt, score, risk in zip(options, scores, risks)
        if risk["risk_level"] != "high"
    ]

    if safe_options:
        # Select best safe option
        best_option, best_score = max(safe_options, key=lambda x: x[1].confidence)
        print(f"Selected: {best_option} (confidence={best_score.confidence:.2%})")
        return best_option
    else:
        # All options high-risk - escalate
        print("All options are high-risk - escalating to human")
        return escalate_to_human(options, risks)

# Example
architectures = ["microservices", "monolith", "serverless"]
selected = make_architecture_decision(architectures)
```

### Integration with Pipeline

#### Example 7: Add Confidence to Every LLM Call

```python
class ConfidenceTrackingAgent:
    def __init__(self, tc: ThermodynamicComputing):
        self.tc = tc
        self.llm_client = LLMClient()

    def call_llm_with_confidence(self, prompt, context):
        # Get LLM response
        response = self.llm_client.call(prompt)

        # Quantify uncertainty
        score = self.tc.quantify_uncertainty(
            prediction=response,
            context=context,
            strategy="bayesian"
        )

        # Return response with confidence
        return {
            "response": response,
            "confidence": score.confidence,
            "confidence_interval": score.confidence_interval(),
            "entropy": score.entropy,
            "should_review": score.confidence < 0.7
        }

# Use in pipeline
agent = ConfidenceTrackingAgent(tc)

result = agent.call_llm_with_confidence(
    prompt="Generate unit tests for...",
    context={"stage": "testing", "card_id": "TASK-456"}
)

if result["should_review"]:
    print(f"Low confidence ({result['confidence']:.0%}) - requesting review")
    request_human_review(result)
else:
    print(f"High confidence ({result['confidence']:.0%}) - proceeding")
    proceed_with_response(result)
```

### Temperature Schedules

```python
from thermodynamic_computing import TemperatureScheduler

# Create scheduler
scheduler = TemperatureScheduler(
    initial_temp=1.0,   # High exploration
    final_temp=0.1,     # Low exploration
    schedule="exponential"  # or "linear", "inverse", "step"
)

# Use in iterative process
for step in range(max_steps):
    # Get temperature for current step
    temp = scheduler.get_temperature(step, max_steps)

    # Sample with current temperature
    choice = scheduler.sample_with_temperature(
        options=["option_a", "option_b", "option_c"],
        scores=[0.8, 0.6, 0.4],
        temperature=temp
    )

    print(f"Step {step}: temp={temp:.2f}, selected={choice}")

# Output:
# Step 0: temp=1.00, selected=option_b  (random)
# Step 50: temp=0.31, selected=option_a (starting to prefer best)
# Step 99: temp=0.10, selected=option_a (greedy, always best)
```

---

## Integration Guide

### How to Enable Features

#### Enable Dynamic Pipelines

```python
from dynamic_pipeline import DynamicPipelineBuilder, ComplexityBasedSelector
from pipeline_observer import PipelineObservable

# 1. Create observable
observable = PipelineObservable(verbose=True)

# 2. Attach observers for monitoring
from pipeline_observer import LoggingObserver, MetricsObserver

observable.attach(LoggingObserver())
observable.attach(MetricsObserver())

# 3. Build dynamic pipeline
pipeline = (DynamicPipelineBuilder()
    .with_name("my-pipeline")
    .add_stages(all_stages)
    .with_strategy(ComplexityBasedSelector())
    .with_context({"complexity": ProjectComplexity.MODERATE})
    .with_observable(observable)
    .with_parallelism(enabled=True, max_workers=4)
    .build())

# 4. Execute
result = pipeline.execute(card_id="TASK-123")
```

#### Enable Two-Pass Pipelines

```python
from two_pass_pipeline import TwoPassPipelineFactory

# 1. Create two-pass pipeline
pipeline = TwoPassPipelineFactory.create_default_pipeline(
    observable=observable,
    verbose=True
)

# 2. Prepare context
context = {
    "inputs": {"requirements": "..."},
    "config": {"analysis_type": "validation"},
    "card_id": "TASK-456"
}

# 3. Execute both passes
result = pipeline.execute(context)

# 4. Check if rolled back
if result.pass_name == "FirstPass":
    print("Second pass degraded quality - rolled back to first pass")
else:
    print("Second pass succeeded")
```

#### Enable Thermodynamic Computing

```python
from thermodynamic_computing import ThermodynamicComputing

# 1. Initialize thermodynamic computing
tc = ThermodynamicComputing(
    observable=observable,
    default_strategy="bayesian"
)

# 2. Use for uncertainty quantification
score = tc.quantify_uncertainty(
    prediction=llm_output,
    context={"stage": "development"},
    strategy="bayesian"
)

# 3. Learn from outcomes
tc.learn_from_outcome(
    prediction=estimated_effort,
    actual=actual_effort,
    context={"stage": "estimation"}
)

# 4. Use temperature-based sampling
selected = tc.sample_with_temperature(
    options=developers,
    scores=performance_scores,
    temperature=0.5
)
```

### Configuration Examples

#### Hydra Configuration (config.yaml)

```yaml
# Dynamic Pipeline Configuration
dynamic_pipeline:
  enabled: true
  default_strategy: "complexity_based"  # or "resource_based", "manual"
  parallel_execution: true
  max_workers: 4
  retry_policy:
    max_retries: 3
    initial_delay: 1.0
    backoff_multiplier: 2.0

# Two-Pass Pipeline Configuration
two_pass_pipeline:
  enabled: true
  auto_rollback: true
  rollback_threshold: -0.1  # Rollback if quality drops by 10%+

# Thermodynamic Computing Configuration
thermodynamic_computing:
  enabled: true
  default_strategy: "bayesian"  # or "monte_carlo", "ensemble"
  temperature_schedule: "exponential"
  initial_temp: 1.0
  final_temp: 0.1

# Observer Configuration
observers:
  logging: true
  metrics: true
  state_tracking: true
  notifications: false
```

### Combining Features

#### Example: Dynamic + Two-Pass + Thermodynamic

```python
# 1. Create thermodynamic computing for uncertainty
tc = ThermodynamicComputing(observable=observable)

# 2. Create two-pass strategies with confidence tracking
class ConfidenceFirstPass(FirstPassStrategy):
    def execute(self, context):
        result = super().execute(context)

        # Add confidence score
        score = tc.quantify_uncertainty(
            prediction=result,
            context=context,
            strategy="bayesian"
        )

        result.confidence = score.confidence
        return result

# 3. Create dynamic pipeline with two-pass stages
dynamic_pipeline = (DynamicPipelineBuilder()
    .with_name("advanced-pipeline")
    .add_stages([
        TwoPassStage(ConfidenceFirstPass(), SecondPassStrategy()),
        # ... other stages
    ])
    .with_strategy(ComplexityBasedSelector())
    .with_context({"complexity": ProjectComplexity.COMPLEX})
    .with_observable(observable)
    .build())

# 4. Execute with full feature integration
result = dynamic_pipeline.execute(card_id="TASK-789")
```

### Observer Integration

#### Custom Observer for Confidence Tracking

```python
from pipeline_observer import PipelineObserver

class ConfidenceTrackingObserver(PipelineObserver):
    def __init__(self):
        self.confidence_history = []

    def on_event(self, event):
        # Track confidence from thermodynamic events
        if "thermodynamic_event" in event.data:
            if event.data.get("confidence"):
                self.confidence_history.append({
                    "timestamp": event.timestamp,
                    "stage": event.stage_name,
                    "confidence": event.data["confidence"],
                    "variance": event.data.get("variance", 0.0)
                })

    def get_average_confidence(self):
        if not self.confidence_history:
            return None

        return sum(h["confidence"] for h in self.confidence_history) / len(self.confidence_history)

# Attach to observable
confidence_observer = ConfidenceTrackingObserver()
observable.attach(confidence_observer)

# After pipeline execution
avg_confidence = confidence_observer.get_average_confidence()
print(f"Average pipeline confidence: {avg_confidence:.2%}")
```

### Performance Tuning

#### Optimize Dynamic Pipeline

```python
# Reduce parallelism for memory-constrained environments
pipeline = (DynamicPipelineBuilder()
    .with_parallelism(enabled=True, max_workers=2)  # Lower from default 4
    .build())

# Use result caching to avoid redundant work
pipeline.clear_cache()  # Clear cache when needed

# Adjust retry policy for faster failure
retry_policy = RetryPolicy(
    max_retries=1,  # Fail fast
    initial_delay=0.5
)
```

#### Optimize Two-Pass Pipeline

```python
# Skip first pass for simple tasks
if task_complexity == "simple":
    # Use single-pass execution
    result = second_pass.execute(context)
else:
    # Use two-pass for complex tasks
    result = pipeline.execute(context)

# Adjust rollback threshold
pipeline = TwoPassPipeline(
    auto_rollback=True,
    rollback_threshold=-0.15  # More lenient (allow 15% degradation)
)
```

#### Optimize Thermodynamic Computing

```python
# Reduce Monte Carlo simulations for faster estimates
tc = ThermodynamicComputing()
score = tc.quantify_uncertainty(
    prediction=estimate,
    context={
        "n_simulations": 100,  # Lower from default 1000
        "simulator_fn": simulator
    },
    strategy="monte_carlo"
)

# Use cached Bayesian priors
bayesian = tc.get_strategy("bayesian")
priors = bayesian.get_priors()
# Save priors to disk
import pickle
with open("learned_priors.pkl", "wb") as f:
    pickle.dump(priors, f)

# Load priors on next run
with open("learned_priors.pkl", "rb") as f:
    priors = pickle.load(f)
    for (stage, pred_type), params in priors.items():
        bayesian.set_prior(stage, pred_type, params["alpha"], params["beta"])
```

---

## Architecture Diagrams

### Component Relationships

```
┌─────────────────────────────────────────────────────────────────┐
│                       Artemis Orchestrator                       │
└───────────┬─────────────────────────────────┬───────────────────┘
            │                                 │
            │                                 │
    ┌───────▼────────┐              ┌────────▼─────────┐
    │ Dynamic        │              │ Two-Pass         │
    │ Pipeline       │              │ Pipeline         │
    └───────┬────────┘              └────────┬─────────┘
            │                                │
            │                                │
    ┌───────▼──────────────────────┬─────────▼─────────┐
    │   Pipeline Observable         │ PassStrategy      │
    │   (Observer Pattern)          │ (Strategy Pattern)│
    └───────┬──────────────────────┴───────────────────┘
            │                                │
            │                                │
    ┌───────▼────────┐              ┌────────▼─────────┐
    │ Observers:     │              │ Pass Components: │
    │ - Logging      │              │ - FirstPass      │
    │ - Metrics      │              │ - SecondPass     │
    │ - State Track  │              │ - Memento        │
    │ - Notification │              │ - Comparator     │
    │ - Confidence   │              │ - Rollback Mgr   │
    └────────────────┘              └──────────────────┘
            │
            │
    ┌───────▼────────────────────────────────────────┐
    │      Thermodynamic Computing                   │
    │  ┌──────────┬──────────┬──────────┬─────────┐ │
    │  │ Bayesian │  Monte   │ Ensemble │  Temp   │ │
    │  │ Strategy │  Carlo   │ Strategy │Scheduler│ │
    │  └──────────┴──────────┴──────────┴─────────┘ │
    └────────────────────────────────────────────────┘
```

### Event Flow

```
┌──────────────┐
│   Pipeline   │
│    Stage     │
└──────┬───────┘
       │ execute()
       │
       ▼
┌──────────────────────────┐
│ Stage Executor           │
│ - Retry logic            │
│ - Error handling         │
└──────┬───────────────────┘
       │ emit_event()
       │
       ▼
┌──────────────────────────┐
│ Pipeline Observable      │
│ - Event broadcasting     │
└──┬───┬───┬───┬───────────┘
   │   │   │   │
   │   │   │   └─────────────────┐
   │   │   │                     │
   ▼   ▼   ▼                     ▼
┌────┐┌────┐┌─────────┐    ┌─────────────┐
│Log ││Metr││State    │    │ Thermodynamic│
│Obsv││Obsv││Tracking │    │ Event        │
└────┘└────┘└─────────┘    │ Listener     │
                            └─────────────┘
                                   │
                                   ▼
                            ┌─────────────┐
                            │ Confidence  │
                            │ Tracking    │
                            └─────────────┘
```

### Data Flow

```
Input Context
     │
     ▼
┌─────────────────┐
│ Stage Selection │  ← Complexity Analysis
│ Strategy        │  ← Resource Constraints
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Selected Stages │
│ [S1, S2, S3...] │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Stage Execution │
│ (Sequential or  │
│  Parallel)      │
└────────┬────────┘
         │
         ├──────────┐
         │          │
         ▼          ▼
    ┌────────┐  ┌────────┐
    │ First  │  │ Second │
    │ Pass   │──│ Pass   │
    └────┬───┘  └───┬────┘
         │          │
         │    ┌─────▼──────┐
         │    │ PassDelta  │
         │    │ Calculation│
         │    └─────┬──────┘
         │          │
         │     Rollback?
         │          │
         │    ┌─────▼──────┐
         └────│   Final    │
              │  Result    │
              └────────────┘
                   │
                   ▼
           ┌───────────────┐
           │  Uncertainty  │
           │ Quantification│
           └───────┬───────┘
                   │
                   ▼
           ┌───────────────┐
           │  Confidence   │
           │    Score      │
           └───────────────┘
```

---

## Troubleshooting

### Common Issues

#### 1. Dynamic Pipeline Not Selecting Expected Stages

**Symptom**: Pipeline runs more/fewer stages than expected

**Diagnosis**:
```python
# Check routing decision
routing = context.get('routing_decision')
print(f"Complexity: {routing.get('complexity')}")
print(f"Selected stages: {routing.get('selected_stages')}")

# Check stage filter
pipeline.logger.log(
    f"Selected {len(pipeline.selected_stages)} stages",
    "INFO"
)
```

**Solutions**:
- Verify complexity classification is correct
- Check if custom strategy is properly configured
- Use ManualSelector for explicit control

#### 2. Two-Pass Always Rolling Back

**Symptom**: Second pass always rolls back to first pass

**Diagnosis**:
```python
# Check quality delta
delta = pipeline.comparator.compare(first_pass, second_pass)
print(f"Quality delta: {delta.quality_delta}")
print(f"Threshold: {pipeline.rollback_threshold}")

# Check quality scores
print(f"First pass: {first_pass.quality_score}")
print(f"Second pass: {second_pass.quality_score}")
```

**Solutions**:
- Adjust rollback threshold: `rollback_threshold=-0.15` (more lenient)
- Improve second pass quality calculation
- Disable auto-rollback for debugging: `auto_rollback=False`

#### 3. Bayesian Confidence Not Learning

**Symptom**: Confidence scores don't improve over time

**Diagnosis**:
```python
# Check priors
bayesian = tc.get_strategy("bayesian")
priors = bayesian.get_priors()

for (stage, pred_type), params in priors.items():
    print(f"{stage}/{pred_type}: α={params['alpha']}, β={params['beta']}")

# Check evidence count
from thermodynamic_computing import BayesianUncertaintyStrategy
evidence_counts = bayesian._evidence_counts
print(f"Evidence counts: {evidence_counts}")
```

**Solutions**:
- Ensure `learn_from_outcome()` is being called
- Verify `comparison_type` is appropriate for prediction type
- Check if threshold is too strict: `threshold_percent=0.3`
- Manually set priors from previous runs

#### 4. Parallel Pipeline Not Faster

**Symptom**: Parallel execution no faster than sequential

**Diagnosis**:
```python
# Check stage grouping
groups = pipeline._group_stages_by_dependencies(stages)
print(f"Execution groups: {len(groups)}")
for i, group in enumerate(groups):
    print(f"  Group {i}: {[s.name for s in group]}")

# Check if stages have dependencies
for stage in stages:
    deps = stage.get_dependencies()
    print(f"{stage.name} depends on: {deps}")
```

**Solutions**:
- Ensure stages declare dependencies correctly
- Increase `max_workers` if stages are truly independent
- Use profiling to identify actual bottlenecks
- Some stages may have sequential dependencies

#### 5. High Memory Usage

**Symptom**: Pipeline consuming excessive memory

**Diagnosis**:
```python
# Check result cache size
print(f"Cached results: {len(pipeline.result_cache)}")

# Check confidence history
print(f"Confidence history entries: {len(tc._confidence_history)}")

# Check observer event storage
metrics_observer = next(o for o in observable._observers if isinstance(o, MetricsObserver))
print(f"Stored events: {len(metrics_observer.metrics['events'])}")
```

**Solutions**:
```python
# Clear caches periodically
pipeline.clear_cache()
tc._confidence_history.clear()

# Limit event storage
class LimitedMetricsObserver(MetricsObserver):
    def on_event(self, event):
        super().on_event(event)
        # Keep only last 1000 events
        if len(self.metrics["events"]) > 1000:
            self.metrics["events"] = self.metrics["events"][-1000:]
```

### Debugging Tips

#### Enable Verbose Logging

```python
# All features support verbose mode
pipeline = DynamicPipelineBuilder().with_verbose(True).build()
two_pass = TwoPassPipeline(verbose=True)
tc = ThermodynamicComputing(verbose=True)

# Attach logging observer
observable.attach(LoggingObserver(verbose=True))
```

#### Check Event Stream

```python
class DebugObserver(PipelineObserver):
    def on_event(self, event):
        print(f"[{event.timestamp}] {event.event_type.value}")
        if event.data:
            print(f"  Data: {event.data}")
        if event.error:
            print(f"  Error: {event.error}")

observable.attach(DebugObserver())
```

#### Inspect State

```python
# Dynamic pipeline state
print(f"Pipeline state: {pipeline.get_state()}")
print(f"Results: {pipeline.get_results()}")
print(f"Context: {pipeline.get_context()}")

# Two-pass state
print(f"Execution history: {pipeline.get_execution_history()}")
print(f"Rollback history: {pipeline.get_rollback_history()}")

# Thermodynamic computing state
print(f"Confidence history: {tc.get_confidence_history()}")
bayesian = tc.get_strategy("bayesian")
print(f"Bayesian priors: {bayesian.get_priors()}")
```

### Performance Optimization

#### Profile Pipeline Execution

```python
import time

class ProfilingObserver(PipelineObserver):
    def __init__(self):
        self.stage_times = {}
        self.stage_starts = {}

    def on_event(self, event):
        if event.event_type == EventType.STAGE_STARTED:
            self.stage_starts[event.stage_name] = time.time()

        elif event.event_type == EventType.STAGE_COMPLETED:
            if event.stage_name in self.stage_starts:
                duration = time.time() - self.stage_starts[event.stage_name]
                self.stage_times[event.stage_name] = duration

    def print_profile(self):
        print("\nStage Execution Times:")
        for stage, duration in sorted(self.stage_times.items(), key=lambda x: x[1], reverse=True):
            print(f"  {stage}: {duration:.2f}s")

profiler = ProfilingObserver()
observable.attach(profiler)
# ... run pipeline ...
profiler.print_profile()
```

#### Optimize Hot Paths

```python
# Cache expensive computations
from functools import lru_cache

@lru_cache(maxsize=100)
def compute_complexity(requirements):
    # Expensive complexity calculation
    return ProjectComplexity.MODERATE

# Use cached version
complexity = compute_complexity(tuple(requirements_list))
```

---

## API Reference

### Dynamic Pipeline Classes

#### `DynamicPipelineBuilder`

Fluent API for constructing dynamic pipelines.

**Methods**:
- `with_name(name: str)` - Set pipeline name
- `add_stage(stage: PipelineStage)` - Add single stage
- `add_stages(stages: List[PipelineStage])` - Add multiple stages
- `with_strategy(strategy: StageSelectionStrategy)` - Set selection strategy
- `with_retry_policy(policy: RetryPolicy)` - Configure retry behavior
- `with_observable(observable: PipelineObservable)` - Set event broadcaster
- `with_parallelism(enabled: bool, max_workers: int = 4)` - Enable parallel execution
- `with_context(context: Dict[str, Any])` - Set initial context
- `build()` - Build and validate pipeline

**Example**:
```python
pipeline = (DynamicPipelineBuilder()
    .with_name("my-pipeline")
    .add_stages([stage1, stage2])
    .with_strategy(ComplexityBasedSelector())
    .build())
```

#### `DynamicPipeline`

Executable dynamic pipeline.

**Methods**:
- `execute(card_id: str)` - Execute pipeline
- `pause()` - Pause execution
- `resume()` - Resume execution
- `add_stage_runtime(stage: PipelineStage)` - Add stage at runtime
- `remove_stage_runtime(stage_name: str)` - Remove stage at runtime
- `get_state()` - Get current state
- `get_results()` - Get execution results
- `get_context()` - Get execution context
- `clear_cache()` - Clear result cache

#### `StageSelectionStrategy` (Abstract)

Base class for stage selection strategies.

**Concrete Implementations**:
- `ComplexityBasedSelector` - Select based on project complexity
- `ResourceBasedSelector` - Select based on available resources
- `ManualSelector` - Explicit stage selection

**Methods**:
- `select_stages(available_stages, context)` - Select stages to execute

#### `ProjectComplexity` (Enum)

- `SIMPLE` - <100 LOC, basic stages
- `MODERATE` - <1000 LOC, includes code review
- `COMPLEX` - >1000 LOC, includes architecture and security
- `ENTERPRISE` - >10K LOC, all stages

#### `PipelineState` (Enum)

- `CREATED` - Pipeline created
- `BUILDING` - Being configured
- `READY` - Ready to execute
- `RUNNING` - Currently executing
- `PAUSED` - Execution paused
- `COMPLETED` - Successfully completed
- `FAILED` - Failed with error
- `CANCELLED` - Cancelled by user

### Two-Pass Pipeline Classes

#### `TwoPassPipeline`

Orchestrates two-pass execution with learning and rollback.

**Constructor**:
```python
TwoPassPipeline(
    first_pass_strategy: PassStrategy,
    second_pass_strategy: PassStrategy,
    observable: Optional[PipelineObservable] = None,
    auto_rollback: bool = True,
    rollback_threshold: float = -0.1,
    verbose: bool = True
)
```

**Methods**:
- `execute(context: Dict[str, Any])` - Execute both passes
- `get_execution_history()` - Get execution history
- `get_rollback_history()` - Get rollback history

**Returns**:
```python
{
    "pass_name": "FirstPass" | "SecondPass",
    "success": bool,
    "artifacts": Dict[str, Any],
    "quality_score": float,
    "execution_time": float,
    "learnings": List[str],
    "insights": Dict[str, Any]
}
```

#### `PassStrategy` (Abstract)

Base class for pass strategies.

**Methods**:
- `execute(context: Dict[str, Any])` - Execute pass
- `get_pass_name()` - Get pass name
- `create_memento(result, state)` - Create state snapshot
- `apply_memento(memento, context)` - Apply previous pass state

**Concrete Implementations**:
- `FirstPassStrategy` - Fast analysis pass
- `SecondPassStrategy` - Refined execution pass

#### `PassResult`

Result of pass execution.

**Fields**:
- `pass_name: str` - Name of pass
- `success: bool` - Execution success
- `artifacts: Dict[str, Any]` - Generated artifacts
- `quality_score: float` - Quality score [0.0, 1.0]
- `execution_time: float` - Execution duration (seconds)
- `learnings: List[str]` - Extracted learnings
- `insights: Dict[str, Any]` - Machine-readable insights
- `errors: List[str]` - Error messages
- `warnings: List[str]` - Warning messages
- `metadata: Dict[str, Any]` - Additional metadata

#### `PassDelta`

Difference between two passes.

**Fields**:
- `first_pass: PassResult`
- `second_pass: PassResult`
- `quality_delta: float` - Quality change (positive = improvement)
- `new_artifacts: List[str]` - Artifacts added in second pass
- `modified_artifacts: List[str]` - Artifacts changed
- `removed_artifacts: List[str]` - Artifacts removed
- `new_learnings: List[str]` - New learnings from second pass
- `quality_improved: bool` - Quality improved flag
- `execution_time_delta: float` - Time difference

#### `PassMemento`

State snapshot for rollback.

**Fields**:
- `pass_name: str`
- `state: Dict[str, Any]` - Pass state
- `artifacts: Dict[str, Any]` - Generated artifacts
- `learnings: List[str]` - Captured learnings
- `insights: Dict[str, Any]` - Insights
- `quality_score: float` - Quality at snapshot time
- `timestamp: datetime` - Snapshot time
- `metadata: Dict[str, Any]`

**Methods**:
- `create_copy()` - Deep copy of memento
- `to_dict()` - Serialize to dict

#### `RollbackManager`

Manages rollback operations.

**Methods**:
- `rollback_to_memento(memento, reason)` - Rollback to snapshot
- `should_rollback(delta, threshold)` - Determine if rollback needed
- `get_rollback_history()` - Get rollback history

### Thermodynamic Computing Classes

#### `ThermodynamicComputing`

Main facade for uncertainty quantification and probabilistic reasoning.

**Constructor**:
```python
ThermodynamicComputing(
    observable: Optional[PipelineObservable] = None,
    default_strategy: str = "bayesian"
)
```

**Methods**:
- `quantify_uncertainty(prediction, context, strategy)` - Quantify uncertainty
- `learn_from_outcome(prediction, actual, context, strategy)` - Learn from outcomes
- `sample_with_temperature(options, scores, temperature, step, max_steps)` - Temperature-based sampling
- `get_confidence_history(filter_context)` - Get confidence history
- `get_strategy(strategy_name)` - Get uncertainty strategy

#### `ConfidenceScore`

Represents uncertainty quantification.

**Fields**:
- `confidence: float` - Probability [0.0, 1.0]
- `variance: float` - Uncertainty in estimate
- `entropy: float` - Information content
- `evidence: Dict[str, Any]` - Supporting evidence
- `sample_size: int` - Number of samples
- `timestamp: datetime` - Score timestamp
- `context: Dict[str, Any]` - Context information

**Methods**:
- `to_dict()` - Serialize to dict
- `standard_error()` - Calculate standard error
- `confidence_interval(z_score)` - Calculate confidence interval

**Example**:
```python
score = tc.quantify_uncertainty(prediction, context)
lower, upper = score.confidence_interval(z_score=1.96)  # 95% CI
print(f"Confidence: {score.confidence:.2%} [{lower:.2%}, {upper:.2%}]")
```

#### `UncertaintyStrategy` (Abstract)

Base class for uncertainty strategies.

**Methods**:
- `estimate_confidence(prediction, context)` - Estimate confidence
- `update_from_outcome(prediction, actual, context)` - Learn from outcome

**Concrete Implementations**:

##### `BayesianUncertaintyStrategy`

Bayesian inference with prior updates.

**Additional Methods**:
- `get_priors()` - Get current Bayesian priors
- `set_prior(stage, prediction_type, alpha, beta)` - Manually set prior

**Example**:
```python
bayesian = tc.get_strategy("bayesian")
priors = bayesian.get_priors()
# Save/load priors for persistence
```

##### `MonteCarloUncertaintyStrategy`

Monte Carlo simulation-based estimation.

**Constructor**:
```python
MonteCarloUncertaintyStrategy(
    n_simulations: int = 1000,
    observable: Optional[PipelineObservable] = None
)
```

**Requirements**:
- Context must include `simulator_fn` callable

##### `EnsembleUncertaintyStrategy`

Ensemble voting across multiple models.

**Constructor**:
```python
EnsembleUncertaintyStrategy(
    model_generators: List[Callable] = None,
    weights: Optional[List[float]] = None,
    observable: Optional[PipelineObservable] = None
)
```

**Methods**:
- `add_model(generator, weight)` - Add model to ensemble

#### `TemperatureScheduler`

Temperature-based annealing for exploration/exploitation.

**Constructor**:
```python
TemperatureScheduler(
    initial_temp: float = 1.0,
    final_temp: float = 0.1,
    schedule: str = "exponential",  # or "linear", "inverse", "step"
    observable: Optional[PipelineObservable] = None
)
```

**Methods**:
- `get_temperature(step, max_steps)` - Get temperature for step
- `sample_with_temperature(options, scores, temperature)` - Sample with Boltzmann distribution

### Pipeline Observer Classes

#### `PipelineObservable`

Event broadcasting hub (Subject in Observer pattern).

**Methods**:
- `attach(observer: PipelineObserver)` - Attach observer
- `detach(observer: PipelineObserver)` - Detach observer
- `notify(event: PipelineEvent)` - Broadcast event
- `get_observer_count()` - Get number of observers

#### `PipelineObserver` (Abstract)

Observer interface for pipeline events.

**Methods**:
- `on_event(event: PipelineEvent)` - Handle event (abstract)
- `get_observer_name()` - Get observer name

**Concrete Implementations**:
- `LoggingObserver` - Logs all events
- `MetricsObserver` - Collects metrics
- `StateTrackingObserver` - Tracks current state
- `NotificationObserver` - Sends notifications
- `SupervisorCommandObserver` - Handles supervisor commands

#### `PipelineEvent`

Immutable event data.

**Fields**:
- `event_type: EventType` - Type of event
- `timestamp: datetime` - Event timestamp
- `card_id: Optional[str]` - Associated card ID
- `stage_name: Optional[str]` - Stage name
- `developer_name: Optional[str]` - Developer name
- `data: Dict[str, Any]` - Event data
- `error: Optional[Exception]` - Error if any

**Methods**:
- `to_dict()` - Serialize to dict

#### `EventType` (Enum)

Standard pipeline event types.

**Categories**:
- Pipeline: `PIPELINE_STARTED`, `PIPELINE_COMPLETED`, `PIPELINE_FAILED`, `PIPELINE_PAUSED`
- Stage: `STAGE_STARTED`, `STAGE_COMPLETED`, `STAGE_FAILED`, `STAGE_SKIPPED`, `STAGE_RETRYING`
- Developer: `DEVELOPER_STARTED`, `DEVELOPER_COMPLETED`, `DEVELOPER_FAILED`
- Git: `GIT_COMMIT_CREATED`, `GIT_PUSH_COMPLETED`, etc.

### Configuration Options

#### Retry Policy

```python
@dataclass
class RetryPolicy:
    max_retries: int = 3
    retryable_exceptions: Set[type] = {Exception}
    backoff_multiplier: float = 2.0
    initial_delay: float = 1.0
```

#### Stage Result

```python
@dataclass
class StageResult:
    stage_name: str
    success: bool
    data: Dict[str, Any] = field(default_factory=dict)
    duration: float = 0.0
    skipped: bool = False
    retry_count: int = 0
    error: Optional[Exception] = None
```

### Events Emitted

#### Dynamic Pipeline Events

```python
EventType.PIPELINE_STARTED
EventType.PIPELINE_COMPLETED
EventType.PIPELINE_FAILED
EventType.PIPELINE_PAUSED
EventType.PIPELINE_RESUMED
EventType.STAGE_STARTED
EventType.STAGE_COMPLETED
EventType.STAGE_FAILED
EventType.STAGE_SKIPPED
EventType.STAGE_RETRYING
```

#### Two-Pass Pipeline Events

```python
TwoPassEventType.FIRST_PASS_STARTED
TwoPassEventType.FIRST_PASS_COMPLETED
TwoPassEventType.FIRST_PASS_FAILED
TwoPassEventType.SECOND_PASS_STARTED
TwoPassEventType.SECOND_PASS_COMPLETED
TwoPassEventType.PASS_QUALITY_IMPROVED
TwoPassEventType.PASS_QUALITY_DEGRADED
TwoPassEventType.MEMENTO_CREATED
TwoPassEventType.MEMENTO_APPLIED
TwoPassEventType.ROLLBACK_INITIATED
TwoPassEventType.ROLLBACK_COMPLETED
TwoPassEventType.LEARNING_CAPTURED
```

#### Thermodynamic Computing Events

```python
ThermodynamicEventType.CONFIDENCE_CALCULATED
ThermodynamicEventType.CONFIDENCE_UPDATED
ThermodynamicEventType.UNCERTAINTY_QUANTIFIED
ThermodynamicEventType.BAYESIAN_PRIOR_UPDATED
ThermodynamicEventType.MONTE_CARLO_STARTED
ThermodynamicEventType.MONTE_CARLO_COMPLETED
ThermodynamicEventType.ENSEMBLE_GENERATED
ThermodynamicEventType.ENSEMBLE_VOTED
ThermodynamicEventType.TEMPERATURE_ADJUSTED
ThermodynamicEventType.RISK_ASSESSED
```

---

## Glossary

**Adaptive Pipeline**: Pipeline that adjusts execution based on runtime conditions

**Bayesian Inference**: Statistical method for updating beliefs based on evidence

**Boltzmann Distribution**: Probability distribution controlled by temperature parameter

**Complexity-Based Selection**: Choosing stages based on project complexity analysis

**Confidence Score**: Quantified uncertainty in a prediction (probability)

**Dynamic Pipeline**: Runtime-configurable pipeline with adaptive stage selection

**Ensemble**: Multiple models/solutions combined for better results

**Entropy**: Measure of uncertainty or information content

**Memento**: Snapshot of state for rollback purposes

**Monte Carlo**: Simulation-based estimation method

**Observer Pattern**: Design pattern for event broadcasting

**Pass**: Single execution phase in two-pass pipeline

**Quality Delta**: Change in quality score between passes

**Rollback**: Reverting to previous known-good state

**Strategy Pattern**: Design pattern for swappable algorithms

**Temperature**: Parameter controlling exploration vs exploitation

**Thermodynamic Computing**: Probabilistic reasoning inspired by statistical thermodynamics

**Two-Pass Pipeline**: Fast analysis followed by refined execution

**Uncertainty Quantification**: Measuring confidence/variance in predictions

---

**End of Documentation**

For questions or issues, please refer to the main Artemis repository or contact the development team.
