import streamlit as st
import pandas as pd
import numpy as np
import pickle
import plotly.graph_objects as go

# Page config
st.set_page_config(
    page_title="Employee Turnover Predictor",
    page_icon="🔮",
    layout="centered"
)

# Custom CSS
st.markdown("""
<style>
    .main { padding-top: 1rem; }
    .stSlider > label { font-weight: 500; }
    .result-box {
        padding: 1.5rem;
        border-radius: 12px;
        text-align: center;
        margin: 1rem 0;
    }
    .leave-box { background: #fff0f0; border: 2px solid #e24b4a; }
    .stay-box  { background: #f0faf4; border: 2px solid #1d9e75; }
    .metric-row { display: flex; gap: 1rem; justify-content: center; margin-top: 0.5rem; }
</style>
""", unsafe_allow_html=True)

# Load model
@st.cache_resource
def load_model():
    with open("hr_rf1_model.pkl", "rb") as f:
        return pickle.load(f)

model = load_model()

FEATURE_IMPORTANCE = {
    'last_evaluation': 0.362,
    'number_project': 0.351,
    'time_spend_company': 0.198,
    'overworked': 0.083,
    'satisfaction_level': 0.006
}

# Header
st.markdown("## 🔮 Employee Turnover Predictor")
st.markdown("Built on a Random Forest model trained on 15,000 employees · 96.2% accuracy · 93.8% AUC")
st.markdown("---")

# Input form
st.markdown("### Enter Employee Details")

col1, col2 = st.columns(2)

with col1:
    satisfaction = st.slider("😊 Satisfaction Level", 0.0, 1.0, 0.5, 0.01,
        help="Employee's self-reported satisfaction (0 = miserable, 1 = thriving)")
    last_eval = st.slider("📊 Last Evaluation Score", 0.0, 1.0, 0.7, 0.01,
        help="Manager's performance evaluation score")
    num_projects = st.slider("📁 Number of Projects", 2, 7, 4,
        help="How many projects the employee is currently handling")
    monthly_hours = st.slider("⏰ Avg Monthly Hours", 80, 320, 160,
        help="Average hours worked per month (normal = ~167)")

with col2:
    tenure = st.slider("🗓️ Years at Company", 1, 10, 3,
        help="How many years they've been at Salifort Motors")
    work_accident = st.selectbox("🚑 Had Work Accident?", ["No", "Yes"])
    promotion = st.selectbox("🏆 Promoted in Last 5 Years?", ["No", "Yes"])
    department = st.selectbox("🏢 Department", [
        "sales", "support", "technical", "hr", "IT",
        "RandD", "product_mng", "marketing", "accounting", "management"
    ])
    salary = st.selectbox("💰 Salary Level", ["low", "medium", "high"])

st.markdown("---")

# Predict button
if st.button("🔮 Predict Turnover Risk", use_container_width=True, type="primary"):

    overworked = 1 if monthly_hours > 175 else 0

    input_data = {
        'satisfaction_level': satisfaction,
        'last_evaluation': last_eval,
        'number_project': num_projects,
        'average_montly_hours': monthly_hours,
        'time_spend_company': tenure,
        'Work_accident': 1 if work_accident == "Yes" else 0,
        'promotion_last_5years': 1 if promotion == "Yes" else 0,
        'overworked': overworked,
        'Department_IT': 1 if department == "IT" else 0,
        'Department_RandD': 1 if department == "RandD" else 0,
        'Department_accounting': 1 if department == "accounting" else 0,
        'Department_hr': 1 if department == "hr" else 0,
        'Department_management': 1 if department == "management" else 0,
        'Department_marketing': 1 if department == "marketing" else 0,
        'Department_product_mng': 1 if department == "product_mng" else 0,
        'Department_sales': 1 if department == "sales" else 0,
        'Department_support': 1 if department == "support" else 0,
        'Department_technical': 1 if department == "technical" else 0,
        'salary_high': 1 if salary == "high" else 0,
        'salary_low': 1 if salary == "low" else 0,
        'salary_medium': 1 if salary == "medium" else 0,
    }

    df_input = pd.DataFrame([input_data])
    prediction = model.predict(df_input)[0]
    proba = model.predict_proba(df_input)[0]
    leave_prob = proba[1]
    stay_prob = proba[0]

    # Result
    if prediction == 1:
        st.markdown(f"""
        <div class="result-box leave-box">
            <h2 style="color:#e24b4a; margin:0;">⚠️ HIGH RISK — Likely to Leave</h2>
            <p style="font-size:1.1rem; margin:0.5rem 0 0;">Probability of leaving: <strong>{leave_prob:.1%}</strong></p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="result-box stay-box">
            <h2 style="color:#1d9e75; margin:0;">✅ LOW RISK — Likely to Stay</h2>
            <p style="font-size:1.1rem; margin:0.5rem 0 0;">Probability of staying: <strong>{stay_prob:.1%}</strong></p>
        </div>
        """, unsafe_allow_html=True)

    # Probability gauge
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=round(leave_prob * 100, 1),
        title={'text': "Turnover Risk %", 'font': {'size': 16}},
        gauge={
            'axis': {'range': [0, 100]},
            'bar': {'color': "#e24b4a" if leave_prob > 0.5 else "#1d9e75"},
            'steps': [
                {'range': [0, 30], 'color': "#f0faf4"},
                {'range': [30, 60], 'color': "#fff8e6"},
                {'range': [60, 100], 'color': "#fff0f0"},
            ],
            'threshold': {
                'line': {'color': "black", 'width': 3},
                'thickness': 0.75,
                'value': 50
            }
        }
    ))
    fig.update_layout(height=260, margin=dict(t=40, b=10, l=20, r=20))
    st.plotly_chart(fig, use_container_width=True)

    # Key risk factors
    st.markdown("### 🔍 What's driving this prediction")

    flags = []
    if satisfaction < 0.3:
        flags.append(("😞 Very low satisfaction", "red"))
    if monthly_hours > 240:
        flags.append(("🔥 Severely overworked (240+ hrs/mo)", "red"))
    elif monthly_hours > 175:
        flags.append(("⏰ Overworked (175+ hrs/mo)", "orange"))
    if num_projects >= 6:
        flags.append(("📁 Too many projects (6–7)", "red"))
    if last_eval >= 0.8 and satisfaction < 0.5:
        flags.append(("🏆 High performer but low satisfaction — classic flight risk", "red"))
    if tenure == 5:
        flags.append(("🗓️ 5-year tenure — highest attrition spike in data", "orange"))
    if promotion == "No" and tenure >= 4:
        flags.append(("🚫 No promotion in 5 years despite long tenure", "orange"))
    if salary == "low" and last_eval >= 0.7:
        flags.append(("💰 Low salary despite strong performance", "orange"))
    if not flags:
        flags.append(("✅ No major red flags detected", "green"))

    for flag, color in flags:
        color_map = {"red": "#e24b4a", "orange": "#ba7517", "green": "#1d9e75"}
        st.markdown(f"<p style='color:{color_map[color]}; font-size:0.95rem;'>→ {flag}</p>",
                    unsafe_allow_html=True)

    #  Model info footer
    st.markdown("---")
    st.markdown(
        "<p style='text-align:center; color:#888; font-size:0.8rem;'>"
        "Random Forest · 100 estimators · Trained on Salifort Motors HR data (n=14,999) · "
        "Built by Bhishant as part of Google Advanced Data Analytics Capstone"
        "</p>",
        unsafe_allow_html=True
    )

# Sidebar
with st.sidebar:
    st.markdown("### 📈 Model Performance")
    st.metric("Accuracy", "96.2%")
    st.metric("Precision", "87.0%")
    st.metric("Recall", "90.4%")
    st.metric("F1 Score", "88.7%")
    st.metric("AUC", "93.8%")
    st.markdown("---")
    st.markdown("### 🔑 Top Predictors")
    for feat, imp in FEATURE_IMPORTANCE.items():
        st.progress(imp, text=f"{feat.replace('_', ' ').title()} ({imp:.1%})")
    st.markdown("---")
    st.markdown("Built by Bhishant  \nGoogle Advanced Data Analytics   \n[LinkedIn](#) · [GitHub](#)  · [Portfolio](#) ")
