import logging
import pandas as pd


logger = logging.getLogger(__name__)

def save_to_csv(product_data, output_path="products.csv"):
	"""Save transformed product data to a CSV file."""
	try:
		if product_data is None:
			logger.warning("No data provided to save.")
			return False

		if isinstance(product_data, pd.DataFrame):
			df = product_data.copy()
		else:
			df = pd.DataFrame(product_data)

		if df.empty:
			logger.warning("No rows to save.")
			return False

		df.to_csv(output_path, index=False)
		logger.info("Data saved to %s", output_path)
		return True
	except Exception as e:
		logger.error("Failed to save data to CSV: %s", e, exc_info=True)
		return False

