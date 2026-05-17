#!/usr/bin/env python3
"""
Generate /vs.html — comparison page positioning Niche Datasets against the
common alternatives: awesome-* GitHub lists, Kaggle datasets, HuggingFace
datasets hub, ProductHunt, and ad-hoc Google searching.

Targets long-tail comparison queries like 'awesome-list vs structured dataset',
'kaggle alternative for developer tools', 'huggingface vs custom dataset', etc.

Run from repo root:  python3 scripts/build-vs.py
"""
import json
import os


COMPARISONS = [
    {
        "alt": "awesome-* GitHub lists",
        "use_case": "Browsing curated link collections for a tooling area you're new to.",
        "good_at": "Discovery + community moderation. Free, accessible, well-known.",
        "weak_at": "Unstructured markdown — can't filter, sort, group, or join. No enrichment fields (downloads, stars, pricing, freshness). Stale links accumulate. Schema inconsistent across lists.",
        "vs_us": "Niche Datasets normalize the same awesome-list source material into JSON+CSV with consistent schema + 40+ semantic enum tiers + per-record enrichment (GitHub stars, install counts, pricing, etc.). You can <code>filter / sort / join</code> across the catalog instead of bullet-scrolling.",
    },
    {
        "alt": "Kaggle datasets",
        "use_case": "ML competition data, public datasets for training, kaggle-hosted notebooks.",
        "good_at": "Huge dataset library, integrated notebooks, competitions.",
        "weak_at": "Mostly aimed at academic / competition ML — not developer tooling catalogs. Browsing is awkward without a Kaggle account. License + freshness vary wildly. Few catalogs of <em>tools</em> (most entries are domain-specific data: medical, finance, NLP corpora, etc.).",
        "vs_us": "Niche Datasets focus specifically on <strong>developer + AI tooling catalogs</strong> — npm packages, MCP servers, AI agent frameworks, vector DBs, etc. — not training data. Each dataset is monthly/quarterly refreshed from canonical APIs (npm registry, HuggingFace Hub, OpenRouter, Homebrew API). Buy-one-download model, no Kaggle account required.",
    },
    {
        "alt": "HuggingFace datasets hub",
        "use_case": "Pre-processed training datasets for fine-tuning + evaluation.",
        "good_at": "Massive selection of ML training data with built-in loaders + previews + size info.",
        "weak_at": "Datasets are about ML <em>inputs</em> (sentences, images, audio). Not catalogs of <em>tools</em> or <em>infrastructure</em>. Discovery for non-ML-data niche (devops tooling, no-code, design resources) is poor.",
        "vs_us": "Niche Datasets are <strong>directory-style catalogs of tools and platforms</strong>, not training corpora. We also ship a 2,600+ HuggingFace Datasets directory — meta-catalog of what's <em>on</em> HuggingFace, normalized + filterable by license + task category + modality + language — useful when you want to <em>browse the universe of HuggingFace datasets</em> from a CSV instead of paginating their hub UI.",
    },
    {
        "alt": "ProductHunt",
        "use_case": "Discovering new launches of consumer SaaS / dev tools.",
        "good_at": "Daily feed of brand-new products, social proof via upvotes + comments.",
        "weak_at": "Recency-biased — focuses on launch day, not the long tail of established tools. Description quality varies. No structured filtering by category / pricing / API availability / license.",
        "vs_us": "Niche Datasets cover the <strong>established universe</strong> (npm packages going back years, Homebrew formulae with install counts, MCP servers across all categories). Structured pricing buckets, hasApi flags, semantic tiers. Designed for 'I need to know what already exists in X' research, not 'what launched this week'.",
    },
    {
        "alt": "Ad-hoc Google searching",
        "use_case": "Finding a specific tool or comparing 2-3 you already know about.",
        "good_at": "Fast for known-item lookups. Ranks freshest + most-linked results.",
        "weak_at": "Bad for enumerating a space ('all MCP servers', 'all vector DBs'). SEO-optimized pages bury the long tail. AI Overview answers are often wrong about niche topics with limited training data.",
        "vs_us": "Niche Datasets are the <strong>exhaustive enumeration</strong>: 12,200+ Homebrew formulae, 6,000+ npm packages, 3,600+ MCP servers, 4,000 HuggingFace models, etc. You get the full set in one CSV/JSON instead of 50 Google tabs. Especially valuable when building an internal 'approved tools' catalog or training data for an AI Q&A agent about a tooling space.",
    },
    {
        "alt": "Paying for a custom data scrape",
        "use_case": "When you really need a specific catalog and can pay a contractor to build it.",
        "good_at": "Bespoke: exactly what you ask for, freshly scraped, sometimes with extra fields.",
        "weak_at": "$$$ ($500-$5000+ per catalog). One-shot — no ongoing refresh unless you keep paying. Quality depends entirely on the contractor's experience with the source.",
        "vs_us": "Niche Datasets are <strong>$7-$14 per dataset, $24-$34 for bundles, $0 for samples</strong>. Monthly/quarterly refresh built in (price already covers it). 20 catalogs already exist; if yours is one of them, you're done in 5 seconds instead of 2 weeks.",
    },
]


PAGE_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Niche Datasets vs. Alternatives — awesome-lists, Kaggle, HuggingFace, ProductHunt, Custom Scrapes</title>
<meta name="description" content="How the Niche Datasets catalog compares to the common alternatives — awesome-* GitHub lists, Kaggle, HuggingFace datasets hub, ProductHunt, ad-hoc Google search, custom contractor scrapes. When to use which.">
<link rel="canonical" href="https://futdevpro.github.io/niche-datasets-free/vs.html">
<link rel="alternate" type="application/rss+xml" title="Niche Datasets — Refresh Feed" href="feed.xml">
<link rel="alternate" type="application/json" title="Niche Datasets — Catalog" href="datasets.json">
<meta property="og:type" content="website">
<meta property="og:url" content="https://futdevpro.github.io/niche-datasets-free/vs.html">
<meta property="og:title" content="Niche Datasets vs. Alternatives — awesome-lists, Kaggle, HuggingFace, ProductHunt, Custom Scrapes">
<meta property="og:description" content="How the Niche Datasets catalog compares to awesome-* lists, Kaggle, HuggingFace datasets, ProductHunt, ad-hoc Google search, custom scrapes. When to use which.">
<meta property="og:site_name" content="Niche Datasets">
<meta property="og:image" content="https://futdevpro.github.io/niche-datasets-free/og-cover.svg">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="Niche Datasets vs. Alternatives">
<meta name="twitter:description" content="Compared to awesome-lists, Kaggle, HuggingFace, ProductHunt, ad-hoc Google, custom scrapes. When to use which.">
<meta name="twitter:image" content="https://futdevpro.github.io/niche-datasets-free/og-cover.svg">
<style>
  body{{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;max-width:880px;margin:0 auto;padding:2rem 1.25rem;line-height:1.55;color:#1a1a1a}}
  h1{{font-size:1.7rem;margin-bottom:.25rem}}
  h2{{font-size:1.15rem;margin-top:2.4rem;color:#0969da;border-bottom:1px solid #eee;padding-bottom:.3rem}}
  h3{{font-size:.95rem;margin-top:1.2rem;margin-bottom:.4rem;color:#444;text-transform:uppercase;letter-spacing:.04em}}
  a{{color:#0969da}}
  code{{background:#f4f4f4;padding:.1rem .3rem;border-radius:3px;font-size:.9em}}
  .lead{{color:#444}}
  .nav{{font-size:.9rem;color:#666;margin-bottom:1rem}}
  .row p{{margin:.4rem 0}}
  .vs{{background:#fafbfc;padding:.85rem 1.1rem;border-left:3px solid #0969da;border-radius:0 4px 4px 0;margin-top:.8rem}}
  footer{{margin-top:3rem;padding-top:1rem;border-top:1px solid #eee;font-size:.85rem;color:#666}}
</style>
</head>
<body>

<p class="nav"><a href="./">← All 20 datasets</a> &nbsp;·&nbsp; <a href="examples.html">Code examples</a> &nbsp;·&nbsp; <a href="faq.html">FAQ</a></p>

<h1>Niche Datasets vs. the alternatives</h1>
<p class="lead">Honest comparison to the 6 places people normally look for tooling catalogs — awesome-* lists, Kaggle, HuggingFace datasets hub, ProductHunt, ad-hoc Google search, and paid custom scrapes. Each has its place; this page maps when to reach for which.</p>

{comparisons_html}

<h2>TL;DR — when to use Niche Datasets</h2>
<p>You want a <strong>structured enumeration of a developer or AI tooling space</strong> (npm, MCP servers, HuggingFace models, Homebrew formulae, vector DBs, AI agents, etc.) that you can filter / sort / join / repackage. Monthly-or-quarterly refresh, license-clean for commercial use, $7-$14 per dataset or $24-$34 in bundles. Free 20-record samples to evaluate the schema before buying.</p>

<p>You'd reach for an alternative if: you need <em>training data</em> (Kaggle / HuggingFace), <em>brand-new launches</em> (ProductHunt), or <em>a bespoke catalog</em> not in our list of 20 (custom scrape).</p>

<p><a class="cta" href="./">Browse the 20 datasets</a> &nbsp;·&nbsp; <a href="examples.html">Code examples for loading</a></p>

<footer>
Part of <a href="./">Niche Datasets — 20 curated developer and AI datasets</a>. Built by <a href="https://github.com/jhonny-ronnie">Ronnie J</a> at <a href="https://github.com/futdevpro">Future Development Program</a>. Free samples are MIT-style permissive for evaluation; full datasets per <a href="https://jhonnyronnie.gumroad.com">Gumroad terms</a>.
</footer>

<script type="application/ld+json">
{jsonld}
</script>

<script type="application/ld+json">
{breadcrumb_jsonld}
</script>

</body>
</html>
"""


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def build_comparisons_html():
    parts = []
    for c in COMPARISONS:
        alt_safe = esc(c["alt"])
        # use_case/good_at/weak_at/vs_us can contain inline HTML (code, em, strong) — don't escape
        parts.append(
            f"<h2>vs. {alt_safe}</h2>\n"
            f"<div class='row'>\n"
            f"  <h3>When to use it</h3>\n"
            f"  <p>{c['use_case']}</p>\n"
            f"  <h3>Good at</h3>\n"
            f"  <p>{c['good_at']}</p>\n"
            f"  <h3>Weak at</h3>\n"
            f"  <p>{c['weak_at']}</p>\n"
            f"  <div class='vs'><strong>Niche Datasets:</strong> {c['vs_us']}</div>\n"
            f"</div>"
        )
    return "\n\n".join(parts)


def build_jsonld():
    return json.dumps({
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": "Niche Datasets vs. Alternatives — awesome-lists, Kaggle, HuggingFace, ProductHunt, Custom Scrapes",
        "description": "How the Niche Datasets catalog compares to the common alternatives. When to use which.",
        "url": "https://futdevpro.github.io/niche-datasets-free/vs.html",
        "author": {"@type": "Organization", "name": "Future Development Program"},
        "publisher": {"@type": "Organization", "name": "Future Development Program",
                      "url": "https://github.com/futdevpro"},
        "keywords": ["awesome lists vs structured dataset", "kaggle alternative",
                     "huggingface datasets alternative", "developer dataset catalog",
                     "ml dataset catalog", "free vs paid dataset"],
        "about": ["data catalogs", "developer tools", "machine learning"],
    }, indent=2)


def build_breadcrumb_jsonld():
    return json.dumps({
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Niche Datasets",
             "item": "https://futdevpro.github.io/niche-datasets-free/"},
            {"@type": "ListItem", "position": 2, "name": "vs. Alternatives",
             "item": "https://futdevpro.github.io/niche-datasets-free/vs.html"},
        ],
    }, indent=2)


def main():
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    html = PAGE_TEMPLATE.format(
        comparisons_html=build_comparisons_html(),
        jsonld=build_jsonld(),
        breadcrumb_jsonld=build_breadcrumb_jsonld(),
    )
    path = os.path.join(repo_root, "vs.html")
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Wrote {path} with {len(COMPARISONS)} alternative comparisons.")


if __name__ == "__main__":
    main()
