from artemis_logger import get_logger
logger = get_logger('self_critique_integration_example')
'\nSelf-Critique Validation Integration Examples\n\nDemonstrates how to use Layer 5 (Self-Critique) hallucination reduction\nin various scenarios.\n'
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from self_critique_validator import SelfCritiqueValidator, SelfCritiqueFactory, CritiqueLevel, CritiqueSeverity
from llm_client import LLMClient
from rag_agent import RAGAgent

def example_1_basic_critique():
    """
    Example 1: Basic self-critique validation
    """
    
    logger.log('\n' + '=' * 70, 'INFO')
    
    logger.log('EXAMPLE 1: Basic Self-Critique Validation', 'INFO')
    
    logger.log('=' * 70, 'INFO')
    llm = LLMClient(provider='openai', model='gpt-4')
    validator = SelfCritiqueValidator(llm_client=llm, level=CritiqueLevel.BALANCED)
    generated_code = '\ndef create_user(username, email):\n    # Create new user\n    user = User(username=username, email=email)\n    db.session.add(user)  # ← HALLUCINATION: Wrong ORM\n    db.session.commit()   # ← Should use Django ORM\n    return user\n'
    result = validator.validate_code(code=generated_code, context={'language': 'python', 'framework': 'django'}, original_prompt='Create a function to create a new user in Django')
    
    logger.log(f'\nPassed: {result.passed}', 'INFO')
    
    logger.log(f'Confidence Score: {result.confidence_score}/10', 'INFO')
    
    logger.log(f'Uncertainty Score: {result.uncertainty_metrics.uncertainty_score}/10', 'INFO')
    
    logger.log(f'\nFindings ({len(result.findings)}):', 'INFO')
    for finding in result.findings:
        
        logger.log(f'\n  [{finding.severity.value.upper()}] {finding.category}', 'INFO')
        
        logger.log(f'  Message: {finding.message}', 'INFO')
        if finding.suggestion:
            
            logger.log(f'  Suggestion: {finding.suggestion}', 'INFO')
    if result.regeneration_needed:
        
        logger.log(f'\n⚠️  REGENERATION NEEDED', 'INFO')
        
        logger.log(f'Feedback:\n{result.feedback}', 'INFO')
    return result

def example_2_uncertainty_detection():
    """
    Example 2: Uncertainty detection
    """
    
    logger.log('\n' + '=' * 70, 'INFO')
    
    logger.log('EXAMPLE 2: Uncertainty Detection', 'INFO')
    
    logger.log('=' * 70, 'INFO')
    llm = LLMClient(provider='openai', model='gpt-4')
    validator = SelfCritiqueValidator(llm_client=llm)
    code_with_uncertainty = '\ndef process_payment(amount, card_number):\n    # TODO: Add input validation\n    # This might need to handle edge cases\n    # Assuming card_number is valid\n\n    # Process payment (needs review)\n    result = payment_gateway.charge(amount, card_number)\n\n    # FIXME: Add error handling\n    return result\n'
    result = validator.validate_code(code=code_with_uncertainty, context={'language': 'python'}, original_prompt='Create payment processing function')
    
    logger.log(f'\nUncertainty Analysis:', 'INFO')
    
    logger.log(f'  Score: {result.uncertainty_metrics.uncertainty_score}/10', 'INFO')
    
    logger.log(f'  Placeholder comments: {result.uncertainty_metrics.placeholder_comments}', 'INFO')
    
    logger.log(f'  Conditional assumptions: {result.uncertainty_metrics.conditional_assumptions}', 'INFO')
    
    logger.log(f'  Missing error handling: {result.uncertainty_metrics.missing_error_handling}', 'INFO')
    return result

def example_3_strict_mode():
    """
    Example 3: Strict mode (fails on warnings)
    """
    
    logger.log('\n' + '=' * 70, 'INFO')
    
    logger.log('EXAMPLE 3: Strict Mode', 'INFO')
    
    logger.log('=' * 70, 'INFO')
    llm = LLMClient(provider='openai', model='gpt-4')
    validator_normal = SelfCritiqueValidator(llm_client=llm, strict_mode=False)
    validator_strict = SelfCritiqueValidator(llm_client=llm, strict_mode=True)
    code = "\ndef calculate_total(items):\n    # Calculate total price\n    total = 0\n    for item in items:\n        total += item['price']  # No error handling if 'price' missing\n    return total\n"
    
    logger.log('\n--- Normal Mode ---', 'INFO')
    result_normal = validator_normal.validate_code(code=code, context={'language': 'python'})
    
    logger.log(f'Passed: {result_normal.passed}', 'INFO')
    
    logger.log('\n--- Strict Mode ---', 'INFO')
    result_strict = validator_strict.validate_code(code=code, context={'language': 'python'})
    
    logger.log(f'Passed: {result_strict.passed}', 'INFO')
    
    logger.log(f'Regeneration needed: {result_strict.regeneration_needed}', 'INFO')
    return (result_normal, result_strict)

def example_4_critique_levels():
    """
    Example 4: Different critique levels
    """
    
    logger.log('\n' + '=' * 70, 'INFO')
    
    logger.log('EXAMPLE 4: Critique Levels (Quick vs Thorough)', 'INFO')
    
    logger.log('=' * 70, 'INFO')
    llm = LLMClient(provider='openai', model='gpt-4')
    code = '\ndef authenticate_user(username, password):\n    user = User.objects.get(username=username)\n    if user.password == password:  # Plain text comparison!\n        return user\n    return None\n'
    
    logger.log('\n--- Quick Critique (~2s) ---', 'INFO')
    validator_quick = SelfCritiqueValidator(llm_client=llm, level=CritiqueLevel.QUICK)
    result_quick = validator_quick.validate_code(code, {'language': 'python'})
    
    logger.log(f'Findings: {len(result_quick.findings)}', 'INFO')
    
    logger.log('\n--- Thorough Critique (~10s) ---', 'INFO')
    validator_thorough = SelfCritiqueValidator(llm_client=llm, level=CritiqueLevel.THOROUGH)
    result_thorough = validator_thorough.validate_code(code, {'language': 'python'})
    
    logger.log(f'Findings: {len(result_thorough.findings)}', 'INFO')
    security_findings = [f for f in result_thorough.findings if f.category == 'security']
    
    logger.log(f'Security issues found: {len(security_findings)}', 'INFO')
    return (result_quick, result_thorough)

def example_5_integration_with_rag():
    """
    Example 5: Integration with RAG for citation verification
    """
    
    logger.log('\n' + '=' * 70, 'INFO')
    
    logger.log('EXAMPLE 5: Integration with RAG', 'INFO')
    
    logger.log('=' * 70, 'INFO')
    llm = LLMClient(provider='openai', model='gpt-4')
    rag = RAGAgent(db_path='../.artemis_data/rag_db')
    validator = SelfCritiqueValidator(llm_client=llm, level=CritiqueLevel.BALANCED, rag_agent=rag)
    code_with_citations = '\ndef create_user(username, email):\n    # From: Django Documentation v4.2\n    # Reference: User model creation\n    user = User.objects.create(\n        username=username,\n        email=email\n    )\n    user.save()\n    return user\n'
    result = validator.validate_code(code=code_with_citations, context={'language': 'python', 'framework': 'django'})
    
    logger.log(f'\nCitations found: {len(result.citations)}', 'INFO')
    for citation in result.citations:
        
        logger.log(f'\n  Source: {citation.source}', 'INFO')
        
        logger.log(f'  Pattern: {citation.pattern[:80]}...', 'INFO')
        
        logger.log(f'  Confidence: {citation.confidence}', 'INFO')
    return result

def example_6_factory_configuration():
    """
    Example 6: Using factory for environment-specific configuration
    """
    
    logger.log('\n' + '=' * 70, 'INFO')
    
    logger.log('EXAMPLE 6: Factory Configuration', 'INFO')
    
    logger.log('=' * 70, 'INFO')
    llm = LLMClient(provider='openai', model='gpt-4')
    dev_validator = SelfCritiqueFactory.create_validator(llm_client=llm, environment='development')
    
    logger.log(f'Development: {dev_validator.level.value} critique', 'INFO')
    prod_validator = SelfCritiqueFactory.create_validator(llm_client=llm, environment='production', strict_mode=True)
    
    logger.log(f'Production: {prod_validator.level.value} critique, strict mode', 'INFO')
    proto_validator = SelfCritiqueFactory.create_validator(llm_client=llm, environment='prototype')
    
    logger.log(f'Prototype: {proto_validator.level.value} critique', 'INFO')
    return (dev_validator, prod_validator, proto_validator)

def example_7_integration_workflow():
    """
    Example 7: Complete workflow with validation pipeline
    """
    
    logger.log('\n' + '=' * 70, 'INFO')
    
    logger.log('EXAMPLE 7: Complete Validation Workflow', 'INFO')
    
    logger.log('=' * 70, 'INFO')
    llm = LLMClient(provider='openai', model='gpt-4')
    validator = SelfCritiqueValidator(llm_client=llm)
    prompt = 'Create a function to hash passwords securely'
    
    logger.log('\n--- Attempt 1 ---', 'INFO')
    code_attempt_1 = '\ndef hash_password(password):\n    # TODO: Add salt\n    import hashlib\n    return hashlib.md5(password.encode()).hexdigest()  # Weak algorithm!\n'
    result_1 = validator.validate_code(code=code_attempt_1, context={'language': 'python'}, original_prompt=prompt)
    
    logger.log(f'Passed: {result_1.passed}', 'INFO')
    
    logger.log(f'Regeneration needed: {result_1.regeneration_needed}', 'INFO')
    if result_1.regeneration_needed:
        
        logger.log(f'\nFeedback for retry:\n{result_1.feedback}', 'INFO')
        
        logger.log('\n--- Attempt 2 (with feedback) ---', 'INFO')
        code_attempt_2 = '\ndef hash_password(password):\n    # Using bcrypt for secure password hashing\n    # Reference: OWASP password storage guidelines\n    import bcrypt\n\n    salt = bcrypt.gensalt()\n    hashed = bcrypt.hashpw(password.encode(), salt)\n    return hashed.decode()\n'
        result_2 = validator.validate_code(code=code_attempt_2, context={'language': 'python'}, original_prompt=prompt)
        
        logger.log(f'Passed: {result_2.passed}', 'INFO')
        
        logger.log(f'Confidence: {result_2.confidence_score}/10', 'INFO')
        
        logger.log(f'Uncertainty: {result_2.uncertainty_metrics.uncertainty_score}/10', 'INFO')
        return result_2
    return result_1

def main():
    """Run all examples"""
    
    logger.log('\n' + '=' * 70, 'INFO')
    
    logger.log('SELF-CRITIQUE VALIDATION - Integration Examples', 'INFO')
    
    logger.log('Layer 5: Metacognitive Hallucination Reduction', 'INFO')
    
    logger.log('=' * 70, 'INFO')
    try:
        example_1_basic_critique()
        example_2_uncertainty_detection()
        example_3_strict_mode()
        example_4_critique_levels()
        example_5_integration_with_rag()
        example_6_factory_configuration()
        example_7_integration_workflow()
        
        logger.log('\n' + '=' * 70, 'INFO')
        
        logger.log('✅ All examples completed successfully', 'INFO')
        
        logger.log('=' * 70, 'INFO')
    except Exception as e:
        
        logger.log(f'\n❌ Error running examples: {e}', 'INFO')
        import traceback
        traceback.print_exc()
        return 1
    return 0
if __name__ == '__main__':
    exit(main())