import requests
from bs4 import BeautifulSoup
from datetime import datetime, timezone

HEADERS = {
	"User-Agent": (
		"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
		"(KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36"
	)
}

DEFAULT_BASE_URL = "https://fashion-studio.dicoding.dev/"

def extract_data(card, extracted_at=None):
	"""
	Extract raw data from one product card.
	Fields are shaped for the transform stage:
	Title, Price, Rating, Colors, Size, Gender + timestamp.
	"""
	try:
		title_el = card.select_one("h3.product-title")
		price_el = card.select_one(".price-container .price, p.price")
		details = card.select("p")

		title = title_el.get_text(strip=True) if title_el else None
		price = price_el.get_text(strip=True) if price_el else None

		rating = details[0].get_text(strip=True) if len(details) > 0 else None
		colors = details[1].get_text(strip=True) if len(details) > 1 else None
		size = details[2].get_text(strip=True) if len(details) > 2 else None
		gender = details[3].get_text(strip=True) if len(details) > 3 else None

		return {
			"Title": title,
			"Price": price,
			"Rating": rating,
			"Colors": colors,
			"Size": size,
			"Gender": gender,
			"timestamp": extracted_at or datetime.now(timezone.utc).isoformat(),
		}
	except Exception as e:
		# Error handling at extract-function level (advanced criteria)
		print(f"Failed to extract a single card: {e}")
		return None


def fetch_page(url, timeout=15):
	"""
	Fetch page content with error handling.
	Returns page bytes on success, None on failure.
	"""
	try:
		response = requests.get(url, headers=HEADERS, timeout=timeout)
		response.raise_for_status()
		return response.content
	except requests.exceptions.Timeout:
		print(f"Timeout while fetching URL: {url}")
	except requests.exceptions.HTTPError as e:
		print(f"HTTP error while fetching {url}: {e}")
	except requests.exceptions.RequestException as e:
		print(f"Request error while fetching {url}: {e}")
	return None


def scrape_data(base_url=DEFAULT_BASE_URL, start_page=1, end_page=50):
	"""
	Scrape all product pages.
	Page 1: /
	Next pages: /page2 ... /page50
	"""
	all_data = []

	# Keep one extraction timestamp for the same batch run
	extracted_at = datetime.now(timezone.utc).isoformat()

	for page in range(start_page, end_page + 1):
		if page == 1:
			url = base_url
		else:
			url = f"{base_url.rstrip('/')}/page{page}"

		content = fetch_page(url)
		if not content:
			print(f"Skipping page {page} because fetch failed.")
			continue

		soup = BeautifulSoup(content, "html.parser")
		cards = soup.select("div.collection-card")

		if not cards:
			print(f"No product cards found on page {page}: {url}")
			continue

		for card in cards:
			row = extract_data(card, extracted_at=extracted_at)
			if row is not None:
				all_data.append(row)

	return all_data
