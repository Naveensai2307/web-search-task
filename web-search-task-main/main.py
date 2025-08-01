import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import unittest
from unittest.mock import patch, MagicMock
import sys
from io import StringIO

class WebCrawler:
    def __init__(self):
        self.index = dict()
        self.visited = set()

    def crawl(self, url, base_url=None):
        abs_url = urljoin(base_url or url, url)
        if abs_url in self.visited:
            return
        self.visited.add(abs_url)

        try:
            response = requests.get(abs_url)
            soup = BeautifulSoup(response.text, 'html.parser')
            self.index[abs_url] = soup.get_text()

            for link in soup.find_all('a'):
                href = link.get('href')
                if href:
                    next_url = urljoin(abs_url, href)
                    if urlparse(next_url).netloc == urlparse(abs_url).netloc:
                        self.crawl(next_url, base_url=abs_url)
        except Exception as e:
            print(f"Error crawling {abs_url}: {e}")

    def search(self, keyword):
        results = []
        for url, text in self.index.items():
            if keyword.lower() in text.lower():
                results.append(url)
        return results

    def print_results(self, results):
        if results:
            print("Search results:")
            for result in results:
                print(f"- {result}")
        else:
            print("No results found.")

def main():
    crawler = WebCrawler()
    start_url = "https://example.com"
    crawler.crawl(start_url)

    keyword = "test"
    results = crawler.search(keyword)
    crawler.print_results(results)

class WebCrawlerTests(unittest.TestCase):

    @patch('requests.get')
    def test_crawl_success_internal_links_only(self, mock_get):
        html = '''
        <html>
            <body>
                <h1>Welcome to Example</h1>
                <a href="/about">About</a>
                <a href="https://external.com/page">External</a>
            </body>
        </html>
        '''
        mock_response = MagicMock()
        mock_response.text = html
        mock_get.return_value = mock_response

        crawler = WebCrawler()
        crawler.crawl("https://example.com")

        self.assertIn("https://example.com", crawler.index)
        self.assertIn("https://example.com/about", crawler.visited)
        self.assertNotIn("https://external.com/page", crawler.visited)

    @patch('requests.get')
    def test_crawl_error_handling(self, mock_get):
        mock_get.side_effect = requests.exceptions.RequestException("Test exception")

        crawler = WebCrawler()
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            crawler.crawl("https://example.com")
            output = mock_stdout.getvalue()
            self.assertIn("Error crawling https://example.com", output)

    def test_search_keyword_found(self):
        crawler = WebCrawler()
        crawler.index = {
            "https://example.com/page1": "This is some test content",
            "https://example.com/page2": "Unrelated content"
        }
        results = crawler.search("test")
        self.assertEqual(results, ["https://example.com/page1"])

    def test_search_keyword_not_found(self):
        crawler = WebCrawler()
        crawler.index = {
            "https://example.com/page1": "No match here"
        }
        results = crawler.search("missing")
        self.assertEqual(results, [])

    def test_print_results_with_matches(self):
        crawler = WebCrawler()
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            crawler.print_results(["https://example.com/found"])
            output = mock_stdout.getvalue()
            self.assertIn("Search results:", output)
            self.assertIn("- https://example.com/found", output)

    def test_print_results_no_matches(self):
        crawler = WebCrawler()
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            crawler.print_results([])
            output = mock_stdout.getvalue()
            self.assertIn("No results found.", output)

if __name__ == "__main__":
    # You can run either the crawler or the tests.
    # To run crawler: uncomment the line below
    # main()
    
    # To run tests
    unittest.main()
