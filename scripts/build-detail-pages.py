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
import datetime
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
     "gumroad": "homebrew-packages-directory", "price": 11,
     "related": ["npm-packages", "vscode-extensions", "developer-tools"]},
    {"slug": "npm-packages", "name": "npm Packages Directory", "records": "6,300+",
     "desc": "Catalog of 6,300+ top JavaScript/TypeScript npm packages with weekly/monthly downloads, dependents count, npm score (popularity/quality/maintenance), and repository.",
     "keywords": ["npm", "javascript", "typescript", "packages"],
     "gumroad": "npm-packages-directory", "price": 11,
     "related": ["homebrew-packages", "vscode-extensions", "developer-tools"]},
    {"slug": "vscode-extensions", "name": "VS Code Extensions Directory", "records": "4,800+",
     "desc": "Catalog of 4,800+ VS Code Marketplace extensions with install counts, version, last-updated, extension ID, and publisher.",
     "keywords": ["vscode", "extensions", "ide", "developer tools"],
     "gumroad": "vscode-extensions-directory", "price": 9,
     "related": ["npm-packages", "homebrew-packages", "developer-tools"]},
    {"slug": "huggingface-models", "name": "HuggingFace Models Directory", "records": "4,000",
     "desc": "Catalog of 4,000 most-downloaded HuggingFace models with downloads, likes, license, pipeline tag, modality, and language.",
     "keywords": ["huggingface", "machine learning", "models", "ai"],
     "gumroad": "huggingface-models-directory", "price": 11,
     "related": ["huggingface-datasets", "ai-models-pricing", "ai-agents"]},
    {"slug": "mcp-servers", "name": "Open MCP Servers Directory", "records": "3,600+",
     "desc": "Catalog of 3,600+ Model Context Protocol (MCP) servers with GitHub stars, category, and capabilities.",
     "keywords": ["mcp", "model context protocol", "ai agents", "tooling"],
     "gumroad": "mcp-servers-directory", "price": 9,
     "related": ["ai-agents", "ai-tools", "llmops-and-eval"]},
    {"slug": "ai-tools", "name": "AI Tools Directory", "records": "2,800+",
     "desc": "Catalog of 2,800+ AI tools and applications with category, pricing model, and API availability.",
     "keywords": ["ai tools", "artificial intelligence", "saas"],
     "gumroad": "ai-tools-directory", "price": 9,
     "related": ["ai-agents", "ai-prompts", "no-code-lowcode"]},
    {"slug": "cybersecurity-tools", "name": "Cybersecurity Tools Directory", "records": "2,700+",
     "desc": "Catalog of 2,700+ cybersecurity tools across pentesting, defensive, forensics, and monitoring categories.",
     "keywords": ["cybersecurity", "infosec", "pentesting", "security tools"],
     "gumroad": "cybersecurity-tools", "price": 9,
     "related": ["open-source-alternatives", "self-hosted-software", "developer-tools"]},
    {"slug": "huggingface-datasets", "name": "HuggingFace Datasets Directory", "records": "2,800+",
     "desc": "Catalog of 2,800+ most-downloaded HuggingFace datasets with downloads, likes, license, task categories, and language.",
     "keywords": ["huggingface", "datasets", "machine learning", "training data"],
     "gumroad": "huggingface-datasets-directory", "price": 11,
     "related": ["huggingface-models", "ai-prompts", "llmops-and-eval"]},
    {"slug": "public-apis", "name": "Public APIs Directory", "records": "2,600+",
     "desc": "Catalog of 2,600+ free and freemium public APIs with auth, HTTPS, and CORS flags per row, across 50+ categories.",
     "keywords": ["public apis", "rest api", "free api", "no-auth api"],
     "gumroad": "public-apis-directory", "price": 12,
     "related": ["developer-tools", "npm-packages", "ai-tools"]},
    {"slug": "self-hosted-software", "name": "Self-Hosted Software Directory", "records": "2,200+",
     "desc": "Catalog of 2,300+ self-hostable open-source applications across communication, file transfer, smart home, and more.",
     "keywords": ["self-hosted", "open source", "homelab", "selfhost"],
     "gumroad": "self-hosted-software-directory", "price": 14,
     "related": ["open-source-alternatives", "platform-engineering", "cybersecurity-tools"]},
    {"slug": "design-resources", "name": "Design Resources Directory", "records": "2,100+",
     "desc": "Catalog of 2,100+ design resources across design systems, UI kits, icons, illustrations, stock photos, and tools.",
     "keywords": ["design", "ui kits", "icons", "illustrations", "design systems"],
     "gumroad": "design-resources", "price": 9,
     "related": ["ai-tools", "no-code-lowcode", "developer-tools"]},
    {"slug": "ai-agents", "name": "AI Agents Directory", "records": "2,000+",
     "desc": "Catalog of 2,000+ AI agent projects and frameworks — autonomous agents, multi-agent systems, agent-as-a-service tools.",
     "keywords": ["ai agents", "autonomous agents", "agent frameworks", "llm agents"],
     "gumroad": "ai-agents-directory", "price": 7,
     "related": ["mcp-servers", "llmops-and-eval", "ai-tools"]},
    {"slug": "ai-prompts", "name": "AI Prompts Directory", "records": "1,800+",
     "desc": "Catalog of 1,800+ AI prompts across text, structured, and image generation — categorized for developer workflows.",
     "keywords": ["ai prompts", "prompt engineering", "llm prompts", "chatgpt prompts"],
     "gumroad": "ai-prompts-directory", "price": 9,
     "related": ["ai-tools", "ai-agents", "huggingface-datasets"]},
    {"slug": "developer-tools", "name": "Developer Tools Directory", "records": "1,600+",
     "desc": "Catalog of 1,600+ developer tools across CLI tools, code editors, debuggers, profilers, and productivity utilities.",
     "keywords": ["developer tools", "dev tools", "cli tools", "productivity"],
     "gumroad": "developer-tools-directory", "price": 9,
     "related": ["npm-packages", "homebrew-packages", "vscode-extensions"]},
    {"slug": "open-source-alternatives", "name": "Open Source Alternatives Directory", "records": "900+",
     "desc": "Catalog of 900+ open-source alternatives to popular commercial software — each entry maps a proprietary product to OSS equivalents.",
     "keywords": ["open source", "alternatives", "saas alternatives", "self-hostable"],
     "gumroad": "open-source-alternatives", "price": 7,
     "related": ["self-hosted-software", "cybersecurity-tools", "no-code-lowcode"]},
    {"slug": "ai-models-pricing", "name": "AI Models & Providers Pricing Matrix", "records": "800+",
     "desc": "Catalog of 800+ AI model endpoints with per-token pricing (prompt + completion), context length, modality, uptime, across providers and quantizations.",
     "keywords": ["ai models pricing", "llm pricing", "openrouter", "model api cost"],
     "gumroad": "ai-models-pricing-matrix", "price": 11,
     "related": ["huggingface-models", "llmops-and-eval", "ai-agents"]},
    {"slug": "no-code-lowcode", "name": "No-Code & Low-Code Tools Directory", "records": "500+",
     "desc": "Catalog of 500+ no-code and low-code tools across automation, app builders, internal tools, and integration platforms.",
     "keywords": ["no-code", "low-code", "automation", "app builders"],
     "gumroad": "no-code-lowcode", "price": 7,
     "related": ["ai-tools", "open-source-alternatives", "design-resources"]},
    {"slug": "llmops-and-eval", "name": "LLMOps & Eval Tooling Directory", "records": "500+",
     "desc": "Catalog of 490+ LLM platform tools spanning evaluation frameworks, observability, prompt management, model serving, fine-tuning, routing/gateway, guardrails, and agent frameworks.",
     "keywords": ["llmops", "llm evaluation", "ai observability", "prompt management", "model serving"],
     "gumroad": "llmops-and-eval-tooling-directory", "price": 11,
     "related": ["vector-db-and-rag", "ai-models-pricing", "ai-agents"]},
    {"slug": "platform-engineering", "name": "Platform Engineering & IDP Tooling Directory", "records": "390+",
     "desc": "Catalog of 390+ platform engineering tools across developer portals, GitOps, service mesh, IaC, observability, container orchestration, CI/CD, secrets, policy, feature flags, service catalog, cost management, and DX.",
     "keywords": ["platform engineering", "idp", "developer portal", "gitops", "devops"],
     "gumroad": "platform-engineering-tooling-directory", "price": 11,
     "related": ["self-hosted-software", "developer-tools", "mcp-servers"]},
    {"slug": "vector-db-and-rag", "name": "Vector DB & RAG Infrastructure Directory", "records": "200+",
     "desc": "Catalog of 190+ vector databases and RAG infrastructure tools — embeddings stores, retrieval engines, RAG frameworks, hybrid-search backends.",
     "keywords": ["vector database", "rag", "embeddings", "retrieval", "semantic search"],
     "gumroad": "vector-db-and-rag-infrastructure", "price": 11,
     "related": ["llmops-and-eval", "huggingface-datasets", "ai-models-pricing"]},
]

DETAIL_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{name} — Free Sample (CSV + JSON)</title>
<meta name="description" content="{desc} Free sample: 30 records in JSON + CSV. Full dataset ${price} on Gumroad.">
<link rel="canonical" href="https://futdevpro.github.io/niche-datasets-free/{slug}.html">
<link rel="alternate" type="application/rss+xml" title="Niche Datasets — Refresh Feed" href="feed.xml">
<link rel="alternate" type="application/json" title="{name} — JSON metadata" href="{slug}-meta.json">
<meta property="og:type" content="website">
<meta property="og:url" content="https://futdevpro.github.io/niche-datasets-free/{slug}.html">
<meta property="og:title" content="{name} — Free Sample (CSV + JSON)">
<meta property="og:description" content="{desc} Free sample: 30 records in JSON + CSV. Full dataset ${price} on Gumroad.">
<meta property="og:site_name" content="Niche Datasets">
<meta property="og:image" content="https://futdevpro.github.io/niche-datasets-free/og-cover.svg">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{name} — Free Sample">
<meta name="twitter:description" content="{records} records · {desc} Free sample 30 records. Full ${price}.">
<meta name="twitter:image" content="https://futdevpro.github.io/niche-datasets-free/og-cover.svg">
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
  ol.preview{{padding-left:1.2rem;font-size:.93rem}}
  ol.preview li{{padding:.5rem 0;line-height:1.45;border-bottom:1px solid #f4f4f4}}
  ol.preview .name{{font-weight:600}}
  ol.preview .tags{{color:#888;font-size:.85em}}
  ol.preview a{{font-size:.88em;word-break:break-all}}
  .badge{{display:inline-block;padding:.1rem .45rem;background:#e6f4ea;color:#1e7a3a;border-radius:3px;font-size:.85em;font-weight:600}}
</style>
</head>
<body>

<p class="nav"><a href="./">← All 20 datasets</a> &nbsp;·&nbsp; <a href="quickstart.html">5-min quickstart</a> &nbsp;·&nbsp; <a href="examples.html">Code examples</a> &nbsp;·&nbsp; <a href="vs.html">vs. alternatives</a> &nbsp;·&nbsp; <a href="faq.html">FAQ</a></p>

<h1>{name}</h1>
<p class="meta">{records} records · Free sample (30 records, JSON + CSV) · Full dataset ${price} · <span class="badge">Sample refreshed {refresh_date}</span>{tier_badge}</p>
<p class="lead">{desc}</p>

<h2>What you'd use this for</h2>
{use_cases_html}

<h2>Sample preview (first 5 records)</h2>
{preview_html}

<h2>Free sample (30 records)</h2>
<ul class="dl">
  <li><a href="{slug}-sample.json">{slug}-sample.json</a> — JSON format</li>
  <li><a href="{slug}-sample.csv">{slug}-sample.csv</a> — CSV format</li>
</ul>

<h2>Full dataset</h2>
<p>The full <strong>{records}</strong> records with all enrichment fields, semantic enum tiers, and category buckets:</p>
<a class="cta" href="https://jhonnyronnie.gumroad.com/l/{gumroad}">Get on Gumroad — ${price}</a>
<p class="meta" style="margin-top:1rem">Or save with a themed sub-bundle (<a href="./#bundles">Dev Stack Pack / Platform Builder Pack / ML Builder Pack — $24–$29</a>).</p>

<h2>Related datasets</h2>
{related_html}

{cross_leverage_html}

<h2>Schema + format</h2>
<p>Each record follows a normalized schema with at minimum <code>name</code>, <code>url</code>, <code>description</code>, <code>category</code>, <code>pricing</code>, <code>hasApi</code>, <code>tags</code>, plus dataset-specific first-class fields. See the <a href="https://github.com/futdevpro/niche-datasets-free#format">repo README</a> for the full field reference.</p>

<footer>
Part of <a href="./">Niche Datasets — 20 curated developer and AI datasets</a>. Built by <a href="https://github.com/jhonny-ronnie">Ronnie J</a> at <a href="https://github.com/futdevpro">Future Development Program</a>. Samples MIT-style permissive for evaluation; full datasets per <a href="https://jhonnyronnie.gumroad.com">Gumroad terms</a>.
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


_SKIP_TIER_ENUMS = {
    "category", "pricing", "urlDomainTier", "categorizationTier",
    "descriptionLengthTier",
}


def count_tier_enums(slug, repo_root):
    """Count derived enum-tier fields in sibling repo's datasets/<slug>/config.json.

    Skips core auto-fields that exist on every dataset. Returns 0 if config not
    reachable or has no enum fields.
    """
    return len(list_tier_enums(slug, repo_root))


def list_tier_enums(slug, repo_root):
    """Return the list of derived enum-tier field names for a dataset.

    Sibling repo lookup, core auto-fields skipped. Empty list if config
    unreachable or has no enum fields.
    """
    sibling_path = os.path.normpath(
        os.path.join(repo_root, "..", "niche-datasets", "datasets", slug, "config.json")
    )
    if not os.path.isfile(sibling_path):
        return []
    try:
        with open(sibling_path, "r", encoding="utf-8") as f:
            cfg = __import__("json").load(f)
    except Exception:
        return []
    out = []
    for fld in cfg.get("schema", {}).get("fields", []):
        name = fld.get("name", "")
        if fld.get("type") == "enum" and name not in _SKIP_TIER_ENUMS:
            out.append(name)
    return out


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


def load_preview(slug, repo_root, n=5):
    """Load first N records from {slug}-sample.json and render as a structured <ol>.
    Each record shows name, description, url, category, pricing, tags — common across
    all 20 datasets. Returns '' if file unreachable."""
    path = os.path.join(repo_root, f"{slug}-sample.json")
    if not os.path.isfile(path):
        return ""
    with open(path, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except Exception:
            return ""
    if not isinstance(data, list) or not data:
        return ""

    def esc(s):
        return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    items = []
    for rec in data[:n]:
        if not isinstance(rec, dict):
            continue
        name = esc(rec.get("name", "(unnamed)"))
        desc = esc(rec.get("description", ""))[:240]
        url = rec.get("url", "")
        category = esc(rec.get("category", ""))
        pricing = esc(rec.get("pricing", ""))
        tags = rec.get("tags", [])
        if isinstance(tags, list):
            tags_str = esc(", ".join(str(t) for t in tags[:5]))
        else:
            tags_str = ""
        meta_bits = []
        if category:
            meta_bits.append(f"<code>{category}</code>")
        if pricing:
            meta_bits.append(f"<code>{pricing}</code>")
        meta_str = " · ".join(meta_bits)
        url_html = f'<a href="{esc(url)}" rel="nofollow noopener">{esc(url)}</a>' if url else ""
        items.append(
            f'  <li><span class="name">{name}</span> — {desc} '
            f'<br><small>{meta_str}{" · " if meta_str and url_html else ""}{url_html}</small>'
            f'{f"<br><span class=\"tags\">tags: {tags_str}</span>" if tags_str else ""}</li>'
        )
    if not items:
        return ""
    return "<ol class='preview'>\n" + "\n".join(items) + "\n</ol>"


def get_refresh_date(slug, repo_root):
    """Read mtime of {slug}-sample.json and format as YYYY-MM-DD. Falls back to today."""
    path = os.path.join(repo_root, f"{slug}-sample.json")
    if not os.path.isfile(path):
        return datetime.date.today().isoformat()
    return datetime.date.fromtimestamp(os.path.getmtime(path)).isoformat()


def build_related_html(d):
    by_slug = {x["slug"]: x for x in DATASETS}
    related_slugs = d.get("related", [])
    if not related_slugs:
        return "<p class='meta'>Browse all 20 on the <a href='./'>index</a>.</p>"
    items = []
    for s in related_slugs:
        r = by_slug.get(s)
        if not r:
            continue
        name_safe = r["name"].replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        records_safe = r["records"].replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        items.append(f'  <li><a href="{s}.html">{name_safe}</a> — {records_safe} records · ${r["price"]}</li>')
    return "<ul>\n" + "\n".join(items) + "\n</ul>"


def build_breadcrumb_jsonld(d):
    return json.dumps({
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Niche Datasets",
             "item": "https://futdevpro.github.io/niche-datasets-free/"},
            {"@type": "ListItem", "position": 2, "name": d["name"],
             "item": f"https://futdevpro.github.io/niche-datasets-free/{d['slug']}.html"},
        ],
    }, indent=2)


_BUNDLES = {
    # NOTE 2026-05-24: "developer-data-bundle" (all-20-dataset SKU) is currently
    # sold_out on Gumroad and not returned by /v2/products API. Removed from
    # graph until Doc re-publishes. See USER_INPUT.md [ACTION-REQUIRED 2026-05-24].
    "ml-builder-pack": {
        "name": "ML Builder Pack",
        "url": "https://jhonnyronnie.gumroad.com/l/ml-builder-pack",
        "members": {"ai-models-pricing", "huggingface-models", "huggingface-datasets",
                    "ai-prompts", "llmops-and-eval", "vector-db-and-rag"},
    },
    "platform-builder-pack": {
        "name": "Platform Builder Pack",
        "url": "https://jhonnyronnie.gumroad.com/l/platform-builder-pack",
        "members": {"platform-engineering", "self-hosted-software", "developer-tools",
                    "npm-packages", "homebrew-packages", "vscode-extensions"},
    },
    "dev-stack-pack": {
        "name": "Dev Stack Pack",
        "url": "https://jhonnyronnie.gumroad.com/l/dev-stack-pack",
        "members": {"npm-packages", "vscode-extensions", "homebrew-packages", "developer-tools"},
    },
}


def _bundle_membership(slug):
    """Returns list of bundles that contain this dataset as schema.org Product refs."""
    out = []
    for _key, b in _BUNDLES.items():
        if b["members"] is None or slug in b["members"]:
            out.append({"@type": "Product", "name": b["name"], "url": b["url"]})
    return out


def build_jsonld(d, repo_root=None):
    refresh_date = (
        get_refresh_date(d["slug"], repo_root) if repo_root else datetime.date.today().isoformat()
    )
    return json.dumps({
        "@context": "https://schema.org/",
        "@type": "Dataset",
        "name": d["name"],
        "description": f"{d['desc']} Free sample: 30 records.",
        "url": f"https://futdevpro.github.io/niche-datasets-free/{d['slug']}.html",
        "keywords": d["keywords"],
        "license": "https://opensource.org/licenses/MIT",
        "dateModified": refresh_date,
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
            "availability": "https://schema.org/InStock",
            "seller": {
                "@type": "Organization",
                "name": "Future Development Program",
                "url": "https://jhonnyronnie.gumroad.com/",
            },
        },
        "isPartOf": _bundle_membership(d["slug"]),
    }, indent=2)


def build_sitemap():
    today = datetime.date.today().isoformat()
    # (url, priority, changefreq)
    urls = [
        ("https://futdevpro.github.io/niche-datasets-free/",                                       "1.0", "weekly"),
        ("https://futdevpro.github.io/niche-datasets-free/buyers-guide.html",                      "0.9", "monthly"),
        ("https://futdevpro.github.io/niche-datasets-free/tiers.html",                             "0.9", "weekly"),
        ("https://futdevpro.github.io/niche-datasets-free/quickstart.html",                        "0.8", "monthly"),
        ("https://futdevpro.github.io/niche-datasets-free/api.html",                               "0.8", "monthly"),
        ("https://futdevpro.github.io/niche-datasets-free/examples.html",                          "0.7", "monthly"),
        ("https://futdevpro.github.io/niche-datasets-free/vs.html",                                "0.7", "monthly"),
        ("https://futdevpro.github.io/niche-datasets-free/faq.html",                               "0.7", "monthly"),
        ("https://futdevpro.github.io/niche-datasets-free/blog-2026-05-24-url-canonicalization.html","0.7", "yearly"),
        ("https://futdevpro.github.io/niche-datasets-free/blog-2026-05-23-3-day-update.html",      "0.7", "yearly"),
        ("https://futdevpro.github.io/niche-datasets-free/blog-2026-05-20-13-day-refresh.html",    "0.7", "yearly"),
        ("https://futdevpro.github.io/niche-datasets-free/blog-semantic-enum-tiers.html",          "0.7", "yearly"),
        ("https://futdevpro.github.io/niche-datasets-free/changelog.html",                         "0.6", "weekly"),
        ("https://futdevpro.github.io/niche-datasets-free/feed.xml",                               "0.6", "weekly"),
        ("https://futdevpro.github.io/niche-datasets-free/openapi.json",                           "0.5", "yearly"),
        ("https://futdevpro.github.io/niche-datasets-free/cross-dataset-overlap.json",             "0.6", "weekly"),
        ("https://futdevpro.github.io/niche-datasets-free/cross-leverage.html",                    "0.8", "weekly"),
        ("https://futdevpro.github.io/niche-datasets-free/llms.txt",                               "0.5", "monthly"),
    ] + [
        (f"https://futdevpro.github.io/niche-datasets-free/{d['slug']}.html", "0.8", "weekly")
        for d in DATASETS
    ]
    body = "\n".join(
        f"  <url>\n    <loc>{u}</loc>\n    <lastmod>{today}</lastmod>\n    <changefreq>{cf}</changefreq>\n    <priority>{p}</priority>\n  </url>"
        for u, p, cf in urls
    )
    return f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{body}\n</urlset>\n'


def build_index_jsonld(repo_root=None):
    """DataCatalog wrapper with 20 Dataset entries, each pointing to its own detail page."""
    today_iso = datetime.date.today().isoformat()
    datasets = []
    for d in DATASETS:
        refresh = (
            get_refresh_date(d["slug"], repo_root) if repo_root else today_iso
        )
        datasets.append({
            "@type": "Dataset",
            "name": d["name"],
            "description": f"{d['desc']} Free sample: 30 records.",
            "url": f"https://futdevpro.github.io/niche-datasets-free/{d['slug']}.html",
            "keywords": d["keywords"],
            "license": "https://opensource.org/licenses/MIT",
            "dateModified": refresh,
            "creator": {"@type": "Organization", "name": "Future Development Program"},
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
                "availability": "https://schema.org/InStock",
                "seller": {
                    "@type": "Organization",
                    "name": "Future Development Program",
                    "url": "https://jhonnyronnie.gumroad.com/",
                },
            },
            "isPartOf": _bundle_membership(d["slug"]),
        })
    return json.dumps({
        "@context": "https://schema.org/",
        "@type": "DataCatalog",
        "name": "Niche Datasets — Free Samples",
        "description": "Free 30-record samples of 20 curated developer and AI datasets: npm packages, MCP servers, HuggingFace models and datasets, Homebrew formulae, VS Code extensions, AI tools, AI agents, AI prompts, AI models pricing, public APIs, developer tools, self-hosted software, open-source alternatives, vector-DB / RAG infrastructure, LLMOps tooling, platform engineering, cybersecurity tools, design resources, no-code/low-code tools.",
        "url": "https://futdevpro.github.io/niche-datasets-free/",
        "keywords": ["datasets", "developer tools", "npm packages", "mcp servers", "huggingface", "homebrew", "vscode extensions", "ai tools", "public apis", "vector database", "structured data"],
        "dateModified": today_iso,
        "creator": {
            "@type": "Organization",
            "name": "Future Development Program",
            "url": "https://github.com/futdevpro",
        },
        "dataset": datasets,
    }, indent=2)


def auto_records_floor(slug, repo_root, fallback):
    """Compute the displayed 'X,XXX+' floor from the live data file.

    Bumps automatically when actual exceeds the static fallback floor by a
    full bump-unit (100 for sub-10k datasets, 1000 for 10k+). Falls back
    to the hand-maintained `fallback` string when the data file isn't
    reachable, or when actual hasn't crossed the next bump-threshold yet
    (so a hand-floor of '4,000' on huggingface-models stays as-is).
    """
    data_path = os.path.normpath(
        os.path.join(repo_root, "..", "niche-datasets", "datasets", slug, "data", f"{slug}.json")
    )
    if not os.path.isfile(data_path):
        return fallback
    try:
        with open(data_path, "r", encoding="utf-8") as f:
            actual = len(__import__("json").load(f))
    except Exception:
        return fallback
    # Parse fallback floor like '4,800+' or '4,000'
    has_plus = fallback.endswith("+")
    floor_str = fallback.rstrip("+").replace(",", "")
    try:
        floor = int(floor_str)
    except ValueError:
        return fallback
    bump = 1000 if floor >= 10000 else 100
    new_floor = (actual // bump) * bump
    if new_floor >= floor + bump:
        return f"{new_floor:,}+"
    return fallback


def build_index_table_html(repo_root=None):
    """Generate the homepage <tbody> rows from the DATASETS list.

    Single source of truth for record-count floors: when DATASETS bumps,
    rebuild auto-syncs the table. Also auto-bumps the displayed floor
    when live actual exceeds the static floor by a full bump-unit.
    """
    rows = []
    for d in DATASETS:
        name = d["name"].replace("&", "&amp;")
        slug = d["slug"]
        records = (
            auto_records_floor(slug, repo_root, d["records"])
            if repo_root else d["records"]
        )
        rows.append(
            f'<tr><td>{name}</td><td>{records}</td>'
            f'<td><a href="{slug}-sample.json">JSON</a> · '
            f'<a href="{slug}-sample.csv">CSV</a></td></tr>'
        )
    return "\n".join(rows)


def update_index_table(repo_root):
    """Replace the index.html dataset <tbody> with regenerated rows.

    Operates on the table that lives between <tbody> and </tbody>.
    """
    import re
    path = os.path.join(repo_root, "index.html")
    with open(path, "r", encoding="utf-8") as f:
        html = f.read()
    new_body = build_index_table_html(repo_root)
    # Match the FIRST <tbody>...</tbody> block (the dataset table).
    pattern = re.compile(r'(<tbody>)(.*?)(</tbody>)', flags=re.DOTALL)
    if not pattern.search(html):
        raise RuntimeError("index.html <tbody> block not found — refusing to write")
    updated = pattern.sub(lambda m: f'{m.group(1)}\n{new_body}\n{m.group(3)}', html, count=1)
    with open(path, "w", encoding="utf-8") as f:
        f.write(updated)


def update_index_jsonld(repo_root):
    """Replace the existing <script type="application/ld+json">...</script> block in index.html
    with regenerated content where each Dataset.url points to its detail page."""
    import re
    path = os.path.join(repo_root, "index.html")
    with open(path, "r", encoding="utf-8") as f:
        html = f.read()
    new_block = '<script type="application/ld+json">\n' + build_index_jsonld(repo_root) + '\n</script>'
    pattern = re.compile(r'<script type="application/ld\+json">.*?</script>', flags=re.DOTALL)
    if not pattern.search(html):
        raise RuntimeError("index.html JSON-LD block not found — refusing to write")
    updated = pattern.sub(lambda m: new_block, html, count=1)
    with open(path, "w", encoding="utf-8") as f:
        f.write(updated)


def _live_record_count(slug, repo_root):
    """Read the exact record count from the live data file. Returns None on
    any failure (file missing, parse error, repo_root unset)."""
    if not repo_root:
        return None
    data_path = os.path.normpath(
        os.path.join(repo_root, "..", "niche-datasets", "datasets", slug, "data", f"{slug}.json")
    )
    if not os.path.isfile(data_path):
        return None
    try:
        with open(data_path, "r", encoding="utf-8") as f:
            return len(__import__("json").load(f))
    except Exception:
        return None


def build_dataset_endpoint(d, repo_root):
    """Per-dataset metadata endpoint at /<slug>-meta.json.

    Same shape as one dataset entry inside /datasets.json plus:
    - lastRefreshed (sample-file mtime)
    - liveRecordCount (exact int from the live data file) — agents that
      need precision use this; marketing-shaped recordCount ('X,XXX+')
      stays for human-facing surfaces.
    """
    site = "https://futdevpro.github.io/niche-datasets-free"
    raw = "https://raw.githubusercontent.com/futdevpro/niche-datasets-free/main"
    out = {
        "schemaVersion": "1.0",
        "slug": d["slug"],
        "name": d["name"],
        "recordCount": d["records"],
        "description": d["desc"],
        "keywords": d["keywords"],
        "license": "https://opensource.org/licenses/MIT",
        "lastRefreshed": get_refresh_date(d["slug"], repo_root),
        "sampleJsonUrl": f"{raw}/{d['slug']}-sample.json",
        "sampleCsvUrl": f"{raw}/{d['slug']}-sample.csv",
        "detailPageUrl": f"{site}/{d['slug']}.html",
        "fullDatasetPriceUsd": d["price"],
        "fullDatasetUrl": f"https://jhonnyronnie.gumroad.com/l/{d['gumroad']}",
        "related": d.get("related", []),
        "catalogUrl": f"{site}/datasets.json",
        "bundles": [
            {"name": b["name"], "url": b["url"]}
            for b in _bundle_membership(d["slug"])
        ],
    }
    live = _live_record_count(d["slug"], repo_root)
    if live is not None:
        out["liveRecordCount"] = live
    return json.dumps(out, indent=2)


def build_feed_xml(repo_root):
    """RSS 2.0 feed of refresh events. Each dataset gets one <item> per known refresh,
    derived from sample-file mtime. Subscribers (feed-aggregator bots, Bing's
    feed-following crawler, individual devs) learn about new data on each refresh."""
    site = "https://futdevpro.github.io/niche-datasets-free"
    items = []
    # Sort datasets by mtime DESC so newest refresh is on top
    annotated = [(d, get_refresh_date(d["slug"], repo_root)) for d in DATASETS]
    annotated.sort(key=lambda x: x[1], reverse=True)
    for d, refresh in annotated:
        items.append(f"""    <item>
      <title>{esc_xml(d['name'])} — refreshed {refresh}</title>
      <link>{site}/{d['slug']}.html</link>
      <guid isPermaLink="false">{d['slug']}-{refresh}</guid>
      <pubDate>{format_rfc822(refresh)}</pubDate>
      <description>{esc_xml(d['desc'])} Full dataset ${d['price']} on Gumroad.</description>
    </item>""")
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>Niche Datasets — Refresh Feed</title>
    <link>{site}/</link>
    <atom:link href="{site}/feed.xml" rel="self" type="application/rss+xml"/>
    <description>Refresh notifications for the 20 curated developer and AI dataset samples. One item per dataset, updated on each monthly/quarterly refresh.</description>
    <language>en-us</language>
    <generator>build-detail-pages.py</generator>
{chr(10).join(items)}
  </channel>
</rss>
"""


def esc_xml(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def format_rfc822(iso_date):
    """Convert YYYY-MM-DD to RFC 822 (RSS pubDate format)."""
    d = datetime.date.fromisoformat(iso_date)
    # Assume midnight UTC; good enough for daily-precision data
    return d.strftime("%a, %d %b %Y 00:00:00 +0000")


def build_catalog_json(repo_root=None):
    """Machine-readable catalog endpoint. Consumed by AI agents / aggregator bots /
    programmatic discovery. Stable shape: top-level metadata + datasets[] array.
    Versioned via 'schemaVersion' so consumers can adapt to future changes.

    Each dataset entry includes liveRecordCount (exact int from live data file)
    alongside the marketing-shaped recordCount string."""
    site = "https://futdevpro.github.io/niche-datasets-free"
    raw = "https://raw.githubusercontent.com/futdevpro/niche-datasets-free/main"
    datasets = []
    for d in DATASETS:
        entry = {
            "slug": d["slug"],
            "name": d["name"],
            "recordCount": d["records"],
            "description": d["desc"],
            "keywords": d["keywords"],
            "license": "https://opensource.org/licenses/MIT",
            "sampleJsonUrl": f"{raw}/{d['slug']}-sample.json",
            "sampleCsvUrl": f"{raw}/{d['slug']}-sample.csv",
            "detailPageUrl": f"{site}/{d['slug']}.html",
            "fullDatasetPriceUsd": d["price"],
            "fullDatasetUrl": f"https://jhonnyronnie.gumroad.com/l/{d['gumroad']}",
            "related": d.get("related", []),
            "bundles": [
                {"name": b["name"], "url": b["url"]}
                for b in _bundle_membership(d["slug"])
            ],
        }
        live = _live_record_count(d["slug"], repo_root)
        if live is not None:
            entry["liveRecordCount"] = live
        datasets.append(entry)
    return json.dumps({
        "schemaVersion": "1.0",
        "name": "Niche Datasets — Free Samples Catalog",
        "description": "20 curated developer and AI dataset samples with per-dataset metadata, download URLs (JSON + CSV), prices, and related datasets. Machine-readable; safe for programmatic enumeration.",
        "homepage": site + "/",
        "license": "https://opensource.org/licenses/MIT",
        "publisher": {
            "name": "Future Development Program",
            "url": "https://github.com/futdevpro",
        },
        "datasetCount": len(DATASETS),
        "datasets": datasets,
    }, indent=2)


def build_cross_dataset_overlap_json(repo_root):
    """Catalog endpoint listing URLs that appear in 3+ datasets — the
    high-cross-leverage tools in the catalog. Useful for buyer-agents doing
    market-mapping ("which tools span the most developer niches?") and for
    cross-sell discovery ("buyers of vector-db-and-rag likely also want
    ai-agents because Qdrant appears in both").

    Source-of-truth: live data files under ../niche-datasets/datasets/<slug>/data/.
    Threshold of 3+ keeps the output to a manageable ~200 entries (vs ~1,300 at 2+).
    """
    from collections import defaultdict
    url_to_entries = defaultdict(list)
    for d in DATASETS:
        slug = d["slug"]
        data_path = os.path.normpath(
            os.path.join(repo_root, "..", "niche-datasets", "datasets", slug, "data", f"{slug}.json")
        )
        if not os.path.isfile(data_path):
            continue
        try:
            with open(data_path, "r", encoding="utf-8") as f:
                records = json.load(f)
        except Exception:
            continue
        for r in records:
            u = (r.get("url") or "").strip().rstrip("/").lower()
            if not u:
                continue
            name = (r.get("name") or "").strip()
            url_to_entries[u].append({"dataset": slug, "name": name})

    top = []
    for url, entries in url_to_entries.items():
        slugs = sorted({e["dataset"] for e in entries})
        if len(slugs) < 3:
            continue
        names = sorted({e["name"] for e in entries if e["name"]})
        top.append({
            "url": url,
            "appearsIn": slugs,
            "count": len(slugs),
            "nameVariants": names,
        })
    top.sort(key=lambda x: (-x["count"], x["url"]))

    return json.dumps({
        "schemaVersion": "1.0",
        "generated": datetime.date.today().isoformat(),
        "name": "Niche Datasets — Cross-Dataset URL Overlap",
        "description": "URLs that appear in 3 or more of the 20 catalog datasets. High-cross-leverage tools spanning multiple developer niches. Use for market-mapping, cross-sell discovery, or to identify which tools justify a multi-dataset bundle purchase.",
        "threshold": "appearsIn >= 3 datasets",
        "totalUrlsAboveThreshold": len(top),
        "topByCount": top,
    }, indent=2)


def build_cross_leverage_section_for_dataset(slug, repo_root):
    """Per-dataset cross-leverage stats block. Counts URLs from this dataset's
    live data file that also appear in 1+ other catalog dataset. Returns the
    full <h2> + body HTML or '' if the dataset has no cross-niche tools.
    """
    from collections import defaultdict
    this_path = os.path.normpath(
        os.path.join(repo_root, "..", "niche-datasets", "datasets", slug, "data", f"{slug}.json")
    )
    if not os.path.isfile(this_path):
        return ""
    url_to_datasets = defaultdict(set)
    url_to_name = {}
    for d in DATASETS:
        dp = os.path.normpath(
            os.path.join(repo_root, "..", "niche-datasets", "datasets", d["slug"], "data", f"{d['slug']}.json")
        )
        if not os.path.isfile(dp):
            continue
        try:
            with open(dp, "r", encoding="utf-8") as f:
                records = json.load(f)
        except Exception:
            continue
        for r in records:
            u = (r.get("url") or "").strip().rstrip("/").lower()
            if not u:
                continue
            url_to_datasets[u].add(d["slug"])
            if d["slug"] == slug:
                name = (r.get("name") or "").strip()
                if name:
                    url_to_name[u] = name

    this_overlap = []
    for u, name in url_to_name.items():
        others = url_to_datasets[u] - {slug}
        if others:
            this_overlap.append({"url": u, "name": name, "others": sorted(others), "count": len(others) + 1})
    if not this_overlap:
        return ""
    this_overlap.sort(key=lambda x: (-x["count"], x["url"]))
    top5 = this_overlap[:5]

    try:
        with open(this_path, "r", encoding="utf-8") as f:
            total_records = len(json.load(f))
    except Exception:
        total_records = 0

    rows = []
    for e in top5:
        slugs_html = ", ".join(f'<a href="{s}.html">{s}</a>' for s in e["others"])
        rows.append(
            f'<li><a href="{e["url"]}" target="_blank" rel="noopener noreferrer nofollow">{e["name"]}</a> '
            f'— spans <strong>{e["count"]}</strong> datasets (also in: {slugs_html})</li>'
        )
    rows_html = "\n".join(rows)

    pct = len(this_overlap) / total_records * 100 if total_records else 0
    return (
        '<h2 id="cross-niche">Cross-niche tools (also appear in other datasets)</h2>\n'
        f'<p><strong>{len(this_overlap)} of {total_records} tools</strong> in this dataset '
        f'({pct:.1f}%) also appear in at least one other dataset in our 20-catalog set. '
        'High-cross-leverage tools — buyers of this dataset who care about these tools may '
        f'also want the adjacent datasets where they appear. Top 5 by span:</p>\n'
        f'<ul>\n{rows_html}\n</ul>\n'
        '<p class="meta">Full cross-leverage table: <a href="cross-leverage.html">/cross-leverage.html</a> · '
        'Programmatic: <a href="cross-dataset-overlap.json"><code>/cross-dataset-overlap.json</code></a>.</p>'
    )


def build_cross_leverage_html(repo_root):
    """Generate /cross-leverage.html — public-readable view of /cross-dataset-overlap.json.
    Lists the top tools by cross-dataset span as an SEO-discoverable HTML page (the
    JSON-only endpoint doesn't surface in search for queries like 'developer tools
    across categories'). Top 40 rows are inlined; full 208-entry list stays in JSON.
    """
    from collections import defaultdict
    url_to_entries = defaultdict(list)
    for d in DATASETS:
        slug = d["slug"]
        data_path = os.path.normpath(
            os.path.join(repo_root, "..", "niche-datasets", "datasets", slug, "data", f"{slug}.json")
        )
        if not os.path.isfile(data_path):
            continue
        try:
            with open(data_path, "r", encoding="utf-8") as f:
                records = json.load(f)
        except Exception:
            continue
        for r in records:
            u = (r.get("url") or "").strip().rstrip("/").lower()
            if not u:
                continue
            name = (r.get("name") or "").strip()
            url_to_entries[u].append({"dataset": slug, "name": name})

    top = []
    for url, entries in url_to_entries.items():
        slugs = sorted({e["dataset"] for e in entries})
        if len(slugs) < 3:
            continue
        names = [e["name"] for e in entries if e["name"]]
        short = min(names, key=len) if names else url
        top.append({"url": url, "name": short, "count": len(slugs), "in": slugs})
    top.sort(key=lambda x: (-x["count"], x["url"]))
    top40 = top[:40]

    rows = []
    for e in top40:
        span_html = "<br>".join(f'<a href="{s}.html">{s}</a>' for s in e["in"])
        rows.append(
            f'<tr><td><a href="{e["url"]}" target="_blank" rel="noopener noreferrer nofollow">{e["name"]}</a></td>'
            f'<td style="text-align:center"><strong>{e["count"]}</strong></td>'
            f'<td>{span_html}</td></tr>'
        )
    rows_html = "\n".join(rows)
    total = len(top)
    five_span = sum(1 for e in top if e["count"] == 5)
    today_iso = datetime.date.today().isoformat()

    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Cross-Niche Developer Tools — Tools That Span 3+ of Our 20 Datasets</title>
<meta name="description" content="{total} developer + AI tools appear in 3 or more of our 20 curated catalog datasets. Top tools span 5 niches at once (ClickUp, KubeStellar Console, Snyk, Taskade). Useful for market-mapping, cross-sell discovery, and bundle-purchase decisions. Reproducible from /cross-dataset-overlap.json.">
<link rel="canonical" href="https://futdevpro.github.io/niche-datasets-free/cross-leverage.html">
<meta property="og:type" content="website">
<meta property="og:url" content="https://futdevpro.github.io/niche-datasets-free/cross-leverage.html">
<meta property="og:title" content="Cross-Niche Developer Tools — Tools Spanning 3+ Datasets">
<meta property="og:description" content="{total} tools span 3+ developer niches at once. {five_span} span 5 niches. Reproducible from /cross-dataset-overlap.json.">
<meta property="og:image" content="https://futdevpro.github.io/niche-datasets-free/og-cover.svg">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="Cross-Niche Developer Tools — {total} Tools, Up to 5-Dataset Span">
<meta name="twitter:description" content="ClickUp, Snyk, KubeStellar, Taskade hit 5 niches. Full top-40 table with member-dataset links.">
<meta name="twitter:image" content="https://futdevpro.github.io/niche-datasets-free/og-cover.svg">
<style>
  body{{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;max-width:920px;margin:0 auto;padding:2rem 1.25rem;line-height:1.55;color:#1a1a1a}}
  h1{{font-size:1.7rem;margin-bottom:.4rem}}
  h2{{font-size:1.2rem;margin-top:2.2rem;color:#0969da;border-bottom:1px solid #eee;padding-bottom:.3rem}}
  a{{color:#0969da}}
  code{{background:#f4f4f4;padding:.1rem .3rem;border-radius:3px;font-size:.9em;font-family:Menlo,Consolas,monospace}}
  .lead{{color:#444;font-size:1.05rem}}
  .nav{{font-size:.9rem;color:#666;margin-bottom:1rem}}
  .meta{{color:#666;font-size:.88rem;margin-bottom:1rem}}
  table{{border-collapse:collapse;width:100%;font-size:.92rem;margin:.8rem 0}}
  th,td{{border:1px solid #e5e7eb;padding:.5rem .6rem;text-align:left;vertical-align:top}}
  thead{{background:#f6f8fa}}
  footer{{margin-top:3rem;padding-top:1rem;border-top:1px solid #eee;font-size:.85rem;color:#666}}
</style>
<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "Dataset",
  "name": "Niche Datasets — Cross-Niche Tools",
  "description": "Public table of {total} developer + AI tools that appear in 3 or more of the Niche Datasets catalog's 20 curated datasets. Recomputed on every refresh.",
  "url": "https://futdevpro.github.io/niche-datasets-free/cross-leverage.html",
  "distribution": [{{
    "@type": "DataDownload",
    "contentUrl": "https://futdevpro.github.io/niche-datasets-free/cross-dataset-overlap.json",
    "encodingFormat": "application/json"
  }}],
  "dateModified": "{today_iso}",
  "license": "https://opensource.org/licenses/MIT",
  "creator": {{"@type": "Organization", "name": "Future Development Program", "url": "https://github.com/futdevpro"}}
}}
</script>
</head>
<body>

<p class="nav"><a href="./">← All 20 datasets</a> &nbsp;·&nbsp; <a href="buyers-guide.html">Buyer's guide</a> &nbsp;·&nbsp; <a href="examples.html#cross-leverage">jq examples</a> &nbsp;·&nbsp; <a href="api.html#cross-dataset-overlap">API docs</a> &nbsp;·&nbsp; <a href="cross-dataset-overlap.json">Full JSON</a></p>

<h1>Cross-Niche Developer Tools — Tools That Span 3+ Datasets</h1>
<p class="meta">Auto-generated {today_iso} from the live data files · {total} tools above threshold · {five_span} at the 5-dataset cap</p>

<p class="lead">Most developer + AI tools live in exactly one niche. But a small set — currently <strong>{total} tools</strong> across the catalog — show up in 3 or more of the 20 datasets at once, because they genuinely span multiple categories. ClickUp is a no-code-lowcode tool, a public-API, a platform-engineering tool, available in homebrew, and listed under developer-tools. The same kind of cross-niche depth applies to {five_span} other "5-span" tools below. Useful for market-mapping ("which tools cover the most niches?"), cross-sell discovery, and bundle-purchase decisions.</p>

<h2 id="top-40">Top {len(top40)} by cross-dataset span</h2>

<table>
<thead><tr><th>Tool</th><th>Datasets</th><th>Appears in</th></tr></thead>
<tbody>
{rows_html}
</tbody>
</table>

<h2 id="full-list">Full list, programmatic access</h2>

<p>The full {total}-entry list is served as JSON at <a href="cross-dataset-overlap.json"><code>/cross-dataset-overlap.json</code></a> (schema: <code>CrossDatasetOverlap</code> in OpenAPI 1.3.0). Recomputed on every catalog refresh from the live <code>liveRecordCount</code> data files. Worked jq snippets at <a href="examples.html#cross-leverage">examples.html#cross-leverage</a>:</p>

<pre style="background:#f6f8fa;padding:.8rem 1rem;border-radius:6px;overflow-x:auto;font-size:.88rem"><code>curl -s https://futdevpro.github.io/niche-datasets-free/cross-dataset-overlap.json \\
  | jq '.topByCount[] | select(.count &gt;= 4) | .url'</code></pre>

<h2 id="how-it-works">How the count is computed</h2>

<p>Each entry in every catalog dataset has a canonical <code>url</code> field. We aggregate URLs case-insensitively, group by dataset slug, and emit any URL that appears in 3+ distinct slugs. Threshold of 3 keeps the output to ~200 entries (vs ~1,300 at 2+, which is dominated by near-duplicates and not very useful). Methodology in <a href="buyers-guide.html#cross-leverage">buyer's guide #cross-leverage</a> and <a href="faq.html">FAQ Q28</a>.</p>

<p>The crawler also strips two common upstream noise patterns at extraction time, so the cross-niche counts reflect real tools — not section-headers leaked into the entry stream. See <a href="api.html#data-quality">api.html#data-quality</a> for details and <a href="examples.html#noise-audit">examples.html#noise-audit</a> for a buyer-runnable verification jq probe.</p>

<p><a href="./">← Browse all 20 datasets</a> &nbsp;·&nbsp; <a href="buyers-guide.html">Buyer's guide</a> &nbsp;·&nbsp; <a href="changelog.html">Refresh changelog</a></p>

<footer>
Niche Datasets · <a href="https://github.com/futdevpro/niche-datasets-free">GitHub repo</a> · <a href="https://jhonnyronnie.gumroad.com/">Gumroad storefront</a><br>
Page auto-generated from <code>scripts/build-detail-pages.py</code> on every catalog refresh. Source-of-truth: the live <code>datasets/&lt;slug&gt;/data/&lt;slug&gt;.json</code> files in the private factory repo.
</footer>

</body>
</html>
'''


def audit_record_floors(repo_root):
    """Warn when a DATASETS records floor like '6,000+' has fallen below the
    actual record count from the live data file. Advisory only — doesn't
    rewrite the list, since the per-dataset desc strings also reference the
    number and a blind rewrite would create inconsistencies.

    Threshold: warn if actual >= floor + 100 (or +1000 for 10k+ datasets).
    """
    import re
    stale = []
    for d in DATASETS:
        slug = d["slug"]
        floor_str = d["records"].rstrip("+").replace(",", "")
        try:
            floor = int(floor_str)
        except ValueError:
            continue
        data_path = os.path.normpath(
            os.path.join(repo_root, "..", "niche-datasets", "datasets", slug, "data", f"{slug}.json")
        )
        if not os.path.isfile(data_path):
            continue
        try:
            with open(data_path, "r", encoding="utf-8") as f:
                actual = len(__import__("json").load(f))
        except Exception:
            continue
        bump = 1000 if floor >= 10000 else 100
        new_floor = (actual // bump) * bump
        if new_floor >= floor + bump:
            stale.append((slug, d["records"], actual, new_floor))
    if stale:
        print("[audit] WARNING: stale record-count floors:")
        for slug, current, actual, new_floor in stale:
            print(f"  {slug}: current={current} actual={actual} suggested={new_floor:,}+")


def main():
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    audit_record_floors(repo_root)
    count = 0
    use_case_hits = 0
    preview_hits = 0
    for d in DATASETS:
        use_cases_html = load_use_cases(d["slug"], repo_root)
        if use_cases_html:
            use_case_hits += 1
        else:
            use_cases_html = "<p class='meta'>Use-cases coming soon.</p>"
        preview_html = load_preview(d["slug"], repo_root)
        if preview_html:
            preview_hits += 1
        else:
            preview_html = "<p class='meta'>Preview unavailable — see the sample files below.</p>"
        tier_list = list_tier_enums(d["slug"], repo_root)
        tier_n = len(tier_list)
        if tier_n > 0:
            tier_names = ", ".join(f"<code>{t}</code>" for t in tier_list)
            tier_badge = (
                f' · <a href="tiers.html" class="badge" style="background:#e6f4ff;color:#0969da;text-decoration:none" '
                f'title="Tier-enums on this dataset: {", ".join(tier_list)}">{tier_n} derived enum tiers</a>'
            )
            tier_badge += (
                f'<br><span style="font-size:.85em;color:#555;display:inline-block;margin-top:.2rem">'
                f'Filter by: {tier_names}</span>'
            )
        else:
            tier_badge = ""
        html = DETAIL_TEMPLATE.format(
            name=d["name"], desc=d["desc"], records=d["records"],
            slug=d["slug"], gumroad=d["gumroad"], price=d["price"],
            refresh_date=get_refresh_date(d["slug"], repo_root),
            tier_badge=tier_badge,
            jsonld=build_jsonld(d, repo_root),
            breadcrumb_jsonld=build_breadcrumb_jsonld(d),
            use_cases_html=use_cases_html,
            preview_html=preview_html,
            related_html=build_related_html(d),
            cross_leverage_html=build_cross_leverage_section_for_dataset(d["slug"], repo_root),
        )
        path = os.path.join(repo_root, f"{d['slug']}.html")
        with open(path, "w", encoding="utf-8") as f:
            f.write(html)
        count += 1
    sitemap_path = os.path.join(repo_root, "sitemap.xml")
    with open(sitemap_path, "w", encoding="utf-8") as f:
        f.write(build_sitemap())
    catalog_path = os.path.join(repo_root, "datasets.json")
    with open(catalog_path, "w", encoding="utf-8") as f:
        f.write(build_catalog_json(repo_root))
    overlap_path = os.path.join(repo_root, "cross-dataset-overlap.json")
    with open(overlap_path, "w", encoding="utf-8") as f:
        f.write(build_cross_dataset_overlap_json(repo_root))
    cross_leverage_path = os.path.join(repo_root, "cross-leverage.html")
    with open(cross_leverage_path, "w", encoding="utf-8") as f:
        f.write(build_cross_leverage_html(repo_root))
    # Per-dataset metadata endpoints
    for d in DATASETS:
        meta_path = os.path.join(repo_root, f"{d['slug']}-meta.json")
        with open(meta_path, "w", encoding="utf-8") as f:
            f.write(build_dataset_endpoint(d, repo_root))
    # RSS feed
    feed_path = os.path.join(repo_root, "feed.xml")
    with open(feed_path, "w", encoding="utf-8") as f:
        f.write(build_feed_xml(repo_root))
    update_index_table(repo_root)
    update_index_jsonld(repo_root)
    print(f"Generated {count} detail pages + {count} -meta.json endpoints + sitemap.xml ({len(DATASETS)+18} URLs: root + buyers-guide + tiers + quickstart + api + examples + vs + faq + blog-url-fix + blog-3day + blog-13day + blog-enum-tiers + changelog + feed + openapi + cross-dataset-overlap + cross-leverage + llms.txt + 20 detail) + datasets.json catalog + cross-dataset-overlap.json + feed.xml RSS + updated index.html JSON-LD. Use-cases injected: {use_case_hits}/{count}. Previews injected: {preview_hits}/{count}.")


if __name__ == "__main__":
    main()
