#!/usr/bin/env bash
# source activate-dags.sh

source myvenv/bin/activate
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export AIRFLOW_HOME="$PROJECT_ROOT/orchestration"
export PYTHONPATH=$PROJECT_ROOT
echo "VIRTUAL_ENV=$VIRTUAL_ENV"
echo "AIRFLOW_HOME=$AIRFLOW_HOME"