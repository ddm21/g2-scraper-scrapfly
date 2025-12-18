"""
Apify Actor for scraping G2.com product reviews and search results.
Uses Scrapfly API for web scraping with anti-bot protection.
"""

import asyncio
from apify import Actor
from scrapfly import ScrapflyClient
from loguru import logger as log
import g2_scraper


async def main():
    """Main Actor entry point."""
    async with Actor:
        # Get input from Apify
        actor_input = await Actor.get_input() or {}
        
        # Validate required inputs
        scrapfly_api_key = actor_input.get("scrapflyApiKey")
        if not scrapfly_api_key:
            await Actor.fail(status_message="Missing required input: scrapflyApiKey")
            return
        
        product_url = actor_input.get("productUrl")
        if not product_url:
            await Actor.fail(status_message="Missing required input: productUrl")
            return
        
        # Get configuration
        scrape_type = actor_input.get("scrapeType", "reviews")
        number_of_reviews = actor_input.get("numberOfReviews", 5)
        max_pages = actor_input.get("maxPages")
        enable_search = actor_input.get("enableSearch", False)
        search_url = actor_input.get("searchUrl")
        search_max_pages = actor_input.get("searchMaxPages", 3)
        
        # Initialize Scrapfly client
        log.info("Initializing Scrapfly client")
        scrapfly_client = ScrapflyClient(key=scrapfly_api_key)
        
        # Enable cache for efficiency
        g2_scraper.BASE_CONFIG["cache"] = True
        
        all_data = {}
        
        try:
            # Main scrape type
            if scrape_type == "reviews":
                log.info(f"Starting review scraping from {product_url}")
                await Actor.set_status_message(f"Scraping reviews (target: {number_of_reviews})...")
                
                if max_pages:
                    # Use max_pages if specified
                    reviews_data = await g2_scraper.scrape_reviews(
                        url=product_url,
                        scrapfly_client=scrapfly_client,
                        max_review_pages=max_pages
                    )
                else:
                    # Use smart pagination by count
                    reviews_data = await g2_scraper.scrape_reviews_by_count(
                        url=product_url,
                        scrapfly_client=scrapfly_client,
                        target_count=number_of_reviews
                    )
                
                all_data["reviews"] = reviews_data
                log.info(f"Scraped {len(reviews_data)} reviews")
                
            elif scrape_type == "search":
                if not search_url:
                    search_url = product_url  # Use product_url as fallback
                    
                log.info(f"Starting search scraping from {search_url}")
                await Actor.set_status_message(f"Scraping search results (max {search_max_pages} pages)...")
                
                search_data = await g2_scraper.scrape_search(
                    url=search_url,
                    scrapfly_client=scrapfly_client,
                    max_scrape_pages=search_max_pages
                )
                
                all_data["search"] = search_data
                log.info(f"Scraped {len(search_data)} search results")
            
            # Optional: Search scraping
            if enable_search and search_url:
                log.info(f"Starting additional search scraping from {search_url}")
                await Actor.set_status_message("Scraping additional search results...")
                
                search_data = await g2_scraper.scrape_search(
                    url=search_url,
                    scrapfly_client=scrapfly_client,
                    max_scrape_pages=search_max_pages
                )
                
                all_data["search"] = search_data
                log.info(f"Scraped {len(search_data)} search results")
            
            # Push data to Apify dataset
            await Actor.set_status_message("Saving results to dataset...")
            
            # Flatten the data for dataset - push each item individually
            items_pushed = 0
            for data_type, data_list in all_data.items():
                if isinstance(data_list, list):
                    for item in data_list:
                        # Add metadata about data type
                        item["_dataType"] = data_type
                        await Actor.push_data(item)
                        items_pushed += 1
            
            log.success(f"Successfully pushed {items_pushed} items to dataset")
            await Actor.set_status_message(f"Completed! Scraped {items_pushed} items")
            
        except Exception as e:
            log.error(f"Actor failed with error: {e}")
            await Actor.fail(
                status_message=f"Scraping failed: {str(e)}",
                exception=e
            )


if __name__ == "__main__":
    asyncio.run(main())
