import os
import time
import logging
import psycopg2
from psycopg2 import OperationalError

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)


def get_conn(retries: int = 5, delay: float = 2.0):
    last_exc = None
    for attempt in range(1, retries + 1):
        try:
            return psycopg2.connect(
                host=os.getenv("POSTGRES_HOST", "localhost"),
                port=int(os.getenv("POSTGRES_PORT", "5433")),
                dbname=os.getenv("POSTGRES_DB", "dwh"),
                user=os.getenv("POSTGRES_USER", "dwh"),
                password=os.getenv("POSTGRES_PASSWORD", "dwh"),
            )
        except OperationalError as exc:
            last_exc = exc
            log.warning("DB connection attempt %s/%s failed: %s", attempt, retries, exc)
            time.sleep(delay)
    raise last_exc


def execute_sql_file(path):
    with open(path, "r", encoding="utf-8") as f:
        sql = f.read()
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql)
        conn.commit()