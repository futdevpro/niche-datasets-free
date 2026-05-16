#!/usr/bin/env python3
"""
Generate per-dataset detail HTML pages with their own schema.org JSON-LD Dataset blocks.

Why: index.html declares 20 Dataset entries inside a DataCatalog, but every Dataset.url
points to the GitHub repo root. Google Dataset Search and other indexers prefer one
URL per Dataset entity. This script emits 20 standalone landing pages (one per dataset)
so each gets its own indexable URL, then updates sitemap.xml to include them.

Also pulls each dataset's hand-crafted use-cases prose from the sibling repo
(../niche-datasets/__agent/content/<slug>/use-cases.md) and injects it as long-tail
SEO content into the detail page.

Run from repo root:  python3 scripts/build-detail-pages.py
"""
import json
import os
import re

try:
    import markdown
except ImportError:
    markdown = None

DATASETS = [
    {"slug": "homebrew-packages", "name": "Homebrew Packages Directory", "records": "12,200+",
     "desc": "Catalog of 12,200+ Homebrew formulae and casks with install counts, package type, dependencies, tap, and deprecation status.",
     "keywords": ["homebrew", "macos", "package manager", "cli tools"],
     "gumroad": "homebrew-packages-directory", "price": 11},
    {"slug": "npm-packages", "name": "npm Packages Directory", "records": "6,000+",
     "desc": "Catalog of 6,000+ top JavaScript/TypeScript npm packages with weekly/monthly downloads, dependents count, npm score (popularity/quality/maintenance), and repository.",
     "keywords": ["npm", "javascript", "typescript", "packages"],
     "gumroad": "npm-packages-directory", "price": 11},
    {"slug": "vscode-extensions", "name": "VS Code Extensions Directory", "records": "4,800+",
     "desc": "Catalog of 4,800+ VS Code Marketplace extensions with install counts, version, last-updated, extension ID, and publisher.",
     "keywords": ["vscode", "extensions", "ide", "developer tools"],
     "gumroad": "vscode-extensions-directory", "price": 9},
    {"slug": "huggingface-models", "name": "HuggingFace Models Directory", "records": "4,000",
     "desc": "Catalog of 4,000 most-downloaded HuggingFace models with downloads, likes, license, pipeline tag, modality, and language.",
     "keywords": ["huggingface", "machine learning", "models", "ai"],
     "gumroad": "huggingface-models-directory", "price": 11},
    {"slug": "mcp-servers", "name": "Open MCP Servers Directory", "records": "3,600+",
     "desc": "Catalog of 3,600+ Model Context Protocol (MCP) servers with GitHub stars, category, and capabilities.",
     "keywords": ["mcp", "model context protocol", "ai agents", "tooling"],
     "gumroad": "mcp-servers-directory", "price": 9},
    {"slug": "ai-tools", "name": "AI Tools Directory", "records": "2,700+",
     "desc": "Catalog of 2,700+ AI tools and applications with category, pricing model, and API availability.",
     "keywords": ["ai tools", "artificial intelligence", "saas"],
     "gumroad": "ai-tools-directory", "price": 9},
    {"slug": "cybersecurity-tools", "name": "Cybersecurity Tools Directory", "records": "2,600+",
     "desc": "Catalog of 2,600+ cybersecurity tools across pentesting, defensive, forensics, and monitoring categories.",
     "keywords": ["cybersecurity", "infosec", "pentesting", "security tools"],
     "gumroad": "cybersecurity-tools", "price": 9},
    {"slug": "huggingface-datasets", "name": "HuggingFace Datasets Directory", "records": "2,600+",
     "desc": "Catalog of 2,600+ most-downloaded HuggingFace datasets with downloads, likes, license, task categories, and language.",
     "keywords": ["huggingface", "datasets", "machine learning", "training data"],
     "gumroad": "huggingface-datasets-directory", "price": 11},
    {"slug": "public-apis", "name": "Public APIs Directory", "records": "2,500+",
     "desc": "Catalog of 2,500+ free and freemium public APIs with auth, HTTPS, and CORS flags per row, across 50+ categories.",
     "keywords": ["public apis", "rest api", "free api", "no-auth api"],
     "gumroad": "public-apis-directory", "price": 12},
    {"slug": "self-hosted-software", "name": "Self-Hosted Software Directory", "records": "2,300+",
     "desc": "Catalog of 2,300+ self-hostable open-source applications across communication, file transfer, smart home, and more.",
     "keywords": ["self-hosted", "open source", "homelab", "selfhost"],
     "gumroad": "self-hosted-software-directory", "price": 14},
    {"slug": "design-resources", "name": "Design Resources Directory", "records": "2,100+",
     "desc": "Catalog of 2,100+ design resources across design systems, UI kits, icons, illustrations, stock photos, and tools.",
     "keywords": ["design", "ui kits", "icons", "illustrations", "design systems"],
     "gumroad": "design-resources", "price": 9},
    {"slug": "ai-agents", "name": "AI Agents Directory", "records": "2,000+",
     "desc": "Catalog of 2,000+ AI agent projects and frameworks — autonomous agents, multi-agent systems, agent-as-a-service tools.",
     "keywords": ["ai agents", "autonomous agents", "agent frameworks", "llm agents"],
     "gumroad": "ai-agents-directory", "price": 7},
    {"slug": "ai-prompts", "name": "AI Prompts Directory", "records": "1,700+",
     "desc": "Catalog of 1,700+ AI prompts across text, structured, and image generation — categorized for developer workflows.",
     "keywords": ["ai prompts", "prompt engineering", "llm prompts", "chatgpt prompts"],
     "gumroad": "ai-prompts-directory", "price": 9},
    {"slug": "developer-tools", "name": "Developer Tools Directory", "records": "1,500+",
     "desc": "Catalog of 1,500+ developer tools across CLI tools, code editors, debuggers, profilers, and productivity utilities.",
     "keywords": ["developer tools", "dev tools", "cli tools", "productivity"],
     "gumroad": "developer-tools-directory", "price": 9},
    {"slug": "open-source-alternatives", "name": "Open Source Alternatives Directory", "records": "900+",
     "desc": "Catalog of 900+ open-source alternatives to popular commercial software — each entry maps a proprietary product to OSS equivalents.",
     "keywords": ["open source", "alternatives", "saas alternatives", "self-hostable"],
     "gumroad": "open-source-alternatives", "price": 7},
    {"slug": "ai-models-pricing", "name": "AI Models & Providers Pricing Matrix", "records": "800+",
     "desc": "Catalog of 800+ AI model endpoints with per-token pricing (prompt + completion), context length, modality, uptime, across providers and quantizations.",
     "keywords": ["ai models pricing", "llm pricing", "openrouter", "model api cost"],
     "gumroad": "ai-models-pricing-matrix", "price": 11},
    {"slug": "no-code-lowcode", "name": "No-Code & Low-Code Tools Directory", "records": "500+",
     "desc": "Catalog of 500+ no-code and low-code tools across automation, app builders, internal tools, and integration platforms.",
     "keywords": ["no-code", "low-code", "automation", "app builders"],
     "gumroad": "no-code-lowcode", "price": 7},
    {"slug": "llmops-and-eval", "name": "LLMOps & Eval Tooling Directory", "records": "490+",
     "desc": "Catalog of 490+ LLM platform tools spanning evaluation frameworks, observability, prompt management, model serving, fine-tuning, routing/gateway, guardrails, and agent frameworks.",
     "keywords": ["llmops", "llm evaluation", "ai observability", "prompt management", "model serving"],
     "gumroad": "llmops-and-eval-tooling-directory", "price": 11},
    {"slug": "platform-engineering", "name": "Platform Engineering & IDP Tooling Directory", "records": "390+",
     "desc": "Catalog of 390+ platform engineering tools across developer portals, GitOps, service mesh, IaC, observability, container orchestration, CI/CD, secrets, policy, feature flags, service catalog, cost management, and DX.",
     "keywords": ["platform engineering", "idp", "developer portal", "gitops", "devops"],
     "gumroad": "platform-engineering-tooling-directory", "price": 11},
    {"slug": "vector-db-and-rag", "name": "Vector DB & RAG Infrastructure Directory", "records": "190+",
     "desc": "Catalog of 190+ vector databases and RAG infrastructure tools — embeddings stores, retrieval engines, RAG frameworks, hybrid-search backends.",
     "keywords": ["vector database", "rag", "embeddings", "retrieval", "semantic search"],
     "gumroad": "vector-db-and-rag-infrastructure", "price": 11},
]

DETAIL_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{name} — Free Sample (CSV + JSON)</title>
<meta name="description" content="{desc} Free sample: 20 records in JSON + CSV. Full dataset ${price} on Gumroad.">
<link rel="canonical" href="https://futdevpro.github.io/niche-datasets-free/{slug}.html">
<style>
  body{{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;max-width:760px;margin:0 auto;padding:2rem 1.25rem;line-height:1.55;color:#1a1a1a}}
  h1{{font-size:1.6rem;margin-bottom:.25rem}}
  h2{{font-size:1.1rem;margin-top:2rem;border-bottom:1px solid #eee;padding-bottom:.25rem}}
  a{{color:#0969da}}
  .lead{{color:#444}}
  .meta{{color:#666;font-size:.9rem;margin:0 0 1rem 0}}
  .cta{{display:inline-block;margin-top:1rem;padding:.6rem 1rem;background:#0969da;color:white;border-radius:6px;text-decoration:none;font-weight:600}}
  ul.dl{{list-style:none;padding-left:0}}
  ul.dl li{{padding:.4rem 0;border-bottom:1px solid #f0f0f0}}
  footer{{margin-top:3rem;padding-top:1rem;border-top:1px solid #eee;font-size:.85rem;color:#666}}
  .nav{{font-size:.9rem;color:#666;margin-bottom:1rem}}
  ol.use-cases{{padding-left:1.2rem}}
  ol.use-cases li{{padding:.45rem 0;line-height:1.5}}
</style>
</head>
<body>

<p class="nav"><a href="./">← All 20 datasets</a></p>

<h1>{name}</h1>
<p class="meta">{records} records · Free sample (20 records, JSON + CSV) · Full dataset ${price}</p>
<p class="lead">{desc}</p>

<h2>What you'd use this for</h2>
{use_cases_html}

<h2>Free sample (20 records)</h2>
<ul class="dl">
  <li><a href="{slug}-sample.json">{slug}-sample.json</a> — JSON format</li>
  <li><a href="{slug}-sample.csv">{slug}-sample.csv</a> — CSV format</li>
</ul>

<h2>Full dataset</h2>
<p>The full <strong>{records}</strong> records with all enrichment fields, semantic enum tiers, and category buckets:</p>
<a class="cta" href="https://jhonnyronnie.gumroad.com/l/{gumroad}">Get on Gumroad — ${price}</a>
<p class="meta" style="margin-top:1rem">Or save with a themed sub-bundle (<a href="./#bundles">Dev Stack Pack / Platform Builder Pack / ML Builder Pack — $24–$29</a>) or the full <a href="https://jhonnyronnie.gumroad.com/l/developer-data-bundle">Complete Developer Data Bundle ($34, 83% off)</a>.</p>

<h2>Schema + format</h2>
<p>Each record follows a normalized schema with at minimum <code>name</code>, <code>url</code>, <code>description</code>, <code>category</code>, <code>pricing</code>, <code>hasApi</code>, <code>tags</code>, plus dataset-specific first-class fields. See the <a href="https://github.com/futdevpro/niche-datasets-free#format">repo README</a> for the full field reference.</p>

<footer>
Part of <a href="./">Niche Datasets — 20 curated developer and AI datasets</a>. Built by <a href="https://github.com/jhonny-ronnie">Ronnie J</a> at <a href="https://github.com/futdevpro">Future Development Program</a>. Samples MIT-style permissive for evaluation; full datasets per <a href="https://jhonnyronnie.gumroad.com">Gumroad terms</a>.
</footer>

<script type="application/ld+json">
{jsonld}
</script>

</body>
</html>
"""


def load_use_cases(slug, repo_root):
    """Read sibling repo's __agent/content/<slug>/use-cases.md and convert to HTML.

    Returns HTML <ul>...</ul> with one <li> per use-case. Strips the markdown title
    line and the trailing version footer. Falls back to '' if file unreachable so
    detail-page generation never blocks on missing prose.
    """
    sibling_path = os.path.normpath(
        os.path.join(repo_root, "..", "niche-datasets", "__agent", "content", slug, "use-cases.md")
    )
    if not os.path.isfile(sibling_path):
        return ""
    with open(sibling_path, "r", encoding="utf-8") as f:
        text = f.read()
    # Drop the H1 + the trailing "*v1 — date — Wonnie*" footer line.
    text = re.sub(r"^#\s.*?\n", "", text, count=1)
    text = re.sub(r"\n---\s*\n\s*\*v\d.*?\*\s*$", "", text, flags=re.DOTALL)
    # Each use-case is "## N. Title\nbody..."; turn into <li><strong>Title</strong>: body</li>.
    items = []
    for block in re.split(r"\n(?=##\s)", text.strip()):
        m = re.match(r"##\s*\d+\.\s*(.+?)\n+(.+)", block, flags=re.DOTALL)
        if not m:
            continue
        title = m.group(1).strip()
        body = " ".join(m.group(2).strip().split())
        # Escape HTML in title/body for safety (use-cases authored by humans, but defensive).
        title_safe = title.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        body_safe = body.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        # Re-render inline `code` back to <code>.
        body_safe = re.sub(r"`([^`]+)`", r"<code>\1</code>", body_safe)
        items.append(f"  <li><strong>{title_safe}</strong> — {body_safe}</li>")
    if not items:
        return ""
    return "<ol class='use-cases'>\n" + "\n".join(items) + "\n</ol>"


def build_jsonld(d):
    return json.dumps({
        "@context": "https://schema.org/",
        "@type": "Dataset",
        "name": d["name"],
        "description": f"{d['desc']} Free sample: 20 records.",
        "url": f"https://futdevpro.github.io/niche-datasets-free/{d['slug']}.html",
        "keywords": d["keywords"],
        "license": "https://opensource.org/licenses/MIT",
        "creator": {
            "@type": "Organization",
            "name": "Future Development Program",
            "url": "https://github.com/futdevpro",
        },
        "distribution": [
            {"@type": "DataDownload", "encodingFormat": "application/json",
             "contentUrl": f"https://raw.githubusercontent.com/futdevpro/niche-datasets-free/main/{d['slug']}-sample.json"},
            {"@type": "DataDownload", "encodingFormat": "text/csv",
             "contentUrl": f"https://raw.githubusercontent.com/futdevpro/niche-datasets-free/main/{d['slug']}-sample.csv"},
        ],
        "offers": {
            "@type": "Offer",
            "price": d["price"],
            "priceCurrency": "USD",
            "url": f"https://jhonnyronnie.gumroad.com/l/{d['gumroad']}",
        },
    }, indent=2)


def build_sitemap():
    today = "2026-05-17"
    urls = [
        ("https://futdevpro.github.io/niche-datasets-free/", "1.0"),
        ("https://futdevpro.github.io/niche-datasets-free/faq.html", "0.7"),
    ] + [
        (f"https://futdevpro.github.io/niche-datasets-free/{d['slug']}.html", "0.8")
        for d in DATASETS
    ]
    body = "\n".join(
        f"  <url>\n    <loc>{u}</loc>\n    <lastmod>{today}</lastmod>\n    <changefreq>monthly</changefreq>\n    <priority>{p}</priority>\n  </url>"
        for u, p in urls
    )
    return f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{body}\n</urlset>\n'


def build_index_jsonld():
    """DataCatalog wrapper with 20 Dataset entries, each pointing to its own detail page."""
    datasets = []
    for d in DATASETS:
        datasets.append({
            "@type": "Dataset",
            "name": d["name"],
            "description": f"{d['desc']} Free sample: 20 records.",
            "url": f"https://futdevpro.github.io/niche-datasets-free/{d['slug']}.html",
            "keywords": d["keywords"],
            "license": "https://opensource.org/licenses/MIT",
            "creator": {"@type": "Organization", "name": "Future Development Program"},
            "distribution": [
                {"@type": "DataDownload", "encodingFormat": "application/json",
                 "contentUrl": f"https://raw.githubusercontent.com/futdevpro/niche-datasets-free/main/{d['slug']}-sample.json"},
                {"@type": "DataDownload", "encodingFormat": "text/csv",
                 "contentUrl": f"https://raw.githubusercontent.com/futdevpro/niche-datasets-free/main/{d['slug']}-sample.csv"},
            ],
        })
    return json.dumps({
        "@context": "https://schema.org/",
        "@type": "DataCatalog",
        "name": "Niche Datasets — Free Samples",
        "description": "Free 20-record samples of 20 curated developer and AI datasets: npm packages, MCP servers, HuggingFace models and datasets, Homebrew formulae, VS Code extensions, AI tools, AI agents, AI prompts, AI models pricing, public APIs, developer tools, self-hosted software, open-source alternatives, vector-DB / RAG infrastructure, LLMOps tooling, platform engineering, cybersecurity tools, design resources, no-code/low-code tools.",
        "url": "https://futdevpro.github.io/niche-datasets-free/",
        "keywords": ["datasets", "developer tools", "npm packages", "mcp servers", "huggingface", "homebrew", "vscode extensions", "ai tools", "public apis", "vector database", "structured data"],
        "creator": {
            "@type": "Organization",
            "name": "Future Development Program",
            "url": "https://github.com/futdevpro",
        },
        "dataset": datasets,
    }, indent=2)


def update_index_jsonld(repo_root):
    """Replace the existing <script type="application/ld+json">...</script> block in index.html
    with regenerated content where each Dataset.url points to its detail page."""
    import re
    path = os.path.join(repo_root, "index.html")
    with open(path, "r", encoding="utf-8") as f:
        html = f.read()
    new_block = '<script type="application/ld+json">\n' + build_index_jsonld() + '\n</script>'
    pattern = re.compile(r'<script type="application/ld\+json">.*?</script>', flags=re.DOTALL)
    if not pattern.search(html):
        raise RuntimeError("index.html JSON-LD block not found — refusing to write")
    updated = pattern.sub(lambda m: new_block, html, count=1)
    with open(path, "w", encoding="utf-8") as f:
        f.write(updated)


def main():
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    count = 0
    use_case_hits = 0
    for d in DATASETS:
        use_cases_html = load_use_cases(d["slug"], repo_root)
        if use_cases_html:
            use_case_hits += 1
        else:
            use_cases_html = "<p class='meta'>Use-cases coming soon.</p>"
        html = DETAIL_TEMPLATE.format(
            name=d["name"], desc=d["desc"], records=d["records"],
            slug=d["slug"], gumroad=d["gumroad"], price=d["price"],
            jsonld=build_jsonld(d),
            use_cases_html=use_cases_html,
        )
        path = os.path.join(repo_root, f"{d['slug']}.html")
        with open(path, "w", encoding="utf-8") as f:
            f.write(html)
        count += 1
    sitemap_path = os.path.join(repo_root, "sitemap.xml")
    with open(sitemap_path, "w", encoding="utf-8") as f:
        f.write(build_sitemap())
    update_index_jsonld(repo_root)
    print(f"Generated {count} detail pages + sitemap.xml ({len(DATASETS)+2} URLs: root + faq + 20 detail) + updated index.html JSON-LD. Use-cases injected: {use_case_hits}/{count}.")


if __name__ == "__main__":
    main()
