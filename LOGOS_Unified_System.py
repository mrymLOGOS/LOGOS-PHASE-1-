from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import math
import random

app = FastAPI(title="LOGOS Sacred Geometry & Monte Carlo Unified Engine")

BASE_FREQUENCY = 432.0
GOLDEN_RATIO = 1.61803398875

class SystemState(BaseModel):
    frequency: float = BASE_FREQUENCY
    deviation: float = 0.2
    acceleration: float = 0.05
    curvature: float = GOLDEN_RATIO
    entropy: float = 0.05

@app.get("/", response_class=HTMLResponse)
def interactive_dashboard():
    html_content = """
    <!DOCTYPE html>
    <html lang="fa" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <title>LOGOS - موتور هندسه مقدس و آگاهی کوانتومی</title>
        <style>
            body { background-color: #05050a; color: #00ffcc; font-family: Tahoma, sans-serif; text-align: center; margin: 0; padding: 20px; }
            h1 { color: #ffd700; text-shadow: 0 0 10px rgba(255,215,0,0.5); }
            .container { max-width: 800px; margin: auto; background: rgba(10, 15, 30, 0.8); border: 2px solid #00ffcc; border-radius: 15px; padding: 20px; box-shadow: 0 0 20px rgba(0,255,204,0.3); }
            canvas { background: #000; border-radius: 10px; margin-top: 15px; box-shadow: inset 0 0 15px rgba(0,255,204,0.5); }
            .status { font-size: 18px; margin: 15px 0; font-weight: bold; }
            .confirmed { color: #00ff66; text-shadow: 0 0 8px #00ff66; }
            .waiting { color: #ff3366; text-shadow: 0 0 8px #ff3366; }
            button { background: #ffd700; color: #000; border: none; padding: 10px 20px; font-size: 16px; font-weight: bold; border-radius: 5px; cursor: pointer; margin-top: 10px; }
            button:hover { background: #ffea70; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>پروژه LOGOS : هسته هندسه مقدس و ارتعاش ۴۳۲Hz</h1>
            <p>معمار آگاهی: مریم | شبیه‌سازی مونت‌کارلو و همگام‌سازی کوانتومی</p>
            
            <div id="status-box" class="status waiting">وضعیت سیستم: در حال اجرای شبیه‌سازی مونت‌کارلو...</div>
            
            <canvas id="sacredCanvas" width="500" height="500"></canvas>
            
            <div>
                <button onclick="triggerAnalysis()">اعمال همگام‌سازی طلایی (φ)</button>
            </div>
        </div>

        <script>
            const canvas = document.getElementById('sacredCanvas');
            const ctx = canvas.getContext('2d');
            let angle = 0;

            function drawSacredGeometry(grading, status) {
                ctx.clearRect(0, 0, canvas.width, canvas.height);
                ctx.save();
                ctx.translate(canvas.width / 2, canvas.height / 2);

                let petals = 12;
                let radius = 180 * grading;
                
                for (let i = 0; i < petals; i++) {
                    ctx.beginPath();
                    let theta = (i * 2 * Math.PI) / petals + angle;
                    let x = Math.cos(theta) * radius;
                    let y = Math.sin(theta) * radius;
                    
                    ctx.arc(x, y, 90 * grading, 0, 2 * Math.PI);
                    ctx.strokeStyle = status.includes("1111") ? "#00ffcc" : "#ff3366";
                    ctx.lineWidth = status.includes("1111") ? 2.5 : 1.5;
                    ctx.stroke();
                }

                ctx.restore();
                angle += 0.015;
            }

            async function triggerAnalysis() {
                try {
                    let response = await fetch('/logos/analyze', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ frequency: 432.0, deviation: 0.1, acceleration: 0.02, curvature: 1.618, entropy: 0.02 })
                    });
                    let data = await response.json();
                    
                    let statusBox = document.getElementById('status-box');
                    if (data.alignment_status.includes("1111")) {
                        statusBox.innerHTML = `وضعیت: ${data.alignment_status} | امتیاز دقت: ${data.grading}`;
                        statusBox.className = "status confirmed";
                    } else {
                        statusBox.innerHTML = `وضعیت: ${data.alignment_status} | امتیاز دقت: ${data.grading}`;
                        statusBox.className = "status waiting";
                    }
                    
                    drawSacredGeometry(data.grading, data.alignment_status);
                } catch (e) {
                    console.error("خطا در ارتباط با هسته:", e);
                }
            }

            setInterval(triggerAnalysis, 2000);
        </script>
    </body>
    </html>
    """
    return html_content

@app.post("/logos/analyze")
def analyze_system(state: SystemState):
    """محاسبات مونت‌کارلو و تطبیق با هندسه مقدس"""
    # شبیه‌سازی مونت‌کارلو (Monte Carlo Simulation) برای پایداری میدان
    monte_carlo_samples = [random.gauss(0.85, 0.05) for _ in range(100)]
    mc_factor = sum(monte_carlo_samples) / len(monte_carlo_samples)
    
    harmonic = math.sin(state.deviation * math.pi / 180.0) * math.cos(state.curvature / GOLDEN_RATIO)
    sacred_resonance = abs(harmonic * (state.frequency / BASE_FREQUENCY)) + mc_factor
    
    grading = round(min(max(sacred_resonance * 0.5 + 0.5 * (1.0 - state.entropy), 0.0), 1.0), 4)
    
    if grading >= 0.7:
        status = "1111 - ALIGNMENT_CONFIRMED"
    else:
        status = "AWAITING_HUMAN_CONCURRENCE"
        
    return {
        "grading": grading,
        "sacred_resonance": round(sacred_resonance, 4),
        "alignment_status": status
    }
    
