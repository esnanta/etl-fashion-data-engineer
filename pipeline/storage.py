from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path

import pandas as pd


PROJECT_DIRECTORY = Path(__file__).resolve().parent.parent
DATA_DIRECTORY = PROJECT_DIRECTORY / "data"

class DataLayer(Enum):
    RAW = "raw"
    PROCESSED = "processed"
    EXPORT = "export"


@dataclass(frozen=True)
class DatasetArtifact:
    dataset: str
    layer: DataLayer
    created_at: datetime
    path: Path


def save_raw_dataset(
    rows: list[dict],
    dataset: str,
    data_directory: Path = DATA_DIRECTORY
) -> DatasetArtifact:
    """
    Save raw extracted dataset as JSON.
    """
    created_at = datetime.now(timezone.utc)
    artifact = _create_artifact(
        dataset=dataset,
        layer=DataLayer.RAW,
        created_at=created_at,
        extension=".json",
        data_directory=data_directory,
    )

    artifact.path.parent.mkdir(parents=True, exist_ok=True)

    with artifact.path.open("w", encoding="utf-8") as fp:
        json.dump(rows, fp, ensure_ascii=False, indent=2)

    return artifact


def load_raw_dataset(
    artifact: DatasetArtifact,
) -> list[dict]:
    """
    Load raw dataset from JSON artifact.
    """
    with artifact.path.open("r", encoding="utf-8") as fp:
        return json.load(fp)


def save_processed_dataset(
    dataframe: pd.DataFrame,
    dataset: str,
    data_directory: Path = DATA_DIRECTORY
) -> DatasetArtifact:
    """
    Save processed dataset as Parquet.
    """
    created_at = datetime.now(timezone.utc)

    artifact = _create_artifact(
        dataset=dataset,
        layer=DataLayer.PROCESSED,
        created_at=created_at,
        extension=".parquet",
        data_directory=data_directory,
    )

    artifact.path.parent.mkdir(parents=True, exist_ok=True)

    dataframe.to_parquet(
        artifact.path,
        index=False,
    )

    return artifact


def load_processed_dataset(
    artifact: DatasetArtifact,
) -> pd.DataFrame:
    """
    Load processed dataset from Parquet artifact.
    """
    return pd.read_parquet(artifact.path)


def artifact_exists(
    artifact: DatasetArtifact,
) -> bool:
    """
    Check whether an artifact exists.
    """
    return artifact.path.exists()


def delete_artifact(
    artifact: DatasetArtifact,
) -> None:
    """
    Delete artifact if it exists.
    """
    if artifact.path.exists():
        artifact.path.unlink()


def _create_artifact(
    *,
    dataset: str,
    layer: DataLayer,
    created_at: datetime,
    extension: str,
    data_directory: Path,
) -> DatasetArtifact:
    """
    Create artifact metadata and path.
    """
    timestamp = created_at.strftime("%Y%m%dT%H%M%SZ")

    path = (
        data_directory
        / layer.value
        / dataset
        / created_at.strftime("%Y")
        / created_at.strftime("%m")
        / created_at.strftime("%d")
        / f"{dataset}_{timestamp}{extension}"
    )

    return DatasetArtifact(
        dataset=dataset,
        layer=layer,
        created_at=created_at,
        path=path,
    )

def create_export_artifact(
    *,
    dataset: str,
    extension: str,
    data_directory: Path = DATA_DIRECTORY,
) -> DatasetArtifact:
    return _create_artifact(
        dataset=dataset,
        layer=DataLayer.EXPORT,
        created_at=datetime.now(timezone.utc),
        extension=extension,
        data_directory=data_directory,
    )