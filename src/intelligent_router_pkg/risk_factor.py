#!/usr/bin/env python3
"""
Risk Factor Model

WHAT: Data structure representing identified risk factors in a task.

WHY: Explicit risk identification enables Thermodynamic Computing to
quantify uncertainty and Monte Carlo simulation to assess probability.
Makes risk factors structured and analyzable rather than informal observations.

RESPONSIBILITY:
    - Store risk type, description, severity, and probability
    - Provide structured risk data for Monte Carlo simulation
    - Support risk mitigation planning

PATTERNS:
    - Value Object: Immutable data structure
    - Data Transfer Object: Carries risk data between components
"""

from dataclasses import dataclass


@dataclass
class RiskFactor:
    """
    Identified risk factor in a task.

    WHY: Explicit risk identification enables Thermodynamic Computing to
    quantify uncertainty and Monte Carlo simulation to assess probability.

    Attributes:
        risk_type: Category of risk (technical, complexity, dependency, security, performance)
        description: Human-readable description of the risk
        severity: Risk severity level (low, medium, high, critical)
        probability: Estimated probability of risk occurring (0.0-1.0)
        mitigation: Suggested mitigation strategy
    """
    risk_type: str  # 'technical', 'complexity', 'dependency', 'security', 'performance'
    description: str
    severity: str  # 'low', 'medium', 'high', 'critical'
    probability: float  # 0.0-1.0 estimated probability of risk occurring
    mitigation: str  # Suggested mitigation strategy
