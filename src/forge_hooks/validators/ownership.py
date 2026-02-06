"""Validator for file ownership rules in task orchestration plans."""

import re
from pathlib import Path
from typing import Optional

from ..common.file_discovery import find_newest_file
from ..common.hook_io import HookResult
from .base import BaseValidator

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


def parse_scope(file_str: str) -> tuple[str, Optional[str]]:
    """
    Parse file::scope notation.

    Args:
        file_str: File string, possibly with scope (e.g., "file.py::ClassName").

    Returns:
        Tuple of (filename, scope) where scope is None for unscoped.

    Examples:
        "file.py" -> ("file.py", None)
        "file.py::ClassName" -> ("file.py", "ClassName")
        "file.py::ClassName.method" -> ("file.py", "ClassName.method")
    """
    if "::" in file_str:
        parts = file_str.split("::", 1)
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

    Args:
        scope1: First scope (or None for unscoped).
        scope2: Second scope (or None for unscoped).

    Returns:
        True if scopes overlap, False otherwise.
    """
    if scope1 is None or scope2 is None:
        return True  # Unscoped always overlaps

    if scope1 == scope2:
        return True  # Same scope overlaps

    # Check for nesting (e.g., "ClassName" vs "ClassName.method")
    if scope1.startswith(scope2 + ".") or scope2.startswith(scope1 + "."):
        return True

    return False


class FileOwnershipValidator(BaseValidator):
    """Validates file ownership rules in task orchestration plans."""

    def _parse_task_metadata(self, content: str) -> dict[str, dict]:
        """
        Parse task sections to extract Wave numbers and file ownership.

        Args:
            content: Plan file content.

        Returns:
            Dict mapping task_id -> {wave, create, modify, boundary}.
        """
        tasks = {}

        # Find all task sections
        # Pattern: #### or ### followed by Task ID
        task_pattern = r"###[#]?\s+.*?\n\*\*Task ID:\*\* (task-\d+).*?\*\*Wave:\*\* (\d+|W\d+).*?(?=###[#]?|\Z)"
        matches = re.finditer(task_pattern, content, re.DOTALL)

        for match in matches:
            task_id = match.group(1)
            wave_str = match.group(2).replace("W", "")  # Handle both "1" and "W1"
            task_content = match.group(0)

            # Extract File Ownership section
            create_files = []
            modify_files = []
            boundary_files = []

            ownership_pattern = r"\*\*File Ownership:\*\*(.*?)(?=\n\*\*[A-Z]|\Z)"
            ownership_match = re.search(ownership_pattern, task_content, re.DOTALL)
            if ownership_match:
                ownership_text = ownership_match.group(1)

                # Parse CREATE
                create_match = re.search(
                    r"- CREATE:\s*(.*?)(?=\n\s*-|\Z)", ownership_text, re.DOTALL
                )
                if create_match:
                    create_text = create_match.group(1).strip()
                    if create_text and create_text != "-":
                        create_files = [f.strip() for f in create_text.split(",") if f.strip()]

                # Parse MODIFY
                modify_match = re.search(
                    r"- MODIFY:\s*(.*?)(?=\n\s*-|\Z)", ownership_text, re.DOTALL
                )
                if modify_match:
                    modify_text = modify_match.group(1).strip()
                    if modify_text and modify_text != "-":
                        modify_files = [f.strip() for f in modify_text.split(",") if f.strip()]

                # Parse BOUNDARY
                boundary_match = re.search(
                    r"- BOUNDARY:\s*(.*?)(?=\n\s*-|\n\*\*|\Z)", ownership_text, re.DOTALL
                )
                if boundary_match:
                    boundary_text = boundary_match.group(1).strip()
                    if boundary_text and boundary_text != "-":
                        boundary_files = [f.strip() for f in boundary_text.split(",") if f.strip()]

            try:
                wave = int(wave_str)
            except ValueError:
                wave = 0

            tasks[task_id] = {
                "wave": wave,
                "create": create_files,
                "modify": modify_files,
                "boundary": boundary_files,
            }

        self.logger.info(f"Parsed {len(tasks)} tasks from plan")
        return tasks

    def _validate_ownership_rules(self, tasks: dict[str, dict]) -> tuple[bool, list[str]]:
        """
        Validate the four ownership rules.

        Rules:
        1. Each file appears in CREATE for at most ONE task (across all waves)
        2. For tasks in same wave with unscoped MODIFY, files must be different
        3. For tasks in same wave with scoped MODIFY (file::scope), scopes must not overlap
        4. No task modifies files in its BOUNDARY list

        Args:
            tasks: Dict mapping task_id -> task metadata.

        Returns:
            Tuple of (success, list of conflict messages).
        """
        conflicts = []

        # Rule 1: Each file appears in CREATE for at most ONE task (across all waves)
        create_map = {}  # file -> list of task_ids that CREATE it
        for task_id, task_data in tasks.items():
            for file in task_data["create"]:
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
            wave = task_data["wave"]
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
                for file_str in tasks[task_id]["modify"]:
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
            modify_files = {parse_scope(f)[0] for f in task_data["modify"]}
            boundary_files = {parse_scope(f)[0] for f in task_data["boundary"]}

            violations = modify_files & boundary_files
            if violations:
                conflicts.append(
                    f"Rule 4 violation: Task {task_id} modifies files in its BOUNDARY: {', '.join(violations)}"
                )

        return len(conflicts) == 0, conflicts

    def validate(self) -> HookResult:
        """
        Validate file ownership rules in the most recent plan file.

        Returns:
            HookResult indicating success or failure.
        """
        pattern = f"{self.directory}/*{self.extension}"
        self.logger.info(
            f"Validating ownership: directory={self.directory}, extension={self.extension}, "
            f"max_age={self.max_age_minutes}min"
        )

        # Step 1: Find the newest plan file
        newest_file = find_newest_file(self.directory, self.extension, self.max_age_minutes)

        if not newest_file:
            msg = NO_FILE_ERROR.format(pattern=pattern, directory=self.directory)
            self.logger.warning(f"FAIL: {msg}")
            return HookResult(ok=True, result="block", reason=msg)

        self.logger.info(f"Found newest file: {newest_file}")

        # Step 2: Read and parse the plan file
        try:
            content = Path(newest_file).read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as e:
            msg = f"Failed to read plan file {newest_file}: {e}"
            self.logger.error(msg)
            return HookResult(ok=True, result="block", reason=msg)

        # Step 3: Parse ownership data
        tasks = self._parse_task_metadata(content)

        if not tasks:
            msg = f"No tasks found in plan file {newest_file} (nothing to validate)"
            self.logger.info(f"PASS: {msg}")
            return HookResult(ok=True, result="continue", message=msg)

        # Step 4: Validate ownership rules
        success, conflicts = self._validate_ownership_rules(tasks)

        if success:
            msg = f"File ownership validation passed for {newest_file} ({len(tasks)} tasks)"
            self.logger.info(f"PASS: {msg}")
            return HookResult(ok=True, result="continue", message=msg)
        else:
            conflicts_text = "\n".join(f"  - {c}" for c in conflicts)
            msg = OWNERSHIP_CONFLICT_ERROR.format(conflicts=conflicts_text)
            self.logger.warning(f"FAIL: {len(conflicts)} ownership conflicts detected")
            for conflict in conflicts:
                self.logger.warning(f"  {conflict}")
            return HookResult(ok=True, result="block", reason=msg)
