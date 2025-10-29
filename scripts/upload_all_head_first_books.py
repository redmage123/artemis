#!/usr/bin/env python3
"""
Upload ALL Head First Books from a directory to RAG Database

WHY: Dynamically find and upload all Head First books instead of hardcoding paths
"""

import sys
from pathlib import Path
import argparse

# Add src to path to import modules
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from upload_pdf_to_rag import PDFToRAGUploader
from artemis_logger import get_logger

logger = get_logger(__name__)


def find_all_pdfs(directory: Path) -> list[Path]:
    """
    Find all PDF files in directory recursively

    Args:
        directory: Directory to search

    Returns:
        List of PDF file paths
    """
    return list(directory.rglob("*.pdf"))


def extract_title_from_filename(pdf_path: Path) -> tuple[str, str]:
    """
    Extract book title and author from filename

    Assumes format like: "Head First Python (Paul Barry) (Z-Library).pdf"

    Args:
        pdf_path: Path to PDF file

    Returns:
        (title, author) tuple
    """
    filename = pdf_path.stem  # Remove .pdf extension

    # Try to extract author from parentheses
    if "(" in filename and ")" in filename:
        parts = filename.split("(")
        title = parts[0].strip()

        # Author is in first set of parentheses
        author_part = "("
.join(parts[1:])
        if ")" in author_part:
            author = author_part.split(")")[0].strip()
        else:
            author = "Unknown"
    else:
        title = filename
        author = "Unknown"

    # Clean up common suffixes
    for suffix in [" Z-Library", " (Z-Library)", "- Z-Library"]:
        title = title.replace(suffix, "").strip()
        author = author.replace(suffix, "").strip()

    return title, author


def main():
    """Upload all Head First books from specified directory"""

    parser = argparse.ArgumentParser(description='Upload all PDF books to RAG database')
    parser.add_argument('directory', type=str, help='Directory containing PDF books')
    parser.add_argument('--chunk-size', type=int, default=5, help='Chunk size for PDF parsing (default: 5)')
    parser.add_argument('--pattern', type=str, default="*.pdf", help='File pattern to match (default: *.pdf)')
    args = parser.parse_args()

    books_dir = Path(args.directory)

    # Validate directory exists
    if not books_dir.exists():
        logger.log(f"Error: Directory not found: {books_dir}", "ERROR")
        return 1

    if not books_dir.is_dir():
        logger.log(f"Error: Path is not a directory: {books_dir}", "ERROR")
        return 1

    logger.log("="*70, "INFO")
    logger.log("ALL BOOKS → RAG DATABASE", "INFO")
    logger.log(f"Directory: {books_dir}", "INFO")
    logger.log("="*70, "INFO")

    # Find all PDFs
    pdf_files = find_all_pdfs(books_dir)

    if not pdf_files:
        logger.log(f"No PDF files found in {books_dir}", "WARNING")
        return 0

    logger.log(f"Found {len(pdf_files)} PDF files", "INFO")

    uploader = PDFToRAGUploader()

    total_chunks = 0
    successful_books = 0
    failed_books = []

    for pdf_path in sorted(pdf_files):
        title, author = extract_title_from_filename(pdf_path)

        logger.log("="*70, "INFO")
        logger.log(f"📚 Uploading: {title}", "INFO")
        logger.log(f"   Author: {author}", "INFO")
        logger.log(f"   File: {pdf_path.name}", "INFO")
        logger.log("="*70, "INFO")

        try:
            # Upload the book
            chunks_uploaded = uploader.upload_pdf_to_rag(
                pdf_path=pdf_path,
                book_title=title,
                author=author,
                chunk_size=args.chunk_size
            )

            if chunks_uploaded > 0:
                logger.log(f"✅ Successfully uploaded: {chunks_uploaded} chunks", "INFO")
                total_chunks += chunks_uploaded
                successful_books += 1
            else:
                logger.log("❌ Failed to upload", "ERROR")
                failed_books.append(title)

        except Exception as e:
            logger.log(f"❌ Error uploading: {e}", "ERROR")
            failed_books.append(title)

    # Final Summary
    logger.log("="*70, "INFO")
    logger.log("UPLOAD SUMMARY", "INFO")
    logger.log("="*70, "INFO")
    logger.log(f"📚 Books Attempted: {len(pdf_files)}", "INFO")
    logger.log(f"✅ Successfully Uploaded: {successful_books}", "INFO")
    logger.log(f"❌ Failed: {len(failed_books)}", "INFO")
    logger.log(f"📊 Total Chunks: {total_chunks}", "INFO")

    if failed_books:
        logger.log("Failed Books:", "WARNING")
        for book in failed_books:
            logger.log(f"   - {book}", "WARNING")

    logger.log("="*70, "INFO")

    # Verify RAG stats
    logger.log("📊 RAG Database Stats:", "INFO")
    stats = uploader.rag.get_stats()
    logger.log(f"   Total artifacts: {stats['total_artifacts']}", "INFO")
    logger.log(f"   Code examples: {stats['by_type'].get('code_example', 0)}", "INFO")
    logger.log("="*70, "INFO")

    return 0 if len(failed_books) == 0 else 1


if __name__ == "__main__":
    exit(main())
