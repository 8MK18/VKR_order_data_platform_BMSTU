import json
import os
from pathlib import Path

import joblib
import mlflow
import mlflow.sklearn
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, f1_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

from src.db import get_conn

# Параметры модели
RANDOM_STATE = 42
TEST_SIZE = 0.2
N_ESTIMATORS = 250
MAX_DEPTH = 10
MODEL_NAME = "order_status_model"
EXPERIMENT_NAME = "order_status_classification"

QUERY = """
SELECT order_id, total_amount, delivery_days, quantity,
       customer_segment, payment_method, channel, category, web_rating, order_status
FROM mart.v_order_dashboard
"""

print("=" * 60)
print("ОБУЧЕНИЕ МОДЕЛИ КЛАССИФИКАЦИИ СТАТУСА ЗАКАЗА")
print("=" * 60)

# 1. Загрузка данных из витрины
print("\n[1/6] Загрузка обучающей выборки из mart.v_order_dashboard...")
with get_conn() as conn:
    df = pd.read_sql(QUERY, conn)

if df.empty:
    raise RuntimeError("Обучающая выборка пуста")

print(f"      Загружено строк: {len(df)}")

# 2. Подготовка признаков
print("\n[2/6] Подготовка признаков...")
features = [
    "total_amount", "delivery_days", "quantity", "customer_segment",
    "payment_method", "channel", "category", "web_rating",
]
X = df[features].copy()

X["delivery_days"] = X["delivery_days"].astype("float64")
X["quantity"] = X["quantity"].astype("float64")

y = df["order_status"]

cat = ["customer_segment", "payment_method", "channel", "category"]
num = ["total_amount", "delivery_days", "quantity", "web_rating"]
print(f"      Числовых признаков:     {len(num)}")
print(f"      Категориальных:         {len(cat)}")
print(f"      Целевая переменная:     order_status")

# 3. Сборка модели
print("\n[3/6] Сборка пайплайна (OneHotEncoder + RandomForest)...")
pre = ColumnTransformer([
    ("cat", OneHotEncoder(handle_unknown="ignore"), cat),
    ("num", "passthrough", num),
])

model = Pipeline([
    ("preprocess", pre),
    ("classifier", RandomForestClassifier(
        n_estimators=N_ESTIMATORS,
        max_depth=MAX_DEPTH,
        random_state=RANDOM_STATE,
        class_weight="balanced",
    )),
])
print(f"      Алгоритм:               RandomForestClassifier")
print(f"      n_estimators:           {N_ESTIMATORS}")
print(f"      max_depth:              {MAX_DEPTH}")

# 4. Разбиение на train/test
print("\n[4/6] Разбиение выборки...")
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=TEST_SIZE, random_state=RANDOM_STATE, stratify=y
)
print(f"      Обучающая выборка:      {len(X_train)} строк")
print(f"      Тестовая выборка:       {len(X_test)} строк")

# 5. Обучение + логирование
tracking_uri = os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000")
mlflow.set_tracking_uri(tracking_uri)
mlflow.set_experiment(EXPERIMENT_NAME)

Path("models").mkdir(exist_ok=True)

print("\n[5/6] Обучение модели и логирование в MLflow...")
print(f"      MLflow Tracking URI:    {tracking_uri}")
print(f"      Experiment:             {EXPERIMENT_NAME}")

with mlflow.start_run() as run:
    model.fit(X_train, y_train)
    pred = model.predict(X_test)

    acc = accuracy_score(y_test, pred)
    f1 = f1_score(y_test, pred, average="weighted")
    report = classification_report(y_test, pred, output_dict=True)

    # Параметры и метрики в MLflow
    mlflow.log_params({
        "algorithm": "RandomForestClassifier",
        "n_estimators": N_ESTIMATORS,
        "max_depth": MAX_DEPTH,
        "test_size": TEST_SIZE,
        "random_state": RANDOM_STATE,
        "feature_count": len(features),
    })
    mlflow.log_metrics({"accuracy": acc, "f1_weighted": f1})

    # Локальные артефакты
    model_path = Path("models/order_status_model.joblib")
    joblib.dump(model, model_path)

    test_index_path = Path("models/test_index.json")
    test_index_path.write_text(
        json.dumps({"order_ids": df.loc[X_test.index, "order_id"].tolist()}, ensure_ascii=False),
        encoding="utf-8",
    )

    metrics_path = Path("models/metrics.json")
    metrics_path.write_text(json.dumps({
        "run_id": run.info.run_id,
        "accuracy": acc,
        "f1_weighted": f1,
        "test_size": TEST_SIZE,
        "train_rows": len(X_train),
        "test_rows": len(X_test),
        "classification_report": report,
    }, indent=2, ensure_ascii=False), encoding="utf-8")

    # Регистрация модели в MLflow Model Registry
    model_info = mlflow.sklearn.log_model(
        sk_model=model,
        artifact_path="sklearn_model",
        registered_model_name=MODEL_NAME,
        input_example=X_train.head(3),
    )

    # Ссылка на run — prediction будет грузить модель по ней
    ref_path = Path("models/model_reference.json")
    ref_path.write_text(json.dumps({
        "run_id": run.info.run_id,
        "model_uri": f"runs:/{run.info.run_id}/sklearn_model",
        "model_name": MODEL_NAME,
        "tracking_uri": tracking_uri,
        "registered_model_version": getattr(model_info, "registered_model_version", None),
    }, indent=2), encoding="utf-8")

    mlflow.log_artifact(str(test_index_path), artifact_path="evaluation")
    mlflow.log_artifact(str(metrics_path), artifact_path="evaluation")
    mlflow.log_artifact(str(ref_path), artifact_path="model_reference")

    # 6. Итоговые метрики
    print("\n[6/6] Результаты обучения:")
    print(f"      Run ID:                 {run.info.run_id}")
    print(f"      Accuracy:               {acc:.4f}")
    print(f"      F1 weighted:            {f1:.4f}")
    print()
    print("      Отчёт по классам:")
    print(classification_report(y_test, pred, digits=4))
    print("=" * 60)
    print("ОБУЧЕНИЕ ЗАВЕРШЕНО УСПЕШНО")
    print("=" * 60)