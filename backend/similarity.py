# services/similarity.py

import anthropic
import os
import json
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic(api_key=os.getenv("CLAUDE"))


def load_corpus() -> list[dict]:
    path = os.path.join(os.path.dirname(__file__), "./corpus/quality-examples.json")
    with open(path, "r") as f:
        return json.load(f)


def check_similarity(hook: str, body: str) -> dict:
    corpus = load_corpus()

    corpus_text = "\n\n---\n\n".join(
        [f"POST {p['id']}: {p['hook']}\n{p['body']}" for p in corpus]
    )

    full_post = f"{hook}\n\n{body}"

    prompt = f"""You are a plagiarism detection system for LinkedIn content.

Compare this NEW POST against the CORPUS of existing posts.

NEW POST:
{full_post}

CORPUS:
{corpus_text}

Return ONLY valid JSON:
{{
  "similarity_score": 23,
  "is_too_similar": false,
  "closest_match_id": 4,
  "closest_match_excerpt": "the overlapping phrase or idea",
  "verdict": "original | too_similar | borderline",
  "suggestion": "how to differentiate if needed"
}}

Score 0-100 where 0 = completely original, 100 = copied verbatim.
Flag as too_similar if score > 60.
"""

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=512,
        messages=[{"role": "user", "content": prompt}],
    )

    raw = message.content[0].text.strip()
    if "```" in raw:
        raw = raw.split("```json")[-1].split("```")[0].strip()

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {"error": "parse failed", "raw": raw}
