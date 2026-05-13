#!/usr/bin/env python3
"""AAAI proceedings via official AAAI/OJS pages."""

from __future__ import annotations

import re
import sys
from html import unescape
from typing import Callable


def _aaai_volume(year: int) -> int:
    # AAAI-39 corresponds to 2025, AAAI-38 to 2024.
    return year - 1986


def _meta(page: str, name: str) -> list[str]:
    return [
        unescape(m).strip()
        for m in re.findall(
            rf'<meta\s+name="{re.escape(name)}"\s+content="([^"]*)"',
            page,
            flags=re.IGNORECASE,
        )
        if m.strip()
    ]


def fetch_aaai(
    venue: str,
    year: int,
    max_per_venue: int,
    fetch_url: Callable[[str, int], str],
    score_paper: Callable[[dict, bool], int],
    folder_label: str,
    source_tag: str,
) -> list[dict]:
    volume = _aaai_volume(year)
    archive_url = f"https://aaai.org/proceeding/aaai-{volume}-{year}/"
    print(f"  AAAI proceedings {archive_url} ...", file=sys.stderr)
    html = fetch_url(archive_url, timeout=120)
    if not html:
        return []

    article_urls: list[str] = []
    seen: set[str] = set()
    for href in re.findall(r'href="(https://ojs\.aaai\.org/index\.php/AAAI/article/view/\d+[^"]*)"', html):
        clean = href.split("#", 1)[0]
        if clean not in seen:
            seen.add(clean)
            article_urls.append(clean)
        if len(article_urls) >= max_per_venue:
            break

    papers: list[dict] = []
    for article_url in article_urls:
        page = fetch_url(article_url, timeout=60)
        if not page:
            continue
        title = (_meta(page, "citation_title") or [""])[0]
        authors = ", ".join(_meta(page, "citation_author"))
        abstract = (_meta(page, "description") or _meta(page, "citation_abstract") or [""])[0]
        pdf = (_meta(page, "citation_pdf_url") or [""])[0]
        doi = (_meta(page, "citation_doi") or [""])[0]

        if not title:
            tm = re.search(r"<title>([^<]+)</title>", page, re.IGNORECASE)
            title = unescape(tm.group(1)).strip() if tm else article_url

        paper = {
            "title": title,
            "authors": authors,
            "affiliations": "",
            "abstract": abstract,
            "url": article_url,
            "pdf": pdf,
            "date": f"{year}-02-01",
            "score": 0,
            "category": "conference",
            "source": source_tag,
            "conference": venue,
            "year": year,
            "track": "main",
            "doi": doi,
            "paper_id": f"aaai:{article_url.rsplit('/', 1)[-1]}",
        }
        paper["score"] = score_paper(paper, is_trending=False)
        if paper["score"] >= 0:
            papers.append(paper)

    print(f"    -> {len(papers)} AAAI papers ({year})", file=sys.stderr)
    return papers
