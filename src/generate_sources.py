import csv
import random
import os
from datetime import datetime, timedelta
from pathlib import Path

random.seed(42)
out = Path("data/raw/orders.csv")
out.parent.mkdir(parents=True, exist_ok=True)

segments = ["mass", "premium", "business"]
channels = ["web", "mobile", "partner"]
payments = ["card", "sbp", "invoice"]
statuses = ["completed", "cancelled", "delayed"]

with out.open("w", newline="", encoding="utf-8") as f:
    fields = [
        "order_id","order_ts","customer_id","product_id","channel",
        "quantity","unit_price","delivery_days","customer_segment",
        "payment_method","order_status","source_system"
    ]
    w = csv.DictWriter(f, fieldnames=fields)
    w.writeheader()
    start = datetime(2025, 1, 1)

    orders_count = int(os.getenv("ORDERS_COUNT", "2000"))

    for i in range(1, orders_count + 1):
        qty = random.randint(1, 5)
        price = random.choice([490, 790, 990, 1490, 2490, 3990, 6990])
        delivery = random.randint(1, 10)
        segment = random.choice(segments)
        channel = random.choice(channels)

        if delivery >= 8:
            status = "delayed"
        elif channel == "partner" and segment == "mass" and random.random() < 0.28:
            status = "cancelled"
        elif random.random() < 0.10:
            status = "cancelled"
        else:
            status = "completed"

        dt = start + timedelta(
            days=random.randint(0, 364),
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59),
        )
        w.writerow({
            "order_id": i,
            "order_ts": dt.isoformat(sep=" "),
            "customer_id": random.randint(1, 300),
            "product_id": random.randint(1, 50),
            "channel": channel,
            "quantity": qty,
            "unit_price": price,
            "delivery_days": delivery,
            "customer_segment": segment,
            "payment_method": random.choice(payments),
            "order_status": status,
            "source_system": "orders_csv",
        })

print(f"Created {out} with {orders_count} orders")
