"""CLI: crawl compileit.com, chunk, embed and persist into Chroma.

Usage:
    python -m ingest.build_index
"""
from __future__ import annotations

import shutil
from pathlib import Path

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.config import settings
from app.retriever import get_vectorstore
from ingest.clean import clean
from ingest.crawl import crawl


def _chunk(docs: list[Document]) -> list[Document]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=100,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    return splitter.split_documents(docs)


def main() -> None:
    print(f"[build_index] crawling {settings.site_base_url}")
    pages = crawl(
        settings.site_base_url,
        max_pages=settings.crawl_max_pages,
        max_depth=settings.crawl_max_depth,
    )
    print(f"[build_index] fetched {len(pages)} pages")

    docs: list[Document] = []
    for p in pages:
        cleaned = clean(p.url, p.html)
        if cleaned is None:
            continue
        docs.append(
            Document(
                page_content=cleaned.text,
                metadata={"source": cleaned.url, "title": cleaned.title},
            )
        )
    print(f"[build_index] {len(docs)} pages had usable content")

    chunks = _chunk(docs)
    print(f"[build_index] split into {len(chunks)} chunks")

    persist_dir = Path(settings.chroma_persist_dir)
    if persist_dir.exists():
        print(f"[build_index] removing old index at {persist_dir}")
        shutil.rmtree(persist_dir)

    vs = get_vectorstore()
    vs.add_documents(chunks)
    print(f"[build_index] index built at {persist_dir.resolve()}")


if __name__ == "__main__":
    main()
