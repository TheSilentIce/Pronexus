# main.py
from fastapi.concurrency import run_in_threadpool
from concurrent.futures import ThreadPoolExecutor
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import asyncio
import json


from scraper import scrape_all
from trend_brief import generate_trend_brief
from generator import generate_posts
from linter import lint_post
from similarity import check_similarity
from comments import generate_comments
import os

print(f"CLAUDE key present: {bool(os.getenv('CLAUDE'))}")
print(f"CLAUDE key length: {len(os.getenv('CLAUDE', ''))}")

app = FastAPI(title="ProNexus LinkedIn Generator")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─────────────────────────────────────────
# MODELS
# ─────────────────────────────────────────


class GenerateRequest(BaseModel):
    industry: str = "Computer Science / B2B SaaS"
    topic_focus: str = "AI agent workflows"
    tone: str = "professional"
    audience: str = "B2B founders and operators"
    length: str = "medium"
    posts_per_week: int = 3


class LintRequest(BaseModel):
    hook: str
    body: str
    cta: Optional[str] = ""


class SimilarityRequest(BaseModel):
    hook: str
    body: str


class CommentsRequest(BaseModel):
    hook: str
    body: str
    industry: str = "Computer Science / B2B SaaS"


class FeedbackRequest(BaseModel):
    post_id: int
    hook_chosen: str  # "a" or "b"
    rating: int  # 1-5
    impressions: Optional[int] = None
    comments_count: Optional[int] = None


# ─────────────────────────────────────────
# CACHE (in-memory for demo)
# ─────────────────────────────────────────

cache = {"trend_brief": None, "generated_posts": None, "feedback": []}

# ─────────────────────────────────────────
# ROUTES
# ─────────────────────────────────────────


@app.get("/")
def root():
    return {"status": "ProNexus LinkedIn Generator running"}


@app.get("/api/v1/health")
def health():
    return {"status": "ok"}


# --- SCRAPE + TRENDS ---


@app.post("/api/v1/scrape")
async def scrape():
    try:
        data = await scrape_all()
        return {"status": "success", "total": data["total"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/trends")
async def get_trends(
    industry: str = "Computer Science / B2B SaaS",
    topic_focus: str = "AI agent workflows",
):
    try:
        data = await scrape_all()
        brief = generate_trend_brief(
            scraped_data=data, industry=industry, topic_focus=topic_focus
        )
        cache["trend_brief"] = brief
        return brief
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# --- GENERATE ---


@app.post("/api/v1/generate")
async def generate(req: GenerateRequest):
    try:
        print("🚀 Generate hit")

        # scrape + trend brief + posts in threadpool
        data = await scrape_all()
        print(f"✅ Scraped {data['total']} items")

        brief = await run_in_threadpool(
            generate_trend_brief,
            scraped_data=data,
            industry=req.industry,
            topic_focus=req.topic_focus,
        )
        print("✅ Trend brief done")

        posts = await run_in_threadpool(
            generate_posts,
            industry=req.industry,
            topic_focus=req.topic_focus,
            trend_brief=brief,
            tone=req.tone,
            audience=req.audience,
            length=req.length,
            posts_per_week=req.posts_per_week,
        )
        print(f"✅ Posts done: {len(posts)}")

        # parallelize enrichment
        def enrich_post(post):
            hook = post.get("hook_a", "")
            body = post.get("body", "")
            cta = post.get("cta", "")
            return {
                **post,
                "lint": lint_post(hook, body, cta),
                "similarity": check_similarity(hook, body),
                "suggested_comments": generate_comments(hook, body, req.industry),
            }

        with ThreadPoolExecutor(max_workers=5) as executor:
            print("🔍 Starting enrichment...")
            futures = [executor.submit(enrich_post, post) for post in posts]
            enriched = []
            for i, f in enumerate(futures):
                try:
                    result = f.result()
                    enriched.append(result)
                    print(f"✅ Enriched post {i+1}")
                except Exception as e:
                    print(f"❌ Enrichment failed for post {i+1}: {e}")
                    enriched.append(
                        {
                            **posts[i],
                            "lint": {},
                            "similarity": {},
                            "suggested_comments": [],
                        }
                    )
        print("✅ Enrichment done")

        cache["generated_posts"] = enriched
        return {"status": "success", "trend_brief": brief, "posts": enriched}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# --- POST ACTIONS ---


@app.post("/api/v1/posts/{post_id}/lint")
def lint(post_id: int, req: LintRequest):
    try:
        return lint_post(req.hook, req.body, req.cta)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/posts/{post_id}/similarity")
def similarity(post_id: int, req: SimilarityRequest):
    try:
        return check_similarity(req.hook, req.body)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/posts/{post_id}/comments")
def comments(post_id: int, req: CommentsRequest):
    try:
        return generate_comments(req.hook, req.body, req.industry)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/posts/{post_id}/feedback")
def feedback(post_id: int, req: FeedbackRequest):
    try:
        entry = {
            "post_id": post_id,
            "hook_chosen": req.hook_chosen,
            "rating": req.rating,
            "impressions": req.impressions,
            "comments_count": req.comments_count,
        }
        cache["feedback"].append(entry)

        # save to file for persistence
        os.makedirs("corpus", exist_ok=True)
        feedback_path = "corpus/feedback.json"
        existing = []
        if os.path.exists(feedback_path):
            with open(feedback_path, "r") as f:
                existing = json.load(f)
        existing.append(entry)
        with open(feedback_path, "w") as f:
            json.dump(existing, f, indent=2)

        return {"status": "saved", "entry": entry}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/style-guide")
def style_guide():
    try:
        path = "corpus/style_guide.json"
        if not os.path.exists(path):
            raise HTTPException(status_code=404, detail="Style guide not found")
        with open(path, "r") as f:
            return json.load(f)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
