"""Fetch YouTube video transcripts."""

import re
import sys
from pathlib import Path
from typing import Any, Optional

try:
    from youtube_transcript_api import YouTubeTranscriptApi
    from youtube_transcript_api._errors import (
        CouldNotRetrieveTranscript,
        NoTranscriptFound,
        TranscriptsDisabled,
        VideoUnavailable,
    )

    YOUTUBE_API_AVAILABLE = True
except ImportError:
    YOUTUBE_API_AVAILABLE = False
    YouTubeTranscriptApi = None
    TranscriptsDisabled = Exception
    NoTranscriptFound = Exception
    VideoUnavailable = Exception
    CouldNotRetrieveTranscript = Exception


class YouTubeFetcher:
    """Fetches transcripts from YouTube videos."""

    @staticmethod
    def check_dependency() -> bool:
        """Check if youtube-transcript-api is installed."""
        return YOUTUBE_API_AVAILABLE

    @staticmethod
    def print_install_instructions() -> None:
        """Print installation instructions for the missing dependency."""
        print("Error: youtube-transcript-api not found", file=sys.stderr)
        print("", file=sys.stderr)
        print("Install with one of:", file=sys.stderr)
        print("  uv tool install forge-cli --with youtube-transcript-api", file=sys.stderr)
        print("  uv pip install 'forge-cli[youtube]'", file=sys.stderr)
        print("  pip install 'forge-cli[youtube]'", file=sys.stderr)

    def extract_video_id(self, url: str) -> Optional[str]:
        """
        Extract video ID from various YouTube URL formats.

        Supported formats:
        - https://www.youtube.com/watch?v=VIDEO_ID
        - https://www.youtube.com/watch?v=VIDEO_ID&t=123s
        - https://youtu.be/VIDEO_ID
        - https://youtu.be/VIDEO_ID?t=123
        - VIDEO_ID (11 characters)

        Args:
            url: YouTube URL or video ID

        Returns:
            Video ID if found, None otherwise
        """
        # Pattern for youtube.com URLs
        watch_pattern = r"(?:youtube\.com/watch\?v=)([a-zA-Z0-9_-]{11})"
        match = re.search(watch_pattern, url)
        if match:
            return match.group(1)

        # Pattern for youtu.be URLs
        short_pattern = r"(?:youtu\.be/)([a-zA-Z0-9_-]{11})"
        match = re.search(short_pattern, url)
        if match:
            return match.group(1)

        # If it looks like a video ID directly (11 characters)
        if re.match(r"^[a-zA-Z0-9_-]{11}$", url):
            return url

        return None

    def format_timestamp(self, seconds: float) -> str:
        """
        Format seconds as [MM:SS] or [HH:MM:SS] timestamp.

        Args:
            seconds: Time in seconds

        Returns:
            Formatted timestamp string
        """
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)

        if hours > 0:
            return f"[{hours:02d}:{minutes:02d}:{secs:02d}]"
        else:
            return f"[{minutes:02d}:{secs:02d}]"

    def fetch_transcript(self, video_id: str) -> list[dict[str, Any]]:
        """
        Fetch transcript for a YouTube video.

        Args:
            video_id: YouTube video ID

        Returns:
            List of transcript entries with 'start' and 'text' keys

        Raises:
            TranscriptsDisabled: If transcripts are disabled for the video
            NoTranscriptFound: If no transcript is available
            VideoUnavailable: If video is unavailable
            CouldNotRetrieveTranscript: If transcript retrieval fails
        """
        if not YOUTUBE_API_AVAILABLE:
            raise ImportError("youtube-transcript-api is not installed")

        # Create API instance and list available transcripts
        api = YouTubeTranscriptApi()
        transcript_list = api.list(video_id)

        # Try to get English transcript, or use the first available
        for transcript in transcript_list:
            if transcript.language_code.startswith("en"):
                return transcript.fetch()

        # If no English, use the first available
        if len(transcript_list) > 0:
            return list(transcript_list)[0].fetch()

        raise NoTranscriptFound("No transcripts available")

    def save_transcript(self, url: str, output_dir: Optional[Path] = None) -> Path:
        """
        Fetch transcript and save to file.

        Args:
            url: YouTube URL or video ID
            output_dir: Output directory (default: .work/transcripts)

        Returns:
            Path to the saved transcript file

        Raises:
            ValueError: If video ID cannot be extracted
            Various youtube_transcript_api exceptions
        """
        if output_dir is None:
            output_dir = Path(".work/transcripts")

        # Extract video ID
        video_id = self.extract_video_id(url)
        if not video_id:
            raise ValueError(f"Could not extract video ID from: {url}")

        # Fetch transcript
        transcript = self.fetch_transcript(video_id)

        # Build output content
        lines = []
        lines.append(f"# YouTube Transcript: {video_id}")
        lines.append(f"# URL: https://www.youtube.com/watch?v={video_id}")
        lines.append("")

        # Add transcript with timestamps
        for entry in transcript:
            # Handle both dict and object attribute access
            if isinstance(entry, dict):
                timestamp = self.format_timestamp(entry["start"])
                text = entry["text"].strip()
            else:
                # Object with attributes
                timestamp = self.format_timestamp(entry.start)
                text = entry.text.strip()

            lines.append(f"{timestamp} {text}")

        # Write to file
        output_dir.mkdir(parents=True, exist_ok=True)
        output_file = output_dir / f"{video_id}.txt"
        output_file.write_text("\n".join(lines) + "\n")

        return output_file
