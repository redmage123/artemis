#!/usr/bin/env python3
"""
Upload C#/.NET related books to RAG database.

WHY: Add C# and .NET books to RAG for Artemis to reference
     during development tasks involving .NET technologies.

RESPONSIBILITY: Extract text from PDFs and upload to RAG in chunks.

PATTERNS: Same pattern as upload_technical_books.py

NOTE: Head First C# was already uploaded in the Head First collection.
      The Udemy courses are video-only with no text transcripts.
"""
import sys
import os
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from artemis_logger import get_logger
from rag_agent import RAGAgent

try:
    import pdfplumber
except ImportError:
    logger = get_logger('book_upload')
    logger.log("Missing dependencies. Install with: pip install pdfplumber", "ERROR")
    sys.exit(1)

logger = get_logger('book_upload')

# Book metadata
BOOKS = [
    {
        "title": "F# Programming: Functional-First Language on .NET Platform",
        "author": "Edet T.",
        "category": "dotnet",
        "file": "/home/bbrelin/Downloads/Edet T. F# Programming. Functional-First Language on .NET Platform...2024/Edet T. F# Programming. Functional-First Language on .NET Platform...2024.pdf"
    }
]


def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract text from PDF using pdfplumber."""
    text_parts = []

    with pdfplumber.open(pdf_path) as pdf:
        total_pages = len(pdf.pages)
        logger.log(f"   📄 Total pages: {total_pages}", "INFO")

        for i, page in enumerate(pdf.pages, 1):
            if i % 50 == 0:
                logger.log(f"   ✓ Processed {i}/{total_pages} pages", "INFO")

            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)

        logger.log(f"   ✅ Extracted {len(text_parts)} pages with text", "INFO")

    return "\n\n".join(text_parts)


def chunk_text(text: str, chunk_size: int = 3000) -> list:
    """
    Split text into chunks by character count.

    WHY: Large books need to be chunked for vector embeddings.
         3000 chars ≈ 750 tokens, good for embedding models.
    """
    chunks = []
    words = text.split()
    current_chunk = []
    current_length = 0

    for word in words:
        word_length = len(word) + 1  # +1 for space

        if current_length + word_length > chunk_size and current_chunk:
            chunks.append(" ".join(current_chunk))
            current_chunk = [word]
            current_length = word_length
        else:
            current_chunk.append(word)
            current_length += word_length

    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks


def upload_book(book_info: dict, rag: RAGAgent) -> bool:
    """Upload a single book to RAG database."""
    try:
        logger.log("=" * 70, "INFO")
        logger.log(f"📚 Uploading: {book_info['title']}", "INFO")
        logger.log(f"   Author: {book_info['author']}", "INFO")
        logger.log(f"   Category: {book_info['category']}", "INFO")
        logger.log(f"   File: {Path(book_info['file']).name}", "INFO")
        logger.log("=" * 70, "INFO")

        file_path = Path(book_info['file'])

        if not file_path.exists():
            logger.log(f"   ❌ File not found: {file_path}", "ERROR")
            return False

        file_size_mb = file_path.stat().st_size / (1024 * 1024)
        logger.log(f"   📁 File: {file_path.name}", "INFO")
        logger.log(f"   📏 Size: {file_size_mb:.2f} MB", "INFO")
        logger.log("", "INFO")

        # Extract text
        logger.log("   🔍 Extracting text...", "INFO")
        logger.log("   📖 Using pdfplumber (high quality)", "INFO")
        text = extract_text_from_pdf(str(file_path))

        if not text.strip():
            logger.log("   ❌ No text extracted from file", "ERROR")
            return False

        logger.log("", "INFO")

        # Create chunks
        logger.log("   📦 Creating chunks (chunk size: 3000 chars)...", "INFO")
        chunks = chunk_text(text)
        logger.log(f"   ✅ Created {len(chunks)} chunks", "INFO")
        logger.log("", "INFO")

        # Upload to RAG
        logger.log("   ☁️  Uploading to RAG...", "INFO")

        for i, chunk in enumerate(chunks, 1):
            metadata = {
                "source": "technical_book",
                "book_title": book_info['title'],
                "author": book_info['author'],
                "category": book_info['category'],
                "chunk_index": i,
                "total_chunks": len(chunks)
            }

            rag.store_artifact(
                artifact_type="code_example",
                card_id=f"book-{book_info['category']}",
                task_title=book_info['title'],
                content=chunk,
                metadata=metadata
            )

            if i % 10 == 0:
                logger.log(f"   ✓ Uploaded {i}/{len(chunks)} chunks", "INFO")

        logger.log(f"   ✅ Successfully uploaded {len(chunks)}/{len(chunks)} chunks", "INFO")
        logger.log(f"   ✅ Successfully uploaded: {len(chunks)} chunks", "INFO")

        return True

    except Exception as e:
        logger.log(f"   ❌ Failed to upload {book_info['title']}: {e}", "ERROR")
        return False


def main():
    """Main entry point."""
    logger.log("=" * 70, "INFO")
    logger.log("C# / .NET BOOKS → RAG DATABASE", "INFO")
    logger.log("=" * 70, "INFO")
    logger.log(f"📚 Found {len(BOOKS)} books to upload", "INFO")
    logger.log("", "INFO")

    logger.log("ℹ️  NOTE: Head First C# already uploaded in Head First collection", "INFO")
    logger.log("ℹ️  NOTE: Udemy courses are video-only (no text transcripts)", "INFO")
    logger.log("", "INFO")

    # Initialize RAG
    rag = RAGAgent()

    # Upload each book
    successful = 0
    failed = 0

    for book in BOOKS:
        if upload_book(book, rag):
            successful += 1
        else:
            failed += 1

    # Summary
    logger.log("", "INFO")
    logger.log("=" * 70, "INFO")
    logger.log("UPLOAD SUMMARY", "INFO")
    logger.log("=" * 70, "INFO")
    logger.log(f"✅ Successfully Uploaded: {successful}", "INFO")
    if failed > 0:
        logger.log(f"❌ Failed: {failed}", "INFO")
    logger.log("", "INFO")
    logger.log("📊 C#/.NET Resources Available in RAG:", "INFO")
    logger.log("   • Head First C# (already uploaded)", "INFO")
    logger.log(f"   • F# Programming (.NET) - {successful} book(s) uploaded", "INFO")
    logger.log("=" * 70, "INFO")


if __name__ == "__main__":
    main()
