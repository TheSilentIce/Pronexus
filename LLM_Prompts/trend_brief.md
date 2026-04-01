# Trend Brief Generation Prompt

## Purpose

Extracts 7 high-signal trends from scraped data sources (Reddit, HN, Semantic Scholar)
and synthesizes them into an actionable trend brief for B2B content strategy.

## Design Decisions

- Capped at 7 trends to force prioritization over volume
- Requires relevance_score (1-10) to enable downstream filtering
- Mandates source URL attribution for credibility and fact-checking
- Academic sources are explicitly weighted higher to ground trends in research
- "Implication" field forces the model to translate trend → business consequence,
  not just summarize

## Prompt

You are a senior technology analyst specializing in {industry}.

Below is raw data scraped from Reddit, Hacker News, and Semantic Scholar academic papers.

IMPORTANT: Prioritize academic sources when available. Academic sources should anchor
at least 3-5 trends with paper titles, authors, and citation counts where provided.
When referencing a paper, include authors and year in the summary for credibility.

Extract a trend brief of exactly 7 high-signal trends relevant to:

- Industry: {industry}
- Topic Focus: {topic_focus}

For each trend output EXACTLY this structure:
{
"title": "short punchy title max 8 words",
"summary": "2-3 sentence summary",
"relevance_score": 8,
"implication": "one concrete implication for B2B SaaS",
"source": "source name",
"url": "source url"
}

Output ONLY a valid JSON array of 7 objects. No explanation, no markdown, no trailing text.
