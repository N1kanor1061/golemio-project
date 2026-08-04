import os
import time

import psycopg2
import requests
from dotenv import load_dotenv
from psycopg2.extras import Json

load_dotenv()

token = os.environ["GOLEMIO_TOKEN"]
url = "https://api.golemio.cz/v2/airqualitystations"
headers = {"X-Access-Token": token}


def fetch_air_quality(retries=3):
    for attempt in range(1, retries + 1):
        try:
            response = requests.get(url, headers=headers, timeout=15)
        except requests.RequestException as e:
            print(f"Попытка {attempt}: сетевая ошибка — {e}")
            time.sleep(2)
            continue

        if response.status_code != 200:
            print(f"Попытка {attempt}: сервер вернул {response.status_code}")
            time.sleep(2)
            continue

        data = response.json()
        if "features" not in data:
            raise ValueError(f"Неожиданный формат ответа, ключи: {list(data.keys())}")

        return data

    raise RuntimeError(f"Не удалось получить данные после {retries} попыток")


def save_raw(data):
    conn = psycopg2.connect(
        host=os.environ.get("PGHOST", "localhost"),
        port=os.environ.get("PGPORT", "5432"),
        dbname=os.environ["PGDATABASE"],
        user=os.environ["PGUSER"],
        password=os.environ["PGPASSWORD"],
    )
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute("""
                    create table if not exists raw_air_quality (
                        id serial primary key,
                        fetched_at timestamptz not null default now(),
                        payload jsonb not null
                    )
                """)
                cur.execute(
                    "insert into raw_air_quality (payload) values (%s)",
                    (Json(data),),
                )
    finally:
        conn.close()


if __name__ == "__main__":
    data = fetch_air_quality()
    print(f"Получено станций: {len(data['features'])}")
    save_raw(data)
    print("Сохранено в Postgres.")