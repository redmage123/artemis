#!/usr/bin/env python3
"""
Upload React Books to RAG Database - Sequential Processing

Uploads all React-related PDFs and EPUBs from Downloads directory to RAG.
"""

from pathlib import Path
from upload_pdf_to_rag import PDFToRAGUploader
from upload_epub_to_rag import EPUBToRAGUploader


def main():
    """Upload React books sequentially"""

    print("\n" + "="*70)
    print("REACT BOOKS → RAG DATABASE (SEQUENTIAL)")
    print("="*70)

    # Initialize uploaders
    pdf_uploader = PDFToRAGUploader()
    epub_uploader = EPUBToRAGUploader()

    # Define React books to upload
    react_books = [
        {
            'path': Path("/home/bbrelin/Downloads/Abdur R. Web Forms with React. Build Robust and Scalable Forms...2025/Abdur R. Web Forms with React. Build Robust and Scalable Forms...2025.pdf"),
            'title': "Web Forms with React - Build Robust and Scalable Forms",
            'author': "Abdur R.",
            'type': 'pdf',
            'chunk_size': 5
        },
        {
            'path': Path("/home/bbrelin/Downloads/Joshi A. The React UX Architect's Handbook. Design Thinking Strategies...2025/Joshi A. The React UX Architect's Handbook. Design Thinking Strategies...2025.pdf"),
            'title': "The React UX Architect's Handbook - Design Thinking Strategies",
            'author': "Joshi A.",
            'type': 'pdf',
            'chunk_size': 5
        },
        {
            'path': Path("/home/bbrelin/Downloads/React 18 Design Patterns and Best Practices, 4th Edition/React 18 Design Patterns and Best Practices, 4th Edition.pdf"),
            'title': "React 18 Design Patterns and Best Practices (4th Edition)",
            'author': "Unknown",
            'type': 'pdf',
            'chunk_size': 5
        },
        {
            'path': Path("/home/bbrelin/Downloads/Fullstack React - The Complete Guide to ReactJS and Friends/Fullstack React - The Complete Guide to ReactJS and Friends.pdf"),
            'title': "Fullstack React - The Complete Guide to ReactJS and Friends",
            'author': "Unknown",
            'type': 'pdf',
            'chunk_size': 5
        },
        {
            'path': Path("/home/bbrelin/Downloads/The Complete Developer - Master the Full Stack with TypeScript, React, Next.js, MongoDB, and Docker/The Complete Developer - Master the Full Stack with TypeScript, React, Next.js, MongoDB, and Docker.epub"),
            'title': "The Complete Developer - Full Stack with TypeScript, React, Next.js",
            'author': "Unknown",
            'type': 'epub',
            'chunk_size': 3
        },
        {
            'path': Path("/home/bbrelin/Downloads/Learning Web Development with React and Bootstrap/Learning Web Development with React and Bootstrap.epub"),
            'title': "Learning Web Development with React and Bootstrap",
            'author': "Unknown",
            'type': 'epub',
            'chunk_size': 3
        }
    ]

    total_books = len(react_books)
    successful_uploads = 0
    failed_uploads = 0

    # Upload each book sequentially
    for i, book in enumerate(react_books, 1):
        print(f"\n{'='*70}")
        print(f"📚 BOOK {i}/{total_books}")
        print(f"{'='*70}")

        if not book['path'].exists():
            print(f"   ❌ File not found: {book['path']}")
            failed_uploads += 1
            continue

        try:
            if book['type'] == 'pdf':
                chunks_uploaded = pdf_uploader.upload_pdf_to_rag(
                    pdf_path=book['path'],
                    book_title=book['title'],
                    author=book['author'],
                    chunk_size=book['chunk_size']
                )
            else:  # epub
                chunks_uploaded = epub_uploader.upload_epub_to_rag(
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
    print(f"📊 Total chunks uploaded: {pdf_uploader.uploaded_count + epub_uploader.uploaded_count}")
    print(f"❌ Total errors: {pdf_uploader.error_count + epub_uploader.error_count}")
    print("="*70)

    # Verify RAG stats
    print("\n📊 RAG Database Stats:")
    stats = pdf_uploader.rag.get_stats()
    print(f"   Total artifacts: {stats['total_artifacts']}")
    print(f"   Code examples: {stats['by_type'].get('code_example', 0)}")
    print("="*70)


if __name__ == "__main__":
    main()
