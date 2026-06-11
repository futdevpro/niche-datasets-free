# 📊 Free Dataset Samples

Preview records from each curated developer dataset. Every sample contains **20 diverse records** in both JSON and CSV format.

**20 datasets, ~53,000 records total.** All sourced from official APIs (npm registry, Homebrew, HuggingFace Hub, OpenRouter, VS Code Marketplace) or CC0/MIT/Apache-2.0 awesome-lists. Aggregation is license-clean for commercial repackaging.

> 🌐 **Browse on the web:** [futdevpro.github.io/niche-datasets-free](https://futdevpro.github.io/niche-datasets-free/) — same content with schema.org JSON-LD for [Google Dataset Search](https://datasetsearch.research.google.com/).

## What just landed (refresh 2026-05-20)

Every dataset got a fresh pull on 2026-05-20 after a 13-day gap. **55,326 records total, 0 validation errors.** Per-source churn varies by 3 orders of magnitude:

- **npm-packages: 122% gross churn** (+3,760 / -3,775 out of 6,171) — top-by-downloads ranking rolls over more than half its members in 2 weeks. Daily-to-weekly refresh required.
- **huggingface-datasets: 43% churn** (+682 / -539) — very active publishing.
- **huggingface-models: 17% churn** on the 4,000-cap top-by-downloads list.
- **ai-models-pricing: 11%** — OpenRouter price changes + new model launches.
- **mcp-servers: 0.8%**, **homebrew-packages: 0.6%**, **vscode-extensions: 0.4%** — mature ecosystems.
- **llmops-and-eval / vector-db-and-rag / design-resources: literal 0** — awesome-list mirrors with no recent edits.

Full per-dataset table: [13-day refresh report](https://futdevpro.github.io/niche-datasets-free/blog-2026-05-20-13-day-refresh.html).

## What makes this different — semantic enum tier fields

Every record carries derived enum-tier fields the source data doesn't have: `costTierAbsolute`, `useCaseTier`, `uptimeTier`, `licenseTier`, `popularityTier`, `vendorTier`, +40 more. Filter by enum names that survive refreshes (absolute thresholds tied to real-world concepts: SLA classes for uptime, `$`/M ranges for cost) and stay consistent across datasets (same enum name across HF models + HF datasets + ai-models-pricing).

Reference + methodology:
- 📋 [All tiers reference](https://futdevpro.github.io/niche-datasets-free/tiers.html) — 10 shared + 40+ dataset-specific.
- 🧪 [Methodology blog](https://futdevpro.github.io/niche-datasets-free/blog-semantic-enum-tiers.html) — why absolute beats percentile, how cross-dataset symmetry works.
- 💻 [jq filter examples](https://futdevpro.github.io/niche-datasets-free/examples.html#tier-filters) — paste-and-run code.
- 🤝 [Buyer's guide](https://futdevpro.github.io/niche-datasets-free/buyers-guide.html) — 8 use cases mapped to specific datasets.
- 🔌 [OpenAPI 3.1 spec](https://futdevpro.github.io/niche-datasets-free/openapi.json) for the 3 free endpoints (catalog / per-dataset meta / RSS).

These are baked into the actual records — the mega-sample below has 5 random records per dataset so you can see the schema and tier-fields first-hand.

## Datasets

### 🔧 Dev Stack — IDE plugins, packages, system tools

| Dataset | Records | Sample | Full Dataset |
|---------|---------|--------|-------------|
| Homebrew Packages Directory | 12,200+ | [JSON](homebrew-packages-sample.json) · [CSV](homebrew-packages-sample.csv) | [$11 on Gumroad](https://jhonnyronnie.gumroad.com/l/homebrew-packages-directory) |
| npm Packages Directory | 4,900+ | [JSON](npm-packages-sample.json) · [CSV](npm-packages-sample.csv) | [$11 on Gumroad](https://jhonnyronnie.gumroad.com/l/npm-packages-directory) |
| VS Code Extensions Directory | 4,800+ | [JSON](vscode-extensions-sample.json) · [CSV](vscode-extensions-sample.csv) | [$9 on Gumroad](https://jhonnyronnie.gumroad.com/l/vscode-extensions-directory) |
| Open MCP Servers Directory | 2,800+ | [JSON](mcp-servers-sample.json) · [CSV](mcp-servers-sample.csv) | [$9 on Gumroad](https://jhonnyronnie.gumroad.com/l/mcp-servers-directory) |
| Public APIs Directory | 2,600+ | [JSON](public-apis-sample.json) · [CSV](public-apis-sample.csv) | [$12 on Gumroad](https://jhonnyronnie.gumroad.com/l/public-apis-directory) |
| Developer Tools Directory | 1,600+ | [JSON](developer-tools-sample.json) · [CSV](developer-tools-sample.csv) | [$9 on Gumroad](https://jhonnyronnie.gumroad.com/l/developer-tools-directory) |

### 🤖 AI / ML — models, datasets, prompts, pricing, infrastructure

| Dataset | Records | Sample | Full Dataset |
|---------|---------|--------|-------------|
| HuggingFace Models Directory | 4,000 | [JSON](huggingface-models-sample.json) · [CSV](huggingface-models-sample.csv) | [$11 on Gumroad](https://jhonnyronnie.gumroad.com/l/huggingface-models-directory) |
| AI Tools Directory | 2,800+ | [JSON](ai-tools-sample.json) · [CSV](ai-tools-sample.csv) | [$9 on Gumroad](https://jhonnyronnie.gumroad.com/l/ai-tools-directory) |
| HuggingFace Datasets Directory | 2,800+ | [JSON](huggingface-datasets-sample.json) · [CSV](huggingface-datasets-sample.csv) | [$11 on Gumroad](https://jhonnyronnie.gumroad.com/l/huggingface-datasets-directory) |
| AI Agents Directory | 2,000+ | [JSON](ai-agents-sample.json) · [CSV](ai-agents-sample.csv) | [$7 on Gumroad](https://jhonnyronnie.gumroad.com/l/ai-agents-directory) |
| AI Prompts Directory | 1,800+ | [JSON](ai-prompts-sample.json) · [CSV](ai-prompts-sample.csv) | [$9 on Gumroad](https://jhonnyronnie.gumroad.com/l/ai-prompts-directory) |
| AI Models & Providers Pricing Matrix | 800+ | [JSON](ai-models-pricing-sample.json) · [CSV](ai-models-pricing-sample.csv) | [$11 on Gumroad](https://jhonnyronnie.gumroad.com/l/ai-models-pricing-matrix) |
| LLMOps & Eval Tooling Directory | 490+ | [JSON](llmops-and-eval-sample.json) · [CSV](llmops-and-eval-sample.csv) | [$11 on Gumroad](https://jhonnyronnie.gumroad.com/l/llmops-and-eval-tooling-directory) |
| Vector DB & RAG Infrastructure Directory | 190+ | [JSON](vector-db-and-rag-sample.json) · [CSV](vector-db-and-rag-sample.csv) | [$11 on Gumroad](https://jhonnyronnie.gumroad.com/l/vector-db-and-rag-infrastructure) |

### 🛠️ Platform Engineering · SRE · Self-Hosting

| Dataset | Records | Sample | Full Dataset |
|---------|---------|--------|-------------|
| Self-Hosted Software Directory | 2,300+ | [JSON](self-hosted-software-sample.json) · [CSV](self-hosted-software-sample.csv) | [$14 on Gumroad](https://jhonnyronnie.gumroad.com/l/self-hosted-software-directory) |
| Platform Engineering & IDP Tooling Directory | 390+ | [JSON](platform-engineering-sample.json) · [CSV](platform-engineering-sample.csv) | [$11 on Gumroad](https://jhonnyronnie.gumroad.com/l/platform-engineering-tooling-directory) |

### 🛡️ Security · Open Source · Design · No-code

| Dataset | Records | Sample | Full Dataset |
|---------|---------|--------|-------------|
| Cybersecurity Tools Directory | 2,700+ | [JSON](cybersecurity-tools-sample.json) · [CSV](cybersecurity-tools-sample.csv) | [$9 on Gumroad](https://jhonnyronnie.gumroad.com/l/cybersecurity-tools) |
| Design Resources Directory | 2,100+ | [JSON](design-resources-sample.json) · [CSV](design-resources-sample.csv) | [$9 on Gumroad](https://jhonnyronnie.gumroad.com/l/design-resources) |
| Open Source Alternatives Directory | 900+ | [JSON](open-source-alternatives-sample.json) · [CSV](open-source-alternatives-sample.csv) | [$7 on Gumroad](https://jhonnyronnie.gumroad.com/l/open-source-alternatives) |
| No-Code & Low-Code Tools Directory | 500+ | [JSON](no-code-lowcode-sample.json) · [CSV](no-code-lowcode-sample.csv) | [$7 on Gumroad](https://jhonnyronnie.gumroad.com/l/no-code-lowcode) |

## Mega Sample

A combined preview with **5 records from each dataset** (100 records total):
- [mega-sample.json](mega-sample.json)
- [mega-sample.csv](mega-sample.csv)

Or download the same combined sample as a single ZIP from Gumroad (no signup): **[Free Developer Data Sample on Gumroad](https://jhonnyronnie.gumroad.com/l/free-sample)** — $0.

## Want everything?

The **[Complete Developer Data Bundle](https://jhonnyronnie.gumroad.com/l/developer-data-bundle)** includes all 20 datasets (~53,000 records combined) for **$34** — 83% off vs $198 individual standalone total.

### Themed sub-bundles (focused buyer personas)

| Bundle | Datasets | Standalone | Bundle | Save |
|--------|----------|------------|--------|------|
| [Dev Stack Pack](https://jhonnyronnie.gumroad.com/l/dev-stack-pack) — npm + VS Code + Homebrew + Dev Tools | 4 (~24,600 records) | $42 | **$24** | 43% |
| [Platform Builder Pack](https://jhonnyronnie.gumroad.com/l/platform-builder-pack) — Platform Engineering + Dev Tools + npm + Homebrew + VS Code + Self-Hosted | 6 (~27,000 records) | $67 | **$29** | 57% |
| [ML Builder Pack](https://jhonnyronnie.gumroad.com/l/ml-builder-pack) — AI Models Pricing + HuggingFace Models + HF Datasets + AI Prompts + LLMOps & Eval + Vector DB & RAG | 6 (~9,900 records) | $64 | **$29** | 55% |

## Format

Every record includes at minimum:

```json
{
  "name": "Tool Name",
  "url": "https://example.com",
  "description": "What this tool does",
  "category": "category-name",
  "pricing": "free | freemium | paid | open-source",
  "hasApi": true,
  "tags": ["tag1", "tag2"]
}
```

Many datasets carry additional first-class fields specific to their niche, e.g.:

- `vscode-extensions`: `installCount`, `version`, `lastUpdated`, `extensionId`, `publisherSlug`
- `homebrew-packages`: `installCount365d`, `packageType` (formula/cask), `dependencies`, `tap`, `deprecated`
- `npm-packages`: `weeklyDownloads`, `monthlyDownloads`, `dependents`, `npmScore` (popularity/quality/maintenance), `repository`
- `ai-models-pricing`: `pricingPromptPerMillionUsd`, `pricingCompletionPerMillionUsd`, `provider`, `quantization`, `modality`, `contextLength`, `uptimeLast30dPct`
- `huggingface-models` / `huggingface-datasets`: `downloads`, `likes`, `license`, `pipelineTag`, `modality`, `taskCategories`, `language`
- `ai-prompts`: `promptText`, `modelType` (text/structured/image), `forDevs`, `contributor`
- `public-apis`: `auth`, `https`, `cors`
- `platform-engineering`: 14 categorical buckets (developer-portal, gitops, service-mesh, iac-and-provisioning, observability, container-orchestration, ci-cd-pipeline, secrets-management, policy-and-governance, feature-flags, service-catalog, cost-management, developer-experience, other), `categorizationTier`

Plus 40+ semantic enum tiers across all datasets — `urlDomainTier`, `descriptionLengthTier`, `categorizationTier`, plus dataset-specific tiers like `popularityTier`, `recencyTier`, `licenseTier`, `supplyChainRisk`, `dependentTier`, `installVolumeTier`, etc.

**New 2026-05-12 (`githubStars` field):** ~8,600 GitHub-hosted records across 13 of 20 datasets now have a `githubStars` integer field — sortable popularity signal for filters like "top 20 mature vector DBs" or "MCP servers above 1K stars". Top across catalog: openclaw 370K, Python Programming by @vinta 297K, Awesome-Selfhosted 291K (curated meta-lists); TensorFlow 195K, n8n 187K, oh-my-zsh 186K, Auto-GPT 184K, Ollama 171K.

**New 2026-05-23 (crawler noise filters):** the awesome-list extractor strips two common section-header-as-list-item patterns at ingest — (a) year-prefix headers like "2021 Result" / "2023 Competition", and (b) self-section pointers (bare `github.com/<owner>/<repo>#anchor` URLs where the name alnum-matches the anchor). Recent scrub removed 3 noise records from `vector-db-and-rag` and 27 from `self-hosted-software`, zero false positives across the other 18 datasets. Verify against any sample with the [noise-audit jq snippets](https://futdevpro.github.io/niche-datasets-free/examples.html#noise-audit) — both probes return 0.

## License

Samples are free to use for evaluation. Full datasets are licensed per the [Gumroad terms](https://jhonnyronnie.gumroad.com).

The catalog metadata is factual data about open-source projects — clean for commercial repackaging. Per-record licenses (where applicable) are surfaced as first-class `license` fields.

## How the data is built

Each dataset is sourced from official APIs (HuggingFace Hub, npm registry, OpenRouter, Homebrew, VS Code Marketplace) or curated from multiple public open-source lists (e.g., `awesome-*` GitHub repos), then run through an automated pipeline:

```
sources → crawl → normalize → dedupe → enrich → validate → export → publish
```

The samples in this repo are random subsets from the full versions. Same schema, structure, and quality as the paid datasets.

Refresh cadence: monthly for `ai-models-pricing` (decay-rate-sensitive), quarterly for the rest.

---

## Local development — rebuilding the public site

The HTML pages in this repo are generated by Python scripts in `scripts/`. Run them after refreshing samples to keep the site current:

```bash
# 1. After a dataset refresh in the sibling niche-datasets repo, regenerate samples
#    (handled by the upstream pipeline — produces *-sample.json, *-sample.csv)

# 2. Rebuild per-dataset detail pages, sitemap.xml, datasets.json catalog, RSS feed
python3 scripts/build-detail-pages.py

# 3. Rebuild any pages that aggregate across the catalog
python3 scripts/build-faq.py           # FAQ Q&A
python3 scripts/build-examples.py      # code snippets
python3 scripts/build-vs.py            # vs. alternatives
python3 scripts/build-changelog.py     # last 60 refresh events
python3 scripts/build-tiers.py         # all enum tiers cross-reference

# 4. Notify search engines (Bing, Yandex, Seznam, Naver via IndexNow)
python3 scripts/indexnow-submit.py
```

All scripts are idempotent; safe to re-run. The build-changelog.py, build-detail-pages.py, and build-tiers.py scripts all read from `../niche-datasets/datasets/<slug>/` in the sibling factory repo (CHANGELOG.md, samples/, and config.json respectively).

---

## Built by

**[Ronnie J](https://github.com/jhonny-ronnie)** at **[Future Development Program](https://github.com/futdevpro)** — independent software + AI development.

- 🛒 [Gumroad Store](https://jhonnyronnie.gumroad.com) — all 20 datasets + bundles
- 💼 [LinkedIn](https://linkedin.com/in/ronnie-j-110752400)
- 🐦 [Twitter/X](https://x.com/RonnieJ_FDP)
