# Comment Generator Prompt

## Purpose

Generates realistic engagement-driving comment replies from diverse personas
to seed authentic discussion on published posts.

## Design Decisions

- 5 comments from 5 distinct personas (founder, engineer, investor, operator,
  researcher) because LinkedIn engagement algorithms reward comment diversity,
  not volume from similar profiles
- type enum (agreement/insight/question/story/challenge) maps to the 5 comment
  archetypes that drive the highest reply rates in B2B content
- "respectful challenge" type is deliberately included — counter-perspectives
  drive 3-4x more replies than pure agreement and signal intellectual credibility
- "no emojis unless natural" instruction prevents the AI default toward
  performative enthusiasm that reads as inauthentic to B2B audiences

## Prompt

Generate 5 high-quality comment replies that will drive engagement.
Each comment from a different persona: founder, engineer, investor, operator, researcher.
Mix types: agreement, insight, question, story, challenge.
No emojis unless absolutely natural. 1-3 sentences max.

Output ONLY valid JSON array:
[{"persona": "...", "comment": "...", "type": "..."}]
