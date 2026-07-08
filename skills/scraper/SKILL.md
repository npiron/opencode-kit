---
name: scraper
description: Use for web scraping, data extraction from websites, crawling multi-page content, handling anti-bot measures, and extracting structured data from HTML. Trigger with keywords: scrape, extract, crawl, fetch, parse, parsing, DOM, selectors.
---

# Scraping Skill

Methodology for effective web scraping with Playwright and Fetch.

## Tool Priority

1. **Fetch MCP** for static content/APIs (fast, lightweight)
   - `fetch_markdown` for documentation pages
   - `fetch_txt` for plain text
   - `fetch_readable` for articles (Readability)
   - `fetch_json` for REST APIs
   - `fetch_youtube_transcript` for YouTube captions

2. **Playwright** for dynamic content (JS rendering, SPAs, forms)
   - Navigate, click, fill forms, scroll

3. **webfetch** built-in as fallback

## Anti-Detection

- Google: accept cookies (`Accept all`) or prefer DuckDuckGo
- Respect `robots.txt`
- Realistic user-agent (Playwright handles this by default)
- No burst of requests: wait 1-2s between navigations

## Structured Extraction

- Use Playwright snapshots (accessibility tree) to extract content
- Prefer stable selectors (data attributes, ARIA roles) over CSS classes
- For tables/lists, extract and format in markdown

## Pagination

- Detect "Next" / "Next page" links
- Browse sequentially with a max counter (default: 5 pages)
- Consolidate results at the end

## Common Errors

- 403/429 → wait 5-10s, retry with less aggressiveness
- Cookie wall → click "Accept all" or "Reject all"
- CAPTCHA → give up, suggest an alternative
- Timeout → increase timeout or simplify the target page
