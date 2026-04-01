# services/linter.py

import anthropic
import os
import json
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic(api_key=os.getenv("CLAUDE"))


def lint_post(hook: str, body: str, cta: str = "") -> dict:

    full_post = f"{hook}\n\n{body}\n\n{cta}".strip()

    prompt = f"""You are an expert LinkedIn content editor who specializes in B2B SaaS posts.

Analyze this LinkedIn post and return a linting report.

POST:
{full_post}

Return ONLY valid JSON, no explanation:
{{
  "score": 85,
  "grade": "A | B | C | D | F",
  "flags": [
    {{
      "type": "weak_hook | vague_claim | fluff | generic_phrasing | too_long | no_credibility | weak_cta | hashtag_spam",
      "severity": "high | medium | low",
      "excerpt": "the specific text that triggered this flag",
      "suggestion": "concrete fix"
    }}
  ],
  "strengths": [
    "specific thing done well"
  ],
  "one_line_verdict": "single sentence summary of post quality"
}}
"""

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
    )

    raw = message.content[0].text.strip()
    if "```" in raw:
        raw = raw.split("```json")[-1].split("```")[0].strip()

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {"error": "parse failed", "raw": raw}
