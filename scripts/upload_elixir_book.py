#!/usr/bin/env python3
"""
Upload Ruby to Elixir Book to RAG Database
"""

import sys
from pathlib import Path

# Add src to path to import modules
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from upload_pdf_to_rag import PDFToRAGUploader


def main():
    """Upload Ruby to Elixir programming book"""

    print("\n" + "="*70)
    print("RUBY TO ELIXIR BOOK → RAG DATABASE")
    print("="*70)

    uploader = PDFToRAGUploader()

    # Ruby to Elixir book details
    elixir_book = {
        'path': Path("/home/bbrelin/Downloads/Bussey S. From Ruby to Elixir.Unleash the Full Potential of Functional Prog.2024/Bussey S. From Ruby to Elixir.Unleash the Full Potential of Functional Prog.2024.pdf"),
        'title': "From Ruby to Elixir: Unleash the Full Potential of Functional Programming",
        'author': "Bussey S.",
        'type': 'pdf',
        'chunk_size': 5  # 5 pages per chunk
    }

    print(f"\n{'='*70}")
    print(f"📚 Uploading Ruby to Elixir Book")
    print(f"{'='*70}")

    if not elixir_book['path'].exists():
        print(f"   ❌ File not found: {elixir_book['path']}")
        return 1

    try:
        # Upload the book
        chunks_uploaded = uploader.upload_pdf_to_rag(
            pdf_path=elixir_book['path'],
            book_title=elixir_book['title'],
            author=elixir_book['author'],
            chunk_size=elixir_book['chunk_size']
        )

        if chunks_uploaded > 0:
            print(f"\n   ✅ Successfully uploaded Ruby to Elixir book: {chunks_uploaded} chunks")
        else:
            print(f"\n   ❌ Failed to upload Ruby to Elixir book")
            return 1

    except Exception as e:
        print(f"\n   ❌ Error uploading Ruby to Elixir book: {e}")
        return 1

    # Final Summary
    print("\n" + "="*70)
    print("UPLOAD SUMMARY")
    print("="*70)
    print(f"📚 From Ruby to Elixir")
    print(f"✅ Successfully uploaded: {chunks_uploaded} chunks")
    print(f"📊 Total uploaded: {uploader.uploaded_count} chunks")
    print(f"❌ Total errors: {uploader.error_count}")
    print("="*70)

    # Verify RAG stats
    print("\n📊 RAG Database Stats:")
    stats = uploader.rag.get_stats()
    print(f"   Total artifacts: {stats['total_artifacts']}")
    print(f"   Code examples: {stats['by_type'].get('code_example', 0)}")
    print("="*70)

    return 0


if __name__ == "__main__":
    exit(main())
