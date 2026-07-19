from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path

from pipeline.load import save_to_csv
from pipeline.storage import (
    DataLayer,
    DatasetArtifact,
    create_export_artifact,
    load_processed_dataset,
)

DATASET_NAME = "products"


def export_csv_task(
    artifact_path: str,
    run_id: str,
) -> str:
    """
    Export a Processed Dataset Artifact
    into a CSV Export Artifact.
    """
    logging.info(
        {
            "message": "Starting CSV export.",
            "correlation_id": run_id,
            "input_artifact_path": artifact_path,
        }
    )

    processed_artifact = DatasetArtifact(
        dataset=DATASET_NAME,
        layer=DataLayer.PROCESSED,
        created_at=datetime.now(),
        path=Path(artifact_path),
    )

    dataframe = load_processed_dataset(
        processed_artifact,
    )
    logging.info(
        {
            "message": f"Loaded dataframe with {len(dataframe)} rows.",
            "correlation_id": run_id,
        }
    )

    csv_artifact = create_export_artifact(
        dataset=DATASET_NAME,
        extension=".csv",
    )

    csv_artifact = save_to_csv(
        product_data=dataframe,
        artifact=csv_artifact,
    )
    logging.info(
        {
            "message": "Successfully saved CSV artifact.",
            "correlation_id": run_id,
            "artifact_path": str(csv_artifact.path),
        }
    )

    return str(csv_artifact.path)
