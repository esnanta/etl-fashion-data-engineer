from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path

from pipeline.storage import (
    DataLayer,
    DatasetArtifact,
    load_raw_dataset,
)
from pipeline.validation import validate_raw_dataset


DATASET_NAME = "products"


def validate_task(
    artifact_path: str,
    run_id: str,
) -> str:
    """
    Validate a Raw Dataset Artifact.
    """
    logging.info(
        {
            "message": "Starting data validation.",
            "correlation_id": run_id,
            "input_artifact_path": artifact_path,
        }
    )

    raw_artifact = DatasetArtifact(
        dataset=DATASET_NAME,
        layer=DataLayer.RAW,
        created_at=datetime.now(),
        path=Path(artifact_path),
    )

    rows = load_raw_dataset(
        raw_artifact,
    )
    logging.info(
        {
            "message": f"Loaded {len(rows)} rows from raw dataset.",
            "correlation_id": run_id,
        }
    )

    validate_raw_dataset(rows)
    logging.info(
        {
            "message": "Successfully validated raw dataset.",
            "correlation_id": run_id,
        }
    )

    return artifact_path
