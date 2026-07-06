# =================================================================================================
# INTEGRATION TEST
#
# Goal:
#   Tests the entire local pipeline end-to-end, ensuring all internal modules integrate correctly.
#   Unit tests for individual functions are separate.
#
# Pipeline Flow:
#   1. (MOCK) Website
#   2. scrape_data
#   3. save_raw
#   4. load_raw
#   5. validate_raw
#   6. transform
#   7. save_processed
#   8. load_processed
#   9. create_export
#   10. save_to_csv
#   11. CSV File
#   12. save_to_google_sheets (MOCK)
#
# Mocks:
#   - scrape_data(): Avoids internet dependency.
#   - save_to_google_sheets(): Avoids hitting the actual Google API.
#
# Acceptance Criteria:
#   - Pipeline completes without exceptions.
#   - Raw, Processed, and CSV artifacts are successfully created.
#   - CSV contains the correctly transformed data.
#   - "Unknown Product" entries are filtered out during transformation.
#   - save_to_google_sheets() is called exactly once.
# =================================================================================================


import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import pandas as pd

from pipeline.storage import DataLayer
from scripts import run_pipeline


class TestRunPipeline(unittest.TestCase):
    """Integration test for the complete local pipeline."""

    @patch("scripts.run_pipeline.save_to_google_sheets")
    @patch("scripts.run_pipeline.scrape_data")
    def test_run_pipeline_end_to_end(
        self,
        mock_scrape_data,
        mock_save_to_google_sheets,
    ):
        """
        Execute the complete pipeline using mocked external services
        and real internal pipeline components.
        """
        rows = [
            {
                "Title": "Classic Shirt",
                "Price": "$10.00",
                "Rating": "Rating: 4.5 / 5",
                "Colors": "3 Colors",
                "Size": "Size: M",
                "Gender": "Gender: Men",
                "timestamp": "2026-07-05T00:00:00Z",
            },
            {
                "Title": "Unknown Product",
                "Price": "$20.00",
                "Rating": "Rating: 4.8 / 5",
                "Colors": "2 Colors",
                "Size": "Size: L",
                "Gender": "Gender: Women",
                "timestamp": "2026-07-05T00:00:00Z",
            },
        ]

        mock_scrape_data.return_value = rows
        mock_save_to_google_sheets.return_value = True

        with tempfile.TemporaryDirectory() as tmp_dir:

            data_directory = Path(tmp_dir)

            artifacts = {}

            original_save_raw = run_pipeline.save_raw_dataset
            original_save_processed = run_pipeline.save_processed_dataset
            original_create_export = run_pipeline.create_export_artifact

            def save_raw_wrapper(*args, **kwargs):
                kwargs["data_directory"] = data_directory

                artifact = original_save_raw(*args, **kwargs)
                artifacts["raw"] = artifact

                return artifact

            def save_processed_wrapper(*args, **kwargs):
                kwargs["data_directory"] = data_directory

                artifact = original_save_processed(*args, **kwargs)
                artifacts["processed"] = artifact

                return artifact

            def create_export_wrapper(*args, **kwargs):
                kwargs["data_directory"] = data_directory

                artifact = original_create_export(*args, **kwargs)
                artifacts["csv"] = artifact

                return artifact

            with (
                patch(
                    "scripts.run_pipeline.save_raw_dataset",
                    side_effect=save_raw_wrapper,
                ),
                patch(
                    "scripts.run_pipeline.save_processed_dataset",
                    side_effect=save_processed_wrapper,
                ),
                patch(
                    "scripts.run_pipeline.create_export_artifact",
                    side_effect=create_export_wrapper,
                ),
            ):
                run_pipeline.main()

            self.assertIn("raw", artifacts)
            self.assertIn("processed", artifacts)
            self.assertIn("csv", artifacts)

            raw_artifact = artifacts["raw"]
            processed_artifact = artifacts["processed"]
            csv_artifact = artifacts["csv"]

            self.assertEqual(
                raw_artifact.layer,
                DataLayer.RAW,
            )
            self.assertTrue(raw_artifact.path.exists())

            self.assertEqual(
                processed_artifact.layer,
                DataLayer.PROCESSED,
            )
            self.assertTrue(processed_artifact.path.exists())

            self.assertEqual(
                csv_artifact.layer,
                DataLayer.EXPORT,
            )
            self.assertTrue(csv_artifact.path.exists())

            dataframe = pd.read_csv(csv_artifact.path)

            self.assertFalse(dataframe.empty)
            self.assertEqual(len(dataframe), 1)
            self.assertEqual(
                dataframe.iloc[0]["Title"],
                "Classic Shirt",
            )
            self.assertNotIn(
                "Unknown Product",
                dataframe["Title"].tolist(),
            )

            mock_scrape_data.assert_called_once_with(
                run_pipeline.DEFAULT_BASE_URL,
                progress_callback=run_pipeline._print_scrape_progress,
            )

            mock_save_to_google_sheets.assert_called_once()


if __name__ == "__main__":
    unittest.main()