from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path

from pipeline.storage import (
    DataLayer,
    DatasetArtifact,
    load_raw_dataset,
    save_processed_dataset,
)
from pipeline.transform import transform_data


DATASET_NAME = "products"


def transform_task(
    artifact_path: str,
    run_id: str,
) -> str:
    """
    Transform a Raw Dataset Artifact into
    a Processed Dataset Artifact.
    """
    logging.info(
        {
            "message": "Starting data transformation.",
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

    raw_rows = load_raw_dataset(
        raw_artifact,
    )
    logging.info(
        {
            "message": f"Loaded {len(raw_rows)} rows from raw dataset.",
            "correlation_id": run_id,
        }
    )

    processed_dataframe = transform_data(
        raw_rows,
    )
    logging.info(
        {
            "message": f"Transformed into a dataframe with {len(processed_dataframe)} rows.",
            "correlation_id": run_id,
        }
    )

    processed_artifact = save_processed_dataset(
        dataframe=processed_dataframe,
        dataset=DATASET_NAME,
    )
    logging.info(
        {
            "message": "Successfully saved processed dataset.",
            "correlation_id": run_id,
            "artifact_path": str(processed_artifact.path),
        }
    )

    return str(processed_artifact.path)
