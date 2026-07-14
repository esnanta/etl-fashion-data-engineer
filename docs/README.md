# ETL Fashion Data Engineer with Airflow

This project implements an ETL (Extract, Transform, Load) pipeline for fashion data using Apache Airflow.

## Prerequisites

- Python 3.12
- A virtual environment tool (e.g., `venv`)

## Setup and Installation

1.  **Create and activate a Python virtual environment:**

    ```bash
    python3 -m venv myvenv
    source myvenv/bin/activate
    ```

2.  **Ensure `pip` is up-to-date:**

    ```bash
    python -m pip install --upgrade pip setuptools wheel
    ```

3.  **Install Apache Airflow:**

    Define the desired Airflow and Python versions.

    ```bash
    AIRFLOW_VERSION=3.2.2
    PYTHON_VERSION=3.12
    CONSTRAINT_URL="https://raw.githubusercontent.com/apache/airflow/constraints-${AIRFLOW_VERSION}/constraints-${PYTHON_VERSION}.txt"
    pip install "apache-airflow==${AIRFLOW_VERSION}" --constraint "${CONSTRAINT_URL}"
    ```

4.  **Set up Airflow Home and Database:**

    Navigate to the project root directory and set the `AIRFLOW_HOME` environment variable.

    ```bash
    export AIRFLOW_HOME=$(pwd)/airflow_home
    ```

    Create the necessary directories for DAGs and plugins:
    ```bash
    mkdir -p airflow_home/dags
    mkdir -p airflow_home/plugins
    ```

    Initialize the Airflow database. This command will create the SQLite database, run migrations, and generate the `airflow.cfg` file.

    ```bash
    airflow db migrate
    ```

5.  **Configure Airflow:**

    Open `airflow_home/airflow.cfg` and disable the example DAGs for a cleaner setup:

    ```ini
    load_examples = False
    ```

## Directory Structure

```
etl-fashion-data-engineer-airflow/
├── airflow_home/
│   ├── dags/
│   ├── logs/
│   ├── plugins/
│   ├── airflow.cfg
│   └── airflow.db
│
├── myvenv/
├── requirements.txt
├── README.md
└── .gitignore
```

## Running Airflow

1.  **Start the Airflow Scheduler:**

    Open a new terminal, activate the virtual environment, and set the `AIRFLOW_HOME` variable as before. Then, start the scheduler:

    ```bash
    source activate-airflow.sh
    airflow scheduler
    ```

2.  **Start the Airflow Webserver:**

    In another terminal, repeat the environment setup and start the webserver:

    ```bash
    source activate-airflow.sh
    airflow api-server
    ```


3.  **Start the Airflow Dag Processor:**

    In another terminal, repeat the environment setup and start the webserver:

    ```bash
    source activate-airflow.sh
    airflow dag-processor
    ```

You can now access the Airflow UI at `http://localhost:8080`.



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


pkill -f "airflow api-server"
pkill -f "airflow scheduler"
pkill -f "airflow dag-processor"
pkill -f "airflow triggerer"

rm -rf ~/airflow
rm -f airflow_home/airflow.db
rm -f airflow_home/simple_auth_manager_passwords.json.generated

source activate-airflow.sh
airflow db migrate