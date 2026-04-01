# services/scraper.py

import asyncio
import aiohttp
import feedparser
from bs4 import BeautifulSoup
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

# ─────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────

AI_SUBREDDITS = [
    "MachineLearning",
    "artificial",
    "LocalLLaMA",
    "ChatGPT",
    "ClaudeAI",
    "AIToolsForBusiness",
    "singularity",
    "deeplearning",
    "LanguageTechnology",
    "ArtificialIntelligence",
]

ACADEMIC_QUERIES = [
    "large language model agents 2026",
    "retrieval augmented generation enterprise",
    "AI workflow automation",
    "LLM reasoning evaluation",
    "prompt engineering structured output",
    "multi-agent systems coordination",
    "AI alignment production systems",
]

HN_TOP_STORIES_URL = "https://hacker-news.firebaseio.com/v0/topstories.json"
HN_ITEM_URL = "https://hacker-news.firebaseio.com/v0/item/{}.json"
SEMANTIC_SCHOLAR_URL = "https://api.semanticscholar.org/graph/v1/paper/search"

# ─────────────────────────────────────────
# REDDIT (RSS - no API key needed)
# ─────────────────────────────────────────


def scrape_reddit_rss(limit_per_sub: int = 10) -> list[dict]:
    posts = []
    for sub in AI_SUBREDDITS:
        try:
            feed = feedparser.parse(
                f"https://www.reddit.com/r/{sub}/.rss",
            )
            for entry in feed.entries[:limit_per_sub]:
                summary = entry.get("summary", "") or ""
                posts.append(
                    {
                        "source": f"reddit/r/{sub}",
                        "title": entry.title,
                        "url": entry.link,
                        "text": BeautifulSoup(str(summary), "html.parser").get_text()[
                            :500
                        ],
                    }
                )
        except Exception as e:
            print(f"RSS failed for r/{sub}: {e}")
            continue
    return posts


# ─────────────────────────────────────────
# HACKER NEWS
# ─────────────────────────────────────────


async def fetch_hn_item(session: aiohttp.ClientSession, item_id: int) -> Optional[dict]:
    try:
        async with session.get(HN_ITEM_URL.format(item_id)) as resp:
            item = await resp.json()
            if not item or item.get("type") != "story":
                return None
            return {
                "source": "hackernews",
                "title": item.get("title", ""),
                "url": item.get("url", ""),
                "score": item.get("score", 0),
                "comments": item.get("descendants", 0),
                "text": item.get("text", "")[:500],
            }
    except:
        return None


async def scrape_hackernews(limit: int = 30) -> list[dict]:
    async with aiohttp.ClientSession() as session:
        async with session.get(HN_TOP_STORIES_URL) as resp:
            top_ids = await resp.json()
        tasks = [fetch_hn_item(session, id) for id in top_ids[:limit]]
        results = await asyncio.gather(*tasks)
    return [r for r in results if r and r["score"] > 50]


# ─────────────────────────────────────────
# SCIENCEDIRECT (BeautifulSoup)
# ─────────────────────────────────────────


async def scrape_semantic_scholar(max_per_query: int = 3) -> list[dict]:
    headers = {"User-Agent": "pronexus-scraper/1.0"}
    results = []

    async with aiohttp.ClientSession(headers=headers) as session:
        for query in ACADEMIC_QUERIES:
            try:
                params = {
                    "query": query,
                    "limit": max_per_query,
                    "fields": "title,abstract,year,authors,url,citationCount,externalIds",
                }
                async with session.get(SEMANTIC_SCHOLAR_URL, params=params) as resp:
                    data = await resp.json()

                for paper in data.get("data", []):
                    abstract = paper.get("abstract") or ""
                    authors = paper.get("authors", [])
                    author_names = ", ".join([a["name"] for a in authors[:3]])

                    # build URL
                    url = paper.get("url", "")
                    if not url:
                        paper_id = paper.get("paperId", "")
                        url = f"https://www.semanticscholar.org/paper/{paper_id}"

                    results.append(
                        {
                            "source": "semantic_scholar",
                            "title": paper.get("title", ""),
                            "text": abstract[:500],
                            "url": url,
                            "year": paper.get("year"),
                            "authors": author_names,
                            "citations": paper.get("citationCount", 0),
                            "query": query,
                        }
                    )

            except Exception as e:
                print(f"Semantic Scholar failed for '{query}': {e}")
                continue

    return results


# ─────────────────────────────────────────
# COMBINED ENTRY POINT
# ─────────────────────────────────────────


async def scrape_all() -> dict:
    reddit = scrape_reddit_rss()
    hn = await scrape_hackernews()
    academic = await scrape_semantic_scholar()

    return {
        "reddit": reddit,
        "hackernews": hn,
        "academic": academic,
        "total": len(reddit) + len(hn) + len(academic),
    }


if __name__ == "__main__":
    import json

    result = asyncio.run(scrape_all())
    # just print counts and first item of each
    print(f"Reddit: {len(result['reddit'])} posts")
    print(f"HN: {len(result['hackernews'])} posts")
    print(f"Academic: {len(result['academic'])} posts")
    print(
        "\nFirst HN item:",
        json.dumps(result["hackernews"][0] if result["hackernews"] else {}, indent=2),
    )
    print(
        "\nFirst Academic item:",
        json.dumps(result["academic"][0] if result["academic"] else {}, indent=2),
    )
