"""Tools exposed to the LangGraph agent."""
from __future__ import annotations

import httpx
import trafilatura
from langchain_core.tools import tool

from app.retriever import get_retriever

_HTTP_TIMEOUT = 15.0
_MAX_PAGE_CHARS = 8000


@tool
def search_compileit(query: str) -> str:
    """Sök i det indexerade innehållet från compileit.com.

    Returnerar de mest relevanta textstyckena tillsammans med deras käll-URL:er.
    Använd alltid detta verktyg först för att svara på frågor om Compileit.

    Args:
        query: En sökfråga på svenska, t.ex. "AI-tjänster" eller "kontorsadress Stockholm".
    """
    retriever = get_retriever()
    docs = retriever.invoke(query)
    if not docs:
        return "Inga relevanta resultat hittades i indexet."

    parts = []
    for i, doc in enumerate(docs, 1):
        url = doc.metadata.get("source", "okänd källa")
        title = doc.metadata.get("title", "")
        header = f"[{i}] {title} ({url})" if title else f"[{i}] {url}"
        parts.append(f"{header}\n{doc.page_content.strip()}")
    return "\n\n---\n\n".join(parts)


@tool
def fetch_page(url: str) -> str:
    """Hämta och rensa hela textinnehållet på en specifik sida på compileit.com.

    Använd när användaren ber om en sammanfattning av en hel sida, eller när
    sökresultaten inte räcker för att svara fullständigt.

    Args:
        url: En fullständig URL på compileit.com, t.ex. https://compileit.com/om-oss.
    """
    if "compileit.com" not in url:
        return "Fel: endast URL:er på compileit.com är tillåtna."

    try:
        with httpx.Client(timeout=_HTTP_TIMEOUT, follow_redirects=True) as client:
            resp = client.get(url, headers={"User-Agent": "compileit-rag-bot/0.1"})
            resp.raise_for_status()
    except httpx.HTTPError as exc:
        return f"Kunde inte hämta sidan: {exc}"

    text = trafilatura.extract(resp.text, include_comments=False, include_tables=True)
    if not text:
        return "Sidan kunde hämtas men inget brödtextinnehåll kunde extraheras."
    return text[:_MAX_PAGE_CHARS]


TOOLS = [search_compileit, fetch_page]
