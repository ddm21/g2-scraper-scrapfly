"""
HTML parsing functions for G2 scraper.
All functions are pure - they take HTML responses and return structured data.
"""

import re
import math
from scrapfly import ScrapeApiResponse
from typing import Dict, List
from urllib.parse import urljoin

from .config import REVIEW_PAGE_SIZE, SEARCH_PAGE_SIZE


def parse_search_page(response: ScrapeApiResponse) -> Dict[str, any]:
    """Parse company data from search pages with updated selectors."""
    try:
        selector = response.selector
    except Exception as e:
        print(f"Failed to create selector: {e}")
        return {"search_data": [], "total_pages": 0}

    data = []

    # Extract total results count
    total_results_text = selector.xpath("//div[contains(text(), 'Products')]/following-sibling::div/text()").get()
    total_results = int(re.search(r"\((\d+)\)", total_results_text).group(1)) if total_results_text else 0

    total_pages = math.ceil(total_results / SEARCH_PAGE_SIZE) if total_results else 0

    # Main selector for each product card
    for result in selector.xpath("//section[.//a[contains(@href, '/products/')]]"):
        name = result.xpath(".//div[contains(@class, 'elv-text-lg')]/text()").get()

        relative_link = result.xpath(".//div[contains(@class, 'elv-text-lg')]/parent::a/@href").get()
        link = urljoin(response.request.url, relative_link)

        image = result.xpath(".//img[@alt='Product Avatar Image']/@src").get()

        raw_rate = result.xpath(".//label[contains(text(), '/5')]/text()").get()
        rate = float(raw_rate.split("/")[0]) if raw_rate else None

        raw_reviews = result.xpath(".//a[contains(@href, '#reviews')]//label[not(contains(text(), '/5'))]/text()").get()
        reviews_number = int(raw_reviews.strip("()")) if raw_reviews else None

        description_parts = result.xpath(".//div[div[contains(text(), 'Product Description')]]/p//text()").getall()
        description = "".join(description_parts).strip() if description_parts else None

        categories = result.xpath(".//aside//div[contains(@class, 'elv-whitespace-nowrap')]/text()").getall()

        if not name:
            continue

        data.append(
            {
                "name": name.strip() if name else None,
                "link": link,
                "image": image,
                "rate": rate,
                "reviewsNumber": reviews_number,
                "description": description if description else None,
                "categories": [cat.strip() for cat in categories],
            }
        )

    return {"search_data": data, "total_pages": total_pages}


def parse_review_page(response: ScrapeApiResponse) -> Dict[str, any]:
    """Parse reviews data from G2 company pages."""
    selector = response.selector

    total_reviews_text = selector.xpath("//a[contains(@href, '/reviews#reviews') and contains(text(), 'reviews')]/text()").get()
    if total_reviews_text:
        # Remove commas from number string before converting to int (e.g., "12,767" -> "12767")
        total_reviews = int(total_reviews_text.split()[2].replace(',', ''))
        total_pages = math.ceil(total_reviews / REVIEW_PAGE_SIZE)
    else:
        total_reviews = None
        total_pages = 0

    data = []
    # main review container selector from 'div' to 'article'
    for review in selector.xpath("//article[.//div[@itemprop='reviewBody']]"):
        author_name = review.xpath(".//div[@itemprop='author']/meta[@itemprop='name']/@content").get()
        author_profile = review.xpath(".//div[contains(@class, 'avatar')]/parent::a/@href").get()

        # Author details have a new, less structured format
        author_details = review.xpath(
            ".//div[div[@itemprop='author']]//div[contains(@class, 'elv-text-subtle')]/text()"
        ).getall()
        author_position = author_details[0] if author_details and len(author_details) > 0 else None
        author_company_size = next((detail for detail in author_details if "emp." in detail), None)

        # selector for review tags
        review_tags = review.xpath(
            ".//div[contains(@class, 'gap-3') and contains(@class, 'flex-wrap')]//label/text()"
        ).getall()

        review_date = review.xpath(".//meta[@itemprop='datePublished']/@content").get()
        # selector for review rate using the reliable itemprop meta tag
        review_rate = review.xpath(".//span[@itemprop='reviewRating']/meta[@itemprop='ratingValue']/@content").get()
        review_title = review.xpath(".//div[@itemprop='name']//text()").get()

        # selectors for review likes and dislikes
        review_likes_parts = review.xpath(
            ".//section[div[contains(text(), 'What do you like best')]]/p//text()"
        ).getall()
        review_likes = "".join(review_likes_parts).replace("Review collected by and hosted on G2.com.", "").strip()

        review_dislikes_parts = review.xpath(
            ".//section[div[contains(text(), 'What do you dislike')]]/p//text()"
        ).getall()
        review_dislikes = (
            "".join(review_dislikes_parts).replace("Review collected by and hosted on G2.com.", "").strip()
        )

        data.append(
            {
                "author": {
                    "authorName": author_name.strip() if author_name else None,
                    "authorProfile": author_profile,
                    "authorPosition": (author_position.strip() if author_position else None),
                    "authorCompanySize": (author_company_size.strip() if author_company_size else None),
                },
                "review": {
                    "reviewTags": [tag.strip() for tag in review_tags if tag.strip()],
                    "reviewData": review_date,
                    "reviewRate": float(review_rate) if review_rate else None,
                    "reviewTitle": (review_title.replace('"', "").strip() if review_title else None),
                    "reviewLikes": review_likes,
                    "reviewDislikes": review_dislikes,
                },
            }
        )

    return {"total_pages": total_pages, "reviews_data": data}
