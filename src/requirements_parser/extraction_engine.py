from artemis_logger import get_logger
logger = get_logger('extraction_engine')
'\nRequirements Extraction Engine\n\nWHY: Separate LLM-based extraction logic from main agent class\nRESPONSIBILITY: Execute multi-step LLM extraction for different requirement types\nPATTERNS: Strategy pattern for different extraction types\n'
from typing import List, Dict, Any, Optional
from datetime import datetime
from requirements_models import FunctionalRequirement, NonFunctionalRequirement, UseCase, DataRequirement, IntegrationRequirement, Stakeholder, Constraint, Assumption, Priority, RequirementType
from llm_client import LLMClient, LLMMessage
VALID_PRIORITIES = {p.value for p in Priority}
VALID_REQ_TYPES = {t.value for t in RequirementType}

class ExtractionEngine:
    """
    Multi-step LLM extraction engine

    WHY: Encapsulate all LLM extraction logic in one place
    RESPONSIBILITY: Convert raw text to structured requirements via LLM
    PATTERNS: Strategy pattern (each extract_* method is a strategy)
    """

    def __init__(self, llm: LLMClient, verbose: bool=False):
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
        prompt = f'You are a requirements analyst. Extract the following from this requirements document:\n\n1. Executive summary (2-3 sentences)\n2. Business goals (list)\n3. Success criteria (measurable outcomes)\n4. Glossary (key terms and definitions)\n\nRequirements Document:\n{raw_text}\n\nReturn JSON with keys: executive_summary, business_goals, success_criteria, glossary\nKeep it concise and factual.'
        response = self.llm.generate_text(messages=[LLMMessage(role='user', content=prompt)])
        result = self._parse_json_response(response.content)
        return result or {'executive_summary': None, 'business_goals': [], 'success_criteria': [], 'glossary': {}}

    def extract_functional_requirements(self, raw_text: str) -> List[FunctionalRequirement]:
        """
        Extract functional requirements with LLM

        WHY: Core requirement extraction step
        RESPONSIBILITY: Identify what system must do
        """
        prompt = f'You are a requirements analyst. Extract ALL functional requirements from this document.\n\nFor each functional requirement, provide:\n- id: REQ-F-XXX (sequential numbering)\n- title: Short descriptive title\n- description: What the system must do\n- priority: critical/high/medium/low/nice_to_have\n- user_story: As a [user], I want [goal], so that [benefit] (if applicable)\n- acceptance_criteria: List of testable criteria\n- estimated_effort: small/medium/large/xl\n- tags: Relevant tags for categorization\n\nRequirements Document:\n{raw_text}\n\nReturn JSON array of functional requirements. Be thorough and extract ALL requirements.'
        response = self.llm.generate_text(messages=[LLMMessage(role='user', content=prompt)])
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
        prompt = f'You are a requirements analyst. Extract ALL non-functional requirements from this document.\n\nNon-functional requirements include:\n- Performance (response time, throughput, scalability)\n- Security (authentication, authorization, encryption)\n- Compliance (GDPR, HIPAA, SOC2, etc.)\n- Usability (user experience, accessibility)\n- Reliability (uptime, availability, fault tolerance)\n- Maintainability (code quality, documentation)\n\nFor each non-functional requirement, provide:\n- id: REQ-NF-XXX (sequential numbering)\n- title: Short descriptive title\n- description: The requirement details\n- type: functional/non_functional/performance/security/compliance/usability/accessibility/integration/data/business\n- priority: critical/high/medium/low/nice_to_have\n- metric: How to measure (if applicable)\n- target: Target value (e.g., "< 200ms", "> 99.9% uptime")\n- acceptance_criteria: List of testable criteria\n- tags: Relevant tags\n\nRequirements Document:\n{raw_text}\n\nReturn JSON array of non-functional requirements.'
        response = self.llm.generate_text(messages=[LLMMessage(role='user', content=prompt)])
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
        prompt = f'Extract use cases from this requirements document.\n\nFor each use case, provide:\n- id: UC-XXX\n- title: Use case name\n- actor: Who performs this use case\n- preconditions: What must be true before\n- main_flow: Step-by-step main scenario\n- alternate_flows: Alternative scenarios (dict)\n- postconditions: System state after\n- related_requirements: Related requirement IDs\n\nRequirements Document:\n{raw_text}\n\nReturn JSON array of use cases.'
        response = self.llm.generate_text(messages=[LLMMessage(role='user', content=prompt)])
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
        prompt = f'Extract data requirements and data models from this document.\n\nFor each data entity, provide:\n- id: REQ-D-XXX\n- entity_name: Name of the data entity\n- description: What this entity represents\n- attributes: List of attributes with name, type, required\n- relationships: Relationships to other entities\n- volume: Expected data volume\n- retention: Data retention policy\n- compliance: Compliance requirements (GDPR, etc.)\n\nRequirements Document:\n{raw_text}\n\nReturn JSON array of data requirements. Only extract if data models are mentioned.'
        response = self.llm.generate_text(messages=[LLMMessage(role='user', content=prompt)])
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
        prompt = f'Extract integration requirements with external systems from this document.\n\nFor each integration, provide:\n- id: REQ-I-XXX\n- system_name: Name of external system\n- description: What the integration does\n- direction: inbound/outbound/bidirectional\n- protocol: REST/GraphQL/gRPC/SOAP/etc\n- data_format: JSON/XML/CSV/etc\n- frequency: real-time/batch/scheduled\n- authentication: OAuth/API key/etc\n- sla: Service level agreement\n\nRequirements Document:\n{raw_text}\n\nReturn JSON array of integration requirements. Only extract if integrations are mentioned.'
        response = self.llm.generate_text(messages=[LLMMessage(role='user', content=prompt)])
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
        prompt = f'Identify stakeholders from this requirements document.\n\nFor each stakeholder, provide:\n- name: Name or role\n- role: Job title/role\n- contact: Contact info (if mentioned)\n- concerns: Key concerns/interests\n\nRequirements Document:\n{raw_text}\n\nReturn JSON array of stakeholders.'
        response = self.llm.generate_text(messages=[LLMMessage(role='user', content=prompt)])
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
        prompt = f'Identify constraints from this requirements document.\n\nConstraints include:\n- Technical constraints (technology stack, platforms)\n- Business constraints (budget, timeline)\n- Regulatory constraints (compliance, legal)\n\nFor each constraint, provide:\n- type: technical/business/regulatory/timeline/budget\n- description: The constraint\n- impact: high/medium/low\n- mitigation: How to address (if mentioned)\n\nRequirements Document:\n{raw_text}\n\nReturn JSON array of constraints.'
        response = self.llm.generate_text(messages=[LLMMessage(role='user', content=prompt)])
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
        prompt = f'Identify assumptions from this requirements document.\n\nFor each assumption, provide:\n- description: The assumption\n- risk_if_false: Risk if assumption is wrong\n- validation_needed: true/false\n\nRequirements Document:\n{raw_text}\n\nReturn JSON array of assumptions.'
        response = self.llm.generate_text(messages=[LLMMessage(role='user', content=prompt)])
        result = self._parse_json_response(response.content)
        if not result or not isinstance(result, list):
            return []
        assumptions = []
        for a in result:
            assumption = self._build_assumption(a)
            if assumption:
                assumptions.append(assumption)
        return assumptions

    def _build_functional_requirement(self, req_data: Dict[str, Any], idx: int) -> Optional[FunctionalRequirement]:
        """Build FunctionalRequirement from LLM data"""
        try:
            priority_str = req_data.get('priority', 'medium')
            priority = Priority(priority_str) if priority_str in VALID_PRIORITIES else Priority.MEDIUM
            return FunctionalRequirement(id=req_data.get('id', f'REQ-F-{idx:03d}'), title=req_data.get('title', ''), description=req_data.get('description', ''), priority=priority, user_story=req_data.get('user_story'), acceptance_criteria=req_data.get('acceptance_criteria', []), dependencies=req_data.get('dependencies', []), estimated_effort=req_data.get('estimated_effort'), tags=req_data.get('tags', []))
        except Exception as e:
            if self.verbose:
                
                logger.log(f'⚠️  Error parsing functional requirement {idx}: {e}', 'INFO')
            return None

    def _build_non_functional_requirement(self, req_data: Dict[str, Any], idx: int) -> Optional[NonFunctionalRequirement]:
        """Build NonFunctionalRequirement from LLM data"""
        try:
            priority_str = req_data.get('priority', 'medium')
            priority = Priority(priority_str) if priority_str in VALID_PRIORITIES else Priority.MEDIUM
            type_str = req_data.get('type', 'non_functional')
            req_type = RequirementType(type_str) if type_str in VALID_REQ_TYPES else RequirementType.NON_FUNCTIONAL
            return NonFunctionalRequirement(id=req_data.get('id', f'REQ-NF-{idx:03d}'), title=req_data.get('title', ''), description=req_data.get('description', ''), type=req_type, priority=priority, metric=req_data.get('metric'), target=req_data.get('target'), acceptance_criteria=req_data.get('acceptance_criteria', []), tags=req_data.get('tags', []))
        except Exception as e:
            if self.verbose:
                
                logger.log(f'⚠️  Error parsing non-functional requirement {idx}: {e}', 'INFO')
            return None

    def _build_use_case(self, uc_data: Dict[str, Any], idx: int) -> Optional[UseCase]:
        """Build UseCase from LLM data"""
        try:
            return UseCase(id=uc_data.get('id', f'UC-{idx:03d}'), title=uc_data.get('title', ''), actor=uc_data.get('actor', ''), preconditions=uc_data.get('preconditions', []), main_flow=uc_data.get('main_flow', []), alternate_flows=uc_data.get('alternate_flows', {}), postconditions=uc_data.get('postconditions', []), related_requirements=uc_data.get('related_requirements', []))
        except Exception as e:
            if self.verbose:
                
                logger.log(f'⚠️  Error parsing use case {idx}: {e}', 'INFO')
            return None

    def _build_data_requirement(self, data: Dict[str, Any], idx: int) -> Optional[DataRequirement]:
        """Build DataRequirement from LLM data"""
        try:
            return DataRequirement(id=data.get('id', f'REQ-D-{idx:03d}'), entity_name=data.get('entity_name', ''), description=data.get('description', ''), attributes=data.get('attributes', []), relationships=data.get('relationships', []), volume=data.get('volume'), retention=data.get('retention'), compliance=data.get('compliance', []))
        except Exception as e:
            if self.verbose:
                
                logger.log(f'⚠️  Error parsing data requirement {idx}: {e}', 'INFO')
            return None

    def _build_integration_requirement(self, integration: Dict[str, Any], idx: int) -> Optional[IntegrationRequirement]:
        """Build IntegrationRequirement from LLM data"""
        try:
            return IntegrationRequirement(id=integration.get('id', f'REQ-I-{idx:03d}'), system_name=integration.get('system_name', ''), description=integration.get('description', ''), direction=integration.get('direction', 'bidirectional'), protocol=integration.get('protocol'), data_format=integration.get('data_format'), frequency=integration.get('frequency'), authentication=integration.get('authentication'), sla=integration.get('sla'))
        except Exception as e:
            if self.verbose:
                
                logger.log(f'⚠️  Error parsing integration requirement {idx}: {e}', 'INFO')
            return None

    def _build_stakeholder(self, s: Dict[str, Any]) -> Optional[Stakeholder]:
        """Build Stakeholder from LLM data"""
        try:
            return Stakeholder(name=s.get('name', ''), role=s.get('role', ''), contact=s.get('contact'), concerns=s.get('concerns', []))
        except Exception as e:
            if self.verbose:
                
                logger.log(f'⚠️  Error parsing stakeholder: {e}', 'INFO')
            return None

    def _build_constraint(self, c: Dict[str, Any]) -> Optional[Constraint]:
        """Build Constraint from LLM data"""
        try:
            return Constraint(type=c.get('type', 'technical'), description=c.get('description', ''), impact=c.get('impact', 'medium'), mitigation=c.get('mitigation'))
        except Exception as e:
            if self.verbose:
                
                logger.log(f'⚠️  Error parsing constraint: {e}', 'INFO')
            return None

    def _build_assumption(self, a: Dict[str, Any]) -> Optional[Assumption]:
        """Build Assumption from LLM data"""
        try:
            return Assumption(description=a.get('description', ''), risk_if_false=a.get('risk_if_false', ''), validation_needed=a.get('validation_needed', True))
        except Exception as e:
            if self.verbose:
                
                logger.log(f'⚠️  Error parsing assumption: {e}', 'INFO')
            return None

    def _parse_json_response(self, response: str) -> Any:
        """Parse JSON from LLM response (handle markdown code blocks)"""
        import json
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return self._extract_json_from_markdown_blocks(response)

    def _extract_json_from_markdown_blocks(self, response: str) -> Any:
        """Extract JSON from markdown code blocks"""
        import json
        if '```json' in response:
            start = response.find('```json') + 7
            end = response.find('```', start)
            json_str = response[start:end].strip()
            return json.loads(json_str)
        if '```' in response:
            start = response.find('```') + 3
            end = response.find('```', start)
            json_str = response[start:end].strip()
            return json.loads(json_str)
        if self.verbose:
            
            logger.log(f'⚠️  Failed to parse JSON from LLM response', 'INFO')
        return None