# services/style_guide.py

import anthropic
import os
import json
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic(api_key=os.getenv("CLAUDE"))


def load_corpus() -> list[dict]:
    corpus_path = os.path.join(
        os.path.dirname(__file__), "./corpus/quality-examples.json"
    )
    with open(corpus_path, "r") as f:
        return json.load(f)


def generate_style_guide(industry: str, topic_focus: str) -> dict:
    corpus = load_corpus()

    # format corpus for prompt
    formatted = "\n\n---\n\n".join(
        [
            f"POST {p['id']} | Hook Type: {p['hook_type']} | Format: {p['format']} | Length: {p['post_length']} | Likes: {p.get('likes', 'N/A')}\n\nHOOK: {p['hook']}\n\nBODY: {p['body']}\n\nCTA: {p.get('cta', 'None')}"
            for p in corpus
        ]
    )

    prompt = f"""You are an expert LinkedIn content strategist analyzing high-performing B2B posts.

Below are {len(corpus)} real LinkedIn posts with engagement data.

Analyze them and extract a reusable style guide for creating viral LinkedIn content in:
- Industry: {industry}
- Topic Focus: {topic_focus}

Extract and output the following as JSON:

{{
  "hook_patterns": [
    {{
      "type": "contrarian | question | number-led | story | bold-claim | breaking-news | timeline",
      "template": "reusable template string with [PLACEHOLDERS]",
      "example": "example from corpus",
      "avg_engagement": "high | medium | low"
    }}
  ],
  "body_patterns": {{
    "optimal_length": "short | medium | long",
    "line_break_style": "description of how to use line breaks",
    "bullet_usage": "when to use bullets vs prose",
    "rhythm": "description of sentence rhythm and pacing",
    "credibility_moves": ["list of techniques that build credibility"]
  }},
  "cta_patterns": [
    "reusable CTA template 1",
    "reusable CTA template 2"
  ],
  "tone": "description of overall tone",
  "avoid": ["list of things that kill engagement"]
}}

Posts to analyze:
{formatted}
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
            style_guide = json.loads(raw)
        except json.JSONDecodeError:
            last_brace = raw.rfind("}")
            if last_brace != -1:
                salvaged = raw[: last_brace + 1]
                style_guide = json.loads(salvaged)
            else:
                style_guide = {"error": "parse failed", "raw": raw}

    except Exception as e:
        style_guide = {"error": str(e), "raw": raw}

    return style_guide


if __name__ == "__main__":
    guide = generate_style_guide(
        industry="Computer Science / B2B SaaS", topic_focus="AI agent workflows"
    )
    print(json.dumps(guide, indent=2))
