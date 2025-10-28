#!/usr/bin/env python3
"""
Risk Identifier

WHAT: Identifies risk factors for Monte Carlo simulation.

WHY: Scans task descriptions for risk patterns and creates structured risk
factors with severity and probability estimates for simulation.

RESPONSIBILITY:
    - Scan for security, performance, database, integration, and complexity risks
    - Create structured RiskFactor objects
    - Estimate severity and probability
    - Suggest mitigations

PATTERNS:
    - Strategy Pattern: Different identification strategies per risk type
    - Factory Pattern: Creates RiskFactor objects
    - Guard Clause Pattern: Early returns for clarity
"""

import re
from typing import Dict, List, Optional
from intelligent_router import TaskRequirements
from intelligent_router_pkg.risk_factor import RiskFactor


class RiskIdentifier:
    """
    Identifies risk factors for Monte Carlo simulation.

    WHY: Scans task descriptions for risk patterns and creates structured
    risk factors with severity and probability estimates.
    """

    def __init__(self, risk_patterns: Dict[str, re.Pattern]):
        """
        Initialize risk identifier.

        Args:
            risk_patterns: Compiled regex patterns for risk detection
        """
        self.risk_patterns = risk_patterns

    def identify_risk_factors(
        self,
        card: Dict,
        requirements: TaskRequirements
    ) -> List[RiskFactor]:
        """
        Identify risk factors for Monte Carlo simulation.

        WHAT: Scans task description for risk patterns and creates structured
        risk factors with severity and probability estimates.

        Args:
            card: Kanban card with task details
            requirements: Analyzed task requirements

        Returns:
            List of identified risk factors
        """
        combined_text = f"{card.get('title', '')} {card.get('description', '')}".lower()
        risk_factors = []

        # Security risks
        security_risk = self._create_security_risk(combined_text)
        if security_risk:
            risk_factors.append(security_risk)

        # Performance risks
        if self.risk_patterns['performance'].search(combined_text):
            risk_factors.append(RiskFactor(
                risk_type='performance',
                description='Performance-critical task with scalability concerns',
                severity='medium',
                probability=0.25,
                mitigation='Add performance testing, load testing, profiling'
            ))

        # Database risks
        database_risk = self._create_database_risk(combined_text)
        if database_risk:
            risk_factors.append(database_risk)

        # Integration risks
        if self.risk_patterns['integration'].search(combined_text) or requirements.has_external_dependencies:
            risk_factors.append(RiskFactor(
                risk_type='dependency',
                description='External dependencies with potential breaking changes',
                severity='medium',
                probability=0.20,
                mitigation='API contract testing, mock servers, version pinning, fallback strategies'
            ))

        # Complexity risks
        if self.risk_patterns['complexity'].search(combined_text) or requirements.complexity == 'complex':
            risk_factors.append(RiskFactor(
                risk_type='complexity',
                description='High complexity with potential for underestimation',
                severity='high' if requirements.estimated_story_points >= 13 else 'medium',
                probability=0.35,
                mitigation='Break into smaller tasks, architecture review, incremental delivery'
            ))

        return risk_factors

    def _create_security_risk(self, combined_text: str) -> Optional[RiskFactor]:
        """
        Create security risk factor - extracted to eliminate nested conditionals.

        Returns None if no security risk patterns found.
        """
        if not self.risk_patterns['security'].search(combined_text):
            return None  # Early return guard

        # Determine severity based on critical keywords
        is_critical = 'critical' in combined_text or 'auth' in combined_text
        severity = 'high' if is_critical else 'medium'

        return RiskFactor(
            risk_type='security',
            description='Security-sensitive task requiring careful implementation',
            severity=severity,
            probability=0.3,
            mitigation='Add security review stage, penetration testing, OWASP guidelines'
        )

    def _create_database_risk(self, combined_text: str) -> Optional[RiskFactor]:
        """
        Create database risk factor - extracted to eliminate nested conditionals.

        Returns None if no database risk patterns found.
        """
        if not self.risk_patterns['database'].search(combined_text):
            return None  # Early return guard

        # Determine severity and probability based on migration presence
        is_migration = 'migration' in combined_text
        severity = 'critical' if is_migration else 'high'
        probability = 0.4 if is_migration else 0.2

        return RiskFactor(
            risk_type='database',
            description='Database changes with potential data loss or corruption',
            severity=severity,
            probability=probability,
            mitigation='Dry-run migration, rollback script, backup verification, staging test'
        )
