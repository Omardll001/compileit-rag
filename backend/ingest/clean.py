"""Extract clean main-content text from HTML using trafilatura."""
from __future__ import annotations

from dataclasses import dataclass

import trafilatura
from bs4 import BeautifulSoup


@dataclass(frozen=True)
class CleanedPage:
    url: str
    title: str
    text: str


def clean(url: str, html: str) -> CleanedPage | None:
    text = trafilatura.extract(
        html,
        include_comments=False,
        include_tables=True,
        favor_recall=True,
    )
    if not text or len(text.strip()) < 100:
        return None

    title = ""
    try:
        soup = BeautifulSoup(html, "lxml")
        if soup.title and soup.title.string:
            title = soup.title.string.strip()
    except Exception:  # noqa: BLE001
        pass

    return CleanedPage(url=url, title=title, text=text.strip())
