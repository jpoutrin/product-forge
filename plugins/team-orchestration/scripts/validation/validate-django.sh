#!/usr/bin/env bash
# Django validation script for team-orchestration plugin
# Runs type checking, linting, tests, and Django-specific checks
#
# DEPRECATED: This script is deprecated in favor of the forge CLI command:
#   forge validate django [files]
#
# The forge command provides the same functionality with better integration
# and logging. This script will be removed in a future version.

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default to current directory if no files specified
FILES="${1:-.}"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Django Validation Suite${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo -e "Validating: ${YELLOW}$FILES${NC}"
echo ""

# Track overall success
VALIDATION_PASSED=true

# Detect if this is a uv-based project
UV_RUN=""
if [ -f "pyproject.toml" ] && command -v uv &> /dev/null; then
    echo -e "${BLUE}📦 Detected uv-based project${NC}"
    UV_RUN="uv run "
    echo ""
fi

# Load environment variables from .envrc if it exists
if [ -f ".envrc" ]; then
    echo -e "${BLUE}🔧 Loading environment variables${NC}"

    # Try using direnv if available
    if command -v direnv &> /dev/null; then
        eval "$(direnv export bash 2>/dev/null)" || true
    else
        # Fallback: manually parse and export simple export statements
        # This skips direnv-specific functions like dotenv_if_exists
        set -a  # Auto-export all variables
        while IFS= read -r line; do
            # Only process lines that start with 'export' and contain '='
            if [[ "$line" =~ ^export[[:space:]].*= ]]; then
                eval "$line" 2>/dev/null || true
            fi
        done < .envrc
        set +a  # Disable auto-export
    fi
    echo ""
fi

# Function to run a check and track results
run_check() {
    local name="$1"
    local command="$2"

    echo -e "${BLUE}→ Running $name...${NC}"

    if eval "$command"; then
        echo -e "${GREEN}✓ $name passed${NC}"
        echo ""
        return 0
    else
        echo -e "${RED}✗ $name failed${NC}"
        echo ""
        VALIDATION_PASSED=false
        return 1
    fi
}

# Check if we're in a Django project
if [ ! -f "manage.py" ]; then
    echo -e "${YELLOW}⚠️  Warning: manage.py not found in current directory${NC}"
    echo -e "   Django-specific checks will be skipped"
    echo ""
    SKIP_DJANGO_CHECKS=true
else
    SKIP_DJANGO_CHECKS=false
fi

# 1. Type Checking with mypy
if command -v mypy &> /dev/null || [ -n "$UV_RUN" ]; then
    # Skip mypy if no Python files to check
    if [ "$FILES" = "." ] || [[ "$FILES" == *.py ]]; then
        run_check "Type checking (mypy)" "${UV_RUN}mypy '$FILES' 2>&1" || true
    else
        echo -e "${YELLOW}⚠️  Skipping mypy - no Python files to check${NC}"
        echo ""
    fi
else
    echo -e "${YELLOW}⚠️  mypy not found - skipping type checks${NC}"
    echo -e "   Install with: pip install mypy"
    echo ""
fi

# 2. Linting with ruff
if command -v ruff &> /dev/null || [ -n "$UV_RUN" ]; then
    run_check "Linting (ruff)" "${UV_RUN}ruff check '$FILES' 2>&1" || true
else
    echo -e "${YELLOW}⚠️  ruff not found - skipping linting${NC}"
    echo -e "   Install with: pip install ruff"
    echo ""
fi

# 3. Unit Tests with pytest
if command -v pytest &> /dev/null || [ -n "$UV_RUN" ]; then
    # If specific files provided, try to find corresponding test files
    if [ "$FILES" != "." ]; then
        # Extract app name from path (e.g., "apps/users/models.py" -> "apps/users")
        APP_DIR=$(dirname "$FILES")
        TEST_PATH="${APP_DIR}/tests/"

        if [ -d "$TEST_PATH" ]; then
            run_check "Unit tests (pytest)" "${UV_RUN}pytest '$TEST_PATH' --cov='$APP_DIR' --cov-fail-under=80 -v 2>&1" || true
        else
            echo -e "${YELLOW}⚠️  Test directory not found: $TEST_PATH${NC}"
            echo -e "   Skipping test execution"
            echo ""
        fi
    else
        run_check "Unit tests (pytest)" "${UV_RUN}pytest --cov --cov-fail-under=80 -v 2>&1" || true
    fi
else
    echo -e "${YELLOW}⚠️  pytest not found - skipping tests${NC}"
    echo -e "   Install with: pip install pytest pytest-cov pytest-django"
    echo ""
fi

# 4. Django System Checks (if in Django project)
if [ "$SKIP_DJANGO_CHECKS" = false ]; then
    run_check "Django system checks" "${UV_RUN}python manage.py check --deploy 2>&1" || true
fi

# 5. Migration Validation (if in Django project)
if [ "$SKIP_DJANGO_CHECKS" = false ]; then
    run_check "Migration consistency" "${UV_RUN}python manage.py makemigrations --check --dry-run 2>&1" || true
fi

# Summary
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Validation Summary${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

if [ "$VALIDATION_PASSED" = true ]; then
    echo -e "${GREEN}✅ All validations passed${NC}"
    echo ""
    exit 0
else
    echo -e "${RED}❌ Some validations failed${NC}"
    echo ""
    echo "Please review the errors above and fix the issues."
    echo "Once fixed, run validation again to verify."
    echo ""
    exit 1
fi
