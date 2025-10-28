#!/usr/bin/env python3
"""
Validated TDD Mixin

WHY: TDD workflow (RED-GREEN-REFACTOR) needs validation at each phase
     to catch hallucinations early in the development cycle.

RESPONSIBILITY:
- Validated RED phase (generate tests with validation)
- Validated GREEN phase (generate implementation with validation)
- Validated REFACTOR phase (improve code with validation)
- Test method extraction utilities

PATTERNS:
- Mixin Pattern: Add TDD workflow to validated agents
- Template Method: Define TDD workflow structure
- Guard Clauses: Early returns to avoid nested conditionals
"""

from typing import Dict
from validation_pipeline import ValidationStage

from validated_developer.core_mixin import ValidatedDeveloperMixin
from validated_developer.code_extractor import CodeExtractor


class ValidatedTDDMixin(ValidatedDeveloperMixin):
    """
    Extended mixin with validated TDD workflow methods.

    WHY: TDD workflow requires validation at each phase to ensure
         tests and implementation are hallucination-free.

    RESPONSIBILITY:
    - Provide validated RED phase (test generation)
    - Provide validated GREEN phase (implementation)
    - Provide validated REFACTOR phase (improvement)
    """

    def _validated_red_phase(
        self,
        task_title: str,
        task_description: str,
        adr_content: str,
        context: Dict
    ) -> Dict:
        """
        RED phase with validation: Write failing tests.

        WHY: Tests must be validated to ensure they properly test requirements
             and don't contain hallucinated assertions.

        Args:
            task_title: Title of task
            task_description: Description of task
            adr_content: Architecture decision record
            context: Additional context (output_dir, etc.)

        Returns:
            Dict with test_code, test_files, validation_result
        """
        logger = getattr(self, 'logger', None)

        if logger:
            logger.log("RED: Generating tests (with validation)...", "INFO")

        # Build prompt for test generation
        prompt = self._build_red_phase_prompt(task_title, task_description, adr_content, context)

        # Generate tests with validation
        test_code = self._validated_llm_query(
            prompt=prompt,
            stage=ValidationStage.TESTS,
            max_retries=2,
            context={
                'task_title': task_title,
                'task_description': task_description
            }
        )

        # Parse and write test files
        test_files = self._write_test_files(test_code, context.get('output_dir'))

        return {
            'test_code': test_code,
            'test_files': test_files,
            'phase': 'RED',
            'validated': True
        }

    def _validated_green_phase(
        self,
        task_title: str,
        task_description: str,
        adr_content: str,
        test_code: str,
        context: Dict
    ) -> Dict:
        """
        GREEN phase with validation: Implement minimum code to pass tests.

        WHY: Implementation must be validated incrementally (imports -> signature -> body)
             to catch hallucinations at each stage.

        Args:
            task_title: Title of task
            task_description: Description of task
            adr_content: Architecture decision record
            test_code: Test code from RED phase
            context: Additional context

        Returns:
            Dict with implementation_code, implementation_files, validation_result
        """
        logger = getattr(self, 'logger', None)

        if logger:
            logger.log("GREEN: Generating implementation (with validation)...", "INFO")

        # Build prompt for implementation
        prompt = self._build_green_phase_prompt(
            task_title, task_description, adr_content, test_code, context
        )

        # Validate incrementally: imports -> signature -> body
        full_code = self._generate_implementation_incrementally(prompt, test_code)

        # Final validation
        final_result = self._validate_generated_code(
            code=full_code,
            stage=ValidationStage.FULL_CODE
        )

        if not final_result.passed and logger:
            logger.log(f"Final validation warnings: {final_result.feedback}", "WARNING")

        # Write implementation files
        impl_files = self._write_implementation_files(full_code, context.get('output_dir'))

        return {
            'implementation_code': full_code,
            'implementation_files': impl_files,
            'phase': 'GREEN',
            'validated': True,
            'validation_result': final_result
        }

    def _validated_refactor_phase(self, implementation_code: str, context: Dict) -> Dict:
        """
        REFACTOR phase with validation: Improve code quality.

        WHY: Refactoring must maintain functionality while improving quality.
             Validation ensures no regressions introduced.

        Args:
            implementation_code: Code to refactor
            context: Additional context

        Returns:
            Dict with refactored_code, phase, validated
        """
        logger = getattr(self, 'logger', None)

        if logger:
            logger.log("REFACTOR: Improving code (with validation)...", "INFO")

        # Build refactoring prompt
        prompt = self._build_refactor_prompt(implementation_code)

        # Refactor with validation
        refactored_code = self._validated_llm_query(
            prompt=prompt,
            stage=ValidationStage.FULL_CODE,
            max_retries=2
        )

        return {
            'refactored_code': refactored_code,
            'phase': 'REFACTOR',
            'validated': True
        }

    def _generate_implementation_incrementally(self, prompt: str, test_code: str) -> str:
        """
        Generate implementation incrementally with validation at each stage.

        WHY: Incremental validation catches hallucinations early before they
             compound into larger issues.

        Args:
            prompt: Base prompt for implementation
            test_code: Test code to implement against

        Returns:
            Full implementation code
        """
        full_code = ""

        # Stage 1: Imports
        imports_prompt = f"{prompt}\n\nFirst, generate only the import statements needed."
        imports = self._validated_llm_query(
            prompt=imports_prompt,
            stage=ValidationStage.IMPORTS,
            max_retries=2
        )
        full_code += imports + "\n\n"

        # Stage 2: Signature
        sig_prompt = f"{prompt}\n\n{full_code}\n\nNow generate function/class signatures with type hints and docstrings."
        signature = self._validated_llm_query(
            prompt=sig_prompt,
            stage=ValidationStage.SIGNATURE,
            max_retries=2
        )
        full_code += signature + "\n\n"

        # Stage 3: Body
        body_prompt = f"{prompt}\n\n{full_code}\n\nNow complete the implementation. No TODOs or placeholders."
        body = self._validated_llm_query(
            prompt=body_prompt,
            stage=ValidationStage.BODY,
            max_retries=2,
            context={'expected_methods': CodeExtractor.extract_test_methods(test_code)}
        )
        full_code += body

        return full_code

    def _build_red_phase_prompt(self, title: str, desc: str, adr: str, context: Dict) -> str:
        """
        Build prompt for RED phase (override in subclass if needed).

        Args:
            title: Task title
            desc: Task description
            adr: Architecture decision record
            context: Additional context

        Returns:
            Prompt string
        """
        return f"Generate pytest tests for: {title}\n\n{desc}\n\nADR:\n{adr}"

    def _build_green_phase_prompt(self, title: str, desc: str, adr: str, tests: str, context: Dict) -> str:
        """
        Build prompt for GREEN phase (override in subclass if needed).

        Args:
            title: Task title
            desc: Task description
            adr: Architecture decision record
            tests: Test code
            context: Additional context

        Returns:
            Prompt string
        """
        return f"Implement code to pass these tests:\n\n{tests}\n\nTask: {title}\n{desc}"

    def _build_refactor_prompt(self, implementation_code: str) -> str:
        """
        Build prompt for REFACTOR phase.

        Args:
            implementation_code: Code to refactor

        Returns:
            Prompt string
        """
        return f"""Refactor this code to improve quality:

{implementation_code}

Requirements:
- Maintain all functionality
- Improve readability
- Add type hints if missing
- Improve docstrings
- Follow best practices
- NO PLACEHOLDERS OR TODOs

Return the refactored code.
"""

    def _write_test_files(self, code: str, output_dir) -> list:
        """
        Write test files (override in subclass).

        Args:
            code: Test code to write
            output_dir: Output directory

        Returns:
            List of written file paths

        Raises:
            NotImplementedError: Must be implemented by subclass
        """
        raise NotImplementedError("Subclass must implement _write_test_files")

    def _write_implementation_files(self, code: str, output_dir) -> list:
        """
        Write implementation files (override in subclass).

        Args:
            code: Implementation code to write
            output_dir: Output directory

        Returns:
            List of written file paths

        Raises:
            NotImplementedError: Must be implemented by subclass
        """
        raise NotImplementedError("Subclass must implement _write_implementation_files")
