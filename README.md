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
- All credentials are read from environment variables (.env), never hardcoded,
  so the same code works on any machine without editing files.

## Setup

Requires: Python 3.11+ (tested with 3.11.0), Docker Desktop, a free Golemio API
token (https://api.golemio.cz).

1. Clone the repo and enter it:
   ```
   git clone https://github.com/N1kanor1061/golemio-project.git
   cd golemio-project
   ```

2. Create a virtualenv and install dependencies:
   ```
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. Copy the env template and fill it in:
   ```
   cp .env.example .env
   ```
   Open `.env` and paste your own `GOLEMIO_TOKEN`. The Postgres values can be
   left as-is - they already match `docker-compose.yml`.

4. Start Postgres:
   ```
   docker compose up -d
   ```

5. Fetch data into the raw table:
   ```
   python fetch.py
   ```

6. Set up your dbt profile (dbt always reads this from `~/.dbt/profiles.yml`,
   never from inside the project):
   ```
   mkdir -p ~/.dbt
   cp air_quality/profiles.yml.example ~/.dbt/profiles.yml
   ```
   The values in the example already match `.env` / `docker-compose.yml`, so
   no editing needed unless you changed something.

7. Run dbt models and tests:
   ```
   cd air_quality
   dbt run
   dbt test
   cd ..
   ```

8. Run the whole pipeline end-to-end through Prefect (fetch -> dbt run -> dbt test):
   ```
   python orchestrate.py
   ```

9. (Optional) Point any BI tool at the `marts` tables in Postgres to build your
   own dashboard, or just check out the live Tableau dashboard linked above.
