"""Tests for feedback manager."""

import json

from forge_hooks.feedback.manager import FeedbackManager


class TestFeedbackManager:
    """Test cases for FeedbackManager."""

    def test_initialize_creates_directory_structure(self, tmp_path):
        """Test that initialize creates the correct directory structure."""
        learnings_dir = tmp_path / "learnings"
        manager = FeedbackManager(learnings_dir)

        result = manager.initialize()

        assert result is True
        assert learnings_dir.exists()
        assert (learnings_dir / "projects").exists()
        assert (learnings_dir / "cross-project").exists()
        assert (learnings_dir / "synced").exists()
        assert (learnings_dir / "projects.json").exists()
        assert (learnings_dir / "stats.json").exists()

    def test_initialize_creates_valid_json_files(self, tmp_path):
        """Test that initialize creates valid JSON files."""
        learnings_dir = tmp_path / "learnings"
        manager = FeedbackManager(learnings_dir)

        manager.initialize()

        # Check projects.json
        projects = json.loads((learnings_dir / "projects.json").read_text())
        assert projects["version"] == "1.0"
        assert "projects" in projects
        assert isinstance(projects["projects"], dict)

        # Check stats.json
        stats = json.loads((learnings_dir / "stats.json").read_text())
        assert stats["version"] == "1.0"
        assert stats["total_feedback"] == 0
        assert "by_type" in stats
        assert "by_project" in stats

    def test_initialize_returns_false_if_exists(self, tmp_path):
        """Test that initialize returns False if directory already exists."""
        learnings_dir = tmp_path / "learnings"
        manager = FeedbackManager(learnings_dir)

        # First initialization
        result1 = manager.initialize()
        assert result1 is True

        # Second initialization without force
        result2 = manager.initialize()
        assert result2 is False

    def test_initialize_with_force_reinitializes(self, tmp_path):
        """Test that initialize with force=True reinitializes."""
        learnings_dir = tmp_path / "learnings"
        manager = FeedbackManager(learnings_dir)

        # First initialization
        manager.initialize()

        # Modify stats
        stats_file = learnings_dir / "stats.json"
        stats = json.loads(stats_file.read_text())
        stats["total_feedback"] = 999
        stats_file.write_text(json.dumps(stats))

        # Reinitialize with force
        result = manager.initialize(force=True)
        assert result is True

        # Check that stats was reset
        stats = json.loads(stats_file.read_text())
        assert stats["total_feedback"] == 0

    def test_get_project_slug_sanitizes_name(self, tmp_path):
        """Test that get_project_slug sanitizes project names."""
        manager = FeedbackManager(tmp_path)

        # Test with special characters
        slug = manager.get_project_slug("/path/to/My Project! (2024)")
        assert slug == "my-project-2024"

        # Test with underscores and hyphens
        slug = manager.get_project_slug("/path/to/my_cool-project")
        assert slug == "my-cool-project"

    def test_register_project_creates_entry(self, tmp_path):
        """Test that register_project creates a project entry."""
        learnings_dir = tmp_path / "learnings"
        manager = FeedbackManager(learnings_dir)
        manager.initialize()

        project_dir = tmp_path / "test-project"
        project_dir.mkdir()

        slug = manager.register_project(str(project_dir))

        assert slug == "test-project"

        # Check that project was registered
        projects = json.loads(manager.projects_file.read_text())
        assert slug in projects["projects"]
        assert projects["projects"][slug]["path"] == str(project_dir)
        assert projects["projects"][slug]["feedback_count"] == 0

    def test_save_feedback_item_creates_file(self, tmp_path):
        """Test that save_feedback_item creates a feedback file."""
        learnings_dir = tmp_path / "learnings"
        manager = FeedbackManager(learnings_dir)
        manager.initialize()
        manager.register_project(str(tmp_path))

        item = {
            "type": "improvement",
            "title": "Test Feedback",
            "description": "This is a test feedback item",
            "target": "test-file.py",
        }

        filepath = manager.save_feedback_item(
            item, project_slug="learnings", session_id="test-session", cwd=str(tmp_path)
        )

        assert filepath is not None
        assert filepath.exists()
        assert filepath.suffix == ".md"

        # Check content
        content = filepath.read_text()
        assert "type: improvement" in content
        assert "# Test Feedback" in content
        assert "This is a test feedback item" in content

    def test_save_feedback_processes_multiple_items(self, tmp_path):
        """Test that save_feedback processes multiple items."""
        learnings_dir = tmp_path / "learnings"
        manager = FeedbackManager(learnings_dir)
        manager.initialize()

        feedback_data = {
            "session_id": "test-session",
            "cwd": str(tmp_path),
            "feedback": [
                {"type": "improvement", "title": "Item 1", "description": "First item"},
                {"type": "bug-report", "title": "Item 2", "description": "Second item"},
            ],
        }

        count = manager.save_feedback(feedback_data)

        assert count == 2

    def test_list_feedback_returns_items(self, tmp_path):
        """Test that list_feedback returns feedback items."""
        learnings_dir = tmp_path / "learnings"
        manager = FeedbackManager(learnings_dir)
        manager.initialize()

        feedback_data = {
            "session_id": "test-session",
            "cwd": str(tmp_path),
            "feedback": [
                {"type": "improvement", "title": "Test Item", "description": "Test description"}
            ],
        }

        manager.save_feedback(feedback_data)

        items = manager.list_feedback()

        assert len(items) > 0
        assert items[0]["type"] == "improvement"

    def test_list_feedback_filters_by_project(self, tmp_path):
        """Test that list_feedback filters by project."""
        learnings_dir = tmp_path / "learnings"
        manager = FeedbackManager(learnings_dir)
        manager.initialize()

        # Create two different project directories
        project1 = tmp_path / "project1"
        project2 = tmp_path / "project2"
        project1.mkdir()
        project2.mkdir()

        # Save feedback for project1
        feedback_data1 = {
            "session_id": "test-session-1",
            "cwd": str(project1),
            "feedback": [{"type": "improvement", "title": "Project 1 Item", "description": "Test"}],
        }
        manager.save_feedback(feedback_data1)

        # Save feedback for project2
        feedback_data2 = {
            "session_id": "test-session-2",
            "cwd": str(project2),
            "feedback": [{"type": "bug-report", "title": "Project 2 Item", "description": "Test"}],
        }
        manager.save_feedback(feedback_data2)

        # Filter by project1
        items = manager.list_feedback(project="project1")

        assert len(items) == 1
        assert items[0]["project"] == "project1"

    def test_list_feedback_filters_by_type(self, tmp_path):
        """Test that list_feedback filters by type."""
        learnings_dir = tmp_path / "learnings"
        manager = FeedbackManager(learnings_dir)
        manager.initialize()

        feedback_data = {
            "session_id": "test-session",
            "cwd": str(tmp_path),
            "feedback": [
                {"type": "improvement", "title": "Improvement Item", "description": "Test"},
                {"type": "bug-report", "title": "Bug Item", "description": "Test"},
            ],
        }
        manager.save_feedback(feedback_data)

        # Filter by improvement
        items = manager.list_feedback(feedback_type="improvement")

        assert len(items) == 1
        assert items[0]["type"] == "improvement"
