from __future__ import annotations

import logging

from pipeline.extract import (
    DEFAULT_BASE_URL,
    scrape_data,
)
from pipeline.storage import save_raw_dataset


DATASET_NAME = "products"


def extract_task(run_id: str) -> str:
    """
    Extract data from website and save it
    as a Raw Dataset Artifact.
    """
    logging.info(
        {
            "message": "Starting data extraction.",
            "correlation_id": run_id,
            "base_url": DEFAULT_BASE_URL,
        }
    )

    rows = scrape_data(DEFAULT_BASE_URL)
    logging.info(
        {
            "message": f"Scraped {len(rows)} rows.",
            "correlation_id": run_id,
        }
    )

    artifact = save_raw_dataset(
        rows=rows,
        dataset=DATASET_NAME,
    )

    logging.info(
        {
            "message": "Successfully saved raw dataset.",
            "correlation_id": run_id,
            "artifact_path": str(artifact.path),
        }
    )

    return str(artifact.path)
