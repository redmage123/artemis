#!/usr/bin/env python3
"""
Upload LangChain Books to RAG Database
"""

from pathlib import Path
from upload_pdf_to_rag import PDFToRAGUploader


def main():
    """Upload LangChain books"""

    print("\n" + "="*70)
    print("LANGCHAIN BOOKS → RAG DATABASE")
    print("="*70)

    uploader = PDFToRAGUploader()

    # LangChain books to upload
    langchain_books = [
        {
            'path': Path("/home/bbrelin/Downloads/Pathan H. Mastering LLM Applications with LangChain and Hugging Face...2025/Pathan H. Mastering LLM Applications with LangChain and Hugging Face...2025.pdf"),
            'title': "Mastering LLM Applications with LangChain and Hugging Face",
            'author': "Pathan H.",
            'type': 'pdf',
            'chunk_size': 5
        },
        {
            'path': Path("/home/bbrelin/Downloads/Oshin M. Learning LangChain. Building AI and LLM Applications...LangGraph 2025/Oshin M. Learning LangChain. Building AI and LLM Applications...LangGraph 2025.pdf"),
            'title': "Learning LangChain: Building AI and LLM Applications with LangGraph",
            'author': "Oshin M.",
            'type': 'pdf',
            'chunk_size': 5
        }
    ]

    total_books = len(langchain_books)
    successful_uploads = 0
    failed_uploads = 0

    # Upload each book sequentially
    for i, book in enumerate(langchain_books, 1):
        print(f"\n{'='*70}")
        print(f"📚 BOOK {i}/{total_books}")
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
