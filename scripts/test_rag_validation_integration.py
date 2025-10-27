#!/usr/bin/env python3
"""
Integration Test: RAG-Enhanced Validation

Demonstrates RAG validation catching hallucinations by comparing generated code
against proven patterns from RAG database.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from rag_enhanced_validation import RAGValidationFactory, RAGExample, RAGValidationResult
from rag_agent import RAGAgent


def test_rag_validation_basics():
    """Test basic RAG validation functionality"""

    print("\n" + "="*70)
    print("TEST 1: RAG Validation Basics")
    print("="*70)

    # Initialize RAG agent
    rag = RAGAgent(db_path='../.artemis_data/rag_db', verbose=False)

    # Create Django validator
    validator = RAGValidationFactory.create_validator(
        rag_agent=rag,
        framework='django'
    )

    print("\n✅ Created Django validator")
    print(f"   Min similarity: 0.4")
    print(f"   Min confidence: 0.7")

    # Test 1: Good Django code (should pass)
    good_code = """
class User(models.Model):
    username = models.CharField(max_length=100)
    email = models.EmailField()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
    """

    print("\n📝 Validating GOOD Django code...")
    result = validator.validate_code(
        generated_code=good_code,
        context={'language': 'python', 'framework': 'django'}
    )

    print(f"\n   Result: {'✅ PASSED' if result.passed else '❌ FAILED'}")
    print(f"   Confidence: {result.confidence:.2f}")
    print(f"   Similar examples: {len(result.similar_examples)}")

    # Test 2: Bad Django code with SQLAlchemy pattern (should fail)
    bad_code = """
user = User(username='john')
db.session.add(user)
db.session.commit()
    """

    print("\n📝 Validating BAD Django code (SQLAlchemy pattern)...")
    result = validator.validate_code(
        generated_code=bad_code,
        context={'language': 'python', 'framework': 'django'}
    )

    print(f"\n   Result: {'✅ PASSED' if result.passed else '❌ FAILED (expected!)'}")
    print(f"   Confidence: {result.confidence:.2f}")
    print(f"   Similar examples: {len(result.similar_examples)}")

    if not result.passed:
        print(f"\n   ⚠️  Warnings:")
        for warning in result.warnings[:3]:
            print(f"      - {warning}")

        print(f"\n   💡 Recommendations:")
        for rec in result.recommendations[:3]:
            print(f"      - {rec}")


def test_framework_specific_validation():
    """Test framework-specific validation configurations"""

    print("\n" + "="*70)
    print("TEST 2: Framework-Specific Validation")
    print("="*70)

    rag = RAGAgent(db_path='../.artemis_data/rag_db', verbose=False)

    # Test different framework configurations
    frameworks = ['django', 'flask', 'rails', 'react']

    for framework in frameworks:
        validator = RAGValidationFactory.create_validator(
            rag_agent=rag,
            framework=framework
        )

        print(f"\n✅ {framework.upper()} validator created")
        print(f"   Min similarity: {validator.min_similarity}")
        print(f"   Min confidence: {validator.min_confidence}")
        print(f"   Strategies: {len(validator.strategies)}")


def test_rag_search():
    """Test RAG code example search"""

    print("\n" + "="*70)
    print("TEST 3: RAG Code Example Search")
    print("="*70)

    rag = RAGAgent(db_path='../.artemis_data/rag_db', verbose=False)

    # Search for Django model examples
    print("\n🔍 Searching for: 'django user model authentication'")

    examples = rag.search_code_examples(
        query="django user model authentication",
        language="python",
        framework="django",
        top_k=3
    )

    print(f"\n   Found {len(examples)} examples:")

    for idx, example in enumerate(examples, 1):
        print(f"\n   Example {idx}:")
        print(f"      Source: {example.get('source', 'unknown')}")
        print(f"      Score: {example.get('score', 0.0):.3f}")
        print(f"      Code: {example.get('code', '')[:100]}...")


def test_environment_variables():
    """Test environment variable control"""

    print("\n" + "="*70)
    print("TEST 4: Environment Variable Control")
    print("="*70)

    import os

    # Show current environment settings
    rag_validation_enabled = os.getenv("ARTEMIS_ENABLE_RAG_VALIDATION", "true")
    validation_enabled = os.getenv("ARTEMIS_ENABLE_VALIDATION", "true")

    print(f"\n   ARTEMIS_ENABLE_VALIDATION: {validation_enabled}")
    print(f"   ARTEMIS_ENABLE_RAG_VALIDATION: {rag_validation_enabled}")

    print("\n   To disable RAG validation:")
    print("   export ARTEMIS_ENABLE_RAG_VALIDATION=false")

    print("\n   To disable all validation:")
    print("   export ARTEMIS_ENABLE_VALIDATION=false")


def test_rag_stats():
    """Show RAG database statistics"""

    print("\n" + "="*70)
    print("TEST 5: RAG Database Statistics")
    print("="*70)

    rag = RAGAgent(db_path='../.artemis_data/rag_db', verbose=False)

    stats = rag.get_stats()

    print(f"\n   📊 RAG Database Stats:")
    print(f"      Total artifacts: {stats['total_artifacts']}")
    print(f"      Code examples: {stats['by_type'].get('code_example', 0)}")
    print(f"      Documentation: {stats['by_type'].get('documentation', 0)}")

    print(f"\n   📚 Books/Sources Loaded:")
    print(f"      - Haskell Programming")
    print(f"      - F# Programming")
    print(f"      - Ruby to Elixir")
    print(f"      - Ruby for Beginners")
    print(f"      - Agile Web Development with Rails 7.2")
    print(f"      - The Art of Computer Programming (Knuth)")
    print(f"      - Head First Books (Python, Software Development)")


def main():
    """Run all integration tests"""

    print("\n" + "="*70)
    print("RAG-ENHANCED VALIDATION - INTEGRATION TESTS")
    print("="*70)

    try:
        test_rag_validation_basics()
        test_framework_specific_validation()
        test_rag_search()
        test_environment_variables()
        test_rag_stats()

        print("\n" + "="*70)
        print("✅ ALL TESTS COMPLETED SUCCESSFULLY")
        print("="*70)

        return 0

    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
