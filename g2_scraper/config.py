"""
Configuration constants for G2 scraper.
"""

# Scrapfly configuration for bypassing G2 web scraping blocking
BASE_CONFIG = {
    "asp": True,  # Anti-scraping protection
    "render_js": True,  # Render JavaScript
    "proxy_pool": "public_residential_pool"
}

# Page size constants
REVIEW_PAGE_SIZE = 10  # Number of reviews per page
SEARCH_PAGE_SIZE = 20  # Number of search results per page
