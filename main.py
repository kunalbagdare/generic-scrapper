import asyncio
from assignment.scraper.generic_scrapper import GenericPlaywrightScraper

if __name__ == "__main__":
    
    domains_to_scrape = [
        "https://www.flipkart.com/", 
        "https://www.amazon.in/", 
        "https://www.snapdeal.com/",
        "https://pharmeasy.in/"
    ]
    
    scraper = GenericPlaywrightScraper(domains_to_scrape)
    asyncio.run(scraper.scrape())
    
    scraper.save_output()

