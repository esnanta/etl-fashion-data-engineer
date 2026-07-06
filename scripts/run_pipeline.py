import os

from dotenv import load_dotenv

from pipeline.extract import DEFAULT_BASE_URL, scrape_data
from pipeline.transform import transform_data
from pipeline.load import save_to_csv, save_to_google_sheets
from pipeline.storage import (
    create_export_artifact,
    load_processed_dataset,
    load_raw_dataset,
    save_processed_dataset,
    save_raw_dataset,
)
from pipeline.validation import validate_raw_dataset

load_dotenv()

DATASET_NAME = "products"


def _print_scrape_progress(current, total, collected_rows, page, is_success):
    percent = (current / total * 100) if total else 100
    status = "OK" if is_success else "SKIP"

    print(
        f"[Extract] "
        f"Page {page} "
        f"({current}/{total}, {percent:.1f}%) "
        f"- {status}, "
        f"total rows: {collected_rows}"
    )


def main():
    # Phase 1 : Extract menghasilkan Raw Artifact.
    # ┌─────────┐
    # │ Website │
    # └────┬────┘
    #      │
    #      ▼
    # ┌───────────────┐
    # │ scrape_data() │
    # └───────┬───────┘
    #         │
    #         ▼
    # ┌────────────────────┐
    # │ save_raw_dataset() │
    # └────────────────────┘

    print("[1/5] Extracting data...")
    raw_rows = scrape_data(
        DEFAULT_BASE_URL,
        progress_callback=_print_scrape_progress,
    )
    raw_artifact = save_raw_dataset(
        rows=raw_rows,
        dataset=DATASET_NAME,
    )
    print(
        f"[1/5] Done. "
        f"{len(raw_rows)} rows saved to\n"
        f"      {raw_artifact.path}"
    )

    # Phase 2-3 : Validate & Transform
    # ┌──────────────┐
    # │ Raw Artifact │
    # └──────┬───────┘
    #        │
    #        ▼
    # ┌────────────────────┐
    # │ load_raw_dataset() │
    # └──────────┬─────────┘
    #            │
    #            ▼
    # ┌────────────────────────┐
    # │ validate_raw_dataset() │    # phase 2/5
    # └──────────┬─────────────┘
    #            │
    #            ▼
    # ┌──────────────────┐
    # │ transform_data() │          # phase 3/5
    # └────────┬─────────┘
    #          │
    #          ▼
    # ┌──────────────────────────┐
    # │ save_processed_dataset() │
    # └──────────────────────────┘

    print("[2/5] Validating raw dataset...")
    raw_rows = load_raw_dataset(raw_artifact)
    validate_raw_dataset(raw_rows)
    print("[2/5] Done...")

    print("[3/5] Transforming data...")
    processed_dataframe = transform_data(raw_rows)

    processed_artifact = save_processed_dataset(
        dataframe=processed_dataframe,
        dataset=DATASET_NAME,
    )
    print(
        f"[3/5] Done. "
        f"{len(processed_dataframe)} rows saved to\n"
        f"      {processed_artifact.path}"
    )

    # Phase 4-5 : Load & Upload
    # ┌────────────────────┐
    # │ Processed Artifact │
    # └──────────┬─────────┘
    #            │
    #            ▼
    # ┌──────────────────────────┐
    # │ load_processed_dataset() │  # phase 4 load data
    # └───────────┬──────────────┘
    #             │
    #   ┌─────────┴─────────┐
    #   │                   │
    #   ▼                   ▼
    # ┌───────────────┐   ┌─────────────────────────┐
    # │ save_to_csv() │   │ save_to_google_sheets() │   #phase 5 upload
    # └──────┬────────┘   └────────────┬────────────┘
    #        │                         │
    #        ▼                         ▼
    #    ┌────────┐            ┌──────────────┐
    #    │  CSV   │            │ Google Sheet │
    #    └────────┘            └──────────────┘

    processed_dataframe = load_processed_dataset(
        processed_artifact,
    )

    if processed_dataframe.empty:
        print("No data found.")
        return

    print("[4/5] Export CSV...")
    csv_artifact = create_export_artifact(
        dataset=DATASET_NAME,
        extension=".csv",
    )

    csv_artifact = save_to_csv(
        processed_dataframe,
        csv_artifact,
    )

    if csv_artifact:
        print(
            f"[4/5] Done.\n"
            f"      {csv_artifact.path}"
        )
    else:
        print("[4/5] Failed.")

    print("[5/5] Upload Google Sheets...")

    is_saved = save_to_google_sheets(
        processed_dataframe,
        spreadsheet_id=os.getenv("GOOGLE_SHEET_ID"),
        spreadsheet_name=os.getenv("GOOGLE_SHEET_NAME"),
        worksheet_name=os.getenv(
            "GOOGLE_WORKSHEET_NAME",
            "Sheet1",
        ),
        credential_path=os.getenv(
            "GOOGLE_SHEETS_CREDENTIAL_PATH",
            "google-sheets-api.json",
        ),
    )

    print(
        "[5/5] Done."
        if is_saved
        else "[5/5] Failed."
    )


if __name__ == "__main__":
    main()