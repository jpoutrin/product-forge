#!/usr/bin/env python3
"""Validate marketplace.json against the Claude Code marketplace schema."""

import json
import sys
from pathlib import Path

try:
    import jsonschema
    import requests
except ImportError:
    print("Missing dependencies. Install with: pip install jsonschema requests")
    sys.exit(1)

SCHEMA_URL = "https://anthropic.com/claude-code/marketplace.schema.json"
MARKETPLACE_PATH = Path(__file__).parent.parent / ".claude-plugin" / "marketplace.json"


def fetch_schema() -> dict:
    """Fetch the JSON schema from Anthropic."""
    try:
        response = requests.get(SCHEMA_URL, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Warning: Could not fetch schema from {SCHEMA_URL}: {e}")
        print("Falling back to basic JSON validation only.")
        return None


def validate_marketplace(marketplace_path: Path, schema: dict | None) -> bool:
    """Validate the marketplace.json file."""
    try:
        with open(marketplace_path) as f:
            marketplace = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Invalid JSON in {marketplace_path}: {e}")
        return False
    except FileNotFoundError:
        print(f"Marketplace file not found: {marketplace_path}")
        return False

    if schema is None:
        print(f"JSON is valid (schema validation skipped)")
        return True

    try:
        jsonschema.validate(instance=marketplace, schema=schema)
        print(f"Marketplace validation passed")
        return True
    except jsonschema.ValidationError as e:
        print(f"Validation error: {e.message}")
        print(f"  Path: {' -> '.join(str(p) for p in e.absolute_path)}")
        return False


def main() -> int:
    marketplace_path = Path(sys.argv[1]) if len(sys.argv) > 1 else MARKETPLACE_PATH

    print(f"Validating: {marketplace_path}")
    schema = fetch_schema()

    if validate_marketplace(marketplace_path, schema):
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
