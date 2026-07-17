from __future__ import annotations

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
) -> str:
    """
    Export a Processed Dataset Artifact
    into a CSV Export Artifact.
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

    csv_artifact = create_export_artifact(
        dataset=DATASET_NAME,
        extension=".csv",
    )

    csv_artifact = save_to_csv(
        product_data=dataframe,
        artifact=csv_artifact,
    )

    return str(csv_artifact.path)