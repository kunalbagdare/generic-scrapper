import requests
import asyncio
import json
import re
from playwright.async_api import async_playwright
from urllib.parse import urljoin, urlparse
from .headers import get_random_headers

class GenericPlaywrightScraper:
    
    def __init__(self, domains):

        """ Initialize the scraper. """

        self.domains = domains
        self.product_urls = {domain: set() for domain in self.domains}
        self.visited = {domain: set() for domain in self.domains}
        self.error_urls = []
        self.to_visit = {domain: set() for domain in self.domains}

        # Regular expressions to match product URLs
        self.product_url_patterns = [
            re.compile(r".*\/product\/.*"),
            re.compile(r".*\/item\/.*"),
            re.compile(r".*\/dp\/.*"),
            re.compile(r".*\/p\/.*"),
            re.compile(r".*\/products\/.*"),
            re.compile(r".*\d{8,12}.*\.html#?\d*$"),
            re.compile(r".*\d{8,12}.*\.php#?\d*$"), 
            re.compile(r".*\d{8,12}.*\.aspx#?\d*$"),
            re.compile(r".*#\d{8,12}$")
        ]

    def make_full_url(self, base_url, url):

        """ Make a full URL from a relative URL and a base URL. """

        if url.startswith(('http://', 'https://')):
            return url
        if url.startswith('//'):
            return "https:" + url
        if url.startswith('/'):
            return urljoin(base_url, url)
        return None

    def is_product_url(self, url):

        """ Check if a URL is a product URL. """

        if not url:
            return False
        return any(pattern.match(url) for pattern in self.product_url_patterns)


    def is_same_domain(self, base_url, target_url):
        
        """ Check if two URLs belong to the same domain. """

        base_domain = urlparse(base_url).netloc
        target_domain = urlparse(target_url).netloc
        return base_domain == target_domain

    async def extract_product_urls(self, page, domain, depth=0):

        """ Extract product URLs from a page. """

        if depth > 3:
            return

        
        await page.wait_for_load_state("domcontentloaded")

        all_links = await page.query_selector_all('a')

        for link in all_links:
            try:
                url = await link.get_attribute('href')
                if not url:
                    continue

                full_url = self.make_full_url(domain, url)
                if not full_url or full_url in self.visited[domain]:
                    continue

                self.visited[domain].add(full_url)

                
                if self.is_product_url(full_url):
                    print(f"Found product URL: {full_url}")
                    self.product_urls[domain].add(full_url)
                elif self.is_same_domain(domain, full_url):
                    print(f"Adding category URL for further scanning: {full_url}")
                    self.to_visit[domain].add(full_url)

            except Exception as e:
                print(f"Error extracting URL from {domain}: {e}")
                self.error_urls.append({"domain": domain, "error": str(e)})


    async def visit_page(self, page, url, domain):
        """
        Visit a page and extract product URLs.
        """
        try:
            response = await page.goto(url)
            if response and response.status == 200:
                await self.extract_product_urls(page, domain)
        except Exception as e:
            self.error_urls.append({"domain": domain, "url": url, "error": str(e)})

    async def scrape_with_playwright(self, browser, domain):
        """ Scrape a domain using Playwright. """

        context = await browser.new_context(
            extra_http_headers=get_random_headers(),
            ignore_https_errors=True
        )
        page = await context.new_page()

        retries = 3
        while retries > 0:
            try:
                print(f"Scraping domain: {domain}")
                await page.goto(domain, timeout=60000, wait_until="domcontentloaded")
                await self.extract_product_urls(page, domain)
                break
            except Exception as e:
                retries -= 1
                print(f"Error loading {domain}: {e}. Retries left: {retries}")
                if retries == 0:
                    print(f"Failed to scrape {domain} using Playwright. Falling back to requests.")
                    
                    headers = get_random_headers()
                    self.scrape_using_requests(domain, headers)

        await page.close()

    def scrape_using_requests(self, domain, headers):
        """Fallback method to scrape using requests if Playwright fails."""

        try:
            response = requests.get(domain, headers=headers, timeout=30)
            if response.status_code == 200:
                self.extract_product_urls_from_html(response.text, domain)
            else:
                print(f"Failed to scrape {domain} with status code {response.status_code}")
                self.error_urls.append({"domain": domain, "error": "Failed with status code"})
        except requests.exceptions.RequestException as e:
            print(f"Error scraping {domain} with requests: {e}")
            self.error_urls.append({"domain": domain, "error": str(e)})

    def extract_product_urls_from_html(self, html, domain):

        """Process HTML and extract product URLs using regex."""
        links = re.findall(r'href=["\'](.*?)["\']', html)
        for link in links:
            full_url = self.make_full_url(domain, link)
            if self.is_product_url(full_url):
                self.product_urls[domain].add(full_url)

    async def scrape(self):
        """ Start scraping all the domains. """

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            tasks = [self.scrape_with_playwright(browser, domain) for domain in self.domains]
            await asyncio.gather(*tasks)
            await browser.close()

    def save_output(self, output_file='product_urls.json'):
        """ Save the product URLs to a file. """
        
        with open(output_file, 'w') as f:
            json.dump({domain: list(urls) for domain, urls in self.product_urls.items()}, f, indent=4)
        print(f"Product URLs saved to {output_file}")
