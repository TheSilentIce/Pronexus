# services/comments.py

import anthropic
import os
import json
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic(api_key=os.getenv("CLAUDE"))


def generate_comments(hook: str, body: str, industry: str) -> list[dict]:

    full_post = f"{hook}\n\n{body}"

    prompt = f"""You are a LinkedIn engagement strategist.

Generate 5 high-quality comment replies for this LinkedIn post that will drive engagement.
Industry context: {industry}

POST:
{full_post}

Rules:
- Comments should feel human, not AI-generated
- Mix of: agreement, insight-adding, question-asking, personal story, respectful challenge
- Each comment from a different "persona" (founder, engineer, investor, operator, researcher)
- No emojis unless absolutely natural
- 1-3 sentences max per comment

Return ONLY valid JSON:
[
  {{
    "persona": "early-stage founder",
    "comment": "comment text",
    "type": "agreement | insight | question | story | challenge"
  }}
]
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
        return [{"error": "parse failed", "raw": raw}]
