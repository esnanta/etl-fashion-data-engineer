import os
import tempfile
import unittest
from unittest.mock import patch

import pandas as pd

from utils.load import save_to_csv


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


if __name__ == "__main__":
    unittest.main()

