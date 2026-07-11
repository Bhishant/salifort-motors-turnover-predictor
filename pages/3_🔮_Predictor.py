import streamlit as st
import pandas as pd
import numpy as np
import pickle
import plotly.graph_objects as go

# ── Load model ──────────────────────────────────────────────────────────
@st.cache_resource
def load_model():
    with open("hr_rf1_model.pkl", "rb") as f:
        return pickle.load(f)

model = load_model()

FEATURE_IMPORTANCE = {
    "last_evaluation": 0.362,
    "number_project": 0.351,
    "time_spend_company": 0.198,
    "overworked": 0.083,
    "satisfaction_level": 0.006,
}

PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, sans-serif", color="#e2e8f0"),
    margin=dict(t=30, b=10, l=20, r=20),
)

# ── Header ──────────────────────────────────────────────────────────────
st.markdown("""
<div style="padding: 0.5rem 0 0.5rem;">
    <h1 style="font-size:2rem; margin-bottom:0.2rem;">
        🔮 <span class="gradient-text">Turnover Predictor</span>
    </h1>
    <p style="color:#94a3b8; font-size:0.95rem;">
        Enter an employee's details to predict their turnover risk.
    </p>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# ── Input Cards ─────────────────────────────────────────────────────────
st.markdown("##### ⚡ Performance & Satisfaction")
perf1, perf2, perf3 = st.columns(3)
with perf1:
    satisfaction = st.slider("😊 Satisfaction Level", 0.0, 1.0, 0.5, 0.01,
        help="Employee's self-reported satisfaction (0 = miserable, 1 = thriving)")
with perf2:
    last_eval = st.slider("📊 Last Evaluation", 0.0, 1.0, 0.7, 0.01,
        help="Manager's performance evaluation score")
with perf3:
    promotion = st.selectbox("🏆 Promoted (Last 5yr)?", ["No", "Yes"],
        help="Was the employee promoted in the last 5 years?")

st.markdown("<div style='height:0.8rem'></div>", unsafe_allow_html=True)

st.markdown("##### 📋 Workload")
wl1, wl2 = st.columns(2)
with wl1:
    num_projects = st.slider("📁 Number of Projects", 2, 7, 4,
        help="How many projects the employee is currently handling")
with wl2:
    monthly_hours = st.slider("⏰ Avg Monthly Hours", 80, 320, 160,
        help="Average hours worked per month (standard ≈ 167)")

st.markdown("<div style='height:0.8rem'></div>", unsafe_allow_html=True)

st.markdown("##### 🏢 Company Info")
ci1, ci2, ci3, ci4 = st.columns(4)
with ci1:
    tenure = st.slider("🗓️ Tenure (years)", 1, 10, 3)
with ci2:
    work_accident = st.selectbox("🚑 Work Accident?", ["No", "Yes"])
with ci3:
    department = st.selectbox("🏢 Department", [
        "sales", "support", "technical", "hr", "IT",
        "RandD", "product_mng", "marketing", "accounting", "management",
    ])
with ci4:
    salary = st.selectbox("💰 Salary Level", ["low", "medium", "high"])

st.markdown("---")

# ── Predict ─────────────────────────────────────────────────────────────
predict_clicked = st.button("⚡ Predict Turnover Risk", use_container_width=True, type="primary")

if predict_clicked:
    overworked = 1 if monthly_hours > 175 else 0

    input_data = {
        "satisfaction_level": satisfaction,
        "last_evaluation": last_eval,
        "number_project": num_projects,
        "average_montly_hours": monthly_hours,
        "time_spend_company": tenure,
        "Work_accident": 1 if work_accident == "Yes" else 0,
        "promotion_last_5years": 1 if promotion == "Yes" else 0,
        "overworked": overworked,
        "Department_IT": 1 if department == "IT" else 0,
        "Department_RandD": 1 if department == "RandD" else 0,
        "Department_accounting": 1 if department == "accounting" else 0,
        "Department_hr": 1 if department == "hr" else 0,
        "Department_management": 1 if department == "management" else 0,
        "Department_marketing": 1 if department == "marketing" else 0,
        "Department_product_mng": 1 if department == "product_mng" else 0,
        "Department_sales": 1 if department == "sales" else 0,
        "Department_support": 1 if department == "support" else 0,
        "Department_technical": 1 if department == "technical" else 0,
        "salary_high": 1 if salary == "high" else 0,
        "salary_low": 1 if salary == "low" else 0,
        "salary_medium": 1 if salary == "medium" else 0,
    }

    df_input = pd.DataFrame([input_data])
    prediction = model.predict(df_input)[0]
    proba = model.predict_proba(df_input)[0]
    leave_prob = proba[1]
    stay_prob = proba[0]

    # ── Classify archetype ──────────────────────────────────────────────
    if monthly_hours > 240 and satisfaction < 0.3:
        archetype = ("🔥 Burned Out", "Employee is severely overworked with rock-bottom satisfaction. Classic burnout profile.", "#ff6b6b")
    elif last_eval >= 0.8 and satisfaction < 0.5:
        archetype = ("🏆 Undervalued Overachiever", "High performer with low satisfaction — doing great work but getting nothing back.", "#f59e0b")
    elif satisfaction < 0.2:
        archetype = ("😞 Checked Out", "Satisfaction near zero. Mentally already gone.", "#94a3b8")
    else:
        archetype = ("💚 Healthy Profile", "No alarming pattern detected in current metrics.", "#00c897")

    # ── Result cards ────────────────────────────────────────────────────
    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

    r1, r2 = st.columns([2, 1])

    with r1:
        if prediction == 1:
            st.markdown(f"""
            <div class="glass-card" style="border-left: 4px solid #ff6b6b; text-align:center;">
                <p style="font-size:0.8rem; color:#ff6b6b; text-transform:uppercase; letter-spacing:0.1em; margin-bottom:0.5rem;">
                    ⚠️ High Risk — Likely to Leave
                </p>
                <p class="stat-value" style="color:#ff6b6b;">{leave_prob:.1%}</p>
                <p class="stat-label">probability of leaving</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="glass-card" style="border-left: 4px solid #00c897; text-align:center;">
                <p style="font-size:0.8rem; color:#00c897; text-transform:uppercase; letter-spacing:0.1em; margin-bottom:0.5rem;">
                    ✅ Low Risk — Likely to Stay
                </p>
                <p class="stat-value" style="color:#00c897;">{stay_prob:.1%}</p>
                <p class="stat-label">probability of staying</p>
            </div>
            """, unsafe_allow_html=True)

        # Archetype card
        st.markdown(f"""
        <div class="glass-card" style="border-left: 4px solid {archetype[2]};">
            <p style="font-size:0.8rem; color:{archetype[2]}; text-transform:uppercase; letter-spacing:0.1em; margin-bottom:0.3rem;">
                Employee Archetype
            </p>
            <p style="font-size:1.2rem; font-weight:700; color:#e2e8f0; margin-bottom:0.3rem;">{archetype[0]}</p>
            <p style="font-size:0.9rem; color:#94a3b8; margin:0;">{archetype[1]}</p>
        </div>
        """, unsafe_allow_html=True)

    with r2:
        # Gauge
        gauge_color = "#ff6b6b" if leave_prob > 0.5 else ("#f59e0b" if leave_prob > 0.3 else "#00c897")
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=round(leave_prob * 100, 1),
            number=dict(suffix="%", font=dict(size=36, color="#e2e8f0")),
            title=dict(text="Turnover Risk", font=dict(size=13, color="#94a3b8")),
            gauge=dict(
                axis=dict(range=[0, 100], tickfont=dict(color="#64748b", size=10),
                          tickcolor="#64748b"),
                bar=dict(color=gauge_color, thickness=0.8),
                bgcolor="rgba(17,24,39,0.5)",
                borderwidth=0,
                steps=[
                    dict(range=[0, 30], color="rgba(0,200,151,0.1)"),
                    dict(range=[30, 60], color="rgba(245,158,11,0.1)"),
                    dict(range=[60, 100], color="rgba(255,107,107,0.1)"),
                ],
                threshold=dict(
                    line=dict(color="#e2e8f0", width=2),
                    thickness=0.75,
                    value=50,
                ),
            ),
        ))
        fig_gauge.update_layout(**PLOTLY_LAYOUT, height=240)
        st.plotly_chart(fig_gauge, use_container_width=True)

    # ── Risk Factors ────────────────────────────────────────────────────
    st.markdown("#### 🔍 Risk Factors")

    flags = []
    if satisfaction < 0.3:
        flags.append(("😞 Very low satisfaction", "critical",
                       "Satisfaction below 0.3 is strongly associated with turnover."))
    if monthly_hours > 240:
        flags.append(("🔥 Severely overworked", "critical",
                       f"Working {monthly_hours} hrs/mo — well above the 175hr overwork threshold."))
    elif monthly_hours > 175:
        flags.append(("⏰ Overworked", "warning",
                       f"Working {monthly_hours} hrs/mo (threshold: 175). Risk of burnout."))
    if num_projects >= 6:
        flags.append(("📁 Too many projects", "critical",
                       f"Handling {num_projects} projects. Employees with 6–7 projects leave at very high rates."))
    if last_eval >= 0.8 and satisfaction < 0.5:
        flags.append(("🏆 High performer, low satisfaction", "critical",
                       "Classic flight risk: doing excellent work but not getting recognition."))
    if tenure == 5:
        flags.append(("🗓️ 5-year tenure spike", "warning",
                       "5-year mark shows the highest attrition spike in the dataset."))
    if promotion == "No" and tenure >= 4:
        flags.append(("🚫 No promotion despite tenure", "warning",
                       f"{tenure} years without promotion erodes engagement."))
    if salary == "low" and last_eval >= 0.7:
        flags.append(("💰 Underpaid high performer", "warning",
                       "Low salary despite strong evaluation — potential dissatisfaction driver."))
    if not flags:
        flags.append(("✅ No major red flags", "ok",
                       "Current metrics don't trigger known risk patterns."))

    for flag_text, severity, explanation in flags:
        st.markdown(f"""
        <div class="risk-flag {severity}">
            <div>
                <p style="margin:0; font-weight:600; color:#e2e8f0; font-size:0.95rem;">{flag_text}</p>
                <p style="margin:0.2rem 0 0; color:#94a3b8; font-size:0.82rem;">{explanation}</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ── Feature importance context ──────────────────────────────────────
    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
    with st.expander("📊 How the model weighs features"):
        fig_imp = go.Figure()
        feats = list(FEATURE_IMPORTANCE.keys())
        vals = list(FEATURE_IMPORTANCE.values())
        fig_imp.add_trace(go.Bar(
            x=vals,
            y=[f.replace("_", " ").title() for f in feats],
            orientation="h",
            marker=dict(
                color=["#00d4ff", "#3b82f6", "#8b5cf6", "#f59e0b", "#64748b"],
                cornerradius=4,
            ),
            text=[f"{v:.1%}" for v in vals],
            textposition="outside",
            textfont=dict(color="#e2e8f0", size=11),
        ))
        fig_imp.update_layout(
            **PLOTLY_LAYOUT,
            height=260,
            showlegend=False,
            xaxis=dict(gridcolor="rgba(99,179,237,0.08)", title="Importance"),
            yaxis=dict(autorange="reversed", gridcolor="rgba(0,0,0,0)"),
        )
        st.plotly_chart(fig_imp, use_container_width=True)

# ── Footer ──────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("""
<p style="text-align:center; color:#64748b; font-size:0.78rem;">
    Random Forest · 100 estimators · Trained on Salifort Motors HR data (n=14,999) ·
    Google Advanced Data Analytics Capstone
</p>
""", unsafe_allow_html=True)
