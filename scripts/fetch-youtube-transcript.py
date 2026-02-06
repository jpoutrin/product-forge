#!/usr/bin/env python3
"""
Fetch YouTube Transcript

Fetches transcripts from YouTube videos and saves them as readable text files.

Usage:
    python fetch-youtube-transcript.py <youtube_url> [--output DIR]

Examples:
    python fetch-youtube-transcript.py "https://www.youtube.com/watch?v=4_2j5wgt_ds&t=135s"
    python fetch-youtube-transcript.py "https://youtu.be/4_2j5wgt_ds" --output .work/transcripts
"""

import argparse
import re
import sys
from pathlib import Path
from typing import Optional

try:
    from youtube_transcript_api import YouTubeTranscriptApi
    from youtube_transcript_api._errors import (
        TranscriptsDisabled,
        NoTranscriptFound,
        VideoUnavailable,
        CouldNotRetrieveTranscript
    )
except ImportError:
    print("Error: youtube-transcript-api not found", file=sys.stderr)
    print("Install with: pip install youtube-transcript-api", file=sys.stderr)
    print("Or run with: uvx --from youtube-transcript-api python scripts/fetch-youtube-transcript.py <url>", file=sys.stderr)
    sys.exit(1)


# === UTILITY FUNCTIONS ===

def log(msg: str) -> None:
    """Log message to stderr."""
    print(f"[fetch-transcript] {msg}", file=sys.stderr)


def extract_video_id(url: str) -> Optional[str]:
    """
    Extract video ID from various YouTube URL formats.

    Supported formats:
    - https://www.youtube.com/watch?v=VIDEO_ID
    - https://www.youtube.com/watch?v=VIDEO_ID&t=123s
    - https://youtu.be/VIDEO_ID
    - https://youtu.be/VIDEO_ID?t=123
    """
    # Pattern for youtube.com URLs
    watch_pattern = r'(?:youtube\.com/watch\?v=)([a-zA-Z0-9_-]{11})'
    match = re.search(watch_pattern, url)
    if match:
        return match.group(1)

    # Pattern for youtu.be URLs
    short_pattern = r'(?:youtu\.be/)([a-zA-Z0-9_-]{11})'
    match = re.search(short_pattern, url)
    if match:
        return match.group(1)

    # If it looks like a video ID directly (11 characters)
    if re.match(r'^[a-zA-Z0-9_-]{11}$', url):
        return url

    return None


def format_timestamp(seconds: float) -> str:
    """Format seconds as [MM:SS] or [HH:MM:SS] timestamp."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)

    if hours > 0:
        return f"[{hours:02d}:{minutes:02d}:{secs:02d}]"
    else:
        return f"[{minutes:02d}:{secs:02d}]"


def fetch_transcript(video_id: str) -> list:
    """
    Fetch transcript for a YouTube video.

    Returns a list of transcript entries with 'start' and 'text' keys.
    Raises various exceptions if transcript is unavailable.
    """
    try:
        # Create API instance and list available transcripts
        api = YouTubeTranscriptApi()
        transcript_list = api.list(video_id)

        # Try to get English transcript, or use the first available
        for transcript in transcript_list:
            if transcript.language_code.startswith('en'):
                return transcript.fetch()

        # If no English, use the first available
        if len(transcript_list) > 0:
            return list(transcript_list)[0].fetch()

        raise NoTranscriptFound("No transcripts available")

    except TranscriptsDisabled:
        log(f"Transcripts are disabled for video: {video_id}")
        raise
    except NoTranscriptFound:
        log(f"No transcript found for video: {video_id}")
        raise
    except VideoUnavailable:
        log(f"Video unavailable: {video_id}")
        raise
    except CouldNotRetrieveTranscript as e:
        log(f"Could not retrieve transcript: {e}")
        raise
    except Exception as e:
        log(f"Error fetching transcript: {e}")
        raise


def save_transcript(transcript: list, output_path: Path, video_id: str) -> None:
    """Save transcript to a text file with timestamps."""
    lines = []

    # Add header
    lines.append(f"# YouTube Transcript: {video_id}")
    lines.append(f"# URL: https://www.youtube.com/watch?v={video_id}")
    lines.append("")

    # Add transcript with timestamps
    for entry in transcript:
        # Handle both dict and object attribute access
        if isinstance(entry, dict):
            timestamp = format_timestamp(entry['start'])
            text = entry['text'].strip()
        else:
            # Object with attributes
            timestamp = format_timestamp(entry.start)
            text = entry.text.strip()

        lines.append(f"{timestamp} {text}")

    # Write to file
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines) + "\n")
    log(f"Saved transcript to: {output_path}")


# === MAIN ===

def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Fetch YouTube video transcripts and save as readable text files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s "https://www.youtube.com/watch?v=4_2j5wgt_ds&t=135s"
  %(prog)s "https://youtu.be/4_2j5wgt_ds" --output .work/transcripts
  %(prog)s 4_2j5wgt_ds --output transcripts/
        """
    )

    parser.add_argument(
        "url",
        help="YouTube video URL or video ID"
    )

    parser.add_argument(
        "--output",
        type=str,
        default=".work/transcripts",
        help="Output directory for transcript files (default: .work/transcripts)"
    )

    args = parser.parse_args()

    # Extract video ID
    video_id = extract_video_id(args.url)
    if not video_id:
        log(f"Error: Could not extract video ID from: {args.url}")
        log("Supported formats:")
        log("  - https://www.youtube.com/watch?v=VIDEO_ID")
        log("  - https://youtu.be/VIDEO_ID")
        log("  - VIDEO_ID (11 characters)")
        return 1

    log(f"Fetching transcript for video: {video_id}")

    # Fetch transcript
    try:
        transcript = fetch_transcript(video_id)
    except TranscriptsDisabled:
        log("Error: Transcripts are disabled for this video")
        return 1
    except NoTranscriptFound:
        log("Error: No transcript available for this video")
        return 1
    except VideoUnavailable:
        log("Error: Video is private, deleted, or unavailable")
        return 1
    except Exception as e:
        log(f"Error: Failed to fetch transcript: {e}")
        return 1

    # Save transcript
    output_dir = Path(args.output)
    output_file = output_dir / f"{video_id}.txt"

    try:
        save_transcript(transcript, output_file, video_id)
        log(f"Success! Transcript saved with {len(transcript)} entries")
        return 0
    except Exception as e:
        log(f"Error saving transcript: {e}")
        return 1


if __name__ == "__main__":
    # Deprecation notice
    print("⚠️  DEPRECATED: Use 'forge youtube' instead", file=sys.stderr)
    print("See: forge youtube --help", file=sys.stderr)
    print("", file=sys.stderr)

    try:
        sys.exit(main())
    except KeyboardInterrupt:
        log("Interrupted by user")
        sys.exit(130)
    except Exception as e:
        log(f"Unexpected error: {e}")
        sys.exit(1)
