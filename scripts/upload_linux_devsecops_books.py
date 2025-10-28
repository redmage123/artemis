#!/usr/bin/env python3
"""
Upload Linux Systems Administration and DevSecOps Books to RAG Database
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from upload_pdf_to_rag import PDFToRAGUploader


def main():
    """Upload Linux and DevSecOps books to RAG"""

    print("\n" + "="*70)
    print("LINUX & DEVSECOPS BOOKS → RAG DATABASE")
    print("="*70)

    uploader = PDFToRAGUploader()

    # Linux and DevSecOps books to upload
    books = [
        {
            'path': Path("/home/bbrelin/Downloads/Practical Linux System Administration A Guide to Installation, Configuration, and Management (Kenneth Hess) (Z-Library).pdf"),
            'title': "Practical Linux System Administration",
            'author': "Kenneth Hess",
            'chunk_size': 5
        },
        {
            'path': Path("/home/bbrelin/Downloads/Learning DevSecOps (for True Epub) (Steve Suehring) (Z-Library).pdf"),
            'title': "Learning DevSecOps",
            'author': "Steve Suehring",
            'chunk_size': 5
        }
    ]

    total_books = len(books)
    successful_uploads = 0
    failed_uploads = 0

    # Upload each book sequentially
    for i, book in enumerate(books, 1):
        print(f"\n{'='*70}")
        print(f"📚 BOOK {i}/{total_books}: {book['title']}")
        print(f"{'='*70}")

        if not book['path'].exists():
            print(f"   ❌ File not found: {book['path']}")
            failed_uploads += 1
            continue

        try:
            chunks_uploaded = uploader.upload_pdf_to_rag(
                pdf_path=book['path'],
                book_title=book['title'],
                author=book['author'],
                chunk_size=book['chunk_size']
            )

            if chunks_uploaded > 0:
                successful_uploads += 1
                print(f"\n   ✅ Successfully uploaded: {book['title']}")
                print(f"   📦 Chunks uploaded: {chunks_uploaded}")
            else:
                failed_uploads += 1
                print(f"\n   ❌ Failed to upload: {book['title']}")

        except Exception as e:
            print(f"\n   ❌ Error uploading {book['title']}: {e}")
            failed_uploads += 1
            import traceback
            traceback.print_exc()
            continue

    # Final Summary
    print("\n" + "="*70)
    print("FINAL UPLOAD SUMMARY")
    print("="*70)
    print(f"📚 Total books processed: {total_books}")
    print(f"✅ Successfully uploaded: {successful_uploads}")
    print(f"❌ Failed uploads: {failed_uploads}")
    print(f"📦 Total chunks uploaded: {uploader.uploaded_count}")
    print(f"❌ Total errors: {uploader.error_count}")
    print("="*70)

    # Verify RAG stats
    print("\n📊 RAG Database Stats:")
    stats = uploader.rag.get_stats()
    print(f"   Total artifacts: {stats['total_artifacts']}")
    print(f"   Code examples: {stats['by_type'].get('code_example', 0)}")
    print(f"   Documentation: {stats['by_type'].get('documentation', 0)}")
    print("="*70)


if __name__ == "__main__":
    main()
