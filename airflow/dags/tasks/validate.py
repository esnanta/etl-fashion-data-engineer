from __future__ import annotations

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
) -> str:
    """
    Validate a Raw Dataset Artifact.
    """
    raw_artifact = DatasetArtifact(
        dataset=DATASET_NAME,
        layer=DataLayer.RAW,
        created_at=datetime.now(),
        path=Path(artifact_path),
    )

    rows = load_raw_dataset(
        raw_artifact,
    )

    validate_raw_dataset(rows)

    return artifact_path