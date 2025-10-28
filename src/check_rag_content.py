#!/usr/bin/env python3
"""
Check RAG Database Content for Django and React
"""

from rag_agent import RAGAgent
from collections import Counter


def _print_sources_from_results(results, category_name, max_display=5):
    """
    Helper method to extract and print unique sources from query results.

    Args:
        results: List of query results
        category_name: Name of the category for display
        max_display: Maximum number of sources to display

    Returns:
        Set of unique sources found
    """
    if not results:
        print(f"   ❌ No {category_name} content found")
        return set()

    print(f"\n✅ Found {len(results)} {category_name}-related artifacts")
    sources = set()

    for result in results[:max_display]:
        metadata = result.get('metadata', {})
        source = metadata.get('book_title', metadata.get('file_name', 'Unknown'))
        sources.add(source)
        print(f"   - {source}")

    return sources


def _print_django_content_section(rag):
    """Search for and display Django content."""
    print("\n" + "="*70)
    print("🐍 DJANGO CONTENT")
    print("="*70)

    django_results = rag.query_similar(
        query_text="Django web framework forms models views templates",
        top_k=10,
        artifact_types=["code_example"]
    )

    django_sources = _print_sources_from_results(django_results, "Django")

    if django_sources:
        print(f"\n   Total unique Django sources: {len(django_sources)}")

    return django_results


def _print_react_content_section(rag):
    """Search for and display React content."""
    print("\n" + "="*70)
    print("⚛️  REACT CONTENT")
    print("="*70)

    react_results = rag.query_similar(
        query_text="React components hooks useState useEffect JSX frontend",
        top_k=10,
        artifact_types=["code_example"]
    )

    react_sources = _print_sources_from_results(react_results, "React")

    if react_sources:
        print(f"\n   Total unique React sources: {len(react_sources)}")

    return react_results


def _print_forms_content_section(rag):
    """Search for and display forms content."""
    print("\n" + "="*70)
    print("📝 FORMS & VALIDATION CONTENT")
    print("="*70)

    forms_results = rag.query_similar(
        query_text="form validation input field submit handling",
        top_k=10,
        artifact_types=["code_example"]
    )

    _print_sources_from_results(forms_results, "form")
    return forms_results


def _print_fullstack_content_section(rag):
    """Search for and display full-stack content."""
    print("\n" + "="*70)
    print("🔗 FULL-STACK INTEGRATION CONTENT")
    print("="*70)

    fullstack_results = rag.query_similar(
        query_text="REST API backend frontend integration database",
        top_k=10,
        artifact_types=["code_example"]
    )

    _print_sources_from_results(fullstack_results, "full-stack")
    return fullstack_results


def _print_verdict_both_technologies():
    """Print verdict when both Django and React content are available."""
    print("\n🎯 VERDICT: Artemis should be capable of producing quality")
    print("   output for Django backends and React frontends with the")
    print("   reference material now available in the RAG database.")


def _print_verdict_react_only():
    """Print verdict when only React content is available."""
    print("\n⚠️  VERDICT: React support is good, but Django content may be limited.")
    print("   Consider uploading more Django reference material.")


def _print_verdict_django_only():
    """Print verdict when only Django content is available."""
    print("\n⚠️  VERDICT: Django support is good, but React content may be limited.")
    print("   Upload more React reference material.")


def _print_verdict_limited_content():
    """Print verdict when both technologies have limited content."""
    print("\n❌ VERDICT: Limited Django and React content. More reference")
    print("   material needed for quality output.")


def _print_assessment_summary(django_results, react_results):
    """
    Print assessment summary based on available Django and React content.

    Args:
        django_results: Results from Django content query
        react_results: Results from React content query
    """
    print("\n" + "="*70)
    print("ASSESSMENT SUMMARY")
    print("="*70)

    has_django = len(django_results) > 0 if django_results else False
    has_react = len(react_results) > 0 if react_results else False

    print(f"\n{'✅' if has_django else '❌'} Django backend development support")
    print(f"{'✅' if has_react else '❌'} React frontend development support")
    print(f"{'✅' if (has_django and has_react) else '❌'} Full-stack Django + React capability")

    # Use early return pattern for verdict printing
    if has_django and has_react:
        _print_verdict_both_technologies()
        return

    if has_react and not has_django:
        _print_verdict_react_only()
        return

    if has_django and not has_react:
        _print_verdict_django_only()
        return

    _print_verdict_limited_content()


def main():
    print("\n" + "="*70)
    print("RAG DATABASE CONTENT ANALYSIS")
    print("="*70)

    rag = RAGAgent(db_path='../.artemis_data/rag_db', verbose=False)

    # Get overall stats
    stats = rag.get_stats()
    print("\n📊 Overall Statistics:")
    print(f"   Total artifacts: {stats['total_artifacts']}")
    print(f"   Code examples: {stats['by_type'].get('code_example', 0)}")

    # Search for content in different categories
    django_results = _print_django_content_section(rag)
    react_results = _print_react_content_section(rag)
    _print_forms_content_section(rag)
    _print_fullstack_content_section(rag)

    # Print assessment summary
    _print_assessment_summary(django_results, react_results)

    print("="*70 + "\n")


if __name__ == "__main__":
    main()
