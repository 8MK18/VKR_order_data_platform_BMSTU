from fastapi import FastAPI
from datetime import datetime
import random

app = FastAPI(title="Order Products Source API")
random.seed(42)

@app.get("/products")
def products():
    categories = ["electronics", "home", "office", "sport", "accessories"]
    return [
        {
            "product_id": i,
            "product_name": f"Product {i}",
            "category": categories[(i - 1) % len(categories)],
            "web_rating": round(random.uniform(3.2, 5.0), 2),
            "web_updated_at": datetime.utcnow().isoformat(),
        }
        for i in range(1, 51)
    ]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
