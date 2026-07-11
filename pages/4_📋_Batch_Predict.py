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

PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, sans-serif", color="#e2e8f0"),
    margin=dict(t=40, b=30, l=40, r=20),
)

# ── Header ──────────────────────────────────────────────────────────────
st.markdown("""
<div style="padding: 0.5rem 0 0.5rem;">
    <h1 style="font-size:2rem; margin-bottom:0.2rem;">
        📋 <span class="gradient-text">Batch Predictions</span>
    </h1>
    <p style="color:#94a3b8; font-size:0.95rem;">
        Upload a CSV of employees to predict turnover risk for all of them at once.
    </p>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# ── Expected format ─────────────────────────────────────────────────────
with st.expander("📄 Expected CSV Format & Sample Download"):
    st.markdown("""
    Your CSV should have these columns (matching the original dataset):

    | Column | Type | Description |
    |---|---|---|
    | `satisfaction_level` | float (0–1) | Self-reported satisfaction |
    | `last_evaluation` | float (0–1) | Manager evaluation score |
    | `number_project` | int (2–7) | Active projects |
    | `average_montly_hours` | int (80–320) | Monthly work hours |
    | `time_spend_company` | int (1–10) | Years at company |
    | `Work_accident` | 0 or 1 | Had a work accident? |
    | `promotion_last_5years` | 0 or 1 | Promoted recently? |
    | `Department` | string | e.g. sales, IT, hr |
    | `salary` | string | low, medium, high |
    """)

    # Generate sample CSV
    sample = pd.DataFrame({
        "satisfaction_level": [0.38, 0.80, 0.72, 0.55, 0.92],
        "last_evaluation": [0.53, 0.86, 0.87, 0.62, 0.45],
        "number_project": [2, 5, 5, 3, 2],
        "average_montly_hours": [157, 262, 223, 150, 135],
        "time_spend_company": [3, 6, 5, 2, 3],
        "Work_accident": [0, 0, 0, 1, 0],
        "promotion_last_5years": [0, 0, 0, 0, 1],
        "Department": ["sales", "technical", "IT", "hr", "marketing"],
        "salary": ["low", "medium", "low", "high", "medium"],
    })
    st.dataframe(sample, use_container_width=True, height=220)
    st.download_button(
        "⬇️ Download Sample CSV",
        data=sample.to_csv(index=False).encode("utf-8"),
        file_name="sample_employees.csv",
        mime="text/csv",
    )

# ── File Upload ─────────────────────────────────────────────────────────
st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
uploaded_file = st.file_uploader(
    "Upload your employee CSV",
    type=["csv"],
    help="Upload a CSV matching the format above.",
)

if uploaded_file is not None:
    try:
        raw_df = pd.read_csv(uploaded_file)
    except Exception as e:
        st.error(f"Error reading file: {e}")
        st.stop()

    st.markdown(f"**Preview** — {len(raw_df):,} employees loaded")
    st.dataframe(raw_df.head(20), use_container_width=True, height=300)

    required = [
        "satisfaction_level", "last_evaluation", "number_project",
        "average_montly_hours", "time_spend_company", "Work_accident",
        "promotion_last_5years", "Department", "salary",
    ]
    missing = [c for c in required if c not in raw_df.columns]
    if missing:
        st.error(f"Missing required columns: {', '.join(missing)}")
        st.stop()

    st.markdown("---")

    if st.button("⚡ Run Batch Predictions", use_container_width=True, type="primary"):
        # Feature engineering
        batch = raw_df.copy()
        batch["overworked"] = (batch["average_montly_hours"] > 175).astype(int)

        # One-hot encode department
        departments = ["IT", "RandD", "accounting", "hr", "management",
                        "marketing", "product_mng", "sales", "support", "technical"]
        for dept in departments:
            batch[f"Department_{dept}"] = (batch["Department"] == dept).astype(int)

        # One-hot encode salary
        for sal in ["high", "low", "medium"]:
            batch[f"salary_{sal}"] = (batch["salary"] == sal).astype(int)

        # Build model input
        model_cols = [
            "satisfaction_level", "last_evaluation", "number_project",
            "average_montly_hours", "time_spend_company", "Work_accident",
            "promotion_last_5years", "overworked",
        ] + [f"Department_{d}" for d in departments] + ["salary_high", "salary_low", "salary_medium"]

        X = batch[model_cols]
        predictions = model.predict(X)
        probas = model.predict_proba(X)[:, 1]

        # Build results
        results = raw_df.copy()
        results["Prediction"] = np.where(predictions == 1, "Leave", "Stay")
        results["Leave Probability"] = np.round(probas * 100, 1)

        # Risk level
        def risk_level(p):
            if p >= 60:
                return "🔴 High"
            elif p >= 30:
                return "🟡 Medium"
            return "🟢 Low"

        results["Risk Level"] = results["Leave Probability"].apply(risk_level)

        # ── Summary KPIs ────────────────────────────────────────────────
        st.markdown("### 📊 Batch Results Summary")

        high_risk = (probas >= 0.6).sum()
        med_risk = ((probas >= 0.3) & (probas < 0.6)).sum()
        low_risk = (probas < 0.3).sum()
        avg_prob = probas.mean() * 100

        s1, s2, s3, s4 = st.columns(4)
        s1.metric("🔴 High Risk", f"{high_risk}")
        s2.metric("🟡 Medium Risk", f"{med_risk}")
        s3.metric("🟢 Low Risk", f"{low_risk}")
        s4.metric("Avg Risk", f"{avg_prob:.1f}%")

        st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

        # ── Risk distribution chart ─────────────────────────────────────
        c1, c2 = st.columns([2, 1])

        with c1:
            st.markdown("**Risk Score Distribution**")
            fig_hist = go.Figure()
            fig_hist.add_trace(go.Histogram(
                x=probas * 100,
                nbinsx=20,
                marker=dict(
                    color=probas * 100,
                    colorscale=[[0, "#00c897"], [0.5, "#f59e0b"], [1, "#ff6b6b"]],
                ),
                hovertemplate="Risk: %{x:.0f}%<br>Count: %{y}<extra></extra>",
            ))
            fig_hist.add_vline(x=50, line_dash="dash", line_color="#e2e8f0",
                               annotation_text="50% threshold", annotation_font_color="#94a3b8")
            fig_hist.update_layout(
                **PLOTLY_LAYOUT, height=320,
                showlegend=False,
                xaxis=dict(gridcolor="rgba(99,179,237,0.08)", title="Leave Probability (%)"),
                yaxis=dict(gridcolor="rgba(99,179,237,0.08)", title="# Employees"),
            )
            st.plotly_chart(fig_hist, use_container_width=True)

        with c2:
            st.markdown("**Risk Breakdown**")
            fig_pie = go.Figure(data=[go.Pie(
                labels=["High Risk", "Medium Risk", "Low Risk"],
                values=[high_risk, med_risk, low_risk],
                hole=0.55,
                marker=dict(
                    colors=["#ff6b6b", "#f59e0b", "#00c897"],
                    line=dict(color="#0a0e1a", width=2),
                ),
                textinfo="label+value",
                textfont=dict(size=11, color="#e2e8f0"),
            )])
            fig_pie.update_layout(**PLOTLY_LAYOUT, height=320, showlegend=False)
            st.plotly_chart(fig_pie, use_container_width=True)

        # ── Full results table ──────────────────────────────────────────
        st.markdown("---")
        st.markdown("### 📄 Detailed Results")

        # Sort by risk
        results_sorted = results.sort_values("Leave Probability", ascending=False)
        st.dataframe(results_sorted, use_container_width=True, height=450)

        # Download
        csv_out = results_sorted.to_csv(index=False).encode("utf-8")
        st.download_button(
            "⬇️ Download Results as CSV",
            data=csv_out,
            file_name="batch_predictions.csv",
            mime="text/csv",
            use_container_width=True,
        )
