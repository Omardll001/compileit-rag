"""Crawl compileit.com using sitemap.xml first, falling back to BFS."""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from urllib.parse import urldefrag, urljoin, urlparse

import httpx
from bs4 import BeautifulSoup

_USER_AGENT = "compileit-rag-bot/0.1 (+https://compileit.com)"
_TIMEOUT = 15.0


@dataclass(frozen=True)
class CrawledPage:
    url: str
    html: str


def _same_domain(url: str, base: str) -> bool:
    return urlparse(url).netloc == urlparse(base).netloc


def _normalize(url: str) -> str:
    url, _ = urldefrag(url)
    return url.rstrip("/")


def _fetch(client: httpx.Client, url: str) -> str | None:
    try:
        r = client.get(url, headers={"User-Agent": _USER_AGENT})
        if r.status_code == 200 and "text/html" in r.headers.get("content-type", "").lower():
            return r.text
        if r.status_code == 200 and url.endswith(".xml"):
            return r.text
    except httpx.HTTPError:
        return None
    return None


def _from_sitemap(client: httpx.Client, base_url: str) -> list[str]:
    """Try /sitemap.xml. Returns list of URLs (empty if none / failed)."""
    sitemap_url = urljoin(base_url.rstrip("/") + "/", "sitemap.xml")
    text = _fetch(client, sitemap_url)
    if not text:
        return []
    soup = BeautifulSoup(text, "xml")
    locs = [loc.get_text().strip() for loc in soup.find_all("loc")]
    # Sitemap index? Recurse one level.
    urls: list[str] = []
    for loc in locs:
        if loc.endswith(".xml"):
            sub = _fetch(client, loc)
            if sub:
                sub_soup = BeautifulSoup(sub, "xml")
                urls.extend(l.get_text().strip() for l in sub_soup.find_all("loc"))
        else:
            urls.append(loc)
    return [_normalize(u) for u in urls if _same_domain(u, base_url)]


def _bfs(client: httpx.Client, base_url: str, max_pages: int, max_depth: int) -> list[CrawledPage]:
    """Fallback: BFS from base_url, same-domain only."""
    start = _normalize(base_url)
    seen: set[str] = {start}
    queue: deque[tuple[str, int]] = deque([(start, 0)])
    pages: list[CrawledPage] = []

    while queue and len(pages) < max_pages:
        url, depth = queue.popleft()
        html = _fetch(client, url)
        if not html:
            continue
        pages.append(CrawledPage(url=url, html=html))

        if depth >= max_depth:
            continue

        soup = BeautifulSoup(html, "lxml")
        for a in soup.find_all("a", href=True):
            link = _normalize(urljoin(url, a["href"]))
            if not link.startswith("http"):
                continue
            if not _same_domain(link, base_url):
                continue
            if link in seen:
                continue
            seen.add(link)
            queue.append((link, depth + 1))

    return pages


def crawl(base_url: str, max_pages: int = 100, max_depth: int = 2) -> list[CrawledPage]:
    """Crawl a site. Prefers sitemap.xml, falls back to BFS."""
    with httpx.Client(timeout=_TIMEOUT, follow_redirects=True) as client:
        sitemap_urls = _from_sitemap(client, base_url)
        if sitemap_urls:
            print(f"[crawl] sitemap.xml found with {len(sitemap_urls)} URLs")
            pages: list[CrawledPage] = []
            for url in sitemap_urls[:max_pages]:
                html = _fetch(client, url)
                if html:
                    pages.append(CrawledPage(url=url, html=html))
            return pages

        print("[crawl] no sitemap.xml, falling back to BFS")
        return _bfs(client, base_url, max_pages=max_pages, max_depth=max_depth)
