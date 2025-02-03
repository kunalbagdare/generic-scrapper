# Generic E-Commerce Scraper

This project provides a generic scraper that identifies product URLs from e-commerce domains. It uses Playwright for browser automation and a fallback to the `requests` library in case Playwright fails. The scraper is designed to identify product URLs based on common patterns (such as `/product/`, `/item/`, and SKU/EAN-like numbers in the URL). This allows the scraper to handle a variety of e-commerce sites with different URL structures.

## Features

- Identifies product URLs using a combination of regex patterns (e.g., `/product/`, `/item/`, SKU/EAN-like numbers).
- Uses Playwright for web scraping with browser automation.
- Falls back to `requests` for scraping if Playwright fails.
- Filters URLs to ensure that only product URLs from the same domain are considered.
- Handles multiple domains and efficiently scrapes them concurrently.
- Extracts product URLs from category pages and individual product pages.

## Requirements

You can install the required dependencies by running:

```bash
pip install -r requirements.txt
```

## Usage
1. Set the domains you want to scrape in the `domains_to_scrape` list inside `main.py`:

```bash
domains_to_scrape = [
    "https://www.flipkart.com/", 
    "https://www.amazon.in/",
]
```
2. Run the scraper:
```
python main.py
```

## Output
The scraper outputs the collected product URLs in a JSON file named `product_urls.json`:
```
{
    "https://www.flipkart.com/": [
        "https://www.flipkart.com/product1",
        "https://www.flipkart.com/product2"
    ],
    "https://www.amazon.in/": [
        "https://www.amazon.in/product1",
        "https://www.amazon.in/product2"
    ]
}

