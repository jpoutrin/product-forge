"""Base validator class for all validators."""

import logging
from abc import ABC, abstractmethod

from ..common.hook_io import HookResult

logger = logging.getLogger(__name__)


class BaseValidator(ABC):
    """Base class for all validators."""

    def __init__(self, directory: str, extension: str, max_age_minutes: int = 5):
        """
        Initialize validator.

        Args:
            directory: Directory to check for files.
            extension: File extension to match.
            max_age_minutes: Maximum file age in minutes.
        """
        self.directory = directory
        self.extension = extension
        self.max_age_minutes = max_age_minutes
        self.logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    def validate(self) -> HookResult:
        """
        Run validation logic. Override in subclasses.

        Returns:
            HookResult with validation outcome.
        """
        pass

    def run(self) -> int:
        """
        Execute validator with error handling and output result.

        Returns:
            Exit code (0 for success, 1 for failure).
        """
        try:
            result = self.validate()
            self.logger.info(
                f"Validation {'PASSED' if result.is_success else 'FAILED'}: "
                f"{result.message or result.reason}"
            )
            return result.exit_code
        except Exception as e:
            # On error, allow through but log
            self.logger.exception(f"Validation error: {e}")
            result = HookResult(
                ok=True, result="continue", message=f"Validation error (allowing through): {str(e)}"
            )
            return 0
