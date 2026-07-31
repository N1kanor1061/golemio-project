# Golemio Air Quality Pipeline

End-to-end data engineering pet-project: pulls live air quality data for Prague
from the Golemio API (https://api.golemio.cz), lands it in Postgres, models it
with dbt, orchestrates the whole thing with Prefect, and visualizes it in
Tableau.

Live dashboard: https://public.tableau.com/app/profile/anuar.baibulatov/viz/GolemioAirQualityDashboard/PragueAirQualityGolemioData

## Architecture

Golemio API -> Python (fetch.py) -> Postgres (raw JSON, jsonb)
  -> dbt staging models (parse JSON into columns)
  -> dbt marts models (dim_stations, fct_air_quality_readings) + data tests
  -> Prefect (orchestrates fetch -> dbt run -> dbt test, with retries)
  -> Tableau (dashboard)

## Stack

Python, PostgreSQL (Docker), dbt, Prefect, Tableau Public, git/GitHub.

## Why this design

- Raw JSON is landed first, then modeled with dbt (ELT) - the API schema can
  shift without needing to re-scrape, since a schema fix is just a SQL change.
- dbt tests (not_null, unique) enforce basic data quality on every run.
- Prefect wraps ingestion and transformation into one retryable, observable flow.

## Run it yourself

python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
docker compose up -d
python fetch.py
cd air_quality && dbt run && dbt test && cd ..
python orchestrate.py
