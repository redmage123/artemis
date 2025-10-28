#!/usr/bin/env python3
"""
Self-Critique Validation Integration Examples

Demonstrates how to use Layer 5 (Self-Critique) hallucination reduction
in various scenarios.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from self_critique_validator import (
    SelfCritiqueValidator,
    SelfCritiqueFactory,
    CritiqueLevel,
    CritiqueSeverity
)
from llm_client import LLMClient
from rag_agent import RAGAgent


def example_1_basic_critique():
    """
    Example 1: Basic self-critique validation
    """
    print("\n" + "="*70)
    print("EXAMPLE 1: Basic Self-Critique Validation")
    print("="*70)

    # Initialize LLM client
    llm = LLMClient(provider='openai', model='gpt-4')

    # Create validator
    validator = SelfCritiqueValidator(
        llm_client=llm,
        level=CritiqueLevel.BALANCED
    )

    # Code with hallucination (wrong Django pattern)
    generated_code = """
def create_user(username, email):
    # Create new user
    user = User(username=username, email=email)
    db.session.add(user)  # ← HALLUCINATION: Wrong ORM
    db.session.commit()   # ← Should use Django ORM
    return user
"""

    # Validate
    result = validator.validate_code(
        code=generated_code,
        context={'language': 'python', 'framework': 'django'},
        original_prompt="Create a function to create a new user in Django"
    )

    # Display results
    print(f"\nPassed: {result.passed}")
    print(f"Confidence Score: {result.confidence_score}/10")
    print(f"Uncertainty Score: {result.uncertainty_metrics.uncertainty_score}/10")
    print(f"\nFindings ({len(result.findings)}):")

    for finding in result.findings:
        print(f"\n  [{finding.severity.value.upper()}] {finding.category}")
        print(f"  Message: {finding.message}")
        if finding.suggestion:
            print(f"  Suggestion: {finding.suggestion}")

    if result.regeneration_needed:
        print(f"\n⚠️  REGENERATION NEEDED")
        print(f"Feedback:\n{result.feedback}")

    return result


def example_2_uncertainty_detection():
    """
    Example 2: Uncertainty detection
    """
    print("\n" + "="*70)
    print("EXAMPLE 2: Uncertainty Detection")
    print("="*70)

    llm = LLMClient(provider='openai', model='gpt-4')
    validator = SelfCritiqueValidator(llm_client=llm)

    # Code with uncertainty signals
    code_with_uncertainty = """
def process_payment(amount, card_number):
    # TODO: Add input validation
    # This might need to handle edge cases
    # Assuming card_number is valid

    # Process payment (needs review)
    result = payment_gateway.charge(amount, card_number)

    # FIXME: Add error handling
    return result
"""

    result = validator.validate_code(
        code=code_with_uncertainty,
        context={'language': 'python'},
        original_prompt="Create payment processing function"
    )

    print(f"\nUncertainty Analysis:")
    print(f"  Score: {result.uncertainty_metrics.uncertainty_score}/10")
    print(f"  Placeholder comments: {result.uncertainty_metrics.placeholder_comments}")
    print(f"  Conditional assumptions: {result.uncertainty_metrics.conditional_assumptions}")
    print(f"  Missing error handling: {result.uncertainty_metrics.missing_error_handling}")

    return result


def example_3_strict_mode():
    """
    Example 3: Strict mode (fails on warnings)
    """
    print("\n" + "="*70)
    print("EXAMPLE 3: Strict Mode")
    print("="*70)

    llm = LLMClient(provider='openai', model='gpt-4')

    # Normal mode
    validator_normal = SelfCritiqueValidator(
        llm_client=llm,
        strict_mode=False
    )

    # Strict mode
    validator_strict = SelfCritiqueValidator(
        llm_client=llm,
        strict_mode=True
    )

    # Code with minor issues
    code = """
def calculate_total(items):
    # Calculate total price
    total = 0
    for item in items:
        total += item['price']  # No error handling if 'price' missing
    return total
"""

    print("\n--- Normal Mode ---")
    result_normal = validator_normal.validate_code(
        code=code,
        context={'language': 'python'}
    )
    print(f"Passed: {result_normal.passed}")

    print("\n--- Strict Mode ---")
    result_strict = validator_strict.validate_code(
        code=code,
        context={'language': 'python'}
    )
    print(f"Passed: {result_strict.passed}")
    print(f"Regeneration needed: {result_strict.regeneration_needed}")

    return result_normal, result_strict


def example_4_critique_levels():
    """
    Example 4: Different critique levels
    """
    print("\n" + "="*70)
    print("EXAMPLE 4: Critique Levels (Quick vs Thorough)")
    print("="*70)

    llm = LLMClient(provider='openai', model='gpt-4')

    code = """
def authenticate_user(username, password):
    user = User.objects.get(username=username)
    if user.password == password:  # Plain text comparison!
        return user
    return None
"""

    print("\n--- Quick Critique (~2s) ---")
    validator_quick = SelfCritiqueValidator(
        llm_client=llm,
        level=CritiqueLevel.QUICK
    )
    result_quick = validator_quick.validate_code(code, {'language': 'python'})
    print(f"Findings: {len(result_quick.findings)}")

    print("\n--- Thorough Critique (~10s) ---")
    validator_thorough = SelfCritiqueValidator(
        llm_client=llm,
        level=CritiqueLevel.THOROUGH
    )
    result_thorough = validator_thorough.validate_code(code, {'language': 'python'})
    print(f"Findings: {len(result_thorough.findings)}")

    # Thorough should catch security issue with plain text password
    security_findings = [
        f for f in result_thorough.findings
        if f.category == 'security'
    ]
    print(f"Security issues found: {len(security_findings)}")

    return result_quick, result_thorough


def example_5_integration_with_rag():
    """
    Example 5: Integration with RAG for citation verification
    """
    print("\n" + "="*70)
    print("EXAMPLE 5: Integration with RAG")
    print("="*70)

    llm = LLMClient(provider='openai', model='gpt-4')
    rag = RAGAgent(db_path='../.artemis_data/rag_db')

    validator = SelfCritiqueValidator(
        llm_client=llm,
        level=CritiqueLevel.BALANCED,
        rag_agent=rag  # Enable citation verification
    )

    # Code with citations
    code_with_citations = """
def create_user(username, email):
    # From: Django Documentation v4.2
    # Reference: User model creation
    user = User.objects.create(
        username=username,
        email=email
    )
    user.save()
    return user
"""

    result = validator.validate_code(
        code=code_with_citations,
        context={'language': 'python', 'framework': 'django'}
    )

    print(f"\nCitations found: {len(result.citations)}")
    for citation in result.citations:
        print(f"\n  Source: {citation.source}")
        print(f"  Pattern: {citation.pattern[:80]}...")
        print(f"  Confidence: {citation.confidence}")

    return result


def example_6_factory_configuration():
    """
    Example 6: Using factory for environment-specific configuration
    """
    print("\n" + "="*70)
    print("EXAMPLE 6: Factory Configuration")
    print("="*70)

    llm = LLMClient(provider='openai', model='gpt-4')

    # Development: Balanced critique
    dev_validator = SelfCritiqueFactory.create_validator(
        llm_client=llm,
        environment='development'
    )
    print(f"Development: {dev_validator.level.value} critique")

    # Production: Thorough critique
    prod_validator = SelfCritiqueFactory.create_validator(
        llm_client=llm,
        environment='production',
        strict_mode=True
    )
    print(f"Production: {prod_validator.level.value} critique, strict mode")

    # Prototype: Quick critique
    proto_validator = SelfCritiqueFactory.create_validator(
        llm_client=llm,
        environment='prototype'
    )
    print(f"Prototype: {proto_validator.level.value} critique")

    return dev_validator, prod_validator, proto_validator


def example_7_integration_workflow():
    """
    Example 7: Complete workflow with validation pipeline
    """
    print("\n" + "="*70)
    print("EXAMPLE 7: Complete Validation Workflow")
    print("="*70)

    llm = LLMClient(provider='openai', model='gpt-4')
    validator = SelfCritiqueValidator(llm_client=llm)

    # Simulate generation-validation loop
    prompt = "Create a function to hash passwords securely"

    print("\n--- Attempt 1 ---")
    code_attempt_1 = """
def hash_password(password):
    # TODO: Add salt
    import hashlib
    return hashlib.md5(password.encode()).hexdigest()  # Weak algorithm!
"""

    result_1 = validator.validate_code(
        code=code_attempt_1,
        context={'language': 'python'},
        original_prompt=prompt
    )

    print(f"Passed: {result_1.passed}")
    print(f"Regeneration needed: {result_1.regeneration_needed}")

    if result_1.regeneration_needed:
        print(f"\nFeedback for retry:\n{result_1.feedback}")

        # Simulate retry with feedback
        print("\n--- Attempt 2 (with feedback) ---")
        code_attempt_2 = """
def hash_password(password):
    # Using bcrypt for secure password hashing
    # Reference: OWASP password storage guidelines
    import bcrypt

    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode(), salt)
    return hashed.decode()
"""

        result_2 = validator.validate_code(
            code=code_attempt_2,
            context={'language': 'python'},
            original_prompt=prompt
        )

        print(f"Passed: {result_2.passed}")
        print(f"Confidence: {result_2.confidence_score}/10")
        print(f"Uncertainty: {result_2.uncertainty_metrics.uncertainty_score}/10")

        return result_2

    return result_1


def main():
    """Run all examples"""
    print("\n" + "="*70)
    print("SELF-CRITIQUE VALIDATION - Integration Examples")
    print("Layer 5: Metacognitive Hallucination Reduction")
    print("="*70)

    try:
        # Example 1: Basic critique
        example_1_basic_critique()

        # Example 2: Uncertainty detection
        example_2_uncertainty_detection()

        # Example 3: Strict mode
        example_3_strict_mode()

        # Example 4: Critique levels
        example_4_critique_levels()

        # Example 5: RAG integration
        example_5_integration_with_rag()

        # Example 6: Factory configuration
        example_6_factory_configuration()

        # Example 7: Complete workflow
        example_7_integration_workflow()

        print("\n" + "="*70)
        print("✅ All examples completed successfully")
        print("="*70)

    except Exception as e:
        print(f"\n❌ Error running examples: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
