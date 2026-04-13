# ProNexus

A full-stack LinkedIn content generation platform powered by Claude. Given an industry and topic focus, ProNexus scrapes live signals from Reddit, Hacker News, and Semantic Scholar, synthesizes a trend brief, and generates ready-to-post LinkedIn content with A/B hooks, linting, similarity checking, and suggested comments.

**Live:** https://pronexus-frontend.vercel.app  
**Backend:** Deployed on Railway

---

## How it works

1. **Scraping** — Pulls live data from 10 AI-focused subreddits (RSS), top Hacker News stories, and Semantic Scholar academic papers across 7 research queries.
2. **Trend brief** — Claude synthesizes scraped signals into a structured trend brief scoped to your industry and topic focus.
3. **Post generation** — Claude generates a weekly batch of LinkedIn posts, each with two hook variants (A/B), a body, and a CTA.
4. **Enrichment** — Each post is run through three parallel pipelines:
   - **Linter** — checks tone, structure, and LinkedIn best practices
   - **Similarity checker** — flags posts that are too similar to each other
   - **Comment generator** — produces suggested engagement comments
5. **Feedback loop** — Users can rate posts and log which hook they chose; feedback is persisted for future style refinement.

---

## Stack

**Backend**
- FastAPI + Python
- Claude API (trend brief, post generation, linting, similarity, comments)
- `aiohttp` + `feedparser` for async scraping
- `ThreadPoolExecutor` for parallel post enrichment
- Deployed on Railway

**Frontend**
- React + TypeScript + Tailwind CSS
- Framer Motion (intro animation)
- react-joyride (feature tour)
- Deployed on Vercel

---

## API

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/generate` | Full pipeline: scrape → brief → posts → enrichment |
| GET | `/api/v1/trends` | Scrape and return trend brief only |
| POST | `/api/v1/scrape` | Trigger scrape, return item counts |
| POST | `/api/v1/posts/{id}/lint` | Lint a specific post |
| POST | `/api/v1/posts/{id}/similarity` | Check similarity for a post |
| POST | `/api/v1/posts/{id}/comments` | Generate suggested comments |
| POST | `/api/v1/posts/{id}/feedback` | Log user feedback |
| GET | `/api/v1/style-guide` | Return saved style guide |

---

## Setup

**Backend**
```bash
cd backend
pip install -r requirements.txt
# set CLAUDE=your_api_key in .env
uvicorn main:app --reload
```

**Frontend**
```bash
cd frontend
npm install
npm run dev
```

---

## Data sources

- **Reddit** — r/MachineLearning, r/LocalLLaMA, r/ChatGPT, r/ClaudeAI, and 6 others (no API key required, RSS)
- **Hacker News** — Top stories via Firebase API, filtered by score > 50
- **Semantic Scholar** — Academic papers across 7 AI/LLM research queries
