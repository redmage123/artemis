#!/usr/bin/env python3
"""
Batch Upload Head First and SQL Books to RAG

Finds and uploads all matching PDFs and EPUBs from ~/Downloads
"""

import re
from pathlib import Path
from upload_pdf_to_rag import PDFToRAGUploader
from upload_epub_to_rag import EPUBToRAGUploader

DOWNLOADS_DIR = Path('/home/bbrelin/Downloads')
SEARCH_KEYWORDS = ['head', 'sql']


def extract_book_metadata(filename: str):
    """Extract book title and author from Z-Library filename format"""
    # Z-Library format: "Title (Author Name) (Z-Library).ext"
    match = re.match(r'^(.+?)\s*\((.+?)\)\s*\(Z-Library\)', filename)

    if match:
        title = match.group(1).strip()
        author = match.group(2).strip()
        return title, author

    # Fallback: use filename without extension
    title = Path(filename).stem
    return title, "Unknown"


def find_matching_files():
    """Find all PDFs and EPUBs matching keywords"""
    all_files = []

    # Find PDFs
    for pdf in DOWNLOADS_DIR.glob('*.pdf'):
        if any(keyword in pdf.name.lower() for keyword in SEARCH_KEYWORDS):
            all_files.append(pdf)

    # Find EPUBs
    for epub in DOWNLOADS_DIR.glob('*.epub'):
        if any(keyword in epub.name.lower() for keyword in SEARCH_KEYWORDS):
            all_files.append(epub)

    # Remove duplicates (same name with .epub and .pdf)
    unique_files = {}
    for file_path in all_files:
        # Use stem (filename without extension) as key to detect duplicates
        base_name = file_path.stem
        if base_name not in unique_files:
            unique_files[base_name] = file_path
        else:
            # Prefer EPUB over PDF for duplicates
            if file_path.suffix == '.epub':
                unique_files[base_name] = file_path

    return list(unique_files.values())


def main():
    """Main execution"""
    print("\n" + "="*70)
    print("HEAD FIRST / SQL BOOKS → RAG DATABASE")
    print("="*70)

    # Find all matching files
    print(f"\n🔍 Searching {DOWNLOADS_DIR} for matching books...")
    matching_files = find_matching_files()

    if not matching_files:
        print("   ❌ No matching files found")
        return

    print(f"\n📚 Found {len(matching_files)} books to upload:")
    for file_path in matching_files:
        title, author = extract_book_metadata(file_path.name)
        size_mb = file_path.stat().st_size / (1024*1024)
        print(f"   - {title}")
        print(f"     Author: {author}")
        print(f"     Type: {file_path.suffix.upper()}, Size: {size_mb:.1f} MB")

    # Initialize uploaders
    pdf_uploader = PDFToRAGUploader()
    epub_uploader = EPUBToRAGUploader()

    # Upload each file
    total_chunks = 0
    total_errors = 0

    for file_path in matching_files:
        title, author = extract_book_metadata(file_path.name)

        if file_path.suffix == '.pdf':
            chunks = pdf_uploader.upload_pdf_to_rag(
                pdf_path=file_path,
                book_title=title,
                author=author,
                chunk_size=5  # 5 pages per chunk
            )
            total_chunks += chunks
            total_errors += pdf_uploader.error_count

        elif file_path.suffix == '.epub':
            chunks = epub_uploader.upload_epub_to_rag(
                epub_path=file_path,
                book_title=title,
                author=author,
                chunk_size=3  # 3 chapters per chunk
            )
            total_chunks += chunks
            total_errors += epub_uploader.error_count

    # Final summary
    print("\n" + "="*70)
    print("FINAL UPLOAD SUMMARY")
    print("="*70)
    print(f"📚 Books processed: {len(matching_files)}")
    print(f"✅ Total chunks uploaded: {total_chunks}")
    print(f"❌ Total errors: {total_errors}")

    # Show RAG stats
    from rag_agent import RAGAgent
    rag = RAGAgent(db_path='../.artemis_data/rag_db', verbose=False)
    stats = rag.get_stats()

    print("\n📊 RAG Database Stats:")
    print(f"   Total artifacts: {stats['total_artifacts']}")
    print(f"   Code examples: {stats['by_type'].get('code_example', 0)}")
    print("="*70)


if __name__ == "__main__":
    main()
