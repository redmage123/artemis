# AI Query Architecture Decision: Orchestrator vs Feature-Level

**Date:** October 26, 2025
**Decision Required:** Should AI queries be made at the Orchestrator level or within each Feature?

---

## Question

Where should AI query logic live for the three advanced features?

**Option A**: Orchestrator makes AI calls and passes results to features
**Option B**: Features make their own AI calls when needed

---

## Analysis

### Option A: Orchestrator-Level AI Calls

```
┌─────────────────────────────────────────┐
│         Artemis Orchestrator            │
│                                         │
│  1. Router recommends features          │
│  2. Orchestrator makes AI calls         │
│  3. Pass results to features            │
│                                         │
│  ┌───────────────────────────────────┐ │
│  │ ai_service.query_for_confidence() │ │
│  │ ai_service.query_for_quality()    │ │
│  │ ai_service.query_for_risk()       │ │
│  └───────────────────────────────────┘ │
│           ↓                             │
│  ┌───────────────────────────────────┐ │
│  │ Feature.execute(                  │ │
│  │   confidence=0.85,                │ │
│  │   quality=0.78,                   │ │
│  │   risks=[...]                     │ │
│  │ )                                 │ │
│  └───────────────────────────────────┘ │
└─────────────────────────────────────────┘
```

#### Pros:
✅ **Single orchestration point** - All AI calls coordinated in one place
✅ **Easier caching** - Orchestrator can cache results across features
✅ **Better cost control** - Centralized token tracking and budgeting
✅ **Simpler feature implementation** - Features are pure logic, no AI dependencies
✅ **Easier testing** - Features can be tested with mock data
✅ **Clear separation of concerns** - Orchestrator = coordination, Features = execution

#### Cons:
❌ **Tight coupling** - Orchestrator must know what each feature needs
❌ **Less flexible** - Features can't make adaptive AI calls during execution
❌ **Upfront cost** - Must pay for all queries even if feature doesn't use them
❌ **Latency** - Sequential queries before feature execution starts

---

### Option B: Feature-Level AI Calls

```
┌─────────────────────────────────────────┐
│         Artemis Orchestrator            │
│                                         │
│  1. Router recommends features          │
│  2. Pass ai_service to features         │
│  3. Features make calls as needed       │
│                                         │
│           ↓                             │
│  ┌───────────────────────────────────┐ │
│  │ Feature.execute(                  │ │
│  │   ai_service=ai_service,          │ │
│  │   context={...}                   │ │
│  │ )                                 │ │
│  └───────────────────────────────────┘ │
└─────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────┐
│      Thermodynamic Computing            │
│                                         │
│  def quantify_uncertainty(code):        │
│      # Make AI call when needed         │
│      confidence = self.ai_service       │
│          .query_for_confidence(code)    │
│                                         │
│      # Adaptive: query again if needed  │
│      if confidence < 0.7:               │
│          refined = self.ai_service      │
│              .query_for_confidence(     │
│                  code, detailed=True)   │
└─────────────────────────────────────────┘
```

#### Pros:
✅ **Loose coupling** - Features are self-contained
✅ **Adaptive execution** - Features can make calls based on runtime decisions
✅ **Lazy evaluation** - Only pay for queries that are actually needed
✅ **Feature autonomy** - Each feature controls its own AI interactions
✅ **Parallel optimization** - Features can make parallel AI calls internally

#### Cons:
❌ **Duplicate queries** - Multiple features might query same thing
❌ **Harder to cache** - Each feature would need its own cache
❌ **Cost tracking complexity** - Distributed token usage tracking
❌ **Feature complexity** - Each feature must handle AI service
❌ **Testing complexity** - Must mock AI service in each feature's tests

---

## Hybrid Approach: **RECOMMENDED** ✅

**Best of both worlds**: Orchestrator prepares context, features make adaptive calls

```
┌─────────────────────────────────────────────────────────────┐
│                  Artemis Orchestrator                       │
│                                                             │
│  Phase 1: Upfront Analysis (Orchestrator)                  │
│  ┌───────────────────────────────────────────────────────┐ │
│  │ - Router already analyzed task                        │ │
│  │ - Uncertainty quantified: 65%                         │ │
│  │ - Risks identified: [security, complexity]            │ │
│  │ - Confidence estimate: 0.72                           │ │
│  └───────────────────────────────────────────────────────┘ │
│           ↓                                                 │
│  Phase 2: Feature Execution (Features + Orchestrator)      │
│  ┌───────────────────────────────────────────────────────┐ │
│  │ Pass to features:                                     │ │
│  │   - Initial analysis (from router)                    │ │
│  │   - ai_service reference (for adaptive calls)         │ │
│  │   - Context from router's prompts                     │ │
│  └───────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────────────────────────┐
│              Feature (e.g., Thermodynamic)                  │
│                                                             │
│  __init__(ai_service, initial_context):                    │
│      # Receive both: initial analysis + ai_service         │
│      self.ai_service = ai_service                           │
│      self.initial_confidence = initial_context.confidence   │
│                                                             │
│  execute():                                                 │
│      # Use initial analysis (free!)                        │
│      confidence = self.initial_confidence  # 0.72          │
│                                                             │
│      # Adaptive: make additional calls if needed           │
│      if confidence < threshold:                             │
│          refined = self.ai_service                          │
│              .query_for_confidence(                         │
│                  code, detailed=True)                       │
│                                                             │
│      # Best of both: upfront + adaptive                     │
└─────────────────────────────────────────────────────────────┘
```

### Hybrid Benefits:

1. **Orchestrator provides initial analysis**
   - Router already does uncertainty calculation
   - Router already identifies risks
   - Router creates comprehensive prompts
   - **Free for features to use!** (already computed)

2. **Features can make adaptive calls**
   - Have ai_service reference for runtime queries
   - Can do additional analysis if initial insufficient
   - Can make domain-specific queries

3. **Cost optimized**
   - Reuse router's analysis (no duplicate queries)
   - Only pay for additional queries when needed
   - Features can decide if more detail warranted

4. **Loose coupling**
   - Features don't depend on specific router implementation
   - Can work with just ai_service if needed
   - Can ignore initial context if desired

---

## Concrete Implementation

### What Router Already Provides (No Extra Cost):

```python
# In intelligent_router_enhanced.py - already computed!
context = {
    # Uncertainty analysis (already done)
    'uncertainty_level': 0.65,
    'confidence_level': 'medium',
    'known_unknowns': [...],

    # Risk assessment (already done)
    'risk_details': [
        {'type': 'security', 'severity': 'high', 'probability': 0.30},
        ...
    ],

    # Rich guidance prompt (already generated)
    'prompt': """## Thermodynamic Computing Guidance
    ### Uncertainty Analysis...
    """,

    # AI service for adaptive calls
    'ai_service': ai_service
}
```

### How Features Use It:

```python
class ThermodynamicComputing:
    def __init__(self, context: Dict[str, Any]):
        # Get pre-computed analysis (free!)
        self.initial_uncertainty = context['uncertainty_level']
        self.known_unknowns = context['known_unknowns']
        self.guidance_prompt = context['prompt']

        # Get ai_service for adaptive calls
        self.ai_service = context['ai_service']

    def quantify_uncertainty(self, code: str) -> float:
        # Start with router's analysis (already computed)
        uncertainty = self.initial_uncertainty  # 0.65

        # Adaptive: If uncertainty high, get more detail
        if uncertainty > 0.6:
            # NOW make AI call for detailed analysis
            detailed = self.ai_service.query_for_confidence(
                code=code,
                context=self.guidance_prompt  # Use router's prompt!
            )
            uncertainty = detailed.score

        return uncertainty
```

### Features Can Use Mixin for DRY:

```python
class ThermodynamicComputing(AdvancedFeaturesAIMixin):
    def __init__(self, context: Dict[str, Any]):
        # Pre-computed from router
        self.initial_uncertainty = context['uncertainty_level']

        # For adaptive calls
        self.ai_service = context['ai_service']

    def quantify_uncertainty(self, code: str) -> float:
        # Use pre-computed if sufficient
        if self.initial_uncertainty < 0.6:
            return self.initial_uncertainty

        # Adaptive: Use mixin method for additional detail
        estimate = self.query_for_confidence(  # From mixin
            code=code,
            context="detailed uncertainty analysis"
        )

        return estimate.score
```

---

## Decision Matrix

| Aspect | Orchestrator Only | Feature Only | **Hybrid** ✅ |
|--------|-------------------|--------------|---------------|
| Coupling | High | Low | **Medium** |
| Flexibility | Low | High | **High** |
| Cost | High (upfront) | Medium | **Low** (lazy) |
| Caching | Easy | Hard | **Easy** (router caches) |
| Testing | Easy | Medium | **Easy** |
| Adaptability | None | Full | **Full** |
| Code reuse | None | Mixin | **Router + Mixin** |

---

## Recommendation: **Hybrid Approach** ✅

### Implementation Strategy:

1. **Router provides rich initial context** (already done!)
   - Uncertainty analysis
   - Risk assessment
   - Guidance prompts
   - AI service reference

2. **Features receive context in constructor**
   ```python
   def __init__(self, context: Dict[str, Any]):
       self.context = context
       self.ai_service = context['ai_service']
   ```

3. **Features use initial analysis first** (free!)
   ```python
   uncertainty = self.context['uncertainty_level']
   ```

4. **Features make adaptive calls if needed**
   ```python
   if need_more_detail:
       refined = self.ai_service.query_for_confidence(...)
   ```

5. **Features inherit from mixin for DRY**
   ```python
   class ThermodynamicComputing(AdvancedFeaturesAIMixin):
       # Use mixin methods for AI calls
   ```

---

## Benefits of Hybrid

### For Simple Tasks:
- Router's initial analysis is sufficient
- Features use pre-computed values
- **Zero additional AI calls** ✓

### For Complex Tasks:
- Router's initial analysis provides baseline
- Features make adaptive calls for detail
- **Pay only for what's needed** ✓

### For All Tasks:
- Mixin provides DRY AI query methods
- Router provides rich prompts as starting point
- Features have full autonomy
- **Best of both worlds** ✓

---

## Code Organization

```
artemis/src/
├── intelligent_router_enhanced.py
│   └── Provides: Initial analysis, context, prompts
│
├── advanced_features_ai_mixin.py   (NEW)
│   └── Provides: DRY AI query methods for features
│
├── thermodynamic_computing.py
│   ├── Inherits: AdvancedFeaturesAIMixin
│   ├── Receives: Context from router
│   └── Uses: Initial analysis + adaptive calls
│
├── two_pass_pipeline.py
│   ├── Inherits: AdvancedFeaturesAIMixin
│   ├── Receives: Context from router
│   └── Uses: Initial analysis + adaptive calls
│
└── dynamic_pipeline.py
    ├── Inherits: AdvancedFeaturesAIMixin
    ├── Receives: Context from router
    └── Uses: Initial analysis + adaptive calls
```

---

## Status

- ✅ Router provides rich context (implemented)
- ✅ Mixin provides DRY AI methods (implemented)
- ⏳ Features need to be updated to use hybrid approach
- ⏳ Features need to inherit from mixin

---

## Next Steps

1. Update feature constructors to accept context dict
2. Update features to inherit from AdvancedFeaturesAIMixin
3. Update features to use initial analysis first
4. Add adaptive AI calls where needed
5. Test hybrid approach with simple and complex tasks

---

**End of Document**
