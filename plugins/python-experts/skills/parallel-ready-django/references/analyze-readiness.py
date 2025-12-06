#!/usr/bin/env python3
"""
Django Parallel Readiness Analyzer

Analyzes a Django codebase for parallelization readiness.
Run from project root: python analyze-readiness.py [apps_dir]

Requirements: None (uses only stdlib)
"""

import os
import re
import sys
import json
import subprocess
from pathlib import Path
from dataclasses import dataclass, field
from typing import TypedDict


class DimensionResult(TypedDict):
    score: int
    max: int
    issues: list[str]
    good: list[str]


@dataclass
class AnalysisResults:
    app_boundaries: DimensionResult = field(
        default_factory=lambda: {"score": 0, "max": 20, "issues": [], "good": []}
    )
    shared_state: DimensionResult = field(
        default_factory=lambda: {"score": 0, "max": 20, "issues": [], "good": []}
    )
    contracts: DimensionResult = field(
        default_factory=lambda: {"score": 0, "max": 20, "issues": [], "good": []}
    )
    tests: DimensionResult = field(
        default_factory=lambda: {"score": 0, "max": 15, "issues": [], "good": []}
    )
    documentation: DimensionResult = field(
        default_factory=lambda: {"score": 0, "max": 15, "issues": [], "good": []}
    )
    dependencies: DimensionResult = field(
        default_factory=lambda: {"score": 0, "max": 10, "issues": [], "good": []}
    )


# Configuration
APPS_DIR = sys.argv[1] if len(sys.argv) > 1 else "apps"
EXCLUDE_DIRS = {"__pycache__", ".git", "node_modules", "venv", ".venv", "env", ".env", "migrations"}

results = AnalysisResults()


def file_exists(path: str) -> bool:
    """Check if a file or directory exists."""
    return Path(path).exists()


def find_python_files(directory: str) -> list[Path]:
    """Find all Python files in directory, excluding certain folders."""
    files = []
    root = Path(directory)
    if not root.exists():
        return files

    for path in root.rglob("*.py"):
        if not any(excluded in path.parts for excluded in EXCLUDE_DIRS):
            files.append(path)
    return files


def read_file_safe(path: Path) -> str:
    """Safely read a file, returning empty string on error."""
    try:
        return path.read_text(encoding="utf-8")
    except Exception:
        return ""


def count_cross_app_imports(file_path: Path) -> dict[str, int]:
    """Count imports in a file, identifying cross-app imports."""
    content = read_file_safe(file_path)

    # Find all imports
    from_imports = re.findall(r"from\s+([\w.]+)\s+import", content)
    direct_imports = re.findall(r"^import\s+([\w.]+)", content, re.MULTILINE)

    all_imports = from_imports + direct_imports
    total = len(all_imports)

    # Count cross-app imports (imports from other apps)
    cross_app = 0
    for imp in all_imports:
        # Check if it's importing from another app
        if imp.startswith("apps.") or imp.startswith(".."):
            # Get the app name from the import
            parts = imp.split(".")
            if len(parts) >= 2:
                # Check if it's a different app than the current file's app
                file_app = None
                for part in file_path.parts:
                    if part != "apps" and part not in EXCLUDE_DIRS:
                        file_app = part
                        break
                if file_app and parts[1] != file_app:
                    cross_app += 1

    return {"total": total, "cross_app": cross_app}


def analyze_app_boundaries() -> None:
    """Analyze Django app separation and module boundaries."""
    python_files = find_python_files(APPS_DIR)

    if not python_files:
        # Try common alternatives
        for alt_dir in [".", "src", "project"]:
            python_files = find_python_files(alt_dir)
            if python_files:
                break

    total_imports = 0
    cross_app_imports = 0

    for file_path in python_files:
        counts = count_cross_app_imports(file_path)
        total_imports += counts["total"]
        cross_app_imports += counts["cross_app"]

    cross_ratio = cross_app_imports / total_imports if total_imports > 0 else 0

    if cross_ratio < 0.1:
        results.app_boundaries["score"] = 20
        results.app_boundaries["good"].append("Low cross-app imports (<10%)")
    elif cross_ratio < 0.3:
        results.app_boundaries["score"] = 12
        results.app_boundaries["issues"].append(
            f"Moderate cross-app imports ({cross_ratio * 100:.1f}%)"
        )
    else:
        results.app_boundaries["score"] = 5
        results.app_boundaries["issues"].append(
            f"High cross-app imports ({cross_ratio * 100:.1f}%)"
        )

    # Check for circular imports
    try:
        # Try to import the apps module to detect circular imports
        result = subprocess.run(
            [sys.executable, "-c", f"import sys; sys.setrecursionlimit(100); import {APPS_DIR.replace('/', '.')}"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if "RecursionError" in result.stderr or "circular" in result.stderr.lower():
            results.app_boundaries["score"] -= 5
            results.app_boundaries["issues"].append("Circular imports detected")
        else:
            results.app_boundaries["good"].append("No obvious circular imports")
    except Exception:
        pass

    # Count models per app to detect god apps
    apps_path = Path(APPS_DIR)
    if apps_path.exists():
        for app_dir in apps_path.iterdir():
            if app_dir.is_dir() and app_dir.name not in EXCLUDE_DIRS:
                models_file = app_dir / "models.py"
                if models_file.exists():
                    content = read_file_safe(models_file)
                    model_count = len(re.findall(r"class\s+\w+\(.*Model.*\):", content))
                    if model_count > 15:
                        results.app_boundaries["issues"].append(
                            f"App '{app_dir.name}' has {model_count} models (consider splitting)"
                        )


def analyze_shared_state() -> None:
    """Analyze global state and shared mutable patterns."""
    python_files = find_python_files(APPS_DIR) or find_python_files(".")

    global_patterns = 0
    signal_count = 0

    # Patterns indicating shared mutable state
    state_patterns = [
        r"^[a-z_][a-z0-9_]*\s*=\s*\[\]",  # module-level empty list
        r"^[a-z_][a-z0-9_]*\s*=\s*\{\}",  # module-level empty dict
        r"^[a-z_][a-z0-9_]*\s*=\s*set\(\)",  # module-level empty set
        r"global\s+\w+",  # global keyword usage
        r"_instance\s*=",  # singleton pattern
    ]

    signal_patterns = [
        r"@receiver\s*\(",
        r"\.connect\s*\(",
        r"post_save\.",
        r"pre_save\.",
        r"post_delete\.",
    ]

    for file_path in python_files:
        content = read_file_safe(file_path)

        for pattern in state_patterns:
            matches = re.findall(pattern, content, re.MULTILINE)
            global_patterns += len(matches)

        for pattern in signal_patterns:
            matches = re.findall(pattern, content)
            signal_count += len(matches)

    # Score based on global patterns
    if global_patterns < 5:
        results.shared_state["score"] = 15
        results.shared_state["good"].append("Minimal global state patterns")
    elif global_patterns < 20:
        results.shared_state["score"] = 10
        results.shared_state["issues"].append(
            f"Some global state patterns ({global_patterns} found)"
        )
    else:
        results.shared_state["score"] = 3
        results.shared_state["issues"].append(
            f"Heavy global state usage ({global_patterns} patterns)"
        )

    # Check signals
    if signal_count == 0:
        results.shared_state["score"] += 5
        results.shared_state["good"].append("No Django signals found")
    elif signal_count < 10:
        results.shared_state["score"] += 3
        results.shared_state["issues"].append(
            f"Some Django signals ({signal_count} found) - document side effects"
        )
    else:
        results.shared_state["issues"].append(
            f"Heavy signal usage ({signal_count} signals) - may cause parallel issues"
        )


def analyze_contracts() -> None:
    """Analyze API contracts, type hints, and serializers."""
    # Check for OpenAPI/Swagger
    openapi_files = [
        "openapi.yaml", "openapi.json", "swagger.yaml", "swagger.json",
        "schema.yaml", "schema.json"
    ]
    has_openapi = any(file_exists(f) for f in openapi_files)

    if has_openapi:
        results.contracts["score"] += 6
        results.contracts["good"].append("OpenAPI/Swagger spec found")
    else:
        # Check for drf-spectacular or similar
        for config_file in ["pyproject.toml", "setup.cfg", "settings.py", "settings/base.py"]:
            if file_exists(config_file):
                content = read_file_safe(Path(config_file))
                if "spectacular" in content.lower() or "swagger" in content.lower():
                    results.contracts["score"] += 4
                    results.contracts["good"].append("OpenAPI generator configured")
                    break
        else:
            results.contracts["issues"].append("No OpenAPI spec or generator found")

    # Check for mypy configuration
    mypy_configs = ["mypy.ini", "pyproject.toml", "setup.cfg", ".mypy.ini"]
    has_mypy = False
    is_strict = False

    for config_file in mypy_configs:
        if file_exists(config_file):
            content = read_file_safe(Path(config_file))
            if "[tool.mypy]" in content or "[mypy]" in content:
                has_mypy = True
                if "strict = true" in content.lower() or "strict=true" in content.lower():
                    is_strict = True
                break

    if has_mypy:
        results.contracts["score"] += 6
        results.contracts["good"].append("Mypy configured")
        if is_strict:
            results.contracts["score"] += 4
            results.contracts["good"].append("Mypy strict mode enabled")
        else:
            results.contracts["issues"].append("Mypy strict mode not enabled")
    else:
        results.contracts["issues"].append("No mypy configuration found")

    # Check serializers for __all__ usage
    python_files = find_python_files(APPS_DIR) or find_python_files(".")
    bad_serializers = 0

    for file_path in python_files:
        if "serializer" in file_path.name.lower():
            content = read_file_safe(file_path)
            matches = re.findall(r'fields\s*=\s*["\']__all__["\']', content)
            bad_serializers += len(matches)

    if bad_serializers == 0:
        results.contracts["score"] += 4
        results.contracts["good"].append("No serializers using __all__")
    else:
        results.contracts["issues"].append(
            f"{bad_serializers} serializers using __all__ (use explicit fields)"
        )


def analyze_tests() -> None:
    """Analyze test infrastructure and coverage."""
    # Find test files
    test_patterns = ["test_*.py", "*_test.py", "tests.py"]
    test_files = []

    for pattern in ["test_*.py", "*_test.py"]:
        test_files.extend(Path(".").rglob(pattern))

    # Filter out __pycache__ etc
    test_files = [f for f in test_files if not any(ex in f.parts for ex in EXCLUDE_DIRS)]

    if len(test_files) > 20:
        results.tests["score"] = 10
        results.tests["good"].append(f"Good test coverage ({len(test_files)} test files)")
    elif len(test_files) > 5:
        results.tests["score"] = 6
        results.tests["issues"].append(f"Moderate test coverage ({len(test_files)} test files)")
    elif len(test_files) > 0:
        results.tests["score"] = 3
        results.tests["issues"].append(f"Limited test coverage ({len(test_files)} test files)")
    else:
        results.tests["score"] = 0
        results.tests["issues"].append("No test files found")

    # Check for pytest configuration
    pytest_configs = ["pytest.ini", "pyproject.toml", "setup.cfg", "conftest.py"]
    has_pytest = False

    for config_file in pytest_configs:
        if file_exists(config_file):
            content = read_file_safe(Path(config_file))
            if "pytest" in content.lower() or config_file == "conftest.py":
                has_pytest = True
                break

    if has_pytest:
        results.tests["score"] += 3
        results.tests["good"].append("Pytest configured")
    else:
        results.tests["issues"].append("No pytest configuration found")

    # Check for factories
    factory_count = 0
    for file_path in Path(".").rglob("*.py"):
        if not any(ex in file_path.parts for ex in EXCLUDE_DIRS):
            content = read_file_safe(file_path)
            if "factory.Factory" in content or "DjangoModelFactory" in content:
                factory_count += 1

    if factory_count > 0:
        results.tests["score"] += 2
        results.tests["good"].append(f"Factory Boy factories found ({factory_count} files)")
    else:
        results.tests["issues"].append("No Factory Boy factories found (recommended)")


def analyze_documentation() -> None:
    """Analyze documentation and conventions."""
    # Check for CLAUDE.md
    if file_exists("CLAUDE.md"):
        results.documentation["score"] += 8
        results.documentation["good"].append("CLAUDE.md exists")
    else:
        results.documentation["issues"].append("CLAUDE.md missing")

    # Check for README
    if file_exists("README.md") or file_exists("README.rst"):
        results.documentation["score"] += 2
        results.documentation["good"].append("README exists")

    # Check for ruff/linting config
    linting_configs = [
        ("pyproject.toml", "[tool.ruff]"),
        (".ruff.toml", ""),
        ("ruff.toml", ""),
        ("setup.cfg", "[flake8]"),
        (".flake8", ""),
    ]

    has_linting = False
    for config_file, marker in linting_configs:
        if file_exists(config_file):
            if not marker:
                has_linting = True
                break
            content = read_file_safe(Path(config_file))
            if marker in content:
                has_linting = True
                break

    if has_linting:
        results.documentation["score"] += 3
        results.documentation["good"].append("Linting configured (ruff/flake8)")
    else:
        results.documentation["issues"].append("No linting configuration found")

    # Check for .claude directory
    if file_exists(".claude"):
        results.documentation["score"] += 2
        results.documentation["good"].append(".claude/ directory exists")


def analyze_dependencies() -> None:
    """Analyze dependency management."""
    # Check for lock files or pinned requirements
    if file_exists("poetry.lock"):
        results.dependencies["score"] += 5
        results.dependencies["good"].append("Poetry lock file present")
    elif file_exists("Pipfile.lock"):
        results.dependencies["score"] += 5
        results.dependencies["good"].append("Pipfile.lock present")
    elif file_exists("requirements.txt"):
        content = read_file_safe(Path("requirements.txt"))
        pinned = len(re.findall(r"==\d", content))
        total = len([line for line in content.split("\n") if line.strip() and not line.startswith("#")])

        if total > 0 and pinned / total > 0.8:
            results.dependencies["score"] += 4
            results.dependencies["good"].append("Most dependencies pinned in requirements.txt")
        elif pinned > 0:
            results.dependencies["score"] += 2
            results.dependencies["issues"].append("Some dependencies not pinned")
        else:
            results.dependencies["issues"].append("Dependencies not pinned in requirements.txt")
    else:
        results.dependencies["issues"].append("No dependency lock file found")

    # Check for pyproject.toml
    if file_exists("pyproject.toml"):
        results.dependencies["score"] += 3
        results.dependencies["good"].append("pyproject.toml present")

    # Check migrations health
    migration_count = len(list(Path(".").rglob("*/migrations/*.py")))
    migration_count -= len(list(Path(".").rglob("*/migrations/__init__.py")))

    if migration_count > 100:
        results.dependencies["issues"].append(
            f"Many migrations ({migration_count}) - consider squashing before parallel work"
        )
    elif migration_count > 0:
        results.dependencies["score"] += 2
        results.dependencies["good"].append(f"Manageable migration count ({migration_count})")


def generate_report() -> str:
    """Generate the markdown readiness report."""
    dimensions = {
        "App Boundaries": results.app_boundaries,
        "Shared State": results.shared_state,
        "API Contracts": results.contracts,
        "Test Infrastructure": results.tests,
        "Documentation": results.documentation,
        "Dependencies": results.dependencies,
    }

    total_score = sum(d["score"] for d in dimensions.values())
    max_score = sum(d["max"] for d in dimensions.values())
    percentage = round(total_score / max_score * 100) if max_score > 0 else 0

    report = f"""# Django Parallelization Readiness Report

## Overall Score: {total_score}/{max_score} ({percentage}%)

## Dimension Scores

| Dimension | Score | Status |
|-----------|-------|--------|
"""

    for name, data in dimensions.items():
        pct = data["score"] / data["max"] if data["max"] > 0 else 0
        if pct >= 0.8:
            status = "✅"
        elif pct >= 0.5:
            status = "⚠️"
        else:
            status = "❌"
        report += f"| {name} | {data['score']}/{data['max']} | {status} |\n"

    # Blockers (score < 50%)
    report += "\n## Blockers (Must Fix)\n\n"
    blockers = []
    for name, data in dimensions.items():
        if data["score"] / data["max"] < 0.5 if data["max"] > 0 else True:
            for issue in data["issues"]:
                blockers.append(f"- **{name}**: {issue}")

    if blockers:
        report += "\n".join(blockers) + "\n"
    else:
        report += "_No critical blockers found._\n"

    # Risks (50-80%)
    report += "\n## Risks (Should Fix)\n\n"
    risks = []
    for name, data in dimensions.items():
        pct = data["score"] / data["max"] if data["max"] > 0 else 0
        if 0.5 <= pct < 0.8:
            for issue in data["issues"]:
                risks.append(f"- **{name}**: {issue}")

    if risks:
        report += "\n".join(risks) + "\n"
    else:
        report += "_No significant risks identified._\n"

    # What's working well
    report += "\n## What's Working Well\n\n"
    for name, data in dimensions.items():
        for good in data["good"]:
            report += f"- ✅ {good}\n"

    # Recommendations
    report += "\n## Recommendations\n\n"

    if percentage < 50:
        report += """### Priority Actions (Score < 50%)

1. **Create CLAUDE.md** with project conventions
2. **Add type hints** to public APIs and run mypy
3. **Set up pytest** with Factory Boy
4. **Configure ruff** for consistent code style
5. **Document API contracts** with OpenAPI
"""
    elif percentage < 80:
        report += """### Improvement Actions (Score 50-80%)

1. **Enable mypy strict mode** for better type safety
2. **Convert signals to explicit service calls** where possible
3. **Use explicit serializer fields** (no `__all__`)
4. **Increase test coverage** in critical paths
5. **Set up .claude/ directory** for orchestration
"""
    else:
        report += """### Ready for Parallel Development (Score ≥ 80%)

1. **Create task specs** in `.claude/tasks/`
2. **Define interface contracts** in `.claude/contracts/`
3. **Plan parallel work boundaries** by app
4. **Set up git worktrees** for isolated development
"""

    # Parallelization potential
    report += f"""
## Parallelization Potential

Based on the analysis:
- **Recommended parallel tracks**: {estimate_parallel_tracks(percentage)}
- **Suggested boundaries**: Django apps (one agent per app)
- **Risk level**: {"Low" if percentage >= 80 else "Medium" if percentage >= 50 else "High"}

### Before Parallel Work

1. Run `python manage.py migrate` on all branches
2. Squash migrations if count > 50 per app
3. Document cross-app dependencies in contracts
4. Set up integration test suite
"""

    return report


def estimate_parallel_tracks(score_pct: int) -> str:
    """Estimate safe number of parallel tracks based on score."""
    if score_pct >= 80:
        return "3-5 (well-structured codebase)"
    elif score_pct >= 60:
        return "2-3 (moderate coupling)"
    elif score_pct >= 40:
        return "1-2 (significant coupling - fix blockers first)"
    else:
        return "1 (sequential recommended until blockers fixed)"


def main() -> None:
    """Run the analysis and generate report."""
    print("🔍 Analyzing Django codebase for parallelization readiness...\n")

    analyze_app_boundaries()
    analyze_shared_state()
    analyze_contracts()
    analyze_tests()
    analyze_documentation()
    analyze_dependencies()

    report = generate_report()

    # Print to console
    print(report)

    # Save report
    claude_dir = Path(".claude")
    claude_dir.mkdir(exist_ok=True)

    report_path = claude_dir / "readiness-report.md"
    report_path.write_text(report, encoding="utf-8")

    print(f"\n📄 Report saved to {report_path}")


if __name__ == "__main__":
    main()
