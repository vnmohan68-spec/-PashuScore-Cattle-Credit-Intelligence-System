import streamlit as st
import sqlite3
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import date
from pathlib import Path

st.set_page_config(page_title="PashuScore", page_icon="🐄",
                   layout="wide", initial_sidebar_state="expanded")

# ══════════════════════════════════════════════════════════════
#  INDIAN FINTECH 3D UI — CSS
# ══════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800;900&family=Baloo+2:wght@700;800&family=JetBrains+Mono:wght@500&display=swap');

:root {
  --saffron:  #FF6B00;
  --saffron2: #FF9500;
  --green:    #138808;
  --green2:   #22c55e;
  --blue:     #1a237e;
  --blue2:    #3b82f6;
  --gold:     #FFD700;
  --pink:     #e91e8c;
  --purple:   #7c3aed;
  --bg:       #0a0a0f;
  --card:     #13131f;
  --card2:    #1a1a2e;
  --border:   #ffffff12;
  --text:     #f1f5f9;
  --muted:    #94a3b8;
}

*, *::before, *::after { box-sizing: border-box; }

html, body, [class*="css"] {
  font-family: 'Nunito', sans-serif !important;
  color: var(--text);
}

/* ── Animated mesh background ── */
.stApp {
  background-color: var(--bg);
  background-image:
    radial-gradient(ellipse 80% 60% at 20% 10%, #FF6B0018 0%, transparent 60%),
    radial-gradient(ellipse 60% 80% at 80% 90%, #13880818 0%, transparent 60%),
    radial-gradient(ellipse 50% 50% at 60% 40%, #1a237e14 0%, transparent 55%),
    radial-gradient(ellipse 40% 40% at 30% 80%, #e91e8c0e 0%, transparent 50%);
  animation: meshMove 12s ease-in-out infinite alternate;
  min-height: 100vh;
}
@keyframes meshMove {
  0%   { background-size: 100% 100%, 100% 100%, 100% 100%, 100% 100%; }
  50%  { background-size: 120% 120%, 110% 110%, 130% 130%, 115% 115%; }
  100% { background-size: 100% 100%, 100% 100%, 100% 100%, 100% 100%; }
}

.main .block-container { padding: 1.5rem 2rem 3rem 2rem !important; }

/* ── SIDEBAR ── */
[data-testid="stSidebar"] {
  background: linear-gradient(160deg, #0f0f1a 0%, #1a0a00 50%, #0a0f0a 100%) !important;
  border-right: 1px solid #FF6B0030 !important;
}

[data-testid="stSidebar"] .stRadio > div {
  gap: 4px;
}
[data-testid="stSidebar"] .stRadio label {
  font-family: 'Nunito', sans-serif !important;
  font-size: 13px !important;
  font-weight: 600 !important;
  color: #64748b !important;
  padding: 10px 14px !important;
  border-radius: 12px !important;
  border: 1px solid transparent !important;
  transition: all 0.25s cubic-bezier(0.4,0,0.2,1) !important;
  display: block !important;
  cursor: pointer !important;
}
[data-testid="stSidebar"] .stRadio label:hover {
  background: linear-gradient(135deg, #FF6B0018, #FF950010) !important;
  border-color: #FF6B0040 !important;
  color: #FF9500 !important;
  transform: translateX(4px) !important;
}

/* ── METRIC CARDS — 3D STYLE ── */
[data-testid="stMetric"] {
  border-radius: 20px !important;
  padding: 22px !important;
  position: relative !important;
  overflow: hidden !important;
  transform: perspective(1000px) rotateX(0deg) rotateY(0deg);
  transition: transform 0.4s ease, box-shadow 0.4s ease !important;
  border: 1px solid var(--border) !important;
}
[data-testid="stMetric"]:hover {
  transform: perspective(1000px) translateY(-6px) rotateX(3deg) !important;
  box-shadow: 0 20px 60px rgba(0,0,0,0.5), 0 0 0 1px #FF6B0030 !important;
}
[data-testid="stMetricValue"] {
  font-family: 'Baloo 2', sans-serif !important;
  font-size: 40px !important;
  font-weight: 800 !important;
  line-height: 1.1 !important;
}
[data-testid="stMetricLabel"] {
  font-family: 'Nunito', sans-serif !important;
  font-size: 11px !important;
  font-weight: 700 !important;
  letter-spacing: 2px !important;
  text-transform: uppercase !important;
}

/* ── BUTTONS ── */
.stButton > button {
  font-family: 'Nunito', sans-serif !important;
  font-weight: 800 !important;
  font-size: 14px !important;
  border-radius: 14px !important;
  padding: 12px 24px !important;
  letter-spacing: 0.5px !important;
  transition: all 0.3s cubic-bezier(0.4,0,0.2,1) !important;
  border: none !important;
  position: relative !important;
  overflow: hidden !important;
  background: linear-gradient(135deg, #1e1e2e, #2a2a3e) !important;
  color: #94a3b8 !important;
  border: 1px solid #ffffff15 !important;
}
.stButton > button::before {
  content: '';
  position: absolute;
  top: 0; left: -100%;
  width: 100%; height: 100%;
  background: linear-gradient(90deg, transparent, #ffffff10, transparent);
  transition: left 0.5s;
}
.stButton > button:hover::before { left: 100%; }
.stButton > button:hover {
  transform: translateY(-3px) scale(1.01) !important;
  box-shadow: 0 10px 30px rgba(0,0,0,0.4) !important;
  border-color: #FF6B0050 !important;
  color: #FF9500 !important;
}
.stButton > button[kind="primary"] {
  background: linear-gradient(135deg, #FF6B00, #FF9500, #FFB700) !important;
  color: #fff !important;
  border: none !important;
  box-shadow: 0 8px 25px #FF6B0050, 0 2px 0 #b34d00 !important;
  text-shadow: 0 1px 2px rgba(0,0,0,0.3) !important;
}
.stButton > button[kind="primary"]:hover {
  box-shadow: 0 14px 40px #FF6B0070, 0 2px 0 #b34d00 !important;
  transform: translateY(-4px) scale(1.02) !important;
  background: linear-gradient(135deg, #FF8500, #FFB500, #FFD700) !important;
}

/* ── SELECTBOX ── */
.stSelectbox > div > div {
  background: var(--card2) !important;
  border: 1px solid #ffffff15 !important;
  border-radius: 14px !important;
  color: var(--text) !important;
  font-family: 'Nunito', sans-serif !important;
  font-weight: 600 !important;
}
.stSelectbox > div > div:focus-within {
  border-color: #FF6B00 !important;
  box-shadow: 0 0 0 3px #FF6B0025 !important;
}

/* ── TEXT INPUTS ── */
.stTextInput input, .stNumberInput input, .stDateInput input {
  background: var(--card2) !important;
  border: 1px solid #ffffff15 !important;
  border-radius: 12px !important;
  color: var(--text) !important;
  font-family: 'Nunito', sans-serif !important;
  font-weight: 600 !important;
  padding: 10px 14px !important;
}
.stTextInput input:focus, .stNumberInput input:focus {
  border-color: #FF6B00 !important;
  box-shadow: 0 0 0 3px #FF6B0020 !important;
}

/* ── DATAFRAME ── */
[data-testid="stDataFrame"] {
  border-radius: 16px !important;
  overflow: hidden !important;
  border: 1px solid #ffffff10 !important;
}

/* ── TABS ── */
.stTabs [data-baseweb="tab-list"] {
  background: var(--card2) !important;
  border-radius: 16px !important;
  padding: 6px !important;
  gap: 6px !important;
  border: 1px solid #ffffff10 !important;
}
.stTabs [data-baseweb="tab"] {
  color: var(--muted) !important;
  border-radius: 10px !important;
  font-family: 'Nunito', sans-serif !important;
  font-weight: 700 !important;
  padding: 8px 16px !important;
}
.stTabs [aria-selected="true"] {
  background: linear-gradient(135deg, #FF6B00, #FF9500) !important;
  color: #fff !important;
  box-shadow: 0 4px 15px #FF6B0040 !important;
}

/* ── PROGRESS BAR ── */
.stProgress > div > div > div {
  background: linear-gradient(90deg, #FF6B00, #FF9500, #FFD700) !important;
  border-radius: 10px !important;
  animation: shimmer 2s linear infinite !important;
}
@keyframes shimmer {
  0%   { background-position: -200% center; }
  100% { background-position: 200% center; }
}

/* ── SCROLLBAR ── */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: #0a0a0f; }
::-webkit-scrollbar-thumb { background: #FF6B0060; border-radius: 5px; }
::-webkit-scrollbar-thumb:hover { background: #FF6B00; }

/* ── ALERTS ── */
[data-testid="stSuccess"] {
  background: linear-gradient(135deg, #13880815, #22c55e10) !important;
  border: 1px solid #22c55e40 !important;
  border-radius: 14px !important;
}
[data-testid="stWarning"] {
  background: linear-gradient(135deg, #FF950015, #FFD70010) !important;
  border: 1px solid #FF950040 !important;
  border-radius: 14px !important;
}
[data-testid="stError"] {
  background: linear-gradient(135deg, #ef444415, #dc262610) !important;
  border: 1px solid #ef444440 !important;
  border-radius: 14px !important;
}

/* ── FORM SUBMIT ── */
[data-testid="stFormSubmitButton"] > button {
  background: linear-gradient(135deg, #FF6B00, #FF9500, #FFB700) !important;
  color: white !important; border: none !important; font-weight: 800 !important;
  border-radius: 14px !important;
  box-shadow: 0 6px 20px #FF6B0050 !important;
}
[data-testid="stFormSubmitButton"] > button:hover {
  box-shadow: 0 10px 30px #FF6B0070 !important;
  transform: translateY(-3px) !important;
}

/* ── DIVIDER ── */
hr { border-color: #ffffff0a !important; }

/* ── MULTISELECT ── */
.stMultiSelect > div > div {
  background: var(--card2) !important;
  border: 1px solid #ffffff15 !important;
  border-radius: 14px !important;
}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
#  DB & LOGIC  (unchanged)
# ══════════════════════════════════════════════════════════════
DB_FILE = Path("pashuscore.db")
BREED_WEIGHTS = {
    "Gir": 30, "Sahiwal": 28, "Red Sindhi": 26,
    "Murrah Buffalo": 27, "Surti Buffalo": 24,
    "HF Cross": 22, "Jersey Cross": 20, "Nondescript": 10,
}
GRADE_TABLE = [
    (80, "A+", 200000, 7.0,  "#22c55e", "#14532d"),
    (65, "A",  150000, 9.0,  "#3b82f6", "#1e3a5f"),
    (50, "B",   75000, 12.0, "#FF9500", "#7c3800"),
    (35, "C",   25000, 16.0, "#f97316", "#7c2d00"),
    (0,  "D",       0,  0.0, "#ef4444", "#7f1d1d"),
]

def init_db():
    conn = sqlite3.connect(DB_FILE); cur = conn.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS farmers (
        farmer_id TEXT PRIMARY KEY, name TEXT NOT NULL, village TEXT NOT NULL,
        state TEXT NOT NULL, land_acres REAL, phone TEXT)""")
    cur.execute("""CREATE TABLE IF NOT EXISTS cattle (
        cattle_id TEXT PRIMARY KEY, farmer_id TEXT NOT NULL, breed TEXT NOT NULL,
        age_years INTEGER, health_status TEXT DEFAULT 'Healthy',
        milk_yield_lpd REAL, ear_tag TEXT,
        FOREIGN KEY (farmer_id) REFERENCES farmers(farmer_id))""")
    cur.execute("""CREATE TABLE IF NOT EXISTS vaccinations (
        vacc_id INTEGER PRIMARY KEY AUTOINCREMENT, cattle_id TEXT NOT NULL,
        vaccine TEXT, given_on TEXT, next_due TEXT, vet_name TEXT,
        FOREIGN KEY (cattle_id) REFERENCES cattle(cattle_id))""")
    cur.execute("""CREATE TABLE IF NOT EXISTS loan_applications (
        app_id INTEGER PRIMARY KEY AUTOINCREMENT, farmer_id TEXT NOT NULL,
        credit_score INTEGER, grade TEXT, amount_eligible REAL,
        status TEXT DEFAULT 'Pending', applied_on TEXT DEFAULT (DATE('now')),
        FOREIGN KEY (farmer_id) REFERENCES farmers(farmer_id))""")
    cur.execute("SELECT COUNT(*) FROM farmers")
    if cur.fetchone()[0] == 0:
        cur.executemany("INSERT INTO farmers VALUES (?,?,?,?,?,?)", [
            ('F001','Ramaiah Gowda','Hosakere','Karnataka',3.50,'9845001234'),
            ('F002','Sunita Devi','Barhaj','Uttar Pradesh',1.20,'9012002345'),
            ('F003','Murugesan P.','Palani','Tamil Nadu',0.80,'8023003456'),
            ('F004','Harpreet Kaur','Barnala','Punjab',6.00,'9779004567'),
        ])
        cur.executemany("INSERT INTO cattle VALUES (?,?,?,?,?,?,?)", [
            ('C01','F001','Gir',4,'Healthy',12.0,'KA-4821'),
            ('C02','F001','Sahiwal',6,'Healthy',10.0,'KA-4822'),
            ('C03','F001','Gir',3,'Healthy',11.0,'KA-4823'),
            ('C04','F001','HF Cross',5,'Healthy',9.0,'KA-4824'),
            ('C05','F002','Murrah Buffalo',5,'Healthy',14.0,'UP-2201'),
            ('C06','F002','Murrah Buffalo',7,'Mild Fever',6.0,'UP-2202'),
            ('C07','F002','Nondescript',8,'Healthy',4.0,'UP-2203'),
            ('C08','F003','Nondescript',10,'Limping',2.0,'TN-0901'),
            ('C09','F003','Nondescript',9,'Healthy',3.0,'TN-0902'),
            ('C10','F004','Murrah Buffalo',4,'Healthy',16.0,'PB-7731'),
            ('C11','F004','Murrah Buffalo',5,'Healthy',15.0,'PB-7732'),
            ('C12','F004','Murrah Buffalo',3,'Healthy',13.0,'PB-7733'),
            ('C13','F004','Sahiwal',4,'Healthy',10.0,'PB-7734'),
            ('C14','F004','HF Cross',6,'Healthy',9.0,'PB-7735'),
        ])
        cur.executemany("INSERT INTO vaccinations (cattle_id,vaccine,given_on,next_due,vet_name) VALUES (?,?,?,?,?)", [
            ('C01','FMD + HS','2024-01-10','2025-01-10','Dr. Nagaraj'),
            ('C02','FMD + HS','2024-01-10','2025-01-10','Dr. Nagaraj'),
            ('C03','FMD + HS','2024-01-10','2025-01-10','Dr. Nagaraj'),
            ('C04','FMD + HS','2024-01-10','2025-01-10','Dr. Nagaraj'),
            ('C05','FMD + BQ','2024-02-14','2025-02-14','Dr. Mishra'),
            ('C07','FMD','2023-06-01','2024-06-01','Dr. Mishra'),
            ('C09','FMD','2022-06-01','2023-06-01','Dr. Arumugam'),
            ('C10','FMD + HS','2024-03-20','2025-03-20','Dr. Gill'),
            ('C11','FMD + HS','2024-03-20','2025-03-20','Dr. Gill'),
            ('C12','FMD + HS','2024-03-20','2025-03-20','Dr. Gill'),
            ('C13','FMD + HS','2024-03-20','2025-03-20','Dr. Gill'),
            ('C14','FMD + HS','2024-03-20','2025-03-20','Dr. Gill'),
        ])
        cur.executemany("INSERT INTO loan_applications (farmer_id,credit_score,grade,amount_eligible,status) VALUES (?,?,?,?,?)", [
            ('F004',88,'A+',200000,'Approved'),('F001',76,'A',150000,'Pending'),
        ])
    conn.commit(); conn.close()

init_db()

def run_query(sql, params=None):
    try:
        conn = sqlite3.connect(DB_FILE)
        df = pd.read_sql_query(sql, conn, params=params or ())
        conn.close(); return df
    except Exception as e:
        st.error(f"DB Error: {e}"); return pd.DataFrame()

def execute(sql, params=None):
    try:
        conn = sqlite3.connect(DB_FILE); cur = conn.cursor()
        cur.execute(sql, params or ()); conn.commit()
        lid = cur.lastrowid; cur.close(); conn.close(); return lid
    except Exception as e:
        st.error(f"DB Error: {e}"); return None

def compute_score(farmer_id):
    df = run_query("""
        SELECT c.cattle_id, c.breed, c.age_years, c.health_status, c.milk_yield_lpd,
               CASE WHEN v.cattle_id IS NOT NULL THEN 1 ELSE 0 END AS vaccinated
        FROM cattle c
        LEFT JOIN vaccinations v ON c.cattle_id=v.cattle_id AND DATE(v.next_due)>=DATE('now')
        WHERE c.farmer_id=? AND c.health_status!='Deceased'
    """, (farmer_id,))
    if df.empty: return None
    n = len(df)
    herd_score    = min(n * 5, 20)
    breed_avg     = df["breed"].map(BREED_WEIGHTS).fillna(10).mean()
    breed_score   = round(breed_avg)
    vacc_count    = int(df["vaccinated"].sum())
    vacc_score    = round((vacc_count / n) * 25)
    healthy_count = int((df["health_status"] == "Healthy").sum())
    health_score  = round((healthy_count / n) * 15)
    high_yield    = int((df["milk_yield_lpd"] >= 8).sum())
    yield_score   = round((high_yield / n) * 10)
    total = herd_score + breed_score + vacc_score + health_score + yield_score
    grade, amount, rate, color, bg = "D", 0, 0.0, "#ef4444", "#7f1d1d"
    for threshold, g, a, r, c, b in GRADE_TABLE:
        if total >= threshold:
            grade, amount, rate, color, bg = g, a, r, c, b; break
    return {"total": total, "grade": grade, "amount": amount, "rate": rate,
            "color": color, "bg": bg, "n": n,
            "breakdown": {
                "Herd Size":     (herd_score,   20, f"{n} animals"),
                "Breed Quality": (breed_score,  30, f"Avg {breed_avg:.1f}"),
                "Vaccination":   (vacc_score,   25, f"{vacc_count}/{n} vaccinated"),
                "Health":        (health_score, 15, f"{healthy_count}/{n} healthy"),
                "Milk Yield":    (yield_score,  10, f"{high_yield} high-yield"),
            },
            "cattle_df": df}

# ── CHART HELPERS ─────────────────────────────────────────────
def gauge_chart(score, color):
    fig = go.Figure(go.Indicator(
        mode="gauge+number", value=score,
        domain={"x": [0,1], "y": [0,1]},
        gauge={
            "axis": {"range":[0,100], "tickfont":{"color":"#475569","size":10},
                     "tickcolor":"#334155", "dtick":20},
            "bar":  {"color": color, "thickness": 0.22},
            "bgcolor": "#1a1a2e",
            "bordercolor": "#ffffff10", "borderwidth": 2,
            "steps": [
                {"range":[0,35],   "color":"#1c0a0a"},
                {"range":[35,50],  "color":"#1c1200"},
                {"range":[50,65],  "color":"#001c08"},
                {"range":[65,80],  "color":"#00111c"},
                {"range":[80,100], "color":"#001c10"},
            ],
            "threshold": {"line":{"color":color,"width":4},
                          "thickness":0.9, "value":score}
        },
        number={"font":{"color":color,"size":58,"family":"Baloo 2"},
                "suffix":"/100"},
        title={"text":"CREDIT SCORE","font":{"color":"#64748b","size":12,"family":"Nunito"}}
    ))
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                      height=280, margin=dict(t=40,b=0,l=20,r=20))
    return fig

def breakdown_chart(breakdown):
    labels = list(breakdown.keys())
    scores = [v[0] for v in breakdown.values()]
    maxes  = [v[1] for v in breakdown.values()]
    bar_colors = []
    for s, m in zip(scores, maxes):
        p = s/m
        bar_colors.append("#22c55e" if p>=0.8 else "#3b82f6" if p>=0.6
                          else "#FF9500" if p>=0.4 else "#ef4444")
    fig = go.Figure()
    fig.add_trace(go.Bar(y=labels, x=maxes, orientation="h",
                         marker=dict(color="#1e293b", cornerradius=6),
                         showlegend=False))
    fig.add_trace(go.Bar(y=labels, x=scores, orientation="h",
                         marker=dict(color=bar_colors, cornerradius=6,
                                     line=dict(width=0)),
                         showlegend=False,
                         text=[f"  {s}/{m}" for s,m in zip(scores, maxes)],
                         textposition="outside",
                         textfont={"color":"#94a3b8","size":12,"family":"JetBrains Mono"}))
    fig.update_layout(
        barmode="overlay", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(color="#94a3b8", tickfont={"size":13,"family":"Nunito"},
                   gridcolor="#ffffff08"),
        height=240, margin=dict(t=10,b=10,l=10,r=60)
    )
    return fig

# ══════════════════════════════════════════════════════════════
#  SIDEBAR
# ══════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div style="padding:20px 16px 12px;">
      <div style="display:flex; align-items:center; gap:10px; margin-bottom:6px;">
        <div style="width:44px;height:44px; background:linear-gradient(135deg,#FF6B00,#FF9500);
             border-radius:12px; display:flex; align-items:center; justify-content:center;
             font-size:24px; box-shadow:0 6px 20px #FF6B0060;">🐄</div>
        <div>
          <div style="font-family:'Baloo 2',sans-serif; font-size:22px; font-weight:800;
               color:#fff; line-height:1;">PashuScore</div>
          <div style="font-size:9px; letter-spacing:2px; color:#FF6B00;
               text-transform:uppercase; font-weight:700;">Credit Intelligence</div>
        </div>
      </div>
      <div style="height:2px; background:linear-gradient(90deg,#FF6B00,#138808,transparent);
           border-radius:2px; margin:14px 0 8px;"></div>
    </div>
    """, unsafe_allow_html=True)

    page = st.radio("", [
        "🏠  Dashboard",
        "📊  Score a Farmer",
        "🌾  Village Batch Score",
        "🐄  Cattle Registry",
        "💉  Vaccination Alerts",
        "🏦  Loan Applications",
        "➕  Register New",
    ], label_visibility="collapsed")

    st.markdown("""
    <div style="margin:20px 16px 0; padding:14px; background:#FF6B0010;
         border:1px solid #FF6B0025; border-radius:14px;">
      <div style="font-size:10px; color:#FF9500; font-weight:800;
           letter-spacing:2px; margin-bottom:8px;">ABOUT</div>
      <div style="font-size:11px; color:#64748b; line-height:1.7;">
        🇮🇳 Made for Rural India<br>
        🐄 SQLite · Python · Plotly<br>
        🏅 NSTI Chennai · 2026<br>
        👨‍💻 Mohan | Team 4
      </div>
    </div>
    """, unsafe_allow_html=True)

# ── Helper: Section header ─────────────────────────────────────
def section_header(icon, title, subtitle, color="#FF6B00"):
    st.markdown(f"""
    <div style="margin-bottom:24px;">
      <div style="display:flex; align-items:center; gap:12px; margin-bottom:4px;">
        <div style="width:42px;height:42px; background:linear-gradient(135deg,{color}30,{color}15);
             border:1px solid {color}40; border-radius:12px;
             display:flex;align-items:center;justify-content:center;font-size:20px;">{icon}</div>
        <div>
          <div style="font-family:'Baloo 2',sans-serif;font-size:26px;font-weight:800;
               color:#f1f5f9;line-height:1;">{title}</div>
          <div style="font-size:12px;color:#64748b;letter-spacing:1px;">{subtitle}</div>
        </div>
      </div>
      <div style="height:2px;background:linear-gradient(90deg,{color},{color}40,transparent);
           border-radius:2px;margin-top:10px;"></div>
    </div>
    """, unsafe_allow_html=True)

def stat_card(value, label, color, icon, bg):
    return f"""
    <div style="background:linear-gradient(135deg,{bg},{bg}80);
         border:1px solid {color}30; border-radius:20px; padding:22px 20px;
         position:relative; overflow:hidden;
         box-shadow:0 8px 32px rgba(0,0,0,0.4), inset 0 1px 0 {color}20;
         transition:all 0.3s;">
      <div style="position:absolute;top:-20px;right:-20px;width:80px;height:80px;
           background:{color}15;border-radius:50%;"></div>
      <div style="position:absolute;top:12px;right:16px;font-size:28px;opacity:0.4;">{icon}</div>
      <div style="font-size:10px;letter-spacing:2px;color:{color};
           font-weight:800;text-transform:uppercase;margin-bottom:6px;">{label}</div>
      <div style="font-family:'Baloo 2',sans-serif;font-size:44px;font-weight:800;
           color:#f1f5f9;line-height:1;text-shadow:0 2px 10px rgba(0,0,0,0.5);">{value}</div>
    </div>"""

# ══════════════════════════════════════════════════════════════
#  PAGE 1 — DASHBOARD
# ══════════════════════════════════════════════════════════════
if page == "🏠  Dashboard":
    # Animated hero banner
    st.markdown("""
    <div style="background:linear-gradient(135deg,#1a0a00,#0a1a00,#000a1a);
         border:1px solid #ffffff10; border-radius:24px; padding:32px 36px;
         margin-bottom:28px; position:relative; overflow:hidden;">
      <div style="position:absolute;top:-40px;right:-40px;width:200px;height:200px;
           background:radial-gradient(circle,#FF6B0025,transparent 70%);
           border-radius:50%;animation:pulse 3s ease-in-out infinite;"></div>
      <div style="position:absolute;bottom:-30px;left:30%;width:150px;height:150px;
           background:radial-gradient(circle,#13880825,transparent 70%);border-radius:50%;"></div>
      <style>@keyframes pulse{0%,100%{transform:scale(1);opacity:1}50%{transform:scale(1.1);opacity:0.7}}</style>
      <div style="font-family:'Baloo 2',sans-serif;font-size:13px;font-weight:800;
           color:#FF9500;letter-spacing:3px;text-transform:uppercase;margin-bottom:8px;">
        🇮🇳 NSTI HACKATHON 2026 · TEAM 4
      </div>
      <div style="font-family:'Baloo 2',sans-serif;font-size:38px;font-weight:800;
           color:#fff;line-height:1.1;margin-bottom:8px;">
        🐄 PashuScore
        <span style="background:linear-gradient(135deg,#FF6B00,#FFD700);
              -webkit-background-clip:text;-webkit-text-fill-color:transparent;">
          Command Center
        </span>
      </div>
      <div style="font-size:14px;color:#64748b;max-width:500px;">
        AI-powered cattle-backed credit scoring for rural India.
        Helping farmers access fair financial services.
      </div>
    </div>
    """, unsafe_allow_html=True)

    farmers_base = run_query("SELECT farmer_id,name,village,state FROM farmers ORDER BY name")
    rows = []
    if not farmers_base.empty:
        for _, r in farmers_base.iterrows():
            s = compute_score(r["farmer_id"])
            rows.append({"farmer_id":r["farmer_id"],"name":r["name"],
                         "village":r["village"],"state":r["state"],
                         "credit_score":s["total"] if s else 0,
                         "herd_size":s["n"] if s else 0,
                         "grade":s["grade"] if s else "D",
                         "color":s["color"] if s else "#ef4444"})
    df_all = pd.DataFrame(rows)
    if not df_all.empty:
        df_all = df_all.sort_values("credit_score", ascending=False)

    total_cattle = run_query("SELECT COUNT(*) AS n FROM cattle WHERE health_status!='Deceased'")
    overdue_vacc = run_query("SELECT COUNT(DISTINCT cattle_id) AS n FROM vaccinations WHERE DATE(next_due)<DATE('now')")
    pending_apps = run_query("SELECT COUNT(*) AS n FROM loan_applications WHERE status='Pending'")

    c1,c2,c3,c4 = st.columns(4)
    n_farmers = len(df_all)
    n_cattle  = int(total_cattle["n"].iloc[0]) if not total_cattle.empty else 0
    n_vacc    = int(overdue_vacc["n"].iloc[0]) if not overdue_vacc.empty else 0
    n_loans   = int(pending_apps["n"].iloc[0]) if not pending_apps.empty else 0

    c1.markdown(stat_card(n_farmers, "Total Farmers", "#FF6B00", "🧑‍🌾", "#1a0a00"), unsafe_allow_html=True)
    c2.markdown(stat_card(n_cattle,  "Active Cattle",  "#22c55e", "🐄", "#001a08"), unsafe_allow_html=True)
    c3.markdown(stat_card(n_vacc,    "Vacc Overdue",   "#ef4444", "💉", "#1a0000"), unsafe_allow_html=True)
    c4.markdown(stat_card(n_loans,   "Pending Loans",  "#3b82f6", "🏦", "#00081a"), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns([1.7, 1])

    with col1:
        st.markdown("""<div style="font-family:'Baloo 2',sans-serif;font-size:18px;
            font-weight:800;color:#f1f5f9;margin-bottom:14px;">🏆 Farmer Leaderboard</div>""",
            unsafe_allow_html=True)
        if not df_all.empty:
            grade_icon = {"A+":"🟢","A":"🔵","B":"🟡","C":"🟠","D":"🔴"}
            df_disp = df_all.copy()
            df_disp["Grade"] = df_disp["grade"].map(lambda g: f"{grade_icon.get(g,'⚪')} {g}")
            df_disp["Score"] = df_disp["credit_score"]
            st.dataframe(df_disp[["name","village","state","herd_size","Score","Grade"]].rename(
                columns={"name":"Farmer","village":"Village","state":"State","herd_size":"🐄 Herd"}),
                use_container_width=True, hide_index=True)

    with col2:
        st.markdown("""<div style="font-family:'Baloo 2',sans-serif;font-size:18px;
            font-weight:800;color:#f1f5f9;margin-bottom:14px;">📊 Grade Split</div>""",
            unsafe_allow_html=True)
        if not df_all.empty:
            gc = df_all["grade"].value_counts().reset_index()
            gc.columns = ["Grade","Count"]
            cm = {"A+":"#22c55e","A":"#3b82f6","B":"#FF9500","C":"#f97316","D":"#ef4444"}
            fig_pie = px.pie(gc, names="Grade", values="Count",
                             color="Grade", color_discrete_map=cm, hole=0.55)
            fig_pie.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                legend=dict(font=dict(color="#94a3b8",size=12,family="Nunito")),
                height=280, margin=dict(t=0,b=0,l=0,r=0)
            )
            fig_pie.update_traces(textfont=dict(color="#fff",size=13,family="Baloo 2"),
                                  marker=dict(line=dict(color="#0a0a0f",width=3)))
            st.plotly_chart(fig_pie, use_container_width=True)

# ══════════════════════════════════════════════════════════════
#  PAGE 2 — SCORE A FARMER
# ══════════════════════════════════════════════════════════════
elif page == "📊  Score a Farmer":
    section_header("📊", "Credit Score Engine", "AI-powered cattle-backed assessment")

    farmers_df = run_query("SELECT farmer_id,name,village FROM farmers ORDER BY name")
    if farmers_df.empty:
        st.warning("No farmers in database.")
    else:
        options = {f"{r['name']}  ·  {r['village']}": r["farmer_id"]
                   for _, r in farmers_df.iterrows()}
        cs1, cs2 = st.columns([3,1])
        with cs1:
            selected_label = st.selectbox("Farmer", list(options.keys()),
                                          label_visibility="collapsed")
        with cs2:
            compute_clicked = st.button("⚡ SCORE NOW", type="primary", use_container_width=True)
        farmer_id = options[selected_label]

        if compute_clicked:
            with st.spinner("Analysing herd..."):
                result      = compute_score(farmer_id)
                farmer_info = run_query("SELECT * FROM farmers WHERE farmer_id=?", (farmer_id,))
            if result is None:
                st.session_state["score_result"] = None
                st.session_state["score_farmer_id"] = None
                st.session_state["score_farmer_info"] = None
                st.error("No active cattle found.")
            else:
                st.session_state["score_result"]      = result
                st.session_state["score_farmer_id"]   = farmer_id
                st.session_state["score_farmer_info"] = farmer_info

        result           = st.session_state.get("score_result")
        farmer_info      = st.session_state.get("score_farmer_info")
        scored_farmer_id = st.session_state.get("score_farmer_id")

        if result is not None and scored_farmer_id == farmer_id:
            st.markdown("<br>", unsafe_allow_html=True)
            col1, col2 = st.columns([1, 1.5])

            with col1:
                # 3D gauge card
                st.markdown(f"""
                <div style="background:linear-gradient(145deg,#1a1a2e,#13131f);
                     border:1px solid {result['color']}30; border-radius:24px;
                     padding:8px 8px 0; margin-bottom:12px;
                     box-shadow:0 20px 60px rgba(0,0,0,0.5),
                               0 0 0 1px {result['color']}20,
                               inset 0 1px 0 #ffffff08;">
                """, unsafe_allow_html=True)
                st.plotly_chart(gauge_chart(result["total"], result["color"]),
                                use_container_width=True)
                st.markdown("</div>", unsafe_allow_html=True)

                # Grade card — 3D effect
                st.markdown(f"""
                <div style="background:linear-gradient(145deg,{result['bg']},{result['bg']}90);
                     border:1px solid {result['color']}40; border-radius:20px;
                     padding:22px; text-align:center; margin-bottom:12px;
                     box-shadow:0 12px 40px rgba(0,0,0,0.5),
                               0 0 0 1px {result['color']}15,
                               inset 0 1px 0 {result['color']}20;
                     position:relative; overflow:hidden;">
                  <div style="position:absolute;top:0;left:0;right:0;height:3px;
                       background:linear-gradient(90deg,transparent,{result['color']},transparent);"></div>
                  <div style="font-size:11px;letter-spacing:3px;color:{result['color']};
                       font-weight:800;text-transform:uppercase;margin-bottom:8px;">Credit Grade</div>
                  <div style="font-family:'Baloo 2',sans-serif;font-size:72px;font-weight:800;
                       color:{result['color']};line-height:1;
                       text-shadow:0 0 40px {result['color']}80,0 4px 0 rgba(0,0,0,0.5);">
                    {result['grade']}
                  </div>
                  <div style="width:60px;height:3px;background:{result['color']};
                       border-radius:2px;margin:10px auto;opacity:0.5;"></div>
                  <div style="font-family:'Baloo 2',sans-serif;font-size:28px;font-weight:800;
                       color:#f1f5f9;margin-bottom:4px;">₹{result['amount']:,}</div>
                  <div style="font-size:12px;color:#64748b;">@ {result['rate']}% per annum</div>
                </div>
                """, unsafe_allow_html=True)

                # Farmer info card
                if farmer_info is not None and not farmer_info.empty:
                    fi = farmer_info.iloc[0]
                    st.markdown(f"""
                    <div style="background:#13131f;border:1px solid #ffffff0f;
                         border-radius:18px;padding:18px;">
                      <div style="font-size:10px;letter-spacing:2px;color:#FF9500;
                           font-weight:800;text-transform:uppercase;margin-bottom:12px;">
                        Farmer Profile
                      </div>
                      <div style="display:flex;flex-direction:column;gap:10px;">
                        <div style="display:flex;justify-content:space-between;align-items:center;
                             padding:8px 12px;background:#1a1a2e;border-radius:10px;">
                          <span style="color:#64748b;font-size:12px;">📍 Location</span>
                          <span style="color:#e2e8f0;font-size:12px;font-weight:700;">
                            {fi['village']}, {fi['state']}</span>
                        </div>
                        <div style="display:flex;justify-content:space-between;align-items:center;
                             padding:8px 12px;background:#1a1a2e;border-radius:10px;">
                          <span style="color:#64748b;font-size:12px;">🌾 Land</span>
                          <span style="color:#e2e8f0;font-size:12px;font-weight:700;">
                            {fi['land_acres']} acres</span>
                        </div>
                        <div style="display:flex;justify-content:space-between;align-items:center;
                             padding:8px 12px;background:#1a1a2e;border-radius:10px;">
                          <span style="color:#64748b;font-size:12px;">🐄 Herd</span>
                          <span style="color:#22c55e;font-size:12px;font-weight:800;">
                            {result['n']} active animals</span>
                        </div>
                      </div>
                    </div>
                    """, unsafe_allow_html=True)

            with col2:
                # Breakdown chart card
                st.markdown("""
                <div style="background:#13131f;border:1px solid #ffffff0f;
                     border-radius:20px;padding:20px;margin-bottom:14px;">
                  <div style="font-family:'Baloo 2',sans-serif;font-size:16px;font-weight:800;
                       color:#f1f5f9;margin-bottom:4px;">📈 Score Breakdown</div>
                  <div style="font-size:11px;color:#64748b;margin-bottom:14px;">
                    Component-wise performance analysis
                  </div>
                """, unsafe_allow_html=True)
                st.plotly_chart(breakdown_chart(result["breakdown"]),
                                use_container_width=True)

                # Pills
                pills = ""
                for label, (score, max_val, detail) in result["breakdown"].items():
                    p = score / max_val
                    c = "#22c55e" if p>=0.8 else "#3b82f6" if p>=0.6 else "#FF9500" if p>=0.4 else "#ef4444"
                    pills += f"""<div style="background:{c}15;border:1px solid {c}35;
                        border-radius:10px;padding:6px 12px;display:inline-block;
                        margin:4px;font-size:11px;color:{c};font-weight:700;">
                        {score}/{max_val} {label}</div>"""
                st.markdown(f'<div style="margin-bottom:4px;">{pills}</div></div>',
                            unsafe_allow_html=True)

                # Herd table
                st.markdown("""
                <div style="background:#13131f;border:1px solid #ffffff0f;
                     border-radius:20px;padding:20px;margin-bottom:14px;">
                  <div style="font-family:'Baloo 2',sans-serif;font-size:16px;font-weight:800;
                       color:#f1f5f9;margin-bottom:14px;">🐄 Herd Details</div>
                """, unsafe_allow_html=True)
                df_c = result["cattle_df"].copy()
                h_map = {"Healthy":"🟢 Healthy","Mild Fever":"🟡 Mild Fever",
                         "Limping":"🟠 Limping","Critical":"🔴 Critical"}
                df_c["Health"]    = df_c["health_status"].map(lambda h: h_map.get(h, h))
                df_c["Vaccinated"] = df_c["vaccinated"].map(lambda v: "✅" if v else "❌")
                st.dataframe(
                    df_c[["cattle_id","breed","age_years","Health","Vaccinated","milk_yield_lpd"]].rename(
                        columns={"cattle_id":"Tag","breed":"Breed","age_years":"Age",
                                 "milk_yield_lpd":"L/day"}),
                    use_container_width=True, hide_index=True)
                st.markdown("</div>", unsafe_allow_html=True)

                # Loan Apply button
                if st.button("🏦  APPLY FOR LOAN  →", use_container_width=True, type="primary"):
                    existing = run_query(
                        "SELECT app_id FROM loan_applications WHERE farmer_id=? AND status='Pending'",
                        (farmer_id,))
                    if not existing.empty:
                        st.warning(f"⚠️ Pending application exists — App #{existing['app_id'].iloc[0]}")
                    else:
                        lid = execute("""INSERT INTO loan_applications
                            (farmer_id,credit_score,grade,amount_eligible,status)
                            VALUES (?,?,?,?,'Pending')""",
                            (farmer_id, result["total"], result["grade"], result["amount"]))
                        if lid is not None:
                            st.success(f"✅ Application #{lid} submitted! Go to 🏦 Loan Applications.")
                            st.session_state["score_result"] = None

# ══════════════════════════════════════════════════════════════
#  PAGE 3 — VILLAGE BATCH SCORE
# ══════════════════════════════════════════════════════════════
elif page == "🌾  Village Batch Score":
    section_header("🌾", "Village Batch Scoring",
                   "Score all farmers in a village simultaneously", "#138808")

    villages = run_query("SELECT DISTINCT village FROM farmers ORDER BY village")
    vlist = villages["village"].tolist() if not villages.empty else []
    bv1, bv2 = st.columns([3,1])
    with bv1:
        village = st.selectbox("Village", vlist, label_visibility="collapsed")
    with bv2:
        run_b = st.button("🚀 RUN", type="primary", use_container_width=True)

    if village and run_b:
        fiv = run_query("SELECT farmer_id,name FROM farmers WHERE village=?", (village,))
        if fiv.empty:
            st.warning("No farmers found.")
        else:
            results = []
            prog = st.progress(0, text="Scoring...")
            for i, (_, row) in enumerate(fiv.iterrows()):
                s = compute_score(row["farmer_id"])
                if s:
                    results.append({"Farmer":row["name"],"Score":s["total"],
                                    "Grade":s["grade"],"Max Loan":f"₹{s['amount']:,}",
                                    "Rate":f"{s['rate']}%","Herd":s["n"]})
                prog.progress((i+1)/len(fiv), text=f"Scored {row['name']}")
            prog.empty()
            if results:
                df_r = pd.DataFrame(results).sort_values("Score", ascending=False)
                st.markdown("<br>", unsafe_allow_html=True)
                r1,r2,r3 = st.columns(3)
                elig = df_r[df_r["Grade"].isin(["A+","A","B"])].shape[0]
                r1.markdown(stat_card(elig, "Loan Eligible", "#22c55e", "✅", "#001a08"), unsafe_allow_html=True)
                r2.markdown(stat_card(f"{df_r['Score'].mean():.0f}", "Avg Score", "#3b82f6", "📊", "#00081a"), unsafe_allow_html=True)
                r3.markdown(stat_card(df_r["Score"].max(), "Top Score", "#FF9500", "🏆", "#1a0800"), unsafe_allow_html=True)
                st.markdown("<br>", unsafe_allow_html=True)
                st.dataframe(df_r, use_container_width=True, hide_index=True)
                cm = {"A+":"#22c55e","A":"#3b82f6","B":"#FF9500","C":"#f97316","D":"#ef4444"}
                fig = px.bar(df_r, x="Farmer", y="Score", color="Grade",
                             color_discrete_map=cm, title=f"Scores — {village}")
                fig.update_layout(paper_bgcolor="rgba(0,0,0,0)",
                                  plot_bgcolor="rgba(0,0,0,0)",
                                  font=dict(color="#94a3b8",family="Nunito"),
                                  title_font=dict(color="#FF9500",family="Baloo 2",size=18),
                                  xaxis=dict(gridcolor="#ffffff08"),
                                  yaxis=dict(gridcolor="#ffffff08"))
                fig.update_traces(marker_line_width=0)
                st.plotly_chart(fig, use_container_width=True)

# ══════════════════════════════════════════════════════════════
#  PAGE 4 — CATTLE REGISTRY
# ══════════════════════════════════════════════════════════════
elif page == "🐄  Cattle Registry":
    section_header("🐄", "Cattle Registry", "Complete herd database", "#138808")
    df = run_query("""
        SELECT c.cattle_id, f.name AS farmer, f.village, c.breed,
               c.age_years, c.health_status, c.milk_yield_lpd, c.ear_tag,
               CASE WHEN v.cattle_id IS NOT NULL THEN '✅ Done' ELSE '❌ Pending' END AS vacc_status
        FROM cattle c
        JOIN farmers f ON c.farmer_id=f.farmer_id
        LEFT JOIN vaccinations v ON c.cattle_id=v.cattle_id AND DATE(v.next_due)>=DATE('now')
        ORDER BY f.name, c.breed
    """)
    if not df.empty:
        f1,f2 = st.columns(2)
        with f1: bf = st.multiselect("Breed", sorted(df["breed"].unique()))
        with f2: hf = st.multiselect("Health", sorted(df["health_status"].unique()))
        if bf: df = df[df["breed"].isin(bf)]
        if hf: df = df[df["health_status"].isin(hf)]
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.markdown(f"<div style='font-size:12px;color:#64748b;margin-top:4px;'>{len(df)} animals</div>",
                    unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("""<div style="font-family:'Baloo 2',sans-serif;font-size:16px;
            font-weight:800;color:#FF9500;margin-bottom:12px;">⚡ Update Health</div>""",
            unsafe_allow_html=True)
        u1,u2,u3 = st.columns(3)
        with u1: cid_sel = st.selectbox("Cattle", df["cattle_id"].tolist())
        with u2: nh = st.selectbox("Status", ["Healthy","Mild Fever","Limping","Critical","Deceased"])
        with u3:
            st.write(""); st.write("")
            if st.button("✅ UPDATE", use_container_width=True, type="primary"):
                execute("UPDATE cattle SET health_status=? WHERE cattle_id=?", (nh, cid_sel))
                st.success(f"Updated {cid_sel} → {nh}"); st.rerun()

# ══════════════════════════════════════════════════════════════
#  PAGE 5 — VACCINATION ALERTS
# ══════════════════════════════════════════════════════════════
elif page == "💉  Vaccination Alerts":
    section_header("💉", "Vaccination Alerts", "Overdue monitoring system", "#ef4444")
    df = run_query("""
        SELECT c.cattle_id, c.ear_tag, c.breed, f.name AS farmer,
               f.phone, f.village, v.vaccine, v.next_due,
               CAST((julianday('now')-julianday(v.next_due)) AS INTEGER) AS days_overdue
        FROM vaccinations v
        JOIN cattle c ON v.cattle_id=c.cattle_id
        JOIN farmers f ON c.farmer_id=f.farmer_id
        WHERE DATE(v.next_due)<DATE('now')
        ORDER BY days_overdue DESC
    """)
    if df.empty:
        st.markdown("""
        <div style="background:linear-gradient(135deg,#00260f,#001a08);
             border:1px solid #22c55e30;border-radius:24px;
             padding:48px;text-align:center;">
          <div style="font-size:64px;margin-bottom:12px;">✅</div>
          <div style="font-family:'Baloo 2',sans-serif;font-size:24px;font-weight:800;
               color:#22c55e;">All Vaccinations Up To Date!</div>
          <div style="font-size:14px;color:#64748b;margin-top:6px;">
            No overdue vaccinations found.</div>
        </div>""", unsafe_allow_html=True)
    else:
        def sev(d): return "🔴 Critical" if d>180 else "🟠 High" if d>90 else "🟡 Moderate"
        df["Severity"] = df["days_overdue"].apply(sev)
        v1,v2,v3 = st.columns(3)
        v1.markdown(stat_card(len(df), "Total Overdue", "#ef4444", "⚠️", "#1a0000"), unsafe_allow_html=True)
        v2.markdown(stat_card(len(df[df["days_overdue"]>180]), "Critical", "#f97316", "🔴", "#1a0800"), unsafe_allow_html=True)
        v3.markdown(stat_card(len(df[df["days_overdue"]>90]), "High Priority", "#FF9500", "🟠", "#1a0d00"), unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        st.dataframe(df.rename(columns={"cattle_id":"Cattle","ear_tag":"Tag","breed":"Breed",
                                         "farmer":"Farmer","phone":"Phone","village":"Village",
                                         "vaccine":"Vaccine","next_due":"Due Date",
                                         "days_overdue":"Days Overdue"}),
                     use_container_width=True, hide_index=True)
        fig = px.bar(df.head(10), x="cattle_id", y="days_overdue", color="Severity",
                     color_discrete_map={"🔴 Critical":"#ef4444","🟠 High":"#f97316","🟡 Moderate":"#FF9500"})
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                          font=dict(color="#94a3b8",family="Nunito"),
                          xaxis=dict(gridcolor="#ffffff08"), yaxis=dict(gridcolor="#ffffff08"))
        st.plotly_chart(fig, use_container_width=True)

# ══════════════════════════════════════════════════════════════
#  PAGE 6 — LOAN APPLICATIONS
# ══════════════════════════════════════════════════════════════
elif page == "🏦  Loan Applications":
    section_header("🏦", "Loan Applications", "Application pipeline & approval system", "#3b82f6")
    df = run_query("""
        SELECT la.app_id, f.name, f.village, f.state,
               la.credit_score, la.grade, la.amount_eligible,
               la.status, la.applied_on
        FROM loan_applications la
        JOIN farmers f ON la.farmer_id=f.farmer_id
        ORDER BY la.applied_on DESC, la.app_id DESC
    """)
    if df.empty:
        st.info("No loan applications yet.")
    else:
        la1,la2,la3,la4 = st.columns(4)
        la1.markdown(stat_card(len(df), "Total Apps", "#3b82f6", "📋", "#00081a"), unsafe_allow_html=True)
        la2.markdown(stat_card(len(df[df["status"]=="Approved"]), "Approved", "#22c55e", "✅", "#001a08"), unsafe_allow_html=True)
        la3.markdown(stat_card(len(df[df["status"]=="Pending"]), "Pending", "#FF9500", "⏳", "#1a0800"), unsafe_allow_html=True)
        la4.markdown(stat_card(len(df[df["status"]=="Rejected"]), "Rejected", "#ef4444", "❌", "#1a0000"), unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        sf = st.selectbox("Filter", ["All","Pending","Approved","Rejected"],
                          label_visibility="collapsed")
        dfd = df if sf=="All" else df[df["status"]==sf]
        def fmt_s(s):
            return "✅ Approved" if s=="Approved" else "⏳ Pending" if s=="Pending" else "❌ Rejected"
        dfd = dfd.copy(); dfd["status"] = dfd["status"].apply(fmt_s)
        st.dataframe(dfd.rename(columns={"app_id":"App #","name":"Farmer","village":"Village",
                                          "state":"State","credit_score":"Score","grade":"Grade",
                                          "amount_eligible":"Eligible ₹","status":"Status",
                                          "applied_on":"Applied On"}),
                     use_container_width=True, hide_index=True)

        pending_df = df[df["status"]=="Pending"]
        if not pending_df.empty:
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("""<div style="font-family:'Baloo 2',sans-serif;font-size:16px;
                font-weight:800;color:#FF9500;margin-bottom:12px;">⚡ Quick Decision</div>""",
                unsafe_allow_html=True)
            qd1,qd2,qd3 = st.columns(3)
            with qd1: sel = st.selectbox("Pending App", pending_df["app_id"].tolist())
            with qd2:
                st.write(""); st.write("")
                if st.button("✅ APPROVE", use_container_width=True, type="primary"):
                    execute("UPDATE loan_applications SET status='Approved' WHERE app_id=?", (sel,))
                    st.success(f"App #{sel} Approved! 🎉"); st.rerun()
            with qd3:
                st.write(""); st.write("")
                if st.button("❌ REJECT", use_container_width=True):
                    execute("UPDATE loan_applications SET status='Rejected' WHERE app_id=?", (sel,))
                    st.warning(f"App #{sel} Rejected."); st.rerun()

# ══════════════════════════════════════════════════════════════
#  PAGE 7 — ADD FARMER / CATTLE
# ══════════════════════════════════════════════════════════════
elif page == "➕  Register New":
    section_header("➕", "Register New Records", "Add farmers, cattle, vaccinations", "#7c3aed")
    tab1, tab2, tab3 = st.tabs(["🧑‍🌾  New Farmer", "🐄  New Cattle", "💉  Vaccination"])

    with tab1:
        with st.form("af"):
            c1,c2 = st.columns(2)
            fid   = c1.text_input("Farmer ID", placeholder="F005")
            nm    = c2.text_input("Full Name")
            vil   = c1.text_input("Village")
            sta   = c2.text_input("State")
            la    = c1.number_input("Land (acres)", 0.0,100.0,1.0,0.1)
            ph    = c2.text_input("Phone")
            if st.form_submit_button("⚡ REGISTER FARMER", use_container_width=True):
                if not all([fid,nm,vil,sta]):
                    st.error("Fill all required fields.")
                else:
                    execute("INSERT INTO farmers (farmer_id,name,village,state,land_acres,phone) VALUES (?,?,?,?,?,?)",
                            (fid,nm,vil,sta,la,ph))
                    st.success(f"✅ {nm} registered as {fid}!")

    with tab2:
        fdf = run_query("SELECT farmer_id,name FROM farmers ORDER BY name")
        fmap = {f"{r['name']} ({r['farmer_id']})": r["farmer_id"]
                for _,r in fdf.iterrows()} if not fdf.empty else {}
        with st.form("ac"):
            c1,c2 = st.columns(2)
            fsel  = c1.selectbox("Farmer", list(fmap.keys()) if fmap else [])
            cid   = c2.text_input("Cattle ID", placeholder="C15")
            br    = c1.selectbox("Breed", list(BREED_WEIGHTS.keys()))
            ag    = c2.number_input("Age (years)", 1,20,3)
            yl    = c1.number_input("Milk Yield (L/day)", 0.0,50.0,5.0,0.5)
            et    = c2.text_input("Ear Tag")
            if st.form_submit_button("⚡ REGISTER CATTLE", use_container_width=True) and fsel:
                execute("INSERT INTO cattle (cattle_id,farmer_id,breed,age_years,health_status,milk_yield_lpd,ear_tag) VALUES (?,?,?,?,'Healthy',?,?)",
                        (cid, fmap.get(fsel,""), br, ag, yl, et))
                st.success(f"✅ {cid} ({br}) registered!")

    with tab3:
        ac = run_query("SELECT cattle_id FROM cattle WHERE health_status!='Deceased'")
        with st.form("av"):
            c1,c2 = st.columns(2)
            cids  = c1.selectbox("Cattle", ac["cattle_id"].tolist() if not ac.empty else [])
            vac   = c2.text_input("Vaccine", placeholder="FMD + HS")
            giv   = c1.date_input("Date Given", value=date.today())
            du    = c2.date_input("Next Due Date")
            vet   = c1.text_input("Vet Name")
            if st.form_submit_button("⚡ ADD RECORD", use_container_width=True) and cids:
                execute("INSERT INTO vaccinations (cattle_id,vaccine,given_on,next_due,vet_name) VALUES (?,?,?,?,?)",
                        (cids,vac,str(giv),str(du),vet))
                st.success(f"✅ Vaccination recorded for {cids}!")
