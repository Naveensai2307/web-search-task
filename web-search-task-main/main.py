import requests
from bs4 import BeautifulSoup
from collections import defaultdict
from urllib.parse import urljoin, urlparse
import unittest
from unittest.mock import patch, MagicMock
import sys
from io import StringIO

class WebCrawler:
    """
    WebCrawler crawls a website, indexes its text, and allows keyword search with highlighting.
    """
    def __init__(self):
        self.index = defaultdict(str)
        self.visited = set()

    def crawl(self, url, base_url=None):
        if url in self.visited:
            return
        self.visited.add(url)

        try:
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            self.index[url] = soup.get_text()

            for link in soup.find_all('a'):
                href = link.get('href')
                if href:
                    full_url = urljoin(base_url or url, href)
                    if full_url.startswith(base_url or url):
                        self.crawl(full_url, base_url=base_url or url)
        except Exception as e:
            print(f"Error crawling {url}: {e}")

    def search(self, keyword):
        results = []
        for url, text in self.index.items():
            if keyword.lower() in text.lower():
                results.append(url)
        return results

    def print_results(self, results, keyword=None):
        if results:
            print("Search results:")
            for result in results:
                if keyword and keyword.strip():
                    # Highlight keyword in the result text (case-insensitive)
                    url = result
                    text = self.index.get(result, "")
                    highlighted = text
                    if keyword:
                        import re
                        pattern = re.compile(re.escape(keyword), re.IGNORECASE)
                        highlighted = pattern.sub(lambda m: f"\033[93m{m.group(0)}\033[0m", text)
                    print(f"- {url}\n  ... {highlighted.strip()[:200]} ...")
                else:
                    print(f"- {result}")
        else:
            print("No results found.")

def main():
    crawler = WebCrawler()
    start_url = "https://example.com"
    crawler.crawl(start_url)

    keyword = "test"
    results = crawler.search(keyword)
    crawler.print_results(results, keyword=keyword)

# ---------------------------- UNIT TESTS ----------------------------

class WebCrawlerTests(unittest.TestCase):
    @patch('requests.get')
    def test_crawl_success(self, mock_get):
        sample_html = """
        <html><body>
            <h1>Welcome!</h1>
            <a href="/about">About Us</a>
            <a href="https://www.external.com">External Link</a>
        </body></html>
        """
        mock_response = MagicMock()
        mock_response.text = sample_html
        mock_get.return_value = mock_response

        crawler = WebCrawler()
        crawler.crawl("https://example.com")

        # Should have visited base and internal link
        self.assertIn("https://example.com", crawler.visited)
        self.assertIn("https://example.com/about", crawler.visited)
        self.assertNotIn("https://www.external.com", crawler.visited)

    @patch('requests.get')
    def test_crawl_error(self, mock_get):
        mock_get.side_effect = requests.exceptions.RequestException("Test Error")

        crawler = WebCrawler()
        crawler.crawl("https://example.com")

        # Check if URL still marked as visited despite error
        self.assertIn("https://example.com", crawler.visited)

    def test_search_functionality(self):
        crawler = WebCrawler()
        crawler.index["page1"] = "This contains the keyword"
        crawler.index["page2"] = "This does not"
        results = crawler.search("keyword")
        self.assertEqual(results, ["page1"])

    @patch('sys.stdout', new_callable=StringIO)
    def test_print_results_found(self, mock_stdout):
        crawler = WebCrawler()
        crawler.print_results(["https://test.com/result"])
        self.assertIn("https://test.com/result", mock_stdout.getvalue())

    @patch('sys.stdout', new_callable=StringIO)
    def test_print_results_empty(self, mock_stdout):
        crawler = WebCrawler()
        crawler.print_results([])
        self.assertIn("No results found", mock_stdout.getvalue())

# ---------------------------- RUN BOTH TESTS & MAIN ----------------------------

if __name__ == "__main__":
    print("Running tests...\n")
    unittest.main(exit=False)
    print("\nRunning crawler...\n")
    main()


