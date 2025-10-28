#!/usr/bin/env python3
"""
Requirements Prompts

WHY: Centralized prompt templates for requirements analysis.
RESPONSIBILITY: Build LLM prompts for requirement extraction.
PATTERNS:
- Template Method pattern
- Single Responsibility (prompt building only)
"""

import json
from typing import Dict, Any


class RequirementsPrompts:
    """
    Prompt builders for requirements analysis

    WHY: Separation of concerns - prompts are separated from business logic.
    WHEN: Used by RequirementsAnalyzer to generate LLM prompts.
    """

    @staticmethod
    def build_requirements_analysis_prompt(
        task_title: str,
        task_description: str,
        context: Dict[str, Any]
    ) -> str:
        """Build prompt for requirements analysis"""
        return f"""You are a Senior Business Analyst tasked with analyzing software requirements.

**Task Title**: {task_title}

**Task Description**:
{task_description}

**Workflow Context**:
- Complexity: {context.get('workflow_plan', {}).get('complexity', 'medium')}
- Task Type: {context.get('workflow_plan', {}).get('task_type', 'feature')}

Analyze this task and provide a structured JSON response with:

1. **key_features**: List of main features/capabilities needed
2. **user_personas**: Who will use this? (roles/types of users)
3. **use_cases**: Primary use cases
4. **technical_domains**: Technical areas involved (e.g., backend, frontend, database, API)
5. **business_goals**: What business objectives does this achieve?
6. **success_metrics**: How will success be measured?

Provide response in JSON format:
```json
{{
  "key_features": ["feature1", "feature2", ...],
  "user_personas": ["persona1", "persona2", ...],
  "use_cases": ["use_case1", "use_case2", ...],
  "technical_domains": ["domain1", "domain2", ...],
  "business_goals": ["goal1", "goal2", ...],
  "success_metrics": ["metric1", "metric2", ...]
}}
```"""

    @staticmethod
    def build_executive_summary_prompt(
        card: Dict[str, Any],
        requirements_analysis: Dict[str, Any]
    ) -> str:
        """Build prompt for executive summary generation"""
        return f"""You are a Technical Documentation Specialist creating an Executive Summary for a Software Specification Document.

**Project**: {card.get('title', 'Untitled Project')}

**Requirements Analysis**:
{json.dumps(requirements_analysis, indent=2)}

Create:

1. **Executive Summary** (2-3 paragraphs):
   - High-level overview of the project
   - What problem it solves
   - Who benefits from it
   - Expected outcomes

2. **Business Case** (3-4 paragraphs):
   - Why this project is needed
   - Business value and ROI
   - Alignment with organizational goals
   - Risks of NOT doing this project

Provide response in JSON format:
```json
{{
  "executive_summary": "Your executive summary here...",
  "business_case": "Your business case here..."
}}
```"""

    @staticmethod
    def build_requirements_extraction_prompt(
        card: Dict[str, Any],
        requirements_analysis: Dict[str, Any]
    ) -> str:
        """Build prompt for structured requirements extraction"""
        return f"""You are a Requirements Engineer extracting detailed software requirements.

**Project**: {card.get('title', 'Untitled Project')}
**Description**: {card.get('description', '')}

**Analysis**:
{json.dumps(requirements_analysis, indent=2)}

Extract and categorize requirements into:

1. **Functional Requirements** (what the system must DO):
   - User-facing features
   - System behaviors
   - Data processing
   - Business logic

2. **Non-Functional Requirements** (how the system must PERFORM):
   - Performance (response time, throughput)
   - Scalability (users, data volume)
   - Security (authentication, authorization, encryption)
   - Reliability (uptime, fault tolerance)
   - Usability (UI/UX standards)
   - Maintainability (code quality, documentation)

3. **Business Requirements** (what business needs must be MET):
   - Compliance/regulatory
   - Budget constraints
   - Timeline/deadlines
   - Stakeholder needs

For each requirement provide:
- **description**: Clear, testable description
- **priority**: must_have | should_have | nice_to_have
- **acceptance_criteria**: List of criteria for completion
- **dependencies**: List of other requirements this depends on (use IDs like "FUNC-001")

Provide response in JSON format:
```json
{{
  "functional_requirements": [
    {{
      "description": "User can register with email and password",
      "priority": "must_have",
      "acceptance_criteria": [
        "Email validation is performed",
        "Password meets complexity requirements",
        "Confirmation email is sent"
      ],
      "dependencies": []
    }}
  ],
  "non_functional_requirements": [...],
  "business_requirements": [...]
}}
```"""

    @staticmethod
    def build_additional_sections_prompt(
        card: Dict[str, Any],
        requirements_analysis: Dict[str, Any]
    ) -> str:
        """Build prompt for constraints, assumptions, risks, success criteria"""
        return f"""You are a Project Manager documenting project constraints and risks.

**Project**: {card.get('title', 'Untitled Project')}

**Analysis**:
{json.dumps(requirements_analysis, indent=2)}

Document:

1. **Constraints**: Limitations we must work within
   - Technical constraints (platforms, languages, frameworks)
   - Resource constraints (budget, team size, timeline)
   - Regulatory constraints (compliance, legal)

2. **Assumptions**: What we're assuming to be true
   - User environment assumptions
   - Technical assumptions
   - Business assumptions

3. **Risks**: Potential problems and mitigation
   - Technical risks
   - Resource risks
   - Timeline risks
   - Dependency risks

4. **Success Criteria**: How we'll know we succeeded
   - Measurable outcomes
   - Acceptance criteria
   - Performance targets

Provide response in JSON format:
```json
{{
  "constraints": [
    "Must use Python 3.12+",
    "Budget limited to $50,000",
    "Must comply with GDPR"
  ],
  "assumptions": [
    "Users have modern browsers (Chrome 90+, Firefox 88+)",
    "Average 1000 concurrent users",
    "Database migration can be done during maintenance window"
  ],
  "risks": [
    "Third-party API may have rate limits (Mitigation: Implement caching)",
    "Key developer may leave (Mitigation: Knowledge sharing sessions)",
    "Timeline is aggressive (Mitigation: MVP approach with phased releases)"
  ],
  "success_criteria": [
    "System handles 10,000 requests/second with <200ms response time",
    "99.9% uptime over 30-day period",
    "All critical security vulnerabilities resolved",
    "Positive user feedback from 80% of beta testers"
  ]
}}
```"""
