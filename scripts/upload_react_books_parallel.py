#!/usr/bin/env python3
"""
Upload React Books to RAG in Parallel
"""

from pathlib import Path
from upload_pdf_to_rag import PDFToRAGUploader
from upload_epub_to_rag import EPUBToRAGUploader
import multiprocessing
import re


def extract_metadata(filename: str):
    """Extract title and author from filename"""
    # Remove file extension
    name = Path(filename).stem

    # Try to match "Author. Title...Year" pattern
    match = re.match(r'^([^.]+)\.\s*(.+?)\.\.\.[0-9]{4}$', name)
    if match:
        author = match.group(1).strip()
        title = match.group(2).strip()
        return title, author

    # Otherwise use filename as title
    return name, "Unknown"


def upload_pdf_book(pdf_path_str: str):
    """Upload a single PDF book"""
    pdf_path = Path(pdf_path_str)
    title, author = extract_metadata(pdf_path.name)

    uploader = PDFToRAGUploader()
    chunks = uploader.upload_pdf_to_rag(
        pdf_path=pdf_path,
        book_title=title,
        author=author,
        chunk_size=5
    )
    return (title, chunks, uploader.error_count)


def upload_epub_book(epub_path_str: str):
    """Upload a single EPUB book"""
    epub_path = Path(epub_path_str)
    title, author = extract_metadata(epub_path.name)

    uploader = EPUBToRAGUploader()
    chunks = uploader.upload_epub_to_rag(
        epub_path=epub_path,
        book_title=title,
        author=author,
        chunk_size=3
    )
    return (title, chunks, uploader.error_count)


def main():
    """Main execution"""
    print("\n" + "="*70)
    print("UPLOADING REACT BOOKS IN PARALLEL")
    print("="*70)

    # Define all React books
    react_books = [
        "/home/bbrelin/Downloads/Abdur R. Web Forms with React. Build Robust and Scalable Forms...2025/Abdur R. Web Forms with React. Build Robust and Scalable Forms...2025.pdf",
        "/home/bbrelin/Downloads/Fullstack React - The Complete Guide to ReactJS and Friends/Fullstack React - The Complete Guide to ReactJS and Friends.pdf",
        "/home/bbrelin/Downloads/Joshi A. The React UX Architect's Handbook. Design Thinking Strategies...2025/Joshi A. The React UX Architect's Handbook. Design Thinking Strategies...2025.pdf",
        "/home/bbrelin/Downloads/The Complete Developer - Master the Full Stack with TypeScript, React, Next.js, MongoDB, and Docker/The Complete Developer - Master the Full Stack with TypeScript, React, Next.js, MongoDB, and Docker.epub"
    ]

    print(f"\n📚 Uploading {len(react_books)} React books in parallel...\n")

    # Create process pool
    with multiprocessing.Pool(processes=4) as pool:
        results = []

        for book_path in react_books:
            if book_path.endswith('.pdf'):
                result = pool.apply_async(upload_pdf_book, (book_path,))
            else:  # .epub
                result = pool.apply_async(upload_epub_book, (book_path,))
            results.append(result)

        # Wait for all to complete
        pool.close()
        pool.join()

        # Collect results
        total_chunks = 0
        total_errors = 0

        print("\n" + "="*70)
        print("UPLOAD COMPLETE")
        print("="*70)

        for result in results:
            try:
                title, chunks, errors = result.get()
                print(f"✅ {title}: {chunks} chunks, {errors} errors")
                total_chunks += chunks
                total_errors += errors
            except Exception as e:
                print(f"❌ Error: {e}")
                total_errors += 1

        print(f"\n📊 Total: {total_chunks} chunks uploaded, {total_errors} errors")

    # Show RAG stats
    from rag_agent import RAGAgent
    rag = RAGAgent(db_path='../.artemis_data/rag_db', verbose=False)
    stats = rag.get_stats()

    print("\n📊 RAG Database Stats:")
    print(f"   Total artifacts: {stats['total_artifacts']}")
    print(f"   Code examples: {stats['by_type'].get('code_example', 0)}")
    print("="*70)
    print()


if __name__ == "__main__":
    main()
