# services/generator.py

import anthropic
import os
import json
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic(api_key=os.getenv("CLAUDE"))


def load_style_guide() -> dict:
    path = os.path.join(os.path.dirname(__file__), "./corpus/style_guide.json")
    with open(path, "r") as f:
        return json.load(f)


def generate_posts(
    industry: str,
    topic_focus: str,
    trend_brief: dict,
    tone: str = "professional",
    audience: str = "B2B founders and operators",
    length: str = "medium",
    posts_per_week: int = 5,
) -> list[dict]:

    style_guide = load_style_guide()

    trends_formatted = "\n".join(
        [
            f"- {t['title']}: {t['summary']} (Implication: {t['implication']})"
            for t in trend_brief.get("trends", [])
        ]
    )

    prompt = f"""You are an elite LinkedIn content strategist writing for a B2B SaaS audience.

## Style Guide
{json.dumps(style_guide, indent=2)}

## Trend Brief
{trends_formatted}

## Parameters
- Industry: {industry}
- Topic Focus: {topic_focus}
- Tone: {tone}
- Target Audience: {audience}
- Preferred Length: {length}

## Task
Generate {posts_per_week} high-quality LinkedIn posts for this week.

Rules:
- Each post must use a DIFFERENT hook type from the style guide
- No AI slop — no generic phrases like "In today's fast-paced world" or "Game changer"
- Each post must have TWO hook variants (hook_a and hook_b) — same body, different opening
- Use specific numbers, named tools, real implications — not vague claims
- Follow line break and rhythm rules from style guide exactly
- At least 2 posts must reference a specific trend from the trend brief

Output as JSON array:
[
  {{
    "id": 1,
    "hook_type": "contrarian | question | number-led | story | bold-claim | timeline",
    "hook_a": "first hook variant",
    "hook_b": "alternative hook variant",
    "body": "full post body (no hook)",
    "cta": "call to action or null",
    "uses_numbers": true,
    "trend_referenced": "trend title or null",
    "estimated_engagement": "high | medium | low"
  }}
]
"""

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}],
    )

    raw = message.content[0].text

    try:
        if "```" in raw:
            raw = raw.split("```json")[-1].split("```")[0].strip()
        try:
            posts = json.loads(raw)
        except json.JSONDecodeError:
            last_bracket = raw.rfind("]")
            if last_bracket != -1:
                posts = json.loads(raw[: last_bracket + 1])
            else:
                posts = [{"error": "parse failed", "raw": raw}]
    except Exception as e:
        posts = [{"error": str(e), "raw": raw}]

    return posts


if __name__ == "__main__":
    # mock trend brief for testing
    mock_trends = {
        "trends": [
            {
                "title": "AI Agents Replacing Junior Dev Tasks",
                "summary": "LLM agents are now handling code review, ticket triage, and documentation at scale.",
                "implication": "B2B SaaS teams can ship faster with smaller headcount.",
            },
            {
                "title": "RAG Becoming Commodity Infrastructure",
                "summary": "Retrieval augmented generation is now a default feature, not a differentiator.",
                "implication": "Startups need to compete on data quality, not RAG implementation.",
            },
        ]
    }

    posts = generate_posts(
        industry="Computer Science / B2B SaaS",
        topic_focus="AI agent workflows",
        trend_brief=mock_trends,
    )

    print(json.dumps(posts, indent=2))
