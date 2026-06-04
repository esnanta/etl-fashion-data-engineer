import logging

import pandas as pd

try:
	import gspread
	from gspread.exceptions import WorksheetNotFound
except ModuleNotFoundError:
	gspread = None

	class WorksheetNotFound(Exception):
		"""Fallback exception when gspread is unavailable."""


logger = logging.getLogger(__name__)

def _prepare_dataframe(product_data):
	"""
	Convert product data into a non-empty DataFrame
	or return None.
	"""
	if product_data is None:
		logger.warning("No data provided to save.")
		return None

	if isinstance(product_data, pd.DataFrame):
		df = product_data.copy()
	else:
		df = pd.DataFrame(product_data)

	if df.empty:
		logger.warning("No rows to save.")
		return None

	return df


def save_to_csv(product_data, output_path="products.csv"):
	"""Save transformed product data to a CSV file."""
	try:
		df = _prepare_dataframe(product_data)
		if df is None:
			return False

		df.to_csv(output_path, index=False)
		logger.info("Data saved to %s", output_path)
		return True
	except Exception as e:
		logger.error("Failed to save data to CSV: %s", e, exc_info=True)
		return False


def save_to_google_sheets(
	product_data,
	spreadsheet_id=None,
	spreadsheet_name=None,
	worksheet_name="Sheet1",
	credential_path="google-sheets-api.json",
):
	"""
	Save transformed product data
	to a Google Sheets worksheet.
	"""
	try:
		df = _prepare_dataframe(product_data)
		if df is None:
			return False

		if not spreadsheet_id and not spreadsheet_name:
			logger.warning("Spreadsheet ID/name is missing. Skip Google Sheets save.")
			return False

		if gspread is None:
			logger.error("gspread is not installed. Skip Google Sheets save.")
			return False

		gc = gspread.service_account(filename=credential_path)
		if spreadsheet_id:
			try:
				spreadsheet = gc.open_by_key(spreadsheet_id)
			except Exception as open_by_key_error:
				if not spreadsheet_name:
					raise
				logger.warning(
					"Failed opening spreadsheet by ID. Fallback to name '%s'. Error: %s",
					spreadsheet_name,
					open_by_key_error,
				)
				spreadsheet = gc.open(spreadsheet_name)
		else:
			spreadsheet = gc.open(spreadsheet_name)

		try:
			worksheet = spreadsheet.worksheet(worksheet_name)
		except WorksheetNotFound:
			worksheet = spreadsheet.add_worksheet(
				title=worksheet_name,
				rows=max(len(df) + 1, 1000),
				cols=max(len(df.columns), 10),
			)

		values = [df.columns.tolist()] + (
			df.where(pd.notna(df), None).values.tolist()
		)

		worksheet.clear()
		worksheet.update(values)
		target = spreadsheet_id if spreadsheet_id else spreadsheet_name
		target_kind = "spreadsheet_id" if spreadsheet_id else "spreadsheet_name"
		logger.info(
			"Data saved to Google Sheets %s=%s worksheet=%s",
			target_kind,
			target,
			worksheet_name,
		)
		return True
	except FileNotFoundError:
		logger.error(
			"Google Sheets credential file not found at %s",
			credential_path,
			exc_info=True,
		)
		return False
	except Exception as e:
		logger.error("Failed to save data to Google Sheets: %s", e, exc_info=True)
		return False


