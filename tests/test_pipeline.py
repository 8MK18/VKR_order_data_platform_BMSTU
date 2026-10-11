import subprocess
from pathlib import Path
import pytest


def test_dag_importable():
    result = subprocess.run(
        ["python", "-c", "from dags.orders_end_to_end import dag; print(dag.dag_id)"],
        capture_output=True, text=True,
    )
    if "ModuleNotFoundError" in result.stderr:
        pytest.skip("Airflow not installed locally")
    assert "orders_end_to_end" in result.stdout


def test_dwh_view_columns():
    sql = Path("sql/01_schema.sql").read_text(encoding="utf-8")
    for col in ["quantity", "payment_method", "customer_segment",
                "channel", "category", "web_rating", "order_status"]:
        assert col in sql, f"Колонка {col} отсутствует в v_order_dashboard"


def test_roles_sql_exists():
    assert Path("sql/03_roles.sql").exists()


def test_data_quality_module_exists():
    assert Path("src/data_quality.py").exists()


def test_generate_sources_creates_csv(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "data/raw").mkdir(parents=True, exist_ok=True)
    subprocess.run(["python", "-m", "src.generate_sources"], check=True,
                   cwd=Path(__file__).resolve().parents[1])
    csv_path = Path(__file__).resolve().parents[1] / "data/raw/orders.csv"
    assert csv_path.exists()
    lines = csv_path.read_text(encoding="utf-8").splitlines()
    assert len(lines) > 1
    header = lines[0].split(",")
    assert "order_id" in header and "order_status" in header