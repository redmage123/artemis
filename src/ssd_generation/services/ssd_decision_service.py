#!/usr/bin/env python3
"""
SSD Decision Service

WHY: Intelligent decision-making for whether SSD generation is needed.
RESPONSIBILITY: Analyze task complexity/type to determine SSD necessity.
PATTERNS:
- Guard clauses (Pattern #10)
- next() for first match (Pattern #4)
- Functional composition (Pattern #0)
"""

from typing import Dict, Any


class SSDDecisionService:
    """
    Decides whether SSD generation is needed based on task characteristics

    WHY: Avoid unnecessary SSD generation for simple tasks (refactoring, docs).
    WHEN: Called at the start of SSD generation pipeline.
    """

    @staticmethod
    def should_generate_ssd(
        card: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Intelligently decide if SSD generation is needed

        Pattern #10: Guard clauses and early returns
        Pattern #4: Use next() for first match in skip conditions

        Skip SSD for:
        - Simple complexity tasks (refactors, small fixes)
        - Documentation-only tasks
        - Bug fixes (unless complex)
        - Minor updates/tweaks

        Require SSD for:
        - Medium/Complex features
        - New applications/services
        - API design
        - Database schema changes
        - Multi-component features

        Returns:
            Dict with 'needed' (bool), 'reason' (str), 'complexity', 'task_type'
        """
        workflow_plan = context.get('workflow_plan', {})
        complexity = workflow_plan.get('complexity', 'medium')
        task_type = workflow_plan.get('task_type', 'other')

        task_description = (
            card.get('description', '') +
            ' ' +
            card.get('title', '')
        ).lower()

        # Define skip conditions (task_type, keywords, reason)
        skip_conditions = [
            ('simple', None, "Simple complexity task doesn't require full SSD"),
            (None, ['refactor', 'cleanup', 'restructure'],
             "Refactoring task doesn't need full specification"),
            (None, ['documentation', 'readme', 'docs'],
             "Documentation task doesn't require SSD"),
            (None, ['fix typo', 'update comment', 'formatting'],
             "Minor update doesn't require SSD"),
            ('bugfix', ['small', 'minor', 'quick'],
             "Simple bug fix doesn't require SSD")
        ]

        # Pattern #4: Use next() to find first matching skip condition
        skip_match = next(
            (
                reason
                for task_type_check, keywords, reason in skip_conditions
                if (
                    # Check task type match
                    (task_type_check and complexity == task_type_check) or
                    # Check keyword match in description
                    (keywords and any(kw in task_description for kw in keywords))
                )
            ),
            None  # Default: no skip match
        )

        # If skip condition matched, return early (Pattern #10)
        if skip_match:
            return {
                "needed": False,
                "reason": skip_match,
                "complexity": complexity,
                "task_type": task_type
            }

        # Define require conditions (complexity/type combinations that NEED SSD)
        require_conditions = [
            (complexity in ['medium', 'complex'], "Medium/complex task benefits from formal specification"),
            (task_type == 'feature', "New feature requires comprehensive specification"),
            ('api' in task_description or 'endpoint' in task_description,
             "API development requires detailed specification"),
            ('database' in task_description or 'schema' in task_description,
             "Database changes require formal specification"),
            ('application' in task_description or 'service' in task_description,
             "New application/service requires SSD"),
            ('architecture' in task_description or 'design' in task_description,
             "Architectural work requires specification document")
        ]

        # Pattern #4: Use next() to find first require condition
        require_match = next(
            (
                reason
                for condition, reason in require_conditions
                if condition
            ),
            "Task scope warrants formal specification"  # Default require reason
        )

        return {
            "needed": True,
            "reason": require_match,
            "complexity": complexity,
            "task_type": task_type
        }
