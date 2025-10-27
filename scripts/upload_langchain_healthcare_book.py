#!/usr/bin/env python3
"""
Upload LangChain for Life Sciences and Healthcare Book to RAG
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from upload_pdf_to_rag import PDFToRAGUploader


def main():
    """Upload LangChain Healthcare book"""

    print("\n" + "="*70)
    print("LANGCHAIN FOR LIFE SCIENCES AND HEALTHCARE → RAG")
    print("="*70)

    uploader = PDFToRAGUploader()

    book_path = Path("/home/bbrelin/Downloads/Reznikov I. LangChain for Life Sciences and Healthcare. Innovation...2025/Reznikov I. LangChain for Life Sciences and Healthcare. Innovation...2025.pdf")

    if not book_path.exists():
        print(f"❌ Book not found: {book_path}")
        return 1

    print(f"\n📚 Uploading: LangChain for Life Sciences and Healthcare")
    print(f"   Author: I. Reznikov")
    print(f"   Path: {book_path}")

    try:
        # Upload the book
        chunks_uploaded = uploader.upload_pdf_to_rag(
            pdf_path=book_path,
            book_title="LangChain for Life Sciences and Healthcare: Innovation in AI Applications",
            author="I. Reznikov",
            chunk_size=5  # 5 pages per chunk
        )

        if chunks_uploaded > 0:
            print(f"\n✅ Successfully uploaded {chunks_uploaded} chunks")

            # Show RAG stats
            print("\n📊 RAG Database Stats:")
            stats = uploader.rag.get_stats()
            print(f"   Total artifacts: {stats['total_artifacts']}")
            print(f"   Code examples: {stats['by_type'].get('code_example', 0)}")
            print("="*70)

            return 0
        else:
            print("\n❌ Upload failed")
            return 1

    except Exception as e:
        print(f"\n❌ Error uploading: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
