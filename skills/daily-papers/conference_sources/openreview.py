#!/usr/bin/env python3
"""Fetch accepted papers from OpenReview (NeurIPS, ICLR, ICML, …)."""

from __future__ import annotations

import json
import sys
from typing import Callable
from urllib.parse import quote

from .common import extract_arxiv_id_from_text, or_content_value

# Venue display name → OpenReview group id (without .cc)
OPENREVIEW_VENUES: dict[str, str] = {
    "NeurIPS": "NeurIPS.cc",
    "ICLR": "ICLR.cc",
    "ICML": "ICML.cc",
}


def _venue_id(group: str, year: int) -> str:
    return f"{group}/{year}/Conference"


def fetch_openreview_venue(
    venue: str,
    year: int,
    max_per_venue: int,
    fetch_url: Callable[[str, int], str],
    score_paper: Callable[[dict, bool], int],
    folder_label: str,
    source_tag: str,
) -> list[dict]:
    group = OPENREVIEW_VENUES.get(venue)
    if not group:
        return []

    venueid = _venue_id(group, year)
    q = quote(venueid, safe="")
    offset = 0
    limit = 1000
    papers: list[dict] = []
    seen_forums: set[str] = set()

    print(f"  OpenReview {venue} {year} ({venueid})...", file=sys.stderr)

    while len(papers) < max_per_venue:
        url = (
            f"https://api2.openreview.net/notes?"
            f"content.venueid={q}&limit={limit}&offset={offset}"
        )
        raw = fetch_url(url, timeout=120)
        if not raw:
            break
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            print(f"  [WARN] OpenReview JSON error at offset {offset}", file=sys.stderr)
            break
        notes = data.get("notes") or []
        if not notes:
            break

        for note in notes:
            if len(papers) >= max_per_venue:
                break
            content = note.get("content") or {}
            if not isinstance(content, dict):
                continue
            title = or_content_value(content, "title").strip()
            abstract = or_content_value(content, "abstract").strip()
            if not title:
                continue

            pdf = or_content_value(content, "pdf").strip()
            forum = (note.get("forum") or note.get("id") or "").strip()
            if forum and forum in seen_forums:
                continue
            if forum:
                seen_forums.add(forum)

            authors = or_content_value(content, "authors").strip()
            aid = extract_arxiv_id_from_text(pdf + " " + abstract + " " + title)
            if aid:
                abs_url = f"https://arxiv.org/abs/{aid}"
                pdf_url = f"https://arxiv.org/pdf/{aid}"
            else:
                abs_url = f"https://openreview.net/forum?id={forum}" if forum else ""
                pdf_url = pdf if pdf.startswith("http") else ""

            paper = {
                "title": title,
                "authors": authors,
                "affiliations": "",
                "abstract": abstract,
                "url": abs_url or (f"https://openreview.net/forum?id={forum}" if forum else ""),
                "pdf": pdf_url,
                "date": f"{year}-01-01",
                "score": 0,
                "category": "conference",
                "source": source_tag,
                "conference": venue,
                "year": year,
                "track": "main",
                "openreview_forum": forum,
                "paper_id": f"or:{forum}" if forum else "",
            }
            paper["score"] = score_paper(paper, is_trending=False)
            if paper["score"] >= 0:
                papers.append(paper)

        if len(notes) < limit:
            break
        offset += limit

    print(f"    → {len(papers)} papers", file=sys.stderr)
    return papers
