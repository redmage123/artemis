#!/usr/bin/env python3
"""
Advanced Validation Reviewer

WHY: Integrate static analysis and property-based testing into code review
RESPONSIBILITY: Coordinate advanced validation techniques
PATTERNS: Facade pattern, Guard clauses

Reduces hallucinations by:
- Static analysis catches type errors and bugs
- Property-based tests find edge cases
- Symbolic execution proves correctness mathematically
- Formal specifications verify requirements compliance
"""

from typing import Dict, List, Optional
from pathlib import Path

from artemis_logger import get_logger
from validation import (
    StaticAnalysisValidator,
    StaticAnalysisResult,
    PropertyBasedTestGenerator,
    PropertyTestSuite,
    SymbolicExecutionValidator,
    SymbolicExecutionResult,
    FormalSpecificationMatcher,
    FormalMatchingResult,
)


class AdvancedValidationReviewer:
    """
    Advanced validation using static analysis and property-based testing.

    WHY: Comprehensive validation reduces hallucinations
    RESPONSIBILITY: Orchestrate multiple validation techniques
    PATTERNS: Facade, Guard clauses
    """

    def __init__(
        self,
        logger,
        enable_static_analysis: bool = True,
        enable_property_tests: bool = True,
        enable_symbolic_execution: bool = True,
        enable_formal_specs: bool = True,
        static_analysis_config: Optional[Dict] = None
    ):
        """
        Initialize advanced validation reviewer.

        Args:
            logger: Logger instance
            enable_static_analysis: Run static analysis tools
            enable_property_tests: Generate property-based tests
            enable_symbolic_execution: Run symbolic execution
            enable_formal_specs: Match formal specifications
            static_analysis_config: Configuration for static analysis
        """
        self.logger = logger
        self.enable_static_analysis = enable_static_analysis
        self.enable_property_tests = enable_property_tests
        self.enable_symbolic_execution = enable_symbolic_execution
        self.enable_formal_specs = enable_formal_specs

        # Initialize validators
        config = static_analysis_config or {}
        self.static_validator = StaticAnalysisValidator(
            enable_type_checking=config.get('enable_type_checking', True),
            enable_linting=config.get('enable_linting', True),
            enable_complexity_check=config.get('enable_complexity_check', True),
            max_complexity=config.get('max_complexity', 10),
            logger=logger
        )

        self.property_generator = PropertyBasedTestGenerator(logger=logger)

        self.symbolic_executor = SymbolicExecutionValidator(
            timeout_seconds=10,
            max_paths=100,
            logger=logger
        )

        self.spec_matcher = FormalSpecificationMatcher(
            enable_z3_verification=True,
            timeout_seconds=10,
            logger=logger
        )

    def review_code(
        self,
        code: str,
        developer_name: str,
        language: str = "python",
        requirements: Optional[str] = None
    ) -> Dict:
        """
        Review code using advanced validation techniques.

        WHY: Main entry point for advanced validation
        RESPONSIBILITY: Run all enabled validation techniques

        Args:
            code: Source code to validate
            developer_name: Name of developer (for reporting)
            language: Programming language
            requirements: Optional requirements document for formal specs

        Returns:
            Dict with validation results
        """
        self.logger.info(f"Advanced validation for {developer_name}")

        result = {
            "developer": developer_name,
            "language": language,
            "static_analysis": None,
            "property_tests": None,
            "symbolic_execution": None,
            "formal_specs": None,
            "overall_passed": True,
            "issues_found": [],
            "suggestions": []
        }

        # Run static analysis
        if self.enable_static_analysis:
            static_result = self._run_static_analysis(code, language)
            result["static_analysis"] = static_result

            # Update overall result
            if not static_result["passed"]:
                result["overall_passed"] = False
                result["issues_found"].extend(static_result.get("issues", []))

        # Generate property-based tests
        if self.enable_property_tests:
            property_result = self._generate_property_tests(code)
            result["property_tests"] = property_result

            # Add suggestion to run generated tests
            if property_result.get("test_suites"):
                result["suggestions"].append(
                    "Run generated property-based tests to verify code correctness"
                )

        # Run symbolic execution
        if self.enable_symbolic_execution:
            symbolic_result = self._run_symbolic_execution(code)
            result["symbolic_execution"] = symbolic_result

            # Update overall result
            if not symbolic_result.get("verified", True):
                result["overall_passed"] = False
                result["issues_found"].extend(symbolic_result.get("errors", []))

        # Match formal specifications
        if self.enable_formal_specs:
            formal_result = self._match_formal_specs(code, requirements)
            result["formal_specs"] = formal_result

            # Update overall result
            if not formal_result.get("satisfied", True):
                result["overall_passed"] = False
                result["suggestions"].append(
                    "Address formal specification violations"
                )

        return result

    def _run_static_analysis(self, code: str, language: str) -> Dict:
        """
        Run static analysis on code.

        WHY: Separate static analysis logic
        RESPONSIBILITY: Execute static analysis, format results
        PATTERNS: Guard clauses
        """
        self.logger.info("  🔍 Running static analysis...")

        # Run static analysis
        analysis_result = self.static_validator.validate_code(
            code=code,
            language=language
        )

        # Format for code review
        formatted_result = {
            "enabled": True,
            "passed": analysis_result.passed,
            "error_count": analysis_result.error_count,
            "warning_count": analysis_result.warning_count,
            "info_count": analysis_result.info_count,
            "summary": analysis_result.summary,
            "issues": []
        }

        # Format issues
        for issue in analysis_result.issues:
            formatted_result["issues"].append({
                "file": issue.file,
                "line": issue.line,
                "column": issue.column,
                "severity": issue.severity,
                "tool": issue.tool,
                "code": issue.code,
                "message": issue.message
            })

        # Log summary
        self._log_static_analysis_summary(analysis_result)

        return formatted_result

    def _log_static_analysis_summary(self, result: StaticAnalysisResult) -> None:
        """
        Log static analysis summary.

        WHY: Provide visibility into validation results
        RESPONSIBILITY: Log appropriate messages
        PATTERNS: Guard clauses for different result types
        """
        # Guard: All passed
        if result.passed and result.warning_count == 0:
            self.logger.log("  ✅ Static analysis: All checks passed", "SUCCESS")
            return

        # Guard: Has errors
        if result.error_count > 0:
            self.logger.log(
                f"  ❌ Static analysis: {result.error_count} error(s), "
                f"{result.warning_count} warning(s)",
                "ERROR"
            )

            # Log sample errors
            errors = [i for i in result.issues if i.severity == "error"]
            for issue in errors[:3]:
                self.logger.log(
                    f"     Line {issue.line}: [{issue.tool}] {issue.message}",
                    "ERROR"
                )

            if len(errors) > 3:
                self.logger.log(
                    f"     ... and {len(errors) - 3} more error(s)",
                    "ERROR"
                )
            return

        # Has warnings but no errors
        self.logger.log(
            f"  ⚠️  Static analysis: {result.warning_count} warning(s)",
            "WARNING"
        )

    def _generate_property_tests(self, code: str) -> Dict:
        """
        Generate property-based tests.

        WHY: Separate property test generation logic
        RESPONSIBILITY: Generate tests, format results
        PATTERNS: Guard clauses
        """
        self.logger.info("  🧪 Generating property-based tests...")

        # Generate tests
        test_suites = self.property_generator.generate_tests(code)

        # Guard: No tests generated
        if not test_suites:
            self.logger.log("  ℹ️  No property tests generated", "INFO")
            return {
                "enabled": True,
                "test_suites": [],
                "summary": "No testable properties found"
            }

        # Format results
        formatted_suites = []
        for suite in test_suites:
            formatted_suites.append({
                "function_name": suite.function_name,
                "property_count": len(suite.properties),
                "properties": [
                    {
                        "type": p.property_type,
                        "description": p.description
                    }
                    for p in suite.properties
                ],
                "test_code": suite.test_code,
                "imports": list(suite.imports_needed)
            })

        # Log summary
        total_properties = sum(len(s.properties) for s in test_suites)
        self.logger.log(
            f"  ✅ Generated {total_properties} property test(s) "
            f"for {len(test_suites)} function(s)",
            "SUCCESS"
        )

        return {
            "enabled": True,
            "test_suites": formatted_suites,
            "summary": f"Generated {total_properties} property tests for {len(test_suites)} functions"
        }

    def _run_symbolic_execution(self, code: str) -> Dict:
        """
        Run symbolic execution on code.

        WHY: Separate symbolic execution logic
        RESPONSIBILITY: Execute symbolically, format results
        PATTERNS: Guard clauses
        """
        self.logger.info("  🔬 Running symbolic execution...")

        # Run symbolic execution
        exec_result = self.symbolic_executor.validate_function(code)

        # Format for code review
        formatted_result = {
            "enabled": True,
            "function_name": exec_result.function_name,
            "status": exec_result.status.value,
            "verified": exec_result.status.value == "verified",
            "paths_explored": exec_result.paths_explored,
            "reachable_paths": exec_result.reachable_paths,
            "unreachable_paths": exec_result.unreachable_paths,
            "errors": exec_result.potential_errors,
            "verification_time_ms": exec_result.verification_time_ms,
            "summary": exec_result.summary
        }

        # Log summary
        self._log_symbolic_execution_summary(exec_result)

        return formatted_result

    def _log_symbolic_execution_summary(self, result: SymbolicExecutionResult) -> None:
        """
        Log symbolic execution summary.

        WHY: Provide visibility into verification results
        RESPONSIBILITY: Log appropriate messages
        PATTERNS: Guard clauses for different status types
        """
        # Guard: Verified
        if result.status.value == "verified":
            self.logger.log(
                f"  ✅ Symbolic execution: {result.summary}",
                "SUCCESS"
            )
            return

        # Guard: Unsupported
        if result.status.value == "unsupported":
            self.logger.log(
                f"  ℹ️  Symbolic execution: {result.summary}",
                "INFO"
            )
            return

        # Guard: Has errors
        if result.potential_errors:
            self.logger.log(
                f"  ⚠️  Symbolic execution: {result.summary}",
                "WARNING"
            )
            # Log sample errors
            for error in result.potential_errors[:3]:
                self.logger.log(f"     {error}", "WARNING")
            if len(result.potential_errors) > 3:
                self.logger.log(
                    f"     ... and {len(result.potential_errors) - 3} more",
                    "WARNING"
                )
            return

        # Default
        self.logger.log(f"  ℹ️  {result.summary}", "INFO")

    def _match_formal_specs(self, code: str, requirements: Optional[str]) -> Dict:
        """
        Match code to formal specifications.

        WHY: Separate formal specification logic
        RESPONSIBILITY: Match specs, format results
        PATTERNS: Guard clauses
        """
        self.logger.info("  📋 Matching formal specifications...")

        # Match specifications
        match_result = self.spec_matcher.match_specifications(
            code=code,
            requirements=requirements
        )

        # Format for code review
        formatted_result = {
            "enabled": True,
            "function_name": match_result.function_name,
            "satisfied": match_result.overall_satisfied,
            "specifications_found": match_result.specifications_found,
            "specifications_verified": match_result.specifications_verified,
            "specifications_failed": match_result.specifications_failed,
            "summary": match_result.summary,
            "specifications": []
        }

        # Format specifications
        for spec in match_result.specifications:
            formatted_result["specifications"].append({
                "type": spec.spec_type.value,
                "description": spec.description,
                "source": spec.source
            })

        # Log summary
        self._log_formal_specs_summary(match_result)

        return formatted_result

    def _log_formal_specs_summary(self, result: FormalMatchingResult) -> None:
        """
        Log formal specification matching summary.

        WHY: Provide visibility into specification results
        RESPONSIBILITY: Log appropriate messages
        PATTERNS: Guard clauses for different result types
        """
        # Guard: All satisfied
        if result.overall_satisfied:
            self.logger.log(
                f"  ✅ Formal specs: {result.summary}",
                "SUCCESS"
            )
            return

        # Guard: No specs found
        if result.specifications_found == 0:
            self.logger.log(
                f"  ℹ️  Formal specs: {result.summary}",
                "INFO"
            )
            return

        # Has failures
        self.logger.log(
            f"  ⚠️  Formal specs: {result.summary}",
            "WARNING"
        )

    def format_report(self, result: Dict) -> str:
        """
        Format validation results as markdown report.

        WHY: Code review needs readable reports
        RESPONSIBILITY: Convert results to markdown

        Args:
            result: Validation result dictionary

        Returns:
            Markdown formatted report
        """
        lines = ["## Advanced Validation Report", ""]

        # Static Analysis Section
        if result.get("static_analysis"):
            lines.extend(self._format_static_analysis_section(result["static_analysis"]))

        # Property-Based Tests Section
        if result.get("property_tests"):
            lines.extend(self._format_property_tests_section(result["property_tests"]))

        # Symbolic Execution Section
        if result.get("symbolic_execution"):
            lines.extend(self._format_symbolic_execution_section(result["symbolic_execution"]))

        # Formal Specifications Section
        if result.get("formal_specs"):
            lines.extend(self._format_formal_specs_section(result["formal_specs"]))

        # Overall Summary
        lines.append("### Overall Assessment")
        lines.append("")

        # Guard: All passed
        if result["overall_passed"]:
            lines.append("✅ All advanced validation checks passed")
        else:
            lines.append(f"❌ Found {len(result['issues_found'])} issue(s)")

        # Add suggestions
        if result.get("suggestions"):
            lines.append("")
            lines.append("### Suggestions")
            lines.append("")
            for suggestion in result["suggestions"]:
                lines.append(f"- {suggestion}")

        return "\n".join(lines)

    def _format_static_analysis_section(self, static_result: Dict) -> List[str]:
        """Format static analysis section of report."""
        lines = ["### Static Analysis", ""]

        # Guard: Not enabled
        if not static_result.get("enabled"):
            lines.append("ℹ️  Static analysis was not enabled")
            return lines

        lines.append(static_result["summary"])
        lines.append("")

        # Guard: No issues
        if not static_result.get("issues"):
            return lines

        # Group issues by severity
        errors = [i for i in static_result["issues"] if i["severity"] == "error"]
        warnings = [i for i in static_result["issues"] if i["severity"] == "warning"]

        # Format errors
        if errors:
            lines.append(f"#### Errors ({len(errors)})")
            lines.append("")
            for issue in errors[:5]:
                lines.append(
                    f"- Line {issue['line']}: [{issue['tool']}] {issue['message']}"
                )
            if len(errors) > 5:
                lines.append(f"- ... and {len(errors) - 5} more")
            lines.append("")

        # Format warnings
        if warnings:
            lines.append(f"#### Warnings ({len(warnings)})")
            lines.append("")
            for issue in warnings[:5]:
                lines.append(
                    f"- Line {issue['line']}: [{issue['tool']}] {issue['message']}"
                )
            if len(warnings) > 5:
                lines.append(f"- ... and {len(warnings) - 5} more")
            lines.append("")

        return lines

    def _format_property_tests_section(self, property_result: Dict) -> List[str]:
        """Format property-based tests section of report."""
        lines = ["### Property-Based Tests", ""]

        # Guard: Not enabled
        if not property_result.get("enabled"):
            lines.append("ℹ️  Property-based test generation was not enabled")
            return lines

        lines.append(property_result["summary"])
        lines.append("")

        # Guard: No test suites
        test_suites = property_result.get("test_suites", [])
        if not test_suites:
            return lines

        # List generated tests
        lines.append("#### Generated Tests")
        lines.append("")

        for suite in test_suites:
            lines.append(f"**{suite['function_name']}** ({suite['property_count']} properties):")
            for prop in suite['properties']:
                lines.append(f"  - {prop['description']}")
            lines.append("")

        return lines

    def _format_symbolic_execution_section(self, symbolic_result: Dict) -> List[str]:
        """Format symbolic execution section of report."""
        lines = ["### Symbolic Execution", ""]

        # Guard: Not enabled
        if not symbolic_result.get("enabled"):
            lines.append("ℹ️  Symbolic execution was not enabled")
            return lines

        lines.append(symbolic_result["summary"])
        lines.append("")

        # Add details
        lines.append(f"**Function:** {symbolic_result['function_name']}")
        lines.append(f"**Status:** {symbolic_result['status']}")
        lines.append(f"**Paths explored:** {symbolic_result['paths_explored']}")
        lines.append(f"**Reachable paths:** {symbolic_result['reachable_paths']}")
        lines.append(f"**Unreachable paths:** {symbolic_result['unreachable_paths']}")
        lines.append(f"**Verification time:** {symbolic_result['verification_time_ms']:.2f}ms")
        lines.append("")

        # Guard: Has errors
        errors = symbolic_result.get("errors", [])
        if errors:
            lines.append("#### Potential Errors")
            lines.append("")
            for error in errors[:5]:
                lines.append(f"- {error}")
            if len(errors) > 5:
                lines.append(f"- ... and {len(errors) - 5} more")
            lines.append("")

        return lines

    def _format_formal_specs_section(self, formal_result: Dict) -> List[str]:
        """Format formal specifications section of report."""
        lines = ["### Formal Specifications", ""]

        # Guard: Not enabled
        if not formal_result.get("enabled"):
            lines.append("ℹ️  Formal specification matching was not enabled")
            return lines

        lines.append(formal_result["summary"])
        lines.append("")

        # Guard: No specs found
        specifications = formal_result.get("specifications", [])
        if not specifications:
            return lines

        # Add specifications details
        lines.append("#### Specifications Found")
        lines.append("")
        lines.append(f"**Function:** {formal_result['function_name']}")
        lines.append(f"**Total specifications:** {formal_result['specifications_found']}")
        lines.append(f"**Verified:** {formal_result['specifications_verified']}")
        lines.append(f"**Failed:** {formal_result['specifications_failed']}")
        lines.append("")

        # List specifications by type
        preconditions = [s for s in specifications if s['type'] == 'precondition']
        postconditions = [s for s in specifications if s['type'] == 'postcondition']
        invariants = [s for s in specifications if s['type'] == 'invariant']
        type_constraints = [s for s in specifications if s['type'] == 'type_constraint']

        if preconditions:
            lines.append("**Preconditions:**")
            for spec in preconditions:
                lines.append(f"- {spec['description']} (from {spec['source']})")
            lines.append("")

        if postconditions:
            lines.append("**Postconditions:**")
            for spec in postconditions:
                lines.append(f"- {spec['description']} (from {spec['source']})")
            lines.append("")

        if invariants:
            lines.append("**Invariants:**")
            for spec in invariants:
                lines.append(f"- {spec['description']} (from {spec['source']})")
            lines.append("")

        if type_constraints:
            lines.append("**Type Constraints:**")
            for spec in type_constraints:
                lines.append(f"- {spec['description']} (from {spec['source']})")
            lines.append("")

        return lines
