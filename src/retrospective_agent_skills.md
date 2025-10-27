# Retrospective Agent - Skills

## Agent Overview
**File**: `retrospective_agent.py`
**Purpose**: Sprint learning and continuous improvement through retrospectives
**Single Responsibility**: Facilitate sprint retrospectives and extract actionable insights

## Core Skills

### 1. Sprint Analysis
- **Metrics Analysis**: Velocity, story points, completion rates
- **Trend Identification**: Improving, declining, or stable
- **Health Assessment**: Overall sprint health (healthy, needs attention, critical)
- **Pattern Recognition**: Recurring issues and successes

### 2. Retrospective Framework
- **What Went Well**: Successes and positive outcomes
- **What Didn't Go Well**: Problems and failures
- **Action Items**: Concrete improvements for next sprint
- **Key Learnings**: Insights for team knowledge base

### 3. Metrics Tracking

```python
SprintMetrics(
    sprint_number=5,
    planned_story_points=50,
    completed_story_points=42,
    velocity=84.0,  # 84% completion
    bugs_found=8,
    bugs_fixed=6,
    tests_passing=95.5,
    code_review_iterations=3,
    average_task_duration_hours=12.5,
    blockers_encountered=2
)
```

### 4. Impact Assessment
- **High Impact**: Critical issues affecting delivery
- **Medium Impact**: Moderate effect on productivity
- **Low Impact**: Minor annoyances
- **Frequency**: Recurring vs one-time issues

### 5. Action Item Generation
- **Specific**: Concrete, actionable steps
- **Measurable**: Can track completion
- **Achievable**: Realistic for team capacity
- **Relevant**: Addresses identified issues
- **Time-Bound**: Target completion date

### 6. Learning Storage
- **RAG Integration**: Stores retrospective insights
- **Historical Context**: "We tried this before, here's what happened"
- **Best Practices**: What worked in similar situations
- **Anti-Patterns**: What to avoid based on past failures

## Retrospective Categories

### What Went Well
```python
RetrospectiveItem(
    category="what_went_well",
    description="Automated testing reduced bug count by 40%",
    impact="high",
    frequency="recurring",
    suggested_action="Continue expanding test coverage"
)
```

### What Didn't Go Well
```python
RetrospectiveItem(
    category="what_didnt",
    description="Code review backlog caused deployment delays",
    impact="medium",
    frequency="recurring",
    suggested_action="Implement code review SLA (24 hours max)"
)
```

### Action Items
```python
RetrospectiveItem(
    category="action_items",
    description="Set up automated code review reminders",
    impact="medium",
    frequency="one-time",
    suggested_action="Configure GitHub Actions for review notifications"
)
```

## Velocity Tracking

- **Improving**: Velocity increasing sprint-over-sprint
- **Declining**: Velocity decreasing (technical debt, burnout)
- **Stable**: Consistent velocity (team maturity)

## Health Assessment

### Healthy Sprint
- Velocity > 80%
- Bugs found ≈ bugs fixed
- Tests passing > 95%
- Low blocker count

### Needs Attention
- Velocity 60-80%
- Bug backlog growing
- Tests passing 85-95%
- Moderate blockers

### Critical
- Velocity < 60%
- Significant bug backlog
- Tests passing < 85%
- High blocker count

## LLM-Powered Analysis

- **Sentiment Analysis**: Team morale from retrospective notes
- **Pattern Detection**: Identifies recurring themes
- **Root Cause Analysis**: Digs deeper into problems
- **Improvement Suggestions**: AI-generated action items

## Dependencies

- `llm_client`: LLM for intelligent analysis
- `artemis_stage_interface`: Logging
- `debug_mixin`: Debug capabilities

## Usage Patterns

```python
# Initialize retrospective agent
retro = RetrospectiveAgent(
    llm_client=llm,
    logger=logger
)

# Run retrospective
report = retro.run_retrospective(
    sprint_number=5,
    metrics=sprint_metrics,
    team_feedback=[
        "Automated tests saved us time",
        "Code reviews were slow this sprint",
        "Documentation improved significantly"
    ]
)

# Generate recommendations
recommendations = retro.generate_recommendations(report)

# Store in RAG for future reference
rag.store_artifact(
    artifact_type="sprint_retrospective",
    content=json.dumps(report),
    metadata={"sprint_number": 5}
)
```

## Output Structure

```json
{
  "sprint_number": 5,
  "sprint_start_date": "2025-10-13",
  "sprint_end_date": "2025-10-27",
  "metrics": {...},
  "what_went_well": [...],
  "what_didnt_go_well": [...],
  "action_items": [...],
  "key_learnings": [
    "Automated testing significantly reduces bug count",
    "Code review SLAs improve delivery predictability"
  ],
  "velocity_trend": "improving",
  "overall_health": "healthy",
  "recommendations": [
    "Continue investing in test automation",
    "Implement code review SLA",
    "Schedule regular technical debt sprints"
  ]
}
```

## Design Patterns

- **Value Object**: SprintMetrics, RetrospectiveItem dataclasses
- **Parameter Object**: RetrospectiveContext reduces method parameters
- **Strategy Pattern**: Different analysis strategies per metric

## Integration Points

- **Sprint Planning**: Uses retrospective insights
- **Orchestrator**: Triggers retrospective after sprint completion
- **RAG Agent**: Stores retrospective data for learning
- **AgentMessenger**: Sends retrospective summary to team

## SOLID Principles

- **Single Responsibility**: Only facilitates retrospectives
- **Immutable Context**: Frozen RetrospectiveContext dataclass
- **Dependency Injection**: LLM client and logger injected

## Continuous Improvement Cycle

1. **Sprint Completion**: Collect metrics
2. **Retrospective**: Analyze what happened
3. **Action Items**: Generate improvements
4. **Next Sprint**: Apply learnings
5. **Measure**: Track if improvements worked
6. **Iterate**: Continuous refinement

## Metrics for Improvement

- **Velocity Trend**: Sprint-over-sprint comparison
- **Bug Reduction**: Fewer bugs over time
- **Test Coverage**: Increasing test coverage
- **Review Speed**: Faster code reviews
- **Team Satisfaction**: Morale improvements
