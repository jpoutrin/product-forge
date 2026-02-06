"""Tests for feedback statistics."""

import json

from forge_hooks.feedback.stats import FeedbackStats


class TestFeedbackStats:
    """Test cases for FeedbackStats."""

    def test_load_creates_default_if_not_exists(self, tmp_path):
        """Test that load creates default stats if file doesn't exist."""
        stats_file = tmp_path / "stats.json"

        stats = FeedbackStats.load(stats_file)

        assert stats.total == 0
        assert len(stats.by_type) > 0
        assert len(stats.by_project) == 0
        assert stats.last_updated is not None

    def test_load_reads_existing_file(self, tmp_path):
        """Test that load reads existing stats file."""
        stats_file = tmp_path / "stats.json"

        # Create stats file
        data = {
            "total_feedback": 10,
            "by_type": {"improvement": 5, "bug-report": 5},
            "by_project": {"project1": 10},
            "last_updated": "2024-01-01T00:00:00",
        }
        stats_file.write_text(json.dumps(data))

        # Load stats
        stats = FeedbackStats.load(stats_file)

        assert stats.total == 10
        assert stats.by_type["improvement"] == 5
        assert stats.by_project["project1"] == 10
        assert stats.last_updated == "2024-01-01T00:00:00"

    def test_save_writes_correct_format(self, tmp_path):
        """Test that save writes stats in correct format."""
        stats_file = tmp_path / "stats.json"

        stats = FeedbackStats(
            total=5,
            by_type={"improvement": 3, "bug-report": 2},
            by_project={"project1": 5},
            last_updated="2024-01-01T00:00:00",
        )

        stats.save(stats_file)

        # Read and verify
        data = json.loads(stats_file.read_text())
        assert data["version"] == "1.0"
        assert data["total_feedback"] == 5
        assert data["by_type"]["improvement"] == 3
        assert data["by_project"]["project1"] == 5

    def test_update_increments_counts(self):
        """Test that update increments counts correctly."""
        stats = FeedbackStats(
            total=0,
            by_type={"improvement": 0, "bug-report": 0},
            by_project={},
            last_updated="2024-01-01T00:00:00",
        )

        stats.update("improvement", "project1")

        assert stats.total == 1
        assert stats.by_type["improvement"] == 1
        assert stats.by_project["project1"] == 1
        assert stats.last_updated != "2024-01-01T00:00:00"

    def test_update_handles_multiple_projects(self):
        """Test that update handles multiple projects."""
        stats = FeedbackStats(
            total=0, by_type={"improvement": 0}, by_project={}, last_updated="2024-01-01T00:00:00"
        )

        stats.update("improvement", "project1")
        stats.update("improvement", "project2")
        stats.update("improvement", "project1")

        assert stats.total == 3
        assert stats.by_project["project1"] == 2
        assert stats.by_project["project2"] == 1

    def test_save_creates_parent_directory(self, tmp_path):
        """Test that save creates parent directory if needed."""
        stats_file = tmp_path / "nested" / "dir" / "stats.json"

        stats = FeedbackStats(
            total=0, by_type={}, by_project={}, last_updated="2024-01-01T00:00:00"
        )

        stats.save(stats_file)

        assert stats_file.exists()
        assert stats_file.parent.exists()
