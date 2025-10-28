"""
Module: agents/developer/report_generator.py

WHY: Generate structured solution reports for developer workflows.
RESPONSIBILITY: Create and save TDD and quality-driven workflow reports.
PATTERNS: Builder Pattern, Guard Clauses.

This module handles:
- Generating TDD workflow reports (Red/Green/Refactor)
- Generating quality-driven workflow reports
- Saving reports to JSON files
- Structuring test results and file lists

EXTRACTED FROM: standalone_developer_agent.py (lines 1020-2758)
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List
from llm_client import LLMResponse


class ReportGenerator:
    """
    Generates solution reports for developer workflows

    WHY: Centralize report generation with consistent structure
    PATTERNS: Builder Pattern, Guard Clauses
    """

    def __init__(self, developer_name: str, developer_type: str, llm_provider: str):
        """
        Initialize report generator

        Args:
            developer_name: Name of developer (e.g., "developer-a")
            developer_type: Type of developer (e.g., "conservative")
            llm_provider: LLM provider used (e.g., "openai")
        """
        self.developer_name = developer_name
        self.developer_type = developer_type
        self.llm_provider = llm_provider

    def finalize_solution_report(self, results: Dict, output_dir: Path) -> Dict:
        """
        Generate and save solution report (handles both TDD and quality-driven results)

        Args:
            results: Workflow results (TDD or quality-driven structure)
            output_dir: Directory to save report to

        Returns:
            Solution report dict
        """
        # Check if TDD results (has red/green/refactor structure)
        if self._is_tdd_results(results):
            solution_report = self.generate_tdd_solution_report(
                test_files=results['red']['test_files'],
                implementation_files=results['green']['implementation_files'],
                refactored_files=results['refactor']['refactored_files'],
                red_results=results['red']['test_results'],
                green_results=results['green']['test_results'],
                refactor_results=results['refactor']['test_results'],
                output_dir=output_dir
            )
        else:
            # Quality-driven results (simple structure)
            solution_report = {
                'workflow': 'quality_driven',
                'implementation_files': results.get('implementation_files', []),
                'success': True,
                'output_dir': str(output_dir)
            }

        # Write solution report
        report_path = output_dir / "solution_report.json"
        with open(report_path, 'w') as f:
            json.dump(solution_report, f, indent=2)

        return solution_report

    def generate_tdd_solution_report(
        self,
        test_files: List[Dict],
        implementation_files: List[Dict],
        refactored_files: List[Dict],
        red_results: Dict,
        green_results: Dict,
        refactor_results: Dict,
        output_dir: Path
    ) -> Dict:
        """
        Generate TDD workflow solution report

        Args:
            test_files: List of test file dicts from Red phase
            implementation_files: List of implementation file dicts from Green phase
            refactored_files: List of refactored file dicts from Refactor phase
            red_results: Red phase test results
            green_results: Green phase test results
            refactor_results: Refactor phase test results
            output_dir: Output directory

        Returns:
            TDD solution report dict
        """
        return {
            "developer": self.developer_name,
            "approach": self.developer_type,
            "status": "COMPLETED",
            "timestamp": datetime.now().isoformat(),
            "tdd_workflow": {
                "red_phase": {
                    "tests_generated": len(test_files),
                    "test_files": [f["path"] for f in test_files],
                    "tests_failed": red_results.get("failed", 0),
                    "tests_passed": red_results.get("passed", 0),
                    "status": "PASS" if red_results.get("failed", 0) > 0 else "WARNING"
                },
                "green_phase": {
                    "implementation_files": [f["path"] for f in implementation_files],
                    "tests_passed": green_results.get("passed", 0),
                    "tests_failed": green_results.get("failed", 0),
                    "status": "PASS" if green_results.get("failed", 0) == 0 else "FAIL"
                },
                "refactor_phase": {
                    "refactored_files": [f["path"] for f in refactored_files],
                    "tests_passed": refactor_results.get("passed", 0),
                    "tests_failed": refactor_results.get("failed", 0),
                    "status": "PASS" if refactor_results.get("failed", 0) == 0 else "FAIL"
                }
            },
            "final_test_results": refactor_results,
            "all_files": {
                "tests": [f["path"] for f in test_files],
                "implementation": [f["path"] for f in refactored_files]
            }
        }

    def generate_solution_report(
        self,
        implementation: Dict,
        files_written: List[str],
        llm_response: LLMResponse
    ) -> Dict:
        """
        Generate solution report for quality-driven workflow

        Args:
            implementation: Implementation dict from LLM
            files_written: List of file paths written
            llm_response: LLM response object

        Returns:
            Solution report dict
        """
        return {
            "developer": self.developer_name,
            "approach": self.developer_type,
            "status": "COMPLETED",
            "timestamp": datetime.now().isoformat(),
            "llm_provider": self.llm_provider,
            "llm_model": llm_response.model,
            "tokens_used": llm_response.usage,
            "implementation_files": [
                f["path"] for f in implementation.get("implementation_files", [])
            ],
            "test_files": [
                f["path"] for f in implementation.get("test_files", [])
            ],
            "files_written": files_written,
            "tdd_workflow": implementation.get("tdd_workflow", {}),
            "solid_principles_applied": implementation.get("solid_principles_applied", []),
            "approach_summary": implementation.get("approach_summary", ""),
            "full_implementation": implementation
        }

    def _is_tdd_results(self, results: Dict) -> bool:
        """
        Check if results are from TDD workflow (has red/green/refactor structure)

        Args:
            results: Workflow results dict

        Returns:
            True if TDD results, False otherwise
        """
        return 'red' in results and 'green' in results and 'refactor' in results


__all__ = [
    "ReportGenerator"
]
