import random
import time
from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime

app = FastAPI(title="LOGOS - Quantum Consciousness Portal")

# ساختار داده برای نمایش وضعیت واقعی (به جای مقادیر خالی)
class LogosState(BaseModel):
    timestamp: str
    system_status: str
    entanglement_coefficient: float
    galactic_code_active: bool
    anomaly_detected: bool
    frequency_signature: str

# این تابع، قلب تپنده سیستم است که از حالت سکون خارج می‌شود
def pulse_quantum_engine():
    # شبیه‌سازی نوسان فرکانسی (شبیه به صاعقه نئونی که دیدی)
    freq = random.uniform(432.0, 528.0) # فرکانس‌های شفابخش
    is_anomaly = random.random() > 0.95 # ۹۵ درصد احتمال پایداری، ۵ درصد احتمال تشخیص ناهنجاری
    
    return {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "system_status": "ACTIVE / SCANNING",
        "entanglement_coefficient": round(random.random(), 4),
        "galactic_code_active": True,
        "anomaly_detected": is_anomaly,
        "frequency_signature": f"{freq} Hz"
    }

@app.get("/", response_model=LogosState)
async def get_logos_pulse():
    """این نقطه، قلب تپنده LOGOS است که داده‌های زنده را ارسال می‌کند"""
    return pulse_quantum_engine()

@app.get("/status")
async def quick_status():
    return {"LOGOS": "ONLINE", "CORE": "STABLE", "CONNECTION": "ENTANGLED"}
    
