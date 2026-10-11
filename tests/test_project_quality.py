import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_source_data_volume_and_schema():
    path = ROOT / "data/raw/orders.csv"
    rows = list(csv.DictReader(path.open(encoding="utf-8")))
    assert len(rows) >= 2000
    required = {"order_id", "customer_id", "product_id", "channel", "quantity", "unit_price", "delivery_days", "order_status"}
    assert required.issubset(rows[0])
    assert len({r["order_id"] for r in rows}) == len(rows)


def test_product_source_contract():
    data = json.loads((ROOT / "data/web/products.json").read_text(encoding="utf-8"))
    assert len(data) == 50
    assert {"product_id", "product_name", "category", "web_rating"}.issubset(data[0])
    assert len({x["product_id"] for x in data}) == len(data)


def test_sql_has_star_schema_and_mart():
    sql = (ROOT / "sql/01_schema.sql").read_text(encoding="utf-8")
    for token in ["dwh.fact_order", "dwh.dim_date", "dwh.dim_customer", "dwh.dim_product", "dwh.dim_channel", "mart.order_predictions", "mart.v_order_dashboard"]:
        assert token in sql
    assert sql.count("REFERENCES dwh.") >= 4


def test_pipeline_order_is_complete():
    dag = (ROOT / "dags/orders_end_to_end.py").read_text(encoding="utf-8")
    expected = ["generate_sources", "web_parsing", "load_staging", "build_dwh", "data_quality", "train_model", "predict"]
    positions = [dag.index(x) for x in expected]
    assert positions == sorted(positions)


def test_ml_outputs_are_documented():
    assert (ROOT / "ml/train.py").exists()
    assert (ROOT / "ml/predict.py").exists()
    assert "accuracy" in (ROOT / "ml/train.py").read_text(encoding="utf-8")
    assert "f1_weighted" in (ROOT / "ml/train.py").read_text(encoding="utf-8")
