#!/usr/bin/env python3
"""
Check upload status and what React books are in RAG
"""

from rag_agent import RAGAgent
from collections import Counter


def main():
    print("\n" + "="*70)
    print("UPLOAD STATUS CHECK")
    print("="*70)

    rag = RAGAgent(db_path='../.artemis_data/rag_db', verbose=False)

    # Get overall stats
    stats = rag.get_stats()
    print("\n📊 Overall Statistics:")
    print(f"   Total artifacts: {stats['total_artifacts']}")
    print(f"   Code examples: {stats['by_type'].get('code_example', 0)}")

    # Query for all React books
    print("\n" + "="*70)
    print("⚛️  REACT BOOKS IN DATABASE")
    print("="*70)

    react_results = rag.query_similar(
        query_text="React web development frontend components hooks",
        top_k=50,
        artifact_types=["code_example"]
    )

    # Collect unique book titles
    react_books = {}
    for result in react_results:
        metadata = result.get('metadata', {})
        book_title = metadata.get('book_title', 'Unknown')

        if 'react' in book_title.lower():
            if book_title not in react_books:
                react_books[book_title] = 0
            react_books[book_title] += 1

    if react_books:
        print(f"\n✅ Found {len(react_books)} unique React books:\n")
        for title, count in sorted(react_books.items(), key=lambda x: x[1], reverse=True):
            print(f"   📚 {title}")
            print(f"      └─ {count} chunks\n")
    else:
        print("   ❌ No React books found")

    # Query for all Django books
    print("="*70)
    print("🐍 DJANGO BOOKS IN DATABASE")
    print("="*70)

    django_results = rag.query_similar(
        query_text="Django web framework backend database models",
        top_k=50,
        artifact_types=["code_example"]
    )

    # Collect unique book titles
    django_books = {}
    for result in django_results:
        metadata = result.get('metadata', {})
        book_title = metadata.get('book_title', 'Unknown')

        if 'django' in book_title.lower():
            if book_title not in django_books:
                django_books[book_title] = 0
            django_books[book_title] += 1

    if django_books:
        print(f"\n✅ Found {len(django_books)} unique Django books:\n")
        for title, count in sorted(django_books.items(), key=lambda x: x[1], reverse=True):
            print(f"   📚 {title}")
            print(f"      └─ {count} chunks\n")
    else:
        print("   ❌ No Django books found")

    print("="*70)
    print("EXPECTED REACT BOOKS")
    print("="*70)
    expected = [
        "Web Forms with React - Build Robust and Scalable Forms",
        "The React UX Architect's Handbook - Design Thinking Strategies",
        "React 18 Design Patterns and Best Practices (4th Edition)",
        "Fullstack React - The Complete Guide to ReactJS and Friends",
        "The Complete Developer - Full Stack with TypeScript, React, Next.js"
    ]

    print("\nExpected to upload:")
    for i, title in enumerate(expected, 1):
        status = "✅" if any(title.lower() in book.lower() for book in react_books.keys()) else "❌"
        print(f"   {status} {i}. {title}")

    print("\n" + "="*70 + "\n")


if __name__ == "__main__":
    main()
