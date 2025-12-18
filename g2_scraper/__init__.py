"""
G2 Scraper - Web scraping module for G2.com
Compatible with Apify Actor and standalone usage.

This package provides functions to scrape:
- Product reviews
- Search results

Example:
    from g2_scraper import scrape_reviews_by_count
    from scrapfly import ScrapflyClient
    
    client = ScrapflyClient(key="your-api-key")
    reviews = await scrape_reviews_by_count(
        url="https://www.g2.com/products/asana/reviews",
        scrapfly_client=client,
        target_count=20
    )
"""

# Import scraping functions for public API
from .scrapers import (
    scrape_search,
    scrape_reviews,
    scrape_reviews_by_count,
)

# Import config for consumers who need to modify it
from .config import BASE_CONFIG

# Define public API
__all__ = [
    "scrape_search",
    "scrape_reviews",
    "scrape_reviews_by_count",
    "BASE_CONFIG",
]
