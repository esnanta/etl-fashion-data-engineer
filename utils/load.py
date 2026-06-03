import pandas as pd


def save_to_csv(product_data, output_path="products.csv"):
	"""Save transformed product data to a CSV file."""
	try:
		if product_data is None:
			print("No data provided to save.")
			return False

		if isinstance(product_data, pd.DataFrame):
			df = product_data.copy()
		else:
			df = pd.DataFrame(product_data)

		if df.empty:
			print("No rows to save.")
			return False

		df.to_csv(output_path, index=False)
		print(f"Data saved to {output_path}")
		return True
	except Exception as e:
		print(f"Failed to save data to CSV: {e}")
		return False

