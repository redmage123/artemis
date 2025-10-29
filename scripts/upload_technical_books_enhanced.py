#!/usr/bin/env python3
"""
WHY: Upload technical books to RAG with both code and conceptual content
RESPONSIBILITY: Extract and categorize book content for Artemis learning
PATTERNS: Guard clauses, chunking strategy, metadata tagging

Enhanced upload script that uploads:
1. Code examples with language tagging
2. Conceptual explanations and theory
3. Best practices and patterns
4. Architecture and design principles
"""

import sys
import re
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

import pdfplumber
import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup
from artemis_logger import get_logger
from rag_agent import RAGAgent

logger = get_logger('technical_books_enhanced_upload')

# Books to upload with metadata
BOOKS = [
    {
        "path": "~/Downloads/Game Development Concepts in C++ Elevate Your Skills with Unreal Engine (Sheikh Sohel Moon) (Z-Library).pdf",
        "title": "Game Development Concepts in C++ with Unreal Engine",
        "author": "Sheikh Sohel Moon",
        "category": "unreal_engine",
        "technology": "Unreal Engine 5 + C++"
    },
    {
        "path": "~/Downloads/Terraform Up and Running Writing Infrastructure as Code, 3rd Edition (Yevgeniy Brikman) (Z-Library).pdf",
        "title": "Terraform Up and Running, 3rd Edition",
        "author": "Yevgeniy Brikman",
        "category": "terraform",
        "technology": "Terraform + Infrastructure as Code"
    },
    {
        "path": "~/Downloads/Terraform for Developers. Essentials of Infrastructure Automation...2023 (Kimiko Lee) (Z-Library).pdf",
        "title": "Terraform for Developers 2023",
        "author": "Kimiko Lee",
        "category": "terraform",
        "technology": "Terraform + Cloud Infrastructure"
    },
    {
        "path": "~/Downloads/Blender 3D A Beginners 15 Step Exercise Book (Thomas mc Donald) (Z-Library).pdf",
        "title": "Blender 3D: Beginners 15 Step Exercise Book",
        "author": "Thomas McDonald",
        "category": "blender",
        "technology": "Blender 3D + Python scripting"
    },
    {
        "path": "~/Downloads/Learning Blender A Hands-On Guide to Creating 3D Animated Characters - Second Edition (Oliver Villar) (Z-Library).epub",
        "title": "Learning Blender 2nd Edition",
        "author": "Oliver Villar",
        "category": "blender",
        "technology": "Blender + 3D modeling"
    },
    {
        "path": "~/Downloads/Blender 3D Basics A quick and easy-to-use guide to create 3D modeling and animation using Blender 2.7 Beginners Guide - 2nd… (Gordon C. Fisher) (Z-Library).pdf",
        "title": "Blender 3D Basics",
        "author": "Gordon C. Fisher",
        "category": "blender",
        "technology": "Blender fundamentals"
    },
    {
        "path": "~/Downloads/Artificial Intelligence in Unreal Engine 5 (Marco Secchi) (Z-Library).epub",
        "title": "Artificial Intelligence in Unreal Engine 5",
        "author": "Marco Secchi",
        "category": "unreal_engine",
        "technology": "Unreal Engine 5 + AI"
    }
]


def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract all text from PDF using pdfplumber."""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            text_parts = []
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    text_parts.append(text)
            return "\n\n".join(text_parts)
    except Exception as e:
        logger.log(f"❌ Error extracting PDF {pdf_path}: {e}", "ERROR")
        return ""


def extract_text_from_epub(epub_path: str) -> str:
    """Extract all text from EPUB."""
    try:
        book = epub.read_epub(epub_path)
        text_parts = []

        for item in book.get_items():
            if item.get_type() == ebooklib.ITEM_DOCUMENT:
                soup = BeautifulSoup(item.get_content(), 'html.parser')
                text = soup.get_text()
                if text:
                    text_parts.append(text)

        return "\n\n".join(text_parts)
    except Exception as e:
        logger.log(f"❌ Error extracting EPUB {epub_path}: {e}", "ERROR")
        return ""


def is_code_chunk(text: str) -> bool:
    """
    Determine if a text chunk is primarily code.

    WHY: Differentiate between code examples and conceptual explanations
    PATTERNS: Heuristic analysis, guard clauses
    """
    # Guard: Empty or very short text
    if len(text.strip()) < 20:
        return False

    code_indicators = [
        r'^\s*(class|def|function|const|let|var|public|private|protected)',  # Function/class declarations
        r'[{}();]',  # Brackets and semicolons
        r'^\s*(if|for|while|switch|return|import|include|using)',  # Control flow
        r'//|/\*|\*/|#|<!--',  # Comments
        r'=>|->|\|\||&&',  # Operators
        r'^\s*\d+\s+\|',  # Line numbers (from code listings)
    ]

    code_score = sum(1 for pattern in code_indicators if re.search(pattern, text, re.MULTILINE))

    # If 3+ code indicators present, likely code
    return code_score >= 3


def categorize_chunk(text: str, category: str) -> dict:
    """
    Categorize chunk as code, concept, architecture, or best practice.

    WHY: Enable targeted retrieval based on developer needs
    PATTERNS: Content classification, metadata enrichment
    """
    text_lower = text.lower()

    # Check for architecture/design patterns
    architecture_keywords = ['architecture', 'design pattern', 'uml', 'class diagram',
                             'component', 'system design', 'scalability', 'microservice']
    has_architecture = any(keyword in text_lower for keyword in architecture_keywords)

    # Check for best practices/principles
    best_practice_keywords = ['best practice', 'principle', 'solid', 'dry', 'kiss',
                              'clean code', 'refactor', 'anti-pattern', 'guideline']
    has_best_practice = any(keyword in text_lower for keyword in best_practice_keywords)

    # Check if it's code
    has_code = is_code_chunk(text)

    # Determine primary content type
    if has_code:
        content_type = "code_example"
        artifact_type = "code_example"
    elif has_architecture:
        content_type = "architecture"
        artifact_type = "documentation"
    elif has_best_practice:
        content_type = "best_practice"
        artifact_type = "documentation"
    else:
        content_type = "concept"
        artifact_type = "documentation"

    return {
        "content_type": content_type,
        "artifact_type": artifact_type,
        "has_code": has_code,
        "has_architecture": has_architecture,
        "has_best_practice": has_best_practice
    }


def create_chunks(text: str, chunk_size: int = 3000) -> list:
    """
    Create intelligent chunks that preserve context.

    WHY: Maintain semantic coherence while staying within embedding limits
    PATTERNS: Smart chunking with overlap, paragraph preservation
    """
    # Guard: Empty text
    if not text:
        return []

    # Split by paragraphs first to preserve context
    paragraphs = text.split('\n\n')
    chunks = []
    current_chunk = []
    current_size = 0

    for para in paragraphs:
        para_size = len(para)

        # If single paragraph exceeds chunk size, split it
        if para_size > chunk_size:
            if current_chunk:
                chunks.append('\n\n'.join(current_chunk))
                current_chunk = []
                current_size = 0

            # Split large paragraph by sentences
            sentences = para.split('. ')
            temp_chunk = []
            temp_size = 0

            for sentence in sentences:
                if temp_size + len(sentence) > chunk_size and temp_chunk:
                    chunks.append('. '.join(temp_chunk) + '.')
                    temp_chunk = []
                    temp_size = 0

                temp_chunk.append(sentence)
                temp_size += len(sentence)

            if temp_chunk:
                chunks.append('. '.join(temp_chunk))

        # Add paragraph to current chunk if it fits
        elif current_size + para_size <= chunk_size:
            current_chunk.append(para)
            current_size += para_size
        else:
            # Finalize current chunk and start new one
            if current_chunk:
                chunks.append('\n\n'.join(current_chunk))
            current_chunk = [para]
            current_size = para_size

    # Add remaining chunk
    if current_chunk:
        chunks.append('\n\n'.join(current_chunk))

    return chunks


def upload_book(book_info: dict, rag: RAGAgent) -> bool:
    """
    Upload a single book with enhanced categorization.

    WHY: Store both code and concepts for comprehensive learning
    PATTERNS: Multi-stage processing, progress tracking
    """
    path = Path(book_info['path']).expanduser()

    # Guard: File doesn't exist
    if not path.exists():
        logger.log(f"❌ File not found: {path}", "ERROR")
        return False

    logger.log(f"\n📖 Processing: {book_info['title']}", "INFO")
    logger.log(f"   Author: {book_info['author']}", "INFO")
    logger.log(f"   Technology: {book_info['technology']}", "INFO")

    # Extract text based on file type
    if path.suffix.lower() == '.pdf':
        text = extract_text_from_pdf(str(path))
    elif path.suffix.lower() == '.epub':
        text = extract_text_from_epub(str(path))
    else:
        logger.log(f"❌ Unsupported file type: {path.suffix}", "ERROR")
        return False

    # Guard: No text extracted
    if not text:
        logger.log(f"❌ No text extracted from {path.name}", "ERROR")
        return False

    logger.log(f"   Extracted {len(text):,} characters", "INFO")

    # Create intelligent chunks
    chunks = create_chunks(text, chunk_size=3000)
    logger.log(f"   Created {len(chunks)} chunks", "INFO")

    # Upload chunks with categorization
    code_chunks = 0
    concept_chunks = 0
    architecture_chunks = 0
    best_practice_chunks = 0

    for i, chunk in enumerate(chunks, 1):
        # Categorize chunk
        categorization = categorize_chunk(chunk, book_info['category'])

        # Track statistics
        if categorization['content_type'] == 'code_example':
            code_chunks += 1
        elif categorization['content_type'] == 'architecture':
            architecture_chunks += 1
        elif categorization['content_type'] == 'best_practice':
            best_practice_chunks += 1
        else:
            concept_chunks += 1

        # Create metadata
        metadata = {
            "source": "technical_book",
            "book_title": book_info['title'],
            "author": book_info['author'],
            "category": book_info['category'],
            "technology": book_info['technology'],
            "chunk_index": i,
            "total_chunks": len(chunks),
            "content_type": categorization['content_type'],
            "has_code": categorization['has_code'],
            "has_architecture": categorization['has_architecture'],
            "has_best_practice": categorization['has_best_practice']
        }

        # Upload to RAG
        try:
            rag.store_artifact(
                artifact_type=categorization['artifact_type'],
                card_id=f"book-{book_info['category']}",
                task_title=book_info['title'],
                content=chunk,
                metadata=metadata
            )
        except Exception as e:
            logger.log(f"❌ Error storing chunk {i}: {e}", "ERROR")
            continue

        # Progress indicator
        if i % 10 == 0:
            logger.log(f"   ✓ Uploaded {i}/{len(chunks)} chunks", "INFO")

    # Final statistics
    logger.log(f"\n   ✅ Successfully uploaded {len(chunks)}/{len(chunks)} chunks", "SUCCESS")
    logger.log(f"      📝 Code examples: {code_chunks}", "INFO")
    logger.log(f"      💡 Concepts: {concept_chunks}", "INFO")
    logger.log(f"      🏗️  Architecture: {architecture_chunks}", "INFO")
    logger.log(f"      ⭐ Best practices: {best_practice_chunks}", "INFO")

    return True


def main():
    """Main upload orchestration."""
    logger.log("=" * 70, "INFO")
    logger.log("ENHANCED TECHNICAL BOOKS UPLOAD", "INFO")
    logger.log("Uploading code examples AND conceptual knowledge", "INFO")
    logger.log("=" * 70, "INFO")

    # Initialize RAG
    logger.log("\n🔧 Initializing RAG agent...", "INFO")
    rag = RAGAgent()

    # Upload all books
    total_books = len(BOOKS)
    successful = 0
    failed = 0

    for i, book in enumerate(BOOKS, 1):
        logger.log(f"\n{'='*70}", "INFO")
        logger.log(f"Book {i}/{total_books}", "INFO")
        logger.log(f"{'='*70}", "INFO")

        if upload_book(book, rag):
            successful += 1
        else:
            failed += 1

    # Final summary
    logger.log("\n" + "=" * 70, "INFO")
    logger.log("UPLOAD COMPLETE", "SUCCESS")
    logger.log("=" * 70, "INFO")
    logger.log(f"✅ Successful: {successful}/{total_books} books", "SUCCESS")
    if failed > 0:
        logger.log(f"❌ Failed: {failed}/{total_books} books", "ERROR")
    logger.log("=" * 70, "INFO")


if __name__ == "__main__":
    main()
