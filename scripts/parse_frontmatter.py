#!/usr/bin/env python3
"""Helper library for parsing YAML frontmatter and document bodies from Markdown files."""

import re
from pathlib import Path
from typing import Dict, Any, Tuple
import yaml

FM_RE = re.compile(r"^---\r?\n(.*?)\r?\n---\r?\n", re.DOTALL)


def parse_frontmatter_and_body(text: str) -> Tuple[Dict[str, Any], str]:
    """Parse YAML frontmatter block and return (frontmatter_dict, body).
    
    If no frontmatter block is found, returns ({}, text).
    If YAML parsing fails, returns ({}, body).
    """
    text = text.replace("\r\n", "\n")
    match = FM_RE.match(text)
    if not match:
        return {}, text

    fm_raw = match.group(1).strip()
    body = text[match.end():]

    if not fm_raw:
        return {}, body

    try:
        data = yaml.safe_load(fm_raw)
        if not isinstance(data, dict):
            data = {}
    except Exception as e:
        data = {}

    return data, body


def parse_file(file_path: str | Path) -> Tuple[Dict[str, Any], str]:
    """Read a Markdown file and return (frontmatter_dict, body)."""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    text = path.read_text(encoding="utf-8")
    return parse_frontmatter_and_body(text)
