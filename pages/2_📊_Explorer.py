import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ── Load data ───────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv("HR_dataset.csv")
    df["overworked"] = (df["average_montly_hours"] > 175).astype(int)
    df["left_label"] = df["left"].map({1: "Left", 0: "Stayed"})
    return df

df = load_data()

PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, sans-serif", color="#e2e8f0"),
    margin=dict(t=40, b=30, l=40, r=20),
)

DEFAULT_AXIS = dict(gridcolor="rgba(99,179,237,0.08)", zerolinecolor="rgba(99,179,237,0.08)")
DEFAULT_LEGEND = dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#94a3b8", size=11))

# ── Header ──────────────────────────────────────────────────────────────
st.markdown("""
<div style="padding: 0.5rem 0 0.5rem;">
    <h1 style="font-size:2rem; margin-bottom:0.2rem;">
        📊 <span class="gradient-text">Data Explorer</span>
    </h1>
    <p style="color:#94a3b8; font-size:0.95rem;">
        Filter, slice, and visualize the HR dataset interactively.
    </p>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# ── Sidebar Filters ─────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🎛️ Filters")
    st.markdown("<p style='color:#64748b;font-size:0.8rem;'>Adjust filters to explore subsets of the data.</p>",
                unsafe_allow_html=True)

    dept_filter = st.multiselect(
        "Department",
        options=sorted(df["Department"].unique()),
        default=sorted(df["Department"].unique()),
    )
    salary_filter = st.multiselect(
        "Salary Level",
        options=["low", "medium", "high"],
        default=["low", "medium", "high"],
    )
    tenure_range = st.slider(
        "Tenure (years)",
        int(df["time_spend_company"].min()),
        int(df["time_spend_company"].max()),
        (int(df["time_spend_company"].min()), int(df["time_spend_company"].max())),
    )
    project_range = st.slider(
        "Number of Projects",
        int(df["number_project"].min()),
        int(df["number_project"].max()),
        (int(df["number_project"].min()), int(df["number_project"].max())),
    )
    hours_range = st.slider(
        "Monthly Hours",
        int(df["average_montly_hours"].min()),
        int(df["average_montly_hours"].max()),
        (int(df["average_montly_hours"].min()), int(df["average_montly_hours"].max())),
    )
    status_filter = st.radio("Employee Status", ["All", "Left Only", "Stayed Only"], index=0)

# ── Apply filters ───────────────────────────────────────────────────────
filtered = df[
    (df["Department"].isin(dept_filter)) &
    (df["salary"].isin(salary_filter)) &
    (df["time_spend_company"].between(*tenure_range)) &
    (df["number_project"].between(*project_range)) &
    (df["average_montly_hours"].between(*hours_range))
]
if status_filter == "Left Only":
    filtered = filtered[filtered["left"] == 1]
elif status_filter == "Stayed Only":
    filtered = filtered[filtered["left"] == 0]

# ── Filtered KPIs ──────────────────────────────────────────────────────
n = len(filtered)
left_n = filtered["left"].sum() if len(filtered) > 0 else 0
turnover = left_n / n if n > 0 else 0

k1, k2, k3, k4 = st.columns(4)
k1.metric("Filtered Employees", f"{n:,}")
k2.metric("Left", f"{left_n:,}")
k3.metric("Turnover Rate", f"{turnover:.1%}")
k4.metric("Avg Satisfaction", f"{filtered['satisfaction_level'].mean():.2f}" if n > 0 else "—")

st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

# ── Chart section with tabs ─────────────────────────────────────────────
tab_dist, tab_corr, tab_cross, tab_data = st.tabs([
    "📈 Distributions", "🔗 Correlations", "🔀 Cross-Analysis", "📄 Data Table"
])

NUMERIC_COLS = [
    "satisfaction_level", "last_evaluation", "number_project",
    "average_montly_hours", "time_spend_company",
]

# ── Tab 1: Distributions ───────────────────────────────────────────────
with tab_dist:
    col_sel = st.selectbox(
        "Select a feature to visualize",
        NUMERIC_COLS,
        format_func=lambda x: x.replace("_", " ").title(),
    )

    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"**Histogram** — {col_sel.replace('_', ' ').title()}")
        fig_hist = go.Figure()
        for label, color in [("Stayed", "#00c897"), ("Left", "#ff6b6b")]:
            sub = filtered[filtered["left_label"] == label]
            fig_hist.add_trace(go.Histogram(
                x=sub[col_sel], name=label, marker_color=color, opacity=0.7, nbinsx=30,
            ))
        fig_hist.update_layout(**PLOTLY_LAYOUT, height=350, barmode="overlay",
                               legend=DEFAULT_LEGEND,
                               xaxis=dict(**DEFAULT_AXIS, title=col_sel.replace("_", " ").title()),
                               yaxis=dict(**DEFAULT_AXIS, title="Count"))
        st.plotly_chart(fig_hist, use_container_width=True)

    with c2:
        st.markdown(f"**Box Plot** — {col_sel.replace('_', ' ').title()}")
        fig_box = go.Figure()
        for label, color in [("Stayed", "#00c897"), ("Left", "#ff6b6b")]:
            sub = filtered[filtered["left_label"] == label]
            fig_box.add_trace(go.Box(
                y=sub[col_sel], name=label, marker_color=color,
                boxmean="sd", line=dict(width=1.5),
            ))
        fig_box.update_layout(**PLOTLY_LAYOUT, height=350, showlegend=False,
                               xaxis=DEFAULT_AXIS,
                               yaxis=dict(**DEFAULT_AXIS, title=col_sel.replace("_", " ").title()))
        st.plotly_chart(fig_box, use_container_width=True)

# ── Tab 2: Correlation ─────────────────────────────────────────────────
with tab_corr:
    st.markdown("**Feature Correlation Matrix**")
    corr_cols = NUMERIC_COLS + ["Work_accident", "promotion_last_5years", "left"]
    corr_matrix = filtered[corr_cols].corr()

    labels = [c.replace("_", " ").title() for c in corr_cols]
    fig_corr = go.Figure(data=go.Heatmap(
        z=corr_matrix.values,
        x=labels, y=labels,
        colorscale=[[0, "#ff6b6b"], [0.5, "#0a0e1a"], [1, "#00d4ff"]],
        zmin=-1, zmax=1,
        text=np.round(corr_matrix.values, 2),
        texttemplate="%{text}",
        textfont=dict(size=10, color="#e2e8f0"),
        hovertemplate="%{x} ↔ %{y}<br>r = %{z:.3f}<extra></extra>",
        colorbar=dict(
            tickfont=dict(color="#94a3b8"),
            title=dict(text="r", font=dict(color="#94a3b8")),
        ),
    ))
    fig_corr.update_layout(**PLOTLY_LAYOUT, height=480,
                            xaxis=dict(tickangle=-45, gridcolor="rgba(0,0,0,0)"),
                            yaxis=dict(gridcolor="rgba(0,0,0,0)"))
    st.plotly_chart(fig_corr, use_container_width=True)

# ── Tab 3: Cross-Analysis ──────────────────────────────────────────────
with tab_cross:
    ca, cb = st.columns(2)
    with ca:
        x_col = st.selectbox("X-Axis", NUMERIC_COLS, index=0,
                              format_func=lambda x: x.replace("_", " ").title(), key="x_col")
    with cb:
        y_col = st.selectbox("Y-Axis", NUMERIC_COLS, index=1,
                              format_func=lambda x: x.replace("_", " ").title(), key="y_col")

    plot_sample = filtered.sample(min(2000, len(filtered)), random_state=42) if len(filtered) > 0 else filtered

    fig_cross = go.Figure()
    for label, color in [("Stayed", "#00c897"), ("Left", "#ff6b6b")]:
        sub = plot_sample[plot_sample["left_label"] == label]
        fig_cross.add_trace(go.Scatter(
            x=sub[x_col], y=sub[y_col], mode="markers", name=label,
            marker=dict(color=color, size=5, opacity=0.5),
        ))
    fig_cross.update_layout(
        **PLOTLY_LAYOUT, height=450,
        legend=DEFAULT_LEGEND,
        xaxis=dict(**DEFAULT_AXIS, title=x_col.replace("_", " ").title()),
        yaxis=dict(**DEFAULT_AXIS, title=y_col.replace("_", " ").title()),
    )
    st.plotly_chart(fig_cross, use_container_width=True)

# ── Tab 4: Data Table ──────────────────────────────────────────────────
with tab_data:
    st.markdown(f"**Filtered Dataset** — {len(filtered):,} rows")
    st.dataframe(
        filtered.drop(columns=["left_label", "overworked"], errors="ignore"),
        use_container_width=True,
        height=500,
    )
    csv = filtered.to_csv(index=False).encode("utf-8")
    st.download_button(
        "⬇️ Download Filtered Data as CSV",
        data=csv,
        file_name="filtered_hr_data.csv",
        mime="text/csv",
        use_container_width=True,
    )
