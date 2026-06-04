import os
import tempfile
import unittest
from unittest.mock import patch

import pandas as pd

from utils.load import save_to_csv, save_to_google_sheets


class TestSaveToCsv(unittest.TestCase):
    """Test saving transformed data into CSV output."""

    def test_save_to_csv_returns_false_for_none_input(self):
        with self.assertLogs("utils.load", level="WARNING") as logs:
            result = save_to_csv(None)

        self.assertFalse(result)
        self.assertIn("No data provided to save.", logs.output[0])

    def test_save_to_csv_returns_false_for_empty_rows(self):
        with self.assertLogs("utils.load", level="WARNING") as logs:
            result = save_to_csv([])

        self.assertFalse(result)
        self.assertIn("No rows to save.", logs.output[0])

    def test_save_to_csv_writes_file_for_list_input(self):
        rows = [
            {
                "Title": "Classic Shirt",
                "Price": 160000,
                "Rating": 4.5,
                "Colors": 3,
                "Size": "M",
                "Gender": "Men",
                "timestamp": "2026-06-03T00:00:00+00:00",
            }
        ]

        with tempfile.TemporaryDirectory() as tmp_dir:
            output_path = os.path.join(tmp_dir, "out.csv")

            with self.assertLogs("utils.load", level="INFO") as logs:
                result = save_to_csv(rows, output_path=output_path)

            self.assertTrue(result)
            self.assertTrue(os.path.exists(output_path))

            saved = pd.read_csv(output_path)
            self.assertEqual(len(saved), 1)
            self.assertEqual(saved.iloc[0]["Title"], "Classic Shirt")
            self.assertIn(f"Data saved to {output_path}", logs.output[0])

    def test_save_to_csv_accepts_dataframe_input(self):
        df = pd.DataFrame(
            [
                {
                    "Title": "Hoodie",
                    "Price": 80000,
                    "Rating": 4.0,
                    "Colors": 2,
                    "Size": "L",
                    "Gender": "Women",
                    "timestamp": "2026-06-03T00:00:00+00:00",
                }
            ]
        )

        with tempfile.TemporaryDirectory() as tmp_dir:
            output_path = os.path.join(tmp_dir, "df_out.csv")

            with self.assertLogs("utils.load", level="INFO") as logs:
                result = save_to_csv(df, output_path=output_path)

            self.assertTrue(result)
            self.assertTrue(os.path.exists(output_path))
            self.assertIn(f"Data saved to {output_path}", logs.output[0])

    def test_save_to_csv_returns_false_when_write_fails(self):
        df = pd.DataFrame([{"Title": "Any"}])

        with patch.object(pd.DataFrame, "to_csv", side_effect=Exception("Disk full")):
            with self.assertLogs("utils.load", level="ERROR") as logs:
                result = save_to_csv(df, output_path="/tmp/will-not-write.csv")

        self.assertFalse(result)
        self.assertIn("Failed to save data to CSV: Disk full", logs.output[0])


class TestSaveToGoogleSheets(unittest.TestCase):
    """Test saving transformed data into Google Sheets output."""

    def test_save_to_google_sheets_returns_false_if_spreadsheet_target_missing(self):
        df = pd.DataFrame([{"Title": "Classic Shirt"}])

        with self.assertLogs("utils.load", level="WARNING") as logs:
            result = save_to_google_sheets(df, spreadsheet_id="", spreadsheet_name="")

        self.assertFalse(result)
        self.assertIn("Spreadsheet ID/name is missing. Skip Google Sheets save.", logs.output[0])

    @patch("utils.load.gspread", create=True)
    def test_save_to_google_sheets_returns_false_for_missing_credentials(self, mock_gspread):
        df = pd.DataFrame([{"Title": "Classic Shirt"}])
        mock_gspread.service_account.side_effect = FileNotFoundError("not found")

        with self.assertLogs("utils.load", level="ERROR") as logs:
            result = save_to_google_sheets(
                df,
                spreadsheet_id="dummy-spreadsheet-id",
                credential_path="/tmp/not-found-credentials.json",
            )

        self.assertFalse(result)
        self.assertIn("Google Sheets credential file not found", logs.output[0])

    @patch("utils.load.gspread", create=True)
    def test_save_to_google_sheets_success(self, mock_gspread):
        df = pd.DataFrame(
            [
                {
                    "Title": "Classic Shirt",
                    "Price": 160000,
                    "Rating": 4.5,
                    "Colors": 3,
                    "Size": "M",
                    "Gender": "Men",
                    "timestamp": "2026-06-03T00:00:00+00:00",
                }
            ]
        )

        mock_worksheet = unittest.mock.Mock()
        mock_spreadsheet = unittest.mock.Mock()
        mock_spreadsheet.worksheet.return_value = mock_worksheet

        mock_client = unittest.mock.Mock()
        mock_client.open_by_key.return_value = mock_spreadsheet
        mock_gspread.service_account.return_value = mock_client

        with self.assertLogs("utils.load", level="INFO") as logs:
            result = save_to_google_sheets(
                df,
                spreadsheet_id="dummy-spreadsheet-id",
                worksheet_name="Sheet1",
                credential_path="google-sheets-api.json",
            )

        self.assertTrue(result)
        mock_gspread.service_account.assert_called_once_with(filename="google-sheets-api.json")
        mock_client.open_by_key.assert_called_once_with("dummy-spreadsheet-id")
        mock_spreadsheet.worksheet.assert_called_once_with("Sheet1")
        mock_worksheet.clear.assert_called_once()
        mock_worksheet.update.assert_called_once()
        self.assertIn("Data saved to Google Sheets", logs.output[0])

    @patch("utils.load.gspread", create=True)
    def test_save_to_google_sheets_success_with_spreadsheet_name(self, mock_gspread):
        df = pd.DataFrame([{"Title": "Classic Shirt"}])

        mock_worksheet = unittest.mock.Mock()
        mock_spreadsheet = unittest.mock.Mock()
        mock_spreadsheet.worksheet.return_value = mock_worksheet

        mock_client = unittest.mock.Mock()
        mock_client.open.return_value = mock_spreadsheet
        mock_gspread.service_account.return_value = mock_client

        with self.assertLogs("utils.load", level="INFO") as logs:
            result = save_to_google_sheets(
                df,
                spreadsheet_name="fashion-etl",
                worksheet_name="Sheet1",
                credential_path="google-sheets-api.json",
            )

        self.assertTrue(result)
        mock_gspread.service_account.assert_called_once_with(filename="google-sheets-api.json")
        mock_client.open.assert_called_once_with("fashion-etl")
        mock_worksheet.clear.assert_called_once()
        mock_worksheet.update.assert_called_once()
        self.assertIn("spreadsheet_name=fashion-etl", logs.output[0])


if __name__ == "__main__":
    unittest.main()

