#!/usr/bin/env python3
"""
Generate /examples.html — code snippets for loading the dataset samples in
Python (pandas + native json), JavaScript (fetch + Node.js), jq CLI, R, curl.

Why: long-tail queries like "how to load json dataset in pandas" or "fetch
github csv in javascript" route to pages that show concrete copy-pasteable code.
Each snippet uses a real sample URL so the reader can run it as-is.

Run from repo root:  python3 scripts/build-examples.py
"""
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

<p class="nav"><a href="./">← All 20 datasets</a> &nbsp;·&nbsp; <a href="faq.html">FAQ</a></p>

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
    return json.dumps({
        "@context": "https://schema.org",
        "@type": "TechArticle",
        "headline": "Examples — How to Load the Niche Datasets",
        "description": "Copy-pasteable code snippets for loading the niche-datasets samples in Python (pandas, urllib), JavaScript (fetch, Node.js), jq CLI, R, curl, and DuckDB. Works on all 20 datasets.",
        "url": "https://futdevpro.github.io/niche-datasets-free/examples.html",
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
