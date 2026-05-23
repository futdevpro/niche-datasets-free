#!/usr/bin/env python3
"""
Generate /tiers.html — cross-dataset reference of all derived enum tiers.

Scans sibling repo's datasets/<name>/config.json files, collects every
type:enum field (skipping core auto-fields), groups by dataset, and
cross-references where tiers are shared across multiple datasets.

Run from repo root:  python3 scripts/build-tiers.py
"""

from __future__ import annotations

import datetime
import json
import os
from collections import defaultdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent  # niche-datasets-free
SIBLING_DATASETS = REPO_ROOT.parent / "niche-datasets" / "datasets"
OUTPUT = REPO_ROOT / "tiers.html"

# Core auto-fields shared by every dataset — not interesting as differentiators.
SKIP_FIELDS = {
    "category", "pricing", "urlDomainTier", "categorizationTier",
    "descriptionLengthTier",
}

ALL_DATASETS = [
    "ai-agents", "ai-models-pricing", "ai-prompts", "ai-tools",
    "cybersecurity-tools", "design-resources", "developer-tools",
    "homebrew-packages", "huggingface-datasets", "huggingface-models",
    "llmops-and-eval", "mcp-servers", "no-code-lowcode", "npm-packages",
    "open-source-alternatives", "platform-engineering", "public-apis",
    "self-hosted-software", "vector-db-and-rag", "vscode-extensions",
]


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;")


def collect_data() -> tuple[dict[str, list[dict]], dict[str, list[str]]]:
    """Returns (per_dataset_enums, shared_tiers_by_name)."""
    data: dict[str, list[dict]] = {}
    for ds in sorted(os.listdir(SIBLING_DATASETS)):
        cfg_path = SIBLING_DATASETS / ds / "config.json"
        if not cfg_path.is_file():
            continue
        try:
            cfg = json.loads(cfg_path.read_text())
        except Exception:
            continue
        enums: list[dict] = []
        for fld in cfg.get("schema", {}).get("fields", []):
            if fld.get("type") == "enum" and fld.get("name") not in SKIP_FIELDS:
                enums.append({"name": fld["name"], "values": fld.get("values", [])})
        if enums:
            data[ds] = enums
    share: dict[str, list[str]] = defaultdict(list)
    for ds, enums in data.items():
        for e in enums:
            share[e["name"]].append(ds)
    return data, dict(share)


HEAD = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>All Semantic Enum Tiers — Cross-Dataset Filter Reference</title>
<meta name="description" content="Complete reference of every derived semantic enum tier across 20 niche datasets. 10+ shared tiers + 40+ dataset-specific tiers. Filter once, answer everywhere.">
<link rel="canonical" href="https://futdevpro.github.io/niche-datasets-free/tiers.html">
<link rel="alternate" type="application/rss+xml" title="Niche Datasets — Refresh Feed" href="feed.xml">
<link rel="alternate" type="application/json" title="Niche Datasets — Catalog" href="datasets.json">
<meta property="og:type" content="article">
<meta property="og:url" content="https://futdevpro.github.io/niche-datasets-free/tiers.html">
<meta property="og:title" content="All Semantic Enum Tiers — Cross-Dataset Filter Reference">
<meta property="og:description" content="10+ shared + 40+ dataset-specific derived enum tiers. Complete filter reference across 20 datasets.">
<meta property="og:site_name" content="Niche Datasets">
<meta property="og:image" content="https://futdevpro.github.io/niche-datasets-free/og-cover.svg">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="All Semantic Enum Tiers — Filter Reference">
<meta name="twitter:description" content="50+ enum tiers across 20 datasets, fully documented.">
<meta name="twitter:image" content="https://futdevpro.github.io/niche-datasets-free/og-cover.svg">
<style>
  body{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;max-width:920px;margin:0 auto;padding:2rem 1.25rem;line-height:1.55;color:#1a1a1a}
  h1{font-size:1.7rem;margin-bottom:.4rem}
  h2{font-size:1.2rem;margin-top:2.2rem;color:#0969da;border-bottom:1px solid #eee;padding-bottom:.3rem}
  h3{font-size:1.05rem;margin-top:1.4rem;color:#222}
  a{color:#0969da}
  code{background:#f4f4f4;padding:.1rem .3rem;border-radius:3px;font-size:.9em;font-family:Menlo,Consolas,monospace}
  .lead{color:#444;font-size:1.05rem}
  .nav{font-size:.9rem;color:#666;margin-bottom:1rem}
  table{border-collapse:collapse;width:100%;font-size:.92rem;margin:.8rem 0}
  th,td{border:1px solid #e5e7eb;padding:.42rem .6rem;text-align:left;vertical-align:top}
  thead{background:#f6f8fa}
  .shared{background:#e6f4ff}
  .ds-block{background:#fafbfc;padding:1rem 1.2rem;border-left:3px solid #0969da;border-radius:0 4px 4px 0;margin:1.2rem 0}
  .ds-block h3{margin-top:0}
  .enum-list{font-size:.92rem;color:#444}
  .enum-list li{margin:.25rem 0}
  .badge{display:inline-block;background:#16a34a;color:white;padding:.05rem .4rem;border-radius:3px;font-size:.8em;margin-left:.4rem;vertical-align:middle}
  footer{margin-top:3rem;padding-top:1rem;border-top:1px solid #eee;font-size:.85rem;color:#666}
</style>
<script type="application/ld+json">
{"@context":"https://schema.org","@type":"TechArticle","headline":"All Semantic Enum Tiers — Cross-Dataset Filter Reference","datePublished":"2026-05-21","dateModified":"__TODAY__","author":{"@type":"Organization","name":"Niche Datasets"},"publisher":{"@type":"Organization","name":"Niche Datasets","url":"https://futdevpro.github.io/niche-datasets-free/"},"mainEntityOfPage":"https://futdevpro.github.io/niche-datasets-free/tiers.html","image":"https://futdevpro.github.io/niche-datasets-free/og-cover.svg","description":"Complete enum-tier reference across 20 niche datasets."}
</script>
<script type="application/ld+json">
{"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[{"@type":"ListItem","position":1,"name":"Home","item":"https://futdevpro.github.io/niche-datasets-free/"},{"@type":"ListItem","position":2,"name":"All Tiers","item":"https://futdevpro.github.io/niche-datasets-free/tiers.html"}]}
</script>
</head>
<body>

<p class="nav"><a href="./">Home</a> | <a href="quickstart.html">Quickstart</a> | <a href="buyers-guide.html">Buyer guide</a> | <a href="api.html">API</a> | <a href="blog-semantic-enum-tiers.html">Tier methodology</a> | <a href="faq.html">FAQ</a></p>

<h1>All Semantic Enum Tiers</h1>
<p class="lead">Every derived enum-tier field in the catalog, grouped by dataset and cross-referenced where tiers are shared across multiple datasets. Filter syntax is identical across datasets when the enum name matches.</p>
<p>Methodology behind these tiers: <a href="blog-semantic-enum-tiers.html">Semantic enum tiers post</a>.</p>
"""


def render(data: dict[str, list[dict]], share: dict[str, list[str]]) -> str:
    today_iso = datetime.date.today().isoformat()
    out: list[str] = [HEAD.replace("__TODAY__", today_iso)]

    total_tier_fields = sum(len(v) for v in data.values())
    shared_count = sum(1 for v in share.values() if len(v) >= 2)
    no_tier_count = len(ALL_DATASETS) - len(data)
    out.append('<h2 id="at-a-glance">At a glance</h2>')
    out.append("<table><thead><tr><th>Stat</th><th>Value</th></tr></thead><tbody>")
    out.append(
        f'<tr><td>Datasets with derived enum tiers</td>'
        f'<td><strong>{len(data)}</strong> of {len(ALL_DATASETS)}</td></tr>'
    )
    out.append(
        f'<tr><td>Total tier-fields across the catalog</td>'
        f'<td><strong>{total_tier_fields}</strong></td></tr>'
    )
    out.append(
        f'<tr><td>Shared tiers (used in 2+ datasets)</td>'
        f'<td><strong>{shared_count}</strong></td></tr>'
    )
    out.append(
        f'<tr><td>Datasets without tiers (awesome-list mirrors, mostly)</td>'
        f'<td><strong>{no_tier_count}</strong></td></tr>'
    )
    if data:
        densest = max(data.items(), key=lambda kv: len(kv[1]))
        out.append(
            f'<tr><td>Most tier-dense dataset</td>'
            f'<td><a href="{densest[0]}.html">{densest[0]}</a> ({len(densest[1])} tiers)</td></tr>'
        )
    out.append("</tbody></table>")

    out.append('<h2 id="recently-added">Recently added (2026-05-21)</h2>')
    out.append('<ul class="enum-list">')
    out.append(
        '<li><code>vendorTier</code> on <a href="cybersecurity-tools.html">cybersecurity-tools</a> '
        '— buyer-aligned <code>oss</code> / <code>commercial</code> / <code>dual</code> / <code>freeware</code> / <code>unknown</code> '
        'derived from <code>isOpenSource × pricing</code> + text-pattern detection (open-core, '
        'community+enterprise, AGPL+commercial).</li>'
    )
    out.append(
        '<li><code>licenseTier</code> on <a href="open-source-alternatives.html">open-source-alternatives</a> '
        '— now matches the same enum across <a href="huggingface-models.html">HF models</a>, '
        '<a href="huggingface-datasets.html">HF datasets</a>, <a href="npm-packages.html">npm</a>, '
        'and <a href="homebrew-packages.html">Homebrew</a> (5 datasets total share this enum).</li>'
    )
    out.append(
        '<li><code>useCaseTier</code> on <a href="ai-models-pricing.html">ai-models-pricing</a> '
        '(2026-05-20) — completes the cross-symmetric trio with <a href="huggingface-models.html">HF '
        'models</a> and <a href="huggingface-datasets.html">HF datasets</a>. <code>useCaseTier=code</code> '
        'now filters all three consistently.</li>'
    )
    out.append("</ul>")
    out.append("<p>See <a href=\"blog-semantic-enum-tiers.html\">tier methodology</a> for the design rules.</p>")

    out.append('<h2 id="shared">Shared tiers (same enum across 2+ datasets)</h2>')
    out.append("<p>A query like <code>useCaseTier=code</code> returns matching records consistently across all listed datasets.</p>")
    out.append("<table><thead><tr><th>Tier name</th><th>Datasets that ship it</th><th>x</th></tr></thead><tbody>")
    shared_sorted = sorted(
        [(k, v) for k, v in share.items() if len(v) >= 2],
        key=lambda x: -len(x[1]),
    )
    for name, datasets in shared_sorted:
        ds_links = " | ".join(f'<a href="{ds}.html">{ds}</a>' for ds in sorted(datasets))
        out.append(
            f'<tr class="shared"><td><code>{esc(name)}</code></td>'
            f'<td>{ds_links}</td><td>{len(datasets)}</td></tr>'
        )
    out.append("</tbody></table>")

    out.append('<h2 id="per-dataset">Per-dataset enum tiers</h2>')
    out.append("<p>Each dataset lists every <em>derived</em> enum field (the source API does not expose these directly; the pipeline computes them).</p>")
    for ds in sorted(data.keys()):
        enums = data[ds]
        if not enums:
            continue
        out.append('<div class="ds-block">')
        out.append(
            f'<h3><a href="{ds}.html">{ds}</a> <span class="badge">{len(enums)} tiers</span></h3>'
        )
        out.append('<ul class="enum-list">')
        for e in enums:
            is_shared = (
                ' <span class="badge">shared</span>'
                if len(share.get(e["name"], [])) > 1 else ""
            )
            vals = " / ".join(f"<code>{esc(v)}</code>" for v in e["values"])
            out.append(
                f'<li><code>{esc(e["name"])}</code>{is_shared}<br>'
                f'<span style="font-size:.85em;color:#555">to {vals}</span></li>'
            )
        out.append("</ul></div>")

    no_enum = [d for d in ALL_DATASETS if d not in data]
    if no_enum:
        out.append('<h2 id="no-tiers">Datasets without derived enum tiers (yet)</h2>')
        out.append("<p>These are mostly awesome-list mirrors where the source data does not have enough structure to derive meaningful semantic tiers without LLM enrichment. Adding tiers to these is on the roadmap.</p>")
        out.append("<ul>")
        for ds in no_enum:
            out.append(f'<li><a href="{ds}.html">{ds}</a></li>')
        out.append("</ul>")

    out.append('<p><a href="./">Browse all 20 datasets</a></p>')
    out.append('<footer>Niche Datasets | <a href="https://github.com/futdevpro/niche-datasets-free">GitHub repo</a> | <a href="https://jhonnyronnie.gumroad.com/">Gumroad storefront</a> | <a href="blog-semantic-enum-tiers.html">Tier methodology</a></footer>')
    out.append("</body>\n</html>\n")
    return "\n".join(out)


def main() -> int:
    data, share = collect_data()
    OUTPUT.write_text(render(data, share))
    shared_count = sum(1 for v in share.values() if len(v) >= 2)
    total_tiers = sum(len(v) for v in data.values())
    print(
        f"Wrote {OUTPUT} — {len(data)} datasets with tiers, "
        f"{total_tiers} total tier-fields, {shared_count} shared, "
        f"{len(ALL_DATASETS) - len(data)} datasets without tiers."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
