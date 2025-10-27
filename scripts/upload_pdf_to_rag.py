#!/usr/bin/env python3
"""
Upload PDF Book to RAG Database

Extracts text from PDF and uploads it to RAG in manageable chunks.
"""

import hashlib
from pathlib import Path
from typing import List, Dict
from rag_agent import RAGAgent

try:
    import PyPDF2
    HAS_PYPDF2 = True
except ImportError:
    HAS_PYPDF2 = False

try:
    import pdfplumber
    HAS_PDFPLUMBER = True
except ImportError:
    HAS_PDFPLUMBER = False


class PDFToRAGUploader:
    """Upload PDF content to RAG database"""

    def __init__(self, rag_db_path: str = '../.artemis_data/rag_db'):
        self.rag = RAGAgent(db_path=rag_db_path, verbose=True)
        self.uploaded_count = 0
        self.error_count = 0

    def extract_text_pypdf2(self, pdf_path: Path) -> List[Dict[str, str]]:
        """Extract text from PDF using PyPDF2"""
        pages = []

        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            total_pages = len(pdf_reader.pages)

            print(f"   📄 Total pages: {total_pages}")

            for page_num in range(total_pages):
                try:
                    page = pdf_reader.pages[page_num]
                    text = page.extract_text()

                    if text and len(text.strip()) > 50:
                        pages.append({
                            'page_num': page_num + 1,
                            'text': text,
                            'char_count': len(text)
                        })

                        if (page_num + 1) % 10 == 0:
                            print(f"   ✓ Processed {page_num + 1}/{total_pages} pages")

                except Exception as e:
                    print(f"   ⚠️  Error extracting page {page_num + 1}: {e}")
                    continue

        return pages

    def extract_text_pdfplumber(self, pdf_path: Path) -> List[Dict[str, str]]:
        """Extract text from PDF using pdfplumber (better quality)"""
        pages = []

        with pdfplumber.open(pdf_path) as pdf:
            total_pages = len(pdf.pages)
            print(f"   📄 Total pages: {total_pages}")

            for page_num, page in enumerate(pdf.pages):
                try:
                    text = page.extract_text()

                    if text and len(text.strip()) > 50:
                        pages.append({
                            'page_num': page_num + 1,
                            'text': text,
                            'char_count': len(text)
                        })

                        if (page_num + 1) % 10 == 0:
                            print(f"   ✓ Processed {page_num + 1}/{total_pages} pages")

                except Exception as e:
                    print(f"   ⚠️  Error extracting page {page_num + 1}: {e}")
                    continue

        return pages

    def chunk_pages(self, pages: List[Dict[str, str]], chunk_size: int = 5) -> List[Dict[str, any]]:
        """Chunk pages into manageable sections for RAG"""
        chunks = []

        for i in range(0, len(pages), chunk_size):
            chunk_pages = pages[i:i + chunk_size]

            # Combine text from chunk
            combined_text = "\n\n---\n\n".join([
                f"[Page {p['page_num']}]\n{p['text']}"
                for p in chunk_pages
            ])

            chunks.append({
                'start_page': chunk_pages[0]['page_num'],
                'end_page': chunk_pages[-1]['page_num'],
                'text': combined_text,
                'page_count': len(chunk_pages),
                'char_count': len(combined_text)
            })

        return chunks

    def upload_pdf_to_rag(
        self,
        pdf_path: Path,
        book_title: str,
        author: str = "Unknown",
        chunk_size: int = 5
    ) -> int:
        """
        Upload PDF to RAG in chunks

        Args:
            pdf_path: Path to PDF file
            book_title: Title of the book
            author: Author name
            chunk_size: Number of pages per chunk

        Returns:
            Number of chunks uploaded
        """
        print(f"\n{'='*70}")
        print(f"📚 Uploading: {book_title}")
        print(f"{'='*70}")

        if not pdf_path.exists():
            print(f"   ❌ File not found: {pdf_path}")
            return 0

        print(f"   📁 File: {pdf_path.name}")
        print(f"   📏 Size: {pdf_path.stat().st_size / (1024*1024):.2f} MB")

        # Extract text
        print(f"\n   🔍 Extracting text from PDF...")

        if HAS_PDFPLUMBER:
            print(f"   📖 Using pdfplumber (high quality)")
            pages = self.extract_text_pdfplumber(pdf_path)
        elif HAS_PYPDF2:
            print(f"   📖 Using PyPDF2 (fallback)")
            pages = self.extract_text_pypdf2(pdf_path)
        else:
            print(f"   ❌ No PDF library available!")
            print(f"   Install: pip install pdfplumber or pip install PyPDF2")
            return 0

        if not pages:
            print(f"   ❌ No text extracted from PDF")
            return 0

        print(f"   ✅ Extracted {len(pages)} pages with text")

        # Chunk pages
        print(f"\n   📦 Creating chunks (chunk size: {chunk_size} pages)...")
        chunks = self.chunk_pages(pages, chunk_size)
        print(f"   ✅ Created {len(chunks)} chunks")

        # Upload chunks
        print(f"\n   ☁️  Uploading to RAG...")
        uploaded = 0

        for i, chunk in enumerate(chunks):
            try:
                # Create unique ID
                chunk_id = hashlib.md5(
                    f"{book_title}-{chunk['start_page']}-{chunk['end_page']}".encode()
                ).hexdigest()[:8]

                card_id = f"book-{chunk_id}"

                # Metadata
                metadata = {
                    'source': 'pdf_book',
                    'book_title': book_title,
                    'author': author,
                    'file_name': pdf_path.name,
                    'start_page': chunk['start_page'],
                    'end_page': chunk['end_page'],
                    'page_count': chunk['page_count'],
                    'char_count': chunk['char_count'],
                    'features': ['python', 'gpt', 'cookbook', 'reference', 'book']
                }

                # Upload to RAG
                artifact_id = self.rag.store_artifact(
                    artifact_type="code_example",
                    card_id=card_id,
                    task_title=f"{book_title} (Pages {chunk['start_page']}-{chunk['end_page']})",
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
    print("PDF BOOK → RAG DATABASE")
    print("="*70)

    # Check PDF library availability
    print("\n📚 PDF Library Check:")
    if HAS_PDFPLUMBER:
        print("   ✅ pdfplumber available (recommended)")
    elif HAS_PYPDF2:
        print("   ✅ PyPDF2 available")
        print("   ⚠️  Consider installing pdfplumber for better quality:")
        print("      pip install pdfplumber")
    else:
        print("   ❌ No PDF library found!")
        print("   Install: pip install pdfplumber")
        return

    uploader = PDFToRAGUploader()

    # Upload Python GPT Cookbook
    pdf_path = Path("/home/bbrelin/Downloads/Python GPT Cookbook (Dr. Neil Williams) (Z-Library).pdf")

    chunks_uploaded = uploader.upload_pdf_to_rag(
        pdf_path=pdf_path,
        book_title="Python GPT Cookbook",
        author="Dr. Neil Williams",
        chunk_size=5  # 5 pages per chunk
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
