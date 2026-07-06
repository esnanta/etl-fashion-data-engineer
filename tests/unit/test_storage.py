import unittest
import tempfile
from pathlib import Path
from datetime import datetime, timezone

import pandas as pd
from pandas.testing import assert_frame_equal

from pipeline.storage import (
    DataLayer,
    DatasetArtifact,
    artifact_exists,
    delete_artifact,
    load_processed_dataset,
    load_raw_dataset,
    save_processed_dataset,
    save_raw_dataset,
)


class TestRawDatasetStorage(unittest.TestCase):
    """Test raw dataset artifact storage."""

    def test_save_and_load_raw_dataset(self):
        rows = [
            {
                "Title": "Classic Shirt",
                "Price": "$10.00",
                "Rating": "Rating: 4.5 / 5",
                "Colors": "3 Colors",
                "Size": "Size: M",
                "Gender": "Gender: Men",
                "timestamp": "2026-07-05T00:00:00Z",
            }
        ]

        with tempfile.TemporaryDirectory() as tmp_dir:

            artifact = save_raw_dataset(
                rows=rows,
                dataset="products",
                data_directory=Path(tmp_dir),
            )

            self.assertEqual(artifact.layer, DataLayer.RAW)
            self.assertTrue(artifact.path.exists())

            loaded = load_raw_dataset(artifact)

            self.assertEqual(rows, loaded)


class TestProcessedDatasetStorage(unittest.TestCase):
    """Test processed dataset artifact storage."""

    def test_save_and_load_processed_dataset(self):
        dataframe = pd.DataFrame(
            [
                {
                    "Title": "Classic Shirt",
                    "Price": 160000.0,
                    "Rating": 4.5,
                    "Colors": 3,
                    "Size": "M",
                    "Gender": "Men",
                    "timestamp": "2026-07-05T00:00:00Z",
                }
            ]
        )

        with tempfile.TemporaryDirectory() as tmp_dir:

            artifact = save_processed_dataset(
                dataframe=dataframe,
                dataset="products",
                data_directory=Path(tmp_dir),
            )

            self.assertEqual(artifact.layer, DataLayer.PROCESSED)
            self.assertTrue(artifact.path.exists())

            loaded = load_processed_dataset(artifact)

            assert_frame_equal(
                dataframe,
                loaded,
                check_dtype=False,
            )


class TestArtifactUtility(unittest.TestCase):
    """Test artifact utility functions."""

    def test_artifact_exists(self):
        with tempfile.TemporaryDirectory() as tmp_dir:

            artifact_path = Path(tmp_dir) / "sample.json"

            artifact_path.write_text("[]")

            artifact = DatasetArtifact(
                dataset="products",
                layer=DataLayer.RAW,
                created_at=datetime.now(timezone.utc),
                path=artifact_path,
            )

            self.assertTrue(artifact_exists(artifact))

        self.assertFalse(artifact_exists(artifact))

    def test_delete_artifact(self):
        with tempfile.TemporaryDirectory() as tmp_dir:

            artifact_path = Path(tmp_dir) / "sample.json"

            artifact_path.write_text("[]")

            artifact = DatasetArtifact(
                dataset="products",
                layer=DataLayer.RAW,
                created_at=datetime.now(timezone.utc),
                path=artifact_path,
            )

            self.assertTrue(artifact_exists(artifact))

            delete_artifact(artifact)

            self.assertFalse(artifact_exists(artifact))
