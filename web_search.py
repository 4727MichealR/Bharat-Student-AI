
import os
import requests
from dotenv import load_dotenv

load_dotenv()

TAVILY_URL = "https://api.tavily.com/search"


def search_current_information(query):
    """
    Search current web information using Tavily.
    Returns a list of sources with titles, URLs
    and extracted content.
    """

    api_key = os.getenv("TAVILY_API_KEY")

    if not api_key:
        raise RuntimeError(
            "TAVILY_API_KEY is missing from .env"
        )

    if not query or not query.strip():
        raise ValueError("Search query cannot be empty.")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "query": query.strip(),
        "search_depth": "basic",
        "max_results": 5,
        "include_answer": False,
        "include_raw_content": False
    }

    try:
        response = requests.post(
            TAVILY_URL,
            headers=headers,
            json=payload,
            timeout=25
        )

        response.raise_for_status()
        data = response.json()

        sources = []

        for item in data.get("results", []):
            title = item.get("title", "")
            url = item.get("url", "")
            content = item.get("content", "")

            if not url or not content:
                continue

            if not url.startswith(("https://", "http://")):
                continue

            sources.append({
                "title": title,
                "url": url,
                "content": content[:1800]
            })

        return sources

    except requests.RequestException as error:
        raise RuntimeError(
            f"Live web search failed: {error}"
        ) from error
