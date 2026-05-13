#!/usr/bin/env python3
"""ACL main proceedings via ACL Anthology volume pages."""

from __future__ import annotations

import re
import sys
from html import unescape
from typing import Callable

from .common import extract_arxiv_id_from_text


def _acl_volume_ids(year: int) -> list[str]:
    return [f"{year}.acl-long", f"{year}.acl-short"]


def fetch_acl_main(
    venue: str,
    year: int,
    max_per_venue: int,
    fetch_url: Callable[[str, int], str],
    score_paper: Callable[[dict, bool], int],
    folder_label: str,
    source_tag: str,
) -> list[dict]:
    papers: list[dict] = []
    for vol in _acl_volume_ids(year):
        if len(papers) >= max_per_venue:
            break
        vol_url = f"https://aclanthology.org/volumes/{vol}/"
        print(f"  ACL Anthology {vol_url} ...", file=sys.stderr)
        html = fetch_url(vol_url, timeout=120)
        if not html:
            continue

        # Paper anchors: /2024.acl-long.1/
        for m in re.finditer(r'href="/(20\d{2}\.acl-(?:long|short)\.\d+)/"', html):
            if len(papers) >= max_per_venue:
                break
            pid = m.group(1)
            purl = f"https://aclanthology.org/{pid}/"
            page = fetch_url(purl, timeout=60)
            title = ""
            abstract = ""
            pdf_url = ""
            authors = ""
            if page:
                tm = re.search(r"<title>([^<|]+)", page)
                if tm:
                    title = unescape(tm.group(1)).strip()
                am = re.search(
                    r'<div class="card-body acl-abstract">(.*?)</div>',
                    page,
                    re.DOTALL | re.IGNORECASE,
                )
                if am:
                    abstract = re.sub(r"<[^>]+>", " ", am.group(1))
                    abstract = unescape(re.sub(r"\s+", " ", abstract)).strip()
                pdfm = re.search(r'href="(https://aclanthology.org/[^"]+\.pdf)"', page)
                if pdfm:
                    pdf_url = pdfm.group(1)
                # authors in <meta content="..." name="citation_author"
                auth_blocks = re.findall(
                    r'<meta\s+name="citation_author"\s+content="([^"]+)"',
                    page,
                    re.IGNORECASE,
                )
                if auth_blocks:
                    authors = ", ".join(auth_blocks)

            aid = extract_arxiv_id_from_text((page or "") + " " + abstract)
            if aid:
                abs_url = f"https://arxiv.org/abs/{aid}"
                if not pdf_url:
                    pdf_url = f"https://arxiv.org/pdf/{aid}"
            else:
                abs_url = purl

            paper = {
                "title": title or pid,
                "authors": authors,
                "affiliations": "",
                "abstract": abstract,
                "url": abs_url,
                "pdf": pdf_url or abs_url,
                "date": f"{year}-07-01",
                "score": 0,
                "category": "conference",
                "source": source_tag,
                "conference": venue,
                "year": year,
                "track": "main",
                "acl_anthology_id": pid,
                "paper_id": f"acl:{pid}",
            }
            paper["score"] = score_paper(paper, is_trending=False)
            if paper["score"] >= 0:
                papers.append(paper)

    print(f"    → {len(papers)} ACL papers ({year})", file=sys.stderr)
    return papers
