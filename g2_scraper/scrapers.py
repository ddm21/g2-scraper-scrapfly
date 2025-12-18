"""
Scraping orchestration functions for G2.
Uses Scrapfly client and parser functions to scrape G2.com data.
"""

from scrapfly import ScrapeConfig, ScrapflyClient
from typing import Dict, List
from loguru import logger as log

from .config import BASE_CONFIG
from .parsers import parse_search_page, parse_review_page
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse


def update_url_params(url: str, new_params: Dict[str, any]) -> str:
    """Safely add or update query parameters in a URL."""
    parsed = urlparse(url)
    query_params = parse_qs(parsed.query)
    for k, v in new_params.items():
        query_params[k] = [str(v)]
        
    new_query = urlencode(query_params, doseq=True)
    return urlunparse(parsed._replace(query=new_query))


async def scrape_search(url: str, scrapfly_client: ScrapflyClient, max_scrape_pages: int = None) -> List[Dict]:
    """Scrape company listings from search pages."""
    log.info(f"scraping search page {url}")
    first_page = await scrapfly_client.async_scrape(ScrapeConfig(url, **BASE_CONFIG))
    data = parse_search_page(first_page)
    search_data = data["search_data"]
    total_pages = data["total_pages"]

    # get the total number of pages to scrape
    if max_scrape_pages and max_scrape_pages < total_pages:
        total_pages = max_scrape_pages

    # scrape the remaining search pages concurrently and remove the successful request URLs
    log.info(f"scraping search pagination, remaining ({total_pages - 1}) more pages")
    remaining_urls = [update_url_params(url, {"page": page_number}) for page_number in range(2, total_pages + 1)]
    to_scrape = [ScrapeConfig(url, **BASE_CONFIG) for url in remaining_urls]
    async for response in scrapfly_client.concurrent_scrape(to_scrape):
        try:
            data = parse_search_page(response)
            search_data.extend(data["search_data"])
            # remove the successful requests from the URLs list
            remaining_urls.remove(response.context["url"])
        except Exception as e:  # catch any exception
            log.error(f"Error encountered: {e}")
            continue

    return search_data


async def scrape_reviews(url: str, scrapfly_client: ScrapflyClient, max_review_pages: int = None) -> List[Dict]:
    """Scrape company reviews from G2 review pages."""
    log.info(f"scraping first review page from company URL {url}")
    # Enhanced config
    enhanced_config = {
        **BASE_CONFIG,
        "auto_scroll": True,
        "wait_for_selector": "//section[@id='reviews']//article",
    }
    first_page = await scrapfly_client.async_scrape(ScrapeConfig(url, **enhanced_config))
    data = parse_review_page(first_page)
    reviews_data = data["reviews_data"]
    total_pages = data["total_pages"]

    # get the number of total review pages to scrape
    if max_review_pages and max_review_pages < total_pages:
        total_pages = max_review_pages

    # scrape the remaining review pages
    log.info(f"scraping reviews pagination, remaining ({total_pages - 1}) more pages")
    remaining_urls = [update_url_params(url, {"page": page_number}) for page_number in range(2, total_pages + 1)]
    to_scrape = [ScrapeConfig(url, **enhanced_config) for url in remaining_urls]
    async for response in scrapfly_client.concurrent_scrape(to_scrape):
        try:
            data = parse_review_page(response)
            reviews_data.extend(data["reviews_data"])
        except Exception as e:  # catch any exception
            log.error(f"Error encountered: {e}")
            continue

    log.success(f"scraped {len(reviews_data)} company reviews from G2 review pages with the URL {url}")
    return reviews_data


async def scrape_reviews_by_count(url: str, scrapfly_client: ScrapflyClient, target_count: int = 5) -> List[Dict]:
    """
    Scrape reviews from G2 until target count is reached.
    Intelligently paginates based on the number of reviews needed.
    """
    log.info(f"scraping reviews from {url} until {target_count} reviews are collected")
    
    # Enhanced config - DISABLE cache to ensure each page is scraped fresh
    enhanced_config = {
        **BASE_CONFIG,
        "auto_scroll": True,
        "wait_for_selector": "//section[@id='reviews']//article",
        "cache": False,  # Prevent cached results from returning duplicates
    }
    
    reviews_data = []
    page = 1
    
    while len(reviews_data) < target_count:
        # Build URL with page parameter
        page_url = url if page == 1 else update_url_params(url, {"page": page})
        
        try:
            log.info(f"scraping page {page}, collected {len(reviews_data)}/{target_count} reviews so far")
            response = await scrapfly_client.async_scrape(ScrapeConfig(page_url, **enhanced_config))
            data = parse_review_page(response)
            
            if not data["reviews_data"]:
                log.warning(f"no more reviews found on page {page}, stopping")
                break
            
            reviews_data.extend(data["reviews_data"])
            page += 1
            
            # Stop if we've reached or exceeded the target
            if len(reviews_data) >= target_count:
                break
                
        except Exception as e:
            log.error(f"Error on page {page}: {e}")
            break
    
    # Trim to exact count if we got more than needed
    reviews_data = reviews_data[:target_count]
    
    log.success(f"scraped {len(reviews_data)} reviews from G2")
    return reviews_data
