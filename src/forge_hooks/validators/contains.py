"""Validator to check if a file contains required content."""

from pathlib import Path

from ..common.file_discovery import find_newest_file
from ..common.hook_io import HookResult
from .base import BaseValidator

NO_FILE_ERROR = (
    "VALIDATION FAILED: No new file found matching {pattern}.\n\n"
    "ACTION REQUIRED: Use the Write tool to create a new file in the {directory}/ directory. "
    "The file must be created before this validation can pass. "
    "Do not stop until the file has been created."
)

MISSING_CONTENT_ERROR = (
    "VALIDATION FAILED: File '{file}' is missing {count} required section(s).\n\n"
    "MISSING SECTIONS:\n{missing_list}\n\n"
    "ACTION REQUIRED: Use the Edit tool to add the missing sections to '{file}'. "
    "Each section must appear exactly as shown above (case-sensitive). "
    "Do not stop until all required sections are present in the file."
)


class FileContainsValidator(BaseValidator):
    """Validates that a file contains required content strings."""

    def __init__(
        self, directory: str, extension: str, required_strings: list[str], max_age_minutes: int = 5
    ):
        """
        Initialize validator.

        Args:
            directory: Directory to check for files.
            extension: File extension to match.
            required_strings: List of strings that must be in the file.
            max_age_minutes: Maximum file age in minutes.
        """
        super().__init__(directory, extension, max_age_minutes)
        self.required_strings = required_strings

    def _check_file_contains(self, filepath: str) -> tuple[bool, list[str], list[str]]:
        """
        Check if file contains all required strings (case-sensitive).

        Args:
            filepath: Path to the file to check.

        Returns:
            Tuple of (all_found, found_list, missing_list).
        """
        try:
            content = Path(filepath).read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as e:
            self.logger.error(f"Failed to read file {filepath}: {e}")
            return False, [], self.required_strings

        found = []
        missing = []

        for req in self.required_strings:
            if req in content:
                found.append(req)
            else:
                missing.append(req)

        return len(missing) == 0, found, missing

    def validate(self) -> HookResult:
        """
        Validate that a file was created AND contains required content.

        Returns:
            HookResult indicating success or failure.
        """
        pattern = f"{self.directory}/*{self.extension}"
        self.logger.info(
            f"Validating: directory={self.directory}, extension={self.extension}, "
            f"max_age={self.max_age_minutes}min"
        )
        self.logger.info(f"Required strings: {self.required_strings}")

        # Step 1: Find the newest file
        newest_file = find_newest_file(self.directory, self.extension, self.max_age_minutes)

        if not newest_file:
            msg = NO_FILE_ERROR.format(pattern=pattern, directory=self.directory)
            self.logger.warning(f"FAIL: {msg}")
            return HookResult(ok=True, result="block", reason=msg)

        self.logger.info(f"Found newest file: {newest_file}")

        # Step 2: Check if file contains all required strings
        if not self.required_strings:
            msg = f"File found: {newest_file} (no content checks specified)"
            self.logger.info(f"PASS: {msg}")
            return HookResult(ok=True, result="continue", message=msg)

        all_found, found, missing = self._check_file_contains(newest_file)

        self.logger.info(f"Content check - Found: {len(found)}/{len(self.required_strings)}")
        if found:
            self.logger.info(f"  Found: {found}")
        if missing:
            self.logger.warning(f"  Missing: {missing}")

        if all_found:
            msg = (
                f"File '{newest_file}' contains all {len(self.required_strings)} required sections"
            )
            self.logger.info(f"PASS: {msg}")
            return HookResult(ok=True, result="continue", message=msg)
        else:
            missing_list = "\n".join(f"  - {m}" for m in missing)
            msg = MISSING_CONTENT_ERROR.format(
                file=newest_file, count=len(missing), missing_list=missing_list
            )
            self.logger.warning(f"FAIL: Missing {len(missing)} required sections")
            return HookResult(ok=True, result="block", reason=msg)
