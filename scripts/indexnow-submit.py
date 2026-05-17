#!/usr/bin/env python3
"""
Submit all 21 Pages URLs to the IndexNow API (Bing, Yandex, Seznam, Naver share the protocol).

IndexNow lets a site owner ping participating search engines to recrawl URLs *now*
instead of waiting for the natural crawl cycle. Zero auth — proof of ownership is a
key file hosted at the site root with the key as filename.

Run:  python3 scripts/indexnow-submit.py
"""
import json
import urllib.request

KEY = "654f24b46f0707d7878c59019aa86237"
HOST = "futdevpro.github.io"
SITE_ROOT = f"https://{HOST}/niche-datasets-free"

URLS = [
    f"{SITE_ROOT}/",
    f"{SITE_ROOT}/faq.html",
    f"{SITE_ROOT}/examples.html",
    f"{SITE_ROOT}/feed.xml",
    f"{SITE_ROOT}/homebrew-packages.html",
    f"{SITE_ROOT}/npm-packages.html",
    f"{SITE_ROOT}/vscode-extensions.html",
    f"{SITE_ROOT}/huggingface-models.html",
    f"{SITE_ROOT}/mcp-servers.html",
    f"{SITE_ROOT}/ai-tools.html",
    f"{SITE_ROOT}/cybersecurity-tools.html",
    f"{SITE_ROOT}/huggingface-datasets.html",
    f"{SITE_ROOT}/public-apis.html",
    f"{SITE_ROOT}/self-hosted-software.html",
    f"{SITE_ROOT}/design-resources.html",
    f"{SITE_ROOT}/ai-agents.html",
    f"{SITE_ROOT}/ai-prompts.html",
    f"{SITE_ROOT}/developer-tools.html",
    f"{SITE_ROOT}/open-source-alternatives.html",
    f"{SITE_ROOT}/ai-models-pricing.html",
    f"{SITE_ROOT}/no-code-lowcode.html",
    f"{SITE_ROOT}/llmops-and-eval.html",
    f"{SITE_ROOT}/platform-engineering.html",
    f"{SITE_ROOT}/vector-db-and-rag.html",
]

# Bing endpoint also serves Yandex/Seznam/Naver via the shared protocol.
ENDPOINTS = ["https://api.indexnow.org/IndexNow"]


def submit(endpoint, payload):
    req = urllib.request.Request(
        endpoint,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json; charset=utf-8"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return resp.status, resp.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", errors="replace")
    except Exception as e:
        return 0, str(e)


def main():
    payload = {
        "host": HOST,
        "key": KEY,
        "keyLocation": f"{SITE_ROOT}/{KEY}.txt",
        "urlList": URLS,
    }
    for ep in ENDPOINTS:
        status, body = submit(ep, payload)
        print(f"{ep} -> HTTP {status}")
        if body:
            print(f"  body: {body[:300]}")


if __name__ == "__main__":
    main()
