# Post Generator Prompt

## Purpose

Generates a weekly batch of LinkedIn posts by combining live trend intelligence
with extracted style patterns from high-performing content.

## Design Decisions

- Each post gets TWO hook variants (A/B) to support split testing without
  requiring a second API call — doubles value at same cost
- "No AI slop" instruction explicitly bans the phrases that kill B2B credibility
  ("game changer", "in today's fast-paced world", "revolutionize")
- Posts are required to use DIFFERENT hook types to ensure batch variety —
  without this constraint the model defaults to the same pattern repeatedly
- trend_referenced field creates a traceable link between live data and output,
  enabling the feedback loop to attribute performance back to source signals
- estimated_engagement field primes downstream linting to focus on the right
  failure modes for each post type

## Prompt

You are an elite LinkedIn content strategist writing for a B2B SaaS audience.

## Style Guide

{style_guide}

## Trend Brief

{trends}

## Parameters

- Industry: {industry}
- Topic Focus: {topic_focus}
- Tone: {tone}
- Target Audience: {audience}

## Rules

- Each post must use a DIFFERENT hook type from the style guide
- No AI slop — no phrases like "In today's fast-paced world" or "Game changer"
- Each post must have TWO hook variants (hook_a and hook_b) — same body, different opening
- Use specific numbers, named tools, real implications — not vague claims
- At least 2 posts must reference a specific trend from the trend brief

Output as JSON array with fields: id, hook_type, hook_a, hook_b, body, cta,
uses_numbers, trend_referenced, estimated_engagement
