import re
import logging
import pandas as pd

EXCHANGE_RATE_IDR = 16000
logger = logging.getLogger(__name__)

def parse_price_from_usd_to_idr(value):
	"""
	Parse USD price text (e.g., '$102.15') into IDR value.
	Returns:
	 	float | None: Price in IDR as float,
		or None when parsing fails.
	"""
	try:
		if not isinstance(value, str):
			return None
		match = re.search(r"\$\s*([0-9]+(?:\.[0-9]+)?)", value)
		if not match:
			return None
		usd_price = float(match.group(1))
		return float(usd_price * EXCHANGE_RATE_IDR)
	except Exception as e:
		logger.debug("Failed to parse price '%s': %s", value, e, exc_info=True)
		return None


def parse_rating(value):
	"""
	Extract rating from text like 'Rating: ... 4.8 / 5'.
	Returns:
		float | None: Parsed rating value,
		or None when parsing fails.
	"""
	try:
		if not isinstance(value, str):
			return None
		match = re.search(r"([0-9]+(?:\.[0-9]+)?)\s*/\s*5", value)
		if not match:
			return None
		return float(match.group(1))
	except Exception as e:
		logger.debug("Failed to parse rating '%s': %s", value, e, exc_info=True)
		return None


def parse_colors(value):
	"""
	Extract color count from text like '3 Colors'.
	Returns:
		int | None: Parsed color count,
		or None when parsing fails.
	"""
	try:
		if not isinstance(value, str):
			return None
		match = re.search(r"(\d+)\s+Colors?", value, flags=re.IGNORECASE)
		if not match:
			return None
		return int(match.group(1))
	except Exception as e:
		logger.debug("Failed to parse colors '%s': %s", value, e, exc_info=True)
		return None


def parse_size(value):
	"""
	Normalize size from text like 'Size: M'.
	Returns:
		object | None: Cleaned size value,
		or None when parsing fails.
	"""
	try:
		if not isinstance(value, str):
			return None
		parsed = value.replace("Size:", "").strip()
		return parsed or None
	except Exception as e:
		logger.debug("Failed to parse size '%s': %s", value, e, exc_info=True)
		return None


def parse_gender(value):
	"""
	Normalize gender from text like 'Gender: Men'.
	Returns:
		object | None: Cleaned gender value,
		or None when parsing fails.
	"""
	try:
		if not isinstance(value, str):
			return None
		parsed = value.replace("Gender:", "").strip()
		return parsed or None
	except Exception as e:
		logger.debug("Failed to parse gender '%s': %s", value, e, exc_info=True)
		return None


def transform_data(raw_data):
	"""
	Clean and transform raw extracted data.
	- Remove invalid products (e.g., Unknown Product)
	- Parse rating, colors, size, gender
	- Convert price USD to IDR
	- Cast Title, Size, and Gender as object dtype
	- Drop null and duplicates
	"""
	try:
		if raw_data is None:
			return pd.DataFrame()

		if isinstance(raw_data, pd.DataFrame):
			df = raw_data.copy()
		else:
			df = pd.DataFrame(raw_data)

		if df.empty:
			return df

		required_columns = [
			"Title",
			"Price",
			"Rating",
			"Colors",
			"Size",
			"Gender",
			"timestamp",
		]
		missing_cols = [col for col in required_columns if col not in df.columns]
		if missing_cols:
			raise ValueError(f"Missing required columns: {missing_cols}")

		df["Title"] = df["Title"].astype(str).str.strip()
		df = df[df["Title"].str.lower() != "unknown product"]

		df["Price"] = df["Price"].apply(parse_price_from_usd_to_idr)
		df["Rating"] = df["Rating"].apply(parse_rating)
		df["Colors"] = df["Colors"].apply(parse_colors)
		df["Size"] = df["Size"].apply(parse_size)
		df["Gender"] = df["Gender"].apply(parse_gender)

		df = df.dropna(subset=required_columns)
		df = df.drop_duplicates()

		df["Title"] = df["Title"].astype("object")
		df["Price"] = df["Price"].astype("float64")
		df["Rating"] = df["Rating"].astype("float64")
		df["Colors"] = df["Colors"].astype("int64")
		df["Size"] = df["Size"].astype("object")
		df["Gender"] = df["Gender"].astype("object")

		return df.reset_index(drop=True)
	except Exception as e:
		logger.debug("Failed to transform data: %s", e, exc_info=True)
		return pd.DataFrame()

