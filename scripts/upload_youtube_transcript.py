#!/usr/bin/env python3
"""
Upload YouTube Video Transcript to RAG
Downloads transcript/subtitles from YouTube and uploads to RAG database
"""

import sys
import hashlib
import subprocess
import json
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from rag_agent import RAGAgent
from artemis_logger import ArtemisLogger


def download_youtube_transcript(video_url: str, output_dir: Path) -> dict:
    """
    Download YouTube transcript using yt-dlp.

    Args:
        video_url: YouTube video URL
        output_dir: Directory to save transcript

    Returns:
        dict with video info and transcript path
    """
    output_dir.mkdir(exist_ok=True, parents=True)

    # First, get video info
    try:
        info_cmd = [
            'yt-dlp',
            '--dump-json',
            '--no-download',
            video_url
        ]
        result = subprocess.run(info_cmd, capture_output=True, text=True, check=True)
        video_info = json.loads(result.stdout)

        video_id = video_info.get('id', 'unknown')
        video_title = video_info.get('title', 'Unknown Title')
        channel = video_info.get('channel', 'Unknown Channel')
        duration = video_info.get('duration', 0)

        print(f"📺 Video: {video_title}")
        print(f"   Channel: {channel}")
        print(f"   Duration: {duration // 60}m {duration % 60}s")

    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to get video info: {e}")
        return None

    # Download transcript/subtitles
    transcript_path = output_dir / f"{video_id}.txt"

    try:
        # Try to download auto-generated or manual subtitles
        subtitle_cmd = [
            'yt-dlp',
            '--skip-download',
            '--write-auto-sub',
            '--write-sub',
            '--sub-lang', 'en',
            '--sub-format', 'vtt',
            '--convert-subs', 'srt',
            '-o', str(output_dir / video_id),
            video_url
        ]

        print("   Downloading transcript...")
        result = subprocess.run(subtitle_cmd, capture_output=True, text=True)

        # Look for subtitle files
        srt_files = list(output_dir.glob(f"{video_id}*.srt"))
        vtt_files = list(output_dir.glob(f"{video_id}*.vtt"))

        if srt_files:
            subtitle_file = srt_files[0]
            print(f"   ✅ Downloaded SRT subtitles")
        elif vtt_files:
            subtitle_file = vtt_files[0]
            print(f"   ✅ Downloaded VTT subtitles")
        else:
            print(f"   ⚠️  No subtitles available, trying description")
            # Fall back to description
            description = video_info.get('description', '')
            if description:
                with open(transcript_path, 'w', encoding='utf-8') as f:
                    f.write(f"# {video_title}\n\n")
                    f.write(f"**Channel**: {channel}\n\n")
                    f.write(f"**Description**:\n\n{description}\n")
                return {
                    'video_id': video_id,
                    'title': video_title,
                    'channel': channel,
                    'duration': duration,
                    'transcript_path': transcript_path,
                    'source_type': 'description'
                }

        # Parse subtitles and extract text
        with open(subtitle_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Extract text from SRT/VTT (remove timestamps)
        lines = content.split('\n')
        text_lines = []
        for line in lines:
            line = line.strip()
            # Skip sequence numbers, timestamps, and empty lines
            if line and not line.isdigit() and '-->' not in line and not line.startswith('WEBVTT'):
                text_lines.append(line)

        # Save clean transcript
        with open(transcript_path, 'w', encoding='utf-8') as f:
            f.write(f"# {video_title}\n\n")
            f.write(f"**Channel**: {channel}\n")
            f.write(f"**URL**: {video_url}\n")
            f.write(f"**Duration**: {duration // 60}m {duration % 60}s\n\n")
            f.write("**Transcript**:\n\n")
            f.write('\n'.join(text_lines))

        return {
            'video_id': video_id,
            'title': video_title,
            'channel': channel,
            'duration': duration,
            'url': video_url,
            'transcript_path': transcript_path,
            'source_type': 'subtitles'
        }

    except Exception as e:
        print(f"❌ Error downloading transcript: {e}")
        return None


def main():
    """Upload YouTube transcript to RAG"""

    import argparse
    parser = argparse.ArgumentParser(description='Upload YouTube video transcript to RAG')
    parser.add_argument('url', help='YouTube video URL')
    parser.add_argument('--output-dir', default='/tmp/youtube_transcripts', help='Output directory for transcripts')

    args = parser.parse_args()

    print("\n" + "="*70)
    print("YOUTUBE TRANSCRIPT → RAG")
    print("="*70)

    # Initialize
    logger = ArtemisLogger()
    rag = RAGAgent(db_path='../.artemis_data/rag_db', verbose=True)

    # Download transcript
    output_dir = Path(args.output_dir)
    video_info = download_youtube_transcript(args.url, output_dir)

    if not video_info:
        print("❌ Failed to download transcript")
        return 1

    # Read transcript
    with open(video_info['transcript_path'], 'r', encoding='utf-8') as f:
        transcript = f.read()

    # Upload to RAG
    print(f"\n📤 Uploading to RAG...")
    try:
        artifact_id = rag.store_artifact(
            artifact_type="code_example",  # Using code_example type for tutorials
            card_id=f"youtube-{video_info['video_id']}",
            task_title=f"YouTube: {video_info['title']}",
            content=transcript,
            metadata={
                'source': 'youtube',
                'video_id': video_info['video_id'],
                'channel': video_info['channel'],
                'duration': video_info['duration'],
                'url': video_info.get('url', args.url),
                'transcript_type': video_info['source_type'],
                'uploaded_at': datetime.now().isoformat()
            }
        )

        print(f"✅ Uploaded transcript to RAG")
        print(f"   Artifact ID: {artifact_id}")

        # Show stats
        print("\n📊 RAG Database Stats:")
        stats = rag.get_stats()
        print(f"   Total artifacts: {stats['total_artifacts']}")
        print(f"   Code examples: {stats['by_type'].get('code_example', 0)}")

        print("="*70)
        return 0

    except Exception as e:
        print(f"❌ Error uploading to RAG: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
