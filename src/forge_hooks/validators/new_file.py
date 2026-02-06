"""Validator to check if a new file was created."""

from ..common.file_discovery import get_recent_files
from ..common.git_utils import get_git_untracked_files
from ..common.hook_io import HookResult
from .base import BaseValidator

NO_FILE_ERROR = (
    "VALIDATION FAILED: No new file found matching {pattern}.\n\n"
    "ACTION REQUIRED: Use the Write tool to create a new file in the {directory}/ directory. "
    "The file must match the expected pattern ({pattern}). "
    "Do not stop until the file has been created."
)


class NewFileValidator(BaseValidator):
    """Validates that a new file was created in the specified directory."""

    def validate(self) -> HookResult:
        """
        Check if a new file was created.

        Returns:
            HookResult indicating success or failure.
        """
        pattern = f"{self.directory}/*{self.extension}"
        self.logger.info(
            f"Validating: directory={self.directory}, extension={self.extension}, "
            f"max_age={self.max_age_minutes}min"
        )

        # Check git for untracked/new files
        git_new = get_git_untracked_files(self.directory, self.extension)
        self.logger.info(f"Git new files: {git_new}")

        # Check for recently modified files
        recent_files = get_recent_files(self.directory, self.extension, self.max_age_minutes)
        self.logger.info(f"Recent files: {recent_files}")

        # If git shows new files, that's a strong signal
        if git_new:
            msg = f"New file(s) found: {', '.join(git_new)}"
            self.logger.info(f"PASS: {msg}")
            return HookResult(ok=True, result="continue", message=msg)

        # If no git new files, check if there are any recent files
        if recent_files:
            msg = f"Recently created file(s) found: {', '.join(recent_files)}"
            self.logger.info(f"PASS: {msg}")
            return HookResult(ok=True, result="continue", message=msg)

        # No files found
        msg = NO_FILE_ERROR.format(pattern=pattern, directory=self.directory)
        self.logger.warning(f"FAIL: {msg}")
        return HookResult(ok=True, result="block", reason=msg)
