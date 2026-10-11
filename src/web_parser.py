import json
import os
from pathlib import Path
import requests

ROOT = Path(__file__).resolve().parents[1]

URL = os.getenv("SOURCE_API_URL", "http://localhost:8001/products")
out = ROOT / "data/web/products.json"
out.parent.mkdir(parents=True, exist_ok=True)

try:
    response = requests.get(URL, timeout=15)
    response.raise_for_status()
    data = response.json()
except Exception as exc:
    # Резервный режим позволяет демонстрировать ETL без доступности API.
    if os.getenv("ALLOW_API_FALLBACK", "true").lower() != "true":
        raise RuntimeError(f"API unavailable and fallback is disabled: {exc}") from exc
    data = [
        {
            "product_id": i,
            "product_name": f"Product {i}",
            "category": "unknown",
            "web_rating": None,
            "web_updated_at": None,
        }
        for i in range(1, 51)
    ]
    print(f"API unavailable: {exc}; fallback data generated")

with out.open("w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"Parsed {len(data)} products from {URL}")
