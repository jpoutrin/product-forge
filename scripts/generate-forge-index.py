#!/usr/bin/env python3
"""
Generate a compact index of all Product Forge agents, skills, and commands.

Usage:
    python generate-forge-index.py [--output index.md] [--format md|json]

This script scans the plugins directory and extracts metadata from:
- agents/*.md files
- skills/*/SKILL.md files
- commands/*.md files

Supports custom frontmatter fields:
- short: Brief one-liner description
- when: Semantic activation - describes when to use this tool
- category: Override auto-detected category

Output is a compact markdown or JSON file that Claude can read quickly.
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

# Categories based on plugin names
PLUGIN_CATEGORIES = {
    "product-design": "Product & Strategy",
    "python-experts": "Backend Development",
    "frontend-experts": "Frontend Development",
    "devops-data": "DevOps & Data",
    "security-compliance": "Security & Compliance",
    "rag-cag": "AI & RAG/CAG",
    "git-workflow": "Git & Workflow",
    "claude-code-dev": "Claude Code Development",
    "atlassian-integration": "Atlassian Integration",
}


def parse_frontmatter(content: str) -> dict[str, Any]:
    """Extract YAML frontmatter from markdown content."""
    match = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
    if not match:
        return {}

    frontmatter = {}
    current_key = None
    current_value_lines = []

    for line in match.group(1).strip().split("\n"):
        # Check if this is a new key
        if re.match(r"^[a-zA-Z_-]+:", line) and not line.startswith(" "):
            # Save previous key if exists
            if current_key:
                frontmatter[current_key] = "\n".join(current_value_lines).strip().strip('"\'')
            # Start new key
            key, value = line.split(":", 1)
            current_key = key.strip()
            current_value_lines = [value.strip()]
        elif current_key:
            # Continue previous value (multiline)
            current_value_lines.append(line)

    # Don't forget the last key
    if current_key:
        frontmatter[current_key] = "\n".join(current_value_lines).strip().strip('"\'')

    return frontmatter


def scan_agents(plugins_dir: Path) -> list[dict]:
    """Scan all agent files."""
    agents = []
    for agent_file in plugins_dir.glob("*/agents/*.md"):
        content = agent_file.read_text()
        meta = parse_frontmatter(content)
        if meta.get("name"):
            plugin_name = agent_file.parent.parent.name
            category = meta.get("category", PLUGIN_CATEGORIES.get(plugin_name, "Other"))
            agents.append(
                {
                    "name": meta["name"],
                    "short": meta.get("short", ""),
                    "description": meta.get("description", ""),
                    "when": meta.get("when", ""),
                    "model": meta.get("model", "sonnet"),
                    "plugin": plugin_name,
                    "category": category,
                }
            )
    return sorted(agents, key=lambda x: (x["category"], x["name"]))


def scan_skills(plugins_dir: Path) -> list[dict]:
    """Scan all skill files."""
    skills = []
    for skill_file in plugins_dir.glob("*/skills/*/SKILL.md"):
        content = skill_file.read_text()
        meta = parse_frontmatter(content)
        if meta.get("name"):
            plugin_name = skill_file.parent.parent.parent.name
            category = meta.get("category", PLUGIN_CATEGORIES.get(plugin_name, "Other"))
            skills.append(
                {
                    "name": meta["name"],
                    "short": meta.get("short", ""),
                    "description": meta.get("description", ""),
                    "when": meta.get("when", ""),
                    "plugin": plugin_name,
                    "category": category,
                }
            )
    return sorted(skills, key=lambda x: (x["category"], x["name"]))


def scan_commands(plugins_dir: Path) -> list[dict]:
    """Scan all command files."""
    commands = []
    for cmd_file in plugins_dir.glob("*/commands/*.md"):
        content = cmd_file.read_text()
        meta = parse_frontmatter(content)
        if meta.get("description"):
            plugin_name = cmd_file.parent.parent.name
            cmd_name = cmd_file.stem
            category = meta.get("category", PLUGIN_CATEGORIES.get(plugin_name, "Other"))
            commands.append(
                {
                    "name": cmd_name,
                    "short": meta.get("short", ""),
                    "description": meta["description"],
                    "when": meta.get("when", ""),
                    "args": meta.get("argument-hint", ""),
                    "plugin": plugin_name,
                    "category": category,
                }
            )
    return sorted(commands, key=lambda x: (x["category"], x["name"]))


def generate_markdown(agents: list, skills: list, commands: list) -> str:
    """Generate compact markdown index."""
    lines = [
        "# Product Forge Index",
        "",
        "Quick reference for all available agents, skills, and commands.",
        "",
        "## Agents",
        "",
        "Use: `@agent-name` or ask Claude to invoke the agent.",
        "",
    ]

    # Group agents by category
    agent_by_cat: dict[str, list] = {}
    for a in agents:
        cat = a["category"]
        if cat not in agent_by_cat:
            agent_by_cat[cat] = []
        agent_by_cat[cat].append(a)

    for cat_name in sorted(agent_by_cat.keys()):
        lines.append(f"### {cat_name}")
        lines.append("")
        for a in agent_by_cat[cat_name]:
            desc = a["short"] if a["short"] else a["description"][:60]
            if not a["short"] and len(a["description"]) > 60:
                desc += "..."
            lines.append(f"- **@{a['name']}** ({a['model']}) - {desc}")
            if a["when"]:
                lines.append(f"  - _When: {a['when']}_")
        lines.append("")

    lines.extend(
        [
            "## Skills",
            "",
            "Auto-activate on context, or use: `skill: \"skill-name\"`",
            "",
        ]
    )

    # Group skills by category
    skill_by_cat: dict[str, list] = {}
    for s in skills:
        cat = s["category"]
        if cat not in skill_by_cat:
            skill_by_cat[cat] = []
        skill_by_cat[cat].append(s)

    for cat_name in sorted(skill_by_cat.keys()):
        lines.append(f"### {cat_name}")
        lines.append("")
        for s in skill_by_cat[cat_name]:
            desc = s["short"] if s["short"] else s["description"][:60]
            if not s["short"] and len(s["description"]) > 60:
                desc += "..."
            lines.append(f"- **{s['name']}** - {desc}")
            if s["when"]:
                lines.append(f"  - _When: {s['when']}_")
        lines.append("")

    lines.extend(
        [
            "## Commands",
            "",
            "Use: `/plugin-name:command-name` or `/command-name`",
            "",
        ]
    )

    # Group commands by category
    cmd_by_cat: dict[str, list] = {}
    for c in commands:
        cat = c["category"]
        if cat not in cmd_by_cat:
            cmd_by_cat[cat] = []
        cmd_by_cat[cat].append(c)

    for cat_name in sorted(cmd_by_cat.keys()):
        lines.append(f"### {cat_name}")
        lines.append("")
        for c in cmd_by_cat[cat_name]:
            desc = c["short"] if c["short"] else c["description"][:50]
            if not c["short"] and len(c["description"]) > 50:
                desc += "..."
            args = f" {c['args']}" if c["args"] else ""
            lines.append(f"- **/{c['name']}**{args} - {desc}")
            if c["when"]:
                lines.append(f"  - _When: {c['when']}_")
        lines.append("")

    return "\n".join(lines)


def generate_json(agents: list, skills: list, commands: list) -> str:
    """Generate JSON index."""
    return json.dumps(
        {"agents": agents, "skills": skills, "commands": commands},
        indent=2,
    )


def main():
    parser = argparse.ArgumentParser(description="Generate Product Forge index")
    parser.add_argument(
        "--output",
        "-o",
        default="forge-index.md",
        help="Output file path",
    )
    parser.add_argument(
        "--format",
        "-f",
        choices=["md", "json"],
        default="md",
        help="Output format",
    )
    parser.add_argument(
        "--plugins-dir",
        "-p",
        default=None,
        help="Path to plugins directory",
    )
    args = parser.parse_args()

    # Find plugins directory
    if args.plugins_dir:
        plugins_dir = Path(args.plugins_dir)
    else:
        # Try relative to script location
        script_dir = Path(__file__).parent
        plugins_dir = script_dir.parent / "plugins"
        if not plugins_dir.exists():
            # Try current directory
            plugins_dir = Path.cwd() / "plugins"

    if not plugins_dir.exists():
        print(f"Error: Plugins directory not found at {plugins_dir}", file=sys.stderr)
        sys.exit(1)

    print(f"Scanning plugins in: {plugins_dir}")

    agents = scan_agents(plugins_dir)
    skills = scan_skills(plugins_dir)
    commands = scan_commands(plugins_dir)

    print(f"Found: {len(agents)} agents, {len(skills)} skills, {len(commands)} commands")

    if args.format == "json":
        output = generate_json(agents, skills, commands)
    else:
        output = generate_markdown(agents, skills, commands)

    output_path = Path(args.output)
    output_path.write_text(output)
    print(f"Index written to: {output_path}")


if __name__ == "__main__":
    main()
