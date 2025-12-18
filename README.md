# G2 Scraper - Apify Actor

Scrape product reviews and search results from G2.com with ease. This Actor extracts detailed review data and product information using smart pagination.

## 🚀 Quick Start

1. **Get Your Scrapfly API Key**
   - Sign up at [scrapfly.io](https://scrapfly.io/dashboard)
   - Copy your API key from the dashboard
   - Paste it in the "Scrapfly API Key" field when running the Actor

2. **Configure Your Scrape**
   - Enter the G2 product URL (e.g., `https://www.g2.com/products/digitalocean/reviews`)
   - Choose what to scrape: Reviews or Search Results
   - Set the number of reviews you want (default: 5)

3. **Run and Download**
   - Click "Start" to run the Actor
   - Download results from the dataset in JSON, CSV, or Excel format

## 📋 What You Can Scrape

### Reviews (Default)
Extract detailed product reviews including:
- Reviewer information (name, position, company size)
- Review ratings and dates
- Pros and cons
- Review tags and categories

### Search Results
Scrape G2 search pages for:
- Product names and descriptions
- Ratings and review counts
- Product categories
- Product links and images


## ⚙️ Input Configuration

### Required Fields
- **Scrapfly API Key**: Your API key from Scrapfly (secure/encrypted)
- **Product URL**: G2 product page URL

### Main Settings
- **Scrape Type**: Choose Reviews or Search
- **Number of Reviews**: Target number of reviews (default: 5, minimum: 5)
- **Max Pages**: Optional limit on pages to scrape

### Optional Features
- **Enable Search**: Add search scraping to your results

## 💡 Usage Examples

### Example 1: Scrape 25 Reviews
```json
{
  "scrapflyApiKey": "your-api-key",
  "productUrl": "https://www.g2.com/products/digitalocean/reviews",
  "scrapeType": "reviews",
  "numberOfReviews": 25
}
```

### Example 2: Search Products
```json
{
  "scrapflyApiKey": "your-api-key",
  "productUrl": "https://www.g2.com/products/digitalocean/reviews",
  "scrapeType": "search",
  "searchUrl": "https://www.g2.com/search?query=Infrastructure",
  "searchMaxPages": 5
}
```

## 📊 Output Format

All data is saved to the Apify dataset with a `_dataType` field:

**Review Output:**
```json
{
  "_dataType": "reviews",
  "author": {
    "authorName": "John Doe",
    "authorPosition": "Software Engineer",
    "authorCompanySize": "50-200 emp."
  },
  "review": {
    "reviewRate": 4.5,
    "reviewTitle": "Great product",
    "reviewLikes": "Easy to use...",
    "reviewDislikes": "Could be cheaper..."
  }
}
```

## 🎯 Smart Features

### Intelligent Pagination
- Specify exactly how many reviews you want
- Actor automatically paginates until target is reached
- Stops early if no more reviews available
- Results trimmed to exact count requested

### Flexible Scraping
- Scrape reviews or search results
- Combine multiple scrape types in one run
- Export data in multiple formats (JSON, CSV, Excel)

## 💰 Cost & Performance

- **Scrapfly Credits**: Uses your Scrapfly API credits for scraping
- **Apify Compute**: Standard Apify compute units apply
- **Speed**: ~30-60 seconds per page depending on content

## ❓ FAQ

**Q: Where do I get a Scrapfly API key?**  
A: Sign up at [scrapfly.io/dashboard](https://scrapfly.io/dashboard) and copy your API key.

**Q: How much does Scrapfly cost?**  
A: Scrapfly offers a free tier with 1,000 API credits. Check their pricing page for details.

**Q: Can I scrape multiple products at once?**  
A: Currently, the Actor processes one product URL per run. For multiple products, run the Actor multiple times or use Apify's batch processing.

**Q: What formats can I export the data in?**  
A: JSON, CSV, Excel, HTML, XML, and RSS - all available from the Apify dataset.

**Q: How many reviews can I scrape?**  
A: There's no hard limit, but we recommend starting with 5-50 reviews per run for optimal performance.

## 🛠️ Support

- **Issues**: Report bugs via the Actor's issue tracker
- **Questions**: Contact support through Apify platform

## 📄 License

This Actor is provided as-is for web scraping G2.com data. Please ensure your usage complies with G2's terms of service and applicable laws.
