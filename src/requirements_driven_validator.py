#!/usr/bin/env python3
"""
Requirements-Driven Validation System

Analyzes requirements → Selects workflow → Validates with appropriate criteria.
Eliminates "one-size-fits-all TDD" problem.
"""

from typing import Dict, Optional
from pathlib import Path
from enum import Enum
from dataclasses import dataclass, asdict


class WorkflowType(Enum):
    """Workflow strategies"""
    TDD = "tdd"  # Test-Driven: tests first, minimal code
    QUALITY_DRIVEN = "quality_driven"  # Requirements first, comprehensive output
    VISUAL_TEST = "visual_test"  # Visual + accessibility
    CONTENT_VALIDATION = "content_validation"  # Structure + content


class ArtifactType(Enum):
    """Artifact types"""
    CODE = "code"
    NOTEBOOK = "notebook"
    UI = "ui"
    DOCUMENTATION = "documentation"
    DEMO = "demo"
    VISUALIZATION = "visualization"


@dataclass
class ValidationStrategy:
    """Complete validation strategy from requirements"""
    artifact_type: ArtifactType
    workflow: WorkflowType
    quality_criteria: Dict
    validator_class: str

    def to_dict(self):
        """
        Convert validation strategy to dictionary format.

        Returns:
            Dictionary representation of validation strategy for serialization
        """
        return {
            'artifact_type': self.artifact_type.value,
            'workflow': self.workflow.value,
            'quality_criteria': self.quality_criteria,
            'validator_class': self.validator_class
        }


class RequirementsDrivenValidator:
    """
    Core component: Requirements → Workflow → Validation

    Replaces hardcoded TDD with intelligent workflow selection.
    """

    def __init__(self, logger=None):
        self.logger = logger

        # Artifact detection keywords (priority order)
        self.keywords = {
            ArtifactType.NOTEBOOK: ['jupyter', '.ipynb', 'notebook', 'data analysis'],
            ArtifactType.UI: ['react', 'vue', 'component', 'frontend', 'ui'],
            ArtifactType.VISUALIZATION: ['chart', 'plotly', 'dashboard', 'viz'],
            ArtifactType.DEMO: ['demo', 'presentation', 'showcase'],
            ArtifactType.DOCUMENTATION: ['documentation', 'readme', 'guide'],
        }

        # Workflow mappings
        self.workflow_map = {
            ArtifactType.CODE: WorkflowType.TDD,
            ArtifactType.NOTEBOOK: WorkflowType.QUALITY_DRIVEN,
            ArtifactType.UI: WorkflowType.VISUAL_TEST,
            ArtifactType.DOCUMENTATION: WorkflowType.CONTENT_VALIDATION,
            ArtifactType.DEMO: WorkflowType.QUALITY_DRIVEN,
            ArtifactType.VISUALIZATION: WorkflowType.QUALITY_DRIVEN,
        }

        # Validator mappings
        self.validator_map = {
            ArtifactType.CODE: 'CodeQualityValidator',
            ArtifactType.NOTEBOOK: 'NotebookQualityValidator',
            ArtifactType.UI: 'UIQualityValidator',
            ArtifactType.DOCUMENTATION: 'DocumentationValidator',
            ArtifactType.DEMO: 'DemoValidator',
            ArtifactType.VISUALIZATION: 'VisualizationValidator',
        }

        # Criteria extraction strategy map (replaces if/elif chain)
        self.criteria_extractors = {
            ArtifactType.NOTEBOOK: self._extract_notebook_criteria,
            ArtifactType.UI: self._extract_ui_criteria,
            ArtifactType.CODE: self._extract_code_criteria,
        }

    def analyze_requirements(self,
                           task_title: str,
                           task_description: str,
                           parsed_requirements: Optional[Dict] = None) -> ValidationStrategy:
        """
        Main entry point: Analyze requirements and return validation strategy.

        Args:
            task_title: Task title
            task_description: Task description
            parsed_requirements: Optional parsed requirements from requirements_parser_agent

        Returns:
            ValidationStrategy with artifact type, workflow, criteria, validator
        """
        # Detect artifact type
        artifact_type = self._detect_artifact_type(
            task_title, task_description, parsed_requirements
        )

        # Extract quality criteria
        quality_criteria = self._extract_quality_criteria(
            artifact_type, task_title, task_description, parsed_requirements
        )

        # Get workflow and validator
        workflow = self.workflow_map.get(artifact_type, WorkflowType.TDD)
        validator_class = self.validator_map.get(artifact_type, 'CodeQualityValidator')

        strategy = ValidationStrategy(
            artifact_type=artifact_type,
            workflow=workflow,
            quality_criteria=quality_criteria,
            validator_class=validator_class
        )

        if self.logger:
            self.logger.log(f"📋 Validation Strategy: {artifact_type.value} → {workflow.value}", "INFO")

        return strategy

    def _detect_artifact_type(self, title: str, description: str, requirements: Optional[Dict]) -> ArtifactType:
        """Detect artifact type from requirements"""
        combined = f"{title} {description}".lower()

        # Check parsed requirements first (early return)
        if self._has_artifact_type_in_requirements(requirements):
            return ArtifactType(requirements['artifact_type'])

        # Keyword matching (priority order)
        detected_type = self._match_artifact_by_keywords(combined)
        if detected_type:
            return detected_type

        return ArtifactType.CODE  # Default

    def _has_artifact_type_in_requirements(self, requirements: Optional[Dict]) -> bool:
        """Check if requirements contain artifact_type"""
        if not requirements:
            return False
        return 'artifact_type' in requirements

    def _match_artifact_by_keywords(self, combined_text: str) -> Optional[ArtifactType]:
        """Match artifact type by keywords"""
        for artifact_type in [
            ArtifactType.NOTEBOOK,
            ArtifactType.UI,
            ArtifactType.VISUALIZATION,
            ArtifactType.DEMO,
            ArtifactType.DOCUMENTATION,
        ]:
            if self._has_matching_keywords(artifact_type, combined_text):
                return artifact_type
        return None

    def _has_matching_keywords(self, artifact_type: ArtifactType, text: str) -> bool:
        """Check if text contains keywords for artifact type"""
        keywords = self.keywords.get(artifact_type, [])
        return any(kw in text for kw in keywords)

    def _extract_quality_criteria(self,
                                  artifact_type: ArtifactType,
                                  title: str,
                                  description: str,
                                  requirements: Optional[Dict]) -> Dict:
        """Extract quality criteria based on artifact type"""
        combined = f"{title} {description}".lower()

        # Use strategy pattern: lookup extractor in map
        extractor = self.criteria_extractors.get(artifact_type, lambda x: {})
        criteria = extractor(combined)

        # Merge with parsed requirements if available
        self._merge_parsed_quality_criteria(criteria, requirements)

        return criteria

    def _extract_notebook_criteria(self, combined: str) -> Dict:
        """Extract quality criteria for notebook artifacts"""
        import re
        criteria = {}

        # Cell count
        match = re.search(r'(\d+)\+?\s*cells?', combined)
        criteria['min_cells'] = int(match.group(1)) if match else 8

        # Visualizations
        criteria['requires_visualizations'] = any(
            w in combined for w in ['chart', 'graph', 'plot', 'viz']
        )

        # Visualization library
        viz_lib = self._detect_visualization_library(combined)
        if viz_lib:
            criteria['visualization_library'] = viz_lib

        # Data source
        data_source = self._detect_data_source(combined)
        if data_source:
            criteria['data_source'] = data_source

        return criteria

    def _detect_visualization_library(self, combined: str) -> Optional[str]:
        """Detect visualization library from text"""
        for lib in ['plotly', 'matplotlib', 'chart.js']:
            if lib in combined:
                return lib
        return None

    def _detect_data_source(self, combined: str) -> Optional[str]:
        """Detect data source file from text"""
        import re
        match = re.search(r'([\w_]+\.(?:json|csv|xlsx))', combined)
        if not match:
            return None
        return match.group(1)

    def _extract_ui_criteria(self, combined: str) -> Dict:
        """Extract quality criteria for UI artifacts"""
        return {
            'accessibility_required': any(
                w in combined for w in ['accessibility', 'wcag', 'a11y']
            ),
            'responsive_required': 'responsive' in combined
        }

    def _extract_code_criteria(self, combined: str) -> Dict:
        """Extract quality criteria for code artifacts"""
        return {
            'min_test_coverage': 0.8,
            'requires_unit_tests': True
        }

    def _merge_parsed_quality_criteria(self, criteria: Dict, requirements: Optional[Dict]) -> None:
        """Merge parsed quality criteria into existing criteria dict"""
        if not requirements:
            return
        if 'quality_criteria' not in requirements:
            return
        criteria.update(requirements['quality_criteria'])
