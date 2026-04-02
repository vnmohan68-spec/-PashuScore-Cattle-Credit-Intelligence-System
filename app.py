import streamlit as st
import mysql.connector
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import date
import os

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

.metric-card {
    background: linear-gradient(135deg, #1a1208, #2c1f0a);
    border: 1px solid #3a2e18;
    border-radius: 12px;
    padding: 20px;
    text-align: center;
}
.score-big {
    font-family: 'Playfair Display', serif;
    font-size: 64px;
    font-weight: 700;
    line-height: 1;
}
.grade-badge {
    display: inline-block;
    padding: 6px 20px;
    border-radius: 20px;
    font-size: 20px;
    font-weight: 700;
    margin: 8px 0;
}
.section-label {
    font-size: 11px;
    letter-spacing: 3px;
    text-transform: uppercase;
    color: #7a6030;
    margin-bottom: 8px;
}
.cattle-card {
    background: #18150e;
    border: 1px solid #2a2218;
    border-radius: 10px;
    padding: 14px;
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

# ── DB Config ────────────────────────────────────────────────────────────────
DB_CONFIG = {
    "host":     os.getenv("DB_HOST", "localhost"),
    "user":     os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", "123"),
    "database": os.getenv("DB_NAME", "pashuscore"),
}

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

# ── Helpers ──────────────────────────────────────────────────────────────────
@st.cache_resource
def get_conn():
    return mysql.connector.connect(**DB_CONFIG)

def run_query(sql, params=None):
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        df = pd.read_sql(sql, conn, params=params)
        conn.close()
        return df
    except Exception as e:
        st.error(f"DB Error: {e}")
        return pd.DataFrame()

def execute(sql, params=None):
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
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
               ON c.cattle_id = v.cattle_id AND v.next_due >= CURDATE()
        WHERE c.farmer_id = %s AND c.health_status != 'Deceased'
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
        "vacc_count": vacc_count,
        "healthy_count": healthy_count,
    }

def gauge_chart(score, color):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        domain={"x": [0, 1], "y": [0, 1]},
        gauge={
            "axis": {
                "range": [0, 100],
                "tickcolor": "#5a4a28",
                "tickfont": {"color": "#7a6030", "size": 11}
            },
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
            "threshold": {
                "line": {"color": color, "width": 4},
                "thickness": 0.8,
                "value": score
            }
        },
        number={
            "font": {"color": "#f0c040", "size": 52, "family": "Georgia"},
            "suffix": "/100"
        },
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
        name="Max",
        showlegend=False
    ))
    fig.add_trace(go.Bar(
        y=labels,
        x=scores,
        orientation="h",
        marker=dict(
            color=["#f0c040"] * len(scores),
            line=dict(color="#8b6914", width=1)
        ),
        name="Score",
        showlegend=False,
        text=[f"{s}/{m}" for s, m in zip(scores, maxes)],
        textposition="inside",
        textfont={"color": "#0f0e0c", "size": 12}
    ))
    fig.update_layout(
        barmode="overlay",
        paper_bgcolor="#18150e",
        plot_bgcolor="#18150e",
        xaxis=dict(showgrid=False, zeroline=False, color="#5a4a28"),
        yaxis=dict(color="#c0a060", tickfont={"size": 12}),
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
    overdue_vacc = run_query("SELECT COUNT(DISTINCT cattle_id) AS n FROM vaccinations WHERE next_due < CURDATE()")
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
            grade_colors = {"A+": "🟢", "A": "🟢", "B": "🟡", "C": "🟠", "D": "🔴"}
            df_display = df_all.copy()
            df_display["grade"] = df_display["grade"].map(lambda g: f"{grade_colors.get(g, '⚪')} {g}")
            df_display["credit_score"] = df_display["credit_score"].astype(int)
            st.dataframe(
                df_display[["name", "village", "state", "herd_size", "credit_score", "grade"]].rename(columns={
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
            color_map = {"A+": "#2d7a2d", "A": "#4a9e4a", "B": "#d4a017", "C": "#cc6600", "D": "#c0392b"}
            fig_pie = px.pie(
                grade_counts,
                names="Grade",
                values="Count",
                color="Grade",
                color_discrete_map=color_map,
                hole=0.5
            )
            fig_pie.update_layout(
                paper_bgcolor="#18150e",
                plot_bgcolor="#18150e",
                legend=dict(font=dict(color="#c0a060")),
                height=280,
                margin=dict(t=10, b=10, l=10, r=10)
            )
            fig_pie.update_traces(textfont_color="#f0f0f0")
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
            farmer_info = run_query("SELECT * FROM farmers WHERE farmer_id = %s", (farmer_id,))

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
                        st.markdown(f"**Land:** {fi['land_acres']} acres &nbsp;|&nbsp; **Animals:** {result['n']}")

                with col2:
                    st.markdown("#### Score Breakdown")
                    st.plotly_chart(breakdown_chart(result["breakdown"]), use_container_width=True)

                    st.markdown("#### Herd Details")
                    df_c = result["cattle_df"].copy()
                    health_icon = {"Healthy": "✅", "Mild Fever": "🟡", "Limping": "🟠", "Critical": "🔴"}
                    df_c["Health"] = df_c["health_status"].map(lambda h: f"{health_icon.get(h, '⚪')} {h}")
                    df_c["Vaccinated"] = df_c["vaccinated"].map(lambda v: "💉 Yes" if v else "❌ No")
                    df_c["Yield (L/day)"] = df_c["milk_yield_lpd"]
                    st.dataframe(
                        df_c[["cattle_id", "breed", "age_years", "Health", "Vaccinated", "Yield (L/day)"]].rename(columns={
                            "cattle_id": "Tag",
                            "breed": "Breed",
                            "age_years": "Age"
                        }),
                        use_container_width=True,
                        hide_index=True
                    )

                    if st.button("📋 Submit Loan Application", use_container_width=True):
                        lid = execute("""
                            INSERT INTO loan_applications
                                (farmer_id, credit_score, grade, amount_eligible, status)
                            VALUES (%s, %s, %s, %s, 'Pending')
                        """, (farmer_id, result["total"], result["grade"], result["amount"]))

                        if lid is not None:
                            st.success(f"✅ Application #{lid} submitted! Status: Pending")

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 3 — VILLAGE BATCH SCORE
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "🌾 Village Batch Score":
    st.markdown("## 🌾 Village Batch Scoring")
    st.markdown("Score every farmer in a village at once — for bank loan camps.")
    st.divider()

    villages = run_query("SELECT DISTINCT village FROM farmers ORDER BY village")
    village = st.selectbox("Select Village", villages["village"].tolist() if not villages.empty else [])

    if st.button("🚀 Run Batch Score", type="primary", use_container_width=True):
        farmers_in_village = run_query(
            "SELECT farmer_id, name FROM farmers WHERE village = %s", (village,)
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

                st.success(f"✅ Scored {len(df_res)} farmers in **{village}**")
                st.divider()

                c1, c2, c3 = st.columns(3)
                eligible = df_res[df_res["Grade"].isin(["A+", "A", "B"])]["Max Loan"].count()
                c1.metric("Eligible for Loan", eligible)
                c2.metric("Avg Score", f"{df_res['Score'].mean():.1f}")
                c3.metric("Top Score", df_res["Score"].max())

                st.dataframe(df_res, use_container_width=True, hide_index=True)

                fig = px.bar(
                    df_res,
                    x="Farmer",
                    y="Score",
                    color="Grade",
                    color_discrete_map={
                        "A+": "#2d7a2d",
                        "A": "#4a9e4a",
                        "B": "#d4a017",
                        "C": "#cc6600",
                        "D": "#c0392b"
                    },
                    title=f"Credit Scores — {village}"
                )
                fig.update_layout(
                    paper_bgcolor="#18150e",
                    plot_bgcolor="#18150e",
                    font=dict(color="#c0a060")
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("No active cattle found for farmers in this village.")

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
               CASE WHEN v.cattle_id IS NOT NULL THEN '💉 Vaccinated' ELSE '❌ Pending' END AS vacc_status
        FROM cattle c
        JOIN farmers f ON c.farmer_id = f.farmer_id
        LEFT JOIN vaccinations v ON c.cattle_id = v.cattle_id AND v.next_due >= CURDATE()
        ORDER BY f.name, c.breed
    """)

    if not df.empty:
        col1, col2 = st.columns([2, 1])
        with col1:
            breed_filter = st.multiselect("Filter by Breed", sorted(df["breed"].unique()))
        with col2:
            health_filter = st.multiselect("Filter by Health", sorted(df["health_status"].unique()))

        if breed_filter:
            df = df[df["breed"].isin(breed_filter)]
        if health_filter:
            df = df[df["health_status"].isin(health_filter)]

        st.dataframe(df, use_container_width=True, hide_index=True)
        st.caption(f"{len(df)} animals shown")

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
                execute(
                    "UPDATE cattle SET health_status = %s WHERE cattle_id = %s",
                    (new_health, cattle_id)
                )
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
               DATEDIFF(CURDATE(), v.next_due) AS days_overdue
        FROM vaccinations v
        JOIN cattle c ON v.cattle_id = c.cattle_id
        JOIN farmers f ON c.farmer_id = f.farmer_id
        WHERE v.next_due < CURDATE()
        ORDER BY days_overdue DESC
    """)

    if df.empty:
        st.success("✅ All vaccinations are up to date!")
    else:
        st.error(f"⚠️ {len(df)} cattle have overdue vaccinations")

        def severity(days):
            if days > 180:
                return "🔴 Critical"
            if days > 90:
                return "🟠 High"
            return "🟡 Moderate"

        df["Severity"] = df["days_overdue"].apply(severity)
        st.dataframe(df.rename(columns={
            "cattle_id": "Cattle ID",
            "ear_tag": "Tag",
            "breed": "Breed",
            "farmer": "Farmer",
            "phone": "Phone",
            "village": "Village",
            "vaccine": "Vaccine",
            "next_due": "Due Date",
            "days_overdue": "Days Overdue"
        }), use_container_width=True, hide_index=True)

        fig = px.bar(
            df.head(10),
            x="cattle_id",
            y="days_overdue",
            color="Severity",
            color_discrete_map={
                "🔴 Critical": "#c0392b",
                "🟠 High": "#cc6600",
                "🟡 Moderate": "#d4a017"
            },
            title="Top 10 Most Overdue"
        )
        fig.update_layout(
            paper_bgcolor="#18150e",
            plot_bgcolor="#18150e",
            font=dict(color="#c0a060")
        )
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
        ORDER BY la.applied_on DESC
    """)

    if df.empty:
        st.info("No loan applications yet. Score a farmer and apply.")
    else:
        c1, c2, c3 = st.columns(3)
        c1.metric("Total Applications", len(df))
        c2.metric("Approved", len(df[df["status"] == "Approved"]))
        c3.metric("Pending Review", len(df[df["status"] == "Pending"]))

        st.divider()
        status_filter = st.selectbox("Filter by Status", ["All", "Pending", "Approved", "Rejected"])
        if status_filter != "All":
            df = df[df["status"] == status_filter]

        st.dataframe(df.rename(columns={
            "app_id": "App #",
            "name": "Farmer",
            "village": "Village",
            "state": "State",
            "credit_score": "Score",
            "grade": "Grade",
            "amount_eligible": "Eligible (₹)",
            "status": "Status",
            "applied_on": "Applied On"
        }), use_container_width=True, hide_index=True)

        st.divider()
        st.markdown("#### Quick Decision")
        app_ids = df[df["status"] == "Pending"]["app_id"].tolist() if "app_id" in df.columns else []

        if app_ids:
            dc1, dc2, dc3 = st.columns(3)
            with dc1:
                sel_app = st.selectbox("Pending App #", app_ids)
            with dc2:
                st.write("")
                st.write("")
                if st.button("✅ Approve", use_container_width=True):
                    execute("UPDATE loan_applications SET status='Approved' WHERE app_id=%s", (sel_app,))
                    st.success(f"App #{sel_app} Approved!")
                    st.rerun()
            with dc3:
                st.write("")
                st.write("")
                if st.button("❌ Reject", use_container_width=True):
                    execute("UPDATE loan_applications SET status='Rejected' WHERE app_id=%s", (sel_app,))
                    st.warning(f"App #{sel_app} Rejected.")
                    st.rerun()
        else:
            st.info("No pending applications.")

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
            submitted = st.form_submit_button("✅ Register Farmer", use_container_width=True)

            if submitted:
                if not all([farmer_id, name, village, state]):
                    st.error("Please fill all required fields.")
                else:
                    execute("""
                        INSERT INTO farmers (farmer_id, name, village, state, land_acres, phone)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, (farmer_id, name, village, state, land, phone))
                    st.success(f"✅ Farmer {name} registered as {farmer_id}")

    with tab2:
        farmers_df = run_query("SELECT farmer_id, name FROM farmers ORDER BY name")
        farmer_map = {
            f"{r['name']} ({r['farmer_id']})": r["farmer_id"]
            for _, r in farmers_df.iterrows()
        } if not farmers_df.empty else {}

        with st.form("add_cattle"):
            c1, c2 = st.columns(2)
            farmer_sel = c1.selectbox("Farmer", list(farmer_map.keys()))
            cattle_id = c2.text_input("Cattle ID (e.g. C15)")
            breed = c1.selectbox("Breed", list(BREED_WEIGHTS.keys()))
            age = c2.number_input("Age (years)", 1, 20, 3)
            yield_lpd = c1.number_input("Milk Yield (L/day)", 0.0, 50.0, 5.0, 0.5)
            ear_tag = c2.text_input("Ear Tag")
            submitted = st.form_submit_button("✅ Register Cattle", use_container_width=True)

            if submitted:
                fid = farmer_map.get(farmer_sel, "")
                execute("""
                    INSERT INTO cattle
                        (cattle_id, farmer_id, breed, age_years, health_status, milk_yield_lpd, ear_tag)
                    VALUES (%s, %s, %s, %s, 'Healthy', %s, %s)
                """, (cattle_id, fid, breed, age, yield_lpd, ear_tag))
                st.success(f"✅ Cattle {cattle_id} ({breed}) registered under {farmer_sel}")

    with tab3:
        all_cattle = run_query("SELECT cattle_id FROM cattle WHERE health_status != 'Deceased'")
        with st.form("add_vacc"):
            c1, c2 = st.columns(2)
            cid = c1.selectbox("Cattle ID", all_cattle["cattle_id"].tolist() if not all_cattle.empty else [])
            vaccine = c2.text_input("Vaccine Name (e.g. FMD + HS)")
            given = c1.date_input("Date Given", value=date.today())
            due = c2.date_input("Next Due Date")
            vet = c1.text_input("Vet Name")
            submitted = st.form_submit_button("✅ Add Record", use_container_width=True)

            if submitted:
                execute("""
                    INSERT INTO vaccinations (cattle_id, vaccine, given_on, next_due, vet_name)
                    VALUES (%s, %s, %s, %s, %s)
                """, (cid, vaccine, given, due, vet))
                st.success(f"✅ Vaccination recorded for {cid}")