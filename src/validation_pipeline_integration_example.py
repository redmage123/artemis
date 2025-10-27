#!/usr/bin/env python3
"""
Validation Pipeline Integration Example

Shows how to integrate validation_pipeline.py with existing stages.
This demonstrates the 4-layer validation architecture:

Layer 1: Preflight (before)       - preflight_validator.py
Layer 2: Strategy Selection        - requirements_driven_validator.py
Layer 3: Pipeline (during)         - validation_pipeline.py ← THIS
Layer 4: Quality Gates (after)     - artifact_quality_validator.py
"""

from pathlib import Path
from typing import Dict, Optional
from validation_pipeline import (
    ValidationPipeline,
    ValidationStage,
    validate_python_code
)
from preflight_validator import PreflightValidator
from requirements_driven_validator import RequirementsDrivenValidator
from artifact_quality_validator import create_validator


class EnhancedDevelopmentStage:
    """
    Example of how to integrate validation pipeline into development stage.

    This demonstrates all 4 layers of validation working together.
    """

    def __init__(self, llm_client, logger):
        self.llm_client = llm_client
        self.logger = logger

    def execute_with_validation(self, task_title: str, task_description: str) -> Dict:
        """
        Execute development task with full 4-layer validation.

        Returns:
            {
                'success': bool,
                'code': str,
                'validation_results': dict,
                'artifacts': list
            }
        """
        self.logger.log(f"🚀 Starting development: {task_title}", "INFO")

        # ═══════════════════════════════════════════════════════════
        # LAYER 1: PREFLIGHT VALIDATION (Static checks before start)
        # ═══════════════════════════════════════════════════════════
        self.logger.log("📋 Layer 1: Preflight validation", "INFO")

        preflight = PreflightValidator(verbose=False)
        preflight_results = preflight.validate_all(base_path=".")

        if not preflight_results['passed']:
            self.logger.log(f"❌ Preflight failed: {preflight_results['critical_count']} critical issues", "ERROR")
            return {
                'success': False,
                'error': 'Preflight validation failed',
                'preflight_results': preflight_results
            }

        self.logger.log("✅ Preflight passed", "INFO")

        # ═══════════════════════════════════════════════════════════
        # LAYER 2: STRATEGY SELECTION (Choose workflow and criteria)
        # ═══════════════════════════════════════════════════════════
        self.logger.log("📋 Layer 2: Strategy selection", "INFO")

        strategy_validator = RequirementsDrivenValidator(logger=self.logger)
        strategy = strategy_validator.analyze_requirements(
            task_title=task_title,
            task_description=task_description
        )

        self.logger.log(
            f"✅ Strategy: {strategy.artifact_type.value} → {strategy.workflow.value}",
            "INFO"
        )

        # ═══════════════════════════════════════════════════════════
        # LAYER 3: VALIDATION PIPELINE (Continuous during generation)
        # ═══════════════════════════════════════════════════════════
        self.logger.log("📋 Layer 3: Validation pipeline (continuous)", "INFO")

        # Create validation pipeline
        pipeline = ValidationPipeline(
            llm_client=self.llm_client,
            logger=self.logger,
            strict_mode=True  # Fail on any validation error
        )

        # Define stages based on workflow type
        if strategy.workflow.value == 'tdd':
            stages = [
                ValidationStage.IMPORTS,
                ValidationStage.TESTS,      # TDD: Tests first
                ValidationStage.SIGNATURE,
                ValidationStage.BODY,
            ]
        else:  # quality_driven
            stages = [
                ValidationStage.IMPORTS,
                ValidationStage.SIGNATURE,
                ValidationStage.DOCSTRING,
                ValidationStage.BODY,
            ]

        # Generate code with continuous validation
        code, generation_success = pipeline.generate_with_validation(
            task=f"{task_title}\n\n{task_description}",
            stages=stages,
            max_retries=2
        )

        pipeline_summary = pipeline.get_validation_summary()
        self.logger.log(
            f"✅ Pipeline: {pipeline_summary['passed']}/{pipeline_summary['total_validations']} passed",
            "INFO"
        )

        if not generation_success:
            self.logger.log("❌ Code generation failed validation pipeline", "ERROR")
            return {
                'success': False,
                'error': 'Validation pipeline failed',
                'pipeline_results': pipeline_summary,
                'partial_code': code
            }

        # ═══════════════════════════════════════════════════════════
        # LAYER 4: QUALITY GATES (Final validation after generation)
        # ═══════════════════════════════════════════════════════════
        self.logger.log("📋 Layer 4: Quality gates", "INFO")

        # Write code to temporary file for validation
        temp_file = Path(f"/tmp/artemis_code_{hash(task_title)}.py")
        temp_file.write_text(code)

        # Create appropriate validator based on strategy
        quality_validator = create_validator(
            validator_class=strategy.validator_class,
            quality_criteria=strategy.quality_criteria,
            logger=self.logger
        )

        # Run final quality validation
        quality_result = quality_validator.validate(temp_file)

        self.logger.log(
            f"✅ Quality: {quality_result.score:.2f} ({quality_result})",
            "INFO"
        )

        if not quality_result.passed:
            self.logger.log(f"❌ Quality gate failed: {quality_result.feedback}", "WARNING")

            # Optional: Try to regenerate with quality feedback
            if pipeline_summary['pass_rate'] > 0.8:
                self.logger.log("⚠️  Pipeline mostly passed, allowing quality issues", "WARNING")
            else:
                return {
                    'success': False,
                    'error': 'Quality gate failed',
                    'quality_result': quality_result,
                    'code': code
                }

        # Clean up temp file
        temp_file.unlink()

        # ═══════════════════════════════════════════════════════════
        # SUCCESS: All 4 layers passed
        # ═══════════════════════════════════════════════════════════
        self.logger.log("🎉 All validation layers passed!", "INFO")

        return {
            'success': True,
            'code': code,
            'validation_results': {
                'preflight': preflight_results,
                'strategy': strategy.to_dict(),
                'pipeline': pipeline_summary,
                'quality': {
                    'passed': quality_result.passed,
                    'score': quality_result.score,
                    'criteria': quality_result.criteria_results,
                    'feedback': quality_result.feedback
                }
            },
            'artifacts': [temp_file]
        }


# ═══════════════════════════════════════════════════════════════════
# SIMPLER USAGE EXAMPLES
# ═══════════════════════════════════════════════════════════════════

def example_1_quick_validation():
    """Example 1: Quick validation of existing code"""
    print("\n" + "="*70)
    print("EXAMPLE 1: Quick Validation")
    print("="*70)

    code = """
import os
from typing import List

def process_data(items: List[str]) -> int:
    \"\"\"
    Process a list of items.

    Args:
        items: List of strings to process

    Returns:
        Number of items processed
    \"\"\"
    count = 0
    for item in items:
        if item:
            count += 1
    return count
"""

    result = validate_python_code(code, strict=True)
    print(f"\nValidation result: {result}")
    print(f"Passed: {result.passed}")
    print(f"Checks: {result.checks}")
    if result.feedback:
        print(f"Feedback: {result.feedback}")


def example_2_incremental_validation():
    """Example 2: Validate code as it's being built"""
    print("\n" + "="*70)
    print("EXAMPLE 2: Incremental Validation")
    print("="*70)

    from validation_pipeline import validate_incrementally

    # Simulate building code incrementally
    code_segments = [
        # Stage 1: Imports
        ("import os\nfrom pathlib import Path", ValidationStage.IMPORTS),

        # Stage 2: Signature
        ("""
import os
from pathlib import Path

def read_file(file_path: Path) -> str:
    \"\"\"Read file contents\"\"\"
    pass
""", ValidationStage.SIGNATURE),

        # Stage 3: Body (with placeholder - should fail)
        ("""
import os
from pathlib import Path

def read_file(file_path: Path) -> str:
    \"\"\"Read file contents\"\"\"
    # TODO: implement this
    pass
""", ValidationStage.BODY),
    ]

    results = validate_incrementally(code_segments, strict=False)

    for i, result in enumerate(results, 1):
        print(f"\nStage {i} ({result.stage.value}): {result}")
        if result.feedback:
            print(f"  Feedback: {result.feedback}")


def example_3_with_llm_regeneration():
    """Example 3: Generate code with automatic retries"""
    print("\n" + "="*70)
    print("EXAMPLE 3: Code Generation with Validation")
    print("="*70)

    # This would use actual LLM client
    # For demo, we'll just show the structure

    print("""
    # Pseudo-code showing how it works:

    pipeline = ValidationPipeline(llm_client=llm, logger=logger)

    code, success = pipeline.generate_with_validation(
        task="Create a REST API endpoint for user registration",
        stages=[
            ValidationStage.IMPORTS,
            ValidationStage.SIGNATURE,
            ValidationStage.BODY,
            ValidationStage.TESTS
        ],
        max_retries=2
    )

    if success:
        print("✅ Generated valid code!")
    else:
        print("❌ Failed after retries")
        # Review pipeline.get_validation_summary() to see what failed
    """)


def example_4_hallucination_prevention():
    """Example 4: Specific hallucination checks"""
    print("\n" + "="*70)
    print("EXAMPLE 4: Hallucination Prevention")
    print("="*70)

    bad_code = """
from sqlalchemy import User

def create_user(name: str, email: str):
    \"\"\"Create a new user\"\"\"
    # TODO: validate email
    user = User(name=name, email=email)
    user.save()  # ← HALLUCINATION: SQLAlchemy doesn't have .save()
    return user
"""

    result = validate_python_code(bad_code, strict=True)
    print(f"\nValidation result: {result}")
    print(f"Passed: {result.passed}")
    print(f"\n❌ Hallucinations detected:")
    for feedback in result.feedback:
        print(f"  - {feedback}")

    print("\n💡 The validation pipeline would catch these issues DURING generation")
    print("   and ask the LLM to regenerate with fixes!")


def example_5_integration_with_existing_stages():
    """Example 5: How to integrate with development_stage.py"""
    print("\n" + "="*70)
    print("EXAMPLE 5: Integration Pattern")
    print("="*70)

    print("""
In your development_stage.py, add this:

from validation_pipeline import ValidationPipeline, ValidationStage

class DevelopmentStage:
    def execute(self, task):
        # ... existing preflight checks ...

        # ADD: Validation pipeline
        pipeline = ValidationPipeline(
            llm_client=self.llm_client,
            logger=self.logger,
            strict_mode=True
        )

        # Generate code with continuous validation
        code, success = pipeline.generate_with_validation(
            task=task,
            stages=[
                ValidationStage.IMPORTS,
                ValidationStage.SIGNATURE,
                ValidationStage.BODY,
            ],
            max_retries=2
        )

        if not success:
            # Handle failure
            summary = pipeline.get_validation_summary()
            self.logger.log(f"Validation failed: {summary}", "ERROR")
            return None

        # ... existing quality checks ...

        return code
    """)


if __name__ == "__main__":
    print("\n" + "="*70)
    print("VALIDATION PIPELINE - INTEGRATION EXAMPLES")
    print("="*70)

    example_1_quick_validation()
    example_2_incremental_validation()
    example_3_with_llm_regeneration()
    example_4_hallucination_prevention()
    example_5_integration_with_existing_stages()

    print("\n" + "="*70)
    print("✅ Examples complete!")
    print("="*70)
