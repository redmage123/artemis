# Intelligent Router Integration with Advanced Features

**Complete integration of Intelligent Router with Dynamic Pipelines, Two-Pass Pipelines, and Thermodynamic Computing**

---

## Overview

The **Enhanced Intelligent Router** extends the base Intelligent Router to not only select which pipeline stages should run, but also **recommend which advanced features** (Dynamic Pipelines, Two-Pass, Thermodynamic Computing) would provide the most benefit for each task.

### Why This Matters

The Intelligent Router already analyzes task requirements, complexity, and risks. It's the **perfect place** to decide:
- Should we use Dynamic Pipeline for adaptive execution?
- Would Two-Pass provide valuable fast feedback?
- Does uncertainty justify Thermodynamic Computing?

This integration creates a **self-optimizing system** that automatically applies the right advanced features to each task.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    ARTEMIS ORCHESTRATOR                          │
│                                                                  │
│  Card arrives: "Implement OAuth2 authentication"                │
│                                                                  │
│  ┌────────────────────────────────────────────────────────┐   │
│  │  ENHANCED INTELLIGENT ROUTER                            │   │
│  │                                                         │   │
│  │  1. Analyze task requirements (base functionality)     │   │
│  │     → Detect: security, API, database, external deps  │   │
│  │     → Complexity: complex (21 story points)            │   │
│  │                                                         │   │
│  │  2. Calculate uncertainty (NEW)                        │   │
│  │     → Overall uncertainty: 0.65 (medium-high)          │   │
│  │     → Known unknowns: OAuth2 edge cases                │   │
│  │     → Similar tasks: 2 (limited experience)            │   │
│  │                                                         │   │
│  │  3. Identify risk factors (NEW)                        │   │
│  │     → Security: HIGH severity, 30% probability         │   │
│  │     → Complexity: MEDIUM severity, 35% probability     │   │
│  │     → Integration: MEDIUM severity, 20% probability    │   │
│  │                                                         │   │
│  │  4. Recommend pipeline mode (NEW)                      │   │
│  │     → Recommended: FULL mode                           │   │
│  │     → Rationale: High uncertainty + multiple risks     │   │
│  │     → Confidence: 85%                                   │   │
│  │                                                         │   │
│  │  5. Create feature contexts (NEW)                      │   │
│  │     → Thermodynamic: use Bayesian, 1000 MC samples    │   │
│  │     → Dynamic: 4 workers, 3 retries, 30min timeout    │   │
│  │     → Two-Pass: 30s first pass, rollback enabled      │   │
│  └────────────────────────────────────────────────────────┘   │
│                           ↓                                      │
│  ┌────────────────────────────────────────────────────────┐   │
│  │  ADVANCED PIPELINE INTEGRATION                          │   │
│  │                                                         │   │
│  │  Uses router's recommendations to execute with:        │   │
│  │  • Dynamic Pipeline (adaptive stages)                  │   │
│  │  • Two-Pass (fast feedback + refinement)              │   │
│  │  • Thermodynamic (uncertainty quantification)         │   │
│  └────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

---

## What the Enhanced Router Adds

### 1. **Uncertainty Quantification**

Calculates how uncertain the task is based on:
- Task complexity
- Presence of "uncertain", "unclear", "unfamiliar" keywords
- External dependencies
- Database migrations
- New technology
- Prior experience with similar tasks

**Output:**
```python
UncertaintyAnalysis(
    overall_uncertainty=0.65,  # 0.0-1.0 scale
    uncertainty_sources=[
        "Task complexity: complex",
        "Uncertainty keywords found: 2",
        "External dependencies add uncertainty"
    ],
    known_unknowns=[
        "OAuth2 edge cases and error handling",
        "External API behavior"
    ],
    similar_task_history=2,
    confidence_level='medium'
)
```

### 2. **Risk Factor Identification**

Scans task for risk patterns and quantifies them:
- **Security risks**: auth, password, encryption, vulnerabilities
- **Performance risks**: scalability, latency, load
- **Database risks**: migration, schema changes, data loss
- **Integration risks**: external APIs, third-party dependencies
- **Complexity risks**: complex, difficult, uncertain

**Output:**
```python
[
    RiskFactor(
        risk_type='security',
        description='Security-sensitive task requiring careful implementation',
        severity='high',
        probability=0.30,  # 30% chance of issues
        mitigation='Add security review stage, penetration testing, OWASP guidelines'
    ),
    RiskFactor(
        risk_type='complexity',
        description='High complexity with potential for underestimation',
        severity='medium',
        probability=0.35,
        mitigation='Break into smaller tasks, architecture review, incremental delivery'
    )
]
```

### 3. **Pipeline Mode Recommendation**

Recommends which execution mode to use:
- **STANDARD**: Simple tasks, no advanced features needed
- **DYNAMIC**: Moderate tasks benefit from adaptive stage selection
- **TWO_PASS**: Prototypes, experiments, refactoring (need fast feedback)
- **ADAPTIVE**: High uncertainty tasks (need confidence tracking)
- **FULL**: Complex, risky tasks (need all advanced features)

**Output:**
```python
AdvancedFeatureRecommendation(
    recommended_mode=PipelineMode.FULL,
    use_dynamic_pipeline=True,
    use_two_pass=True,
    use_thermodynamic=True,
    rationale="High benefit from both two-pass and uncertainty quantification",
    confidence_in_recommendation=0.85,
    expected_benefits=[
        "Dynamic: Optimize stage selection (estimated 30% time savings)",
        "Two-Pass: Fast feedback in ~30s, refined in ~42min",
        "Thermodynamic: Quantify uncertainty (current: 65%), learn from outcome"
    ]
)
```

### 4. **Rich Context for Each Feature**

Creates detailed context for each advanced feature:

**Thermodynamic Context:**
```python
{
    'task_type': 'feature',
    'complexity': 'complex',
    'story_points': 21,
    'uncertainty_level': 0.65,
    'confidence_level': 'medium',
    'similar_task_count': 2,
    'risk_count': 3,
    'high_risk_count': 1,
    'suggested_strategy': 'bayesian',  # Based on prior experience
    'suggested_samples': 1000,         # For Monte Carlo
    'suggested_temperature': 1.475     # For temperature sampling
}
```

**Dynamic Pipeline Context:**
```python
{
    'complexity': 'complex',
    'estimated_duration': 42,  # hours
    'parallel_developers': 2,
    'has_database': True,
    'has_external_deps': True,
    'suggested_max_workers': 8,
    'suggested_retry_attempts': 3,
    'suggested_timeout': 210  # minutes
}
```

**Two-Pass Context:**
```python
{
    'task_type': 'feature',
    'complexity': 'complex',
    'uncertainty_level': 0.65,
    'suggested_first_pass_timeout': 30,   # seconds
    'suggested_second_pass_timeout': 105, # minutes
    'suggested_quality_threshold': 0.75,
    'enable_rollback': True,
    'learning_transfer_enabled': True
}
```

---

## Usage Examples

### Example 1: Simple Task (README Fix)

```python
from intelligent_router_enhanced import IntelligentRouterEnhanced

router = IntelligentRouterEnhanced()

card = {
    'card_id': 'CARD-001',
    'title': 'Fix typo in README',
    'description': 'Correct spelling mistake in documentation',
    'story_points': 1
}

decision = router.make_enhanced_routing_decision(card)

# Router's analysis:
print(f"Complexity: {decision.requirements.complexity}")
# Output: simple

print(f"Uncertainty: {decision.uncertainty_analysis.overall_uncertainty:.0%}")
# Output: 10%

print(f"Risks: {len(decision.risk_factors)}")
# Output: 0

print(f"Recommended mode: {decision.feature_recommendation.recommended_mode.value}")
# Output: standard

print(f"Use advanced features: {decision.feature_recommendation.use_dynamic_pipeline}")
# Output: False

# Result: Standard pipeline sufficient for simple task
```

---

### Example 2: Prototype Task (Experimental Feature)

```python
card = {
    'card_id': 'CARD-002',
    'title': 'Prototype real-time notifications',
    'description': 'Build experimental prototype using WebSockets',
    'story_points': 8
}

decision = router.make_enhanced_routing_decision(card)

# Router's analysis:
print(f"Uncertainty: {decision.uncertainty_analysis.overall_uncertainty:.0%}")
# Output: 55% (keywords: prototype, experimental)

print(f"Recommended mode: {decision.feature_recommendation.recommended_mode.value}")
# Output: two_pass

print(f"Two-pass benefit: {decision.feature_recommendation.use_two_pass}")
# Output: True

print(f"Rationale: {decision.feature_recommendation.rationale}")
# Output: "Task benefits from fast feedback and iterative refinement"

# Result: Two-pass provides fast feedback (30s) for experimental work
```

---

### Example 3: Security-Critical Task (OAuth2)

```python
card = {
    'card_id': 'CARD-003',
    'title': 'Implement OAuth2 authentication',
    'description': 'Add secure authentication with Google/Facebook/GitHub',
    'story_points': 21
}

decision = router.make_enhanced_routing_decision(card)

# Router's analysis:
print(f"Uncertainty: {decision.uncertainty_analysis.overall_uncertainty:.0%}")
# Output: 65%

print(f"Risk factors: {len(decision.risk_factors)}")
# Output: 3

for risk in decision.risk_factors:
    print(f"  - {risk.risk_type}: {risk.severity} ({risk.probability:.0%} probability)")
# Output:
#   - security: high (30% probability)
#   - complexity: medium (35% probability)
#   - dependency: medium (20% probability)

print(f"Recommended mode: {decision.feature_recommendation.recommended_mode.value}")
# Output: full

print(f"Features enabled:")
print(f"  Dynamic: {decision.feature_recommendation.use_dynamic_pipeline}")
print(f"  Two-Pass: {decision.feature_recommendation.use_two_pass}")
print(f"  Thermodynamic: {decision.feature_recommendation.use_thermodynamic}")
# Output:
#   Dynamic: True
#   Two-Pass: True
#   Thermodynamic: True

# Result: Full advanced features for complex, risky task
```

---

### Example 4: Database Migration (High Risk)

```python
card = {
    'card_id': 'CARD-004',
    'title': 'Migrate from MongoDB to PostgreSQL',
    'description': 'Major database migration with schema changes',
    'story_points': 13
}

decision = router.make_enhanced_routing_decision(card)

# Router's analysis:
print(f"Uncertainty: {decision.uncertainty_analysis.overall_uncertainty:.0%}")
# Output: 75% (database migration adds significant uncertainty)

print(f"Database risk detected: {any(r.risk_type == 'database' for r in decision.risk_factors)}")
# Output: True

db_risk = [r for r in decision.risk_factors if r.risk_type == 'database'][0]
print(f"Database risk severity: {db_risk.severity}")
# Output: critical

print(f"Probability of issues: {db_risk.probability:.0%}")
# Output: 40%

print(f"Suggested mitigation: {db_risk.mitigation}")
# Output: "Dry-run migration, rollback script, backup verification, staging test"

print(f"Thermodynamic context - MC samples: {decision.thermodynamic_context['suggested_samples']}")
# Output: 1000 (high sample count for risk quantification)

# Result: Risk quantification via Monte Carlo, two-pass for safety
```

---

## Integration with Orchestrator

### Step 1: Use Enhanced Router

```python
# In artemis_orchestrator.py

from intelligent_router_enhanced import IntelligentRouterEnhanced
from advanced_pipeline_integration import AdvancedPipelineIntegration, PipelineMode

class ArtemisOrchestrator:
    def __init__(self, ...):
        # Use enhanced router instead of base router
        self.router = IntelligentRouterEnhanced(
            ai_service=self.ai_query_service,
            logger=self.logger,
            config=self.config,
            advanced_config=AdvancedPipelineConfig()
        )

        # Initialize advanced pipeline integration
        self.advanced_pipeline = AdvancedPipelineIntegration(
            observable=self.observable
        )

    def execute_card(self, card_id: str):
        # Get enhanced routing decision
        decision = self.router.make_enhanced_routing_decision(card)

        # Log router's recommendations
        self.logger.log(f"Router recommends: {decision.feature_recommendation.recommended_mode.value}")
        self.logger.log(f"Uncertainty: {decision.uncertainty_analysis.overall_uncertainty:.0%}")
        self.logger.log(f"Risks: {len(decision.risk_factors)}")

        # Execute with recommended mode
        result = self.advanced_pipeline.execute_with_mode(
            mode=decision.feature_recommendation.recommended_mode,
            card_id=card_id,
            context={
                'routing_decision': decision,
                'thermodynamic_context': decision.thermodynamic_context,
                'dynamic_context': decision.dynamic_pipeline_context,
                'two_pass_context': decision.two_pass_context
            }
        )

        return result
```

### Step 2: Advanced Features Use Router's Context

```python
# In advanced_pipeline_integration.py

def execute_with_mode(self, mode: PipelineMode, card_id: str, context: Dict) -> Dict:
    routing_decision = context.get('routing_decision')

    if mode == PipelineMode.FULL:
        # Use router's recommendations
        thermodynamic_ctx = context.get('thermodynamic_context', {})

        # Configure Thermodynamic Computing based on router
        thermodynamic = ThermodynamicComputing(
            strategy=thermodynamic_ctx.get('suggested_strategy', 'bayesian'),
            monte_carlo_samples=thermodynamic_ctx.get('suggested_samples', 1000),
            initial_temperature=thermodynamic_ctx.get('suggested_temperature', 1.0)
        )

        # Configure Dynamic Pipeline based on router
        dynamic_ctx = context.get('dynamic_context', {})
        dynamic_pipeline = DynamicPipelineBuilder(card_id) \
            .with_complexity(routing_decision.requirements.complexity) \
            .with_parallel_execution(
                max_workers=dynamic_ctx.get('suggested_max_workers', 4)
            ) \
            .with_retry_policy(
                max_retries=dynamic_ctx.get('suggested_retry_attempts', 2)
            ) \
            .build()

        # Configure Two-Pass based on router
        two_pass_ctx = context.get('two_pass_context', {})
        two_pass = TwoPassPipeline(
            rollback_enabled=two_pass_ctx.get('enable_rollback', True),
            quality_threshold=two_pass_ctx.get('suggested_quality_threshold', 0.75)
        )

        # Execute with all features
        return self._execute_full_mode(
            thermodynamic, dynamic_pipeline, two_pass, card_id
        )
```

---

## Decision Matrix

### How Router Decides Which Features to Use

| Task Characteristic | STANDARD | DYNAMIC | TWO_PASS | ADAPTIVE | FULL |
|---------------------|----------|---------|----------|----------|------|
| **Story Points** | 1-3 | 5-8 | 5-13 | 8-21 | 13-21+ |
| **Uncertainty** | <20% | <40% | Any | >60% | >60% |
| **Risk Factors** | 0 | 0-1 | Any | 2+ | 3+ |
| **Keywords** | simple, minor | - | prototype, experiment | research, unclear | critical, complex |
| **Task Type** | bugfix, doc | feature | refactor, prototype | any | refactor, security |
| **Experience** | 10+ similar | 5+ similar | Any | <3 similar | <3 similar |

### Feature Benefit Scores

Router calculates 0.0-1.0 benefit scores:

**Dynamic Pipeline Benefit:**
- Moderate complexity: +0.4
- External dependencies: +0.2
- Multiple stages: +0.3

**Two-Pass Benefit:**
- Prototype keywords: +0.5
- Refactoring: +0.4
- High uncertainty: +0.3
- Complex task: +0.2

**Thermodynamic Benefit:**
- High uncertainty: +0.5
- Multiple risks: +0.3
- Low experience: +0.2
- Critical risks: +0.2

---

## Configuration

### Enable/Disable Features

```yaml
# hydra_config/pipeline_config.yaml

# Router configuration
routing:
  enable_ai: true
  skip_threshold: 0.8
  require_threshold: 0.6

# Advanced features configuration
advanced_features:
  enabled: true

  # Feature toggles
  enable_dynamic_pipeline: true
  enable_two_pass: true
  enable_thermodynamic: true

  # Auto mode selection
  auto_mode_selection: true  # Let router decide

  # Thresholds
  confidence_threshold: 0.70
  simple_task_max_story_points: 3
  complex_task_min_story_points: 8

  # Dynamic pipeline
  parallel_execution_enabled: true
  max_parallel_workers: 8

  # Two-pass
  two_pass_auto_rollback: true
  first_pass_timeout_multiplier: 0.3

  # Thermodynamic
  default_uncertainty_strategy: "bayesian"
  enable_temperature_annealing: true
```

### Override Router Recommendations

```python
# Manual override if needed
decision = router.make_enhanced_routing_decision(card)

# Override mode if you disagree with router
if user_wants_two_pass:
    decision.feature_recommendation.recommended_mode = PipelineMode.TWO_PASS
    decision.feature_recommendation.use_two_pass = True

result = advanced_pipeline.execute_with_mode(
    mode=decision.feature_recommendation.recommended_mode,
    card_id=card_id,
    context=...
)
```

---

## Monitoring and Feedback

### Router Logs Everything

```
================================================================================
🧭 INTELLIGENT ROUTING DECISION
================================================================================
Task: Implement OAuth2 authentication
Complexity: complex
Type: feature
Story Points: 21
Parallel Developers: 2

Requirements Detected:
  Frontend: False
  Backend: True
  API: True
  Database: True
  UI Components: False
  Accessibility: False
  External Deps: True

Stages to Run (10):
  ✓ requirements
  ✓ sprint_planning
  ✓ project_analysis
  ✓ architecture
  ✓ project_review
  ✓ development
  ✓ arbitration
  ✓ code_review
  ✓ validation
  ✓ integration
  ✓ testing

Reasoning: Arbitration required: 2 developers competing
Confidence: 70.0%
================================================================================
🚀 ADVANCED FEATURE RECOMMENDATIONS
================================================================================
Recommended Mode: FULL
Confidence: 85%
Rationale: High benefit from both two-pass and uncertainty quantification

Features to Enable:
  Dynamic Pipeline: ✓
  Two-Pass: ✓
  Thermodynamic: ✓

Expected Benefits:
  • Dynamic: Optimize stage selection (estimated 30% time savings)
  • Two-Pass: Fast feedback in ~30s, refined in ~42min
  • Thermodynamic: Quantify uncertainty (current: 65%), learn from outcome

Uncertainty Analysis:
  Overall: 65% (medium)
  Similar Tasks: 2
  Known Unknowns:
    - OAuth2 edge cases and error handling
    - External API behavior

Risk Factors Identified: 3
  ⚠️  SECURITY: Security-sensitive task (severity: high, probability: 30%)
  ⚠️  COMPLEXITY: High complexity (severity: medium, probability: 35%)
  ⚠️  DEPENDENCY: External dependencies (severity: medium, probability: 20%)
================================================================================
```

### Learning Loop

Router learns from outcomes:

```python
# After execution
thermodynamic.learn_from_outcome(
    context=decision.thermodynamic_context,
    predicted_confidence=decision.uncertainty_analysis.overall_uncertainty,
    actual_confidence=final_quality_score,
    success=(final_quality_score > 0.8)
)

# Next similar task will have better estimates
```

---

## Testing

Run comprehensive tests:

```bash
cd /home/bbrelin/src/repos/artemis/src

# Run all tests
python3 -m unittest test_intelligent_router_enhanced.py

# Run specific test
python3 -m unittest test_intelligent_router_enhanced.TestPipelineModeRecommendation

# Verbose output
python3 -m unittest test_intelligent_router_enhanced.py -v
```

---

## Summary

### What We Built

1. **Enhanced Intelligent Router** that:
   - Quantifies task uncertainty
   - Identifies risk factors
   - Recommends optimal pipeline mode
   - Creates rich context for each advanced feature

2. **Seamless Integration** with:
   - Dynamic Pipelines (adaptive execution)
   - Two-Pass Pipelines (fast feedback + refinement)
   - Thermodynamic Computing (uncertainty quantification)

3. **Self-Optimizing System** that:
   - Automatically selects right features for each task
   - Learns from outcomes
   - Improves recommendations over time

### Benefits

- ✅ **Simple tasks**: No wasted overhead (STANDARD mode)
- ✅ **Prototypes**: Fast feedback in 30s (TWO_PASS mode)
- ✅ **Uncertain tasks**: Risk quantification (ADAPTIVE mode)
- ✅ **Complex/risky**: All advanced features (FULL mode)
- ✅ **Automatic**: No manual configuration needed
- ✅ **Transparent**: Clear rationale for all recommendations
- ✅ **Learning**: Gets better with every task

**Result:** Artemis intelligently adapts to each task, using the right tools at the right time!
