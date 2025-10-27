#!/usr/bin/env python3
"""
Upload F# Programming Book to RAG Database
"""

import sys
from pathlib import Path

# Add src to path to import modules
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from upload_pdf_to_rag import PDFToRAGUploader


def main():
    """Upload F# programming book"""

    print("\n" + "="*70)
    print("F# PROGRAMMING BOOK → RAG DATABASE")
    print("="*70)

    uploader = PDFToRAGUploader()

    # F# book details
    fsharp_book = {
        'path': Path("/home/bbrelin/Downloads/Edet T. F# Programming. Functional-First Language on .NET Platform...2024/Edet T. F# Programming. Functional-First Language on .NET Platform...2024.pdf"),
        'title': "F# Programming: Functional-First Language on .NET Platform",
        'author': "Edet T.",
        'type': 'pdf',
        'chunk_size': 5  # 5 pages per chunk
    }

    print(f"\n{'='*70}")
    print(f"📚 Uploading F# Programming Book")
    print(f"{'='*70}")

    if not fsharp_book['path'].exists():
        print(f"   ❌ File not found: {fsharp_book['path']}")
        return 1

    try:
        # Upload the book
        chunks_uploaded = uploader.upload_pdf_to_rag(
            pdf_path=fsharp_book['path'],
            book_title=fsharp_book['title'],
            author=fsharp_book['author'],
            chunk_size=fsharp_book['chunk_size']
        )

        if chunks_uploaded > 0:
            print(f"\n   ✅ Successfully uploaded F# book: {chunks_uploaded} chunks")
        else:
            print(f"\n   ❌ Failed to upload F# book")
            return 1

    except Exception as e:
        print(f"\n   ❌ Error uploading F# book: {e}")
        return 1

    # Final Summary
    print("\n" + "="*70)
    print("UPLOAD SUMMARY")
    print("="*70)
    print(f"📚 F# Programming Book")
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
