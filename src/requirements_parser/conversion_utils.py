from artemis_logger import get_logger
logger = get_logger('conversion_utils')
'\nRequirements Conversion Utilities\n\nWHY: Convert between different requirement representations\nRESPONSIBILITY: Map LLM output format to StructuredRequirements dataclass\nPATTERNS: Adapter pattern - adapts LLM format to our domain model\n'
from typing import Dict, Any, List
from datetime import datetime
from requirements_models import StructuredRequirements, FunctionalRequirement, NonFunctionalRequirement, Stakeholder, Constraint, Assumption, Priority, RequirementType, UseCase, DataRequirement, IntegrationRequirement

class RequirementsConverter:
    """
    Convert LLM output to StructuredRequirements

    WHY: LLM outputs simpler format than our rich domain model
    RESPONSIBILITY: Bridge the gap between LLM and domain model
    PATTERNS: Adapter pattern
    """

    def __init__(self, verbose: bool=False):
        """
        Initialize converter

        Args:
            verbose: Enable verbose logging
        """
        self.verbose = verbose

    def convert_llm_output_to_structured_requirements(self, llm_output: Dict[str, Any], project_name: str) -> StructuredRequirements:
        """
        Convert LLM JSON output to StructuredRequirements object

        WHY: Separate conversion logic from main parser
        RESPONSIBILITY: Map flat LLM structure to rich dataclass model

        Args:
            llm_output: LLM JSON output with simpler structure
            project_name: Project name for metadata

        Returns:
            StructuredRequirements object
        """
        nfr_data = llm_output.get('non_functional_requirements', {})
        functional_reqs = self._convert_functional_requirements(llm_output)
        non_functional_reqs = self._convert_non_functional_requirements(nfr_data)
        stakeholders = self._convert_actors_to_stakeholders(llm_output)
        constraints = self._convert_risks_to_constraints(llm_output)
        assumptions = self._convert_assumptions(llm_output)
        use_cases = self._convert_use_cases(llm_output)
        data_requirements = self._convert_data_requirements(llm_output)
        integration_requirements = self._convert_integration_requirements(llm_output)
        return StructuredRequirements(project_name=project_name, version='1.0', created_date=datetime.now().strftime('%Y-%m-%d'), executive_summary=llm_output.get('domain_context'), business_goals=llm_output.get('objectives', []), success_criteria=llm_output.get('acceptance_criteria', []), stakeholders=stakeholders, constraints=constraints, assumptions=assumptions, functional_requirements=functional_reqs, non_functional_requirements=non_functional_reqs, use_cases=use_cases, data_requirements=data_requirements, integration_requirements=integration_requirements)

    def _convert_functional_requirements(self, llm_output: Dict[str, Any]) -> List[FunctionalRequirement]:
        """
        Convert functional requirements from LLM output

        WHY: LLM outputs simple strings, we need rich objects
        RESPONSIBILITY: Create FunctionalRequirement objects from strings
        """
        functional_reqs = []
        for idx, req_text in enumerate(llm_output.get('functional_requirements', []), 1):
            functional_reqs.append(FunctionalRequirement(id=f'REQ-F-{idx:03d}', title=req_text[:100], description=req_text, priority=Priority.MEDIUM, acceptance_criteria=[f'Implements: {req_text[:50]}...']))
        return functional_reqs

    def _convert_non_functional_requirements(self, nfr_data: Dict[str, Any]) -> List[NonFunctionalRequirement]:
        """
        Convert non-functional requirements from LLM output

        WHY: NFRs have multiple categories (performance, security, etc.)
        RESPONSIBILITY: Create NFR objects from categorized data
        """
        non_functional_reqs = []
        nfr_idx = 1
        if 'performance' in nfr_data:
            nfr_idx = self._add_performance_requirements(nfr_data['performance'], non_functional_reqs, nfr_idx)
        for security_req in nfr_data.get('security', []):
            non_functional_reqs.append(NonFunctionalRequirement(id=f'REQ-NF-{nfr_idx:03d}', title=security_req[:100], description=security_req, type=RequirementType.SECURITY, priority=Priority.CRITICAL))
            nfr_idx += 1
        return non_functional_reqs

    def _convert_actors_to_stakeholders(self, llm_output: Dict[str, Any]) -> List[Stakeholder]:
        """
        Convert actors to stakeholders

        WHY: LLM outputs "actors", domain model uses "stakeholders"
        RESPONSIBILITY: Semantic mapping between concepts
        """
        stakeholders = []
        for actor in llm_output.get('actors', []):
            stakeholders.append(Stakeholder(name=actor.get('name', 'Unknown'), role=', '.join(actor.get('roles', [])), concerns=[f"Auth: {', '.join(actor.get('auth', []))}"]))
        return stakeholders

    def _convert_risks_to_constraints(self, llm_output: Dict[str, Any]) -> List[Constraint]:
        """
        Convert risks to constraints

        WHY: Risks are often constraints in disguise
        RESPONSIBILITY: Map risk concept to constraint model
        """
        constraints = []
        for risk in llm_output.get('risks', []):
            constraints.append(Constraint(type='risk', description=risk.get('item', ''), impact=risk.get('impact', 'M'), mitigation=risk.get('mitigation')))
        return constraints

    def _convert_assumptions(self, llm_output: Dict[str, Any]) -> List[Assumption]:
        """
        Convert assumptions from LLM output

        WHY: Simple list to rich objects
        RESPONSIBILITY: Create Assumption objects
        """
        return [Assumption(description=assumption, risk_if_false='Unknown') for assumption in llm_output.get('assumptions', [])]

    def _add_performance_requirements(self, perf_data: Dict[str, Any], non_functional_reqs: List[NonFunctionalRequirement], nfr_idx: int) -> int:
        """
        Add performance requirements

        WHY: Performance data needs special handling
        RESPONSIBILITY: Convert performance metrics to NFRs

        Returns:
            Updated NFR index
        """
        if 'p95_latency_ms' not in perf_data:
            return nfr_idx
        non_functional_reqs.append(NonFunctionalRequirement(id=f'REQ-NF-{nfr_idx:03d}', title=f"P95 Latency < {perf_data['p95_latency_ms']}ms", description=f"95th percentile latency must be under {perf_data['p95_latency_ms']} milliseconds", type=RequirementType.PERFORMANCE, priority=Priority.HIGH, metric='p95_latency_ms', target=f"< {perf_data['p95_latency_ms']}ms"))
        return nfr_idx + 1

    def _convert_use_cases(self, llm_output: Dict[str, Any]) -> List[UseCase]:
        """
        Convert use cases from LLM output if present

        WHY: Use cases may be included in LLM output or extracted separately
        RESPONSIBILITY: Convert use case data if available, otherwise return empty list

        Note: Use cases are typically extracted via extraction_engine in multi-step mode.
              This method handles the case where LLM output includes them directly.
        """
        use_cases = []
        use_case_data = llm_output.get('use_cases', [])
        for idx, uc in enumerate(use_case_data, 1):
            if isinstance(uc, dict):
                use_cases.append(UseCase(id=uc.get('id', f'UC-{idx:03d}'), title=uc.get('title', f'Use Case {idx}'), actor=uc.get('actor', 'User'), preconditions=uc.get('preconditions', []), main_flow=uc.get('main_flow', []), alternate_flows=uc.get('alternate_flows', {}), postconditions=uc.get('postconditions', []), related_requirements=uc.get('related_requirements', [])))
        return use_cases

    def _convert_data_requirements(self, llm_output: Dict[str, Any]) -> List[DataRequirement]:
        """
        Convert data requirements from LLM output if present

        WHY: Data entities may be included in LLM output or extracted separately
        RESPONSIBILITY: Convert data entity information if available

        Note: Data requirements are typically extracted via extraction_engine in multi-step mode.
              This method handles the case where LLM output includes data entities directly.
        """
        data_requirements = []
        data_entities = llm_output.get('data_entities', llm_output.get('data_requirements', []))
        for idx, entity in enumerate(data_entities, 1):
            if isinstance(entity, dict):
                data_requirements.append(DataRequirement(id=entity.get('id', f'REQ-D-{idx:03d}'), entity_name=entity.get('entity_name', entity.get('name', f'Entity{idx}')), description=entity.get('description', ''), attributes=entity.get('attributes', []), relationships=entity.get('relationships', []), volume=entity.get('volume'), retention=entity.get('retention'), compliance=entity.get('compliance', [])))
        return data_requirements

    def _convert_integration_requirements(self, llm_output: Dict[str, Any]) -> List[IntegrationRequirement]:
        """
        Convert integration requirements from LLM output if present

        WHY: Integrations may be included in LLM output or extracted separately
        RESPONSIBILITY: Convert integration information if available

        Note: Integration requirements are typically extracted via extraction_engine in multi-step mode.
              This method handles the case where LLM output includes integrations directly.
        """
        integration_requirements = []
        integrations = llm_output.get('integrations', llm_output.get('integration_requirements', []))
        for idx, integration in enumerate(integrations, 1):
            if isinstance(integration, dict):
                integration_requirements.append(IntegrationRequirement(id=integration.get('id', f'REQ-I-{idx:03d}'), system_name=integration.get('system_name', integration.get('name', f'System{idx}')), description=integration.get('description', ''), direction=integration.get('direction', 'bidirectional'), protocol=integration.get('protocol'), data_format=integration.get('data_format'), frequency=integration.get('frequency'), authentication=integration.get('authentication'), sla=integration.get('sla')))
        return integration_requirements

    def log(self, message: str):
        """Log message if verbose"""
        if self.verbose:
            
            logger.log(f'[RequirementsConverter] {message}', 'INFO')