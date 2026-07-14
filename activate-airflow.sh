#!/usr/bin/env bash
# source activate-airflow.sh

source myvenv/bin/activate
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export AIRFLOW_HOME="$PROJECT_ROOT/airflow_home"
echo "VIRTUAL_ENV=$VIRTUAL_ENV"
echo "AIRFLOW_HOME=$AIRFLOW_HOME"