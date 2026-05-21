#!/usr/bin/env python3
"""
Generate /changelog.html aggregating per-dataset CHANGELOG.md entries.

Reads from the sibling niche-datasets repo (../niche-datasets/datasets/<name>/
CHANGELOG.md). Picks the last 60 refresh events, groups by date, writes a
buyer-facing single-page reference with adds/updates/removes per dataset.

Run from repo root:  python3 scripts/build-changelog.py
"""

from __future__ import annotations

import datetime
import json
import os
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent  # niche-datasets-free
SIBLING_DATASETS = REPO_ROOT.parent / "niche-datasets" / "datasets"
OUTPUT = REPO_ROOT / "changelog.html"
LIMIT = 60


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;")


def collect_events() -> list[dict]:
    events: list[dict] = []
    if not SIBLING_DATASETS.is_dir():
        return events
    for ds in sorted(os.listdir(SIBLING_DATASETS)):
        cl_path = SIBLING_DATASETS / ds / "CHANGELOG.md"
        if not cl_path.is_file():
            continue
        text = cl_path.read_text()
        for m in re.finditer(
            r'## (\d{4}-\d{2}-\d{2})\n((?:- \*\*[^*]+:\*\* \d+ record\(s\)\s*\n?)+)',
            text,
        ):
            stats: dict[str, int] = {}
            for sm in re.finditer(
                r'- \*\*([^*]+):\*\*\s*(\d+)\s*record', m.group(2)
            ):
                stats[sm.group(1).lower().strip()] = int(sm.group(2))
            events.append({
                "date": m.group(1),
                "dataset": ds,
                "added": stats.get("added", 0),
                "updated": stats.get("updated", 0),
                "removed": stats.get("removed", 0),
            })
    events.sort(key=lambda e: (e["date"], e["dataset"]), reverse=True)
    return events[:LIMIT]


HEAD = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Changelog — Recent Refreshes Across 20 Niche Datasets</title>
<meta name="description" content="Last 60 dataset-refresh events across the 20-dataset catalog. Adds, updates, removes per dataset per date. Demonstrates ongoing-maintenance signal and per-source refresh cadence.">
<link rel="canonical" href="https://futdevpro.github.io/niche-datasets-free/changelog.html">
<link rel="alternate" type="application/rss+xml" title="Niche Datasets — Refresh Feed" href="feed.xml">
<meta property="og:type" content="article">
<meta property="og:url" content="https://futdevpro.github.io/niche-datasets-free/changelog.html">
<meta property="og:title" content="Changelog — Recent Refreshes Across 20 Niche Datasets">
<meta property="og:description" content="Last 60 dataset-refresh events with adds/updates/removes per dataset per date.">
<meta property="og:site_name" content="Niche Datasets">
<meta property="og:image" content="https://futdevpro.github.io/niche-datasets-free/og-cover.svg">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="Changelog — Recent Refreshes">
<meta name="twitter:description" content="Last 60 dataset-refresh events. Adds/updates/removes per dataset.">
<meta name="twitter:image" content="https://futdevpro.github.io/niche-datasets-free/og-cover.svg">
<style>
  body{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;max-width:920px;margin:0 auto;padding:2rem 1.25rem;line-height:1.55;color:#1a1a1a}
  h1{font-size:1.7rem;margin-bottom:.4rem}
  h2{font-size:1.15rem;margin-top:2rem;color:#0969da;border-bottom:1px solid #eee;padding-bottom:.3rem}
  a{color:#0969da}
  code{background:#f4f4f4;padding:.1rem .3rem;border-radius:3px;font-size:.9em;font-family:Menlo,Consolas,monospace}
  .lead{color:#444;font-size:1.05rem}
  .nav{font-size:.9rem;color:#666;margin-bottom:1rem}
  table{border-collapse:collapse;width:100%;font-size:.92rem;margin:.8rem 0}
  th,td{border:1px solid #e5e7eb;padding:.42rem .6rem;text-align:right}
  th:nth-child(-n+2),td:nth-child(-n+2){text-align:left}
  thead{background:#f6f8fa}
  .pos{color:#16a34a}.neg{color:#b91c1c}.zero{color:#999}
  footer{margin-top:3rem;padding-top:1rem;border-top:1px solid #eee;font-size:.85rem;color:#666}
</style>
<script type="application/ld+json">
{"@context":"https://schema.org","@type":"TechArticle","headline":"Changelog — Recent Refreshes Across 20 Niche Datasets","datePublished":"2026-05-21","dateModified":"__TODAY__","author":{"@type":"Organization","name":"Niche Datasets"},"publisher":{"@type":"Organization","name":"Niche Datasets","url":"https://futdevpro.github.io/niche-datasets-free/"},"mainEntityOfPage":"https://futdevpro.github.io/niche-datasets-free/changelog.html","image":"https://futdevpro.github.io/niche-datasets-free/og-cover.svg","description":"Last 60 dataset-refresh events across the catalog."}
</script>
<script type="application/ld+json">
{"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[{"@type":"ListItem","position":1,"name":"Home","item":"https://futdevpro.github.io/niche-datasets-free/"},{"@type":"ListItem","position":2,"name":"Changelog","item":"https://futdevpro.github.io/niche-datasets-free/changelog.html"}]}
</script>
</head>
<body>

<p class="nav"><a href="./">Home</a> | <a href="quickstart.html">Quickstart</a> | <a href="buyers-guide.html">Buyer guide</a> | <a href="api.html">API</a> | <a href="tiers.html">All tiers</a> | <a href="faq.html">FAQ</a></p>

<h1>Changelog</h1>
<p class="lead">Last __LIMIT__ dataset-refresh events across the 20-dataset catalog. Demonstrates per-source refresh cadence + ongoing-maintenance signal. Subscribe to <a href="feed.xml">/feed.xml</a> for live updates.</p>

<p>For commentary on the 2026-05-20 sprint, see the <a href="blog-2026-05-20-13-day-refresh.html">13-day refresh report</a>.</p>
"""


def render(events: list[dict]) -> str:
    today_iso = datetime.date.today().isoformat()
    out: list[str] = [
        HEAD.replace("__LIMIT__", str(len(events)))
            .replace("__TODAY__", today_iso)
    ]
    by_date: dict[str, list[dict]] = {}
    for e in events:
        by_date.setdefault(e["date"], []).append(e)
    for date in sorted(by_date.keys(), reverse=True):
        rows = by_date[date]
        out.append(f"<h2>{date}</h2>")
        out.append('<table><thead><tr><th>Dataset</th><th>+ Added</th><th>~ Updated</th><th>- Removed</th><th>Net</th></tr></thead><tbody>')
        tot_a = tot_u = tot_r = 0
        for r in sorted(rows, key=lambda x: -(x["added"] + x["removed"])):
            net = r["added"] - r["removed"]
            added_html = f'<span class="pos">+{r["added"]}</span>' if r["added"] else '<span class="zero">0</span>'
            removed_html = f'<span class="neg">-{r["removed"]}</span>' if r["removed"] else '<span class="zero">0</span>'
            updated_html = str(r["updated"]) if r["updated"] else '<span class="zero">0</span>'
            net_cls = "pos" if net > 0 else "neg" if net < 0 else "zero"
            net_str = f"+{net}" if net > 0 else str(net)
            out.append(
                f'<tr><td><a href="{r["dataset"]}.html">{r["dataset"]}</a></td>'
                f'<td>{added_html}</td><td>{updated_html}</td><td>{removed_html}</td>'
                f'<td><span class="{net_cls}">{net_str}</span></td></tr>'
            )
            tot_a += r["added"]; tot_u += r["updated"]; tot_r += r["removed"]
        net_total = tot_a - tot_r
        out.append(
            f'<tr style="background:#fafafa;font-weight:600"><td>Total ({len(rows)} datasets)</td>'
            f'<td class="pos">+{tot_a}</td><td>{tot_u}</td><td class="neg">-{tot_r}</td>'
            f'<td>{net_total:+d}</td></tr>'
        )
        out.append("</tbody></table>")
    out.append('''
<p><a href="./">Browse all 20 datasets</a></p>
<footer>Niche Datasets | <a href="https://github.com/futdevpro/niche-datasets-free">GitHub repo</a> | <a href="https://jhonnyronnie.gumroad.com/">Gumroad storefront</a> | <a href="feed.xml">RSS feed</a></footer>
</body>
</html>
''')
    return "\n".join(out) + "\n"


def main() -> int:
    events = collect_events()
    OUTPUT.write_text(render(events))
    print(f"Wrote {OUTPUT} with {len(events)} events across {len({e['date'] for e in events})} dates and {len({e['dataset'] for e in events})} datasets.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
