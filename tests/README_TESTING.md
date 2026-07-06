# Fashion ETL Pipeline Testing

> This document describes the testing strategy for the Fashion ETL Pipeline. Its goal is to ensure that every pipeline component works correctly and that the pipeline is ready for orchestration with Apache Airflow.

Most tests are **unit tests** because they are fast, deterministic, and isolate failures. A single **integration test** verifies that the complete ETL workflow functions correctly from extraction to export.

---

## 🧪 Testing Philosophy

The project follows a two-layer testing strategy:

- **Unit Tests** validate each pipeline module independently.
- **Integration Tests** verify that all modules work together as a complete ETL pipeline.

```text
               Integration Test
                     │
     ┌───────────────┴───────────────┐
     ▼                               ▼
 Extract → Validate → Transform → Export

        ▲
        │
 Unit Tests validate each module independently
```

---

## 📂 Directory Structure

```text
tests/
├── unit/
│   ├── test_extract.py
│   ├── test_validation.py
│   ├── test_transform.py
│   ├── test_storage.py
│   └── test_load.py
└── integration/
    └── test_run_pipeline.py
```

---

## 🔬 Unit Tests

Each unit test validates a single pipeline component in isolation.

| Test File | Purpose |
|-----------|---------|
| `test_extract.py` | Verifies HTML parsing, HTTP requests, and multi-page scraping logic. |
| `test_validation.py` | Ensures raw datasets conform to the required schema. |
| `test_transform.py` | Validates data cleaning, parsing, type conversion, and business rules. |
| `test_storage.py` | Confirms that dataset artifacts can be saved, loaded, and managed correctly. |
| `test_load.py` | Verifies CSV export and Google Sheets upload using mocked external services. |

---

## ⚙️ Integration Test

### `test_run_pipeline.py`

This test executes the **complete local ETL pipeline** to verify end-to-end functionality.

### Pipeline Flow

```text
(Mock Website)
      │
      ▼
   Extract
      │
      ▼
   Validate
      │
      ▼
   Transform
      │
      ▼
 Save / Load Artifacts
      │
      ├──────────────┐
      ▼              ▼
 Export CSV   Google Sheets (Mock)
```

### Testing Strategy

- Only external dependencies are mocked:
  - Website
  - Google Sheets API
- All internal pipeline components execute using their real implementations.

### Goal

Verify that all pipeline components integrate correctly and produce the expected output artifacts.

---

## ✅ Acceptance Criteria

The integration test succeeds only if all of the following conditions are met:

- Pipeline completes without exceptions.
- Raw dataset artifact is created.
- Processed dataset artifact is created.
- CSV export artifact is created.
- Raw dataset validation succeeds.
- Data transformation produces the expected output.
- `Unknown Product` records are removed.
- The exported CSV contains the transformed data.
- Google Sheets upload is invoked exactly once.