"""Web search and concise Q&A synthesis."""

from typing import List

from duckduckgo_search import DDGS


def _compact_answer(snippets: List[str], query: str) -> str:
    if not snippets:
        return (
            f"I couldn't find a confident web result for '{query}'. "
            "Please try rephrasing your question."
        )
    return " ".join(snippets[:2]).strip()


def search_and_answer(query: str, max_results: int = 5) -> str:
    """Search web and provide a concise synthesized answer."""
    snippets: List[str] = []
    try:
        with DDGS() as ddgs:
            for result in ddgs.text(query, max_results=max_results):
                body = (result.get("body") or "").strip()
                if body:
                    snippets.append(body)
    except Exception as exc:  # noqa: BLE001
        return f"Web search failed: {exc}"
    return _compact_answer(snippets, query)

