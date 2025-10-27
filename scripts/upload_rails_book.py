#!/usr/bin/env python3
"""
Upload Agile Web Development with Rails 7.2 Book to RAG Database
"""

import sys
from pathlib import Path

# Add src to path to import modules
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from upload_pdf_to_rag import PDFToRAGUploader


def main():
    """Upload Agile Web Development with Rails 7.2 book"""

    print("\n" + "="*70)
    print("AGILE WEB DEVELOPMENT WITH RAILS 7.2 BOOK → RAG DATABASE")
    print("="*70)

    uploader = PDFToRAGUploader()

    # Rails book details
    rails_book = {
        'path': Path("/home/bbrelin/Downloads/Ruby S., Thomas D. Agile Web Development With Rails 7.2 2025/Ruby S., Thomas D. Agile Web Development With Rails 7.2 2025.pdf"),
        'title': "Agile Web Development with Rails 7.2",
        'author': "Ruby S., Thomas D.",
        'type': 'pdf',
        'chunk_size': 5  # 5 pages per chunk
    }

    print(f"\n{'='*70}")
    print(f"📚 Uploading Agile Web Development with Rails 7.2")
    print(f"{'='*70}")

    if not rails_book['path'].exists():
        print(f"   ❌ File not found: {rails_book['path']}")
        return 1

    try:
        # Upload the book
        chunks_uploaded = uploader.upload_pdf_to_rag(
            pdf_path=rails_book['path'],
            book_title=rails_book['title'],
            author=rails_book['author'],
            chunk_size=rails_book['chunk_size']
        )

        if chunks_uploaded > 0:
            print(f"\n   ✅ Successfully uploaded Rails 7.2 book: {chunks_uploaded} chunks")
        else:
            print(f"\n   ❌ Failed to upload Rails 7.2 book")
            return 1

    except Exception as e:
        print(f"\n   ❌ Error uploading Rails 7.2 book: {e}")
        return 1

    # Final Summary
    print("\n" + "="*70)
    print("UPLOAD SUMMARY")
    print("="*70)
    print(f"📚 Agile Web Development with Rails 7.2")
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
