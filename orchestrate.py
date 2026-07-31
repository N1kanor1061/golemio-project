import subprocess
from prefect import flow, task
from fetch import fetch_air_quality, save_raw


@task(retries=2, retry_delay_seconds=10)
def fetch_task():
    data = fetch_air_quality()
    save_raw(data)
    return len(data["features"])


@task
def dbt_run_task():
    result = subprocess.run(["dbt", "run"], cwd="air_quality", capture_output=True, text=True)
    print(result.stdout)
    if result.returncode != 0:
        raise RuntimeError("dbt run failed:\n" + result.stderr)


@task
def dbt_test_task():
    result = subprocess.run(["dbt", "test"], cwd="air_quality", capture_output=True, text=True)
    print(result.stdout)
    if result.returncode != 0:
        raise RuntimeError("dbt test failed:\n" + result.stderr)


@flow(name="golemio-air-quality-pipeline")
def air_quality_pipeline():
    n = fetch_task()
    print(f"Получено станций: {n}")
    dbt_run_task()
    dbt_test_task()


if __name__ == "__main__":
    air_quality_pipeline()