"""Tests for YouTube transcript fetcher."""

from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from forge_hooks.utils.youtube import YouTubeFetcher


class TestYouTubeFetcher:
    """Test cases for YouTubeFetcher."""

    def test_extract_video_id_from_watch_url(self):
        """Test extracting video ID from youtube.com/watch URL."""
        fetcher = YouTubeFetcher()

        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        video_id = fetcher.extract_video_id(url)

        assert video_id == "dQw4w9WgXcQ"

    def test_extract_video_id_from_watch_url_with_timestamp(self):
        """Test extracting video ID from URL with timestamp."""
        fetcher = YouTubeFetcher()

        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=135s"
        video_id = fetcher.extract_video_id(url)

        assert video_id == "dQw4w9WgXcQ"

    def test_extract_video_id_from_short_url(self):
        """Test extracting video ID from youtu.be URL."""
        fetcher = YouTubeFetcher()

        url = "https://youtu.be/dQw4w9WgXcQ"
        video_id = fetcher.extract_video_id(url)

        assert video_id == "dQw4w9WgXcQ"

    def test_extract_video_id_from_short_url_with_timestamp(self):
        """Test extracting video ID from youtu.be URL with timestamp."""
        fetcher = YouTubeFetcher()

        url = "https://youtu.be/dQw4w9WgXcQ?t=123"
        video_id = fetcher.extract_video_id(url)

        assert video_id == "dQw4w9WgXcQ"

    def test_extract_video_id_from_direct_id(self):
        """Test extracting video ID when given ID directly."""
        fetcher = YouTubeFetcher()

        url = "dQw4w9WgXcQ"
        video_id = fetcher.extract_video_id(url)

        assert video_id == "dQw4w9WgXcQ"

    def test_extract_video_id_returns_none_for_invalid_url(self):
        """Test that invalid URL returns None."""
        fetcher = YouTubeFetcher()

        url = "https://example.com/not-a-youtube-url"
        video_id = fetcher.extract_video_id(url)

        assert video_id is None

    def test_format_timestamp_minutes_only(self):
        """Test formatting timestamp with minutes and seconds."""
        fetcher = YouTubeFetcher()

        timestamp = fetcher.format_timestamp(135.5)

        assert timestamp == "[02:15]"

    def test_format_timestamp_with_hours(self):
        """Test formatting timestamp with hours."""
        fetcher = YouTubeFetcher()

        timestamp = fetcher.format_timestamp(3665.0)

        assert timestamp == "[01:01:05]"

    def test_format_timestamp_zero(self):
        """Test formatting zero timestamp."""
        fetcher = YouTubeFetcher()

        timestamp = fetcher.format_timestamp(0)

        assert timestamp == "[00:00]"

    @pytest.mark.skipif(
        not YouTubeFetcher.check_dependency(), reason="youtube-transcript-api not installed"
    )
    @patch("forge_hooks.utils.youtube.YouTubeTranscriptApi")
    def test_fetch_transcript_success(self, mock_api_class):
        """Test successful transcript fetch."""
        fetcher = YouTubeFetcher()

        # Mock the API
        mock_api = Mock()
        mock_api_class.return_value = mock_api

        # Mock transcript
        mock_transcript = Mock()
        mock_transcript.language_code = "en"
        mock_transcript.fetch.return_value = [
            {"start": 0.0, "text": "Hello world"},
            {"start": 2.5, "text": "This is a test"},
        ]

        mock_api.list.return_value = [mock_transcript]

        # Fetch transcript
        result = fetcher.fetch_transcript("dQw4w9WgXcQ")

        assert len(result) == 2
        assert result[0]["text"] == "Hello world"

    @pytest.mark.skipif(
        not YouTubeFetcher.check_dependency(), reason="youtube-transcript-api not installed"
    )
    def test_save_transcript(self, tmp_path):
        """Test saving transcript to file."""
        fetcher = YouTubeFetcher()

        # Mock fetch_transcript
        with patch.object(fetcher, "fetch_transcript") as mock_fetch:
            mock_fetch.return_value = [
                {"start": 0.0, "text": "Hello world"},
                {"start": 2.5, "text": "This is a test"},
            ]

            # Save transcript
            output_path = fetcher.save_transcript(
                "https://www.youtube.com/watch?v=dQw4w9WgXcQ", tmp_path
            )

            # Verify file was created
            assert output_path.exists()
            assert output_path.name == "dQw4w9WgXcQ.txt"

            # Verify content
            content = output_path.read_text()
            assert "# YouTube Transcript: dQw4w9WgXcQ" in content
            assert "[00:00] Hello world" in content
            assert "[00:02] This is a test" in content

    def test_save_transcript_raises_on_invalid_url(self):
        """Test that save_transcript raises ValueError for invalid URL."""
        fetcher = YouTubeFetcher()

        with pytest.raises(ValueError, match="Could not extract video ID"):
            fetcher.save_transcript("not-a-url", Path("/tmp"))
