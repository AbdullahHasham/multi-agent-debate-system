import logging
from ddgs import DDGS

# --- 1. SUPPRESS LIBRARY NOISE ---
# This stops ddgs and httpx from spamming your logs with warnings
logging.getLogger("ddgs").setLevel(logging.ERROR)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)

# --- 2. USE CORRECT LOGGER NAME ---
logger = logging.getLogger(__name__)


def search_web(query: str) -> str:
    """
    Searches the web for a query and returns the top 3 results.
    Uses 'html' backend to avoid rate limits/blocks.
    """
    # --- 3. REPLACE PRINT WITH LOGGER ---
    logger.info(f"Searching web for: {query}")

    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=3, backend="html"))

        if not results:
            return "No results found. (Try a simpler query)"

        # Format the results into a string
        knowledge = ""
        for r in results:
            knowledge += f"Source: {r['title']}\nSnippet: {r['body']}\nURL: {r['href']}\n\n"

        logger.info(f"Search successful. Found {len(knowledge)} chars.")
        return knowledge

    except Exception as e:
        logger.error(f"Search failed: {e}")
        return f"Search failed. Error: {e}"