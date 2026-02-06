"""
forge-hooks: Hook scripts and validators for Product Forge plugins.

This package provides:
- Common utilities for file discovery, git operations, and hook I/O
- Validators for file ownership, content, and creation
- CLI interface for running validators
"""

__version__ = "0.1.0"

from .common.hook_io import HookResult

__all__ = ["HookResult", "__version__"]
