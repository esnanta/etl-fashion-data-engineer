from __future__ import annotations

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
) -> str:
    """
    Transform a Raw Dataset Artifact into
    a Processed Dataset Artifact.
    """
    raw_artifact = DatasetArtifact(
        dataset=DATASET_NAME,
        layer=DataLayer.RAW,
        created_at=datetime.now(),
        path=Path(artifact_path),
    )

    raw_rows = load_raw_dataset(
        raw_artifact,
    )

    processed_dataframe = transform_data(
        raw_rows,
    )

    processed_artifact = save_processed_dataset(
        dataframe=processed_dataframe,
        dataset=DATASET_NAME,
    )

    return str(processed_artifact.path)