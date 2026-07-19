from __future__ import annotations

import logging
import os
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

from pipeline.load import save_to_google_sheets
from pipeline.storage import (
    DataLayer,
    DatasetArtifact,
    load_processed_dataset,
)

load_dotenv()

DATASET_NAME = "products"


def upload_google_sheets_task(
    artifact_path: str,
    run_id: str,
) -> bool:
    """
    Upload a Processed Dataset Artifact
    into Google Sheets.
    """
    logging.info(
        {
            "message": "Starting Google Sheets upload.",
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

    is_saved = save_to_google_sheets(
        product_data=dataframe,
        spreadsheet_id=os.getenv(
            "GOOGLE_SHEET_ID",
        ),
        spreadsheet_name=os.getenv(
            "GOOGLE_SHEET_NAME",
        ),
        worksheet_name=os.getenv(
            "GOOGLE_WORKSHEET_NAME",
            "Sheet1",
        ),
        credential_path=os.getenv(
            "GOOGLE_SHEETS_CREDENTIAL_PATH",
            "google-sheets-api.json",
        ),
    )

    if not is_saved:
        logging.error(
            {
                "message": "Failed to upload dataset to Google Sheets.",
                "correlation_id": run_id,
            }
        )
        raise RuntimeError(
            "Failed to upload dataset to Google Sheets."
        )

    logging.info(
        {
            "message": "Successfully uploaded dataset to Google Sheets.",
            "correlation_id": run_id,
        }
    )

    return True
