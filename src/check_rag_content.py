#!/usr/bin/env python3
"""
Check RAG Database Content for Django and React
"""

from rag_agent import RAGAgent
from collections import Counter


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

    # Search for Django content
    print("\n" + "="*70)
    print("🐍 DJANGO CONTENT")
    print("="*70)

    django_results = rag.query_similar(
        query_text="Django web framework forms models views templates",
        top_k=10,
        artifact_types=["code_example"]
    )

    if django_results:
        print(f"\n✅ Found {len(django_results)} Django-related artifacts")
        django_sources = set()
        for result in django_results[:5]:
            metadata = result.get('metadata', {})
            source = metadata.get('book_title', metadata.get('file_name', 'Unknown'))
            django_sources.add(source)
            print(f"   - {source}")
        print(f"\n   Total unique Django sources: {len(django_sources)}")
    else:
        print("   ❌ No Django content found")

    # Search for React content
    print("\n" + "="*70)
    print("⚛️  REACT CONTENT")
    print("="*70)

    react_results = rag.query_similar(
        query_text="React components hooks useState useEffect JSX frontend",
        top_k=10,
        artifact_types=["code_example"]
    )

    if react_results:
        print(f"\n✅ Found {len(react_results)} React-related artifacts")
        react_sources = set()
        for result in react_results[:5]:
            metadata = result.get('metadata', {})
            source = metadata.get('book_title', metadata.get('file_name', 'Unknown'))
            react_sources.add(source)
            print(f"   - {source}")
        print(f"\n   Total unique React sources: {len(react_sources)}")
    else:
        print("   ❌ No React content found")

    # Search for forms content (relevant for both)
    print("\n" + "="*70)
    print("📝 FORMS & VALIDATION CONTENT")
    print("="*70)

    forms_results = rag.query_similar(
        query_text="form validation input field submit handling",
        top_k=10,
        artifact_types=["code_example"]
    )

    if forms_results:
        print(f"\n✅ Found {len(forms_results)} form-related artifacts")
        forms_sources = set()
        for result in forms_results[:5]:
            metadata = result.get('metadata', {})
            source = metadata.get('book_title', metadata.get('file_name', 'Unknown'))
            forms_sources.add(source)
            print(f"   - {source}")
    else:
        print("   ❌ No forms content found")

    # Search for full-stack content
    print("\n" + "="*70)
    print("🔗 FULL-STACK INTEGRATION CONTENT")
    print("="*70)

    fullstack_results = rag.query_similar(
        query_text="REST API backend frontend integration database",
        top_k=10,
        artifact_types=["code_example"]
    )

    if fullstack_results:
        print(f"\n✅ Found {len(fullstack_results)} full-stack artifacts")
        fullstack_sources = set()
        for result in fullstack_results[:5]:
            metadata = result.get('metadata', {})
            source = metadata.get('book_title', metadata.get('file_name', 'Unknown'))
            fullstack_sources.add(source)
            print(f"   - {source}")
    else:
        print("   ❌ No full-stack content found")

    print("\n" + "="*70)
    print("ASSESSMENT SUMMARY")
    print("="*70)

    has_django = len(django_results) > 0 if django_results else False
    has_react = len(react_results) > 0 if react_results else False

    print(f"\n{'✅' if has_django else '❌'} Django backend development support")
    print(f"{'✅' if has_react else '❌'} React frontend development support")
    print(f"{'✅' if (has_django and has_react) else '❌'} Full-stack Django + React capability")

    if has_django and has_react:
        print("\n🎯 VERDICT: Artemis should be capable of producing quality")
        print("   output for Django backends and React frontends with the")
        print("   reference material now available in the RAG database.")
    elif has_react and not has_django:
        print("\n⚠️  VERDICT: React support is good, but Django content may be limited.")
        print("   Consider uploading more Django reference material.")
    elif has_django and not has_react:
        print("\n⚠️  VERDICT: Django support is good, but React content may be limited.")
        print("   Upload more React reference material.")
    else:
        print("\n❌ VERDICT: Limited Django and React content. More reference")
        print("   material needed for quality output.")

    print("="*70 + "\n")


if __name__ == "__main__":
    main()
