def web_search(query: str, max_results: int = 5) -> str:
    """Search the web and return formatted results. Supports both ddgs and duckduckgo_search."""
    try:
        # Try new package name first
        try:
            from ddgs import DDGS
        except ImportError:
            from duckduckgo_search import DDGS

        results = DDGS().text(query, max_results=max_results)
        if not results:
            return ""
        formatted = []
        for r in results:
            title = r.get("title", "")
            body = r.get("body", "")
            formatted.append(f"[{title}]\n{body}")
        return "\n\n".join(formatted)
    except Exception as e:
        return f"Web search unavailable: {str(e)}"
