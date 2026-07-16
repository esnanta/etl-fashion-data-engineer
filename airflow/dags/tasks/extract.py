from __future__ import annotations

from pipeline.extract import (
    DEFAULT_BASE_URL,
    scrape_data,
)
from pipeline.storage import (
    DatasetArtifact,
    save_raw_dataset,
)

DATASET_NAME = "products"


def extract_task() -> DatasetArtifact:
    """
    Extract data from a website and save it
    as a Raw Dataset Artifact.
    """
    rows = scrape_data(DEFAULT_BASE_URL)

    artifact = save_raw_dataset(
        rows=rows,
        dataset=DATASET_NAME,
    )

    return artifact