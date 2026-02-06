"""Tests for hook I/O utilities."""

import json

from forge_hooks.common.hook_io import HookResult


def test_hook_result_success():
    """Test successful hook result."""
    result = HookResult(ok=True, result="continue", message="Success!")
    assert result.is_success
    assert result.exit_code == 0
    assert result.to_dict() == {"ok": True, "result": "continue", "message": "Success!"}


def test_hook_result_block():
    """Test blocking hook result."""
    result = HookResult(ok=True, result="block", reason="Failed!")
    assert not result.is_success
    assert result.exit_code == 1
    assert result.to_dict() == {"ok": True, "result": "block", "reason": "Failed!"}


def test_hook_result_to_json():
    """Test JSON serialization."""
    result = HookResult(ok=True, result="continue", message="Test")
    json_str = result.to_json()
    data = json.loads(json_str)
    assert data == {"ok": True, "result": "continue", "message": "Test"}


def test_hook_result_excludes_none():
    """Test that None values are excluded from dict."""
    result = HookResult(ok=True, result="continue")
    data = result.to_dict()
    assert "message" not in data
    assert "reason" not in data
