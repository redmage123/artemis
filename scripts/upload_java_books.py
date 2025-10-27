#!/usr/bin/env python3
"""
Upload Java Books to RAG Database
"""

from pathlib import Path
from upload_epub_to_rag import EPUBToRAGUploader


def main():
    """Upload Java books"""

    print("\n" + "="*70)
    print("JAVA BOOKS → RAG DATABASE")
    print("="*70)

    uploader = EPUBToRAGUploader()

    # Java books to upload
    java_books = [
        {
            'path': Path("/home/bbrelin/Downloads/Effective Java, 3rd Edition - 6549 [ECLiPSE]/Effective Java, 3rd Edition.epub"),
            'title': "Effective Java (3rd Edition)",
            'author': "Joshua Bloch",
            'type': 'epub',
            'chunk_size': 3
        }
    ]

    total_books = len(java_books)
    successful_uploads = 0
    failed_uploads = 0

    # Upload each book sequentially
    for i, book in enumerate(java_books, 1):
        print(f"\n{'='*70}")
        print(f"📚 BOOK {i}/{total_books}")
        print(f"{'='*70}")

        if not book['path'].exists():
            print(f"   ❌ File not found: {book['path']}")
            failed_uploads += 1
            continue

        try:
            chunks_uploaded = uploader.upload_epub_to_rag(
                epub_path=book['path'],
                book_title=book['title'],
                author=book['author'],
                chunk_size=book['chunk_size']
            )

            if chunks_uploaded > 0:
                successful_uploads += 1
                print(f"\n   ✅ Successfully uploaded book {i}/{total_books}")
            else:
                failed_uploads += 1
                print(f"\n   ❌ Failed to upload book {i}/{total_books}")

        except Exception as e:
            print(f"\n   ❌ Error uploading book {i}/{total_books}: {e}")
            failed_uploads += 1
            continue

    # Final Summary
    print("\n" + "="*70)
    print("FINAL UPLOAD SUMMARY")
    print("="*70)
    print(f"📚 Total books processed: {total_books}")
    print(f"✅ Successfully uploaded: {successful_uploads}")
    print(f"❌ Failed uploads: {failed_uploads}")
    print(f"📊 Total chunks uploaded: {uploader.uploaded_count}")
    print(f"❌ Total errors: {uploader.error_count}")
    print("="*70)

    # Verify RAG stats
    print("\n📊 RAG Database Stats:")
    stats = uploader.rag.get_stats()
    print(f"   Total artifacts: {stats['total_artifacts']}")
    print(f"   Code examples: {stats['by_type'].get('code_example', 0)}")
    print("="*70)


if __name__ == "__main__":
    main()
