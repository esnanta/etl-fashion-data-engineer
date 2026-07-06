import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import pandas as pd

from pipeline.load import save_to_csv, save_to_google_sheets
from pipeline.storage import (
    create_export_artifact,
)

class TestSaveToCsv(unittest.TestCase):
    """Test it saving transformed data into CSV output."""

    def test_save_to_csv_returns_none_for_none_input(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            artifact = create_export_artifact(
                dataset="products",
                extension=".csv",
                data_directory=Path(tmp_dir),
            )

            with self.assertLogs("pipeline.load", level="WARNING") as logs:
                result = save_to_csv(None, artifact)

            self.assertIsNone(result)
            self.assertIn(
                "No data provided to save.",
                logs.output[0],
            )

    def test_save_to_csv_returns_none_when_write_fails(self):
        df = pd.DataFrame([{"Title": "Any"}])

        with tempfile.TemporaryDirectory() as tmp_dir:
            artifact = create_export_artifact(
                dataset="products",
                extension=".csv",
                data_directory=Path(tmp_dir),
            )

            with patch.object(
                    pd.DataFrame,
                    "to_csv",
                    side_effect=Exception("Disk full"),
            ):
                with self.assertLogs("pipeline.load", level="ERROR") as logs:
                    result = save_to_csv(df, artifact)

            self.assertIsNone(result)
            self.assertIn(
                "Failed to save data to CSV: Disk full",
                logs.output[0],
            )


    def test_save_to_csv_returns_none_for_empty_rows(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            artifact = create_export_artifact(
                dataset="products",
                extension=".csv",
                data_directory=Path(tmp_dir),
            )

            with self.assertLogs("pipeline.load", level="WARNING") as logs:
                result = save_to_csv([], artifact)

            self.assertIsNone(result)
            self.assertIn(
                "No rows to save.",
                logs.output[0],
            )

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
            artifact = create_export_artifact(
                dataset="products",
                extension=".csv",
                data_directory=Path(tmp_dir),
            )

            with self.assertLogs("pipeline.load", level="INFO") as logs:
                result = save_to_csv(rows, artifact)

            self.assertIsNotNone(result)
            self.assertTrue(result.path.exists())

            saved = pd.read_csv(result.path)

            self.assertEqual(len(saved), 1)
            self.assertEqual(
                saved.iloc[0]["Title"],
                "Classic Shirt",
            )

            self.assertIn(
                f"Data saved to {result.path}",
                logs.output[0],
            )


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
            artifact = create_export_artifact(
                dataset="products",
                extension=".csv",
                data_directory=Path(tmp_dir),
            )

            with self.assertLogs("pipeline.load", level="INFO") as logs:
                result = save_to_csv(
                    df,
                    artifact,
                )

            self.assertIsNotNone(result)
            self.assertTrue(result.path.exists())

            saved = pd.read_csv(result.path)

            self.assertEqual(len(saved), 1)
            self.assertEqual(
                saved.iloc[0]["Title"],
                "Hoodie",
            )

            self.assertIn(
                f"Data saved to {result.path}",
                logs.output[0],
            )


class TestSaveToGoogleSheets(unittest.TestCase):
    """Test saving transformed data into Google Sheets output."""

    def test_save_to_google_sheets_returns_false_if_spreadsheet_target_missing(self):
        df = pd.DataFrame([{"Title": "Classic Shirt"}])

        with self.assertLogs("pipeline.load", level="WARNING") as logs:
            result = save_to_google_sheets(df, spreadsheet_id="", spreadsheet_name="")

        self.assertFalse(result)
        self.assertIn("Spreadsheet ID/name is missing. Skip Google Sheets save.", logs.output[0])

    @patch("pipeline.load.gspread", create=True)
    def test_save_to_google_sheets_returns_false_for_missing_credentials(self, mock_gspread):
        df = pd.DataFrame([{"Title": "Classic Shirt"}])
        mock_gspread.service_account.side_effect = FileNotFoundError("not found")

        with self.assertLogs("pipeline.load", level="ERROR") as logs:
            result = save_to_google_sheets(
                df,
                spreadsheet_id="dummy-spreadsheet-id",
                credential_path="/tmp/not-found-credentials.json",
            )

        self.assertFalse(result)
        self.assertIn("Google Sheets credential file not found", logs.output[0])

    @patch("pipeline.load.gspread", create=True)
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

        with self.assertLogs("pipeline.load", level="INFO") as logs:
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

    @patch("pipeline.load.gspread", create=True)
    def test_save_to_google_sheets_success_with_spreadsheet_name(self, mock_gspread):
        df = pd.DataFrame([{"Title": "Classic Shirt"}])

        mock_worksheet = unittest.mock.Mock()
        mock_spreadsheet = unittest.mock.Mock()
        mock_spreadsheet.worksheet.return_value = mock_worksheet

        mock_client = unittest.mock.Mock()
        mock_client.open.return_value = mock_spreadsheet
        mock_gspread.service_account.return_value = mock_client

        with self.assertLogs("pipeline.load", level="INFO") as logs:
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

