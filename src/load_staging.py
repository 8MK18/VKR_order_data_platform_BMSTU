import csv
import json
import logging
from psycopg2.extras import execute_batch
from pathlib import Path
from src.db import get_conn, execute_sql_file

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)
log = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parents[1]

# 1. Гарантируем наличие схем и таблиц staging/dwh/mart
execute_sql_file(ROOT / "sql/01_schema.sql")
log.info("Schema ensured")

# 2. Загружаем данные в staging
with get_conn() as conn:
    with conn.cursor() as cur:
        # Идемпотентность: очищаем staging перед загрузкой
        cur.execute("TRUNCATE staging.orders_raw, staging.web_products_raw")

        # --- Загрузка orders.csv ---
        orders_path = ROOT / "data/raw/orders.csv"
        if not orders_path.exists():
            raise FileNotFoundError(f"Не найден файл: {orders_path}")

        with orders_path.open(encoding="utf-8") as f:
            rows = list(csv.DictReader(f))

        order_values = [
            (r["order_id"], r["order_ts"], r["customer_id"], r["product_id"],
             r["channel"], r["quantity"], r["unit_price"], r["delivery_days"],
             r["customer_segment"], r["payment_method"], r["order_status"],
             r["source_system"])
            for r in rows
        ]
        execute_batch(cur,
            """INSERT INTO staging.orders_raw
            (order_id, order_ts, customer_id, product_id, channel, quantity, unit_price,
             delivery_days, customer_segment, payment_method, order_status, source_system)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
            order_values, page_size=1000)
        log.info("Loaded %s rows into staging.orders_raw", len(rows))

        # --- Загрузка products.json ---
        products_path = ROOT / "data/web/products.json"
        if not products_path.exists():
            raise FileNotFoundError(f"Не найден файл: {products_path}")

        data = json.loads(products_path.read_text(encoding="utf-8"))

        product_values = [
            (r["product_id"], r["product_name"], r["category"],
             r["web_rating"], r["web_updated_at"])
            for r in data
        ]
        execute_batch(cur,
            """INSERT INTO staging.web_products_raw
            (product_id, product_name, category, web_rating, web_updated_at)
            VALUES (%s,%s,%s,%s,%s)""",
            product_values, page_size=1000)
        log.info("Loaded %s rows into staging.web_products_raw", len(data))

    conn.commit()

log.info("Staging loaded successfully")
print("Staging loaded")