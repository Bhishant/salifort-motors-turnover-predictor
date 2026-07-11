import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# ── Load data ───────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv("HR_dataset.csv")
    df["overworked"] = (df["average_montly_hours"] > 175).astype(int)
    df["left_label"] = df["left"].map({1: "Left", 0: "Stayed"})
    return df

df = load_data()

# ── Plotly theme defaults ───────────────────────────────────────────────
PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, sans-serif", color="#e2e8f0"),
    margin=dict(t=40, b=30, l=40, r=20),
)

DEFAULT_AXIS = dict(gridcolor="rgba(99,179,237,0.08)", zerolinecolor="rgba(99,179,237,0.08)")
DEFAULT_LEGEND = dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#94a3b8", size=11))

COLORS = {
    "Left": "#ff6b6b",
    "Stayed": "#00c897",
    "cyan": "#00d4ff",
    "blue": "#3b82f6",
    "purple": "#8b5cf6",
    "amber": "#f59e0b",
    "coral": "#ff6b6b",
    "emerald": "#00c897",
}

# ── Hero header ─────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center; padding: 1.5rem 0 0.5rem;">
    <h1 style="font-size:2.6rem; font-weight:800; margin-bottom:0.3rem;">
        <span class="gradient-text">Salifort Motors</span>
    </h1>
    <p style="color:#94a3b8; font-size:1.1rem; margin:0;">
        Employee Turnover Analytics Dashboard · 14,999 employees analyzed
    </p>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# ── KPI Row ─────────────────────────────────────────────────────────────
total = len(df)
left_count = df["left"].sum()
turnover_rate = left_count / total
avg_satisfaction = df["satisfaction_level"].mean()
avg_hours = df["average_montly_hours"].mean()
avg_tenure = df["time_spend_company"].mean()
promo_rate = df["promotion_last_5years"].mean()

k1, k2, k3, k4, k5, k6 = st.columns(6)
k1.metric("Total Employees", f"{total:,}")
k2.metric("Turnover Rate", f"{turnover_rate:.1%}")
k3.metric("Avg Satisfaction", f"{avg_satisfaction:.2f}")
k4.metric("Avg Monthly Hours", f"{avg_hours:.0f}")
k5.metric("Avg Tenure", f"{avg_tenure:.1f} yrs")
k6.metric("Promotion Rate", f"{promo_rate:.1%}")

st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)

# ── Row 1: Turnover by Department + Turnover by Salary ──────────────────
col_a, col_b = st.columns([3, 2])

with col_a:
    st.markdown("#### Turnover by Department")
    dept_stats = df.groupby("Department").agg(
        total=("left", "count"),
        left=("left", "sum"),
    ).reset_index()
    dept_stats["turnover_pct"] = (dept_stats["left"] / dept_stats["total"] * 100).round(1)
    dept_stats = dept_stats.sort_values("turnover_pct", ascending=True)

    fig_dept = go.Figure()
    fig_dept.add_trace(go.Bar(
        y=dept_stats["Department"],
        x=dept_stats["turnover_pct"],
        orientation="h",
        marker=dict(
            color=dept_stats["turnover_pct"],
            colorscale=[[0, "#00c897"], [0.5, "#f59e0b"], [1, "#ff6b6b"]],
            line=dict(width=0),
            cornerradius=4,
        ),
        text=[f"{v}%" for v in dept_stats["turnover_pct"]],
        textposition="outside",
        textfont=dict(color="#e2e8f0", size=11),
        hovertemplate="<b>%{y}</b><br>Turnover: %{x}%<br>Left: %{customdata[0]} / %{customdata[1]}<extra></extra>",
        customdata=np.stack([dept_stats["left"], dept_stats["total"]], axis=-1),
    ))
    fig_dept.update_layout(
        **PLOTLY_LAYOUT,
        height=380,
        xaxis=dict(**DEFAULT_AXIS, title="Turnover Rate (%)"),
        yaxis=dict(**DEFAULT_AXIS, title=""),
        showlegend=False,
    )
    st.plotly_chart(fig_dept, use_container_width=True)

with col_b:
    st.markdown("#### Turnover by Salary Level")
    sal_stats = df.groupby("salary").agg(
        total=("left", "count"),
        left=("left", "sum"),
    ).reset_index()
    sal_stats["turnover_pct"] = (sal_stats["left"] / sal_stats["total"] * 100).round(1)
    # Order: low, medium, high
    sal_order = {"low": 0, "medium": 1, "high": 2}
    sal_stats["order"] = sal_stats["salary"].map(sal_order)
    sal_stats = sal_stats.sort_values("order")

    sal_colors = ["#ff6b6b", "#f59e0b", "#00c897"]
    fig_sal = go.Figure(data=[go.Pie(
        labels=sal_stats["salary"].str.title(),
        values=sal_stats["left"],
        hole=0.55,
        marker=dict(colors=sal_colors, line=dict(color="#0a0e1a", width=2)),
        textinfo="label+percent",
        textfont=dict(size=12, color="#e2e8f0"),
        hovertemplate="<b>%{label}</b><br>Left: %{value}<br>Share: %{percent}<extra></extra>",
    )])
    fig_sal.update_layout(
        **PLOTLY_LAYOUT,
        height=380,
        showlegend=False,
        annotations=[dict(
            text=f"<b>{left_count}</b><br><span style='font-size:11px;color:#94a3b8'>Left</span>",
            x=0.5, y=0.5, font_size=22, showarrow=False,
            font_color="#e2e8f0",
        )],
    )
    st.plotly_chart(fig_sal, use_container_width=True)

# ── Row 2: Hours Distribution + Satisfaction vs Evaluation ──────────────
col_c, col_d = st.columns(2)

with col_c:
    st.markdown("#### Monthly Hours Distribution")
    fig_hours = go.Figure()
    for label, color in [("Stayed", COLORS["Stayed"]), ("Left", COLORS["Left"])]:
        subset = df[df["left_label"] == label]
        fig_hours.add_trace(go.Histogram(
            x=subset["average_montly_hours"],
            name=label,
            marker_color=color,
            opacity=0.7,
            nbinsx=40,
            hovertemplate="Hours: %{x}<br>Count: %{y}<extra></extra>",
        ))
    fig_hours.update_layout(
        **PLOTLY_LAYOUT,
        height=380,
        barmode="overlay",
        xaxis=dict(**DEFAULT_AXIS, title="Average Monthly Hours"),
        yaxis=dict(**DEFAULT_AXIS, title="Count"),
        legend=dict(**DEFAULT_LEGEND, x=0.75, y=0.95),
    )
    st.plotly_chart(fig_hours, use_container_width=True)

with col_d:
    st.markdown("#### Satisfaction vs Evaluation — Employee Archetypes")
    # Sample for performance if large dataset
    plot_df = df.sample(min(3000, len(df)), random_state=42)
    fig_scatter = go.Figure()
    for label, color in [("Stayed", COLORS["Stayed"]), ("Left", COLORS["Left"])]:
        subset = plot_df[plot_df["left_label"] == label]
        fig_scatter.add_trace(go.Scatter(
            x=subset["satisfaction_level"],
            y=subset["last_evaluation"],
            mode="markers",
            name=label,
            marker=dict(color=color, size=4, opacity=0.5),
            hovertemplate=(
                "Satisfaction: %{x:.2f}<br>"
                "Evaluation: %{y:.2f}<br>"
                "<extra></extra>"
            ),
        ))
    # Archetype annotations
    fig_scatter.add_annotation(x=0.1, y=0.9, text="🔥 Burned Out",
        showarrow=False, font=dict(size=10, color="#ff6b6b"),
        bgcolor="rgba(255,107,107,0.12)", borderpad=4)
    fig_scatter.add_annotation(x=0.35, y=0.85, text="🏆 Undervalued",
        showarrow=False, font=dict(size=10, color="#f59e0b"),
        bgcolor="rgba(245,158,11,0.12)", borderpad=4)
    fig_scatter.add_annotation(x=0.12, y=0.48, text="😞 Checked Out",
        showarrow=False, font=dict(size=10, color="#94a3b8"),
        bgcolor="rgba(148,163,184,0.12)", borderpad=4)

    fig_scatter.update_layout(
        **PLOTLY_LAYOUT,
        height=380,
        xaxis=dict(**DEFAULT_AXIS, title="Satisfaction Level"),
        yaxis=dict(**DEFAULT_AXIS, title="Last Evaluation Score"),
        legend=dict(**DEFAULT_LEGEND, x=0.75, y=0.05),
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

# ── Row 3: Tenure spike + project count ─────────────────────────────────
col_e, col_f = st.columns(2)

with col_e:
    st.markdown("#### Turnover Rate by Tenure")
    tenure_stats = df.groupby("time_spend_company").agg(
        total=("left", "count"),
        left=("left", "sum"),
    ).reset_index()
    tenure_stats["turnover_pct"] = (tenure_stats["left"] / tenure_stats["total"] * 100).round(1)

    fig_tenure = go.Figure()
    fig_tenure.add_trace(go.Bar(
        x=tenure_stats["time_spend_company"],
        y=tenure_stats["turnover_pct"],
        marker=dict(
            color=tenure_stats["turnover_pct"],
            colorscale=[[0, "#00c897"], [0.5, "#f59e0b"], [1, "#ff6b6b"]],
            cornerradius=6,
        ),
        text=[f"{v}%" for v in tenure_stats["turnover_pct"]],
        textposition="outside",
        textfont=dict(color="#e2e8f0", size=11),
        hovertemplate="Tenure: %{x} years<br>Turnover: %{y}%<extra></extra>",
    ))
    fig_tenure.update_layout(
        **PLOTLY_LAYOUT,
        height=360,
        xaxis=dict(**DEFAULT_AXIS, title="Years at Company"),
        yaxis=dict(**DEFAULT_AXIS, title="Turnover Rate (%)"),
        showlegend=False,
    )
    st.plotly_chart(fig_tenure, use_container_width=True)

with col_f:
    st.markdown("#### Turnover Rate by Projects")
    proj_stats = df.groupby("number_project").agg(
        total=("left", "count"),
        left=("left", "sum"),
    ).reset_index()
    proj_stats["turnover_pct"] = (proj_stats["left"] / proj_stats["total"] * 100).round(1)

    fig_proj = go.Figure()
    fig_proj.add_trace(go.Bar(
        x=proj_stats["number_project"],
        y=proj_stats["turnover_pct"],
        marker=dict(
            color=proj_stats["turnover_pct"],
            colorscale=[[0, "#00c897"], [0.5, "#f59e0b"], [1, "#ff6b6b"]],
            cornerradius=6,
        ),
        text=[f"{v}%" for v in proj_stats["turnover_pct"]],
        textposition="outside",
        textfont=dict(color="#e2e8f0", size=11),
        hovertemplate="Projects: %{x}<br>Turnover: %{y}%<extra></extra>",
    ))
    fig_proj.update_layout(
        **PLOTLY_LAYOUT,
        height=360,
        xaxis=dict(**DEFAULT_AXIS, title="Number of Projects"),
        yaxis=dict(**DEFAULT_AXIS, title="Turnover Rate (%)"),
        showlegend=False,
    )
    st.plotly_chart(fig_proj, use_container_width=True)

# ── Key Insight Callout ─────────────────────────────────────────────────
st.markdown("---")
st.markdown("""
<div class="glass-card" style="text-align:center;">
    <p style="font-size:1rem; color:#94a3b8; margin-bottom:0.5rem;">KEY INSIGHT</p>
    <p style="font-size:1.15rem; color:#e2e8f0; line-height:1.7; max-width:700px; margin:0 auto;">
        Salary barely matters. The top predictors of turnover are
        <span style="color:#00d4ff; font-weight:600;">evaluation score</span> (36.2%),
        <span style="color:#3b82f6; font-weight:600;">project count</span> (35.1%), and
        <span style="color:#8b5cf6; font-weight:600;">tenure</span> (19.8%).
        Employees don't leave for more money — they leave because they're
        <em>overworked, undervalued, or ignored</em>.
    </p>
</div>
""", unsafe_allow_html=True)
