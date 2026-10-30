import os
import json
import numpy as np
from datetime import datetime, timezone
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List

# --- LOGOS CORE ENGINE ---
class LogosEngine:
    def __init__(self, system_id: str):
        self.system_id = system_id
        self.history = []

    def process(self, payload: dict) -> dict:
        raw_stream = payload.get("raw_stream", [0.0])
        anomalies = []
        for i, val in enumerate(raw_stream):
            if abs(np.sin(val)) > 0.8:
                anomalies.append({"index": i, "val": val, "type": "RED-CODE"})
        
        result = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "status": "CRITICAL" if anomalies else "STABLE",
            "anomalies_count": len(anomalies),
            "node": self.system_id
        }
        self.history.append(result)
        if len(self.history) > 50: self.history.pop(0)
        return result

engine = LogosEngine("LOGOS-PROD-CLOUD")
app = FastAPI(title="LOGOS Control Center")

# --- API ENDPOINTS ---
class QuantumData(BaseModel):
    raw_stream: List[float]

@app.get("/api/status")
async def get_status():
    return {
        "system_id": engine.system_id,
        "history": engine.history[-20:]
    }

@app.post("/api/process")
async def process_data(data: QuantumData):
    return engine.process({"raw_stream": data.raw_stream})

# --- DASHBOARD FRONTEND ---
@app.get("/", response_class=HTMLResponse)
async def get_dashboard():
    return """
    <!DOCTYPE html>
    <html lang="fa" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>LOGOS | Cloud Dashboard</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <style>
            body { background-color: #0a0a0c; color: #e0e0e0; font-family: sans-serif; }
            .glass { background: rgba(255, 255, 255, 0.05); backdrop-filter: blur(10px); border: 1px solid rgba(255,255,255,0.1); }
        </style>
    </head>
    <body class="p-4 md:p-8">
        <div class="max-w-7xl mx-auto">
            <div class="flex justify-between items-center mb-8">
                <h1 class="text-2xl md:text-4xl font-bold text-white">LOGOS <span class="text-blue-500">CLOUD</span></h1>
                <div id="status-badge" class="px-3 py-1 rounded-full glass text-xs">Connecting...</div>
            </div>
            <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
                <div class="glass p-4 rounded-xl"><h3 class="text-gray-400 text-xs">ID</h3><p id="sys-id" class="text-lg font-mono">---</p></div>
                <div class="glass p-4 rounded-xl"><h3 class="text-gray-400 text-xs">STATE</h3><p id="current-state" class="text-lg">---</p></div>
                <div class="glass p-4 rounded-xl"><h3 class="text-gray-400 text-xs">RED-CODES</h3><p id="red-codes" class="text-lg text-red-500">0</p></div>
            </div>
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div class="glass p-4 rounded-xl h-64"><canvas id="historyChart"></canvas></div>
                <div class="glass p-4 rounded-xl h-64 overflow-y-auto"><div id="logs" class="text-[10px] font-mono space-y-1"></div></div>
            </div>
        </div>
        <script>
            let chart;
            async function fetchData() {
                try {
                    const res = await fetch('/api/status');
                    const data = await res.json();
                    document.getElementById('sys-id').innerText = data.system_id;
                    const lastStatus = data.history.length > 0 ? data.history[data.history.length-1].status : 'STABLE';
                    document.getElementById('current-state').innerText = lastStatus;
                    document.getElementById('status-badge').innerText = lastStatus;
                    document.getElementById('red-codes').innerText = data.history.reduce((a, c) => a + c.anomalies_count, 0);
                    
                    const logs = document.getElementById('logs');
                    logs.innerHTML = data.history.reverse().map(h => `<div class="${h.status==='CRITICAL'?'text-red-400':'text-blue-400'}">[${h.timestamp.split('T')[1].split('.')[0]}] ${h.status}</div>`).join('');

                    const labels = data.history.map(h => h.timestamp.split('T')[1].split('.')[0]);
                    const counts = data.history.map(h => h.anomalies_count);
                    if (!chart) {
                        chart = new Chart(document.getElementById('historyChart'), {
                            type: 'line', data: { labels, datasets: [{ label: 'Anomalies', data: counts, borderColor: '#00d4ff', tension: 0.4 }] },
                            options: { maintainAspectRatio: false }
                        });
                    } else { chart.data.labels = labels; chart.data.datasets[0].data = counts; chart.update(); }
                } catch (e) {}
            }
            setInterval(fetchData, 3000);
            fetchData();
        </script>
    </body>
    </html>
    """


  
