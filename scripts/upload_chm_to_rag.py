#!/usr/bin/env python3
"""
Upload CHM (Compiled HTML Help) Books to RAG Database

Extracts HTML content from CHM files and uploads them to RAG in manageable chunks.
"""

import hashlib
import subprocess
import tempfile
import shutil
from pathlib import Path
from typing import List, Dict
from rag_agent import RAGAgent
from bs4 import BeautifulSoup


class CHMToRAGUploader:
    """Upload CHM content to RAG database"""

    def __init__(self, rag_db_path: str = '../.artemis_data/rag_db'):
        self.rag = RAGAgent(db_path=rag_db_path, verbose=True)
        self.uploaded_count = 0
        self.error_count = 0

    def extract_chm(self, chm_path: Path, extract_dir: Path) -> bool:
        """Extract CHM file using 7z"""
        try:
            print(f"   🔓 Extracting CHM file...")
            result = subprocess.run(
                ['7z', 'x', str(chm_path), f'-o{extract_dir}', '-y'],
                capture_output=True,
                text=True,
                timeout=120
            )

            if result.returncode == 0:
                print(f"   ✅ CHM file extracted successfully")
                return True
            else:
                print(f"   ❌ Failed to extract CHM: {result.stderr}")
                return False

        except Exception as e:
            print(f"   ❌ Error extracting CHM: {e}")
            return False

    def extract_text_from_html(self, html_content: str) -> str:
        """Extract text from HTML using BeautifulSoup"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')

            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()

            text = soup.get_text(separator='\n', strip=True)
            return text
        except Exception:
            return ""

    def find_html_files(self, extract_dir: Path) -> List[Path]:
        """Find all HTML files in extracted directory"""
        html_files = []

        for ext in ['.html', '.htm']:
            html_files.extend(extract_dir.rglob(f'*{ext}'))

        return sorted(html_files)

    def process_html_files(self, html_files: List[Path]) -> List[Dict[str, str]]:
        """Process HTML files and extract text"""
        chapters = []

        print(f"   📄 Found {len(html_files)} HTML files")

        for idx, html_file in enumerate(html_files, 1):
            try:
                content = html_file.read_text(encoding='utf-8', errors='ignore')
                text = self.extract_text_from_html(content)

                if text and len(text.strip()) > 100:
                    chapters.append({
                        'chapter_num': idx,
                        'text': text,
                        'char_count': len(text),
                        'file_name': html_file.name
                    })

                    if idx % 20 == 0:
                        print(f"   ✓ Processed {idx}/{len(html_files)} files")

            except Exception as e:
                print(f"   ⚠️  Error processing {html_file.name}: {e}")
                continue

        print(f"   ✅ Extracted {len(chapters)} chapters with text")
        return chapters

    def chunk_chapters(self, chapters: List[Dict[str, str]], chunk_size: int = 5) -> List[Dict[str, any]]:
        """Chunk chapters into manageable sections for RAG"""
        chunks = []

        for i in range(0, len(chapters), chunk_size):
            chunk_chapters = chapters[i:i + chunk_size]

            # Combine text from chunk
            combined_text = "\n\n---\n\n".join([
                f"[Section {c['chapter_num']}]\n{c['text']}"
                for c in chunk_chapters
            ])

            chunks.append({
                'start_section': chunk_chapters[0]['chapter_num'],
                'end_section': chunk_chapters[-1]['chapter_num'],
                'text': combined_text,
                'section_count': len(chunk_chapters),
                'char_count': len(combined_text)
            })

        return chunks

    def upload_chm_to_rag(
        self,
        chm_path: Path,
        book_title: str,
        author: str = "Unknown",
        chunk_size: int = 5
    ) -> int:
        """
        Upload CHM to RAG in chunks

        Args:
            chm_path: Path to CHM file
            book_title: Title of the book
            author: Author name
            chunk_size: Number of sections per chunk

        Returns:
            Number of chunks uploaded
        """
        print(f"\n{'='*70}")
        print(f"📚 Uploading: {book_title}")
        print(f"{'='*70}")

        if not chm_path.exists():
            print(f"   ❌ File not found: {chm_path}")
            return 0

        print(f"   📁 File: {chm_path.name}")
        print(f"   📏 Size: {chm_path.stat().st_size / (1024*1024):.2f} MB")

        # Create temporary directory for extraction
        with tempfile.TemporaryDirectory() as temp_dir:
            extract_dir = Path(temp_dir) / 'chm_extracted'
            extract_dir.mkdir()

            # Extract CHM
            if not self.extract_chm(chm_path, extract_dir):
                return 0

            # Find HTML files
            print(f"\n   🔍 Searching for HTML content...")
            html_files = self.find_html_files(extract_dir)

            if not html_files:
                print(f"   ❌ No HTML files found in CHM")
                return 0

            # Process HTML files
            chapters = self.process_html_files(html_files)

            if not chapters:
                print(f"   ❌ No text extracted from HTML files")
                return 0

            # Chunk sections
            print(f"\n   📦 Creating chunks (chunk size: {chunk_size} sections)...")
            chunks = self.chunk_chapters(chapters, chunk_size)
            print(f"   ✅ Created {len(chunks)} chunks")

            # Upload chunks
            print(f"\n   ☁️  Uploading to RAG...")
            uploaded = 0

            for i, chunk in enumerate(chunks):
                try:
                    # Create unique ID
                    chunk_id = hashlib.md5(
                        f"{book_title}-{chunk['start_section']}-{chunk['end_section']}".encode()
                    ).hexdigest()[:8]

                    card_id = f"chm-{chunk_id}"

                    # Metadata
                    metadata = {
                        'source': 'chm_book',
                        'book_title': book_title,
                        'author': author,
                        'file_name': chm_path.name,
                        'start_section': chunk['start_section'],
                        'end_section': chunk['end_section'],
                        'section_count': chunk['section_count'],
                        'char_count': chunk['char_count'],
                        'features': ['sql', 'database', 'cookbook', 'reference', 'book']
                    }

                    # Upload to RAG
                    artifact_id = self.rag.store_artifact(
                        artifact_type="code_example",
                        card_id=card_id,
                        task_title=f"{book_title} (Sections {chunk['start_section']}-{chunk['end_section']})",
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
    print("CHM BOOKS → RAG DATABASE")
    print("="*70)

    uploader = CHMToRAGUploader()

    # Upload SQL Cookbook
    chm_path = Path("/home/bbrelin/Downloads/SQL Cookbook (Anthony Molinaro) (Z-Library).chm")

    chunks_uploaded = uploader.upload_chm_to_rag(
        chm_path=chm_path,
        book_title="SQL Cookbook",
        author="Anthony Molinaro",
        chunk_size=5  # 5 sections per chunk
    )

    # Summary
    print("\n" + "="*70)
    print("UPLOAD SUMMARY")
    print("="*70)
    print(f"✅ Total chunks uploaded: {uploader.uploaded_count}")
    print(f"❌ Errors: {uploader.error_count}")
    print()

    # Verify RAG stats
    stats = uploader.rag.get_stats()
    print("📊 RAG Database Stats:")
    print(f"   Total artifacts: {stats['total_artifacts']}")
    print(f"   Code examples: {stats['by_type'].get('code_example', 0)}")
    print("="*70)


if __name__ == "__main__":
    main()
