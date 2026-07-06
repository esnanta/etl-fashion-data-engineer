# ETL Fashion Data Engineer

This repository is a **case-study project** from a data engineer learning path, focused on practicing the end-to-end workflow: extracting, transforming, and loading data in a clean and testable way.

The scenario simulates a fashion retail company that needs competitor product data from **Fashion Studio** (`https://fashion-studio.dicoding.dev/`) to support analytics and downstream data science work.

![Fashion studio website](https://github.com/esnanta/etl-fashion-data-engineer/blob/main/images/fashion_studio.png)

## Case Study

In this project, you take the role of a data engineer in a fashion retail business. The company wants structured competitor data (title, price, rating, color variants, size, and gender) to monitor market trends.

This project is intentionally designed as a learning-focused ETL pipeline that demonstrates:

- modular code organization.
- data cleaning and type normalization.
- basic data quality handling.
- automated tests for each ETL stage.

## Project Goals

- Scrape product data from multiple pages of the target website.
- Clean and standardize raw web data.
- Convert price from USD to IDR (`1 USD = Rp16,000`).
- Remove invalid, null, and duplicate records.
- Save production-ready output to CSV.
- Validate behavior with unit tests.

![Sample products.csv output](https://raw.githubusercontent.com/esnanta/etl-fashion-data-engineer/main/images/output_data_scraping.png)

## Modular Architecture

This repository is built with a modular structure so each concern is isolated and easy to maintain.

```text
etl-fashion-data-engineer/
├── data/
├── docs/
├── images/
│   ├── fashion_studio.png
│   ├── log_scrape_data.png
│   ├── log_test_run.png
│   ├── output_data_scraping.png
│   ├── test_coverage.png
│   ├── test_extract.png
│   ├── test_load.png
│   └── test_transform.png
├── pipeline/
│   ├── extract.py
│   ├── load.py
│   ├── storage.py
│   ├── transform.py
│   └── validation.py
├── scripts/
│   └── run_pipeline.py
├── tests/
│   ├── integration/
│   └── unit/
├── .env.example
├── .gitignore
├── google-sheets-api.json-example
├── products.csv
├── pytest.ini
├── README.md
└── requirements.txt
```

### Module Breakdown

- `scripts/run_pipeline.py`
  - Pipeline orchestrator.
  - Executes the 5-step ETL flow: Extract -> Validate -> Transform -> Export -> Upload.

- `pipeline/extract.py`
  - Web scraping logic (request + HTML parsing with BeautifulSoup).
  - Extracts raw fields from product cards.
  - Adds extraction `timestamp`.
  - Includes request and extraction error handling.

- `pipeline/transform.py`
  - Data cleaning and normalization logic.
  - Parses fields (`Price`, `Rating`, `Colors`, `Size`, `Gender`).
  - Converts `Price` from USD to IDR.
  - Removes invalid rows (e.g., `Unknown Product`), null values, and duplicates.
  - Enforces expected output data types.

- `pipeline/load.py`
  - Data loading/output logic.
  - Saves transformed data into `products.csv` and Google Sheets.
  - Includes basic save-time error handling.

- `pipeline/validation.py`
  - Contains functions for data validation.

- `pipeline/storage.py`
  - Handles saving data to different formats or locations.

- `tests/`
  - Unit and integration tests for each ETL stage:
    - `tests/unit/`
    - `tests/integration/`
  - Ensures modular components can be verified independently.

![Sample test coverage](https://github.com/esnanta/etl-fashion-data-engineer/blob/main/images/test_coverage.png)

## ETL Flow

```text
┌──────────────────┐
│ Fashion Studio │
│    (Website)   │
└────────┬─────────┘
         │
         ▼
┌───────────────────┐
│  pipeline.extract │
│   (scrape_data)   │
└─────────┬─────────┘
          │
          ▼
┌──────────────────────────┐
│ data/raw/{dataset}.json  │
│      (Raw Artifact)      │
└───────────┬──────────────┘
            │
            ▼
┌────────────────────┐
│ pipeline.validation│
│(validate_raw_dataset)│
└──────────┬─────────┘
           │
           ▼
┌────────────────────┐
│ pipeline.transform │
│  (transform_data)  │
└──────────┬─────────┘
           │
           ▼
┌───────────────────────────────┐
│ data/processed/{dataset}.parquet│
│      (Processed Artifact)     │
└───────────────┬───────────────┘
                │
      ┌─────────┴─────────┐
      │                   │
      ▼                   ▼
┌───────────────┐   ┌─────────────────────────┐
│ pipeline.load │   │     pipeline.load       │
│ (save_to_csv) │   │ (save_to_google_sheets) │
└──────┬────────┘   └────────────┬────────────┘
       │                         │
       ▼                         ▼
┌────────────────┐       ┌────────────────┐
│ data/export/   │       │  Google Sheets │
│ {dataset}.csv  │       └────────────────┘
└────────────────┘
```

## Requirements

- Python 3.10+ (Python 3.12 recommended)
- Dependencies in `requirements.txt`

## Installation

```bash
python -m venv myvenv
source myvenv/bin/activate
pip install -r requirements.txt
```

## Run the Pipeline

Set Google Sheets environment variables in `.env` (the app loads them automatically):

```dotenv
GOOGLE_SHEET_ID=
GOOGLE_SHEET_NAME=
GOOGLE_WORKSHEET_NAME=Sheet1
GOOGLE_SHEETS_CREDENTIAL_PATH=google-sheets-api.json
```

Configuration Notes:

- Provide at least one of: `GOOGLE_SHEET_ID` or `GOOGLE_SHEET_NAME`.
- Share your spreadsheet with service account email from `google-sheets-api.json` as **Editor**.

```bash
python scripts/run_pipeline.py
```

Main output:

- `products.csv`
- Google Sheets worksheet (if Sheets config is valid)

### Running All Tests

To run all tests (both unit and integration), use this command:

```bash
pytest -v
```

### Running Unit Tests

To run only the unit tests, specify the `tests/unit/` directory:

```bash
pytest tests/unit/ -v
```

### Running Integration Tests

To run only the integration tests, specify the `tests/integration/` directory:

```bash
pytest tests/integration/ -v
```

### Test Coverage

To run the tests and generate a coverage report, use this command:

```bash
pytest --cov=pipeline --cov-report=term-missing -v
```

## Expected Data Quality Output

After transformation, the output is expected to satisfy:

- No `Unknown Product` rows.
- No null values in required columns.
- No duplicated records.
- `Price` in IDR (`float`).
- `Rating` as `float`.
- `Colors` as `int`.
- `Size` and `Gender` as clean strings.

## Notes

- This is a learning project from Dicoding and is intended to demonstrate practical ETL fundamentals in Python.
- The case-study website and data are simulated for educational purposes.