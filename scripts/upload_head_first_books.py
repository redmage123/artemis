#!/usr/bin/env python3
"""
Upload Head First Books to RAG Database
"""

import sys
from pathlib import Path

# Add src to path to import modules
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from upload_pdf_to_rag import PDFToRAGUploader


def main():
    """Upload Head First programming books"""

    print("\n" + "="*70)
    print("HEAD FIRST BOOKS → RAG DATABASE")
    print("="*70)

    uploader = PDFToRAGUploader()

    # Head First books
    books = [
        {
            'path': Path("/home/bbrelin/Downloads/Head First Programming A Learners Guide to Programming Using the Python Language (David Griffiths, Paul Barry) (Z-Library).pdf"),
            'title': "Head First Programming: A Learner's Guide to Programming Using Python",
            'author': "David Griffiths, Paul Barry",
            'chunk_size': 5
        },
        {
            'path': Path("/home/bbrelin/Downloads/Head First Software Development (Dan Pilone, Russ Miles) (Z-Library).pdf"),
            'title': "Head First Software Development",
            'author': "Dan Pilone, Russ Miles",
            'chunk_size': 5
        },
    ]

    total_chunks = 0
    successful_books = 0
    failed_books = []

    for book in books:
        print(f"\n{'='*70}")
        print(f"📚 Uploading: {book['title']}")
        print(f"{'='*70}")

        if not book['path'].exists():
            print(f"   ❌ File not found: {book['path']}")
            failed_books.append(book['title'])
            continue

        try:
            # Upload the book
            chunks_uploaded = uploader.upload_pdf_to_rag(
                pdf_path=book['path'],
                book_title=book['title'],
                author=book['author'],
                chunk_size=book['chunk_size']
            )

            if chunks_uploaded > 0:
                print(f"\n   ✅ Successfully uploaded: {chunks_uploaded} chunks")
                total_chunks += chunks_uploaded
                successful_books += 1
            else:
                print(f"\n   ❌ Failed to upload")
                failed_books.append(book['title'])

        except Exception as e:
            print(f"\n   ❌ Error uploading: {e}")
            failed_books.append(book['title'])

    # Final Summary
    print("\n" + "="*70)
    print("UPLOAD SUMMARY")
    print("="*70)
    print(f"📚 Books Attempted: {len(books)}")
    print(f"✅ Successfully Uploaded: {successful_books}")
    print(f"❌ Failed: {len(failed_books)}")
    print(f"📊 Total Chunks: {total_chunks}")

    if failed_books:
        print(f"\nFailed Books:")
        for book in failed_books:
            print(f"   - {book}")

    print("="*70)

    # Verify RAG stats
    print("\n📊 RAG Database Stats:")
    stats = uploader.rag.get_stats()
    print(f"   Total artifacts: {stats['total_artifacts']}")
    print(f"   Code examples: {stats['by_type'].get('code_example', 0)}")
    print("="*70)

    return 0 if len(failed_books) == 0 else 1


if __name__ == "__main__":
    exit(main())
