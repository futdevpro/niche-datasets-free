# 📊 Free Dataset Samples

Preview records from each curated developer dataset. Every sample contains **20 diverse records** in both JSON and CSV format.

## Datasets

### 🔧 Dev Stack — IDE plugins, packages, system tools

| Dataset | Records | Sample | Full Dataset |
|---------|---------|--------|-------------|
| **Homebrew Packages Directory** ⭐NEW | 12,200+ | [JSON](homebrew-packages-sample.json) · [CSV](homebrew-packages-sample.csv) | _launching soon ($11)_ |
| **VS Code Extensions Directory** ⭐NEW | 4,800+ | [JSON](vscode-extensions-sample.json) · [CSV](vscode-extensions-sample.csv) | _launching soon ($9)_ |
| **npm Packages Directory** ⭐NEW | 6,000+ | [JSON](npm-packages-sample.json) · [CSV](npm-packages-sample.csv) | _launching soon ($11)_ |
| Developer Tools Directory | 1,600+ | [JSON](developer-tools-sample.json) · [CSV](developer-tools-sample.csv) | [$9 on Gumroad](https://jhonnyronnie.gumroad.com/l/developer-tools-directory) |
| Open MCP Servers Directory | 3,600+ | [JSON](mcp-servers-sample.json) · [CSV](mcp-servers-sample.csv) | [$9 on Gumroad](https://jhonnyronnie.gumroad.com/l/mcp-servers-directory) |
| Public APIs Directory | 2,500+ | [JSON](public-apis-sample.json) · [CSV](public-apis-sample.csv) | [$12 on Gumroad](https://jhonnyronnie.gumroad.com/l/public-apis-directory) |

### 🤖 AI / ML — models, datasets, prompts, pricing

| Dataset | Records | Sample | Full Dataset |
|---------|---------|--------|-------------|
| **LLMOps & Eval Tooling Directory** ⭐NEW | 490+ | [JSON](llmops-and-eval-sample.json) · [CSV](llmops-and-eval-sample.csv) | _launching soon ($11)_ |
| **Vector DB & RAG Infrastructure Directory** ⭐NEW | 190+ | [JSON](vector-db-and-rag-sample.json) · [CSV](vector-db-and-rag-sample.csv) | _launching soon ($11)_ |
| **AI Models & Providers Pricing Matrix** ⭐NEW | 800+ | [JSON](ai-models-pricing-sample.json) · [CSV](ai-models-pricing-sample.csv) | _launching soon ($11)_ |
| **HuggingFace Models Directory** ⭐NEW | 4,000 | [JSON](huggingface-models-sample.json) · [CSV](huggingface-models-sample.csv) | _launching soon ($11)_ |
| **HuggingFace Datasets Directory** ⭐NEW | 2,600+ (curated, with metadata) | [JSON](huggingface-datasets-sample.json) · [CSV](huggingface-datasets-sample.csv) | _launching soon ($11)_ |
| **AI Prompts Directory** ⭐NEW | 1,700+ | [JSON](ai-prompts-sample.json) · [CSV](ai-prompts-sample.csv) | _launching soon ($9)_ |
| AI Tools Directory | 2,700+ | [JSON](ai-tools-sample.json) · [CSV](ai-tools-sample.csv) | [$9 on Gumroad](https://jhonnyronnie.gumroad.com/l/ai-tools-directory) |
| AI Agents Directory | 2,000+ | [JSON](ai-agents-sample.json) · [CSV](ai-agents-sample.csv) | [$7 on Gumroad](https://jhonnyronnie.gumroad.com/l/ai-agents-directory) |

### 🛡️ Security · Self-hosting · Open Source · Design · No-code

| Dataset | Records | Sample | Full Dataset |
|---------|---------|--------|-------------|
| Self-Hosted Software Directory | 2,300+ | [JSON](self-hosted-software-sample.json) · [CSV](self-hosted-software-sample.csv) | [$14 on Gumroad](https://jhonnyronnie.gumroad.com/l/self-hosted-software-directory) |
| Cybersecurity Tools Directory | 2,700+ | [JSON](cybersecurity-tools-sample.json) · [CSV](cybersecurity-tools-sample.csv) | [$9 on Gumroad](https://jhonnyronnie.gumroad.com/l/cybersecurity-tools) |
| Design Resources Directory | 2,100+ | [JSON](design-resources-sample.json) · [CSV](design-resources-sample.csv) | [$9 on Gumroad](https://jhonnyronnie.gumroad.com/l/design-resources) |
| Open Source Alternatives | 900+ | [JSON](open-source-alternatives-sample.json) · [CSV](open-source-alternatives-sample.csv) | [$7 on Gumroad](https://jhonnyronnie.gumroad.com/l/open-source-alternatives) |
| No-Code & Low-Code Tools | 500+ | [JSON](no-code-lowcode-sample.json) · [CSV](no-code-lowcode-sample.csv) | [$7 on Gumroad](https://jhonnyronnie.gumroad.com/l/no-code-lowcode) |

> ⭐ **NEW** — 9 datasets just shipped (cycleWeek 2026-05-05/06). Samples available now; Gumroad products launching shortly. Watch the [LinkedIn showcase page](https://www.linkedin.com/showcase/niche-datasets/) for live URLs.

## Mega Sample

A combined preview with **5 records from each dataset**:
- [mega-sample.json](mega-sample.json)
- [mega-sample.csv](mega-sample.csv)

## Want everything?

The **[Complete Developer Data Bundle](https://jhonnyronnie.gumroad.com/l/developer-data-bundle)** currently includes 10 datasets (~22,000 records after recent improve sweep) for **$29** — 73% off individual prices.

After the 9 new datasets launch, the bundle will expand to **19 datasets (~52,300 records)** with a planned tier-up to $34-39 — still 80%+ off vs $95 standalone.

**Themed sub-bundles** (launching with the new products):
- 🤖 **ML Builder Pack** ($35-39 planned, expanded to 6-pack) — AI Models Pricing + HuggingFace Models + HuggingFace Datasets + AI Prompts + LLMOps & Eval Tooling + **Vector DB & RAG Infrastructure** (6 datasets, ~9,900 records, complete LLM/ML engineering stack: data → models → APIs → prompts → platform tooling → retrieval/RAG infrastructure)
- 🔧 **Dev Stack Pack** ($29) — npm Packages + VS Code Extensions + Homebrew Packages + Developer Tools (4 datasets, ~23,400 records, 31% off)

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

## License

Samples are free to use for evaluation. Full datasets are licensed per the [Gumroad terms](https://jhonnyronnie.gumroad.com).

The catalog metadata is factual data about open-source projects — clean for commercial repackaging. Per-record licenses (where applicable) are surfaced as first-class `license` fields.

---

## Built by

These datasets are built and maintained by **[Future Development Program (FDP)](https://www.linkedin.com/company/futdevpro/)** — a custom software and AI development studio.

- 💼 [Niche Datasets on LinkedIn](https://www.linkedin.com/showcase/niche-datasets/) — product line page, follow for updates
- 🏢 [FDP on LinkedIn](https://www.linkedin.com/company/futdevpro/) — parent company
- 🛒 [Gumroad Store](https://jhonnyronnie.gumroad.com) — all datasets

## How the data is built

Each dataset is sourced from official APIs (HuggingFace Hub, npm registry, OpenRouter, Homebrew, VS Code Marketplace) or curated from multiple public open-source lists (e.g., `awesome-*` GitHub repos), then run through an automated pipeline:

```
sources → crawl → normalize → dedupe → enrich → validate → export → publish
```

The samples in this repo are random subsets from the full versions. Same schema, structure, and quality as the paid datasets.

Refresh cadence: monthly for `ai-models-pricing` (decay-rate-sensitive), quarterly for the rest.
