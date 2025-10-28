#!/usr/bin/env python3
"""
WHY: Validate Jupyter notebooks using functional composition
RESPONSIBILITY: Check notebooks for cells, visualizations, documentation, data
PATTERNS: Template Method (extends base), Composition (functional checks)

Notebook validator ensures rich, production-quality notebooks.
"""

import json
from typing import Dict, List, Optional
from pathlib import Path

from artifacts.quality.base import ArtifactQualityValidator
from artifacts.quality.models import ValidationResult
from artifacts.quality.aggregator import ResultAggregator


class NotebookQualityValidator(ArtifactQualityValidator):
    """
    Validates Jupyter notebooks using functional validation checks.

    WHY: Notebooks need comprehensive validation (cells, viz, docs, data).
    RESPONSIBILITY: Execute validation checks, aggregate results.
    PATTERNS: Template Method, Functional composition (check functions).
    """

    def validate(self, artifact_path: Path) -> ValidationResult:
        """
        Validate notebook quality using functional composition.

        WHY: Composition of small check functions enables easy extension.

        Args:
            artifact_path: Path to notebook (.ipynb file)

        Returns:
            ValidationResult with aggregated check results
        """
        notebook = self._load_notebook(artifact_path)
        cells = notebook.get('cells', [])

        # Define validation checks as functions
        checks = [
            self._check_cell_count(cells),
            self._check_visualizations(cells),
            self._check_documentation(cells),
            self._check_data_loading(cells)
        ]

        # Filter out None values (checks that don't apply)
        active_checks = [c for c in checks if c is not None]

        # Aggregate results
        return ResultAggregator.aggregate(active_checks)

    def generate_validation_prompt(self, requirements: str) -> str:
        """
        Generate comprehensive prompt for notebook creation.

        WHY: Rich prompts produce rich notebooks.

        Args:
            requirements: User requirements

        Returns:
            Comprehensive prompt with quality criteria
        """
        min_cells = self.quality_criteria.get('min_cells', 8)
        viz_lib = self.quality_criteria.get('visualization_library', 'plotly')
        data_source = self.quality_criteria.get('data_source', '')

        prompt = f"""Create a COMPREHENSIVE, production-quality Jupyter notebook.

**CRITICAL: This is NOT a minimal implementation. Create complete, rich output.**

Requirements:
{requirements}

Quality Criteria (ALL must be met):
- Minimum {min_cells} cells (mix of code and markdown)
- Multiple visualizations using {viz_lib}
- Clear markdown documentation explaining each step
- Real data from {data_source if data_source else 'appropriate source'}
- Interactive elements where applicable
- Professional quality suitable for presentation

Structure:
1. Title and overview (markdown)
2. Import libraries (code)
3. Load and explore data (code + markdown)
4. Create multiple visualizations (code + markdown)
5. Analysis and insights (markdown)
6. Conclusions (markdown)

Return JSON format:
{{{{
    "files": [
        {{{{"path": "notebook.ipynb", "content": "notebook JSON content here"}}}}
    ]
}}}}
"""
        return prompt

    def _load_notebook(self, path: Path) -> Dict:
        """Load notebook JSON"""
        with open(path, 'r') as f:
            return json.load(f)

    def _check_cell_count(self, cells: List) -> Dict:
        """Check minimum cell count"""
        min_cells = self.quality_criteria.get('min_cells', 5)
        count = len(cells)
        passed = count >= min_cells

        return {
            'name': 'min_cells',
            'passed': passed,
            'feedback': None if passed else f"Only {count} cells, expected {min_cells}+"
        }

    def _check_visualizations(self, cells: List) -> Optional[Dict]:
        """Check for visualization library usage"""
        requires_viz = self.quality_criteria.get('requires_visualizations')

        # Guard clause - visualization not required
        if not requires_viz:
            return None

        return self._validate_viz_presence(cells)

    def _validate_viz_presence(self, cells: List) -> Dict:
        """Validate visualization library is present"""
        viz_lib = self.quality_criteria.get('visualization_library', 'plotly')
        has_viz = any(
            viz_lib.lower() in str(cell.get('source', '')).lower()
            for cell in cells
        )

        return {
            'name': 'has_visualizations',
            'passed': has_viz,
            'feedback': None if has_viz else f"Missing {viz_lib} visualizations"
        }

    def _check_documentation(self, cells: List) -> Dict:
        """Check for markdown documentation"""
        markdown_count = sum(1 for c in cells if c.get('cell_type') == 'markdown')
        passed = markdown_count >= 2

        return {
            'name': 'has_documentation',
            'passed': passed,
            'feedback': None if passed else "Insufficient markdown documentation"
        }

    def _check_data_loading(self, cells: List) -> Optional[Dict]:
        """Check for data source loading"""
        data_source = self.quality_criteria.get('data_source')

        # Guard clause - data source not specified
        if not data_source:
            return None

        return self._validate_data_source(cells, data_source)

    def _validate_data_source(self, cells: List, data_source: str) -> Dict:
        """Validate data source is loaded"""
        has_data = any(
            data_source in str(cell.get('source', ''))
            for cell in cells
        )

        return {
            'name': 'loads_data',
            'passed': has_data,
            'feedback': None if has_data else f"Missing data loading from {data_source}"
        }
