#!/usr/bin/env python3
"""ACM Multimedia — SIGMM Open TOC HTML when available."""

from __future__ import annotations

import re
import sys
from html import unescape
from typing import Callable

from .common import extract_arxiv_id_from_text


def _mm_toc_url(year: int) -> str | None:
    # Common SIGMM opentoc pattern
    return f"https://www.sigmm.org/opentoc/MM{year}-TOC"


def fetch_acm_mm(
    venue: str,
    year: int,
    max_per_venue: int,
    fetch_url: Callable[[str, int], str],
    score_paper: Callable[[dict, bool], int],
    folder_label: str,
    source_tag: str,
) -> list[dict]:
    toc = _mm_toc_url(year)
    if not toc:
        return []
    print(f"  ACM MM Open TOC {toc} ...", file=sys.stderr)
    html = fetch_url(toc, timeout=120)
    if not html:
        return []

    # Links to .pdf or ACM DL
    papers: list[dict] = []
    seen: set[str] = set()
    for m in re.finditer(r'href="([^"]+\.pdf)"[^>]*>([^<]{6,})</a>', html, re.IGNORECASE):
        if len(papers) >= max_per_venue:
            break
        pdf_url, title_raw = m.group(1), m.group(2)
        title = unescape(re.sub(r"\s+", " ", title_raw)).strip()
        key = pdf_url
        if key in seen:
            continue
        seen.add(key)

        aid = extract_arxiv_id_from_text(pdf_url + " " + title)
        abs_url = f"https://arxiv.org/abs/{aid}" if aid else pdf_url

        paper = {
            "title": title,
            "authors": "",
            "affiliations": "",
            "abstract": "",
            "url": abs_url,
            "pdf": pdf_url,
            "date": f"{year}-10-01",
            "score": 0,
            "category": "conference",
            "source": source_tag,
            "conference": "ACM MM",
            "year": year,
            "track": "main",
            "paper_id": f"mm:{key}",
        }
        paper["score"] = score_paper(paper, is_trending=False)
        if paper["score"] >= 0:
            papers.append(paper)

    print(f"    → {len(papers)} MM papers ({year})", file=sys.stderr)
    return papers
