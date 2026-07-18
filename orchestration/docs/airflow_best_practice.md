# Apache Airflow Best Practices for Data Engineers

This document outlines key best practices for designing, building, and maintaining robust and scalable data pipelines with Apache Airflow. Adhering to these principles will lead to more reliable, efficient, and maintainable workflows.

---

### 🏗️ 1. DAG Design & Coding Patterns

**a. Ensure Idempotency**
- **Principle:** A DAG run, when executed multiple times with the same parameters, must produce the exact same result.
- **Implementation:** When writing data, always use an "upsert" (update/insert) or "overwrite" strategy for your data partitions instead of simple appends. This prevents data duplication if a task is re-run.

**b. Avoid Top-Level Python Code**
- **Principle:** Keep DAG files lean and fast to parse. The Airflow Scheduler executes the code in your DAG files frequently to update the DAG's structure.
- **Implementation:** Heavy computations, API calls, or database connections should be placed within the `execute` method of an operator. Any code outside of an operator (at the top level of your script) will slow down the scheduler and increase CPU load.

**c. Keep Tasks Atomic and Granular**
- **Principle:** Each task should perform a single, well-defined unit of work.
- **Implementation:** Break down complex workflows into smaller tasks (e.g., `extract_data`, `transform_data`, `load_data`). This improves modularity, simplifies debugging, and allows for targeted retries of failed components without re-running the entire pipeline.

---

### 💾 2. Data & Communication Management

**a. Limit XCom Usage for Small Metadata**
- **Principle:** XComs (Cross-Communications) are designed for passing small amounts of metadata, not large datasets.
- **Implementation:** Use XComs to share information like execution IDs, file paths, configuration details, or status flags. Avoid passing large objects like Pandas DataFrames or extensive JSON payloads.

**b. Offload Large Data to External Storage**
- **Principle:** For passing large datasets between tasks, use a dedicated storage layer.
- **Implementation:** A standard pattern is for an upstream task to write its output (e.g., a CSV or Parquet file) to an external object store like **AWS S3** or **Google Cloud Storage (GCS)**. The task then passes the file's URI (e.g., `s3://my-bucket/data/file.parquet`) via XCom to downstream tasks, which can then read the data from that location.

---

### 🔒 3. Security & Resource Management

**a. Never Hardcode Credentials**
- **Principle:** Keep sensitive information out of your DAG files and source code.
- **Implementation:** Store all secrets—passwords, API keys, and connection strings—in a secure backend. Use Airflow's built-in **Connections** and **Variables**, or integrate with a dedicated secrets manager like **HashiCorp Vault** or **AWS Secrets Manager**.

**b. Disable `catchup` by Default**
- **Principle:** Prevent unintended mass execution of historical DAG runs.
- **Implementation:** Set `catchup=False` in your DAG definition. Only enable it (`catchup=True`) when you have a specific need to backfill historical data. This avoids overwhelming your system and external APIs when a DAG is first deployed or un-paused.

**c. Use Pools for Rate Limiting**
- **Principle:** Protect external systems (like databases or APIs) from being overloaded by concurrent tasks.
- **Implementation:** Define **Airflow Pools** to limit the number of tasks that can run simultaneously against a specific resource. For example, create a pool for a rate-limited API with a small number of slots to ensure your pipeline doesn't exceed its usage quota.

---

### ⚙️ 4. Production Operations & Optimization

**a. Set Sensible Task Retries**
- **Principle:** Build resilience against transient (temporary) failures.
- **Implementation:** Configure `retries` and `retry_delay` in your `default_args`. This allows tasks to automatically recover from temporary issues like network glitches or brief resource unavailability without manual intervention.

**b. Optimize Your Sensor Strategy**
- **Principle:** Use sensor resources efficiently, especially for long-running waits.
- **Implementation:** For sensors that need to wait for an extended period (minutes to hours), set the `mode` to `reschedule`. This frees up the worker slot while waiting, allowing other tasks to run. The default `poke` mode should be reserved for short waits, as it occupies a worker slot for the entire duration.

**c. Enforce Version Control and CI/CD**
- **Principle:** Treat your DAGs as code and manage them with software engineering discipline.
- **Implementation:** Store all DAGs in a **Git repository**. Implement a **CI/CD pipeline** that automatically runs tests (e.g., syntax checks, import validation) and deploys valid DAGs to your production environment. This ensures that only tested, high-quality code reaches production.

---

### 📂 5. Project Structure for Orchestration

**Principle: Separate Orchestration from Core Logic**

The folder structure below is a blueprint for a dedicated **Airflow orchestration project**. It is a critical best practice to keep your core business logic (e.g., complex data transformations, machine learning models) in a **separate repository**.

Your Airflow project should only be responsible for **orchestrating** these tasks, not executing the complex logic itself. This separation keeps your Airflow environment lean, scalable, and easy to maintain.

A robust and production-ready folder structure for your Airflow project is defined below:

```
airflow-project/
├── dags/                     # Executable DAG files ONLY (thin orchestrators)
│   ├── ingestion/            # Group by domain, project, or team
│   │   └── load_crm_daily.py # Naming: {domain}_{entity}_{frequency}.py
│   ├── transformation/
│   └── .airflowignore        # Files/directories for the Scheduler to skip
├── include/                  # Non-DAG business logic & static resources
│   ├── sql/                  # Raw SQL queries loaded dynamically by tasks
│   ├── scripts/              # Helper bash/Python scripts called by tasks
│   └── schemas/              # Data contract/schema definitions
├── plugins/                  # Custom Airflow components (Operators, Hooks)
│   └── custom_operators/
├── tests/                    # Unit and integration tests for DAGs and plugins
├── requirements.txt          # Python dependencies for the Airflow environment
└── packages.txt              # OS-level packages (if applicable)
```

**Key Takeaways:**
- **Keep the `dags/` folder clean:** It should only contain Python files that define DAGs. The Airflow scheduler scans this folder frequently, so any heavy or non-DAG code here will slow it down.
- **Use `include/` for assets:** Store static files like SQL queries or helper scripts here. Your DAG tasks will read or execute these files.
- **Treat DAGs as "Thin Orchestrators":** Your DAG files should act like configuration. Their job is to define the workflow, set dependencies, and delegate the actual work to operators. The heavy lifting should be done by external systems, which can be triggered by operators like `DockerOperator`, `KubernetesPodOperator`, or `SparkSubmitOperator`.

---

### 🪵 6. Logging Best Practices: Keep it Simple and Separate

The goal of logging in your business logic is to provide clarity on what your code is doing, not to replicate Airflow's complex orchestration logs. The best approach is to keep your logging **simple, independent, and easy to debug**.

**a. Keep Business Logic Logs Separate from Airflow**

-   **Airflow's Job:** Airflow is excellent at logging the *orchestration* layer: when a task starts, stops, fails, or retries. Let Airflow handle this.
-   **Your Job:** Your business logic (e.g., a data transformation script) should only log what's relevant to its own execution: how many records were processed, what decisions were made, or what specific error occurred. Your script should have **no awareness** it's being run by Airflow. This clean separation is the key to simplicity and maintainability.

**b. Make Your Logs More Useful with Minimal Effort**

These practices are not about adding complexity. They are simple techniques to make your independent logs far more powerful for debugging.

-   **Use Structured Logging (e.g., JSON):**
    -   **Why:** It makes your logs instantly searchable and filterable in modern logging tools (Splunk, Datadog, etc.). This is much simpler than trying to parse plain text.
    -   **How:** Instead of `logging.info("Processing done")`, log a simple dictionary: `logging.info({"message": "Processing done", "records_processed": 100})`. The code change is tiny, but the benefit for debugging is huge.

-   **Add a Correlation ID for Easy Debugging:**
    -   **Why:** When an error happens in your business logic, you need to find the exact Airflow task that ran it. A correlation ID makes this trivial.
    -   **How:** Simply pass Airflow's `run_id` from the task context into your script. Including this ID in your logs creates a simple, powerful link between two separate systems without mixing their concerns.

    ```python
    # In your DAG: Pass the context
    def my_python_callable(**context):
        # This is the only "link" you need.
        correlation_id = context["run_id"]
        # Pass it to your independent script.
        my_business_logic(correlation_id=correlation_id)

    # In your business logic script (completely separate from Airflow):
    def my_business_logic(correlation_id):
        # Use the standard Python logger.
        import logging
        logging.info({
            "message": "Something happened in the business logic",
            "correlation_id": correlation_id # Now you can trace it back!
        })
    ```

This approach ensures your business logic remains clean and testable on its own, while still giving you the end-to-end traceability needed in a production environment.
