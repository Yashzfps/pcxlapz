from typing import List

from duckduckgo_search import DDGS

from config import WEB_SEARCH_MAX_RESULTS, WEB_SEARCH_SNIPPET_LIMIT


def _collect_snippets(query: str) -> List[str]:
    snippets: List[str] = []

    with DDGS() as ddgs:
        results = ddgs.text(query, max_results=WEB_SEARCH_MAX_RESULTS)
        for item in results:
            snippet = (item.get("body") or item.get("title") or "").strip()
            if snippet:
                snippets.append(snippet)
            if len(snippets) >= WEB_SEARCH_SNIPPET_LIMIT:
                break

    return snippets


def search_and_answer(query: str) -> str:
    if not query.strip():
        return "Please ask me a question so I can help!"

    try:
        snippets = _collect_snippets(query)
    except Exception:
        return "I couldn't fetch web results right now. Please try again in a moment."

    if not snippets:
        return "I couldn't find reliable results for that right now."

    if len(snippets) == 1:
        return snippets[0]

    return f"{snippets[0]}\nAlso: {snippets[1]}"
