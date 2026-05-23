#!/usr/bin/env python3
"""
Generate /examples.html — code snippets for loading the dataset samples in
Python (pandas + native json), JavaScript (fetch + Node.js), jq CLI, R, curl.

Why: long-tail queries like "how to load json dataset in pandas" or "fetch
github csv in javascript" route to pages that show concrete copy-pasteable code.
Each snippet uses a real sample URL so the reader can run it as-is.

Run from repo root:  python3 scripts/build-examples.py
"""
import datetime
import json
import os

# We use npm-packages as the canonical example dataset throughout — concrete URL,
# common record shape, recognized name. Snippets are agnostic; reader can swap
# the URL for any of the 20 datasets.
SAMPLE_URL_JSON = "https://raw.githubusercontent.com/futdevpro/niche-datasets-free/main/npm-packages-sample.json"
SAMPLE_URL_CSV = "https://raw.githubusercontent.com/futdevpro/niche-datasets-free/main/npm-packages-sample.csv"


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


SNIPPETS = [
    {
        "lang": "Python · pandas",
        "id": "python-pandas",
        "intro": "Load the CSV directly from the GitHub raw URL into a DataFrame. Works for all 20 datasets — change the slug in the URL.",
        "code": f"""import pandas as pd

df = pd.read_csv("{SAMPLE_URL_CSV}")
print(df.shape)            # (20, N) — N varies per dataset
print(df.columns.tolist())
print(df.head(3))""",
    },
    {
        "lang": "Python · stdlib json",
        "id": "python-json",
        "intro": "No pandas dependency — pure stdlib via urllib + json. Returns a list of dicts you can filter directly.",
        "code": f"""import json, urllib.request

with urllib.request.urlopen("{SAMPLE_URL_JSON}") as r:
    records = json.load(r)

# Filter: only open-source packages with an API
oss_with_api = [r for r in records if r.get("pricing") == "open-source" and r.get("hasApi")]
print(len(oss_with_api), "of", len(records))""",
    },
    {
        "lang": "JavaScript · fetch (browser or Node 18+)",
        "id": "javascript-fetch",
        "intro": "Native fetch in any modern browser or Node 18+. No dependencies.",
        "code": f"""const url = "{SAMPLE_URL_JSON}";
const records = await fetch(url).then(r => r.json());

console.log(records.length, "records");
console.log(records[0]);

// Group by category
const byCategory = Object.groupBy(records, r => r.category);
console.log(Object.keys(byCategory));""",
    },
    {
        "lang": "Node.js · node-fetch / undici",
        "id": "nodejs",
        "intro": "If you're on older Node and need a fetch polyfill. Otherwise the JS snippet above already works in Node 18+.",
        "code": f"""// npm i undici
import {{ fetch }} from 'undici';

const records = await fetch("{SAMPLE_URL_JSON}").then(r => r.json());
console.log(records[0].name, records[0].url);""",
    },
    {
        "lang": "jq CLI",
        "id": "jq",
        "intro": "Pipe curl into jq. Great for one-off filtering or pre-pipeline data exploration without a script.",
        "code": f"""# All names + categories
curl -s {SAMPLE_URL_JSON} | jq -r '.[] | "\\(.name)\\t\\(.category)"'

# Just the ai-and-ml packages
curl -s {SAMPLE_URL_JSON} | jq '.[] | select(.category == "ai-and-ml")'

# Count by pricing bucket
curl -s {SAMPLE_URL_JSON} | jq -r '[.[].pricing] | group_by(.) | map({{key: .[0], count: length}})'""",
    },
    {
        "lang": "R · read.csv",
        "id": "r",
        "intro": "Base R reads from a URL directly. No packages required.",
        "code": f"""df <- read.csv("{SAMPLE_URL_CSV}", stringsAsFactors = FALSE)
str(df)
table(df$pricing)
table(df$category)""",
    },
    {
        "lang": "curl + jq pipe (shell one-liner)",
        "id": "shell-pipe",
        "intro": "Useful for shell scripts, CI checks, or grepping the catalog from a Bash alias.",
        "code": f"""# How many records?
curl -s {SAMPLE_URL_JSON} | jq 'length'

# Just URLs (one per line) — pipe into wget/curl for follow-up
curl -s {SAMPLE_URL_JSON} | jq -r '.[].url'

# Save the full catalog locally
curl -o npm-packages.json {SAMPLE_URL_JSON}""",
    },
    {
        "lang": "Pandas-style filter + join (npm + Homebrew supply-chain audit)",
        "id": "supply-chain",
        "intro": "Real use-case: cross-reference two datasets. Load both, join on a key, surface risk.",
        "code": f"""import pandas as pd

npm = pd.read_csv("https://raw.githubusercontent.com/futdevpro/niche-datasets-free/main/npm-packages-sample.csv")
brew = pd.read_csv("https://raw.githubusercontent.com/futdevpro/niche-datasets-free/main/homebrew-packages-sample.csv")

# Packages that appear in BOTH ecosystems (rare — usually a CLI tool with both an npm wrapper
# and a Homebrew formula). Useful for supply-chain audits: a package that's distributed
# through multiple package managers has more attack surface.
overlap = pd.merge(npm[['name']], brew[['name']], on='name')
print(f"{{len(overlap)}} packages in both registries")
print(overlap.head())""",
    },
    {
        "lang": "DuckDB · query JSON/CSV remote URL",
        "id": "duckdb",
        "intro": "DuckDB reads CSV + JSON straight from HTTPS, no download. Perfect for ad-hoc SQL on the catalog.",
        "code": f"""-- in duckdb shell or via duckdb-python
INSTALL httpfs; LOAD httpfs;

SELECT category, COUNT(*) AS n
FROM read_csv_auto('{SAMPLE_URL_CSV}')
GROUP BY category
ORDER BY n DESC;""",
    },
    {
        "lang": "Semantic enum tier filters (Python · pandas)",
        "id": "tier-filters-pandas",
        "intro": "Same buyer-question, in Python. Loads from the sample URL straight into pandas, filters by semantic enum tier fields with one boolean-mask combo per use case.",
        "code": """import pandas as pd

BASE = "https://raw.githubusercontent.com/futdevpro/niche-datasets-free/main"

# AI Models Pricing — cheap chat models with production-grade uptime
pricing = pd.read_json(f"{BASE}/ai-models-pricing-sample.json")
cheap_chat = pricing[
    (pricing["useCaseTier"] == "chat") &
    (pricing["costTierAbsolute"] == "cheap") &
    (pricing["uptimeTier"] == "excellent")
]
print(cheap_chat[["name", "provider", "pricingPromptPerMillionUsd", "contextLength"]])

# HuggingFace Models — embedding models only, permissively licensed
hf = pd.read_json(f"{BASE}/huggingface-models-sample.json")
emb_perm = hf[(hf["useCaseTier"] == "embedding") & (hf["licenseTier"] == "permissive")]
print(emb_perm[["modelId", "downloads", "license"]])

# npm Packages — popular, safe, fresh
npm = pd.read_json(f"{BASE}/npm-packages-sample.json")
trusted = npm[
    (npm["popularityTier"] == "top25pct") &
    (npm["supplyChainRisk"] == "low") &
    (npm["recencyTier"] == "fresh")
]
print(trusted[["name", "weeklyDownloads", "lastPublished"]])""",
    },
    {
        "lang": "Semantic enum tier filters (jq)",
        "id": "tier-filters",
        "intro": "Filter by derived enum tier fields — same enum names work across datasets where the buyer-question is the same. Full reference at /tiers.html, methodology at /blog-semantic-enum-tiers.html.",
        "code": """# AI Models Pricing — cheap chat models with production-grade uptime
curl -s https://raw.githubusercontent.com/futdevpro/niche-datasets-free/main/ai-models-pricing-sample.json \\
  | jq '.[] | select(.useCaseTier == "chat" and .costTierAbsolute == "cheap" and .uptimeTier == "excellent")
        | {name, provider, pricingPromptPerMillionUsd, contextLength}'

# HuggingFace Models — embedding models only, permissively licensed
curl -s https://raw.githubusercontent.com/futdevpro/niche-datasets-free/main/huggingface-models-sample.json \\
  | jq '.[] | select(.useCaseTier == "embedding" and .licenseTier == "permissive")
        | {modelId, downloads, license}'

# npm Packages — popular (top-25%), no supply-chain risk, recently published
curl -s https://raw.githubusercontent.com/futdevpro/niche-datasets-free/main/npm-packages-sample.json \\
  | jq '.[] | select(.popularityTier == "top25pct" and .supplyChainRisk == "low" and .recencyTier == "fresh")
        | {name, weeklyDownloads, lastPublished}'

# Cybersecurity Tools — OSS only, network-targeting
curl -s https://raw.githubusercontent.com/futdevpro/niche-datasets-free/main/cybersecurity-tools-sample.json \\
  | jq '.[] | select(.vendorTier == "oss" and .targetPlatform == "network")
        | {name, description}'""",
    },
    {
        "lang": "Semantic enum tier filters (Node.js · fetch)",
        "id": "tier-filters-node",
        "intro": "JavaScript / Node.js (18+) with native fetch. Same buyer-questions as the jq + pandas snippets, in JS. Useful for agent-builders, API gateways, frontend filtering UIs.",
        "code": """const BASE = 'https://raw.githubusercontent.com/futdevpro/niche-datasets-free/main';

// AI Models Pricing — cheap chat models with production-grade uptime
const pricing = await (await fetch(`${BASE}/ai-models-pricing-sample.json`)).json();
const cheapChat = pricing.filter(r =>
  r.useCaseTier === 'chat' &&
  r.costTierAbsolute === 'cheap' &&
  r.uptimeTier === 'excellent'
);
console.log(cheapChat.map(r => ({
  name: r.name, provider: r.provider,
  pricePerM: r.pricingPromptPerMillionUsd, ctx: r.contextLength,
})));

// HuggingFace Models — embedding models only, permissively licensed
const hf = await (await fetch(`${BASE}/huggingface-models-sample.json`)).json();
const embPerm = hf.filter(r =>
  r.useCaseTier === 'embedding' && r.licenseTier === 'permissive'
);
console.log(embPerm.map(({ modelId, downloads, license }) => ({ modelId, downloads, license })));

// npm Packages — popular, safe, fresh
const npm = await (await fetch(`${BASE}/npm-packages-sample.json`)).json();
const trusted = npm.filter(r =>
  r.popularityTier === 'top25pct' &&
  r.supplyChainRisk === 'low' &&
  r.recencyTier === 'fresh'
);
console.log(trusted.map(({ name, weeklyDownloads, lastPublished }) => ({ name, weeklyDownloads, lastPublished })));""",
    },
    {
        "lang": "Semantic enum tier filters (DuckDB · SQL)",
        "id": "tier-filters-duckdb",
        "intro": "Same buyer-questions, in SQL via DuckDB reading the JSON straight from HTTPS. Useful when you already have a DuckDB warehouse + want to join the niche-datasets samples against your own tables.",
        "code": """-- in duckdb shell, duckdb-python, or duckdb-wasm
INSTALL httpfs; LOAD httpfs;

-- AI Models Pricing — cheap chat models with production-grade uptime
SELECT name, provider, pricingPromptPerMillionUsd, contextLength
FROM read_json_auto('https://raw.githubusercontent.com/futdevpro/niche-datasets-free/main/ai-models-pricing-sample.json')
WHERE useCaseTier = 'chat'
  AND costTierAbsolute = 'cheap'
  AND uptimeTier = 'excellent'
ORDER BY pricingPromptPerMillionUsd ASC;

-- HuggingFace Models — embedding models only, permissively licensed
SELECT modelId, downloads, license
FROM read_json_auto('https://raw.githubusercontent.com/futdevpro/niche-datasets-free/main/huggingface-models-sample.json')
WHERE useCaseTier = 'embedding'
  AND licenseTier = 'permissive'
ORDER BY downloads DESC;

-- npm Packages — popular, safe, fresh
SELECT name, weeklyDownloads, lastPublished
FROM read_json_auto('https://raw.githubusercontent.com/futdevpro/niche-datasets-free/main/npm-packages-sample.json')
WHERE popularityTier = 'top25pct'
  AND supplyChainRisk = 'low'
  AND recencyTier = 'fresh'
ORDER BY weeklyDownloads DESC;""",
    },
    {
        "lang": "Bundle vs single-SKU price comparison (jq)",
        "id": "bundle-compare",
        "intro": "Pick a target use case (e.g. 'agent registry'), enumerate the datasets you need, sum their single-SKU prices, compare against the bundle that includes them. Decision-support for the buyer's guide use-case mapping.",
        "code": """# Use case: build an agent / MCP registry.
# Needed datasets: mcp-servers + ai-agents + ai-tools.
# Compare per-dataset sum vs Platform Builder Pack (which includes platform + dev tools).

curl -s https://futdevpro.github.io/niche-datasets-free/datasets.json \\
  | jq '
      .datasets
      | map(select(.slug | IN("mcp-servers", "ai-agents", "ai-tools")))
      | {
          single_skus_total: (map(.fullDatasetPriceUsd) | add),
          single_skus:       map({slug, price: .fullDatasetPriceUsd}),
          bundle_options:    (.[0].bundles // [])
        }'

# Output (illustrative):
# {
#   "single_skus_total": 33,
#   "single_skus": [
#     {"slug": "ai-agents",  "price": 11},
#     {"slug": "ai-tools",   "price": 11},
#     {"slug": "mcp-servers","price": 11}
#   ],
#   "bundle_options": [
#     {"name": "Complete Developer Data Bundle", "url": "...l/developer-data-bundle"}
#   ]
# }""",
    },
    {
        "lang": "Change-detection between refreshes (Python · liveRecordCount)",
        "id": "change-detection",
        "intro": "Poll /datasets.json, compare liveRecordCount per dataset against a saved snapshot, alert when anything moves. Use this if you mirror our catalog into your own pipeline and want a 'pull only what changed' loop. Documented in /api.html under 'Two record-count fields'.",
        "code": """import json, urllib.request, pathlib

URL = 'https://futdevpro.github.io/niche-datasets-free/datasets.json'
SNAPSHOT = pathlib.Path('niche-datasets-snapshot.json')

# Fetch current catalog
with urllib.request.urlopen(URL) as r:
    current = {d['slug']: d.get('liveRecordCount') for d in json.load(r)['datasets']}

# Load previous snapshot (or treat first run as 'everything changed')
prev = json.loads(SNAPSHOT.read_text()) if SNAPSHOT.exists() else {}

# Diff
changed = {
    slug: (prev.get(slug), n) for slug, n in current.items()
    if prev.get(slug) != n and n is not None
}

if changed:
    print(f'{len(changed)} datasets changed since last poll:')
    for slug, (was, now) in sorted(changed.items()):
        delta = '+new' if was is None else f'{now - was:+d}'
        print(f'  {slug}: {was} -> {now} ({delta})')
else:
    print('No changes since last poll.')

# Save current as next snapshot
SNAPSHOT.write_text(json.dumps(current, indent=2))""",
    },
]


PAGE_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Examples — How to Load the Niche Datasets (Python · JS · jq · R · DuckDB)</title>
<meta name="description" content="Copy-pasteable code snippets for loading the niche-datasets samples — pandas, urllib, fetch, jq, R, DuckDB, curl. Works on all 20 datasets — change the slug in the URL.">
<link rel="canonical" href="https://futdevpro.github.io/niche-datasets-free/examples.html">
<meta property="og:type" content="website">
<meta property="og:url" content="https://futdevpro.github.io/niche-datasets-free/examples.html">
<meta property="og:title" content="Examples — How to Load the Niche Datasets (Python · JS · jq · R · DuckDB)">
<meta property="og:description" content="Copy-pasteable code snippets for loading the niche-datasets samples — pandas, urllib, fetch, jq, R, DuckDB, curl. Works on all 20 datasets.">
<meta property="og:site_name" content="Niche Datasets">
<meta property="og:image" content="https://futdevpro.github.io/niche-datasets-free/og-cover.svg">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="Code Examples — Loading the Niche Datasets">
<meta name="twitter:description" content="Copy-pasteable snippets for pandas, urllib, fetch, jq, R, DuckDB, curl.">
<meta name="twitter:image" content="https://futdevpro.github.io/niche-datasets-free/og-cover.svg">
<style>
  body{{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;max-width:880px;margin:0 auto;padding:2rem 1.25rem;line-height:1.55;color:#1a1a1a}}
  h1{{font-size:1.7rem;margin-bottom:.25rem}}
  h2{{font-size:1.1rem;margin-top:2.2rem;color:#0969da;border-bottom:1px solid #eee;padding-bottom:.3rem}}
  a{{color:#0969da}}
  .lead{{color:#444}}
  .nav{{font-size:.9rem;color:#666;margin-bottom:1rem}}
  pre{{background:#0d1117;color:#e6edf3;padding:1rem;border-radius:6px;overflow-x:auto;font-size:.86rem;line-height:1.5}}
  pre code{{background:transparent;padding:0;font-family:Menlo,Consolas,monospace}}
  code{{background:#f4f4f4;padding:.1rem .3rem;border-radius:3px;font-size:.9em;font-family:Menlo,Consolas,monospace}}
  .intro{{color:#444;margin:.5rem 0 .75rem 0}}
  .toc{{background:#fafafa;padding:.8rem 1.2rem;border-radius:6px;font-size:.9rem;margin:1.2rem 0}}
  .toc ul{{margin:.4rem 0;padding-left:1.2rem}}
  footer{{margin-top:3rem;padding-top:1rem;border-top:1px solid #eee;font-size:.85rem;color:#666}}
</style>
</head>
<body>

<p class="nav"><a href="./">← All 20 datasets</a> &nbsp;·&nbsp; <a href="quickstart.html">5-min quickstart</a> &nbsp;·&nbsp; <a href="vs.html">vs. alternatives</a> &nbsp;·&nbsp; <a href="faq.html">FAQ</a></p>

<h1>Examples — How to Load the Niche Datasets</h1>
<p class="lead">Copy-pasteable code snippets for loading the 20 free dataset samples in your preferred environment. All snippets use the <code>npm-packages</code> sample as the example URL — swap the slug for any of the other 19 datasets.</p>

<div class="toc">
<strong>Languages covered:</strong>
<ul>{toc_html}</ul>
</div>

{snippets_html}

<h2>Switching to a different dataset</h2>
<p>Every snippet above uses <code>npm-packages-sample.json</code> / <code>.csv</code>. To load a different one, change the slug in the URL. Available slugs:</p>
<p style="font-size:.92rem;line-height:1.9">
  <code>homebrew-packages</code> · <code>npm-packages</code> · <code>vscode-extensions</code> · <code>huggingface-models</code> · <code>mcp-servers</code> · <code>ai-tools</code> · <code>cybersecurity-tools</code> · <code>huggingface-datasets</code> · <code>public-apis</code> · <code>self-hosted-software</code> · <code>design-resources</code> · <code>ai-agents</code> · <code>ai-prompts</code> · <code>developer-tools</code> · <code>open-source-alternatives</code> · <code>ai-models-pricing</code> · <code>no-code-lowcode</code> · <code>llmops-and-eval</code> · <code>platform-engineering</code> · <code>vector-db-and-rag</code>
</p>

<h2>Schema reference</h2>
<p>All 20 datasets share a base schema: <code>name</code>, <code>url</code>, <code>description</code>, <code>category</code>, <code>pricing</code> (free / freemium / paid / open-source), <code>hasApi</code>, <code>tags</code>. Each dataset adds first-class fields specific to its niche — see the per-dataset detail pages (e.g. <a href="npm-packages.html">npm-packages</a>) for the full reference, or the <a href="https://github.com/futdevpro/niche-datasets-free#format">repo README §Format</a>.</p>

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


def build_jsonld():
    today_iso = datetime.date.today().isoformat()
    return json.dumps({
        "@context": "https://schema.org",
        "@type": "TechArticle",
        "headline": "Examples — How to Load the Niche Datasets",
        "description": "Copy-pasteable code snippets for loading the niche-datasets samples in Python (pandas, urllib), JavaScript (fetch, Node.js), jq CLI, R, curl, and DuckDB. Works on all 20 datasets.",
        "url": "https://futdevpro.github.io/niche-datasets-free/examples.html",
        "datePublished": "2026-05-17",
        "dateModified": today_iso,
        "author": {"@type": "Organization", "name": "Future Development Program"},
        "publisher": {"@type": "Organization", "name": "Future Development Program",
                      "url": "https://github.com/futdevpro"},
        "keywords": ["pandas", "load csv from url", "jq json filter", "fetch github raw json",
                     "duckdb httpfs csv", "r read csv from url", "huggingface dataset csv"],
        "about": ["data engineering", "developer tools", "machine learning"],
    }, indent=2)


def build_breadcrumb_jsonld():
    return json.dumps({
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Niche Datasets",
             "item": "https://futdevpro.github.io/niche-datasets-free/"},
            {"@type": "ListItem", "position": 2, "name": "Examples",
             "item": "https://futdevpro.github.io/niche-datasets-free/examples.html"},
        ],
    }, indent=2)


def main():
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    toc = "\n".join(f'  <li><a href="#{s["id"]}">{esc(s["lang"])}</a></li>' for s in SNIPPETS)
    blocks = []
    for s in SNIPPETS:
        blocks.append(
            f'<h2 id="{s["id"]}">{esc(s["lang"])}</h2>\n'
            f'<p class="intro">{esc(s["intro"])}</p>\n'
            f'<pre><code>{esc(s["code"])}</code></pre>'
        )
    html = PAGE_TEMPLATE.format(
        toc_html=toc,
        snippets_html="\n\n".join(blocks),
        jsonld=build_jsonld(),
        breadcrumb_jsonld=build_breadcrumb_jsonld(),
    )
    path = os.path.join(repo_root, "examples.html")
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Wrote {path} with {len(SNIPPETS)} code snippets across {len({s['lang'].split()[0] for s in SNIPPETS})} languages.")


if __name__ == "__main__":
    main()
