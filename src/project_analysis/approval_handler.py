#!/usr/bin/env python3
"""
WHY: Handle user approval workflow for analysis findings
RESPONSIBILITY: Present findings to user and collect approval decisions
PATTERNS: Single Responsibility, Guard clauses, Dispatch table for approval logic

This module handles the user interaction layer of project analysis, presenting
findings in a clear format and processing user approval decisions.
"""

from typing import Dict, List

from project_analysis.models import ApprovalOptions


class UserApprovalHandler:
    """
    WHY: Separate UI concerns from analysis logic
    RESPONSIBILITY: Handle user approval flow (presentation + decision processing)
    PATTERNS: Single Responsibility (UI/approval only), Guard clauses

    Single Responsibility: Handle user approval flow.
    Presents findings to user and collects approval decision, keeping UI
    concerns separate from analysis logic.
    """

    def present_findings(self, analysis: Dict) -> str:
        """
        Format analysis results for user presentation.

        Args:
            analysis: Analysis summary from ProjectAnalysisEngine containing:
                - critical_count: Number of critical issues
                - high_count: Number of high-priority issues
                - medium_count: Number of medium-priority issues
                - critical_issues: List of critical Issue objects
                - high_issues: List of high-priority Issue objects

        Returns:
            Formatted string for display
        """
        output = []
        output.append("=" * 60)
        output.append("PROJECT ANALYSIS COMPLETE")
        output.append("=" * 60)
        output.append("")
        output.append("SUMMARY:")
        output.append(f"  ⚠️  {analysis['critical_count']} CRITICAL issues found")
        output.append(f"  ⚠️  {analysis['high_count']} HIGH-PRIORITY improvements")
        output.append(f"  💡 {analysis['medium_count']} MEDIUM-PRIORITY enhancements")
        output.append("")

        # Show critical issues
        if analysis['critical_issues']:
            output.append("CRITICAL ISSUES (Must Address):")
            for i, issue in enumerate(analysis['critical_issues'], 1):
                output.append(f"{i}. [{issue.category}] {issue.description}")
                output.append(f"   → {issue.suggestion}")
                output.append(f"   Impact: {issue.impact}")
                output.append("")

        # Show high priority
        if analysis['high_issues']:
            output.append("HIGH-PRIORITY IMPROVEMENTS:")
            for i, issue in enumerate(analysis['high_issues'], 1):
                output.append(f"{i}. [{issue.category}] {issue.description}")
                output.append(f"   → {issue.suggestion}")
                output.append("")

        output.append("=" * 60)
        output.append("USER APPROVAL REQUIRED")
        output.append("=" * 60)
        output.append("")
        output.append("What would you like to do?")
        output.append("1. APPROVE ALL - Accept all critical and high-priority changes")
        output.append("2. APPROVE CRITICAL ONLY - Accept only critical security/compliance fixes")
        output.append("3. CUSTOM - Let me choose which suggestions to approve")
        output.append("4. REJECT - Proceed with original task as-is")
        output.append("5. MODIFY - I want to suggest different changes")
        output.append("")

        return "\n".join(output)

    def get_approval_decision(self, analysis: Dict, user_choice: str) -> Dict:
        """
        Process user's approval decision.

        Args:
            analysis: Analysis summary containing:
                - critical_issues: List of critical Issue objects
                - high_issues: List of high-priority Issue objects
            user_choice: User's selection (1-5)

        Returns:
            Dict with approval decision:
            - approved: Boolean indicating if any changes approved
            - approved_issues: List of approved Issue objects
            - approved_count: Number of approved issues
        """
        approved_issues = self._get_approved_issues(analysis, user_choice)

        return {
            "approved": len(approved_issues) > 0,
            "approved_issues": approved_issues,
            "approved_count": len(approved_issues)
        }

    def _get_approved_issues(self, analysis: Dict, user_choice: str) -> List:
        """
        Determine which issues to approve based on user choice.

        Dispatch table pattern using guard clauses.

        Args:
            analysis: Analysis summary containing issue lists
            user_choice: User's selection (1-5)

        Returns:
            List of approved issues
        """
        # Dispatch table for user choices
        approval_handlers = {
            "1": lambda: analysis['critical_issues'] + analysis['high_issues'],  # APPROVE ALL
            "2": lambda: analysis['critical_issues'],  # APPROVE CRITICAL ONLY
            "4": lambda: [],  # REJECT
        }

        # Use dispatch table if choice exists
        if user_choice in approval_handlers:
            return approval_handlers[user_choice]()

        # CUSTOM or MODIFY would require interactive flow
        # Default to critical issues for safety
        return analysis['critical_issues']
