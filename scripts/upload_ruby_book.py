#!/usr/bin/env python3
"""
Upload Ruby for Beginners Book to RAG Database
"""

import sys
from pathlib import Path

# Add src to path to import modules
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from upload_pdf_to_rag import PDFToRAGUploader


def main():
    """Upload Ruby for Beginners programming book"""

    print("\n" + "="*70)
    print("RUBY FOR BEGINNERS BOOK → RAG DATABASE")
    print("="*70)

    uploader = PDFToRAGUploader()

    # Ruby for Beginners book details
    ruby_book = {
        'path': Path("/home/bbrelin/Downloads/Blunt B. Ruby for Beginners. From Fundamentals to Building Full-Stack Apps 2025/Blunt B. Ruby for Beginners. From Fundamentals to Building Full-Stack Apps 2025.pdf"),
        'title': "Ruby for Beginners: From Fundamentals to Building Full-Stack Apps",
        'author': "Blunt B.",
        'type': 'pdf',
        'chunk_size': 5  # 5 pages per chunk
    }

    print(f"\n{'='*70}")
    print(f"📚 Uploading Ruby for Beginners Book")
    print(f"{'='*70}")

    if not ruby_book['path'].exists():
        print(f"   ❌ File not found: {ruby_book['path']}")
        return 1

    try:
        # Upload the book
        chunks_uploaded = uploader.upload_pdf_to_rag(
            pdf_path=ruby_book['path'],
            book_title=ruby_book['title'],
            author=ruby_book['author'],
            chunk_size=ruby_book['chunk_size']
        )

        if chunks_uploaded > 0:
            print(f"\n   ✅ Successfully uploaded Ruby for Beginners book: {chunks_uploaded} chunks")
        else:
            print(f"\n   ❌ Failed to upload Ruby for Beginners book")
            return 1

    except Exception as e:
        print(f"\n   ❌ Error uploading Ruby for Beginners book: {e}")
        return 1

    # Final Summary
    print("\n" + "="*70)
    print("UPLOAD SUMMARY")
    print("="*70)
    print(f"📚 Ruby for Beginners")
    print(f"✅ Successfully uploaded: {chunks_uploaded} chunks")
    print(f"📊 Total uploaded: {uploader.uploaded_count} chunks")
    print(f"❌ Total errors: {uploader.error_count}")
    print("="*70)

    # Verify RAG stats
    print("\n📊 RAG Database Stats:")
    stats = uploader.rag.get_stats()
    print(f"   Total artifacts: {stats['total_artifacts']}")
    print(f"   Code examples: {stats['by_type'].get('code_example', 0)}")
    print("="*70)

    return 0


if __name__ == "__main__":
    exit(main())
