#!/usr/bin/env python3
"""
Generate /faq.html — schema.org FAQPage with 12 Q+A entries targeting long-tail
queries like "free dataset csv json sample", "where to download huggingface
models list", "open dataset for machine learning training".

Why: FAQPage is rich-result eligible (Google may show the Q+A directly in SERP),
and the questions themselves are query-keyword-dense. Adds another indexable
page to the link graph + opens long-tail entry points the per-dataset pages
don't directly cover.

Run from repo root:  python3 scripts/build-faq.py
"""
import json
import os

FAQS = [
    {
        "q": "Are these datasets really free?",
        "a": "Yes. The 20-record samples in this repo (one per dataset, JSON + CSV) are free to download and free to use for evaluation, prototyping, blog posts, and side projects. Permissively licensed (MIT-style) for the samples. The full datasets (the complete ~12,000 / 4,000 / 2,600 / etc. records) are paid via Gumroad — $7 to $14 per dataset, $24 to $34 for bundles."
    },
    {
        "q": "What formats are available?",
        "a": "Every dataset ships in both JSON and CSV. Same records, same schema. JSON is preferred when you'll parse programmatically (Python, JS, Go); CSV is easier when you'll load into a spreadsheet or BI tool. Records share a common base schema (name, url, description, category, pricing, hasApi, tags) plus dataset-specific first-class fields (e.g. weeklyDownloads for npm, installCount365d for Homebrew, downloads/likes/license for HuggingFace)."
    },
    {
        "q": "How fresh is the data?",
        "a": "Monthly refresh for ai-models-pricing (pricing decays fast). Quarterly for the other 19 datasets. Source-pulled from official APIs (npm registry, Homebrew API, HuggingFace Hub, OpenRouter, VS Code Marketplace) or maintained awesome-list repos — not scraped from third-party aggregators, so the data quality matches what you'd get pulling directly."
    },
    {
        "q": "Where does the data come from?",
        "a": "Each dataset is sourced from either (a) the official API for its ecosystem (npm registry for npm-packages, Homebrew API for homebrew-packages, HuggingFace Hub for huggingface-models and -datasets, OpenRouter for ai-models-pricing, VS Code Marketplace for vscode-extensions, etc.), or (b) curated from multiple public CC0/MIT/Apache-2.0 awesome-lists where no central API exists (mcp-servers, ai-agents, cybersecurity-tools, self-hosted-software, etc.). The aggregation is license-clean for commercial repackaging."
    },
    {
        "q": "Can I use these datasets commercially?",
        "a": "The free 20-record samples are MIT-style permissive — yes, including commercial. The full paid datasets are licensed per the Gumroad terms (also commercially usable, but covered by the purchase). The catalog metadata itself (the structured records about open-source projects) is factual data and clean for commercial repackaging. Per-record licenses, where applicable to the underlying project (e.g. an MIT-licensed npm package), are surfaced as first-class license fields."
    },
    {
        "q": "What are 'derived enum tiers' and why do you ship them?",
        "a": "Source data is raw — npm gives a downloads number, HuggingFace gives a pipeline tag, OpenRouter gives a per-token price. Buyer questions are categorical: 'cheap models', 'production-grade providers', 'permissively-licensed packages', 'chat-only models'. We compute the derived enum-tier fields once during the pipeline run and ship them as first-class fields: costTierAbsolute, useCaseTier, uptimeTier, licenseTier, popularityTier, vendorTier, and ~40 more. Filter by them directly instead of writing your own threshold-and-OR-clause query. Full reference: /tiers.html and /blog-semantic-enum-tiers.html for the methodology."
    },
    {
        "q": "Are tiers consistent across datasets?",
        "a": "Where the buyer-question is the same, yes — same enum name, same enum values. useCaseTier=chat returns matching records consistently across huggingface-models, huggingface-datasets, and ai-models-pricing. licenseTier=permissive does the same across HF models, HF datasets, npm-packages, homebrew-packages, and open-source-alternatives. Cross-dataset filters work without remapping. The /tiers.html page lists which datasets share which tiers."
    },
    {
        "q": "Do you ship percentile-based ranks or absolute thresholds?",
        "a": "Both, deliberately. popularityTier is percentile-based (top1pct/top5pct/top25pct/rest) because buyers asking 'show me giants' want a relative position. costTierAbsolute and uptimeTier are absolute thresholds (cheap=<$1/M, excellent=>99.9%) because buyers asking 'fits my budget' or 'production-grade' want stability across refreshes. A model that's top-5% today and top-25% next month is the same model — only percentile tiers shift; absolute tiers do not."
    },
    {
        "q": "How big is each full dataset?",
        "a": "Homebrew Packages: 12,200+ records. npm Packages: 6,100+. VS Code Extensions: 4,800+. HuggingFace Models: 4,000. MCP Servers: 3,600+. AI Tools: 2,800+. Cybersecurity Tools: 2,700+. HuggingFace Datasets: 2,800+. Public APIs: 2,600+. Self-Hosted Software: 2,300+. Design Resources: 2,100+. AI Agents: 2,000+. AI Prompts: 1,800+. Developer Tools: 1,600+. Open Source Alternatives: 900+. AI Models Pricing: 800+. No-Code/Low-Code: 500+. LLMOps & Eval: 490+. Platform Engineering: 390+. Vector DB & RAG: 190+. Total: ~55,000 records across 20 datasets."
    },
    {
        "q": "Is there a free sample of everything combined?",
        "a": "Yes — the mega-sample.json / mega-sample.csv in this repo combines 5 random records from each dataset (100 records total). Useful to inspect the schema and see how datasets compare side-by-side. Also available as a single ZIP from Gumroad ($0): the Free Developer Data Sample."
    },
    {
        "q": "What's the best dataset for a machine-learning training pipeline?",
        "a": "Depends on the task. For supervised fine-tuning with instruction data: huggingface-datasets (2,600+ datasets filtered by task category + license). For LLM tooling research: llmops-and-eval (490+ frameworks across 9 buckets) + vector-db-and-rag (190+ embedding stores and RAG infrastructure). For pricing comparison across model providers: ai-models-pricing (800+ endpoints with per-token cost, context length, uptime). For agent-framework landscape: ai-agents (2,000+ frameworks)."
    },
    {
        "q": "How is this different from awesome-* lists on GitHub?",
        "a": "awesome-lists are unstructured markdown — great for human browsing, terrible for programmatic filtering. These datasets are normalized JSON + CSV with consistent schema, semantic enum tiers (popularityTier, recencyTier, licenseTier, supplyChainRisk, etc.), and enrichment fields (githubStars, weeklyDownloads, downloads/likes, install counts, pricing). You can filter, sort, group, and join these — you can't do that with a bullet list."
    },
    {
        "q": "Can I download via API instead of a static file?",
        "a": "The free samples are static JSON/CSV served from GitHub Pages or raw.githubusercontent.com (any HTTP client works — curl, wget, fetch). No API key needed. For programmatic discovery of available datasets, the index.html JSON-LD declares all 20 with their download URLs (parseable as schema.org DataCatalog). Full paid datasets ship as a one-time download from Gumroad after purchase."
    },
    {
        "q": "What schema fields are in every record?",
        "a": "Base schema across all 20 datasets: name (string), url (string), description (string), category (string), pricing (free | freemium | paid | open-source), hasApi (boolean), tags (string array). Dataset-specific first-class fields layer on top — e.g. weeklyDownloads + dependents + npmScore for npm, downloads + likes + pipelineTag + modality + language for huggingface-models, auth + https + cors for public-apis, installCount365d + packageType + dependencies for homebrew. Plus 40+ semantic enum tiers across the catalog (urlDomainTier, descriptionLengthTier, popularityTier, etc.)."
    },
    {
        "q": "Where can I report a missing or wrong entry?",
        "a": "File an issue on the GitHub repo at github.com/futdevpro/niche-datasets-free. PRs welcome for the samples; the full datasets are regenerated from sources on the monthly/quarterly refresh, so corrections to the source (e.g. fixing an awesome-list upstream) propagate automatically. For specific source-data complaints (e.g. 'this MCP server is mislabeled'), the relevant source repo / API is the right place to fix it at the root."
    },
    {
        "q": "What refresh cadence should I expect per dataset?",
        "a": "Per-source — not uniform. API-backed datasets that change daily (npm registry, HuggingFace Hub) need at least weekly refresh. The OpenRouter pricing matrix shifts with provider price changes (medium cadence). Awesome-list-mirror datasets (mcp-servers, ai-agents, cybersecurity-tools, design-resources, vector-db-and-rag, llmops-and-eval) only move when humans PR new entries — monthly or quarterly is enough. The 13-day refresh report (linked from the homepage) documents actual per-source churn so you can pick the right cadence for your use case."
    },
    {
        "q": "Can I subscribe to refresh notifications?",
        "a": "Yes. Each dataset publishes an RSS feed entry every time it refreshes — subscribe to /feed.xml in your reader (Feedly, NetNewsWire, miniflux, etc.) and you'll see new entries when any dataset re-pulls. The entry includes the dataset slug + the lastRefreshed date so you can decide whether to re-download. Programmatic alternative: poll /datasets.json daily and compare each dataset's lastRefreshed timestamp."
    },
    {
        "q": "How do I auto-generate a typed client for the API?",
        "a": "Use the /openapi.json spec with openapi-generator (any language) or openapi-typescript (TypeScript). The /api.html page has copy-pasteable commands for Python and TypeScript codegen. The spec covers all 3 free endpoints (catalog, per-dataset metadata, RSS feed) with full request/response schemas and the 20-slug enum for the per-dataset path. Idempotent — same spec across releases unless a schemaVersion bump."
    },
    {
        "q": "Are there rate limits on the free API?",
        "a": "No explicit rate limit on /datasets.json, /<slug>-meta.json, or /feed.xml — they are static files served from GitHub Pages CDN. Pages applies its own bandwidth fair-use (~100GB/month per repo) but for a no-key catalog enumeration that's not a real cap. The sample JSON/CSV files served from raw.githubusercontent.com may rate-limit at extreme volume (~10K req/min from one IP) — back off with jitter if you see HTTP 429. For higher-volume access patterns, see the in-planning distribution-model note in /api.html."
    },
    {
        "q": "Can an LLM agent use this catalog directly?",
        "a": "Yes — by design. The /openapi.json spec is OpenAPI 3.1 (LLM-friendly), the /datasets.json and per-dataset meta endpoints are flat JSON (easy to parse with no client SDK), every record has derived semantic enum tier fields (filterable without numeric thresholds the LLM might hallucinate), and the FAQ + buyer's-guide pages have schema.org markup that AI Overview / Bing Copilot / Perplexity will cite. The /api.html page has an end-to-end Python agent-callable example using openapi-python-client."
    },
    {
        "q": "Is there a refund policy on the paid datasets?",
        "a": "Yes — 30 days, no questions asked, via your Gumroad library page. If the data does not match what is described (record count, schema, freshness), request the refund within 30 days of purchase. Refund policy is also embedded in every Gumroad product description and on the project's storefront page."
    },
    {
        "q": "How do I get the exact record count instead of the 'X,XXX+' marketing string?",
        "a": "Use the liveRecordCount field on /datasets.json or any /<slug>-meta.json — it's an integer with the exact count from the live data file (e.g. 6171 for npm-packages, alongside the recordCount string '6,100+'). Useful for size estimation, pagination, and change-detection between refreshes. Documented in /api.html under 'Two record-count fields'."
    },
]


PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>FAQ — Free Developer Datasets (CSV + JSON)</title>
<meta name="description" content="Frequently asked questions about the 20 free developer and AI dataset samples — formats, freshness, sources, licensing, schema, and how to use them in machine-learning pipelines.">
<link rel="canonical" href="https://futdevpro.github.io/niche-datasets-free/faq.html">
<meta property="og:type" content="website">
<meta property="og:url" content="https://futdevpro.github.io/niche-datasets-free/faq.html">
<meta property="og:title" content="FAQ — Free Developer Datasets (CSV + JSON)">
<meta property="og:description" content="Frequently asked questions about the 20 free developer and AI dataset samples — formats, freshness, sources, licensing, schema, ML-pipeline use.">
<meta property="og:site_name" content="Niche Datasets">
<meta property="og:image" content="https://futdevpro.github.io/niche-datasets-free/og-cover.svg">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="FAQ — Free Developer Datasets">
<meta name="twitter:description" content="Common questions about the 20 free dataset samples — formats, freshness, sources, licensing, schema, ML use.">
<meta name="twitter:image" content="https://futdevpro.github.io/niche-datasets-free/og-cover.svg">
<style>
  body{{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;max-width:760px;margin:0 auto;padding:2rem 1.25rem;line-height:1.55;color:#1a1a1a}}
  h1{{font-size:1.7rem;margin-bottom:.25rem}}
  h2{{font-size:1.05rem;margin-top:2rem;color:#0969da}}
  a{{color:#0969da}}
  .lead{{color:#444}}
  .nav{{font-size:.9rem;color:#666;margin-bottom:1rem}}
  details{{margin:1rem 0;padding:.6rem .9rem;border:1px solid #eee;border-radius:6px}}
  details[open]{{background:#fafbfc}}
  summary{{cursor:pointer;font-weight:600;font-size:1rem}}
  details p{{margin:.75rem 0 .25rem 0}}
  footer{{margin-top:3rem;padding-top:1rem;border-top:1px solid #eee;font-size:.85rem;color:#666}}
</style>
</head>
<body>

<p class="nav"><a href="./">← All 20 datasets</a> &nbsp;·&nbsp; <a href="quickstart.html">5-min quickstart</a> &nbsp;·&nbsp; <a href="examples.html">Code examples</a> &nbsp;·&nbsp; <a href="vs.html">vs. alternatives</a></p>

<h1>FAQ — Free Developer Datasets</h1>
<p class="lead">Common questions about the 20 free developer and AI dataset samples: what's included, how to download, formats, freshness, sources, licensing, and how to use them in machine-learning workflows.</p>

{faq_html}

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


def build_faq_html():
    parts = []
    for f in FAQS:
        q_safe = f["q"].replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        a_safe = f["a"].replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        parts.append(f"<details>\n  <summary>{q_safe}</summary>\n  <p>{a_safe}</p>\n</details>")
    return "\n".join(parts)


def build_jsonld():
    return json.dumps({
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name": f["q"],
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": f["a"],
                },
            }
            for f in FAQS
        ],
    }, indent=2)


def build_breadcrumb_jsonld():
    return json.dumps({
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Niche Datasets",
             "item": "https://futdevpro.github.io/niche-datasets-free/"},
            {"@type": "ListItem", "position": 2, "name": "FAQ",
             "item": "https://futdevpro.github.io/niche-datasets-free/faq.html"},
        ],
    }, indent=2)


def main():
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    html = PAGE.format(
        faq_html=build_faq_html(),
        jsonld=build_jsonld(),
        breadcrumb_jsonld=build_breadcrumb_jsonld(),
    )
    path = os.path.join(repo_root, "faq.html")
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Wrote {path} with {len(FAQS)} Q+A entries.")


if __name__ == "__main__":
    main()
