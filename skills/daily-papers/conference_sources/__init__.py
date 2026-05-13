#!/usr/bin/env python3
"""Official top-conference paper fetchers (OpenReview, CVF, ACL, …)."""

from __future__ import annotations

import sys
from typing import Callable

from . import aaai, acm_mm, acl, cvf, openreview

FetchFn = Callable[[str, int], str]


def fetch_conference_papers(
    *,
    venues: list[str],
    years: list[int],
    max_per_venue: int,
    fetch_url: FetchFn,
    score_paper: Callable[[dict, bool], int],
    venue_folder_label_fn: Callable[[str], str],
) -> list[dict]:
    """Return normalized paper dicts for all (venue, year) pairs."""
    out: list[dict] = []
    for venue in venues:
        v = venue.strip()
        if not v:
            continue
        for year in years:
            y = int(year)
            label = venue_folder_label_fn(v)
            src = f"conference-{label.lower()}"
            try:
                if v in openreview.OPENREVIEW_VENUES:
                    batch = openreview.fetch_openreview_venue(
                        v, y, max_per_venue, fetch_url, score_paper, label, src
                    )
                elif v in ("CVPR", "ICCV", "ECCV"):
                    batch = cvf.fetch_cvf_venue(v, y, max_per_venue, fetch_url, score_paper, label, src)
                elif v == "ACL":
                    batch = acl.fetch_acl_main(v, y, max_per_venue, fetch_url, score_paper, label, src)
                elif v == "AAAI":
                    batch = aaai.fetch_aaai(v, y, max_per_venue, fetch_url, score_paper, label, src)
                elif v in ("ACM MM", "ACMMM"):
                    batch = acm_mm.fetch_acm_mm(v, y, max_per_venue, fetch_url, score_paper, label, src)
                else:
                    print(f"  [WARN] Unknown conference venue: {v}", file=sys.stderr)
                    batch = []
            except Exception as e:  # noqa: BLE001
                print(f"  [WARN] conference fetch failed {v} {y}: {e}", file=sys.stderr)
                batch = []
            out.extend(batch)
    return out
