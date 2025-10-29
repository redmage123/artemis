#!/usr/bin/env python3
"""
Upload 20 Head First Books Collection to RAG Database

WHY: Upload the complete Head First series from the local collection directory
WHAT: Processes all 20 PDF books in the '20 Head First Series Books Collection' directory
HOW: Uses PDFToRAGUploader with proper logging
"""

import sys
from pathlib import Path

# Add src to path to import modules
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from upload_pdf_to_rag import PDFToRAGUploader
from artemis_logger import get_logger

logger = get_logger(__name__)


def main():
    """Upload all 20 Head First books from the collection directory"""

    # Directory containing the books
    books_dir = Path(__file__).parent.parent / "20 Head First Series Books Collection"

    # Validate directory exists
    if not books_dir.exists():
        logger.log(f"❌ Error: Directory not found: {books_dir}", "ERROR")
        return 1

    logger.log("="*70, "INFO")
    logger.log("20 HEAD FIRST BOOKS COLLECTION → RAG DATABASE", "INFO")
    logger.log(f"Directory: {books_dir}", "INFO")
    logger.log("="*70, "INFO")

    # Find all PDF files (excluding covers directory)
    pdf_files = [f for f in books_dir.glob("*.pdf")]

    if not pdf_files:
        logger.log(f"❌ No PDF files found in {books_dir}", "WARNING")
        return 0

    logger.log(f"📚 Found {len(pdf_files)} PDF files", "INFO")
    logger.log("", "INFO")

    uploader = PDFToRAGUploader()

    # Define all 20 books with proper metadata
    books = [
        {"filename": "Head First Ajax.pdf", "title": "Head First Ajax", "author": "Rebecca Riordan"},
        {"filename": "Head First C.pdf", "title": "Head First C", "author": "David Griffiths, Dawn Griffiths"},
        {"filename": "Head First C#.pdf", "title": "Head First C#", "author": "Andrew Stellman, Jennifer Greene"},
        {"filename": "Head First Data Analysis.pdf", "title": "Head First Data Analysis", "author": "Michael Milton"},
        {"filename": "Head First Design Patterns.pdf", "title": "Head First Design Patterns", "author": "Eric Freeman, Elisabeth Robson"},
        {"filename": "Head First Excel.pdf", "title": "Head First Excel", "author": "Michael Milton"},
        {"filename": "Head First iPhone Development.pdf", "title": "Head First iPhone Development", "author": "Dan Pilone, Tracey Pilone"},
        {"filename": "Head First JavaScript.pdf", "title": "Head First JavaScript", "author": "Michael Morrison"},
        {"filename": "Head First Mobile Web.pdf", "title": "Head First Mobile Web", "author": "Lyza Danger Gardner, Jason Grigsby"},
        {"filename": "Head First Networking.pdf", "title": "Head First Networking", "author": "Al Anderson, Ryan Benedetti"},
        {"filename": "Head First Object-Oriented Analysis and Design.pdf", "title": "Head First Object-Oriented Analysis and Design", "author": "Brett McLaughlin, Gary Pollice, David West"},
        {"filename": "Head First PHP & MySQL.pdf", "title": "Head First PHP & MySQL", "author": "Lynn Beighley, Michael Morrison"},
        {"filename": "Head First PMP, 3rd Edition.pdf", "title": "Head First PMP (3rd Edition)", "author": "Jennifer Greene, Andrew Stellman"},
        {"filename": "Head First Python.pdf", "title": "Head First Python", "author": "Paul Barry"},
        {"filename": "Head First Rails.pdf", "title": "Head First Rails", "author": "David Griffiths"},
        {"filename": "Head First Servlets and JSP.pdf", "title": "Head First Servlets and JSP", "author": "Bryan Basham, Kathy Sierra, Bert Bates"},
        {"filename": "Head First Software Development.pdf", "title": "Head First Software Development", "author": "Dan Pilone, Russ Miles"},
        {"filename": "Head First SQL.pdf", "title": "Head First SQL", "author": "Lynn Beighley"},
        {"filename": "Head First Web Design.pdf", "title": "Head First Web Design", "author": "Ethan Watrall, Jeff Siarto"},
        {"filename": "Head First WordPress.pdf", "title": "Head First WordPress", "author": "Jeff Siarto"},
    ]

    total_chunks = 0
    successful_books = 0
    failed_books = []

    for book in books:
        pdf_path = books_dir / book["filename"]

        logger.log("="*70, "INFO")
        logger.log(f"📚 Uploading: {book['title']}", "INFO")
        logger.log(f"   Author: {book['author']}", "INFO")
        logger.log(f"   File: {book['filename']}", "INFO")
        logger.log("="*70, "INFO")

        if not pdf_path.exists():
            logger.log(f"   ❌ File not found: {pdf_path}", "WARNING")
            failed_books.append(book['title'])
            continue

        try:
            # Upload the book (chunk_size=5 pages for better granularity)
            chunks_uploaded = uploader.upload_pdf_to_rag(
                pdf_path=pdf_path,
                book_title=book['title'],
                author=book['author'],
                chunk_size=5
            )

            if chunks_uploaded > 0:
                logger.log(f"   ✅ Successfully uploaded: {chunks_uploaded} chunks", "INFO")
                total_chunks += chunks_uploaded
                successful_books += 1
            else:
                logger.log("   ❌ Failed to upload", "ERROR")
                failed_books.append(book['title'])

        except Exception as e:
            logger.log(f"   ❌ Error uploading: {e}", "ERROR")
            failed_books.append(book['title'])

    # Final Summary
    logger.log("", "INFO")
    logger.log("="*70, "INFO")
    logger.log("UPLOAD SUMMARY", "INFO")
    logger.log("="*70, "INFO")
    logger.log(f"📚 Books Attempted: {len(books)}", "INFO")
    logger.log(f"✅ Successfully Uploaded: {successful_books}", "INFO")
    logger.log(f"❌ Failed: {len(failed_books)}", "INFO")
    logger.log(f"📊 Total Chunks: {total_chunks}", "INFO")

    if failed_books:
        logger.log("", "INFO")
        logger.log("Failed Books:", "WARNING")
        for book_title in failed_books:
            logger.log(f"   - {book_title}", "WARNING")

    logger.log("="*70, "INFO")

    # Verify RAG stats
    logger.log("", "INFO")
    logger.log("📊 RAG Database Stats:", "INFO")
    stats = uploader.rag.get_stats()
    logger.log(f"   Total artifacts: {stats['total_artifacts']}", "INFO")
    logger.log(f"   Code examples: {stats['by_type'].get('code_example', 0)}", "INFO")
    logger.log("="*70, "INFO")

    return 0 if len(failed_books) == 0 else 1


if __name__ == "__main__":
    exit(main())
