import json
import os
from pathlib import Path

import joblib
import mlflow
import mlflow.sklearn
import pandas as pd

from src.db import get_conn

MODEL_NAME = "order_status_model"
mlflow.set_tracking_uri(os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000"))

print("=" * 60)
print("ПРОГНОЗИРОВАНИЕ СТАТУСА ЗАКАЗОВ")
print("=" * 60)

# 1. Загрузка модели
print("\n[1/3] Загрузка модели...")
reference = Path("models/model_reference.json")
model = None
model_version = "local-fallback"

if reference.exists():
    ref = json.loads(reference.read_text(encoding="utf-8"))
    try:
        model = mlflow.sklearn.load_model(ref["model_uri"])
        model_version = f"mlflow-run-{ref['run_id'][:8]}"
        print(f"      Источник:               MLflow run artifact")
        print(f"      Run ID:                 {ref['run_id']}")
    except Exception as exc:
        print(f"      MLflow недоступен:      {exc}")
        print(f"      Fallback: локальный артефакт")

if model is None:
    model = joblib.load("models/order_status_model.joblib")
    print(f"      Источник: локальный файл")

# 2. Загрузка данных для прогноза
print("\n[2/3] Загрузка данных для прогноза...")
with get_conn() as conn:
    df = pd.read_sql(
        """SELECT order_id, total_amount, delivery_days, quantity,
                  customer_segment, payment_method, channel, category, web_rating
           FROM mart.v_order_dashboard""", conn
    )

if df.empty:
    raise RuntimeError("Набор данных для прогноза пуст")

print(f"      Заказов к обработке:    {len(df)}")

X = df.drop(columns=["order_id"])

# Те же типы, что и при обучении
X["delivery_days"] = X["delivery_days"].astype("float64")
X["quantity"] = X["quantity"].astype("float64")

# 3. Прогноз и запись в БД
print("\n[3/3] Расчёт прогнозов и запись в mart.order_predictions...")

pred = model.predict(X)
if hasattr(model, "predict_proba"):
    proba = model.predict_proba(X).max(axis=1)
else:
    proba = [None] * len(df)

with get_conn() as conn:
    with conn.cursor() as cur:
        cur.execute("TRUNCATE mart.order_predictions RESTART IDENTITY")

        rows = [
            (
                int(order_id),
                str(label),
                None if probability is None else float(probability),
                model_version,
            )
            for order_id, label, probability in zip(df["order_id"], pred, proba)
        ]

        from psycopg2.extras import execute_batch
        execute_batch(
            cur,
            """INSERT INTO mart.order_predictions
               (order_id, predicted_status, probability, model_version)
               VALUES (%s,%s,%s,%s)""",
            rows, page_size=1000,
        )
    conn.commit()

print(f"      Записано прогнозов:     {len(df)}")
print(f"      Версия модели:          {model_version}")
print("=" * 60)
print("ПРОГНОЗИРОВАНИЕ ЗАВЕРШЕНО УСПЕШНО")
print("=" * 60)