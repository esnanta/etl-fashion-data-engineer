from __future__ import annotations

from pipeline.storage import (
    DataLayer,
    DatasetArtifact,
    load_raw_dataset,
)
from pipeline.validation import validate_raw_dataset


def validate_task(
    raw_artifact: DatasetArtifact,
) -> DatasetArtifact:
    """
    Validate a Raw Dataset Artifact.
    """
    if raw_artifact.layer is not DataLayer.RAW:
        raise ValueError(
            "Validate task only accepts Raw Dataset Artifact."
        )

    rows = load_raw_dataset(raw_artifact)
    validate_raw_dataset(rows)
    return raw_artifact