#!/usr/bin/env python3
"""
WHY: Extract learning patterns from historical artifacts.
     Enables continuous improvement through data-driven recommendations.

RESPONSIBILITY:
- Analyze technology success rates from past solutions
- Generate recommendations based on historical patterns
- Extract common issues and avoidance patterns
- Calculate confidence levels for recommendations

PATTERNS:
- Strategy Pattern: Different analysis strategies (technology, success, issues)
- Builder Pattern: Build complex recommendations incrementally
- Command Pattern: Encapsulate analysis requests
"""

from typing import Dict, List, Optional, Any, Callable
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from itertools import chain


class PatternAnalyzer:
    """
    Analyzes historical artifacts to extract learning patterns.
    """

    def __init__(
        self,
        query_fn: Callable[[str, Optional[List[str]], int, Optional[Dict]], List[Dict]],
        log_fn: Optional[Callable[[str], None]] = None
    ):
        """
        Initialize pattern analyzer.

        Args:
            query_fn: Function to query artifacts
            log_fn: Optional logging function
        """
        self.query_fn = query_fn
        self.log_fn = log_fn or (lambda msg: None)

    def get_recommendations(
        self,
        task_description: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Get RAG-informed recommendations based on past experience.

        Args:
            task_description: Description of new task
            context: Additional context (technologies, priority, etc.)

        Returns:
            Dict with recommendations based on history
        """
        context = context or {}

        # Query for similar tasks
        similar_tasks = self.query_fn(
            task_description,
            ["research_report", "architecture_decision", "developer_solution"],
            10,
            None
        )

        # Guard: Handle no similar tasks
        if not similar_tasks:
            return self._empty_recommendations()

        # Extract patterns
        technologies = self._extract_technology_patterns(similar_tasks)
        success_patterns = self._extract_success_patterns(similar_tasks)
        issues = self._extract_issues(similar_tasks)

        # Generate recommendations
        based_on = self._build_based_on_history(technologies, success_patterns)
        recommendations = self._build_recommendations(technologies)
        avoid = self._build_avoidance_list(issues)
        confidence = self._calculate_confidence(similar_tasks)

        return {
            "based_on_history": based_on,
            "recommendations": recommendations if recommendations else ["Insufficient history for recommendations"],
            "avoid": avoid,
            "confidence": confidence,
            "similar_tasks_count": len(similar_tasks)
        }

    def extract_patterns(
        self,
        pattern_type: str = "technology_success_rates",
        time_window_days: int = 90
    ) -> Dict[str, Any]:
        """
        Extract learning patterns from stored artifacts.

        Args:
            pattern_type: Type of pattern to extract
            time_window_days: Time window for analysis

        Returns:
            Dict with extracted patterns
        """
        # Dispatch table for pattern extraction
        pattern_extractors = {
            "technology_success_rates": self._extract_technology_success_rates
        }

        # Guard: Check if pattern type is supported
        extractor = pattern_extractors.get(pattern_type)
        if not extractor:
            self.log_fn(f"⚠️  Unknown pattern type: {pattern_type}")
            return {}

        return extractor(time_window_days)

    def _extract_technology_success_rates(self, time_window_days: int) -> Dict[str, Any]:
        """
        Extract technology success rates from developer solutions.

        Args:
            time_window_days: Time window for analysis

        Returns:
            Technology success rate patterns
        """
        cutoff_date = datetime.utcnow() - timedelta(days=time_window_days)
        cutoff_str = cutoff_date.isoformat()

        # Get all developer solutions
        solutions = self.query_fn("", ["developer_solution"], 1000, None)

        # Calculate success rates per technology
        tech_stats = defaultdict(lambda: {
            "tasks_count": 0,
            "total_score": 0,
            "successes": 0
        })

        for solution in solutions:
            metadata = solution.get('metadata', {})

            # Guard: Check time window
            if metadata.get('timestamp', '') < cutoff_str:
                continue

            technologies = metadata.get('technologies', [])
            score = metadata.get('arbitration_score', 0)
            success = metadata.get('winner', False)

            # Update statistics
            for tech in technologies:
                tech_stats[tech]["tasks_count"] += 1
                tech_stats[tech]["total_score"] += score
                if success:
                    tech_stats[tech]["successes"] += 1

        # Calculate averages and recommendations
        patterns = {}
        for tech, stats in tech_stats.items():
            # Guard: Skip technologies with no tasks
            if stats["tasks_count"] == 0:
                continue

            avg_score = stats["total_score"] / stats["tasks_count"]
            success_rate = stats["successes"] / stats["tasks_count"]

            recommendation = self._determine_recommendation(avg_score, success_rate)

            patterns[tech] = {
                "tasks_count": stats["tasks_count"],
                "avg_score": round(avg_score, 1),
                "success_rate": round(success_rate, 2),
                "recommendation": recommendation
            }

        return patterns

    def _extract_technology_patterns(self, tasks: List[Dict]) -> Dict[str, Dict[str, Any]]:
        """Extract technology usage patterns from tasks."""
        technologies = defaultdict(lambda: {"count": 0, "avg_score": 0, "scores": []})

        for task in tasks:
            metadata = task.get('metadata', {})
            for tech in metadata.get('technologies', []):
                technologies[tech]["count"] += 1

        return dict(technologies)

    def _extract_success_patterns(self, tasks: List[Dict]) -> List[Dict[str, Any]]:
        """Extract success patterns from winning solutions."""
        return [
            {
                "approach": task['metadata'].get('approach', 'unknown'),
                "score": task['metadata'].get('arbitration_score', 0),
                "technologies": task['metadata'].get('technologies', [])
            }
            for task in tasks
            if task.get('artifact_type') == 'developer_solution'
            and task.get('metadata', {}).get('winner')
        ]

    def _extract_issues(self, tasks: List[Dict]) -> List[Dict[str, Any]]:
        """Extract issues from validation results."""
        return list(chain.from_iterable(
            task.get('metadata', {}).get('issues', [])
            for task in tasks
            if task.get('artifact_type') == 'validation_result'
        ))

    def _build_based_on_history(
        self,
        technologies: Dict[str, Dict[str, Any]],
        success_patterns: List[Dict[str, Any]]
    ) -> List[str]:
        """Build based on history list."""
        based_on = []

        # Technology usage
        top_techs = sorted(technologies.items(), key=lambda x: x[1]['count'], reverse=True)[:3]
        based_on.extend([
            f"Used {tech} in {data['count']} past similar tasks"
            for tech, data in top_techs
        ])

        # Success patterns
        based_on.extend([
            f"{pattern['approach']} approach scored {pattern['score']}/100"
            for pattern in success_patterns[:3]
        ])

        return based_on

    def _build_recommendations(self, technologies: Dict[str, Dict[str, Any]]) -> List[str]:
        """Build recommendations list."""
        top_techs = sorted(technologies.items(), key=lambda x: x[1]['count'], reverse=True)[:3]
        return [
            f"Consider {tech} (proven in {data['count']} similar tasks)"
            for tech, data in top_techs
            if data['count'] >= 2
        ]

    def _build_avoidance_list(self, issues: List[Dict[str, Any]]) -> List[str]:
        """Build avoidance recommendations list."""
        common_issues = Counter(issue.get('type', 'unknown') for issue in issues)
        return [
            f"Watch for {issue_type} issues (found in {count} similar tasks)"
            for issue_type, count in common_issues.items()
            if count >= 2
        ]

    def _calculate_confidence(self, similar_tasks: List[Dict]) -> str:
        """Calculate confidence level based on number of similar tasks."""
        count = len(similar_tasks)
        if count >= 5:
            return "HIGH"
        if count >= 2:
            return "MEDIUM"
        return "LOW"

    def _determine_recommendation(self, avg_score: float, success_rate: float) -> str:
        """Determine recommendation level based on score and success rate."""
        if avg_score >= 90 and success_rate >= 0.8:
            return "HIGHLY_RECOMMENDED"
        if avg_score >= 80 and success_rate >= 0.6:
            return "RECOMMENDED"
        return "CONSIDER_ALTERNATIVES"

    def _empty_recommendations(self) -> Dict[str, Any]:
        """Return empty recommendations structure."""
        return {
            "based_on_history": [],
            "recommendations": ["No similar tasks found in history"],
            "avoid": [],
            "confidence": "LOW",
            "similar_tasks_count": 0
        }
