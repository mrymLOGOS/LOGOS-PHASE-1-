from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import math
import random

app = FastAPI(title="LOGOS v2 - Sacred Geometry & Monte Carlo")

BASE_FREQUENCY = 432.0
GOLDEN_RATIO = 1.61803398875

class SystemState(BaseModel):
    frequency: float = BASE_FREQUENCY
    deviation: float = 0.1
    acceleration: float = 0.02
    curvature: float = GOLDEN_RATIO
    entropy: float = 0.02

@app.get("/", response_class=HTMLResponse)
def dashboard():
    return """
    <!DOCTYPE html>
    <html lang="fa" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>LOGOS v2</title>
        <style>
            body { background:#05050a; color:#00ffcc; font-family:Tahoma,sans-serif; text-align:center; margin:0; padding:15px; }
            h1 { color:#ffd700; font-size:20px; text-shadow:0 0 10px rgba(255,215,0,.6); }
            .box { max-width:760px; margin:auto; background:rgba(10,15,30,.85); border:2px solid #00ffcc; border-radius:15px; padding:15px; box-shadow:0 0 25px rgba(0,255,204,.35); }
            canvas { background:#000; border-radius:10px; margin-top:12px; width:100%; max-width:500px; height:auto; }
            .status { font-size:16px; margin:12px 0; font-weight:bold; }
            .ok { color:#00ff66; text-shadow:0 0 10px #00ff66; }
            .wait { color:#ff3366; text-shadow:0 0 10px #ff3366; }
            .ver { color:#888; font-size:12px; }
        </style>
    </head>
    <body>
      <div class="box">
        <h1>LOGOS v2 — هندسه مقدس و ارتعاش ۴۳۲Hz</h1>
        <p class="ver">معمار آگاهی: مریم | موتور مونت‌کارلو فعال</p>
        <div id="st" class="status wait">در حال محاسبه...</div>
        <canvas id="cv" width="500" height="500"></canvas>
      </div>
      <script>
        const cv=document.getElementById('cv'), ctx=cv.getContext('2d');
        let ang=0;
        function draw(g, ok){
          ctx.clearRect(0,0,500,500);
          ctx.save(); ctx.translate(250,250);
          const petals=12, r=170*Math.max(g,.15);
          for(let i=0;i<petals;i++){
            const th=i*2*Math.PI/petals+ang;
            ctx.beginPath();
            ctx.arc(Math.cos(th)*r, Math.sin(th)*r, 85*Math.max(g,.15), 0, 2*Math.PI);
            ctx.strokeStyle = ok ? "#00ffcc" : "#ff3366";
            ctx.lineWidth = ok ? 2.6 : 1.4;
            ctx.stroke();
          }
          ctx.restore(); ang+=0.015;
        }
        async function tick(){
          try{
            const r=await fetch('/logos/analyze',{method:'POST',headers:{'Content-Type':'application/json'},
              body:JSON.stringify({frequency:432.0,deviation:0.1,acceleration:0.02,curvature:1.618,entropy:0.02})});
            const d=await r.json();
            const ok=d.alignment_status.includes('1111');
            const el=document.getElementById('st');
            el.textContent='وضعیت: '+d.alignment_status+' | امتیاز: '+d.grading;
            el.className='status '+(ok?'ok':'wait');
            draw(d.grading, ok);
          }catch(e){ console.error(e); }
        }
        setInterval(tick,1800); tick();
      </script>
    </body>
    </html>
    """

@app.post("/logos/analyze")
def analyze(state: SystemState):
    samples=[random.gauss(0.86,0.04) for _ in range(200)]
    mc=sum(samples)/len(samples)
    harmonic=math.sin(state.deviation*math.pi/180.0)*math.cos(state.curvature/GOLDEN_RATIO)
    resonance=abs(harmonic*(state.frequency/BASE_FREQUENCY))+mc
    grading=round(min(max(resonance*0.5+0.5*(1.0-state.entropy),0.0),1.0),4)
    status="1111 - ALIGNMENT_CONFIRMED" if grading>=0.7 else "AWAITING_HUMAN_CONCURRENCE"
    return {"grading":grading,"sacred_resonance":round(resonance,4),"alignment_status":status}
  
