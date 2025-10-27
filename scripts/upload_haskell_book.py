#!/usr/bin/env python3
"""
Upload Haskell Programming Book to RAG Database
"""

from pathlib import Path
from upload_pdf_to_rag import PDFToRAGUploader


def main():
    """Upload Haskell programming book"""

    print("\n" + "="*70)
    print("HASKELL PROGRAMMING BOOK → RAG DATABASE")
    print("="*70)

    uploader = PDFToRAGUploader()

    # Haskell book details
    haskell_book = {
        'path': Path("/home/bbrelin/Downloads/Edet T. Haskell Programming. Pure Functional Language with Strong Typing...2024/Edet T. Haskell Programming. Pure Functional Language with Strong Typing...2024.pdf"),
        'title': "Haskell Programming: Pure Functional Language with Strong Typing",
        'author': "Edet T.",
        'type': 'pdf',
        'chunk_size': 5  # 5 pages per chunk
    }

    print(f"\n{'='*70}")
    print(f"📚 Uploading Haskell Programming Book")
    print(f"{'='*70}")

    if not haskell_book['path'].exists():
        print(f"   ❌ File not found: {haskell_book['path']}")
        return 1

    try:
        # Upload the book
        chunks_uploaded = uploader.upload_pdf_to_rag(
            pdf_path=haskell_book['path'],
            book_title=haskell_book['title'],
            author=haskell_book['author'],
            chunk_size=haskell_book['chunk_size']
        )

        if chunks_uploaded > 0:
            print(f"\n   ✅ Successfully uploaded Haskell book: {chunks_uploaded} chunks")
        else:
            print(f"\n   ❌ Failed to upload Haskell book")
            return 1

    except Exception as e:
        print(f"\n   ❌ Error uploading Haskell book: {e}")
        return 1

    # Final Summary
    print("\n" + "="*70)
    print("UPLOAD SUMMARY")
    print("="*70)
    print(f"📚 Haskell Programming Book")
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
