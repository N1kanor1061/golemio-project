import subprocess

from prefect import flow, get_run_logger, task
from fetch import fetch_air_quality, save_raw


@task(retries=2, retry_delay_seconds=10)
def fetch_task():
    logger = get_run_logger()
    logger.info("Fetching air quality data from Golemio API")
    data = fetch_air_quality()
    save_raw(data)
    n = len(data["features"])
    logger.info(f"Fetched and saved {n} stations")
    return n


@task(retries=2, retry_delay_seconds=30)
def dbt_run_task():
    logger = get_run_logger()
    logger.info("Running dbt run")
    result = subprocess.run(["dbt", "run"], cwd="air_quality", capture_output=True, text=True)
    logger.info(result.stdout)
    if result.returncode != 0:
        logger.error(f"dbt run failed:\n{result.stderr}")
        raise RuntimeError("dbt run failed:\n" + result.stderr)
    logger.info("dbt run completed successfully")


@task(retries=1, retry_delay_seconds=30)
def dbt_test_task():
    logger = get_run_logger()
    logger.info("Running dbt test")
    result = subprocess.run(["dbt", "test"], cwd="air_quality", capture_output=True, text=True)
    logger.info(result.stdout)
    if result.returncode != 0:
        logger.warning(f"dbt test found data quality issues:\n{result.stderr}")
        raise RuntimeError("dbt test failed:\n" + result.stderr)
    logger.info("dbt test completed successfully")


@flow(name="golemio-air-quality-pipeline")
def air_quality_pipeline():
    logger = get_run_logger()
    logger.info("Starting Golemio air quality pipeline")
    n = fetch_task()
    logger.info(f"Получено станций: {n}")
    dbt_run_task()
    dbt_test_task()
    logger.info("Pipeline finished successfully")


if __name__ == "__main__":
    air_quality_pipeline()