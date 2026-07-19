# Data Orchestration with Apache Airflow

This project uses Apache Airflow to orchestrate the ETL (Extract, Transform, Load) pipeline for fashion data. The business logic resides within the `pipeline/` directory, and Airflow acts as the orchestrator.

## Prerequisites

- Python 3.12
- A virtual environment tool (e.g., `venv`)

## Setup and Installation

1.  **Create and activate a Python virtual environment:**

    ```bash
    python3 -m venv myvenv
    source myvenv/bin/activate
    ```

2.  **Install Apache Airflow:**

    ```bash
    AIRFLOW_VERSION=3.2.2
    PYTHON_VERSION=3.12
    CONSTRAINT_URL="https://raw.githubusercontent.com/apache/airflow/constraints-${AIRFLOW_VERSION}/constraints-${PYTHON_VERSION}.txt"
    pip install "apache-airflow==${AIRFLOW_VERSION}" --constraint "${CONSTRAINT_URL}"
    ```

3.  **Initialize Airflow:**

    Set the `AIRFLOW_HOME` environment variable to the `orchestration` directory and initialize the database.

    ```bash
    export AIRFLOW_HOME=$(pwd)/orchestration
    airflow db migrate
    ```

4.  **Configure Airflow:**

    In `orchestration/airflow.cfg`, it's recommended to disable the example DAGs:

    ```ini
    load_examples = False
    ```

## Running the Orchestration

To run the data orchestration, you need to start the Airflow scheduler, webserver, and DAG processor.

1.  **Start the Airflow Services:**

    Open three separate terminals and run the following commands in each:

    *   **Terminal 1: Scheduler**
        ```bash
        export AIRFLOW_HOME=$(pwd)/orchestration
        airflow scheduler
        ```

    *   **Terminal 2: Webserver**
        ```bash
        export AIRFLOW_HOME=$(pwd)/orchestration
        airflow webserver
        ```

    *   **Terminal 3: DAG Processor**
        ```bash
        export AIRFLOW_HOME=$(pwd)/orchestration
        airflow dag-processor
        ```

2.  **Access the Airflow UI:**

    You can now access the Airflow UI at `http://localhost:8080`.

## Project Structure

```
etl-fashion-data-engineer/
├── orchestration/
│   ├── dags/
│   ├── logs/
│   ├── tasks/
│   ├── airflow.cfg
│   └── airflow.db
└── ...
```

## Task Flow

The ETL process is broken down into a series of tasks orchestrated by Airflow.

                     fashion_etl.py
                            │
                            ▼
                     Dag Processor
                            │
                            ▼
                    DAG Definition
                            │
            ┌───────────────┴───────────────┐
            ▼               ▼               ▼
     Extract Task   Validate Task   Transform Task
                            │
                            ▼
                      Scheduler
                            │
                            ▼
                       DAG Run #42
                            │
            ┌───────────────┴───────────────┐
            ▼               ▼               ▼
   Extract TI      Validate TI     Transform TI
            │               │               │
            ▼               ▼               ▼
      LocalExecutor   LocalExecutor   LocalExecutor
            │               │               │
            ▼               ▼               ▼
      scrape_data()   validate()    transform()

### Task Principles

-   **Airflow as Orchestrator:** Airflow is only responsible for triggering and monitoring tasks.
-   **Thin DAGs:** The DAG definitions are lightweight and focus on task dependencies.
-   **Granular and Atomic Tasks:** Each task has a single, well-defined responsibility.
-   **Artifact-based Communication:** Tasks communicate through artifacts (files), not in-memory data.

### Task Breakdown

| Task         | Input         | Output        |
|--------------|---------------|---------------|
| Extract      | Website       | artifact.path |
| Validate     | artifact.path | artifact.path |
| Transform    | artifact.path | artifact.path |
| Export CSV   | artifact.path | artifact.path |
| Upload to GS | artifact.path | status (bool) |

## Cleanup

To stop all Airflow processes and reset the environment:

```bash
pkill -f "airflow"
rm -f airflow/airflow.db
```
