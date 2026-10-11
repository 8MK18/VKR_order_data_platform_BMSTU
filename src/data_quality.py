"""
Модуль контроля качества данных (DQ).
Проверяет staging и DWH на соответствие бизнес-правилам.
"""
from src.db import get_conn


CHECKS = [
    ("staging.orders_raw: not empty",
     "SELECT COUNT(*) FROM staging.orders_raw", lambda n: n > 0),
    ("staging.orders_raw: unique order_id",
     "SELECT COUNT(*) - COUNT(DISTINCT order_id) FROM staging.orders_raw",
     lambda n: n == 0),
    ("staging.orders_raw: valid status",
     """SELECT COUNT(*) FROM staging.orders_raw
        WHERE order_status NOT IN ('completed','cancelled','delayed')""",
     lambda n: n == 0),
    ("staging.orders_raw: positive quantity",
     "SELECT COUNT(*) FROM staging.orders_raw WHERE quantity <= 0",
     lambda n: n == 0),
    ("staging.orders_raw: positive price",
     "SELECT COUNT(*) FROM staging.orders_raw WHERE unit_price <= 0",
     lambda n: n == 0),
    ("staging.orders_raw: valid channel",
     "SELECT COUNT(*) FROM staging.orders_raw WHERE channel NOT IN ('web','mobile','partner')",
     lambda n: n == 0),
    ("staging.orders_raw: valid delivery days",
     "SELECT COUNT(*) FROM staging.orders_raw WHERE delivery_days <= 0",
     lambda n: n == 0),
    ("staging.web_products_raw: unique product_id",
     "SELECT COUNT(*) - COUNT(DISTINCT product_id) FROM staging.web_products_raw",
     lambda n: n == 0),
    ("staging.web_products_raw: valid rating",
     "SELECT COUNT(*) FROM staging.web_products_raw WHERE web_rating IS NOT NULL AND (web_rating < 0 OR web_rating > 5)",
     lambda n: n == 0),
    ("dwh.fact_order: not empty",
     "SELECT COUNT(*) FROM dwh.fact_order", lambda n: n > 0),
    ("dwh.fact_order: unique order_id",
     "SELECT COUNT(*) - COUNT(DISTINCT order_id) FROM dwh.fact_order",
     lambda n: n == 0),
    ("dwh.fact_order: all FK valid (date)",
     """SELECT COUNT(*) FROM dwh.fact_order f
        LEFT JOIN dwh.dim_date d ON d.date_key = f.date_key
        WHERE d.date_key IS NULL""",
     lambda n: n == 0),
    ("dwh.fact_order: all FK valid (customer)",
     """SELECT COUNT(*) FROM dwh.fact_order f
        LEFT JOIN dwh.dim_customer c ON c.customer_key = f.customer_key
        WHERE c.customer_key IS NULL""",
     lambda n: n == 0),
    ("dwh.fact_order: all FK valid (product)",
     """SELECT COUNT(*) FROM dwh.fact_order f
        LEFT JOIN dwh.dim_product p ON p.product_key = f.product_key
        WHERE p.product_key IS NULL""",
     lambda n: n == 0),
    ("dwh.fact_order: all FK valid (channel)",
     """SELECT COUNT(*) FROM dwh.fact_order f
        LEFT JOIN dwh.dim_channel ch ON ch.channel_key = f.channel_key
        WHERE ch.channel_key IS NULL""",
     lambda n: n == 0),
    ("mart.v_order_dashboard: not empty",
     "SELECT COUNT(*) FROM mart.v_order_dashboard", lambda n: n > 0),
]


def run_checks(verbose: bool = True) -> bool:
    ok = True
    with get_conn() as conn:
        with conn.cursor() as cur:
            for name, sql, condition in CHECKS:
                cur.execute(sql)
                value = cur.fetchone()[0]
                passed = condition(value)
                if verbose:
                    status = "OK" if passed else "FAIL"
                    print(f"[{status}] {name}: {value}")
                ok = ok and passed
    if not ok:
        raise RuntimeError("Data quality checks failed")
    return ok


if __name__ == "__main__":
    run_checks()