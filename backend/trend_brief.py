# services/trend_brief.py

import anthropic
import os
import json
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic(api_key=os.getenv("CLAUDE"))

# ─────────────────────────────────────────
# TREND BRIEF GENERATOR
# ─────────────────────────────────────────


def generate_trend_brief(
    scraped_data: dict,
    industry: str,
    topic_focus: str,
) -> dict:

    all_items = (
        scraped_data.get("reddit", [])
        + scraped_data.get("hackernews", [])
        + scraped_data.get("academic", [])
    )

    formatted = "\n".join(
        [
            f"- [{item['source']}] {item['title']}: {item.get('text', '')[:200]} | URL: {item.get('url', 'N/A')}"
            for item in all_items[:60]
        ]
    )

    prompt = f"""You are a senior technology analyst specializing in {industry}.

Below is raw data scraped from Reddit, Hacker News, and Semantic Scholar academic papers.

IMPORTANT: Prioritize academic sources (Semantic Scholar papers) over Reddit/HN when available.
Academic sources should anchor at least 3-5 trends with paper titles, authors, and citation counts.
When referencing a paper, include authors and year in the summary for credibility.

Extract a trend brief of exactly 7 high-signal trends relevant to:
- Industry: {industry}
- Topic Focus: {topic_focus}

For each trend output EXACTLY this structure:
{{
  "title": "short punchy title max 8 words",
  "summary": "2-3 sentence summary",
  "relevance_score": 8,
  "implication": "one concrete implication for B2B SaaS",
  "source": "source name",
  "url": "source url"
}}

Output ONLY a valid JSON array of 7 objects. No explanation, no markdown, no trailing text.

Raw data:
{formatted}
"""

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=8096,
        messages=[{"role": "user", "content": prompt}],
    )

    raw = message.content[0].text.strip()

    # strip markdown code fences if present
    if "```" in raw:
        raw = raw.split("```json")[-1].split("```")[0].strip()

    # try parsing directly
    try:
        trends = json.loads(raw)
    except json.JSONDecodeError:
        # salvage: find last complete object
        last = raw.rfind("}]")
        if last != -1:
            trends = json.loads(raw[: last + 2])
        else:
            last = raw.rfind("}")
            if last != -1:
                try:
                    trends = json.loads(raw[: last + 1] + "]")
                except:
                    trends = []
            else:
                trends = []

    return {
        "industry": industry,
        "topic_focus": topic_focus,
        "trends": trends,
        "total": len(trends),
    }


if __name__ == "__main__":
    from scraper import scrape_all
    import asyncio

    data = asyncio.run(scrape_all())
    brief = generate_trend_brief(
        scraped_data=data, industry="Computer Science", topic_focus="AI agent workflows"
    )
    print(json.dumps(brief, indent=2))
