import unittest
from unittest.mock import Mock, patch

from bs4 import BeautifulSoup

from pipeline.extract import DEFAULT_BASE_URL, extract_data, fetch_page, scrape_data


class TestExtractData(unittest.TestCase):
    """
    Test raw field extraction from a product card,
    including complete and missing elements.
    """

    def test_extract_data_with_complete_card(self):
        html = """
        <div class="collection-card">
            <h3 class="product-title">Classic Shirt</h3>
            <div class="price-container"><span class="price">$12.50</span></div>
            <p>Rating: 4.8 / 5</p>
            <p>3 Colors</p>
            <p>Size: M</p>
            <p>Gender: Men</p>
        </div>
        """
        card = BeautifulSoup(html, "html.parser").select_one("div.collection-card")

        row = extract_data(card, extracted_at="2026-06-03T00:00:00+00:00")

        self.assertIsNotNone(row)
        self.assertEqual(row["Title"], "Classic Shirt")
        self.assertEqual(row["Price"], "$12.50")
        self.assertEqual(row["Rating"], "Rating: 4.8 / 5")
        self.assertEqual(row["Colors"], "3 Colors")
        self.assertEqual(row["Size"], "Size: M")
        self.assertEqual(row["Gender"], "Gender: Men")
        self.assertEqual(row["timestamp"], "2026-06-03T00:00:00+00:00")

    def test_extract_data_with_missing_elements(self):
        html = """
        <div class="collection-card">
            <h3 class="product-title">No Detail Product</h3>
        </div>
        """
        card = BeautifulSoup(html, "html.parser").select_one("div.collection-card")

        row = extract_data(card, extracted_at="fixed-ts")

        self.assertIsNotNone(row)
        self.assertEqual(row["Title"], "No Detail Product")
        self.assertIsNone(row["Price"])
        self.assertIsNone(row["Rating"])
        self.assertIsNone(row["Colors"])
        self.assertIsNone(row["Size"])
        self.assertIsNone(row["Gender"])
        self.assertEqual(row["timestamp"], "fixed-ts")


class TestFetchPage(unittest.TestCase):
    """
    Test HTTP page fetching behavior for successful responses
    and timeout failures.
    """

    @patch("pipeline.extract.requests.get")
    def test_fetch_page_success(self, mock_get):
        response = Mock()
        response.content = b"<html>ok</html>"
        response.raise_for_status.return_value = None
        mock_get.return_value = response

        content = fetch_page("https://example.com")

        self.assertEqual(content, b"<html>ok</html>")
        mock_get.assert_called_once()

    @patch("builtins.print")
    @patch("pipeline.extract.requests.get")
    def test_fetch_page_timeout(self, mock_get, mock_print):
        import requests

        mock_get.side_effect = requests.exceptions.Timeout()

        content = fetch_page("https://example.com")

        self.assertIsNone(content)
        mock_print.assert_called_once_with("Timeout while fetching URL: https://example.com")


class TestScrapeData(unittest.TestCase):
    """
    Test end-to-end scraping flow across pages and
    skipping pages that fail to fetch.
    """

    @patch("pipeline.extract.fetch_page")
    def test_scrape_data_collects_data_from_multiple_pages(self, mock_fetch_page):
        page_1 = b"""
        <html><body>
            <div class="collection-card">
                <h3 class="product-title">Product A</h3>
                <div class="price-container"><span class="price">$10.00</span></div>
                <p>Rating: 4.5 / 5</p><p>2 Colors</p><p>Size: M</p><p>Gender: Men</p>
            </div>
        </body></html>
        """
        page_2 = b"""
        <html><body>
            <div class="collection-card">
                <h3 class="product-title">Product B</h3>
                <div class="price-container"><span class="price">$20.00</span></div>
                <p>Rating: 4.0 / 5</p><p>4 Colors</p><p>Size: L</p><p>Gender: Women</p>
            </div>
        </body></html>
        """

        def fake_fetch(url):
            if url == DEFAULT_BASE_URL:
                return page_1
            if url == f"{DEFAULT_BASE_URL.rstrip('/')}/page2":
                return page_2
            return None

        mock_fetch_page.side_effect = fake_fetch

        rows = scrape_data(start_page=1, end_page=2)

        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0]["Title"], "Product A")
        self.assertEqual(rows[1]["Title"], "Product B")

        timestamps = {row["timestamp"] for row in rows}
        self.assertEqual(len(timestamps), 1)

    @patch("builtins.print")
    @patch("pipeline.extract.fetch_page", return_value=None)
    def test_scrape_data_skips_failed_page(self, mock_fetch_page, mock_print):
        rows = scrape_data(start_page=1, end_page=1)

        self.assertEqual(rows, [])
        mock_fetch_page.assert_called_once()
        mock_print.assert_called_once_with("Skipping page 1 because fetch failed.")

if __name__ == "__main__":
    unittest.main()
