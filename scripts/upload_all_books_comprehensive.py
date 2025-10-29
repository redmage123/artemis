#!/usr/bin/env python3
"""
WHY: Comprehensive upload of ALL books/courses with code + concept extraction
RESPONSIBILITY: Auto-discover, categorize, and upload all educational content
PATTERNS: Auto-discovery, metadata extraction, progress tracking, resume capability

This script:
1. Finds ALL PDFs/EPUBs in Downloads and repo
2. Extracts metadata from filenames
3. Auto-categorizes by technology keywords
4. Uploads code examples AND conceptual knowledge
5. Tracks progress with resume capability
6. Handles errors gracefully
"""

import sys
import re
import json
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

import pdfplumber
import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup
from artemis_logger import get_logger
from rag_agent import RAGAgent

logger = get_logger('comprehensive_upload')

# Progress tracking file
PROGRESS_FILE = Path("/tmp/artemis_book_upload_progress.json")

# Technology keywords for categorization
TECH_CATEGORIES = {
    'python': ['python', 'django', 'flask', 'pandas', 'numpy', 'pytorch', 'tensorflow'],
    'javascript': ['javascript', 'js', 'node', 'react', 'vue', 'angular', 'typescript'],
    'java': ['java', 'spring', 'hibernate', 'maven', 'gradle'],
    'csharp': ['c#', 'csharp', '.net', 'dotnet', 'asp.net', 'f#'],
    'cpp': ['c++', 'cpp'],
    'rust': ['rust', 'cargo'],
    'go': ['golang', 'go programming'],
    'ruby': ['ruby', 'rails'],
    'php': ['php', 'laravel', 'symfony'],
    'unreal_engine': ['unreal', 'ue4', 'ue5'],
    'unity': ['unity', 'unity3d'],
    'blender': ['blender', '3d modeling'],
    'terraform': ['terraform', 'infrastructure as code'],
    'docker': ['docker', 'container'],
    'kubernetes': ['kubernetes', 'k8s'],
    'aws': ['aws', 'amazon web services'],
    'azure': ['azure', 'microsoft cloud'],
    'gcp': ['google cloud', 'gcp'],
    'database': ['sql', 'postgresql', 'mysql', 'mongodb', 'redis'],
    'machine_learning': ['machine learning', 'ml', 'deep learning', 'ai', 'artificial intelligence'],
    'web_dev': ['web development', 'html', 'css', 'frontend', 'backend'],
    'mobile': ['android', 'ios', 'swift', 'kotlin', 'react native'],
    'devops': ['devops', 'ci/cd', 'jenkins', 'gitlab'],
    'security': ['security', 'cybersecurity', 'penetration testing', 'ethical hacking'],
    'data_science': ['data science', 'data analysis', 'statistics'],
    'algorithms': ['algorithm', 'data structure', 'competitive programming'],
    'design': ['design pattern', 'architecture', 'uml', 'solid'],
}

# Fiction detection - books to skip
FICTION_AUTHORS = [
    'david guymer', 'aaron dembski-bowden', 'dan abnett', 'graham mcneill',
    'j.k. rowling', 'george r.r. martin', 'stephen king', 'brandon sanderson',
    'patrick rothfuss', 'neil gaiman', 'terry pratchett', 'isaac asimov'
]

FICTION_KEYWORDS = [
    'warhammer 40k', 'warhammer 40,000', 'black library',
    'novel', 'a novel', 'fiction', 'fantasy novel', 'sci-fi novel',
    'thriller', 'mystery novel', 'romance novel'
]

FICTION_SERIES = [
    'horus heresy', 'warhammer', 'primarchs', 'space marine',
    'harry potter', 'lord of the rings', 'game of thrones'
]


def load_progress() -> Dict:
    """Load progress from previous run."""
    if PROGRESS_FILE.exists():
        with open(PROGRESS_FILE, 'r') as f:
            return json.load(f)
    return {"completed": [], "failed": [], "last_updated": None}


def save_progress(progress: Dict):
    """Save progress for resume capability."""
    progress["last_updated"] = datetime.now().isoformat()
    with open(PROGRESS_FILE, 'w') as f:
        json.dump(progress, f, indent=2)


def find_all_books(search_paths: List[str]) -> List[Path]:
    """
    Find all PDF and EPUB files recursively.

    WHY: Auto-discover all educational content
    PATTERNS: Recursive search, deduplication
    """
    all_books = []
    seen_names = set()

    for search_path in search_paths:
        path = Path(search_path).expanduser()
        if not path.exists():
            logger.log(f"⚠️  Path not found: {path}", "WARNING")
            continue

        logger.log(f"🔍 Scanning: {path}", "INFO")

        # Find all PDFs and EPUBs
        for pattern in ['**/*.pdf', '**/*.epub']:
            for book_path in path.glob(pattern):
                # Skip if already seen (deduplication)
                if book_path.name in seen_names:
                    continue

                seen_names.add(book_path.name)
                all_books.append(book_path)

    return sorted(all_books)


def extract_metadata_from_filename(file_path: Path) -> Dict:
    """
    Extract book metadata from filename.

    WHY: Auto-extract title and author from standardized filenames
    PATTERNS: Regex parsing, fallback handling
    """
    filename = file_path.stem

    # Common patterns:
    # "Title (Author) (Publisher).pdf"
    # "Author - Title.pdf"
    # "Title by Author.pdf"

    # Try pattern: Title (Author)
    match = re.match(r'(.+?)\s*\((.+?)\)', filename)
    if match:
        title = match.group(1).strip()
        author = match.group(2).strip()
        # Remove publisher/year info
        author = re.sub(r'\s*\(Z-Library\).*$', '', author)
        return {"title": title, "author": author}

    # Try pattern: Author - Title
    match = re.match(r'(.+?)\s*-\s*(.+)', filename)
    if match:
        author = match.group(1).strip()
        title = match.group(2).strip()
        return {"title": title, "author": author}

    # Fallback: use filename as title
    return {"title": filename, "author": "Unknown"}


def is_fiction_book(title: str, author: str, file_path: Path) -> bool:
    """
    Determine if book is fiction (should be skipped).

    WHY: Filter out fiction books from technical content
    PATTERNS: Multi-criteria detection with author, title, series matching
    """
    text = f"{title} {author}".lower()
    filename = file_path.name.lower()

    # Check for known fiction authors
    if any(fiction_author in text for fiction_author in FICTION_AUTHORS):
        return True

    # Check for fiction keywords in title
    if any(keyword in text for keyword in FICTION_KEYWORDS):
        return True

    # Check for known fiction series
    if any(series in text or series in filename for series in FICTION_SERIES):
        return True

    return False


def categorize_by_technology(title: str, author: str) -> str:
    """
    Auto-categorize book by technology keywords.

    WHY: Enable targeted retrieval by technology
    PATTERNS: Keyword matching, priority ordering
    """
    text = f"{title} {author}".lower()

    # Check each category
    for category, keywords in TECH_CATEGORIES.items():
        if any(keyword.lower() in text for keyword in keywords):
            return category

    # Default to general if no match
    return "general"


def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract all text from PDF."""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            text_parts = []
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    text_parts.append(text)
            return "\n\n".join(text_parts)
    except Exception as e:
        logger.log(f"❌ Error extracting PDF: {e}", "ERROR")
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
        logger.log(f"❌ Error extracting EPUB: {e}", "ERROR")
        return ""


def is_code_chunk(text: str) -> bool:
    """Determine if chunk is primarily code."""
    if len(text.strip()) < 20:
        return False

    code_indicators = [
        r'^\s*(class|def|function|const|let|var|public|private)',
        r'[{}();]',
        r'^\s*(if|for|while|switch|return|import|include)',
        r'//|/\*|#|<!--',
        r'=>|->|\|\||&&',
    ]

    code_score = sum(1 for p in code_indicators if re.search(p, text, re.MULTILINE))
    return code_score >= 3


def categorize_chunk(text: str) -> dict:
    """
    Categorize chunk as code, concept, architecture, or best practice.

    NOTE: All chunks use 'code_example' artifact_type as it's the only
    supported type in RAG for book content. The content_type metadata
    distinguishes between code, concepts, etc.
    """
    text_lower = text.lower()

    architecture_keywords = ['architecture', 'design pattern', 'uml', 'system design']
    best_practice_keywords = ['best practice', 'principle', 'solid', 'clean code']

    has_architecture = any(k in text_lower for k in architecture_keywords)
    has_best_practice = any(k in text_lower for k in best_practice_keywords)
    has_code = is_code_chunk(text)

    if has_code:
        content_type = "code_example"
    elif has_architecture:
        content_type = "architecture"
    elif has_best_practice:
        content_type = "best_practice"
    else:
        content_type = "concept"

    return {
        "content_type": content_type,
        "artifact_type": "code_example",  # Only supported type for book content
        "has_code": has_code,
        "has_architecture": has_architecture,
        "has_best_practice": has_best_practice
    }


def create_chunks(text: str, chunk_size: int = 3000) -> list:
    """Create intelligent chunks preserving context."""
    if not text:
        return []

    paragraphs = text.split('\n\n')
    chunks = []
    current_chunk = []
    current_size = 0

    for para in paragraphs:
        para_size = len(para)

        if para_size > chunk_size:
            if current_chunk:
                chunks.append('\n\n'.join(current_chunk))
                current_chunk = []
                current_size = 0

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

        elif current_size + para_size <= chunk_size:
            current_chunk.append(para)
            current_size += para_size
        else:
            if current_chunk:
                chunks.append('\n\n'.join(current_chunk))
            current_chunk = [para]
            current_size = para_size

    if current_chunk:
        chunks.append('\n\n'.join(current_chunk))

    return chunks


def upload_book(book_path: Path, rag: RAGAgent, progress: Dict) -> bool:
    """Upload single book with enhanced categorization."""

    # Check if already processed
    book_id = str(book_path)
    if book_id in progress["completed"]:
        logger.log(f"⏭️  Already uploaded: {book_path.name}", "INFO")
        return True

    logger.log(f"\n📖 Processing: {book_path.name}", "INFO")

    # Extract metadata
    metadata = extract_metadata_from_filename(book_path)

    # Check if fiction - skip if so
    if is_fiction_book(metadata['title'], metadata['author'], book_path):
        logger.log(f"⏭️  SKIPPING FICTION: {metadata['title']}", "WARNING")
        logger.log(f"   Author: {metadata['author']}", "INFO")
        progress["completed"].append(book_id)  # Mark as completed so we don't retry
        save_progress(progress)
        return True

    category = categorize_by_technology(metadata['title'], metadata['author'])

    logger.log(f"   Title: {metadata['title']}", "INFO")
    logger.log(f"   Author: {metadata['author']}", "INFO")
    logger.log(f"   Category: {category}", "INFO")

    # Extract text
    if book_path.suffix.lower() == '.pdf':
        text = extract_text_from_pdf(str(book_path))
    elif book_path.suffix.lower() == '.epub':
        text = extract_text_from_epub(str(book_path))
    else:
        logger.log(f"❌ Unsupported format: {book_path.suffix}", "ERROR")
        progress["failed"].append(book_id)
        return False

    if not text:
        logger.log(f"❌ No text extracted", "ERROR")
        progress["failed"].append(book_id)
        return False

    logger.log(f"   Extracted {len(text):,} characters", "INFO")

    # Create chunks
    chunks = create_chunks(text, chunk_size=3000)
    logger.log(f"   Created {len(chunks)} chunks", "INFO")

    # Upload with categorization
    stats = {"code": 0, "concept": 0, "architecture": 0, "best_practice": 0}

    for i, chunk in enumerate(chunks, 1):
        categorization = categorize_chunk(chunk)
        stats[categorization['content_type']] += 1

        chunk_metadata = {
            "source": "comprehensive_upload",
            "book_title": metadata['title'],
            "author": metadata['author'],
            "category": category,
            "file_path": str(book_path),
            "chunk_index": i,
            "total_chunks": len(chunks),
            "content_type": categorization['content_type'],
            "has_code": categorization['has_code'],
            "has_architecture": categorization['has_architecture'],
            "has_best_practice": categorization['has_best_practice']
        }

        try:
            rag.store_artifact(
                artifact_type=categorization['artifact_type'],
                card_id=f"book-{category}",
                task_title=metadata['title'],
                content=chunk,
                metadata=chunk_metadata
            )
        except Exception as e:
            logger.log(f"❌ Error storing chunk {i}: {e}", "ERROR")
            continue

        if i % 50 == 0:
            logger.log(f"   ✓ {i}/{len(chunks)} chunks", "INFO")

    # Log statistics
    logger.log(f"   ✅ Uploaded {len(chunks)} chunks:", "SUCCESS")
    logger.log(f"      📝 Code: {stats['code']}", "INFO")
    logger.log(f"      💡 Concepts: {stats['concept']}", "INFO")
    logger.log(f"      🏗️  Architecture: {stats['architecture']}", "INFO")
    logger.log(f"      ⭐ Best practices: {stats['best_practice']}", "INFO")

    # Mark as completed
    progress["completed"].append(book_id)
    save_progress(progress)

    return True


def main():
    """Main orchestration."""
    logger.log("=" * 70, "INFO")
    logger.log("COMPREHENSIVE BOOKS UPLOAD - ALL CONTENT", "INFO")
    logger.log("Uploading code examples AND conceptual knowledge", "INFO")
    logger.log("=" * 70, "INFO")

    # Load progress
    progress = load_progress()
    logger.log(f"\n📊 Progress: {len(progress['completed'])} completed, {len(progress['failed'])} failed", "INFO")

    # Define search paths
    search_paths = [
        "~/Downloads",
        "/home/bbrelin/src/repos/artemis"
    ]

    # Find all books
    logger.log("\n🔍 Finding all books...", "INFO")
    all_books = find_all_books(search_paths)
    logger.log(f"   Found {len(all_books)} total books", "INFO")

    # Filter out already completed
    remaining = [b for b in all_books if str(b) not in progress["completed"]]
    logger.log(f"   {len(remaining)} remaining to upload", "INFO")

    if not remaining:
        logger.log("\n✅ All books already uploaded!", "SUCCESS")
        return

    # Initialize RAG
    logger.log("\n🔧 Initializing RAG agent...", "INFO")
    rag = RAGAgent()

    # Upload all remaining books
    successful = 0
    failed = 0

    for i, book in enumerate(remaining, 1):
        logger.log(f"\n{'='*70}", "INFO")
        logger.log(f"Book {i}/{len(remaining)} ({len(progress['completed']) + i}/{len(all_books)} total)", "INFO")
        logger.log(f"{'='*70}", "INFO")

        try:
            if upload_book(book, rag, progress):
                successful += 1
            else:
                failed += 1
        except Exception as e:
            logger.log(f"❌ Fatal error: {e}", "ERROR")
            failed += 1
            progress["failed"].append(str(book))
            save_progress(progress)

    # Final summary
    logger.log("\n" + "=" * 70, "INFO")
    logger.log("UPLOAD COMPLETE", "SUCCESS")
    logger.log("=" * 70, "INFO")
    logger.log(f"✅ Successfully uploaded: {successful} books", "SUCCESS")
    logger.log(f"❌ Failed: {failed} books", "ERROR" if failed > 0 else "INFO")
    logger.log(f"📊 Total processed: {len(progress['completed'])} books", "INFO")
    logger.log("=" * 70, "INFO")


if __name__ == "__main__":
    main()
