#!/usr/bin/env python3
"""
Requirements Extraction Engine

WHY: Separate LLM-based extraction logic from main agent class
RESPONSIBILITY: Execute multi-step LLM extraction for different requirement types
PATTERNS: Strategy pattern for different extraction types
"""

from typing import List, Dict, Any, Optional
from datetime import datetime

from requirements_models import (
    FunctionalRequirement,
    NonFunctionalRequirement,
    UseCase,
    DataRequirement,
    IntegrationRequirement,
    Stakeholder,
    Constraint,
    Assumption,
    Priority,
    RequirementType
)
from llm_client import LLMClient, LLMMessage

# Performance: Pre-compute valid enum values for O(1) lookup
VALID_PRIORITIES = {p.value for p in Priority}
VALID_REQ_TYPES = {t.value for t in RequirementType}


class ExtractionEngine:
    """
    Multi-step LLM extraction engine

    WHY: Encapsulate all LLM extraction logic in one place
    RESPONSIBILITY: Convert raw text to structured requirements via LLM
    PATTERNS: Strategy pattern (each extract_* method is a strategy)
    """

    def __init__(self, llm: LLMClient, verbose: bool = False):
        """
        Initialize extraction engine

        Args:
            llm: LLM client for making extraction calls
            verbose: Enable verbose logging
        """
        self.llm = llm
        self.verbose = verbose

    def extract_overview(self, raw_text: str, project_name: str) -> Dict[str, Any]:
        """
        Extract project overview, goals, and success criteria

        WHY: First step in multi-step extraction
        RESPONSIBILITY: Get high-level project metadata
        """
        prompt = f"""You are a requirements analyst. Extract the following from this requirements document:

1. Executive summary (2-3 sentences)
2. Business goals (list)
3. Success criteria (measurable outcomes)
4. Glossary (key terms and definitions)

Requirements Document:
{raw_text}

Return JSON with keys: executive_summary, business_goals, success_criteria, glossary
Keep it concise and factual."""

        response = self.llm.generate_text(messages=[LLMMessage(role="user", content=prompt)])
        result = self._parse_json_response(response.content)

        return result or {
            "executive_summary": None,
            "business_goals": [],
            "success_criteria": [],
            "glossary": {}
        }

    def extract_functional_requirements(self, raw_text: str) -> List[FunctionalRequirement]:
        """
        Extract functional requirements with LLM

        WHY: Core requirement extraction step
        RESPONSIBILITY: Identify what system must do
        """
        prompt = f"""You are a requirements analyst. Extract ALL functional requirements from this document.

For each functional requirement, provide:
- id: REQ-F-XXX (sequential numbering)
- title: Short descriptive title
- description: What the system must do
- priority: critical/high/medium/low/nice_to_have
- user_story: As a [user], I want [goal], so that [benefit] (if applicable)
- acceptance_criteria: List of testable criteria
- estimated_effort: small/medium/large/xl
- tags: Relevant tags for categorization

Requirements Document:
{raw_text}

Return JSON array of functional requirements. Be thorough and extract ALL requirements."""

        response = self.llm.generate_text(messages=[LLMMessage(role="user", content=prompt)])
        result = self._parse_json_response(response.content)

        if not result or not isinstance(result, list):
            return []

        functional_reqs = []
        for idx, req_data in enumerate(result, 1):
            req = self._build_functional_requirement(req_data, idx)
            if req:
                functional_reqs.append(req)

        return functional_reqs

    def extract_non_functional_requirements(self, raw_text: str) -> List[NonFunctionalRequirement]:
        """
        Extract non-functional requirements (performance, security, etc.)

        WHY: NFRs are often implicit and need careful extraction
        RESPONSIBILITY: Identify quality attributes and constraints
        """
        prompt = f"""You are a requirements analyst. Extract ALL non-functional requirements from this document.

Non-functional requirements include:
- Performance (response time, throughput, scalability)
- Security (authentication, authorization, encryption)
- Compliance (GDPR, HIPAA, SOC2, etc.)
- Usability (user experience, accessibility)
- Reliability (uptime, availability, fault tolerance)
- Maintainability (code quality, documentation)

For each non-functional requirement, provide:
- id: REQ-NF-XXX (sequential numbering)
- title: Short descriptive title
- description: The requirement details
- type: functional/non_functional/performance/security/compliance/usability/accessibility/integration/data/business
- priority: critical/high/medium/low/nice_to_have
- metric: How to measure (if applicable)
- target: Target value (e.g., "< 200ms", "> 99.9% uptime")
- acceptance_criteria: List of testable criteria
- tags: Relevant tags

Requirements Document:
{raw_text}

Return JSON array of non-functional requirements."""

        response = self.llm.generate_text(messages=[LLMMessage(role="user", content=prompt)])
        result = self._parse_json_response(response.content)

        if not result or not isinstance(result, list):
            return []

        non_functional_reqs = []
        for idx, req_data in enumerate(result, 1):
            req = self._build_non_functional_requirement(req_data, idx)
            if req:
                non_functional_reqs.append(req)

        return non_functional_reqs

    def extract_use_cases(self, raw_text: str) -> List[UseCase]:
        """
        Extract use cases and user scenarios

        WHY: Use cases describe system behavior from user perspective
        RESPONSIBILITY: Capture user interactions and workflows
        """
        prompt = f"""Extract use cases from this requirements document.

For each use case, provide:
- id: UC-XXX
- title: Use case name
- actor: Who performs this use case
- preconditions: What must be true before
- main_flow: Step-by-step main scenario
- alternate_flows: Alternative scenarios (dict)
- postconditions: System state after
- related_requirements: Related requirement IDs

Requirements Document:
{raw_text}

Return JSON array of use cases."""

        response = self.llm.generate_text(messages=[LLMMessage(role="user", content=prompt)])
        result = self._parse_json_response(response.content)

        if not result or not isinstance(result, list):
            return []

        use_cases = []
        for idx, uc_data in enumerate(result, 1):
            uc = self._build_use_case(uc_data, idx)
            if uc:
                use_cases.append(uc)

        return use_cases

    def extract_data_requirements(self, raw_text: str) -> List[DataRequirement]:
        """
        Extract data models and data requirements

        WHY: Data requirements define information architecture
        RESPONSIBILITY: Identify data entities and their relationships
        """
        prompt = f"""Extract data requirements and data models from this document.

For each data entity, provide:
- id: REQ-D-XXX
- entity_name: Name of the data entity
- description: What this entity represents
- attributes: List of attributes with name, type, required
- relationships: Relationships to other entities
- volume: Expected data volume
- retention: Data retention policy
- compliance: Compliance requirements (GDPR, etc.)

Requirements Document:
{raw_text}

Return JSON array of data requirements. Only extract if data models are mentioned."""

        response = self.llm.generate_text(messages=[LLMMessage(role="user", content=prompt)])
        result = self._parse_json_response(response.content)

        if not result or not isinstance(result, list):
            return []

        data_reqs = []
        for idx, data in enumerate(result, 1):
            req = self._build_data_requirement(data, idx)
            if req:
                data_reqs.append(req)

        return data_reqs

    def extract_integration_requirements(self, raw_text: str) -> List[IntegrationRequirement]:
        """
        Extract external system integration requirements

        WHY: Integrations are critical architectural decisions
        RESPONSIBILITY: Identify external dependencies and interfaces
        """
        prompt = f"""Extract integration requirements with external systems from this document.

For each integration, provide:
- id: REQ-I-XXX
- system_name: Name of external system
- description: What the integration does
- direction: inbound/outbound/bidirectional
- protocol: REST/GraphQL/gRPC/SOAP/etc
- data_format: JSON/XML/CSV/etc
- frequency: real-time/batch/scheduled
- authentication: OAuth/API key/etc
- sla: Service level agreement

Requirements Document:
{raw_text}

Return JSON array of integration requirements. Only extract if integrations are mentioned."""

        response = self.llm.generate_text(messages=[LLMMessage(role="user", content=prompt)])
        result = self._parse_json_response(response.content)

        if not result or not isinstance(result, list):
            return []

        integration_reqs = []
        for idx, integration in enumerate(result, 1):
            req = self._build_integration_requirement(integration, idx)
            if req:
                integration_reqs.append(req)

        return integration_reqs

    def extract_stakeholders(self, raw_text: str) -> List[Stakeholder]:
        """
        Extract stakeholder information

        WHY: Stakeholders drive requirements and priorities
        RESPONSIBILITY: Identify who cares about what
        """
        prompt = f"""Identify stakeholders from this requirements document.

For each stakeholder, provide:
- name: Name or role
- role: Job title/role
- contact: Contact info (if mentioned)
- concerns: Key concerns/interests

Requirements Document:
{raw_text}

Return JSON array of stakeholders."""

        response = self.llm.generate_text(messages=[LLMMessage(role="user", content=prompt)])
        result = self._parse_json_response(response.content)

        if not result or not isinstance(result, list):
            return []

        stakeholders = []
        for s in result:
            stakeholder = self._build_stakeholder(s)
            if stakeholder:
                stakeholders.append(stakeholder)

        return stakeholders

    def extract_constraints(self, raw_text: str) -> List[Constraint]:
        """
        Extract project constraints

        WHY: Constraints limit solution space
        RESPONSIBILITY: Identify boundaries and limitations
        """
        prompt = f"""Identify constraints from this requirements document.

Constraints include:
- Technical constraints (technology stack, platforms)
- Business constraints (budget, timeline)
- Regulatory constraints (compliance, legal)

For each constraint, provide:
- type: technical/business/regulatory/timeline/budget
- description: The constraint
- impact: high/medium/low
- mitigation: How to address (if mentioned)

Requirements Document:
{raw_text}

Return JSON array of constraints."""

        response = self.llm.generate_text(messages=[LLMMessage(role="user", content=prompt)])
        result = self._parse_json_response(response.content)

        if not result or not isinstance(result, list):
            return []

        constraints = []
        for c in result:
            constraint = self._build_constraint(c)
            if constraint:
                constraints.append(constraint)

        return constraints

    def extract_assumptions(self, raw_text: str) -> List[Assumption]:
        """
        Extract project assumptions

        WHY: Assumptions are hidden risks
        RESPONSIBILITY: Make implicit assumptions explicit
        """
        prompt = f"""Identify assumptions from this requirements document.

For each assumption, provide:
- description: The assumption
- risk_if_false: Risk if assumption is wrong
- validation_needed: true/false

Requirements Document:
{raw_text}

Return JSON array of assumptions."""

        response = self.llm.generate_text(messages=[LLMMessage(role="user", content=prompt)])
        result = self._parse_json_response(response.content)

        if not result or not isinstance(result, list):
            return []

        assumptions = []
        for a in result:
            assumption = self._build_assumption(a)
            if assumption:
                assumptions.append(assumption)

        return assumptions

    def _build_functional_requirement(
        self,
        req_data: Dict[str, Any],
        idx: int
    ) -> Optional[FunctionalRequirement]:
        """Build FunctionalRequirement from LLM data"""
        try:
            priority_str = req_data.get('priority', 'medium')
            priority = Priority(priority_str) if priority_str in VALID_PRIORITIES else Priority.MEDIUM

            return FunctionalRequirement(
                id=req_data.get('id', f'REQ-F-{idx:03d}'),
                title=req_data.get('title', ''),
                description=req_data.get('description', ''),
                priority=priority,
                user_story=req_data.get('user_story'),
                acceptance_criteria=req_data.get('acceptance_criteria', []),
                dependencies=req_data.get('dependencies', []),
                estimated_effort=req_data.get('estimated_effort'),
                tags=req_data.get('tags', [])
            )
        except Exception as e:
            if self.verbose:
                print(f"⚠️  Error parsing functional requirement {idx}: {e}")
            return None

    def _build_non_functional_requirement(
        self,
        req_data: Dict[str, Any],
        idx: int
    ) -> Optional[NonFunctionalRequirement]:
        """Build NonFunctionalRequirement from LLM data"""
        try:
            priority_str = req_data.get('priority', 'medium')
            priority = Priority(priority_str) if priority_str in VALID_PRIORITIES else Priority.MEDIUM

            type_str = req_data.get('type', 'non_functional')
            req_type = RequirementType(type_str) if type_str in VALID_REQ_TYPES else RequirementType.NON_FUNCTIONAL

            return NonFunctionalRequirement(
                id=req_data.get('id', f'REQ-NF-{idx:03d}'),
                title=req_data.get('title', ''),
                description=req_data.get('description', ''),
                type=req_type,
                priority=priority,
                metric=req_data.get('metric'),
                target=req_data.get('target'),
                acceptance_criteria=req_data.get('acceptance_criteria', []),
                tags=req_data.get('tags', [])
            )
        except Exception as e:
            if self.verbose:
                print(f"⚠️  Error parsing non-functional requirement {idx}: {e}")
            return None

    def _build_use_case(self, uc_data: Dict[str, Any], idx: int) -> Optional[UseCase]:
        """Build UseCase from LLM data"""
        try:
            return UseCase(
                id=uc_data.get('id', f'UC-{idx:03d}'),
                title=uc_data.get('title', ''),
                actor=uc_data.get('actor', ''),
                preconditions=uc_data.get('preconditions', []),
                main_flow=uc_data.get('main_flow', []),
                alternate_flows=uc_data.get('alternate_flows', {}),
                postconditions=uc_data.get('postconditions', []),
                related_requirements=uc_data.get('related_requirements', [])
            )
        except Exception as e:
            if self.verbose:
                print(f"⚠️  Error parsing use case {idx}: {e}")
            return None

    def _build_data_requirement(
        self,
        data: Dict[str, Any],
        idx: int
    ) -> Optional[DataRequirement]:
        """Build DataRequirement from LLM data"""
        try:
            return DataRequirement(
                id=data.get('id', f'REQ-D-{idx:03d}'),
                entity_name=data.get('entity_name', ''),
                description=data.get('description', ''),
                attributes=data.get('attributes', []),
                relationships=data.get('relationships', []),
                volume=data.get('volume'),
                retention=data.get('retention'),
                compliance=data.get('compliance', [])
            )
        except Exception as e:
            if self.verbose:
                print(f"⚠️  Error parsing data requirement {idx}: {e}")
            return None

    def _build_integration_requirement(
        self,
        integration: Dict[str, Any],
        idx: int
    ) -> Optional[IntegrationRequirement]:
        """Build IntegrationRequirement from LLM data"""
        try:
            return IntegrationRequirement(
                id=integration.get('id', f'REQ-I-{idx:03d}'),
                system_name=integration.get('system_name', ''),
                description=integration.get('description', ''),
                direction=integration.get('direction', 'bidirectional'),
                protocol=integration.get('protocol'),
                data_format=integration.get('data_format'),
                frequency=integration.get('frequency'),
                authentication=integration.get('authentication'),
                sla=integration.get('sla')
            )
        except Exception as e:
            if self.verbose:
                print(f"⚠️  Error parsing integration requirement {idx}: {e}")
            return None

    def _build_stakeholder(self, s: Dict[str, Any]) -> Optional[Stakeholder]:
        """Build Stakeholder from LLM data"""
        try:
            return Stakeholder(
                name=s.get('name', ''),
                role=s.get('role', ''),
                contact=s.get('contact'),
                concerns=s.get('concerns', [])
            )
        except Exception as e:
            if self.verbose:
                print(f"⚠️  Error parsing stakeholder: {e}")
            return None

    def _build_constraint(self, c: Dict[str, Any]) -> Optional[Constraint]:
        """Build Constraint from LLM data"""
        try:
            return Constraint(
                type=c.get('type', 'technical'),
                description=c.get('description', ''),
                impact=c.get('impact', 'medium'),
                mitigation=c.get('mitigation')
            )
        except Exception as e:
            if self.verbose:
                print(f"⚠️  Error parsing constraint: {e}")
            return None

    def _build_assumption(self, a: Dict[str, Any]) -> Optional[Assumption]:
        """Build Assumption from LLM data"""
        try:
            return Assumption(
                description=a.get('description', ''),
                risk_if_false=a.get('risk_if_false', ''),
                validation_needed=a.get('validation_needed', True)
            )
        except Exception as e:
            if self.verbose:
                print(f"⚠️  Error parsing assumption: {e}")
            return None

    def _parse_json_response(self, response: str) -> Any:
        """Parse JSON from LLM response (handle markdown code blocks)"""
        import json

        try:
            # Try direct JSON parse
            return json.loads(response)
        except json.JSONDecodeError:
            return self._extract_json_from_markdown_blocks(response)

    def _extract_json_from_markdown_blocks(self, response: str) -> Any:
        """Extract JSON from markdown code blocks"""
        import json

        # Try extracting from markdown code block
        if "```json" in response:
            start = response.find("```json") + 7
            end = response.find("```", start)
            json_str = response[start:end].strip()
            return json.loads(json_str)

        if "```" in response:
            start = response.find("```") + 3
            end = response.find("```", start)
            json_str = response[start:end].strip()
            return json.loads(json_str)

        if self.verbose:
            print(f"⚠️  Failed to parse JSON from LLM response")
        return None
