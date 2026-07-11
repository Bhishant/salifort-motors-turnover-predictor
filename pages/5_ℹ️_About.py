import streamlit as st
import plotly.graph_objects as go
import numpy as np

PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, sans-serif", color="#e2e8f0"),
)

DEFAULT_AXIS = dict(gridcolor="rgba(99,179,237,0.08)", zerolinecolor="rgba(99,179,237,0.08)")

st.markdown("""
<div style="padding: 0.5rem 0 0.5rem;">
    <h1 style="font-size:2rem; margin-bottom:0.2rem;">
        ℹ️ <span class="gradient-text">About This Project</span>
    </h1>
    <p style="color:#94a3b8; font-size:0.95rem;">
        Model architecture, performance, methodology, and credits.
    </p>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

st.markdown("""
<div class="glass-card">
    <p style="font-size:0.75rem; color:#00d4ff; text-transform:uppercase; letter-spacing:0.1em; margin-bottom:0.8rem;">
        Model Architecture
    </p>
    <div style="display:grid; grid-template-columns: repeat(3, 1fr); gap:1.5rem;">
        <div>
            <p class="stat-value" style="color:#00d4ff;">Random Forest</p>
            <p class="stat-label">Algorithm</p>
        </div>
        <div>
            <p class="stat-value" style="color:#3b82f6;">100</p>
            <p class="stat-label">Estimators</p>
        </div>
        <div>
            <p class="stat-value" style="color:#8b5cf6;">14,999</p>
            <p class="stat-label">Training Samples</p>
        </div>
    </div>
    <div style="margin-top:1.5rem; display:grid; grid-template-columns: repeat(3, 1fr); gap:1.5rem;">
        <div>
            <p class="stat-value" style="color:#f59e0b; font-size:1.6rem;">18</p>
            <p class="stat-label">Input Features</p>
        </div>
        <div>
            <p class="stat-value" style="color:#00c897; font-size:1.6rem;">Binary</p>
            <p class="stat-label">Classification</p>
        </div>
        <div>
            <p class="stat-value" style="color:#ff6b6b; font-size:1.6rem;">80/20</p>
            <p class="stat-label">Train/Test Split</p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("### 📈 Model Performance")

metrics = {
    "Accuracy": (0.962, "#00d4ff"),
    "Precision": (0.870, "#3b82f6"),
    "Recall": (0.904, "#8b5cf6"),
    "F1 Score": (0.887, "#f59e0b"),
    "AUC": (0.938, "#00c897"),
}

cols = st.columns(5)
for col, (name, (val, color)) in zip(cols, metrics.items()):
    with col:
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=val * 100,
            number=dict(suffix="%", font=dict(size=24, color=color)),
            title=dict(text=name, font=dict(size=12, color="#94a3b8")),
            gauge=dict(
                axis=dict(range=[0, 100], visible=False),
                bar=dict(color=color, thickness=0.85),
                bgcolor="rgba(17,24,39,0.5)",
                borderwidth=0,
            ),
        ))
        fig.update_layout(**PLOTLY_LAYOUT, height=180, margin=dict(t=50, b=10, l=15, r=15),
                          xaxis=DEFAULT_AXIS, yaxis=DEFAULT_AXIS)
        st.plotly_chart(fig, use_container_width=True)

st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
st.markdown("### 🔑 Feature Importance")

features = {
    "Last Evaluation": 0.362,
    "Number of Projects": 0.351,
    "Tenure (Years)": 0.198,
    "Overworked": 0.083,
    "Satisfaction Level": 0.006,
}

feat_names = list(features.keys())[::-1]
feat_vals = list(features.values())[::-1]
feat_colors = ["#64748b", "#f59e0b", "#8b5cf6", "#3b82f6", "#00d4ff"][::-1]

fig_imp = go.Figure()
fig_imp.add_trace(go.Bar(
    x=feat_vals,
    y=feat_names,
    orientation="h",
    marker=dict(color=feat_colors, cornerradius=6),
    text=[f"{v:.1%}" for v in feat_vals],
    textposition="outside",
    textfont=dict(color="#e2e8f0", size=12),
    hovertemplate="<b>%{y}</b><br>Importance: %{x:.1%}<extra></extra>",
))
fig_imp.update_layout(
    **PLOTLY_LAYOUT, height=300,
    margin=dict(t=40, b=30, l=40, r=20),
    showlegend=False,
    xaxis=dict(gridcolor="rgba(99,179,237,0.08)", title="Feature Importance"),
    yaxis=dict(gridcolor="rgba(0,0,0,0)"),
)
st.plotly_chart(fig_imp, use_container_width=True)

st.markdown("### 🧮 Confusion Matrix (Test Set)")


cm = np.array([[2421, 69], [49, 461]])
labels = ["Stayed (Actual)", "Left (Actual)"]
pred_labels = ["Stayed (Predicted)", "Left (Predicted)"]

fig_cm = go.Figure(data=go.Heatmap(
    z=cm,
    x=pred_labels,
    y=labels,
    colorscale=[[0, "#0a0e1a"], [0.5, "#1e3a5f"], [1, "#00d4ff"]],
    text=cm,
    texttemplate="%{text:,}",
    textfont=dict(size=18, color="#e2e8f0"),
    hovertemplate="Actual: %{y}<br>Predicted: %{x}<br>Count: %{z:,}<extra></extra>",
    showscale=False,
))
fig_cm.update_layout(**PLOTLY_LAYOUT, height=320,
                      margin=dict(t=40, b=30, l=40, r=20),
                      xaxis=dict(gridcolor="rgba(0,0,0,0)"),
                      yaxis=dict(gridcolor="rgba(0,0,0,0)", autorange="reversed"))
st.plotly_chart(fig_cm, use_container_width=True)

st.markdown("---")
st.markdown("### 📘 Methodology")

st.markdown("""
<div class="glass-card">
    <div style="display:grid; grid-template-columns: 1fr 1fr; gap:2rem;">
        <div>
            <p style="color:#00d4ff; font-weight:600; margin-bottom:0.5rem;">Data & EDA</p>
            <ul style="color:#94a3b8; font-size:0.9rem; line-height:1.8; padding-left:1.2rem;">
                <li>Analyzed 14,999 employee records from Salifort Motors (fictional)</li>
                <li>Identified 3 turnover archetypes: Burned Out, Undervalued Overachiever, Checked-Out</li>
                <li>Engineered <code style="color:#00d4ff;">overworked</code> binary feature (175+ hrs/mo threshold)</li>
                <li>Found salary is nearly irrelevant vs. workload and evaluation</li>
            </ul>
        </div>
        <div>
            <p style="color:#3b82f6; font-weight:600; margin-bottom:0.5rem;">Modeling & Evaluation</p>
            <ul style="color:#94a3b8; font-size:0.9rem; line-height:1.8; padding-left:1.2rem;">
                <li>Compared Decision Tree vs Random Forest</li>
                <li>Random Forest chosen: better AUC (93.8% vs ~91%), less overfitting</li>
                <li>80/20 train-test split, 100 estimators</li>
                <li>One-hot encoded Department (10 categories) and Salary (3 levels)</li>
            </ul>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("### 🚀 Potential Improvements")
st.markdown("""
<div class="glass-card">
    <div style="display:grid; grid-template-columns: 1fr 1fr; gap:1rem;">
        <div style="display:flex; gap:0.6rem; align-items:start;">
            <span style="color:#00d4ff;">→</span>
            <p style="color:#94a3b8; font-size:0.9rem; margin:0;">Proper k-fold cross-validation instead of single split</p>
        </div>
        <div style="display:flex; gap:0.6rem; align-items:start;">
            <span style="color:#3b82f6;">→</span>
            <p style="color:#94a3b8; font-size:0.9rem; margin:0;">SHAP values for per-prediction explainability</p>
        </div>
        <div style="display:flex; gap:0.6rem; align-items:start;">
            <span style="color:#8b5cf6;">→</span>
            <p style="color:#94a3b8; font-size:0.9rem; margin:0;">Department-level dashboard view</p>
        </div>
        <div style="display:flex; gap:0.6rem; align-items:start;">
            <span style="color:#f59e0b;">→</span>
            <p style="color:#94a3b8; font-size:0.9rem; margin:0;">Better handling of class imbalance (~83% "stayed")</p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("---")
st.markdown("""
<div style="text-align:center; padding:2rem 0;">
    <p style="font-size:0.8rem; color:#64748b; text-transform:uppercase; letter-spacing:0.15em; margin-bottom:0.8rem;">
        Built by
    </p>
    <h2 style="font-size:1.8rem; margin-bottom:0.3rem;">
        <span class="gradient-text">Bhishant</span>
    </h2>
    <p style="color:#94a3b8; font-size:0.95rem; margin-bottom:1.2rem;">

</div>
""", unsafe_allow_html=True)
