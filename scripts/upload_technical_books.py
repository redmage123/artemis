#!/usr/bin/env python3
"""
Upload Unreal Engine, Blender, and Terraform books to RAG database.

WHY: Add specialized technical books to RAG for Artemis to reference
     during development tasks involving these technologies.

RESPONSIBILITY: Extract text from PDFs/EPUBs and upload to RAG in chunks.

PATTERNS: Same pattern as upload_20_head_first_collection.py
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
    import ebooklib
    from ebooklib import epub
    from bs4 import BeautifulSoup
except ImportError:
    logger = get_logger('book_upload')
    logger.log("Missing dependencies. Install with: pip install pdfplumber ebooklib beautifulsoup4", "ERROR")
    sys.exit(1)

logger = get_logger('book_upload')

# Book metadata with corrected titles
BOOKS = [
    {
        "title": "Artificial Intelligence in Unreal Engine 5",
        "author": "Marco Secchi",
        "category": "unreal_engine",
        "file": "/home/bbrelin/Downloads/Artificial Intelligence in Unreal Engine 5 (Marco Secchi) (Z-Library).epub"
    },
    {
        "title": "Game Development Concepts in C++ with Unreal Engine",
        "author": "Sheikh Sohel Moon",
        "category": "unreal_engine",
        "file": "/home/bbrelin/Downloads/Game Development Concepts in C++ Elevate Your Skills with Unreal Engine (Sheikh Sohel Moon) (Z-Library).pdf"
    },
    {
        "title": "Terraform Up and Running: Infrastructure as Code, 3rd Edition",
        "author": "Yevgeniy Brikman",
        "category": "terraform",
        "file": "/home/bbrelin/Downloads/Terraform Up and Running Writing Infrastructure as Code, 3rd Edition (Yevgeniy Brikman) (Z-Library).pdf"
    },
    {
        "title": "Terraform for Developers: Essentials of Infrastructure Automation 2023",
        "author": "Kimiko Lee",
        "category": "terraform",
        "file": "/home/bbrelin/Downloads/Terraform for Developers. Essentials of Infrastructure Automation...2023 (Kimiko Lee) (Z-Library).pdf"
    },
    {
        "title": "Blender 3D: A Beginners 15 Step Exercise Book",
        "author": "Thomas McDonald",
        "category": "blender",
        "file": "/home/bbrelin/Downloads/Blender 3D A Beginners 15 Step Exercise Book (Thomas mc Donald) (Z-Library).pdf"
    },
    {
        "title": "Learning Blender: A Hands-On Guide to 3D Animated Characters, 2nd Edition",
        "author": "Oliver Villar",
        "category": "blender",
        "file": "/home/bbrelin/Downloads/Learning Blender A Hands-On Guide to Creating 3D Animated Characters - Second Edition (Oliver Villar) (Z-Library).epub"
    },
    {
        "title": "Blender 3D Basics: Guide to 3D Modeling and Animation 2.7",
        "author": "Gordon C. Fisher",
        "category": "blender",
        "file": "/home/bbrelin/Downloads/Blender 3D Basics A quick and easy-to-use guide to create 3D modeling and animation using Blender 2.7 Beginners Guide - 2nd… (Gordon C. Fisher) (Z-Library).pdf"
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


def extract_text_from_epub(epub_path: str) -> str:
    """Extract text from EPUB using ebooklib."""
    text_parts = []

    book = epub.read_epub(epub_path)
    items = list(book.get_items_of_type(ebooklib.ITEM_DOCUMENT))
    total_items = len(items)

    logger.log(f"   📄 Total chapters/sections: {total_items}", "INFO")

    for i, item in enumerate(items, 1):
        if i % 10 == 0:
            logger.log(f"   ✓ Processed {i}/{total_items} sections", "INFO")

        content = item.get_content()
        soup = BeautifulSoup(content, 'html.parser')
        text = soup.get_text()

        if text.strip():
            text_parts.append(text)

    logger.log(f"   ✅ Extracted {len(text_parts)} sections with text", "INFO")

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

        # Extract text based on file type
        logger.log("   🔍 Extracting text...", "INFO")

        if file_path.suffix.lower() == '.pdf':
            logger.log("   📖 Using pdfplumber (high quality)", "INFO")
            text = extract_text_from_pdf(str(file_path))
        elif file_path.suffix.lower() == '.epub':
            logger.log("   📖 Using ebooklib + BeautifulSoup", "INFO")
            text = extract_text_from_epub(str(file_path))
        else:
            logger.log(f"   ❌ Unsupported format: {file_path.suffix}", "ERROR")
            return False

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
    logger.log("TECHNICAL BOOKS → RAG DATABASE", "INFO")
    logger.log("Categories: Unreal Engine, Blender, Terraform", "INFO")
    logger.log("=" * 70, "INFO")
    logger.log(f"📚 Found {len(BOOKS)} books to upload", "INFO")
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
    logger.log("=" * 70, "INFO")


if __name__ == "__main__":
    main()
