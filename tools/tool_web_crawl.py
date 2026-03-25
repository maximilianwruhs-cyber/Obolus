#!/usr/bin/env python3
"""
Wave 8: The Great Archive — Autonomous Web Crawler
Fetches a URL, strips boilerplate, and converts to Markdown for agent ingestion.
"""

import sys
import json
import re
import requests
from bs4 import BeautifulSoup
import markdownify


def fetch_and_parse(url: str) -> dict:
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        resp = requests.get(url, headers=headers, timeout=15)
        resp.raise_for_status()

        soup = BeautifulSoup(resp.text, "html.parser")

        for element in soup(["script", "style", "nav", "footer", "header", "aside", "noscript", "meta"]):
            element.decompose()

        main_content = soup.find("main") or soup.find("article") or soup.find("body")
        if not main_content:
            return {"status": "error", "message": "Could not find body/main content block."}

        md_text = markdownify.markdownify(str(main_content), heading_style="ATX").strip()
        md_text = re.sub(r"\n{3,}", "\n\n", md_text)

        max_chars = 6000
        if len(md_text) > max_chars:
            md_text = md_text[:max_chars] + f"\n...[TRUNCATED: Exceeded {max_chars} chars]..."

        title = soup.title.string.strip() if soup.title else url
        return {"status": "success", "title": title, "url": url, "markdown": md_text}
    except requests.exceptions.RequestException as e:
        return {"status": "error", "message": f"Network Error: {e}"}
    except Exception as e:
        return {"status": "error", "message": f"Parse Error: {e}"}


def main():
    if len(sys.argv) < 2:
        print(json.dumps({"status": "error", "message": "Usage: python3 tool_web_crawl.py <url>"}))
        sys.exit(1)
    result = fetch_and_parse(sys.argv[1])
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
