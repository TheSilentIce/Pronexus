# test_pipeline.py (put this in root of project)

import asyncio
import json
from scraper import scrape_all
from trend_brief import generate_trend_brief


async def main():
    print("Scraping...")
    data = await scrape_all()
    print(f"Got {data['total']} items")

    print("\nGenerating trend brief...")
    brief = generate_trend_brief(
        scraped_data=data,
        industry="Computer Science / B2B SaaS",
        topic_focus="AI agent workflows",
    )

    print(json.dumps(brief, indent=2))

    # save it
    with open("./corpus/trend_brief.json", "w") as f:
        json.dump(brief, f, indent=2)

    print("\nSaved to corpus/trend_brief.json")


asyncio.run(main())
