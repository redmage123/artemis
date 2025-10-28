#!/usr/bin/env python3
"""
WHY: Determine which pipeline stages should run based on task requirements.

RESPONSIBILITY:
- Map task requirements to stage decisions (REQUIRED/OPTIONAL/SKIP)
- Apply core stage rules (development, testing always run)
- Handle conditional stages (UI/UX, architecture, etc.)
- Build reasoning for stage selections

PATTERNS:
- Strategy Pattern: Different selection strategies for each stage
- Dispatch Table: Stage decision mapping
- Guard Clauses: Early decisions for required/skipped stages
- Single Responsibility: Only handles stage selection logic
"""

from typing import Dict, List, Any

from routing.models import StageDecision, TaskRequirements


class StageSelector:
    """
    WHY: Encapsulate stage selection logic in single responsibility class.

    RESPONSIBILITY:
    - Evaluate each stage against task requirements
    - Return stage decisions with reasoning
    - Maintain list of core (always-required) stages
    """

    # All available stages in execution order
    ALL_STAGES = [
        "requirements",
        "sprint_planning",
        "project_analysis",
        "architecture",
        "project_review",
        "research",  # Research stage - retrieves code examples before development
        "dependency_validation",
        "development",
        "arbitration",  # Adjudicator selects winner when multiple developers compete
        "code_review",
        "uiux",
        "validation",
        "integration",
        "testing",
        "notebook_generation"
    ]

    # Stages that are always required (core pipeline)
    CORE_STAGES = {
        "development",      # Always need code
        "code_review",      # Always review code
        "validation",       # Always validate
        "integration",      # Always integrate
        "testing"          # Always test
    }

    def select_stages(
        self,
        requirements: TaskRequirements
    ) -> Dict[str, Any]:
        """
        WHY: Main entry point for stage selection.

        RESPONSIBILITY:
        - Evaluate each stage against requirements
        - Build stage decisions dictionary
        - Generate reasoning list
        - Return structured stage selection result

        Args:
            requirements: Analyzed task requirements

        Returns:
            Dictionary with:
                - stage_decisions: Dict[str, StageDecision]
                - reasoning_parts: List[str]

        PATTERNS: Template Method - defines stage evaluation sequence
        """
        stage_decisions = {}
        reasoning_parts = []

        # Evaluate each stage
        self._select_requirements_stage(requirements, stage_decisions, reasoning_parts)
        self._select_sprint_planning_stage(requirements, stage_decisions, reasoning_parts)
        self._select_project_analysis_stage(requirements, stage_decisions, reasoning_parts)
        self._select_architecture_stage(requirements, stage_decisions, reasoning_parts)
        self._select_project_review_stage(requirements, stage_decisions, reasoning_parts)
        self._select_research_stage(requirements, stage_decisions, reasoning_parts)
        self._select_dependency_validation_stage(requirements, stage_decisions, reasoning_parts)
        self._select_development_stage(requirements, stage_decisions, reasoning_parts)
        self._select_arbitration_stage(requirements, stage_decisions, reasoning_parts)
        self._select_code_review_stage(requirements, stage_decisions, reasoning_parts)
        self._select_validation_stage(requirements, stage_decisions, reasoning_parts)
        self._select_integration_stage(requirements, stage_decisions, reasoning_parts)
        self._select_testing_stage(requirements, stage_decisions, reasoning_parts)
        self._select_uiux_stage(requirements, stage_decisions, reasoning_parts)
        self._select_notebook_generation_stage(requirements, stage_decisions, reasoning_parts)

        return {
            'stage_decisions': stage_decisions,
            'reasoning_parts': reasoning_parts
        }

    def _select_requirements_stage(
        self,
        requirements: TaskRequirements,
        stage_decisions: Dict[str, StageDecision],
        reasoning_parts: List[str]
    ) -> None:
        """WHY: Requirements stage is optional (runs if using requirements parser)."""
        stage_decisions['requirements'] = StageDecision.OPTIONAL

    def _select_sprint_planning_stage(
        self,
        requirements: TaskRequirements,
        stage_decisions: Dict[str, StageDecision],
        reasoning_parts: List[str]
    ) -> None:
        """
        WHY: Sprint planning adds overhead - skip for simple tasks.

        PATTERNS: Guard Clause - skip simple, require others
        """
        # Guard: Skip simple tasks
        if requirements.complexity == 'simple':
            stage_decisions['sprint_planning'] = StageDecision.SKIP
            reasoning_parts.append("Skipping sprint planning for simple task")
            return

        # Require for medium/complex
        stage_decisions['sprint_planning'] = StageDecision.REQUIRED

    def _select_project_analysis_stage(
        self,
        requirements: TaskRequirements,
        stage_decisions: Dict[str, StageDecision],
        reasoning_parts: List[str]
    ) -> None:
        """
        WHY: Project analysis needed for medium/complex tasks to understand codebase.

        PATTERNS: Guard Clause - skip simple, require others
        """
        # Guard: Skip simple tasks
        if requirements.complexity not in ['medium', 'complex']:
            stage_decisions['project_analysis'] = StageDecision.SKIP
            reasoning_parts.append("Skipping project analysis for simple task")
            return

        # Require for medium/complex
        stage_decisions['project_analysis'] = StageDecision.REQUIRED

    def _select_architecture_stage(
        self,
        requirements: TaskRequirements,
        stage_decisions: Dict[str, StageDecision],
        reasoning_parts: List[str]
    ) -> None:
        """
        WHY: Architecture review needed for complex tasks or DB/API changes.

        PATTERNS: Guard Clause - skip if not required
        """
        # Guard: Skip if not required
        if not requirements.requires_architecture_review:
            stage_decisions['architecture'] = StageDecision.SKIP
            reasoning_parts.append("Skipping architecture for simple implementation")
            return

        # Require for complex/DB/API tasks
        stage_decisions['architecture'] = StageDecision.REQUIRED

    def _select_project_review_stage(
        self,
        requirements: TaskRequirements,
        stage_decisions: Dict[str, StageDecision],
        reasoning_parts: List[str]
    ) -> None:
        """
        WHY: Project review needed for complex tasks requiring oversight.

        PATTERNS: Guard Clause - skip if not required
        """
        # Guard: Skip if not required
        if not requirements.requires_project_review:
            stage_decisions['project_review'] = StageDecision.SKIP
            reasoning_parts.append("Skipping project review for simple task")
            return

        # Require for complex tasks
        stage_decisions['project_review'] = StageDecision.REQUIRED

    def _select_research_stage(
        self,
        requirements: TaskRequirements,
        stage_decisions: Dict[str, StageDecision],
        reasoning_parts: List[str]
    ) -> None:
        """
        WHY: Research stage retrieves task-specific code examples before development.

        RESPONSIBILITY: Always run to provide context-rich examples to developers.
        """
        stage_decisions['research'] = StageDecision.REQUIRED
        reasoning_parts.append(
            "Research stage retrieves task-specific code examples for developers"
        )

    def _select_dependency_validation_stage(
        self,
        requirements: TaskRequirements,
        stage_decisions: Dict[str, StageDecision],
        reasoning_parts: List[str]
    ) -> None:
        """
        WHY: Dependency validation only needed if external dependencies detected.

        PATTERNS: Guard Clause - skip if no dependencies
        """
        # Guard: Skip if no external dependencies
        if not requirements.has_external_dependencies:
            stage_decisions['dependency_validation'] = StageDecision.SKIP
            reasoning_parts.append("No external dependencies detected, skipping validation")
            return

        # Require if dependencies detected
        stage_decisions['dependency_validation'] = StageDecision.REQUIRED

    def _select_development_stage(
        self,
        requirements: TaskRequirements,
        stage_decisions: Dict[str, StageDecision],
        reasoning_parts: List[str]
    ) -> None:
        """WHY: Development stage is always required (core pipeline)."""
        stage_decisions['development'] = StageDecision.REQUIRED

    def _select_arbitration_stage(
        self,
        requirements: TaskRequirements,
        stage_decisions: Dict[str, StageDecision],
        reasoning_parts: List[str]
    ) -> None:
        """
        WHY: Arbitration required when multiple developers compete.

        RESPONSIBILITY:
        - Adjudicator selects winning implementation
        - Only needed for dev groups with 2+ developers

        PATTERNS: Guard Clause - skip single developer
        """
        # Guard: Skip single developer
        if requirements.parallel_developers_recommended < 2:
            stage_decisions['arbitration'] = StageDecision.SKIP
            reasoning_parts.append("Single developer - skipping arbitration")
            return

        # Require for multiple developers
        stage_decisions['arbitration'] = StageDecision.REQUIRED
        reasoning_parts.append(
            f"Arbitration required: {requirements.parallel_developers_recommended} "
            f"developers competing, adjudicator must select winner"
        )

    def _select_code_review_stage(
        self,
        requirements: TaskRequirements,
        stage_decisions: Dict[str, StageDecision],
        reasoning_parts: List[str]
    ) -> None:
        """WHY: Code review stage is always required (core pipeline)."""
        stage_decisions['code_review'] = StageDecision.REQUIRED

    def _select_validation_stage(
        self,
        requirements: TaskRequirements,
        stage_decisions: Dict[str, StageDecision],
        reasoning_parts: List[str]
    ) -> None:
        """WHY: Validation stage is always required (core pipeline)."""
        stage_decisions['validation'] = StageDecision.REQUIRED

    def _select_integration_stage(
        self,
        requirements: TaskRequirements,
        stage_decisions: Dict[str, StageDecision],
        reasoning_parts: List[str]
    ) -> None:
        """WHY: Integration stage is always required (core pipeline)."""
        stage_decisions['integration'] = StageDecision.REQUIRED

    def _select_testing_stage(
        self,
        requirements: TaskRequirements,
        stage_decisions: Dict[str, StageDecision],
        reasoning_parts: List[str]
    ) -> None:
        """WHY: Testing stage is always required (core pipeline)."""
        stage_decisions['testing'] = StageDecision.REQUIRED

    def _select_uiux_stage(
        self,
        requirements: TaskRequirements,
        stage_decisions: Dict[str, StageDecision],
        reasoning_parts: List[str]
    ) -> None:
        """
        WHY: UI/UX stage only needed for frontend/UI/accessibility tasks.

        PATTERNS: Guard Clause - skip if no UI requirements
        """
        # Guard: Skip if no UI requirements
        if not (requirements.has_frontend or
                requirements.has_ui_components or
                requirements.has_accessibility_requirements):
            stage_decisions['uiux'] = StageDecision.SKIP
            reasoning_parts.append("No frontend/UI requirements detected, skipping UI/UX stage")
            return

        # Require for UI tasks
        stage_decisions['uiux'] = StageDecision.REQUIRED
        reasoning_parts.append(
            f"UI/UX stage required (frontend={requirements.has_frontend}, "
            f"ui_components={requirements.has_ui_components}, "
            f"a11y={requirements.has_accessibility_requirements})"
        )

    def _select_notebook_generation_stage(
        self,
        requirements: TaskRequirements,
        stage_decisions: Dict[str, StageDecision],
        reasoning_parts: List[str]
    ) -> None:
        """
        WHY: Notebook generation only needed for data science/ML/analysis tasks.

        PATTERNS: Guard Clause - skip if not notebook task
        """
        # Guard: Skip if not notebook task
        if not requirements.requires_notebook:
            stage_decisions['notebook_generation'] = StageDecision.SKIP
            return

        # Require for notebook tasks
        stage_decisions['notebook_generation'] = StageDecision.REQUIRED
        reasoning_parts.append("Notebook generation required for data analysis/ML task")

    def build_stage_lists(
        self,
        stage_decisions: Dict[str, StageDecision]
    ) -> Dict[str, List[str]]:
        """
        WHY: Convert stage decisions to filtered stage lists.

        RESPONSIBILITY:
        - Build list of stages to run
        - Build list of stages to skip
        - Maintain execution order

        Args:
            stage_decisions: Dictionary of stage decisions

        Returns:
            Dictionary with 'stages_to_run' and 'stages_to_skip' lists

        PATTERNS: Single Responsibility - only builds stage lists
        """
        stages_to_run = [
            stage for stage in self.ALL_STAGES
            if stage_decisions.get(stage, StageDecision.SKIP) in [
                StageDecision.REQUIRED,
                StageDecision.OPTIONAL
            ]
        ]

        stages_to_skip = [
            stage for stage in self.ALL_STAGES
            if stage_decisions.get(stage, StageDecision.SKIP) == StageDecision.SKIP
        ]

        return {
            'stages_to_run': stages_to_run,
            'stages_to_skip': stages_to_skip
        }
