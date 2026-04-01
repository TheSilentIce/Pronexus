# Style Guide Extraction Prompt

## Purpose

Analyzes a curated corpus of high-performing LinkedIn posts to extract reusable
structural and tonal patterns for content generation.

## Design Decisions

- Uses a manually curated corpus of 10 real high-performing posts rather than
  scraped data to ensure quality signal over noise
- Extracts hook_patterns as reusable templates with [PLACEHOLDERS] to enable
  systematic variation at generation time
- Separates body_patterns from hook_patterns because rhythm and formatting
  decisions are orthogonal to opening strategy
- "avoid" list is as important as the positive patterns — most AI content fails
  because it doesn't know what not to do
- credibility_moves section explicitly encodes the techniques that make B2B
  content feel authoritative without being corporate

## Prompt

You are an expert LinkedIn content strategist analyzing high-performing B2B posts.

Below are {n} real LinkedIn posts with engagement data.

Analyze them and extract a reusable style guide for creating viral LinkedIn content in:

- Industry: {industry}
- Topic Focus: {topic_focus}

Extract and output the following as JSON:
{
"hook_patterns": [...],
"body_patterns": {
"optimal_length": "...",
"line_break_style": "...",
"bullet_usage": "...",
"rhythm": "...",
"credibility_moves": [...]
},
"cta_patterns": [...],
"tone": "...",
"avoid": [...]
}
