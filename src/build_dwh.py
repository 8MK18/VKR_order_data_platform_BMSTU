from datetime import date
from src.db import get_conn

with get_conn() as conn:
    with conn.cursor() as cur:
        cur.execute("TRUNCATE dwh.fact_order, dwh.dim_channel, dwh.dim_product, dwh.dim_customer, dwh.dim_date RESTART IDENTITY CASCADE")

        cur.execute("""
        INSERT INTO dwh.dim_date(date_key, full_date, year, quarter, month, week, day)
        SELECT DISTINCT
            TO_CHAR(order_ts::date, 'YYYYMMDD')::int,
            order_ts::date,
            EXTRACT(YEAR FROM order_ts)::int,
            EXTRACT(QUARTER FROM order_ts)::int,
            EXTRACT(MONTH FROM order_ts)::int,
            EXTRACT(WEEK FROM order_ts)::int,
            EXTRACT(DAY FROM order_ts)::int
        FROM staging.orders_raw
        """)

        cur.execute("""
        INSERT INTO dwh.dim_customer(customer_id, customer_segment)
        SELECT customer_id, MAX(customer_segment)
        FROM staging.orders_raw GROUP BY customer_id
        """)

        cur.execute("""
        INSERT INTO dwh.dim_product(product_id, product_name, category, web_rating)
        SELECT w.product_id, w.product_name, w.category, w.web_rating
        FROM staging.web_products_raw w
        """)

        cur.execute("""
        INSERT INTO dwh.dim_channel(channel)
        SELECT DISTINCT channel FROM staging.orders_raw
        """)

        cur.execute("""
        INSERT INTO dwh.fact_order(
            order_id, date_key, customer_key, product_key, channel_key,
            quantity, unit_price, total_amount, delivery_days,
            customer_segment, payment_method, order_status, source_system
        )
        SELECT
            o.order_id,
            TO_CHAR(o.order_ts::date, 'YYYYMMDD')::int,
            c.customer_key,
            p.product_key,
            ch.channel_key,
            o.quantity,
            o.unit_price,
            o.quantity * o.unit_price,
            o.delivery_days,
            o.customer_segment,
            o.payment_method,
            o.order_status,
            o.source_system
        FROM staging.orders_raw o
        JOIN dwh.dim_customer c ON c.customer_id = o.customer_id
        JOIN dwh.dim_product p ON p.product_id = o.product_id
        JOIN dwh.dim_channel ch ON ch.channel = o.channel
        """)
    conn.commit()

print("DWH built")
