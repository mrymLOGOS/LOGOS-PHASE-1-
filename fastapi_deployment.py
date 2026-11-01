from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import random
from datetime import datetime

app = FastAPI()
@app.get("/")
async def root():
    return {"status": "LOGOS online", "docs": "/docs"}
    
# اجازه دادن به فرانت‌اند برای ارتباط با بک‌اند
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/status")
async def get_status():
    # این همان دیتایی است که داشبورد HTML تو به دنبال آن می‌گردد
return {
        "system_id": "LOGOS-PROD-CLOUD",
        "history": [
            {
                "timestamp": datetime.now().isoformat(),
                "status": random.choice(["STABLE", "ACTIVE", "CRITICAL"]),
                "anomalies_count": random.randint(0, 5)
            }
        ]
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
    
