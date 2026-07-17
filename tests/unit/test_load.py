import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import pandas as pd

from pipeline.load import (
    save_to_csv,
    save_to_google_sheets,
)
from pipeline.storage import (
    create_export_artifact,
)


class TestSaveToCsv(unittest.TestCase):
    """Test saving transformed data into CSV artifacts."""

    def test_save_to_csv_raises_runtime_error_for_none_input(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            artifact = create_export_artifact(
                dataset="products",
                extension=".csv",
                data_directory=Path(tmp_dir),
            )

            with (
                self.assertLogs(
                    "pipeline.load",
                    level="WARNING",
                ) as logs,
                self.assertRaises(
                    RuntimeError,
                ) as error,
            ):
                save_to_csv(
                    None,
                    artifact,
                )

            self.assertEqual(
                str(error.exception),
                "No data provided for CSV export.",
            )

            self.assertIn(
                "No data provided to save.",
                logs.output[0],
            )

    def test_save_to_csv_raises_runtime_error_for_empty_rows(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            artifact = create_export_artifact(
                dataset="products",
                extension=".csv",
                data_directory=Path(tmp_dir),
            )

            with (
                self.assertLogs(
                    "pipeline.load",
                    level="WARNING",
                ) as logs,
                self.assertRaises(
                    RuntimeError,
                ) as error,
            ):
                save_to_csv(
                    [],
                    artifact,
                )

            self.assertEqual(
                str(error.exception),
                "No data provided for CSV export.",
            )

            self.assertIn(
                "No rows to save.",
                logs.output[0],
            )

    def test_save_to_csv_raises_exception_when_write_fails(self):
        df = pd.DataFrame(
            [
                {"Title": "Any"},
            ]
        )

        with tempfile.TemporaryDirectory() as tmp_dir:
            artifact = create_export_artifact(
                dataset="products",
                extension=".csv",
                data_directory=Path(tmp_dir),
            )

            with patch.object(
                pd.DataFrame,
                "to_csv",
                side_effect=OSError("Disk full"),
            ):
                with self.assertRaises(
                    OSError,
                ) as error:
                    save_to_csv(
                        df,
                        artifact,
                    )

            self.assertEqual(
                str(error.exception),
                "Disk full",
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

            with self.assertLogs(
                "pipeline.load",
                level="INFO",
            ) as logs:
                result = save_to_csv(
                    rows,
                    artifact,
                )

            self.assertTrue(
                result.path.exists(),
            )

            saved = pd.read_csv(
                result.path,
            )

            self.assertEqual(
                len(saved),
                1,
            )

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

            with self.assertLogs(
                "pipeline.load",
                level="INFO",
            ) as logs:
                result = save_to_csv(
                    df,
                    artifact,
                )

            self.assertTrue(
                result.path.exists(),
            )

            saved = pd.read_csv(
                result.path,
            )

            self.assertEqual(
                len(saved),
                1,
            )

            self.assertEqual(
                saved.iloc[0]["Title"],
                "Hoodie",
            )

            self.assertIn(
                f"Data saved to {result.path}",
                logs.output[0],
            )