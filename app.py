import streamlit as st
import sqlite3
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import date
from pathlib import Path

# ── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="PashuScore",
    page_icon="🐄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Custom CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=Source+Sans+3:wght@400;600&display=swap');

html, body, [class*="css"] { font-family: 'Source Sans 3', sans-serif; }
.main { background-color: #0f0e0c; }

.section-label {
    font-size: 11px;
    letter-spacing: 3px;
    text-transform: uppercase;
    color: #7a6030;
    margin-bottom: 8px;
}

.stTabs [data-baseweb="tab-list"] {
    background-color: #18150e;
    border-radius: 10px;
}
.stTabs [data-baseweb="tab"] {
    color: #7a6030;
}
.stTabs [aria-selected="true"] {
    color: #f0c040 !important;
    background-color: #2c1f0a !important;
    border-radius: 8px;
}
div[data-testid="stMetricValue"] { font-size: 28px; color: #f0c040; }
div[data-testid="stMetricLabel"] { color: #7a6030; font-size: 12px; }
</style>
""", unsafe_allow_html=True)

# ── Database File ────────────────────────────────────────────────────────────
DB_FILE = Path("pashuscore.db")

BREED_WEIGHTS = {
    "Gir": 30, "Sahiwal": 28, "Red Sindhi": 26,
    "Murrah Buffalo": 27, "Surti Buffalo": 24,
    "HF Cross": 22, "Jersey Cross": 20, "Nondescript": 10,
}

GRADE_TABLE = [
    (80, "A+", 200000, 7.0,  "#2d7a2d"),
    (65, "A",  150000, 9.0,  "#4a9e4a"),
    (50, "B",   75000, 12.0, "#d4a017"),
    (35, "C",   25000, 16.0, "#cc6600"),
    (0,  "D",       0,  0.0, "#c0392b"),
]

# ── SQLite Setup ─────────────────────────────────────────────────────────────
def init_db():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS farmers (
            farmer_id   TEXT PRIMARY KEY,
            name        TEXT NOT NULL,
            village     TEXT NOT NULL,
            state       TEXT NOT NULL,
            land_acres  REAL,
            phone       TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS cattle (
            cattle_id       TEXT PRIMARY KEY,
            farmer_id       TEXT NOT NULL,
            breed           TEXT NOT NULL,
            age_years       INTEGER,
            health_status   TEXT DEFAULT 'Healthy',
            milk_yield_lpd  REAL,
            ear_tag         TEXT,
            FOREIGN KEY (farmer_id) REFERENCES farmers(farmer_id)
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS vaccinations (
            vacc_id      INTEGER PRIMARY KEY AUTOINCREMENT,
            cattle_id    TEXT NOT NULL,
            vaccine      TEXT,
            given_on     TEXT,
            next_due     TEXT,
            vet_name     TEXT,
            FOREIGN KEY (cattle_id) REFERENCES cattle(cattle_id)
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS loan_applications (
            app_id            INTEGER PRIMARY KEY AUTOINCREMENT,
            farmer_id         TEXT NOT NULL,
            credit_score      INTEGER,
            grade             TEXT,
            amount_eligible   REAL,
            status            TEXT DEFAULT 'Pending',
            applied_on        TEXT DEFAULT (DATE('now')),
            FOREIGN KEY (farmer_id) REFERENCES farmers(farmer_id)
        )
    """)

    # Insert sample data only if empty
    cur.execute("SELECT COUNT(*) FROM farmers")
    if cur.fetchone()[0] == 0:
        cur.executemany("""
            INSERT INTO farmers (farmer_id, name, village, state, land_acres, phone)
            VALUES (?, ?, ?, ?, ?, ?)
        """, [
            ('F001', 'Ramaiah Gowda', 'Hosakere', 'Karnataka', 3.50, '9845001234'),
            ('F002', 'Sunita Devi', 'Barhaj', 'Uttar Pradesh', 1.20, '9012002345'),
            ('F003', 'Murugesan P.', 'Palani', 'Tamil Nadu', 0.80, '8023003456'),
            ('F004', 'Harpreet Kaur', 'Barnala', 'Punjab', 6.00, '9779004567'),
        ])

        cur.executemany("""
            INSERT INTO cattle (cattle_id, farmer_id, breed, age_years, health_status, milk_yield_lpd, ear_tag)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, [
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

        cur.executemany("""
            INSERT INTO vaccinations (cattle_id, vaccine, given_on, next_due, vet_name)
            VALUES (?, ?, ?, ?, ?)
        """, [
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

        cur.executemany("""
            INSERT INTO loan_applications (farmer_id, credit_score, grade, amount_eligible, status)
            VALUES (?, ?, ?, ?, ?)
        """, [
            ('F004', 88, 'A+', 200000, 'Approved'),
            ('F001', 76, 'A', 150000, 'Pending'),
        ])

    conn.commit()
    conn.close()

init_db()

# ── Helpers ──────────────────────────────────────────────────────────────────
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
        cur.close()
        conn.close()
        return lid
    except Exception as e:
        st.error(f"DB Error: {e}")
        return None

def compute_score(farmer_id):
    df = run_query("""
        SELECT c.cattle_id, c.breed, c.age_years,
               c.health_status, c.milk_yield_lpd,
               CASE WHEN v.cattle_id IS NOT NULL THEN 1 ELSE 0 END AS vaccinated
        FROM cattle c
        LEFT JOIN vaccinations v
               ON c.cattle_id = v.cattle_id AND DATE(v.next_due) >= DATE('now')
        WHERE c.farmer_id = ? AND c.health_status != 'Deceased'
    """, (farmer_id,))

    if df.empty:
        return None

    n = len(df)
    herd_score = min(n * 5, 20)
    breed_avg = df["breed"].map(BREED_WEIGHTS).fillna(10).mean()
    breed_score = round(breed_avg)
    vacc_count = int(df["vaccinated"].sum())
    vacc_score = round((vacc_count / n) * 25)
    healthy_count = int((df["health_status"] == "Healthy").sum())
    health_score = round((healthy_count / n) * 15)
    high_yield = int((df["milk_yield_lpd"] >= 8).sum())
    yield_score = round((high_yield / n) * 10)
    total = herd_score + breed_score + vacc_score + health_score + yield_score

    grade, amount, rate, color = "D", 0, 0.0, "#c0392b"
    for threshold, g, a, r, c in GRADE_TABLE:
        if total >= threshold:
            grade, amount, rate, color = g, a, r, c
            break

    return {
        "total": total,
        "grade": grade,
        "amount": amount,
        "rate": rate,
        "color": color,
        "n": n,
        "breakdown": {
            "Herd Size": (herd_score, 20, f"{n} animals"),
            "Breed Quality": (breed_score, 30, f"Avg {breed_avg:.1f}"),
            "Vaccination": (vacc_score, 25, f"{vacc_count}/{n} vaccinated"),
            "Health": (health_score, 15, f"{healthy_count}/{n} healthy"),
            "Milk Yield": (yield_score, 10, f"{high_yield} high-yield"),
        },
        "cattle_df": df,
    }

def gauge_chart(score, color):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        domain={"x": [0, 1], "y": [0, 1]},
        gauge={
            "axis": {"range": [0, 100], "tickcolor": "#5a4a28"},
            "bar": {"color": color, "thickness": 0.25},
            "bgcolor": "#18150e",
            "bordercolor": "#3a2e18",
            "steps": [
                {"range": [0, 35], "color": "#1a0a0a"},
                {"range": [35, 50], "color": "#1a1008"},
                {"range": [50, 65], "color": "#1a1508"},
                {"range": [65, 80], "color": "#0f1a0f"},
                {"range": [80, 100], "color": "#0a1a0a"},
            ],
        },
        number={"font": {"color": "#f0c040", "size": 48}, "suffix": "/100"},
        title={"text": "Credit Score", "font": {"color": "#7a6030", "size": 13}}
    ))
    fig.update_layout(
        paper_bgcolor="#0f0e0c",
        plot_bgcolor="#0f0e0c",
        height=260,
        margin=dict(t=30, b=10, l=30, r=30)
    )
    return fig

def breakdown_chart(breakdown):
    labels = list(breakdown.keys())
    scores = [v[0] for v in breakdown.values()]
    maxes = [v[1] for v in breakdown.values()]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=labels,
        x=maxes,
        orientation="h",
        marker_color="#1e1a10",
        showlegend=False
    ))
    fig.add_trace(go.Bar(
        y=labels,
        x=scores,
        orientation="h",
        marker=dict(color=["#f0c040"] * len(scores)),
        showlegend=False,
        text=[f"{s}/{m}" for s, m in zip(scores, maxes)],
        textposition="inside"
    ))
    fig.update_layout(
        barmode="overlay",
        paper_bgcolor="#18150e",
        plot_bgcolor="#18150e",
        xaxis=dict(showgrid=False, zeroline=False, color="#5a4a28"),
        yaxis=dict(color="#c0a060"),
        height=220,
        margin=dict(t=10, b=10, l=10, r=10)
    )
    return fig

# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🐄 PashuScore")
    st.markdown("<div class='section-label'>Cattle-Backed Credit Intelligence</div>", unsafe_allow_html=True)
    st.divider()
    page = st.radio("Navigate", [
        "🏠 Dashboard",
        "📊 Score a Farmer",
        "🌾 Village Batch Score",
        "🐄 Cattle Registry",
        "💉 Vaccination Alerts",
        "🏦 Loan Applications",
        "➕ Add Farmer / Cattle",
    ])
    st.divider()
    st.caption("Developed by Mohan | NSTI Chennai")

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 1 — DASHBOARD
# ═══════════════════════════════════════════════════════════════════════════════
if page == "🏠 Dashboard":
    st.markdown("## 🐄 PashuScore — Cattle Credit Intelligence")
    st.markdown("<div class='section-label'>Real-time overview across all registered farmers</div>", unsafe_allow_html=True)
    st.divider()

    farmers_base = run_query("""
        SELECT farmer_id, name, village, state
        FROM farmers
        ORDER BY name
    """)

    dashboard_rows = []

    if not farmers_base.empty:
        for _, row in farmers_base.iterrows():
            score_data = compute_score(row["farmer_id"])
            if score_data:
                dashboard_rows.append({
                    "farmer_id": row["farmer_id"],
                    "name": row["name"],
                    "village": row["village"],
                    "state": row["state"],
                    "credit_score": score_data["total"],
                    "herd_size": score_data["n"],
                    "grade": score_data["grade"]
                })
            else:
                dashboard_rows.append({
                    "farmer_id": row["farmer_id"],
                    "name": row["name"],
                    "village": row["village"],
                    "state": row["state"],
                    "credit_score": 0,
                    "herd_size": 0,
                    "grade": "D"
                })

    df_all = pd.DataFrame(dashboard_rows)
    if not df_all.empty:
        df_all = df_all.sort_values("credit_score", ascending=False)

    total_cattle = run_query("SELECT COUNT(*) AS n FROM cattle WHERE health_status != 'Deceased'")
    overdue_vacc = run_query("SELECT COUNT(DISTINCT cattle_id) AS n FROM vaccinations WHERE DATE(next_due) < DATE('now')")
    pending_apps = run_query("SELECT COUNT(*) AS n FROM loan_applications WHERE status = 'Pending'")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Farmers", len(df_all))
    c2.metric("Active Cattle", int(total_cattle["n"].iloc[0]) if not total_cattle.empty else 0)
    c3.metric("Vacc Overdue", int(overdue_vacc["n"].iloc[0]) if not overdue_vacc.empty else 0)
    c4.metric("Pending Loans", int(pending_apps["n"].iloc[0]) if not pending_apps.empty else 0)

    st.divider()
    col1, col2 = st.columns([1.6, 1])

    with col1:
        st.markdown("#### 🏆 Farmer Leaderboard")
        if not df_all.empty:
            st.dataframe(
                df_all[["name", "village", "state", "herd_size", "credit_score", "grade"]].rename(columns={
                    "name": "Farmer",
                    "village": "Village",
                    "state": "State",
                    "herd_size": "Herd",
                    "credit_score": "Score",
                    "grade": "Grade"
                }),
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("No farmers found.")

    with col2:
        st.markdown("#### 📊 Grade Distribution")
        if not df_all.empty:
            grade_counts = df_all["grade"].value_counts().reset_index()
            grade_counts.columns = ["Grade", "Count"]
            fig_pie = px.pie(
                grade_counts,
                names="Grade",
                values="Count",
                hole=0.5
            )
            fig_pie.update_layout(
                paper_bgcolor="#18150e",
                plot_bgcolor="#18150e",
                height=280,
                margin=dict(t=10, b=10, l=10, r=10)
            )
            st.plotly_chart(fig_pie, use_container_width=True)

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 2 — SCORE A FARMER
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "📊 Score a Farmer":
    st.markdown("## 📊 Credit Score Engine")
    st.divider()

    farmers_df = run_query("SELECT farmer_id, name, village FROM farmers ORDER BY name")
    if farmers_df.empty:
        st.warning("No farmers in database.")
    else:
        options = {f"{r['name']} ({r['village']})": r["farmer_id"] for _, r in farmers_df.iterrows()}
        selected_label = st.selectbox("Select Farmer", list(options.keys()))
        farmer_id = options[selected_label]

        if st.button("🔍 Compute Score", type="primary", use_container_width=True):
            result = compute_score(farmer_id)
            farmer_info = run_query("SELECT * FROM farmers WHERE farmer_id = ?", (farmer_id,))

            if result is None:
                st.error("No active cattle found for this farmer.")
            else:
                st.divider()
                col1, col2 = st.columns([1, 1.6])

                with col1:
                    st.plotly_chart(gauge_chart(result["total"], result["color"]), use_container_width=True)

                    st.markdown(f"""
                    <div style="background:{result['color']}22; border:1px solid {result['color']}55;
                         border-radius:12px; padding:16px; text-align:center;">
                        <div style="font-size:42px; font-weight:bold; color:{result['color']}; font-family:Georgia">
                            Grade {result['grade']}
                        </div>
                        <div style="color:#c0a060; margin-top:6px;">
                            Max Loan: <b>₹{result['amount']:,}</b> @ <b>{result['rate']}%</b> p.a.
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                    if not farmer_info.empty:
                        fi = farmer_info.iloc[0]
                        st.markdown("---")
                        st.markdown(f"**Village:** {fi['village']}, {fi['state']}")
                        st.markdown(f"**Land:** {fi['land_acres']} acres | **Animals:** {result['n']}")

                with col2:
                    st.markdown("#### Score Breakdown")
                    st.plotly_chart(breakdown_chart(result["breakdown"]), use_container_width=True)

                    st.markdown("#### Herd Details")
                    df_c = result["cattle_df"].copy()
                    df_c["Vaccinated"] = df_c["vaccinated"].map(lambda v: "Yes" if v else "No")
                    st.dataframe(
                        df_c[["cattle_id", "breed", "age_years", "health_status", "Vaccinated", "milk_yield_lpd"]].rename(columns={
                            "cattle_id": "Tag",
                            "breed": "Breed",
                            "age_years": "Age",
                            "health_status": "Health",
                            "milk_yield_lpd": "Yield (L/day)"
                        }),
                        use_container_width=True,
                        hide_index=True
                    )

                    if st.button("📋 Submit Loan Application", use_container_width=True):
                        lid = execute("""
                            INSERT INTO loan_applications
                                (farmer_id, credit_score, grade, amount_eligible, status)
                            VALUES (?, ?, ?, ?, 'Pending')
                        """, (farmer_id, result["total"], result["grade"], result["amount"]))

                        if lid is not None:
                            st.success(f"Application #{lid} submitted! Status: Pending")

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 3 — VILLAGE BATCH SCORE
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "🌾 Village Batch Score":
    st.markdown("## 🌾 Village Batch Scoring")
    st.markdown("Score every farmer in a village at once.")
    st.divider()

    villages = run_query("SELECT DISTINCT village FROM farmers ORDER BY village")
    village_list = villages["village"].tolist() if not villages.empty else []
    village = st.selectbox("Select Village", village_list)

    if village and st.button("🚀 Run Batch Score", type="primary", use_container_width=True):
        farmers_in_village = run_query(
            "SELECT farmer_id, name FROM farmers WHERE village = ?", (village,)
        )
        if farmers_in_village.empty:
            st.warning("No farmers found.")
        else:
            results = []
            prog = st.progress(0, text="Scoring farmers...")
            for i, (_, row) in enumerate(farmers_in_village.iterrows()):
                s = compute_score(row["farmer_id"])
                if s:
                    results.append({
                        "Farmer": row["name"],
                        "Score": s["total"],
                        "Grade": s["grade"],
                        "Max Loan": f"₹{s['amount']:,}",
                        "Rate": f"{s['rate']}%",
                        "Herd": s["n"],
                    })
                prog.progress((i + 1) / len(farmers_in_village), text=f"Scored {row['name']}")

            prog.empty()

            if results:
                df_res = pd.DataFrame(results).sort_values("Score", ascending=False)
                st.success(f"Scored {len(df_res)} farmers in {village}")

                c1, c2, c3 = st.columns(3)
                eligible = df_res[df_res["Grade"].isin(["A+", "A", "B"])]["Max Loan"].count()
                c1.metric("Eligible for Loan", eligible)
                c2.metric("Avg Score", f"{df_res['Score'].mean():.1f}")
                c3.metric("Top Score", df_res["Score"].max())

                st.dataframe(df_res, use_container_width=True, hide_index=True)

                fig = px.bar(df_res, x="Farmer", y="Score", color="Grade", title=f"Credit Scores — {village}")
                fig.update_layout(paper_bgcolor="#18150e", plot_bgcolor="#18150e")
                st.plotly_chart(fig, use_container_width=True)

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 4 — CATTLE REGISTRY
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "🐄 Cattle Registry":
    st.markdown("## 🐄 Cattle Registry")
    st.divider()

    df = run_query("""
        SELECT c.cattle_id, f.name AS farmer, f.village,
               c.breed, c.age_years, c.health_status,
               c.milk_yield_lpd, c.ear_tag,
               CASE WHEN v.cattle_id IS NOT NULL THEN 'Vaccinated' ELSE 'Pending' END AS vacc_status
        FROM cattle c
        JOIN farmers f ON c.farmer_id = f.farmer_id
        LEFT JOIN vaccinations v ON c.cattle_id = v.cattle_id AND DATE(v.next_due) >= DATE('now')
        ORDER BY f.name, c.breed
    """)

    if not df.empty:
        st.dataframe(df, use_container_width=True, hide_index=True)

        st.divider()
        st.markdown("#### Update Health Status")
        uc1, uc2, uc3 = st.columns(3)
        with uc1:
            cattle_id = st.selectbox("Cattle ID", df["cattle_id"].tolist())
        with uc2:
            new_health = st.selectbox("New Status", ["Healthy", "Mild Fever", "Limping", "Critical", "Deceased"])
        with uc3:
            st.write("")
            st.write("")
            if st.button("✅ Update", use_container_width=True):
                execute("UPDATE cattle SET health_status = ? WHERE cattle_id = ?", (new_health, cattle_id))
                st.success(f"Updated {cattle_id} → {new_health}")
                st.rerun()
    else:
        st.info("No cattle records found.")

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 5 — VACCINATION ALERTS
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "💉 Vaccination Alerts":
    st.markdown("## 💉 Vaccination Overdue Alerts")
    st.divider()

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
        st.success("All vaccinations are up to date!")
    else:
        st.error(f"{len(df)} cattle have overdue vaccinations")
        st.dataframe(df, use_container_width=True, hide_index=True)

        fig = px.bar(df.head(10), x="cattle_id", y="days_overdue", title="Top 10 Most Overdue")
        fig.update_layout(paper_bgcolor="#18150e", plot_bgcolor="#18150e")
        st.plotly_chart(fig, use_container_width=True)

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 6 — LOAN APPLICATIONS
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "🏦 Loan Applications":
    st.markdown("## 🏦 Loan Applications")
    st.divider()

    df = run_query("""
        SELECT la.app_id, f.name, f.village, f.state,
               la.credit_score, la.grade,
               la.amount_eligible,
               la.status, la.applied_on
        FROM loan_applications la
        JOIN farmers f ON la.farmer_id = f.farmer_id
        ORDER BY la.applied_on DESC, la.app_id DESC
    """)

    if df.empty:
        st.info("No loan applications yet.")
    else:
        c1, c2, c3 = st.columns(3)
        c1.metric("Total Applications", len(df))
        c2.metric("Approved", len(df[df["status"] == "Approved"]))
        c3.metric("Pending Review", len(df[df["status"] == "Pending"]))

        st.dataframe(df, use_container_width=True, hide_index=True)

        pending_df = df[df["status"] == "Pending"]
        if not pending_df.empty:
            st.divider()
            st.markdown("#### Quick Decision")
            dc1, dc2, dc3 = st.columns(3)
            with dc1:
                sel_app = st.selectbox("Pending App #", pending_df["app_id"].tolist())
            with dc2:
                st.write("")
                st.write("")
                if st.button("✅ Approve", use_container_width=True):
                    execute("UPDATE loan_applications SET status='Approved' WHERE app_id=?", (sel_app,))
                    st.success(f"App #{sel_app} Approved!")
                    st.rerun()
            with dc3:
                st.write("")
                st.write("")
                if st.button("❌ Reject", use_container_width=True):
                    execute("UPDATE loan_applications SET status='Rejected' WHERE app_id=?", (sel_app,))
                    st.warning(f"App #{sel_app} Rejected.")
                    st.rerun()

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 7 — ADD FARMER / CATTLE
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "➕ Add Farmer / Cattle":
    st.markdown("## ➕ Register New Farmer / Cattle")
    st.divider()

    tab1, tab2, tab3 = st.tabs(["🧑‍🌾 New Farmer", "🐄 New Cattle", "💉 Add Vaccination"])

    with tab1:
        with st.form("add_farmer"):
            c1, c2 = st.columns(2)
            farmer_id = c1.text_input("Farmer ID (e.g. F005)")
            name = c2.text_input("Full Name")
            village = c1.text_input("Village")
            state = c2.text_input("State")
            land = c1.number_input("Land (acres)", 0.0, 100.0, 1.0, 0.1)
            phone = c2.text_input("Phone")
            submitted = st.form_submit_button("Register Farmer", use_container_width=True)

            if submitted:
                if not all([farmer_id, name, village, state]):
                    st.error("Please fill all required fields.")
                else:
                    execute("""
                        INSERT INTO farmers (farmer_id, name, village, state, land_acres, phone)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (farmer_id, name, village, state, land, phone))
                    st.success(f"Farmer {name} registered as {farmer_id}")

    with tab2:
        farmers_df = run_query("SELECT farmer_id, name FROM farmers ORDER BY name")
        farmer_map = {
            f"{r['name']} ({r['farmer_id']})": r["farmer_id"]
            for _, r in farmers_df.iterrows()
        } if not farmers_df.empty else {}

        with st.form("add_cattle"):
            c1, c2 = st.columns(2)
            farmer_sel = c1.selectbox("Farmer", list(farmer_map.keys()) if farmer_map else [])
            cattle_id = c2.text_input("Cattle ID (e.g. C15)")
            breed = c1.selectbox("Breed", list(BREED_WEIGHTS.keys()))
            age = c2.number_input("Age (years)", 1, 20, 3)
            yield_lpd = c1.number_input("Milk Yield (L/day)", 0.0, 50.0, 5.0, 0.5)
            ear_tag = c2.text_input("Ear Tag")
            submitted = st.form_submit_button("Register Cattle", use_container_width=True)

            if submitted and farmer_sel:
                fid = farmer_map.get(farmer_sel, "")
                execute("""
                    INSERT INTO cattle
                        (cattle_id, farmer_id, breed, age_years, health_status, milk_yield_lpd, ear_tag)
                    VALUES (?, ?, ?, ?, 'Healthy', ?, ?)
                """, (cattle_id, fid, breed, age, yield_lpd, ear_tag))
                st.success(f"Cattle {cattle_id} ({breed}) registered under {farmer_sel}")

    with tab3:
        all_cattle = run_query("SELECT cattle_id FROM cattle WHERE health_status != 'Deceased'")
        with st.form("add_vacc"):
            c1, c2 = st.columns(2)
            cid = c1.selectbox("Cattle ID", all_cattle["cattle_id"].tolist() if not all_cattle.empty else [])
            vaccine = c2.text_input("Vaccine Name (e.g. FMD + HS)")
            given = c1.date_input("Date Given", value=date.today())
            due = c2.date_input("Next Due Date")
            vet = c1.text_input("Vet Name")
            submitted = st.form_submit_button("Add Record", use_container_width=True)

            if submitted and cid:
                execute("""
                    INSERT INTO vaccinations (cattle_id, vaccine, given_on, next_due, vet_name)
                    VALUES (?, ?, ?, ?, ?)
                """, (cid, vaccine, str(given), str(due), vet))
                st.success(f"Vaccination recorded for {cid}")
