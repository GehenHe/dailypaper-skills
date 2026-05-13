#!/usr/bin/env python3
"""CVF Open Access listings (CVPR, ICCV, ECCV)."""

from __future__ import annotations

import re
import sys
from html import unescape
from typing import Callable

from .common import extract_arxiv_id_from_text


def _cvf_key(venue: str, year: int) -> str:
    return f"{venue}{year}"


def fetch_cvf_venue(
    venue: str,
    year: int,
    max_per_venue: int,
    fetch_url: Callable[[str, int], str],
    score_paper: Callable[[dict, bool], int],
    folder_label: str,
    source_tag: str,
) -> list[dict]:
    key = _cvf_key(venue, year)
    index_url = f"https://openaccess.thecvf.com/{key}?day=all"
    print(f"  CVF {index_url} ...", file=sys.stderr)
    html = fetch_url(index_url, timeout=120)
    if not html:
        return []

    # Paper HTML pages + anchor text as title
    pat = re.compile(
        rf'href="(/content/{re.escape(key)}/html/[^"#]+\.html)"[^>]*>([^<]+)</a>',
        re.IGNORECASE,
    )
    seen: set[str] = set()
    papers: list[dict] = []
    for m in pat.finditer(html):
        if len(papers) >= max_per_venue:
            break
        path, title_raw = m.group(1), m.group(2)
        path = path.strip()
        title = unescape(re.sub(r"\s+", " ", title_raw)).strip()
        if not path or not title or path in seen:
            continue
        seen.add(path)

        page_url = f"https://openaccess.thecvf.com{path}"
        page_html = fetch_url(page_url, timeout=60)
        abstract = ""
        pdf_url = ""
        if page_html:
            pm = re.search(r'href="([^"]+\.pdf)"', page_html)
            if pm:
                pdf_href = pm.group(1)
                pdf_url = (
                    pdf_href
                    if pdf_href.startswith("http")
                    else f"https://openaccess.thecvf.com{pdf_href}"
                )
            am = re.search(
                r'<div id="abstract"[^>]*>\s*<blockquote[^>]*>(.*?)</blockquote>',
                page_html,
                re.DOTALL | re.IGNORECASE,
            )
            if am:
                abstract = re.sub(r"<[^>]+>", " ", am.group(1))
                abstract = unescape(re.sub(r"\s+", " ", abstract)).strip()

        aid = extract_arxiv_id_from_text((page_html or "") + " " + pdf_url)
        if aid:
            abs_url = f"https://arxiv.org/abs/{aid}"
            if not pdf_url:
                pdf_url = f"https://arxiv.org/pdf/{aid}"
        else:
            abs_url = page_url

        paper = {
            "title": title,
            "authors": "",
            "affiliations": "",
            "abstract": abstract,
            "url": abs_url,
            "pdf": pdf_url or abs_url,
            "date": f"{year}-06-01",
            "score": 0,
            "category": "conference",
            "source": source_tag,
            "conference": venue,
            "year": year,
            "track": "main",
            "cvf_paper_path": path,
            "paper_id": f"cvf:{path}",
        }
        paper["score"] = score_paper(paper, is_trending=False)
        if paper["score"] >= 0:
            papers.append(paper)

    print(f"    → {len(papers)} papers", file=sys.stderr)
    return papers
