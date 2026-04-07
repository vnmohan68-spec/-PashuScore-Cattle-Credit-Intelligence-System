import streamlit as st
import sqlite3
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import date
from pathlib import Path

# ── Page Config ───────────────────────────────────────────────
st.set_page_config(
    page_title="PashuScore",
    page_icon="🐄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── PREMIUM CSS + ANIMATIONS ──────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@600;700&family=Inter:wght@300;400;500;600&family=Space+Mono:wght@400;700&display=swap');

/* ── Root variables ── */
:root {
  --neon:    #00ff88;
  --neon2:   #00ccff;
  --gold:    #f0c040;
  --bg:      #030712;
  --surface: #0d1117;
  --card:    #111827;
  --border:  #1f2937;
  --text:    #e2e8f0;
  --muted:   #6b7280;
}

/* ── Global ── */
html, body, [class*="css"] {
  font-family: 'Inter', sans-serif;
  background-color: var(--bg) !important;
  color: var(--text);
}
.main .block-container { padding-top: 1rem; }

/* ── Animated gradient background ── */
.stApp {
  background:
    radial-gradient(ellipse at 10% 20%, #00ff8808 0%, transparent 50%),
    radial-gradient(ellipse at 90% 80%, #00ccff06 0%, transparent 50%),
    radial-gradient(ellipse at 50% 50%, #0d1117 0%, #030712 100%);
  animation: bgPulse 8s ease-in-out infinite alternate;
}
@keyframes bgPulse {
  0%   { background-position: 0% 0%; }
  100% { background-position: 100% 100%; }
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
  background: linear-gradient(180deg, #0a0f1a 0%, #030712 100%) !important;
  border-right: 1px solid #00ff8820 !important;
}
[data-testid="stSidebar"]::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 2px;
  background: linear-gradient(90deg, transparent, #00ff88, #00ccff, transparent);
  animation: scanline 3s linear infinite;
}
@keyframes scanline {
  0%   { transform: translateX(-100%); }
  100% { transform: translateX(100%); }
}

/* ── Sidebar radio buttons ── */
[data-testid="stSidebar"] .stRadio label {
  color: #e2e8f0 !important;
  font-family: 'Inter', sans-serif;
  font-size: 13px;
  padding: 8px 12px;
  border-radius: 8px;
  transition: all 0.2s;
  display: block;
  border: 1px solid transparent;
}
[data-testid="stSidebar"] .stRadio label:hover {
  color: #00ff88 !important;
  background: #00ff8810;
  border-color: #00ff8830;
}

/* ── Metric cards ── */
[data-testid="stMetric"] {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 16px;
  padding: 20px !important;
  position: relative;
  overflow: hidden;
  transition: transform 0.2s, border-color 0.2s;
}
[data-testid="stMetric"]:hover {
  transform: translateY(-2px);
  border-color: #00ff8840;
}
[data-testid="stMetric"]::after {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 2px;
  background: linear-gradient(90deg, var(--neon), var(--neon2));
  opacity: 0.6;
}
[data-testid="stMetricValue"] {
  font-family: 'Rajdhani', sans-serif !important;
  font-size: 36px !important;
  font-weight: 700 !important;
  color: var(--neon) !important;
  text-shadow: 0 0 20px #00ff8860;
}
[data-testid="stMetricLabel"] {
  color: var(--muted) !important;
  font-size: 11px !important;
  letter-spacing: 2px !important;
  text-transform: uppercase !important;
}

/* ── Buttons ── */
.stButton > button {
  background: linear-gradient(135deg, #00ff8820, #00ccff15) !important;
  color: var(--neon) !important;
  border: 1px solid #00ff8840 !important;
  border-radius: 10px !important;
  font-family: 'Inter', sans-serif !important;
  font-weight: 600 !important;
  font-size: 13px !important;
  letter-spacing: 1px !important;
  padding: 10px 20px !important;
  transition: all 0.3s !important;
  position: relative !important;
  overflow: hidden !important;
}
.stButton > button:hover {
  background: linear-gradient(135deg, #00ff8835, #00ccff25) !important;
  border-color: var(--neon) !important;
  box-shadow: 0 0 20px #00ff8830, 0 0 40px #00ff8815 !important;
  transform: translateY(-1px) !important;
}
.stButton > button[kind="primary"] {
  background: linear-gradient(135deg, #00ff88, #00ccff) !important;
  color: #030712 !important;
  border: none !important;
  font-weight: 700 !important;
  box-shadow: 0 4px 20px #00ff8840 !important;
}
.stButton > button[kind="primary"]:hover {
  box-shadow: 0 6px 30px #00ff8860 !important;
  transform: translateY(-2px) !important;
}

/* ── Selectbox ── */
.stSelectbox > div > div {
  background: var(--card) !important;
  border: 1px solid var(--border) !important;
  border-radius: 10px !important;
  color: var(--text) !important;
}
.stSelectbox > div > div:focus-within {
  border-color: var(--neon) !important;
  box-shadow: 0 0 0 2px #00ff8820 !important;
}

/* ── Inputs ── */
.stTextInput input, .stNumberInput input {
  background: var(--card) !important;
  border: 1px solid var(--border) !important;
  border-radius: 10px !important;
  color: var(--text) !important;
  font-family: 'Inter', sans-serif !important;
}
.stTextInput input:focus, .stNumberInput input:focus {
  border-color: var(--neon) !important;
  box-shadow: 0 0 0 2px #00ff8820 !important;
}

/* ── Dataframe ── */
[data-testid="stDataFrame"] {
  border: 1px solid var(--border) !important;
  border-radius: 12px !important;
  overflow: hidden !important;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
  background: var(--card) !important;
  border-radius: 12px !important;
  padding: 4px !important;
  gap: 4px !important;
  border: 1px solid var(--border) !important;
}
.stTabs [data-baseweb="tab"] {
  color: var(--muted) !important;
  border-radius: 8px !important;
  font-family: 'Inter', sans-serif !important;
}
.stTabs [aria-selected="true"] {
  background: linear-gradient(135deg, #00ff8820, #00ccff15) !important;
  color: var(--neon) !important;
  border: 1px solid #00ff8830 !important;
}

/* ── Divider ── */
hr {
  border-color: var(--border) !important;
}

/* ── Progress bar ── */
.stProgress > div > div > div {
  background: linear-gradient(90deg, var(--neon), var(--neon2)) !important;
  border-radius: 10px !important;
}

/* ── Alert / Success / Warning ── */
.stSuccess {
  background: #00ff8810 !important;
  border: 1px solid #00ff8830 !important;
  border-radius: 10px !important;
  color: var(--neon) !important;
}
.stWarning {
  background: #f0c04010 !important;
  border: 1px solid #f0c04030 !important;
  border-radius: 10px !important;
}
.stError {
  background: #ff003310 !important;
  border: 1px solid #ff003330 !important;
  border-radius: 10px !important;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: #00ff8840; border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: var(--neon); }

/* ── Page title animation ── */
@keyframes glowPulse {
  0%, 100% { text-shadow: 0 0 20px #00ff8860, 0 0 40px #00ff8830; }
  50%       { text-shadow: 0 0 30px #00ff8890, 0 0 60px #00ff8850, 0 0 80px #00ccff30; }
}
.glow-title {
  font-family: 'Rajdhani', sans-serif;
  font-size: 2.4rem;
  font-weight: 700;
  color: var(--neon);
  animation: glowPulse 3s ease-in-out infinite;
  letter-spacing: 2px;
  margin-bottom: 0;
}
.subtitle {
  font-size: 11px;
  letter-spacing: 4px;
  color: var(--muted);
  text-transform: uppercase;
  margin-top: 4px;
}

/* ── Stat card ── */
.stat-card {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 16px;
  padding: 20px 24px;
  position: relative;
  overflow: hidden;
  transition: all 0.3s;
}
.stat-card::before {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, #00ff8806, transparent);
  opacity: 0;
  transition: opacity 0.3s;
}
.stat-card:hover::before { opacity: 1; }
.stat-card:hover { border-color: #00ff8840; transform: translateY(-2px); }

/* ── Grade badge ── */
.grade-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 56px; height: 56px;
  border-radius: 50%;
  font-family: 'Rajdhani', sans-serif;
  font-size: 22px;
  font-weight: 700;
}

/* ── Neon line separator ── */
.neon-line {
  height: 1px;
  background: linear-gradient(90deg, transparent, var(--neon), var(--neon2), transparent);
  margin: 20px 0;
  opacity: 0.4;
}

/* ── Cattle tag chip ── */
.tag-chip {
  display: inline-block;
  background: #00ff8815;
  border: 1px solid #00ff8830;
  color: var(--neon);
  border-radius: 6px;
  padding: 2px 10px;
  font-family: 'Space Mono', monospace;
  font-size: 11px;
}

/* ── Loan status badge ── */
.badge-pending  { background:#f0c04020; border:1px solid #f0c04050; color:#f0c040; padding:3px 12px; border-radius:20px; font-size:12px; }
.badge-approved { background:#00ff8820; border:1px solid #00ff8850; color:#00ff88; padding:3px 12px; border-radius:20px; font-size:12px; }
.badge-rejected { background:#ff000020; border:1px solid #ff000050; color:#ff4444; padding:3px 12px; border-radius:20px; font-size:12px; }

/* ── Sidebar logo area ── */
.sidebar-logo {
  font-family: 'Rajdhani', sans-serif;
  font-size: 28px;
  font-weight: 700;
  background: linear-gradient(135deg, var(--neon), var(--neon2));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  letter-spacing: 2px;
}
.sidebar-tag {
  font-size: 9px;
  letter-spacing: 3px;
  color: #9ca3af;
  text-transform: uppercase;
  margin-top: 2px;
}

/* ── Form submit button ── */
[data-testid="stFormSubmitButton"] > button {
  background: linear-gradient(135deg, #00ff88, #00ccff) !important;
  color: #030712 !important;
  border: none !important;
  font-weight: 700 !important;
  letter-spacing: 1px !important;
  box-shadow: 0 4px 20px #00ff8840 !important;
}

/* ── Spinner ── */
.stSpinner > div { border-top-color: var(--neon) !important; }
</style>
""", unsafe_allow_html=True)

# ── Database ──────────────────────────────────────────────────
DB_FILE = Path("pashuscore.db")

BREED_WEIGHTS = {
    "Gir": 30, "Sahiwal": 28, "Red Sindhi": 26,
    "Murrah Buffalo": 27, "Surti Buffalo": 24,
    "HF Cross": 22, "Jersey Cross": 20, "Nondescript": 10,
}
GRADE_TABLE = [
    (80, "A+", 200000, 7.0,  "#00ff88"),
    (65, "A",  150000, 9.0,  "#00ccff"),
    (50, "B",   75000, 12.0, "#f0c040"),
    (35, "C",   25000, 16.0, "#ff8800"),
    (0,  "D",       0,  0.0, "#ff4444"),
]

# ── DB Init ───────────────────────────────────────────────────
def init_db():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS farmers (
        farmer_id TEXT PRIMARY KEY, name TEXT NOT NULL,
        village TEXT NOT NULL, state TEXT NOT NULL,
        land_acres REAL, phone TEXT)""")
    cur.execute("""CREATE TABLE IF NOT EXISTS cattle (
        cattle_id TEXT PRIMARY KEY, farmer_id TEXT NOT NULL,
        breed TEXT NOT NULL, age_years INTEGER,
        health_status TEXT DEFAULT 'Healthy',
        milk_yield_lpd REAL, ear_tag TEXT,
        FOREIGN KEY (farmer_id) REFERENCES farmers(farmer_id))""")
    cur.execute("""CREATE TABLE IF NOT EXISTS vaccinations (
        vacc_id INTEGER PRIMARY KEY AUTOINCREMENT,
        cattle_id TEXT NOT NULL, vaccine TEXT,
        given_on TEXT, next_due TEXT, vet_name TEXT,
        FOREIGN KEY (cattle_id) REFERENCES cattle(cattle_id))""")
    cur.execute("""CREATE TABLE IF NOT EXISTS loan_applications (
        app_id INTEGER PRIMARY KEY AUTOINCREMENT,
        farmer_id TEXT NOT NULL, credit_score INTEGER,
        grade TEXT, amount_eligible REAL,
        status TEXT DEFAULT 'Pending',
        applied_on TEXT DEFAULT (DATE('now')),
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
            ('F004',88,'A+',200000,'Approved'),
            ('F001',76,'A',150000,'Pending'),
        ])
    conn.commit(); conn.close()

init_db()

# ── Helpers ───────────────────────────────────────────────────
def run_query(sql, params=None):
    try:
        conn = sqlite3.connect(DB_FILE)
        df = pd.read_sql_query(sql, conn, params=params or ())
        conn.close()
        return df
    except Exception as e:
        st.error(f"DB Error: {e}")
        return pd.DataFrame()

def execute(sql, params=None):
    try:
        conn = sqlite3.connect(DB_FILE)
        cur = conn.cursor()
        cur.execute(sql, params or ())
        conn.commit()
        lid = cur.lastrowid
        cur.close(); conn.close()
        return lid
    except Exception as e:
        st.error(f"DB Error: {e}")
        return None

def compute_score(farmer_id):
    df = run_query("""
        SELECT c.cattle_id, c.breed, c.age_years, c.health_status, c.milk_yield_lpd,
               CASE WHEN v.cattle_id IS NOT NULL THEN 1 ELSE 0 END AS vaccinated
        FROM cattle c
        LEFT JOIN vaccinations v ON c.cattle_id = v.cattle_id AND DATE(v.next_due) >= DATE('now')
        WHERE c.farmer_id = ? AND c.health_status != 'Deceased'
    """, (farmer_id,))
    if df.empty: return None
    n = len(df)
    herd_score   = min(n * 5, 20)
    breed_avg    = df["breed"].map(BREED_WEIGHTS).fillna(10).mean()
    breed_score  = round(breed_avg)
    vacc_count   = int(df["vaccinated"].sum())
    vacc_score   = round((vacc_count / n) * 25)
    healthy_count = int((df["health_status"] == "Healthy").sum())
    health_score = round((healthy_count / n) * 15)
    high_yield   = int((df["milk_yield_lpd"] >= 8).sum())
    yield_score  = round((high_yield / n) * 10)
    total = herd_score + breed_score + vacc_score + health_score + yield_score
    grade, amount, rate, color = "D", 0, 0.0, "#ff4444"
    for threshold, g, a, r, c in GRADE_TABLE:
        if total >= threshold:
            grade, amount, rate, color = g, a, r, c
            break
    return {"total": total, "grade": grade, "amount": amount, "rate": rate,
            "color": color, "n": n,
            "breakdown": {
                "Herd Size":     (herd_score,   20, f"{n} animals"),
                "Breed Quality": (breed_score,  30, f"Avg {breed_avg:.1f}"),
                "Vaccination":   (vacc_score,   25, f"{vacc_count}/{n} vaccinated"),
                "Health":        (health_score, 15, f"{healthy_count}/{n} healthy"),
                "Milk Yield":    (yield_score,  10, f"{high_yield} high-yield"),
            },
            "cattle_df": df}

def gauge_chart(score, color):
    fig = go.Figure(go.Indicator(
        mode="gauge+number", value=score,
        domain={"x": [0,1], "y": [0,1]},
        gauge={
            "axis": {"range": [0,100], "tickcolor": "#374151",
                     "tickfont": {"color": "#6b7280", "size": 10}},
            "bar":  {"color": color, "thickness": 0.2},
            "bgcolor": "#0d1117",
            "bordercolor": "#1f2937",
            "steps": [
                {"range": [0, 35],  "color": "#1a0a0a"},
                {"range": [35, 50], "color": "#1a1200"},
                {"range": [50, 65], "color": "#001a0a"},
                {"range": [65, 80], "color": "#001a10"},
                {"range": [80,100], "color": "#001a15"},
            ],
            "threshold": {"line": {"color": color, "width": 3},
                          "thickness": 0.85, "value": score}
        },
        number={"font": {"color": color, "size": 54, "family": "Rajdhani"},
                "suffix": "/100"},
        title={"text": "CREDIT SCORE",
               "font": {"color": "#6b7280", "size": 11, "family": "Inter"}}
    ))
    fig.update_layout(
        paper_bgcolor="#0d1117", plot_bgcolor="#0d1117",
        height=270, margin=dict(t=40, b=10, l=20, r=20)
    )
    return fig

def breakdown_chart(breakdown):
    labels = list(breakdown.keys())
    scores = [v[0] for v in breakdown.values()]
    maxes  = [v[1] for v in breakdown.values()]
    pcts   = [s/m for s,m in zip(scores, maxes)]
    colors = ["#00ff88" if p >= 0.8 else "#00ccff" if p >= 0.6 else "#f0c040" if p >= 0.4 else "#ff8800"
              for p in pcts]
    fig = go.Figure()
    fig.add_trace(go.Bar(y=labels, x=maxes, orientation="h",
                         marker_color="#1f2937", showlegend=False))
    fig.add_trace(go.Bar(y=labels, x=scores, orientation="h",
                         marker=dict(color=colors,
                                     line=dict(width=0)),
                         showlegend=False,
                         text=[f"{s}/{m}" for s,m in zip(scores, maxes)],
                         textposition="inside",
                         textfont={"color": "#030712", "size": 11, "family": "Space Mono"}))
    fig.update_layout(
        barmode="overlay", paper_bgcolor="#111827", plot_bgcolor="#111827",
        xaxis=dict(showgrid=False, zeroline=False, color="#374151",
                   showticklabels=False),
        yaxis=dict(color="#9ca3af", tickfont={"size": 12, "family": "Inter"}),
        height=230, margin=dict(t=10, b=10, l=10, r=10)
    )
    return fig

# ── SIDEBAR ───────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding: 16px 8px 8px 8px;">
      <div class="sidebar-logo">🐄 PASHU<span style="color:#00ccff">SCORE</span></div>
      <div class="sidebar-tag">Cattle Credit Intelligence · v2.0</div>
    </div>
    <div class="neon-line"></div>
    """, unsafe_allow_html=True)

    page = st.radio("", [
        "🏠  Dashboard",
        "📊  Score a Farmer",
        "🌾  Village Batch Score",
        "🐄  Cattle Registry",
        "💉  Vaccination Alerts",
        "🏦  Loan Applications",
        "➕  Add Farmer / Cattle",
    ], label_visibility="collapsed")

    st.markdown("""<div class="neon-line"></div>""", unsafe_allow_html=True)
    st.markdown("""
    <div style="padding:8px; font-size:10px; color:#374151; letter-spacing:1px; line-height:1.8;">
      <div style="color:#00ff8860;">▸</div> SQLite Backend<br>
      <div style="color:#00ccff60;">▸</div> Python Scoring Engine<br>
      <div style="color:#f0c04060;">▸</div> Plotly Visualizations<br>
    </div>
    <div style="margin-top:12px; font-size:9px; color:#374151; letter-spacing:2px; text-align:center;">
      DEVELOPED BY MOHAN<br>NSTI CHENNAI · 2026
    </div>
    """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# PAGE 1 — DASHBOARD
# ═══════════════════════════════════════════════════════════════
if page == "🏠  Dashboard":
    st.markdown("""
    <div class="glow-title">⚡ PASHUSCORE COMMAND CENTER</div>
    <div class="subtitle">Real-time cattle credit intelligence across all registered farmers</div>
    <div class="neon-line"></div>
    """, unsafe_allow_html=True)

    farmers_base = run_query("SELECT farmer_id, name, village, state FROM farmers ORDER BY name")
    dashboard_rows = []
    if not farmers_base.empty:
        for _, row in farmers_base.iterrows():
            s = compute_score(row["farmer_id"])
            dashboard_rows.append({
                "farmer_id": row["farmer_id"], "name": row["name"],
                "village": row["village"], "state": row["state"],
                "credit_score": s["total"] if s else 0,
                "herd_size": s["n"] if s else 0,
                "grade": s["grade"] if s else "D"
            })

    df_all = pd.DataFrame(dashboard_rows)
    if not df_all.empty:
        df_all = df_all.sort_values("credit_score", ascending=False)

    total_cattle = run_query("SELECT COUNT(*) AS n FROM cattle WHERE health_status != 'Deceased'")
    overdue_vacc = run_query("SELECT COUNT(DISTINCT cattle_id) AS n FROM vaccinations WHERE DATE(next_due) < DATE('now')")
    pending_apps = run_query("SELECT COUNT(*) AS n FROM loan_applications WHERE status = 'Pending'")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("TOTAL FARMERS",  len(df_all))
    c2.metric("ACTIVE CATTLE",  int(total_cattle["n"].iloc[0]) if not total_cattle.empty else 0)
    c3.metric("VACC OVERDUE",   int(overdue_vacc["n"].iloc[0]) if not overdue_vacc.empty else 0)
    c4.metric("PENDING LOANS",  int(pending_apps["n"].iloc[0]) if not pending_apps.empty else 0)

    st.markdown("<div class='neon-line'></div>", unsafe_allow_html=True)
    col1, col2 = st.columns([1.6, 1])

    with col1:
        st.markdown("""<div style="font-family:'Rajdhani',sans-serif; font-size:16px;
            color:#00ff88; letter-spacing:2px; margin-bottom:12px;">
            🏆 FARMER LEADERBOARD</div>""", unsafe_allow_html=True)
        if not df_all.empty:
            grade_colors = {"A+": "🟢", "A": "🟢", "B": "🟡", "C": "🟠", "D": "🔴"}
            df_disp = df_all.copy()
            df_disp["grade"] = df_disp["grade"].map(lambda g: f"{grade_colors.get(g,'⚪')} {g}")
            st.dataframe(
                df_disp[["name","village","state","herd_size","credit_score","grade"]].rename(columns={
                    "name":"Farmer","village":"Village","state":"State",
                    "herd_size":"Herd","credit_score":"Score","grade":"Grade"}),
                use_container_width=True, hide_index=True
            )

    with col2:
        st.markdown("""<div style="font-family:'Rajdhani',sans-serif; font-size:16px;
            color:#00ccff; letter-spacing:2px; margin-bottom:12px;">
            📊 GRADE DISTRIBUTION</div>""", unsafe_allow_html=True)
        if not df_all.empty:
            grade_counts = df_all["grade"].value_counts().reset_index()
            grade_counts.columns = ["Grade", "Count"]
            color_map = {"A+":"#00ff88","A":"#00ccff","B":"#f0c040","C":"#ff8800","D":"#ff4444"}
            fig_pie = px.pie(grade_counts, names="Grade", values="Count",
                             color="Grade", color_discrete_map=color_map, hole=0.6)
            fig_pie.update_layout(
                paper_bgcolor="#111827", plot_bgcolor="#111827",
                legend=dict(font=dict(color="#9ca3af", size=12)),
                height=300, margin=dict(t=10,b=10,l=10,r=10)
            )
            fig_pie.update_traces(textfont_color="#030712",
                                  marker=dict(line=dict(color="#0d1117", width=2)))
            st.plotly_chart(fig_pie, use_container_width=True)

# ═══════════════════════════════════════════════════════════════
# PAGE 2 — SCORE A FARMER
# ═══════════════════════════════════════════════════════════════
elif page == "📊  Score a Farmer":
    st.markdown("""
    <div class="glow-title">📊 CREDIT SCORE ENGINE</div>
    <div class="subtitle">AI-powered cattle-backed credit assessment</div>
    <div class="neon-line"></div>
    """, unsafe_allow_html=True)

    farmers_df = run_query("SELECT farmer_id, name, village FROM farmers ORDER BY name")
    if farmers_df.empty:
        st.warning("No farmers in database.")
    else:
        options = {f"{r['name']} — {r['village']}": r["farmer_id"] for _, r in farmers_df.iterrows()}
        col_sel, col_btn = st.columns([3, 1])
        with col_sel:
            selected_label = st.selectbox("Select Farmer", list(options.keys()),
                                          label_visibility="collapsed")
        with col_btn:
            compute_clicked = st.button("⚡ COMPUTE SCORE", type="primary", use_container_width=True)

        farmer_id = options[selected_label]

        if compute_clicked:
            with st.spinner("Analysing herd data..."):
                result = compute_score(farmer_id)
                farmer_info = run_query("SELECT * FROM farmers WHERE farmer_id = ?", (farmer_id,))
            if result is None:
                st.session_state["score_result"] = None
                st.session_state["score_farmer_id"] = None
                st.session_state["score_farmer_info"] = None
                st.error("No active cattle found for this farmer.")
            else:
                st.session_state["score_result"] = result
                st.session_state["score_farmer_id"] = farmer_id
                st.session_state["score_farmer_info"] = farmer_info

        result          = st.session_state.get("score_result")
        farmer_info     = st.session_state.get("score_farmer_info")
        scored_farmer_id = st.session_state.get("score_farmer_id")

        if result is not None and scored_farmer_id == farmer_id:
            st.markdown("<div class='neon-line'></div>", unsafe_allow_html=True)
            col1, col2 = st.columns([1, 1.6])

            with col1:
                st.plotly_chart(gauge_chart(result["total"], result["color"]),
                                use_container_width=True)
                # Grade card
                st.markdown(f"""
                <div style="background:linear-gradient(135deg,{result['color']}15,{result['color']}08);
                     border:1px solid {result['color']}40; border-radius:16px;
                     padding:20px; text-align:center; position:relative; overflow:hidden;">
                  <div style="position:absolute;top:0;left:0;right:0;height:2px;
                       background:linear-gradient(90deg,transparent,{result['color']},transparent);"></div>
                  <div style="font-family:'Rajdhani',sans-serif; font-size:52px;
                       font-weight:700; color:{result['color']};
                       text-shadow:0 0 30px {result['color']}80; line-height:1;">
                    {result['grade']}
                  </div>
                  <div style="font-size:10px; letter-spacing:3px; color:#6b7280;
                       text-transform:uppercase; margin:4px 0;">CREDIT GRADE</div>
                  <div style="font-size:22px; color:{result['color']}; font-family:'Rajdhani',sans-serif;
                       font-weight:600; margin-top:8px;">
                    ₹{result['amount']:,}
                  </div>
                  <div style="font-size:11px; color:#6b7280; margin-top:2px;">
                    @ {result['rate']}% per annum
                  </div>
                </div>
                """, unsafe_allow_html=True)

                if farmer_info is not None and not farmer_info.empty:
                    fi = farmer_info.iloc[0]
                    st.markdown(f"""
                    <div style="margin-top:12px; background:#111827; border:1px solid #1f2937;
                         border-radius:12px; padding:14px;">
                      <div style="font-size:10px; letter-spacing:2px; color:#6b7280;
                           text-transform:uppercase; margin-bottom:8px;">FARMER PROFILE</div>
                      <div style="display:flex; justify-content:space-between; margin-bottom:6px;">
                        <span style="color:#9ca3af; font-size:12px;">📍 Village</span>
                        <span style="color:#e2e8f0; font-size:12px; font-weight:500;">
                          {fi['village']}, {fi['state']}</span>
                      </div>
                      <div style="display:flex; justify-content:space-between; margin-bottom:6px;">
                        <span style="color:#9ca3af; font-size:12px;">🌾 Land</span>
                        <span style="color:#e2e8f0; font-size:12px;">{fi['land_acres']} acres</span>
                      </div>
                      <div style="display:flex; justify-content:space-between;">
                        <span style="color:#9ca3af; font-size:12px;">🐄 Animals</span>
                        <span style="color:#00ff88; font-size:12px; font-weight:600;">{result['n']} active</span>
                      </div>
                    </div>
                    """, unsafe_allow_html=True)

            with col2:
                st.markdown("""<div style="font-family:'Rajdhani',sans-serif; font-size:15px;
                    color:#00ccff; letter-spacing:2px; margin-bottom:8px;">
                    SCORE BREAKDOWN</div>""", unsafe_allow_html=True)
                st.plotly_chart(breakdown_chart(result["breakdown"]),
                                use_container_width=True)

                # Score component pills
                pills_html = '<div style="display:flex; gap:8px; flex-wrap:wrap; margin-bottom:16px;">'
                for label, (score, max_val, detail) in result["breakdown"].items():
                    pct = score / max_val
                    c = "#00ff88" if pct >= 0.8 else "#00ccff" if pct >= 0.6 else "#f0c040" if pct >= 0.4 else "#ff8800"
                    pills_html += f"""<div style="background:{c}15; border:1px solid {c}40;
                        border-radius:8px; padding:6px 12px; font-size:11px; color:{c};">
                        <b>{score}/{max_val}</b> {label}</div>"""
                pills_html += '</div>'
                st.markdown(pills_html, unsafe_allow_html=True)

                st.markdown("""<div style="font-family:'Rajdhani',sans-serif; font-size:15px;
                    color:#00ccff; letter-spacing:2px; margin-bottom:8px;">
                    HERD DETAILS</div>""", unsafe_allow_html=True)
                df_c = result["cattle_df"].copy()
                df_c["Vaccinated"] = df_c["vaccinated"].map(lambda v: "✅ Yes" if v else "❌ No")
                df_c["Health"] = df_c["health_status"].map(lambda h: {
                    "Healthy":"🟢 Healthy","Mild Fever":"🟡 Mild Fever",
                    "Limping":"🟠 Limping","Critical":"🔴 Critical"}.get(h, h))
                st.dataframe(
                    df_c[["cattle_id","breed","age_years","Health","Vaccinated","milk_yield_lpd"]].rename(columns={
                        "cattle_id":"Tag","breed":"Breed","age_years":"Age",
                        "milk_yield_lpd":"Yield L/day"}),
                    use_container_width=True, hide_index=True
                )

                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("🏦 SUBMIT LOAN APPLICATION", use_container_width=True, type="primary"):
                    existing = run_query(
                        "SELECT app_id FROM loan_applications WHERE farmer_id=? AND status='Pending'",
                        (farmer_id,))
                    if not existing.empty:
                        st.warning(f"⚠️ Pending application already exists — App #{existing['app_id'].iloc[0]}")
                    else:
                        lid = execute("""INSERT INTO loan_applications
                            (farmer_id,credit_score,grade,amount_eligible,status)
                            VALUES (?,?,?,?,'Pending')""",
                            (farmer_id, result["total"], result["grade"], result["amount"]))
                        if lid is not None:
                            st.success(f"✅ Application #{lid} submitted! Check 🏦 Loan Applications.")
                            st.session_state["score_result"] = None

# ═══════════════════════════════════════════════════════════════
# PAGE 3 — VILLAGE BATCH SCORE
# ═══════════════════════════════════════════════════════════════
elif page == "🌾  Village Batch Score":
    st.markdown("""
    <div class="glow-title">🌾 VILLAGE BATCH SCORING</div>
    <div class="subtitle">Score every farmer in a village simultaneously</div>
    <div class="neon-line"></div>
    """, unsafe_allow_html=True)

    villages = run_query("SELECT DISTINCT village FROM farmers ORDER BY village")
    village_list = villages["village"].tolist() if not villages.empty else []

    col_v, col_b = st.columns([3, 1])
    with col_v:
        village = st.selectbox("Select Village", village_list,
                               label_visibility="collapsed")
    with col_b:
        run_batch = st.button("🚀 RUN BATCH", type="primary", use_container_width=True)

    if village and run_batch:
        farmers_in_village = run_query(
            "SELECT farmer_id, name FROM farmers WHERE village = ?", (village,))
        if farmers_in_village.empty:
            st.warning("No farmers found.")
        else:
            results = []
            prog = st.progress(0, text="Initialising...")
            for i, (_, row) in enumerate(farmers_in_village.iterrows()):
                s = compute_score(row["farmer_id"])
                if s:
                    results.append({"Farmer": row["name"], "Score": s["total"],
                                    "Grade": s["grade"], "Max Loan": f"₹{s['amount']:,}",
                                    "Rate": f"{s['rate']}%", "Herd": s["n"]})
                prog.progress((i+1)/len(farmers_in_village), text=f"Scoring {row['name']}...")
            prog.empty()

            if results:
                df_res = pd.DataFrame(results).sort_values("Score", ascending=False)
                st.markdown("<div class='neon-line'></div>", unsafe_allow_html=True)

                c1, c2, c3 = st.columns(3)
                eligible = df_res[df_res["Grade"].isin(["A+","A","B"])].shape[0]
                c1.metric("LOAN ELIGIBLE", eligible)
                c2.metric("AVG SCORE", f"{df_res['Score'].mean():.1f}")
                c3.metric("TOP SCORE", df_res["Score"].max())

                st.dataframe(df_res, use_container_width=True, hide_index=True)

                color_map = {"A+":"#00ff88","A":"#00ccff","B":"#f0c040","C":"#ff8800","D":"#ff4444"}
                fig = px.bar(df_res, x="Farmer", y="Score", color="Grade",
                             color_discrete_map=color_map,
                             title=f"Credit Scores — {village}")
                fig.update_layout(paper_bgcolor="#111827", plot_bgcolor="#111827",
                                  font=dict(color="#9ca3af"),
                                  title_font=dict(color="#00ff88", family="Rajdhani", size=16))
                st.plotly_chart(fig, use_container_width=True)

# ═══════════════════════════════════════════════════════════════
# PAGE 4 — CATTLE REGISTRY
# ═══════════════════════════════════════════════════════════════
elif page == "🐄  Cattle Registry":
    st.markdown("""
    <div class="glow-title">🐄 CATTLE REGISTRY</div>
    <div class="subtitle">Complete herd database with health and vaccination status</div>
    <div class="neon-line"></div>
    """, unsafe_allow_html=True)

    df = run_query("""
        SELECT c.cattle_id, f.name AS farmer, f.village, c.breed,
               c.age_years, c.health_status, c.milk_yield_lpd, c.ear_tag,
               CASE WHEN v.cattle_id IS NOT NULL THEN '✅ Vaccinated' ELSE '❌ Pending' END AS vacc_status
        FROM cattle c
        JOIN farmers f ON c.farmer_id = f.farmer_id
        LEFT JOIN vaccinations v ON c.cattle_id = v.cattle_id AND DATE(v.next_due) >= DATE('now')
        ORDER BY f.name, c.breed
    """)

    if not df.empty:
        f1, f2 = st.columns(2)
        with f1:
            breed_filter = st.multiselect("Filter Breed", sorted(df["breed"].unique()))
        with f2:
            health_filter = st.multiselect("Filter Health", sorted(df["health_status"].unique()))
        if breed_filter:  df = df[df["breed"].isin(breed_filter)]
        if health_filter: df = df[df["health_status"].isin(health_filter)]

        st.dataframe(df, use_container_width=True, hide_index=True)
        st.markdown(f"""<div style="font-size:11px; color:#6b7280; letter-spacing:1px;
            margin-top:4px;">{len(df)} animals displayed</div>""", unsafe_allow_html=True)

        st.markdown("<div class='neon-line'></div>", unsafe_allow_html=True)
        st.markdown("""<div style="font-family:'Rajdhani',sans-serif; font-size:15px;
            color:#00ccff; letter-spacing:2px; margin-bottom:12px;">
            UPDATE HEALTH STATUS</div>""", unsafe_allow_html=True)
        uc1, uc2, uc3 = st.columns(3)
        with uc1:
            cattle_id = st.selectbox("Cattle ID", df["cattle_id"].tolist())
        with uc2:
            new_health = st.selectbox("New Status",
                ["Healthy","Mild Fever","Limping","Critical","Deceased"])
        with uc3:
            st.write(""); st.write("")
            if st.button("⚡ UPDATE", use_container_width=True):
                execute("UPDATE cattle SET health_status=? WHERE cattle_id=?", (new_health, cattle_id))
                st.success(f"Updated {cattle_id} → {new_health}")
                st.rerun()
    else:
        st.info("No cattle records found.")

# ═══════════════════════════════════════════════════════════════
# PAGE 5 — VACCINATION ALERTS
# ═══════════════════════════════════════════════════════════════
elif page == "💉  Vaccination Alerts":
    st.markdown("""
    <div class="glow-title">💉 VACCINATION ALERTS</div>
    <div class="subtitle">Overdue vaccination monitoring and alert system</div>
    <div class="neon-line"></div>
    """, unsafe_allow_html=True)

    df = run_query("""
        SELECT c.cattle_id, c.ear_tag, c.breed,
               f.name AS farmer, f.phone, f.village,
               v.vaccine, v.next_due,
               CAST((julianday('now') - julianday(v.next_due)) AS INTEGER) AS days_overdue
        FROM vaccinations v
        JOIN cattle c ON v.cattle_id = c.cattle_id
        JOIN farmers f ON c.farmer_id = f.farmer_id
        WHERE DATE(v.next_due) < DATE('now')
        ORDER BY days_overdue DESC
    """)

    if df.empty:
        st.markdown("""
        <div style="background:#00ff8810; border:1px solid #00ff8830; border-radius:16px;
             padding:32px; text-align:center; margin:20px 0;">
          <div style="font-size:48px;">✅</div>
          <div style="font-family:'Rajdhani',sans-serif; font-size:20px; color:#00ff88;
               letter-spacing:2px; margin-top:8px;">ALL CLEAR</div>
          <div style="color:#6b7280; font-size:13px; margin-top:4px;">All vaccinations up to date</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        def severity(d):
            if d > 180: return "🔴 Critical"
            if d > 90:  return "🟠 High"
            return "🟡 Moderate"
        df["Severity"] = df["days_overdue"].apply(severity)

        c1, c2, c3 = st.columns(3)
        c1.metric("TOTAL OVERDUE", len(df))
        c2.metric("CRITICAL (180d+)", len(df[df["days_overdue"]>180]))
        c3.metric("HIGH (90d+)", len(df[df["days_overdue"]>90]))

        st.dataframe(df.rename(columns={
            "cattle_id":"Cattle","ear_tag":"Tag","breed":"Breed","farmer":"Farmer",
            "phone":"Phone","village":"Village","vaccine":"Vaccine",
            "next_due":"Due","days_overdue":"Days Overdue"}),
            use_container_width=True, hide_index=True)

        fig = px.bar(df.head(10), x="cattle_id", y="days_overdue", color="Severity",
                     color_discrete_map={"🔴 Critical":"#ff4444","🟠 High":"#ff8800","🟡 Moderate":"#f0c040"},
                     title="Top 10 Most Overdue")
        fig.update_layout(paper_bgcolor="#111827", plot_bgcolor="#111827",
                          font=dict(color="#9ca3af"),
                          title_font=dict(color="#ff4444", family="Rajdhani", size=16))
        st.plotly_chart(fig, use_container_width=True)

# ═══════════════════════════════════════════════════════════════
# PAGE 6 — LOAN APPLICATIONS
# ═══════════════════════════════════════════════════════════════
elif page == "🏦  Loan Applications":
    st.markdown("""
    <div class="glow-title">🏦 LOAN APPLICATIONS</div>
    <div class="subtitle">Application pipeline management and approval system</div>
    <div class="neon-line"></div>
    """, unsafe_allow_html=True)

    df = run_query("""
        SELECT la.app_id, f.name, f.village, f.state,
               la.credit_score, la.grade, la.amount_eligible,
               la.status, la.applied_on
        FROM loan_applications la
        JOIN farmers f ON la.farmer_id = f.farmer_id
        ORDER BY la.applied_on DESC, la.app_id DESC
    """)

    if df.empty:
        st.info("No loan applications yet. Score a farmer and apply.")
    else:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("TOTAL APPS",     len(df))
        c2.metric("APPROVED",       len(df[df["status"]=="Approved"]))
        c3.metric("PENDING",        len(df[df["status"]=="Pending"]))
        c4.metric("REJECTED",       len(df[df["status"]=="Rejected"]))

        st.markdown("<div class='neon-line'></div>", unsafe_allow_html=True)

        # Status filter
        status_filter = st.selectbox("Filter", ["All","Pending","Approved","Rejected"],
                                     label_visibility="collapsed")
        dfd = df if status_filter == "All" else df[df["status"]==status_filter]

        # Style status column
        def fmt_status(s):
            if s == "Approved": return "✅ Approved"
            if s == "Pending":  return "⏳ Pending"
            return "❌ Rejected"
        dfd = dfd.copy()
        dfd["status"] = dfd["status"].apply(fmt_status)

        st.dataframe(dfd.rename(columns={
            "app_id":"App #","name":"Farmer","village":"Village","state":"State",
            "credit_score":"Score","grade":"Grade","amount_eligible":"Eligible ₹",
            "status":"Status","applied_on":"Applied On"}),
            use_container_width=True, hide_index=True)

        pending_df = df[df["status"]=="Pending"]
        if not pending_df.empty:
            st.markdown("<div class='neon-line'></div>", unsafe_allow_html=True)
            st.markdown("""<div style="font-family:'Rajdhani',sans-serif; font-size:15px;
                color:#f0c040; letter-spacing:2px; margin-bottom:12px;">
                QUICK DECISION</div>""", unsafe_allow_html=True)
            dc1, dc2, dc3 = st.columns(3)
            with dc1:
                sel_app = st.selectbox("Pending App #", pending_df["app_id"].tolist())
            with dc2:
                st.write(""); st.write("")
                if st.button("✅ APPROVE", use_container_width=True, type="primary"):
                    execute("UPDATE loan_applications SET status='Approved' WHERE app_id=?", (sel_app,))
                    st.success(f"App #{sel_app} Approved!")
                    st.rerun()
            with dc3:
                st.write(""); st.write("")
                if st.button("❌ REJECT", use_container_width=True):
                    execute("UPDATE loan_applications SET status='Rejected' WHERE app_id=?", (sel_app,))
                    st.warning(f"App #{sel_app} Rejected.")
                    st.rerun()

# ═══════════════════════════════════════════════════════════════
# PAGE 7 — ADD FARMER / CATTLE
# ═══════════════════════════════════════════════════════════════
elif page == "➕  Add Farmer / Cattle":
    st.markdown("""
    <div class="glow-title">➕ REGISTER NEW RECORDS</div>
    <div class="subtitle">Add farmers, cattle, and vaccination records</div>
    <div class="neon-line"></div>
    """, unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["🧑‍🌾  New Farmer", "🐄  New Cattle", "💉  Add Vaccination"])

    with tab1:
        with st.form("add_farmer"):
            c1, c2 = st.columns(2)
            farmer_id = c1.text_input("Farmer ID", placeholder="e.g. F005")
            name      = c2.text_input("Full Name")
            village   = c1.text_input("Village")
            state     = c2.text_input("State")
            land      = c1.number_input("Land (acres)", 0.0, 100.0, 1.0, 0.1)
            phone     = c2.text_input("Phone")
            submitted = st.form_submit_button("⚡ REGISTER FARMER", use_container_width=True)
            if submitted:
                if not all([farmer_id, name, village, state]):
                    st.error("Please fill all required fields.")
                else:
                    execute("INSERT INTO farmers (farmer_id,name,village,state,land_acres,phone) VALUES (?,?,?,?,?,?)",
                            (farmer_id, name, village, state, land, phone))
                    st.success(f"✅ {name} registered as {farmer_id}")

    with tab2:
        farmers_df = run_query("SELECT farmer_id, name FROM farmers ORDER BY name")
        farmer_map = {f"{r['name']} ({r['farmer_id']})": r["farmer_id"]
                      for _, r in farmers_df.iterrows()} if not farmers_df.empty else {}
        with st.form("add_cattle"):
            c1, c2 = st.columns(2)
            farmer_sel = c1.selectbox("Farmer", list(farmer_map.keys()) if farmer_map else [])
            cattle_id  = c2.text_input("Cattle ID", placeholder="e.g. C15")
            breed      = c1.selectbox("Breed", list(BREED_WEIGHTS.keys()))
            age        = c2.number_input("Age (years)", 1, 20, 3)
            yield_lpd  = c1.number_input("Milk Yield (L/day)", 0.0, 50.0, 5.0, 0.5)
            ear_tag    = c2.text_input("Ear Tag")
            submitted  = st.form_submit_button("⚡ REGISTER CATTLE", use_container_width=True)
            if submitted and farmer_sel:
                fid = farmer_map.get(farmer_sel, "")
                execute("INSERT INTO cattle (cattle_id,farmer_id,breed,age_years,health_status,milk_yield_lpd,ear_tag) VALUES (?,?,?,?,'Healthy',?,?)",
                        (cattle_id, fid, breed, age, yield_lpd, ear_tag))
                st.success(f"✅ {cattle_id} ({breed}) registered under {farmer_sel}")

    with tab3:
        all_cattle = run_query("SELECT cattle_id FROM cattle WHERE health_status != 'Deceased'")
        with st.form("add_vacc"):
            c1, c2 = st.columns(2)
            cid     = c1.selectbox("Cattle ID", all_cattle["cattle_id"].tolist() if not all_cattle.empty else [])
            vaccine = c2.text_input("Vaccine", placeholder="e.g. FMD + HS")
            given   = c1.date_input("Date Given", value=date.today())
            due     = c2.date_input("Next Due Date")
            vet     = c1.text_input("Vet Name")
            submitted = st.form_submit_button("⚡ ADD RECORD", use_container_width=True)
            if submitted and cid:
                execute("INSERT INTO vaccinations (cattle_id,vaccine,given_on,next_due,vet_name) VALUES (?,?,?,?,?)",
                        (cid, vaccine, str(given), str(due), vet))
                st.success(f"✅ Vaccination recorded for {cid}")
