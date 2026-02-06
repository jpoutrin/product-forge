#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.9"
# dependencies = []
# ///

"""
Validates file ownership rules in task orchestration plans.

Hook Type: Stop

Checks:
1. Find the most recently created plan file in the specified directory
2. Parse File Ownership Matrix table
3. Extract task Wave numbers
4. Validate four ownership rules:
   - Rule 1: Each file appears in CREATE for at most ONE task (across all waves)
   - Rule 2: For tasks in same wave with unscoped MODIFY, files must be different
   - Rule 3: For tasks in same wave with scoped MODIFY (file::scope), scopes must not overlap
   - Rule 4: No task modifies files in its BOUNDARY list

Exit codes:
- 0: Validation passed (all ownership rules satisfied)
- 1: Validation failed (ownership conflicts detected)

Usage:
  uv run validate_file_ownership.py -d specs -e .md
  uv run validate_file_ownership.py --directory output --extension .md --max-age 10

Frontmatter example:
  hooks:
    Stop:
      - type: command
        command: "uv run $CLAUDE_PROJECT_DIR/.claude/hooks/validators/validate_file_ownership.py -d specs -e .md"
"""

import argparse
import json
import logging
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import Optional, Dict, List, Set, Tuple

# Logging setup - log file next to this script
SCRIPT_DIR = Path(__file__).parent
LOG_FILE = SCRIPT_DIR / "validate_file_ownership.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[logging.FileHandler(LOG_FILE, mode='a')]
)
logger = logging.getLogger(__name__)

# Constants
DEFAULT_DIRECTORY = "specs"
DEFAULT_EXTENSION = ".md"
DEFAULT_MAX_AGE_MINUTES = 5

# Error messages
NO_FILE_ERROR = (
    "VALIDATION FAILED: No plan file found matching {pattern}.\n\n"
    "ACTION REQUIRED: Create a plan file in the {directory}/ directory before validation can run."
)

OWNERSHIP_CONFLICT_ERROR = (
    "VALIDATION FAILED: File ownership conflicts detected.\n\n"
    "CONFLICTS:\n{conflicts}\n\n"
    "ACTION REQUIRED: Review the File Ownership Matrix and task definitions. "
    "Ensure each file is CREATEd by at most one task, parallel tasks have non-overlapping scopes, "
    "and no task modifies files in its BOUNDARY list."
)


def get_git_untracked_files(directory: str, extension: str) -> List[str]:
    """Get list of untracked files in directory from git."""
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain", f"{directory}/"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode != 0:
            logger.info(f"git status returned non-zero: {result.returncode}")
            return []

        untracked = []
        for line in result.stdout.strip().split('\n'):
            if not line:
                continue
            status = line[:2]
            filepath = line[3:].strip()

            if status in ('??', 'A ', ' A', 'AM') and filepath.endswith(extension):
                untracked.append(filepath)

        logger.info(f"Git untracked files: {untracked}")
        return untracked
    except (subprocess.TimeoutExpired, subprocess.SubprocessError) as e:
        logger.warning(f"Git command failed: {e}")
        return []


def get_recent_files(directory: str, extension: str, max_age_minutes: int) -> List[str]:
    """Get list of files in directory modified within the last N minutes."""
    target_dir = Path(directory)
    if not target_dir.exists():
        return []

    recent = []
    now = time.time()
    max_age_seconds = max_age_minutes * 60

    ext = extension if extension.startswith('.') else f'.{extension}'
    pattern = f"*{ext}"

    for filepath in target_dir.glob(pattern):
        try:
            mtime = filepath.stat().st_mtime
            age = now - mtime
            if age <= max_age_seconds:
                recent.append(str(filepath))
        except OSError:
            continue

    return recent


def find_newest_file(directory: str, extension: str, max_age_minutes: int) -> Optional[str]:
    """
    Find the most recently created/modified file in directory.

    Returns:
        Path to the newest file, or None if no recent files found.
    """
    # Check git for untracked/new files
    git_new = get_git_untracked_files(directory, extension)

    # Check for recently modified files
    recent_files = get_recent_files(directory, extension, max_age_minutes)

    # Combine and deduplicate
    all_files = list(set(git_new + recent_files))

    if not all_files:
        return None

    # Find the newest file by modification time
    newest = None
    newest_mtime = 0

    for filepath in all_files:
        try:
            path = Path(filepath)
            if path.exists():
                mtime = path.stat().st_mtime
                if mtime > newest_mtime:
                    newest_mtime = mtime
                    newest = str(path)
        except OSError:
            continue

    return newest


def parse_file_ownership_matrix(content: str) -> List[Dict[str, str]]:
    """
    Parse File Ownership Matrix table from markdown content.

    Returns list of dicts with keys: file, create, modify_scope, task_id, wave
    """
    matrix = []

    # Find the File Ownership Matrix section
    matrix_pattern = r'## File Ownership Matrix\s*\n\n(.*?)(?:\n##|\Z)'
    match = re.search(matrix_pattern, content, re.DOTALL)
    if not match:
        logger.warning("No File Ownership Matrix found in plan")
        return matrix

    matrix_section = match.group(1)

    # Parse table rows (skip header and separator)
    lines = matrix_section.strip().split('\n')
    for line in lines[2:]:  # Skip header and separator
        if not line.strip() or line.startswith('**'):
            continue

        # Parse table columns
        parts = [p.strip() for p in line.split('|')[1:-1]]  # Skip empty first/last
        if len(parts) >= 5:
            matrix.append({
                'file': parts[0],
                'create': parts[1],
                'modify_scope': parts[2],
                'task_id': parts[3],
                'wave': parts[4]
            })

    logger.info(f"Parsed {len(matrix)} entries from File Ownership Matrix")
    return matrix


def parse_task_metadata(content: str) -> Dict[str, Dict[str, any]]:
    """
    Parse task sections to extract Wave numbers and file ownership.

    Returns dict mapping task_id -> {wave, create, modify, boundary}
    """
    tasks = {}

    # Find all task sections
    # Pattern: #### or ### followed by Task ID
    task_pattern = r'###[#]?\s+.*?\n\*\*Task ID:\*\* (task-\d+).*?\*\*Wave:\*\* (\d+|W\d+).*?(?=###[#]?|\Z)'
    matches = re.finditer(task_pattern, content, re.DOTALL)

    for match in matches:
        task_id = match.group(1)
        wave_str = match.group(2).replace('W', '')  # Handle both "1" and "W1"
        task_content = match.group(0)

        # Extract File Ownership section
        create_files = []
        modify_files = []
        boundary_files = []

        ownership_pattern = r'\*\*File Ownership:\*\*(.*?)(?=\n\*\*[A-Z]|\Z)'
        ownership_match = re.search(ownership_pattern, task_content, re.DOTALL)
        if ownership_match:
            ownership_text = ownership_match.group(1)

            # Parse CREATE
            create_match = re.search(r'- CREATE:\s*(.*?)(?=\n\s*-|\Z)', ownership_text, re.DOTALL)
            if create_match:
                create_text = create_match.group(1).strip()
                if create_text and create_text != '-':
                    create_files = [f.strip() for f in create_text.split(',') if f.strip()]

            # Parse MODIFY
            modify_match = re.search(r'- MODIFY:\s*(.*?)(?=\n\s*-|\Z)', ownership_text, re.DOTALL)
            if modify_match:
                modify_text = modify_match.group(1).strip()
                if modify_text and modify_text != '-':
                    modify_files = [f.strip() for f in modify_text.split(',') if f.strip()]

            # Parse BOUNDARY
            boundary_match = re.search(r'- BOUNDARY:\s*(.*?)(?=\n\s*-|\n\*\*|\Z)', ownership_text, re.DOTALL)
            if boundary_match:
                boundary_text = boundary_match.group(1).strip()
                if boundary_text and boundary_text != '-':
                    boundary_files = [f.strip() for f in boundary_text.split(',') if f.strip()]

        try:
            wave = int(wave_str)
        except ValueError:
            wave = 0

        tasks[task_id] = {
            'wave': wave,
            'create': create_files,
            'modify': modify_files,
            'boundary': boundary_files
        }

    logger.info(f"Parsed {len(tasks)} tasks from plan")
    return tasks


def parse_scope(file_str: str) -> Tuple[str, Optional[str]]:
    """
    Parse file::scope notation.

    Returns: (filename, scope) where scope is None for unscoped
    Examples:
        "file.py" -> ("file.py", None)
        "file.py::ClassName" -> ("file.py", "ClassName")
        "file.py::ClassName.method" -> ("file.py", "ClassName.method")
    """
    if '::' in file_str:
        parts = file_str.split('::', 1)
        return parts[0].strip(), parts[1].strip()
    return file_str.strip(), None


def scopes_overlap(scope1: Optional[str], scope2: Optional[str]) -> bool:
    """
    Check if two scopes overlap.

    Rules:
    - If either is None (unscoped), they overlap
    - If they're identical, they overlap
    - If one is a prefix of the other (nested), they overlap
    - Otherwise they don't overlap
    """
    if scope1 is None or scope2 is None:
        return True  # Unscoped always overlaps

    if scope1 == scope2:
        return True  # Same scope overlaps

    # Check for nesting (e.g., "ClassName" vs "ClassName.method")
    if scope1.startswith(scope2 + '.') or scope2.startswith(scope1 + '.'):
        return True

    return False


def validate_ownership_rules(tasks: Dict[str, Dict[str, any]]) -> Tuple[bool, List[str]]:
    """
    Validate the four ownership rules.

    Returns: (success, list of conflict messages)
    """
    conflicts = []

    # Rule 1: Each file appears in CREATE for at most ONE task (across all waves)
    create_map = {}  # file -> list of task_ids that CREATE it
    for task_id, task_data in tasks.items():
        for file in task_data['create']:
            filename, _ = parse_scope(file)
            if filename not in create_map:
                create_map[filename] = []
            create_map[filename].append(task_id)

    for file, task_ids in create_map.items():
        if len(task_ids) > 1:
            conflicts.append(
                f"Rule 1 violation: File '{file}' is CREATEd by multiple tasks: {', '.join(task_ids)}"
            )

    # Group tasks by wave for Rules 2 and 3
    waves = {}  # wave -> list of task_ids
    for task_id, task_data in tasks.items():
        wave = task_data['wave']
        if wave not in waves:
            waves[wave] = []
        waves[wave].append(task_id)

    # Rules 2 & 3: Check parallel tasks (same wave) for MODIFY conflicts
    for wave, task_ids in waves.items():
        if len(task_ids) < 2:
            continue  # No conflicts possible with single task

        # Build modify map for this wave: file -> list of (task_id, scope)
        modify_map = {}
        for task_id in task_ids:
            for file_str in tasks[task_id]['modify']:
                filename, scope = parse_scope(file_str)
                if filename not in modify_map:
                    modify_map[filename] = []
                modify_map[filename].append((task_id, scope))

        # Check for conflicts
        for filename, modifiers in modify_map.items():
            if len(modifiers) < 2:
                continue

            # Check all pairs for scope overlap
            for i in range(len(modifiers)):
                for j in range(i + 1, len(modifiers)):
                    task1, scope1 = modifiers[i]
                    task2, scope2 = modifiers[j]

                    if scopes_overlap(scope1, scope2):
                        scope1_str = f"::{scope1}" if scope1 else " (unscoped)"
                        scope2_str = f"::{scope2}" if scope2 else " (unscoped)"
                        conflicts.append(
                            f"Rule 2/3 violation: Tasks {task1} and {task2} in Wave {wave} "
                            f"both MODIFY '{filename}' with overlapping scopes: "
                            f"{scope1_str} vs {scope2_str}"
                        )

    # Rule 4: No task modifies files in its BOUNDARY list
    for task_id, task_data in tasks.items():
        modify_files = {parse_scope(f)[0] for f in task_data['modify']}
        boundary_files = {parse_scope(f)[0] for f in task_data['boundary']}

        violations = modify_files & boundary_files
        if violations:
            conflicts.append(
                f"Rule 4 violation: Task {task_id} modifies files in its BOUNDARY: {', '.join(violations)}"
            )

    return len(conflicts) == 0, conflicts


def validate_file_ownership(
    directory: str,
    extension: str,
    max_age_minutes: int
) -> Tuple[bool, str]:
    """
    Validate file ownership rules in the most recent plan file.

    Returns:
        tuple: (success: bool, message: str)
    """
    pattern = f"{directory}/*{extension}"
    logger.info(f"Validating ownership: directory={directory}, extension={extension}, max_age={max_age_minutes}min")

    # Step 1: Find the newest plan file
    newest_file = find_newest_file(directory, extension, max_age_minutes)

    if not newest_file:
        msg = NO_FILE_ERROR.format(pattern=pattern, directory=directory)
        logger.warning(f"FAIL: {msg}")
        return False, msg

    logger.info(f"Found newest file: {newest_file}")

    # Step 2: Read and parse the plan file
    try:
        content = Path(newest_file).read_text(encoding='utf-8')
    except (OSError, UnicodeDecodeError) as e:
        msg = f"Failed to read plan file {newest_file}: {e}"
        logger.error(msg)
        return False, msg

    # Step 3: Parse ownership data
    tasks = parse_task_metadata(content)

    if not tasks:
        msg = f"No tasks found in plan file {newest_file} (nothing to validate)"
        logger.info(f"PASS: {msg}")
        return True, msg

    # Step 4: Validate ownership rules
    success, conflicts = validate_ownership_rules(tasks)

    if success:
        msg = f"File ownership validation passed for {newest_file} ({len(tasks)} tasks)"
        logger.info(f"PASS: {msg}")
        return True, msg
    else:
        conflicts_text = "\n".join(f"  - {c}" for c in conflicts)
        msg = OWNERSHIP_CONFLICT_ERROR.format(conflicts=conflicts_text)
        logger.warning(f"FAIL: {len(conflicts)} ownership conflicts detected")
        for conflict in conflicts:
            logger.warning(f"  {conflict}")
        return False, msg


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Validate file ownership rules in task orchestration plans"
    )
    parser.add_argument(
        '-d', '--directory',
        type=str,
        default=DEFAULT_DIRECTORY,
        help=f'Directory to check for plan files (default: {DEFAULT_DIRECTORY})'
    )
    parser.add_argument(
        '-e', '--extension',
        type=str,
        default=DEFAULT_EXTENSION,
        help=f'File extension to match (default: {DEFAULT_EXTENSION})'
    )
    parser.add_argument(
        '--max-age',
        type=int,
        default=DEFAULT_MAX_AGE_MINUTES,
        help=f'Maximum file age in minutes (default: {DEFAULT_MAX_AGE_MINUTES})'
    )
    return parser.parse_args()


def main():
    """Main entry point for the validator."""
    logger.info("=" * 60)
    logger.info("Validator started: validate_file_ownership")

    try:
        # Parse CLI arguments
        args = parse_args()
        logger.info(f"Args: directory={args.directory}, extension={args.extension}, max_age={args.max_age}")

        # Read hook input from stdin (if provided)
        try:
            input_data = json.load(sys.stdin)
            logger.info(f"Stdin input received: {len(json.dumps(input_data))} bytes")
        except (json.JSONDecodeError, EOFError):
            input_data = {}
            logger.info("No stdin input or invalid JSON")

        # Run validation
        success, message = validate_file_ownership(
            directory=args.directory,
            extension=args.extension,
            max_age_minutes=args.max_age
        )

        # Output result with "ok" field for hook schema
        if success:
            result = {"ok": True, "result": "continue", "message": message}
            logger.info(f"Result: CONTINUE - {message}")
            print(json.dumps(result))
            sys.exit(0)
        else:
            result = {"ok": True, "result": "block", "reason": message}
            logger.info(f"Result: BLOCK")
            print(json.dumps(result))
            sys.exit(1)

    except Exception as e:
        # On error, allow through but log
        logger.exception(f"Validation error: {e}")
        print(json.dumps({
            "ok": True,
            "result": "continue",
            "message": f"Validation error (allowing through): {str(e)}"
        }))
        sys.exit(0)


if __name__ == "__main__":
    main()
