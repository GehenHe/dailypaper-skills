#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import re
from typing import Any


def or_content_value(content: dict[str, Any], key: str, default: str = "") -> str:
    """Read OpenReview note.content.{key}.value (string or list)."""
    block = content.get(key)
    if not isinstance(block, dict):
        return default
    val = block.get("value")
    if val is None:
        return default
    if isinstance(val, list):
        return ", ".join(str(x) for x in val if x is not None)
    return str(val)


def extract_arxiv_id_from_text(text: str) -> str:
    if not text:
        return ""
    m = re.search(r"(\d{4}\.\d{4,5})(?:v\d+)?", text)
    return m.group(1) if m else ""


def stable_title_key(title: str) -> str:
    t = re.sub(r"\s+", " ", (title or "").strip().lower())
    return hashlib.sha256(t.encode("utf-8")).hexdigest()[:16]


def paper_dedup_key(p: dict) -> str:
    """Stable merge key across HF, arXiv, and conference sources."""
    for field in ("url", "pdf"):
        aid = extract_arxiv_id_from_text(str(p.get(field, "")))
        if aid:
            return f"arxiv:{aid}"
    if p.get("openreview_forum"):
        return f"or:{p['openreview_forum']}"
    if p.get("acl_anthology_id"):
        return f"acl:{p['acl_anthology_id']}"
    if p.get("cvf_paper_path"):
        return f"cvf:{p['cvf_paper_path']}"
    if p.get("doi"):
        return f"doi:{p['doi']}"
    if p.get("paper_id"):
        return f"id:{p['paper_id']}"
    return f"title:{stable_title_key(str(p.get('title', '')))}"
