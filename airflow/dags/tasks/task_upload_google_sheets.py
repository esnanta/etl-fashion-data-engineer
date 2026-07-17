from __future__ import annotations

from datetime import datetime
from pathlib import Path

from pipeline.load import save_to_google_sheets
from pipeline.storage import (
    DataLayer,
    DatasetArtifact,
    load_processed_dataset,
)

DATASET_NAME = "products"


def upload_google_sheets_task(
    artifact_path: str,
) -> bool:
    """
    Upload a Processed Dataset Artifact
    into Google Sheets.
    """
    processed_artifact = DatasetArtifact(
        dataset=DATASET_NAME,
        layer=DataLayer.PROCESSED,
        created_at=datetime.now(),
        path=Path(artifact_path),
    )

    dataframe = load_processed_dataset(
        processed_artifact,
    )

    result = save_to_google_sheets(
        product_data=dataframe,
    )

    if not result:
        raise RuntimeError(
            "Failed to upload dataset to Google Sheets."
        )

    return True