# 📊 Free Dataset Samples

Preview records from each curated developer dataset. Every sample contains **20 diverse records** in both JSON and CSV format.

## Datasets

| Dataset | Records | Sample | Full Dataset |
|---------|---------|--------|-------------|
| AI Tools Directory | 1,600+ | [JSON](ai-tools-sample.json) · [CSV](ai-tools-sample.csv) | [$9 on Gumroad](https://jhonnyronnie.gumroad.com/l/ai-tools-directory) |
| AI Agents Directory | 800+ | [JSON](ai-agents-sample.json) · [CSV](ai-agents-sample.csv) | [$7 on Gumroad](https://jhonnyronnie.gumroad.com/l/ai-agents-directory) |
| Public APIs Directory | 2,500+ | [JSON](public-apis-sample.json) · [CSV](public-apis-sample.csv) | [$12 on Gumroad](https://jhonnyronnie.gumroad.com/l/public-apis-directory) |
| Developer Tools Directory | 1,500+ | [JSON](developer-tools-sample.json) · [CSV](developer-tools-sample.csv) | [$9 on Gumroad](https://jhonnyronnie.gumroad.com/l/developer-tools-directory) |
| Self-Hosted Software Directory | 2,100+ | [JSON](self-hosted-software-sample.json) · [CSV](self-hosted-software-sample.csv) | [$14 on Gumroad](https://jhonnyronnie.gumroad.com/l/self-hosted-software-directory) |
| Open MCP Servers Directory | 2,900+ | [JSON](mcp-servers-sample.json) · [CSV](mcp-servers-sample.csv) | [$9 on Gumroad](https://jhonnyronnie.gumroad.com/l/mcp-servers-directory) |
| Design Resources Directory | 1,800+ | [JSON](design-resources-sample.json) · [CSV](design-resources-sample.csv) | [$9 on Gumroad](https://jhonnyronnie.gumroad.com/l/design-resources) |
| Cybersecurity Tools Directory | 1,800+ | [JSON](cybersecurity-tools-sample.json) · [CSV](cybersecurity-tools-sample.csv) | [$9 on Gumroad](https://jhonnyronnie.gumroad.com/l/cybersecurity-tools) |
| Open Source Alternatives | 800+ | [JSON](open-source-alternatives-sample.json) · [CSV](open-source-alternatives-sample.csv) | [$7 on Gumroad](https://jhonnyronnie.gumroad.com/l/open-source-alternatives) |
| No-Code & Low-Code Tools | 500+ | [JSON](no-code-lowcode-sample.json) · [CSV](no-code-lowcode-sample.csv) | [$7 on Gumroad](https://jhonnyronnie.gumroad.com/l/no-code-lowcode) |

## Mega Sample

A combined preview with **5 records from each dataset** (50 total):
- [mega-sample.json](mega-sample.json)
- [mega-sample.csv](mega-sample.csv)

## Want everything?

The **[Complete Developer Data Bundle](https://jhonnyronnie.gumroad.com/l/developer-data-bundle)** includes all 10 datasets (16,000+ records) for **$29** — 68% off individual prices.

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

Some datasets have additional fields (e.g., `auth`, `license`, `openSource`, `toolType`).

## License

Samples are free to use for evaluation. Full datasets are licensed per the [Gumroad terms](https://jhonnyronnie.gumroad.com).

---

## Built by

These datasets are built and maintained by **[Future Development Program (FDP)](https://www.linkedin.com/company/futdevpro/)** — a custom software and AI development studio.

- 💼 [Niche Datasets on LinkedIn](https://www.linkedin.com/showcase/niche-datasets/) — product line page, follow for updates
- 🏢 [FDP on LinkedIn](https://www.linkedin.com/company/futdevpro/) — parent company
- 🛒 [Gumroad Store](https://jhonnyronnie.gumroad.com) — all 10 datasets

## How the data is built

Each dataset is curated from multiple public open-source lists (e.g., `awesome-*` GitHub repos), then run through an automated pipeline:

```
sources → crawl → normalize → dedupe → enrich → validate → export → publish
```

The samples in this repo are random subsets from the full versions. Same schema, structure, and quality as the paid datasets.
