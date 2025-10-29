from artemis_logger import get_logger
logger = get_logger('validation_pipeline_integration_example')
'\nValidation Pipeline Integration Example\n\nShows how to integrate validation_pipeline.py with existing stages.\nThis demonstrates the 4-layer validation architecture:\n\nLayer 1: Preflight (before)       - preflight_validator.py\nLayer 2: Strategy Selection        - requirements_driven_validator.py\nLayer 3: Pipeline (during)         - validation_pipeline.py ← THIS\nLayer 4: Quality Gates (after)     - artifact_quality_validator.py\n'
from pathlib import Path
from typing import Dict, Optional
from validation_pipeline import ValidationPipeline, ValidationStage, validate_python_code
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
        self.logger.log(f'🚀 Starting development: {task_title}', 'INFO')
        self.logger.log('📋 Layer 1: Preflight validation', 'INFO')
        preflight = PreflightValidator(verbose=False)
        preflight_results = preflight.validate_all(base_path='.')
        if not preflight_results['passed']:
            self.logger.log(f"❌ Preflight failed: {preflight_results['critical_count']} critical issues", 'ERROR')
            return {'success': False, 'error': 'Preflight validation failed', 'preflight_results': preflight_results}
        self.logger.log('✅ Preflight passed', 'INFO')
        self.logger.log('📋 Layer 2: Strategy selection', 'INFO')
        strategy_validator = RequirementsDrivenValidator(logger=self.logger)
        strategy = strategy_validator.analyze_requirements(task_title=task_title, task_description=task_description)
        self.logger.log(f'✅ Strategy: {strategy.artifact_type.value} → {strategy.workflow.value}', 'INFO')
        self.logger.log('📋 Layer 3: Validation pipeline (continuous)', 'INFO')
        pipeline = ValidationPipeline(llm_client=self.llm_client, logger=self.logger, strict_mode=True)
        if strategy.workflow.value == 'tdd':
            stages = [ValidationStage.IMPORTS, ValidationStage.TESTS, ValidationStage.SIGNATURE, ValidationStage.BODY]
        else:
            stages = [ValidationStage.IMPORTS, ValidationStage.SIGNATURE, ValidationStage.DOCSTRING, ValidationStage.BODY]
        code, generation_success = pipeline.generate_with_validation(task=f'{task_title}\n\n{task_description}', stages=stages, max_retries=2)
        pipeline_summary = pipeline.get_validation_summary()
        self.logger.log(f"✅ Pipeline: {pipeline_summary['passed']}/{pipeline_summary['total_validations']} passed", 'INFO')
        if not generation_success:
            self.logger.log('❌ Code generation failed validation pipeline', 'ERROR')
            return {'success': False, 'error': 'Validation pipeline failed', 'pipeline_results': pipeline_summary, 'partial_code': code}
        self.logger.log('📋 Layer 4: Quality gates', 'INFO')
        temp_file = Path(f'/tmp/artemis_code_{hash(task_title)}.py')
        temp_file.write_text(code)
        quality_validator = create_validator(validator_class=strategy.validator_class, quality_criteria=strategy.quality_criteria, logger=self.logger)
        quality_result = quality_validator.validate(temp_file)
        self.logger.log(f'✅ Quality: {quality_result.score:.2f} ({quality_result})', 'INFO')
        if not quality_result.passed:
            self.logger.log(f'❌ Quality gate failed: {quality_result.feedback}', 'WARNING')
            if pipeline_summary['pass_rate'] > 0.8:
                self.logger.log('⚠️  Pipeline mostly passed, allowing quality issues', 'WARNING')
            else:
                return {'success': False, 'error': 'Quality gate failed', 'quality_result': quality_result, 'code': code}
        temp_file.unlink()
        self.logger.log('🎉 All validation layers passed!', 'INFO')
        return {'success': True, 'code': code, 'validation_results': {'preflight': preflight_results, 'strategy': strategy.to_dict(), 'pipeline': pipeline_summary, 'quality': {'passed': quality_result.passed, 'score': quality_result.score, 'criteria': quality_result.criteria_results, 'feedback': quality_result.feedback}}, 'artifacts': [temp_file]}

def example_1_quick_validation():
    """Example 1: Quick validation of existing code"""
    
    logger.log('\n' + '=' * 70, 'INFO')
    
    logger.log('EXAMPLE 1: Quick Validation', 'INFO')
    
    logger.log('=' * 70, 'INFO')
    code = '\nimport os\nfrom typing import List\n\ndef process_data(items: List[str]) -> int:\n    """\n    Process a list of items.\n\n    Args:\n        items: List of strings to process\n\n    Returns:\n        Number of items processed\n    """\n    count = 0\n    for item in items:\n        if item:\n            count += 1\n    return count\n'
    result = validate_python_code(code, strict=True)
    
    logger.log(f'\nValidation result: {result}', 'INFO')
    
    logger.log(f'Passed: {result.passed}', 'INFO')
    
    logger.log(f'Checks: {result.checks}', 'INFO')
    if result.feedback:
        
        logger.log(f'Feedback: {result.feedback}', 'INFO')

def example_2_incremental_validation():
    """Example 2: Validate code as it's being built"""
    
    logger.log('\n' + '=' * 70, 'INFO')
    
    logger.log('EXAMPLE 2: Incremental Validation', 'INFO')
    
    logger.log('=' * 70, 'INFO')
    from validation_pipeline import validate_incrementally
    code_segments = [('import os\nfrom pathlib import Path', ValidationStage.IMPORTS), ('\nimport os\nfrom pathlib import Path\n\ndef read_file(file_path: Path) -> str:\n    """Read file contents"""\n    pass\n', ValidationStage.SIGNATURE), ('\nimport os\nfrom pathlib import Path\n\ndef read_file(file_path: Path) -> str:\n    """Read file contents"""\n    # TODO: implement this\n    pass\n', ValidationStage.BODY)]
    results = validate_incrementally(code_segments, strict=False)
    for i, result in enumerate(results, 1):
        
        logger.log(f'\nStage {i} ({result.stage.value}): {result}', 'INFO')
        if result.feedback:
            
            logger.log(f'  Feedback: {result.feedback}', 'INFO')

def example_3_with_llm_regeneration():
    """Example 3: Generate code with automatic retries"""
    
    logger.log('\n' + '=' * 70, 'INFO')
    
    logger.log('EXAMPLE 3: Code Generation with Validation', 'INFO')
    
    logger.log('=' * 70, 'INFO')
    
    logger.log('\n    # Pseudo-code showing how it works:\n\n    pipeline = ValidationPipeline(llm_client=llm, logger=logger)\n\n    code, success = pipeline.generate_with_validation(\n        task="Create a REST API endpoint for user registration",\n        stages=[\n            ValidationStage.IMPORTS,\n            ValidationStage.SIGNATURE,\n            ValidationStage.BODY,\n            ValidationStage.TESTS\n        ],\n        max_retries=2\n    )\n\n    if success:\n        print("✅ Generated valid code!")\n    else:\n        print("❌ Failed after retries")\n        # Review pipeline.get_validation_summary() to see what failed\n    ', 'INFO')

def example_4_hallucination_prevention():
    """Example 4: Specific hallucination checks"""
    
    logger.log('\n' + '=' * 70, 'INFO')
    
    logger.log('EXAMPLE 4: Hallucination Prevention', 'INFO')
    
    logger.log('=' * 70, 'INFO')
    bad_code = '\nfrom sqlalchemy import User\n\ndef create_user(name: str, email: str):\n    """Create a new user"""\n    # TODO: validate email\n    user = User(name=name, email=email)\n    user.save()  # ← HALLUCINATION: SQLAlchemy doesn\'t have .save()\n    return user\n'
    result = validate_python_code(bad_code, strict=True)
    
    logger.log(f'\nValidation result: {result}', 'INFO')
    
    logger.log(f'Passed: {result.passed}', 'INFO')
    
    logger.log(f'\n❌ Hallucinations detected:', 'INFO')
    for feedback in result.feedback:
        
        logger.log(f'  - {feedback}', 'INFO')
    
    logger.log('\n💡 The validation pipeline would catch these issues DURING generation', 'INFO')
    
    logger.log('   and ask the LLM to regenerate with fixes!', 'INFO')

def example_5_integration_with_existing_stages():
    """Example 5: How to integrate with development_stage.py"""
    
    logger.log('\n' + '=' * 70, 'INFO')
    
    logger.log('EXAMPLE 5: Integration Pattern', 'INFO')
    
    logger.log('=' * 70, 'INFO')
    
    logger.log('\nIn your development_stage.py, add this:\n\nfrom validation_pipeline import ValidationPipeline, ValidationStage\n\nclass DevelopmentStage:\n    def execute(self, task):\n        # ... existing preflight checks ...\n\n        # ADD: Validation pipeline\n        pipeline = ValidationPipeline(\n            llm_client=self.llm_client,\n            logger=self.logger,\n            strict_mode=True\n        )\n\n        # Generate code with continuous validation\n        code, success = pipeline.generate_with_validation(\n            task=task,\n            stages=[\n                ValidationStage.IMPORTS,\n                ValidationStage.SIGNATURE,\n                ValidationStage.BODY,\n            ],\n            max_retries=2\n        )\n\n        if not success:\n            # Handle failure\n            summary = pipeline.get_validation_summary()\n            self.logger.log(f"Validation failed: {summary}", "ERROR")\n            return None\n\n        # ... existing quality checks ...\n\n        return code\n    ', 'INFO')
if __name__ == '__main__':
    
    logger.log('\n' + '=' * 70, 'INFO')
    
    logger.log('VALIDATION PIPELINE - INTEGRATION EXAMPLES', 'INFO')
    
    logger.log('=' * 70, 'INFO')
    example_1_quick_validation()
    example_2_incremental_validation()
    example_3_with_llm_regeneration()
    example_4_hallucination_prevention()
    example_5_integration_with_existing_stages()
    
    logger.log('\n' + '=' * 70, 'INFO')
    
    logger.log('✅ Examples complete!', 'INFO')
    
    logger.log('=' * 70, 'INFO')