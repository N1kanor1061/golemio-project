from orchestrate import air_quality_pipeline

if __name__ == "__main__":
    air_quality_pipeline.serve(
        name="golemio-air-quality-scheduled",
        cron="0 */3 * * *",
    )