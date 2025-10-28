#!/usr/bin/env python3
"""
Prompt Generator

WHAT: Generates comprehensive prompts for each advanced feature.

WHY: Provides rich context explaining WHAT to do and WHY, helping
features make informed decisions about execution strategies.

RESPONSIBILITY:
    - Generate thermodynamic computing prompt
    - Generate dynamic pipeline prompt
    - Generate two-pass pipeline prompt
    - Format prompts with task details and guidance

PATTERNS:
    - Template Method: Standard prompt structure with variable content
    - Strategy Pattern: Different prompt strategies per feature
"""

from typing import Dict, List
from intelligent_router import TaskRequirements
from intelligent_router_pkg.uncertainty_analysis import UncertaintyAnalysis
from intelligent_router_pkg.risk_factor import RiskFactor


class PromptGenerator:
    """
    Generates comprehensive prompts for each advanced feature.

    WHY: Provides rich context that helps features understand
    what to do and why.
    """

    def generate_thermodynamic_prompt(
        self,
        card: Dict,
        requirements: TaskRequirements,
        uncertainty: UncertaintyAnalysis,
        risks: List[RiskFactor]
    ) -> str:
        """Generate comprehensive prompt for Thermodynamic Computing."""
        risk_summary = "\n".join([
            f"  - {r.risk_type.upper()} ({r.severity}): {r.description}"
            for r in risks
        ])

        return f"""## Thermodynamic Computing Guidance

### Task Overview
**Title**: {card.get('title', 'Unknown')}
**Complexity**: {requirements.complexity}
**Story Points**: {requirements.estimated_story_points}
**Type**: {requirements.task_type}

### Uncertainty Analysis
**Overall Uncertainty**: {uncertainty.overall_uncertainty:.0%}
**Confidence Level**: {uncertainty.confidence_level}
**Similar Tasks in History**: {uncertainty.similar_task_history}

**Uncertainty Sources**:
{chr(10).join(f"  - {source}" for source in uncertainty.uncertainty_sources)}

**Known Unknowns**:
{chr(10).join(f"  - {unknown}" for unknown in uncertainty.known_unknowns)}

### Risk Factors ({len(risks)} identified)
{risk_summary if risks else "  No significant risks identified"}

### Your Mission
Use Thermodynamic Computing to:

1. **Quantify Uncertainty** ({uncertainty.overall_uncertainty:.0%} current)
   - Track confidence scores throughout execution
   - Update as unknowns become known
   - Provide probabilistic estimates for outcomes

2. **Risk Quantification**
   - Run Monte Carlo simulations for {len(risks)} risk factors
   - Calculate probability distributions for outcomes
   - Identify high-impact, high-probability risks

3. **Bayesian Learning**
   - Update priors based on similar tasks ({uncertainty.similar_task_history} in history)
   - Learn from this execution for future tasks
   - Improve confidence estimates over time

4. **Decision Support**
   - Provide confidence intervals for estimates
   - Recommend when to seek human input
   - Suggest risk mitigations based on simulations

### Expected Outcomes
- Confidence trajectory: {uncertainty.overall_uncertainty:.0%} → 85%+
- Risk assessment: Quantified probabilities for all {len(risks)} risks
- Learning: Updated Bayesian priors for future similar tasks
"""

    def generate_dynamic_pipeline_prompt(
        self,
        card: Dict,
        requirements: TaskRequirements,
        intensity: float
    ) -> str:
        """Generate comprehensive prompt for Dynamic Pipeline."""
        intensity_meaning = self._get_intensity_meaning(intensity)

        return f"""## Dynamic Pipeline Guidance

### Task Overview
**Title**: {card.get('title', 'Unknown')}
**Complexity**: {requirements.complexity}
**Story Points**: {requirements.estimated_story_points}
**Type**: {requirements.task_type}

### Execution Intensity: {intensity:.0%}
**Meaning**: {intensity_meaning}

### Your Mission
Optimize pipeline execution using Dynamic Pipeline at {intensity:.0%} intensity:

1. **Stage Selection** (Intensity: {intensity:.0%})
   {self._get_stage_selection_guidance(intensity)}
   - Skip unnecessary stages based on requirements
   - Prioritize critical path stages
   - Cache results for reuse

2. **Resource Allocation**
   - Workers: Scale up to {int(1 + intensity * 7)} parallel workers
   - Retries: Based on complexity
   - Timeout: {requirements.estimated_story_points * 10} minutes per stage

3. **Optimization Strategies**
   {self._get_optimization_strategy(intensity)}

4. **Monitoring & Adaptation**
   - Track stage execution times
   - Detect bottlenecks early
   - Adjust parallelization if needed
   - Learn optimal configurations

### Task-Specific Guidance
**Requirements**: {', '.join([
    'Frontend' if requirements.requires_frontend else '',
    'Backend' if requirements.requires_backend else '',
    'API' if requirements.requires_api else '',
    'Database' if requirements.has_database else '',
    'External Dependencies' if requirements.has_external_dependencies else ''
]).strip(', ')}

**Priority Stages**: Focus optimization efforts on stages that handle above requirements.

### Expected Outcomes
- Execution time: ~{requirements.estimated_story_points * 2} hours
- Time savings: {int(intensity * 30)}% vs sequential
- Resource utilization: {intensity:.0%} of maximum capacity
"""

    def generate_two_pass_prompt(
        self,
        card: Dict,
        requirements: TaskRequirements,
        uncertainty: UncertaintyAnalysis,
        intensity: float
    ) -> str:
        """Generate comprehensive prompt for Two-Pass Pipeline."""
        return f"""## Two-Pass Pipeline Guidance

### Task Overview
**Title**: {card.get('title', 'Unknown')}
**Complexity**: {requirements.complexity}
**Story Points**: {requirements.estimated_story_points}
**Uncertainty**: {uncertainty.overall_uncertainty:.0%}

### Two-Pass Intensity: {intensity:.0%}
**Meaning**: {self._get_two_pass_meaning(intensity)}

### Your Mission
Execute using two-pass strategy at {intensity:.0%} intensity:

## FIRST PASS (~30 seconds)

### Focus Areas:
1. **Quick Architecture Validation**
   - Verify approach is feasible
   - Identify architectural risks
   - Validate key assumptions

2. **Risk Discovery**
   - Scan for security concerns
   - Identify performance bottlenecks
   - Find integration challenges

3. **Uncertainty Reduction**
   Current unknowns:
{chr(10).join(f"   - {unknown}" for unknown in uncertainty.known_unknowns)}

   Goal: Convert as many unknowns to knowns as possible

4. **Complexity Refinement**
   - Initial estimate: {requirements.estimated_story_points} points
   - Refine based on discoveries
   - Adjust second pass plan

### First Pass Outputs:
- **Architecture Decision**: Chosen approach and trade-offs
- **Risk List**: All identified risks with severity
- **Learnings**: Key insights about the task
- **Refined Estimate**: Updated story points if needed
- **Go/No-Go Decision**: Continue to second pass?

---

## SECOND PASS (~{requirements.estimated_story_points * 5} minutes)

### Focus Areas:
1. **Full Implementation**
   - Apply architecture from first pass
   - Implement with learnings applied
   - Address all identified risks

2. **Risk Mitigation**
   - Apply mitigations for each discovered risk
   - Add safeguards and error handling
   - Implement security measures

3. **Quality Optimization**
   - Target quality: {0.70 + intensity * 0.15:.0%}
   - Comprehensive testing
   - Code review and refinement

4. **Learning Capture**
   - Document what worked/didn't work
   - Update Bayesian priors
   - Share insights for future tasks

### Success Criteria:
- Quality threshold: {0.70 + intensity * 0.15:.0%}
- All risks mitigated
- All tests passing
- Code meets standards

### Rollback Conditions:
- Quality drops below {0.70 + intensity * 0.15 - 0.1:.0%}
- Critical functionality broken
- Significant regressions detected

If rollback triggered: Revert to first pass state and report findings.

### Expected Outcomes
- First pass: Architecture validated, risks identified
- Second pass: High-quality implementation with risk mitigations
- Learning: Updated priors for future similar tasks
"""

    def _get_intensity_meaning(self, intensity: float) -> str:
        """Get intensity meaning - extracted to eliminate nested ternaries."""
        if intensity > 0.8:
            return "Maximum parallelization and optimization"
        if intensity > 0.6:
            return "High parallelization"
        if intensity > 0.3:
            return "Moderate optimization"
        return "Sequential execution with minimal overhead"

    def _get_stage_selection_guidance(self, intensity: float) -> str:
        """Get stage selection guidance - extracted to eliminate nested ternaries."""
        if intensity > 0.7:
            return "- Aggressively parallelize all independent stages"
        if intensity > 0.4:
            return "- Parallelize some independent stages"
        return "- Mostly sequential execution"

    def _get_optimization_strategy(self, intensity: float) -> str:
        """Get optimization strategy - extracted to eliminate nested ternaries."""
        if intensity > 0.8:
            return "- Maximum: Aggressive parallelization, extensive caching, fast failure detection"
        if intensity > 0.6:
            return "- High: Significant parallelization, selective caching"
        if intensity > 0.3:
            return "- Moderate: Some parallelization, minimal caching"
        return "- Minimal: Sequential execution, basic error handling"

    def _get_two_pass_meaning(self, intensity: float) -> str:
        """Get two-pass meaning - extracted to eliminate nested ternaries."""
        if intensity > 0.8:
            return "Aggressive two-pass with high quality threshold"
        if intensity > 0.6:
            return "Full two-pass with rollback enabled"
        if intensity > 0.3:
            return "Moderate two-pass approach"
        return "Single pass (two-pass disabled)"
