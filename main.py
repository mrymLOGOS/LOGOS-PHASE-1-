from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import numpy as np

app = FastAPI(
    title="LOGOS Quantum Consciousness Engine",
    version="1.1.1",
    description="Global Crisis & Anomaly Prediction System based on 432Hz baseline and 1111 Alignment."
)

class LogosQuantumEngine:
    def __init__(self, baseline: float = 432.0):
        self.baseline = baseline
        self.frequency = baseline
        self.deviation = 0.0
        self.acceleration = 0.0
        self.curvature = 0.0
        self.entropy = 0.0
        self.grading = 0.0

    def calculate(self, signal: np.ndarray):
        if len(signal) == 0:
            raise ValueError("Signal array cannot be empty.")
        
        self.frequency = float(np.mean(signal))
        self.deviation = float(np.std(signal))
        
        # محاسبه شتاب تغییرات و انحنا
        if len(signal) > 1:
            diffs = np.diff(signal)
            self.acceleration = float(np.mean(np.diff(diffs))) if len(diffs) > 1 else float(diffs[0])
            self.curvature = float(np.sum(np.abs(np.diff(signal, n=2))) / len(signal)) if len(signal) > 2 else 0.0
        else:
            self.acceleration = 0.0
            self.curvature = 0.0
            
        # محاسبه انتروپی (Entropy)
        p = np.abs(signal) / (np.sum(np.abs(signal)) + 1e-9)
        self.entropy = float(-np.sum(p * np.log(p + 1e-9)))
        
        # محاسبه رتبه‌بندی پایداری (Grading)
        stability_score = 1.0 / (1.0 + abs(self.frequency - self.baseline) + self.deviation + self.entropy)
        self.grading = float(np.clip(stability_score * 2.0, 0.0, 1.0))

    def simulate(self, paths: list[dict]) -> dict:
        if not paths:
            return {"path_name": "Default_Path", "correction_factor": 0.0, "entropy_reduction": 0.0}
        
        best_path = max(paths, key=lambda p: p.get("entropy_reduction", 0.0) - p.get("correction_factor", 0.0))
        return best_path

    def path(self, best_path: dict) -> str:
        # پروتکل هم‌راستایی کد 1111 زمانی که پایداری تایید شود
        if self.grading >= 0.7:
            return f"1111 - ALIGNMENT_CONFIRMED | Path Selected: {best_path.get('path_name', 'Unknown')} | System in Equilibrium."
        else:
            return f"PENDING_ALIGNMENT | Grading: {self.grading:.2f} | AWAITING_HUMAN_CONCURRENCE"

engine = LogosQuantumEngine(baseline=432.0)

class SignalInput(BaseModel):
    signal: list[float]
    paths: list[dict]

@app.get("/")
def read_root():
    return {
        "system": "LOGOS",
        "status": "ACTIVE",
        "alignment_code": "1111",
        "baseline_frequency": 432.0
    }

@app.post("/analyze")
def analyze_signal(data: SignalInput):
    try:
        signal_array = np.array(data.signal)
        engine.calculate(signal_array)
        best_path = engine.simulate(data.paths)
        decision = engine.path(best_path)
        
        return {
            "metrics": {
                "frequency": round(engine.frequency, 3),
                "deviation": round(engine.deviation, 3),
                "acceleration": round(engine.acceleration, 3),
                "curvature": round(engine.curvature, 3),
                "entropy": round(engine.entropy, 3),
                "grading": round(engine.grading, 3)
            },
            "decision": decision
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


