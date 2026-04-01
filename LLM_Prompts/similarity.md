# Similarity Checker Prompt

## Purpose

Detects plagiarism and structural over-reliance on corpus examples to ensure
generated content is original and legally safe to publish.

## Design Decisions

- 0-100 score with a hard threshold at 60 gives a clear publishability signal
- closest_match_id enables traceability back to the corpus for human review
- verdict enum (original/too_similar/borderline) avoids numeric interpretation
  ambiguity — borderline posts get flagged for human review rather than auto-rejected
- suggestion field only fires when score > 40 to avoid noise on clearly original content

## Prompt

Compare this NEW POST against the CORPUS of existing posts.
Score 0-100 where 0 = completely original, 100 = copied verbatim.
Flag as too_similar if score > 60.

Output ONLY valid JSON:
{
"similarity_score": 23,
"is_too_similar": false,
"closest_match_id": 4,
"closest_match_excerpt": "...",
"verdict": "original|too_similar|borderline",
"suggestion": "..."
}
