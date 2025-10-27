#!/usr/bin/env python3
"""
Upload EPUB Books to RAG Database

Extracts text from EPUB files and uploads them to RAG in manageable chunks.
"""

import hashlib
import zipfile
from pathlib import Path
from typing import List, Dict
from rag_agent import RAGAgent
from bs4 import BeautifulSoup

try:
    import ebooklib
    from ebooklib import epub
    HAS_EBOOKLIB = True
except ImportError:
    HAS_EBOOKLIB = False


class EPUBToRAGUploader:
    """Upload EPUB content to RAG database"""

    def __init__(self, rag_db_path: str = '../.artemis_data/rag_db'):
        self.rag = RAGAgent(db_path=rag_db_path, verbose=True)
        self.uploaded_count = 0
        self.error_count = 0

    def extract_text_with_ebooklib(self, epub_path: Path) -> List[Dict[str, str]]:
        """Extract text from EPUB using ebooklib"""
        chapters = []

        try:
            book = epub.read_epub(str(epub_path))

            chapter_num = 0
            for item in book.get_items():
                if item.get_type() == ebooklib.ITEM_DOCUMENT:
                    chapter_num += 1

                    # Extract text from HTML
                    soup = BeautifulSoup(item.get_content(), 'html.parser')
                    text = soup.get_text(separator='\n', strip=True)

                    if text and len(text.strip()) > 100:
                        chapters.append({
                            'chapter_num': chapter_num,
                            'text': text,
                            'char_count': len(text),
                            'title': item.get_name()
                        })

                        if chapter_num % 10 == 0:
                            print(f"   ✓ Processed {chapter_num} chapters")

            print(f"   ✅ Extracted {len(chapters)} chapters with text")
            return chapters

        except Exception as e:
            print(f"   ❌ Error extracting EPUB: {e}")
            return []

    def extract_text_with_zipfile(self, epub_path: Path) -> List[Dict[str, str]]:
        """Extract text from EPUB using zipfile (fallback method)"""
        chapters = []

        try:
            with zipfile.ZipFile(epub_path, 'r') as zip_ref:
                # Find all HTML/XHTML files
                html_files = [f for f in zip_ref.namelist()
                             if f.endswith(('.html', '.xhtml', '.htm'))]

                print(f"   📄 Found {len(html_files)} HTML files")

                for idx, html_file in enumerate(html_files, 1):
                    try:
                        content = zip_ref.read(html_file)
                        soup = BeautifulSoup(content, 'html.parser')
                        text = soup.get_text(separator='\n', strip=True)

                        if text and len(text.strip()) > 100:
                            chapters.append({
                                'chapter_num': idx,
                                'text': text,
                                'char_count': len(text),
                                'title': html_file
                            })

                            if idx % 10 == 0:
                                print(f"   ✓ Processed {idx}/{len(html_files)} files")

                    except Exception as e:
                        print(f"   ⚠️  Error processing {html_file}: {e}")
                        continue

                print(f"   ✅ Extracted {len(chapters)} chapters with text")
                return chapters

        except Exception as e:
            print(f"   ❌ Error extracting EPUB: {e}")
            return []

    def chunk_chapters(self, chapters: List[Dict[str, str]], chunk_size: int = 3) -> List[Dict[str, any]]:
        """Chunk chapters into manageable sections for RAG"""
        chunks = []

        for i in range(0, len(chapters), chunk_size):
            chunk_chapters = chapters[i:i + chunk_size]

            # Combine text from chunk
            combined_text = "\n\n---\n\n".join([
                f"[Chapter {c['chapter_num']}]\n{c['text']}"
                for c in chunk_chapters
            ])

            chunks.append({
                'start_chapter': chunk_chapters[0]['chapter_num'],
                'end_chapter': chunk_chapters[-1]['chapter_num'],
                'text': combined_text,
                'chapter_count': len(chunk_chapters),
                'char_count': len(combined_text)
            })

        return chunks

    def upload_epub_to_rag(
        self,
        epub_path: Path,
        book_title: str,
        author: str = "Unknown",
        chunk_size: int = 3
    ) -> int:
        """
        Upload EPUB to RAG in chunks

        Args:
            epub_path: Path to EPUB file
            book_title: Title of the book
            author: Author name
            chunk_size: Number of chapters per chunk

        Returns:
            Number of chunks uploaded
        """
        print(f"\n{'='*70}")
        print(f"📚 Uploading: {book_title}")
        print(f"{'='*70}")

        if not epub_path.exists():
            print(f"   ❌ File not found: {epub_path}")
            return 0

        print(f"   📁 File: {epub_path.name}")
        print(f"   📏 Size: {epub_path.stat().st_size / (1024*1024):.2f} MB")

        # Extract text
        print(f"\n   🔍 Extracting text from EPUB...")

        if HAS_EBOOKLIB:
            print(f"   📖 Using ebooklib (high quality)")
            chapters = self.extract_text_with_ebooklib(epub_path)
        else:
            print(f"   📖 Using zipfile + BeautifulSoup (fallback)")
            chapters = self.extract_text_with_zipfile(epub_path)

        if not chapters:
            print(f"   ❌ No text extracted from EPUB")
            return 0

        # Chunk chapters
        print(f"\n   📦 Creating chunks (chunk size: {chunk_size} chapters)...")
        chunks = self.chunk_chapters(chapters, chunk_size)
        print(f"   ✅ Created {len(chunks)} chunks")

        # Upload chunks
        print(f"\n   ☁️  Uploading to RAG...")
        uploaded = 0

        for i, chunk in enumerate(chunks):
            try:
                # Create unique ID
                chunk_id = hashlib.md5(
                    f"{book_title}-{chunk['start_chapter']}-{chunk['end_chapter']}".encode()
                ).hexdigest()[:8]

                card_id = f"ebook-{chunk_id}"

                # Metadata
                metadata = {
                    'source': 'epub_book',
                    'book_title': book_title,
                    'author': author,
                    'file_name': epub_path.name,
                    'start_chapter': chunk['start_chapter'],
                    'end_chapter': chunk['end_chapter'],
                    'chapter_count': chunk['chapter_count'],
                    'char_count': chunk['char_count'],
                    'features': ['django', 'python', 'web', 'book', 'reference']
                }

                # Upload to RAG
                artifact_id = self.rag.store_artifact(
                    artifact_type="code_example",
                    card_id=card_id,
                    task_title=f"{book_title} (Chapters {chunk['start_chapter']}-{chunk['end_chapter']})",
                    content=chunk['text'],
                    metadata=metadata
                )

                if artifact_id:
                    uploaded += 1
                    if (i + 1) % 5 == 0:
                        print(f"   ✓ Uploaded {i + 1}/{len(chunks)} chunks")
                else:
                    self.error_count += 1

            except Exception as e:
                print(f"   ❌ Error uploading chunk {i + 1}: {e}")
                self.error_count += 1
                continue

        self.uploaded_count += uploaded
        print(f"\n   ✅ Successfully uploaded {uploaded}/{len(chunks)} chunks")

        return uploaded


def main():
    """Main execution"""
    print("\n" + "="*70)
    print("EPUB BOOKS → RAG DATABASE")
    print("="*70)

    # Check library availability
    print("\n📚 Library Check:")
    if HAS_EBOOKLIB:
        print("   ✅ ebooklib available (recommended)")
    else:
        print("   ⚠️  ebooklib not available, using fallback method")
        print("   Install for better quality: pip install ebooklib beautifulsoup4")

    uploader = EPUBToRAGUploader()

    # This will be called by the batch processor
    # Individual EPUB uploads will be handled there

    print("="*70)


if __name__ == "__main__":
    main()
