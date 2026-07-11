import streamlit as st

# ── Page config (must be first Streamlit call) ──────────────────────────
st.set_page_config(
    page_title="Salifort Motors · Employee Turnover Dashboard",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Global CSS Theme ────────────────────────────────────────────────────
st.markdown("""
<style>
    /* ── Google Font ─────────────────────────────────────── */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

    /* ── Root variables ──────────────────────────────────── */
    :root {
        --bg-primary:    #0a0e1a;
        --bg-secondary:  #111827;
        --bg-card:       rgba(17, 24, 39, 0.7);
        --bg-card-hover: rgba(23, 33, 54, 0.85);
        --border-card:   rgba(99, 179, 237, 0.12);
        --border-glow:   rgba(0, 212, 255, 0.25);
        --accent-cyan:   #00d4ff;
        --accent-blue:   #3b82f6;
        --accent-purple: #8b5cf6;
        --accent-coral:  #ff6b6b;
        --accent-amber:  #f59e0b;
        --accent-emerald:#00c897;
        --text-primary:  #f1f5f9;
        --text-secondary:#94a3b8;
        --text-muted:    #64748b;
        --glass-blur:    12px;
        --radius-lg:     16px;
        --radius-md:     12px;
        --radius-sm:     8px;
        --shadow-glow:   0 0 20px rgba(0, 212, 255, 0.08);
        --transition:    all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }

    /* ── Global resets ───────────────────────────────────── */
    html, body, [data-testid="stAppViewContainer"],
    [data-testid="stApp"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
        background: var(--bg-primary) !important;
        color: var(--text-primary) !important;
    }
    
    .main .block-container {
        padding: 2rem 2.5rem 3rem !important;
        max-width: 1200px !important;
    }

    /* ── Sidebar ─────────────────────────────────────────── */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0d1321 0%, #111827 100%) !important;
        border-right: 1px solid var(--border-card) !important;
    }
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] span,
    [data-testid="stSidebar"] label {
        color: var(--text-secondary) !important;
        font-family: 'Inter', sans-serif !important;
    }
    [data-testid="stSidebar"] .stRadio label span {
        font-weight: 500 !important;
    }
    
    /* ── Navigation styling ──────────────────────────────── */
    [data-testid="stSidebarNav"] {
        padding-top: 1.5rem;
    }
    [data-testid="stSidebarNav"] a {
        color: var(--text-secondary) !important;
        font-weight: 500 !important;
        padding: 0.6rem 1rem !important;
        border-radius: var(--radius-sm) !important;
        transition: var(--transition) !important;
    }
    [data-testid="stSidebarNav"] a:hover {
        background: rgba(0, 212, 255, 0.08) !important;
        color: var(--accent-cyan) !important;
    }
    [data-testid="stSidebarNav"] a[aria-selected="true"] {
        background: rgba(0, 212, 255, 0.12) !important;
        color: var(--accent-cyan) !important;
        font-weight: 600 !important;
    }

    /* ── Headers ─────────────────────────────────────────── */
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Inter', sans-serif !important;
        color: var(--text-primary) !important;
        font-weight: 700 !important;
    }
    h1 { font-weight: 800 !important; letter-spacing: -0.03em !important; }

    /* ── Metric cards ────────────────────────────────────── */
    [data-testid="stMetric"] {
        background: var(--bg-card) !important;
        backdrop-filter: blur(var(--glass-blur)) !important;
        -webkit-backdrop-filter: blur(var(--glass-blur)) !important;
        border: 1px solid var(--border-card) !important;
        border-radius: var(--radius-md) !important;
        padding: 1.2rem 1.4rem !important;
        box-shadow: var(--shadow-glow) !important;
        transition: var(--transition) !important;
    }
    [data-testid="stMetric"]:hover {
        border-color: var(--border-glow) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 24px rgba(0, 212, 255, 0.12) !important;
    }
    [data-testid="stMetricLabel"] {
        color: var(--text-secondary) !important;
        font-weight: 500 !important;
        font-size: 0.85rem !important;
        text-transform: uppercase !important;
        letter-spacing: 0.05em !important;
    }
    [data-testid="stMetricValue"] {
        color: var(--text-primary) !important;
        font-weight: 700 !important;
        font-size: 1.8rem !important;
    }
    [data-testid="stMetricDelta"] > div {
        font-weight: 500 !important;
    }

    /* ── Buttons ─────────────────────────────────────────── */
    .stButton > button {
        background: linear-gradient(135deg, var(--accent-cyan), var(--accent-blue)) !important;
        color: #fff !important;
        border: none !important;
        border-radius: var(--radius-sm) !important;
        font-family: 'Inter', sans-serif !important;
        font-weight: 600 !important;
        padding: 0.65rem 1.5rem !important;
        transition: var(--transition) !important;
        text-transform: none !important;
        letter-spacing: 0 !important;
    }
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 24px rgba(0, 212, 255, 0.3) !important;
        filter: brightness(1.1) !important;
    }
    .stButton > button:active {
        transform: translateY(0) !important;
    }

    /* ── Download button ─────────────────────────────────── */
    .stDownloadButton > button {
        background: linear-gradient(135deg, var(--accent-emerald), #059669) !important;
        color: #fff !important;
        border: none !important;
        border-radius: var(--radius-sm) !important;
        font-family: 'Inter', sans-serif !important;
        font-weight: 600 !important;
    }
    .stDownloadButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 24px rgba(0, 200, 151, 0.3) !important;
    }

    /* ── Selectbox / Inputs ──────────────────────────────── */
    [data-testid="stSelectbox"] > div > div,
    .stSelectbox > div > div {
        background: var(--bg-secondary) !important;
        border: 1px solid var(--border-card) !important;
        border-radius: var(--radius-sm) !important;
        color: var(--text-primary) !important;
    }
    .stSlider label, .stSelectbox label, .stNumberInput label,
    .stTextInput label, .stFileUploader label {
        color: var(--text-secondary) !important;
        font-weight: 500 !important;
        font-family: 'Inter', sans-serif !important;
    }

    /* ── Slider track ────────────────────────────────────── */
    .stSlider [data-testid="stThumbValue"] {
        color: var(--accent-cyan) !important;
        font-weight: 600 !important;
    }

    /* ── Tabs ────────────────────────────────────────────── */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem !important;
        background: transparent !important;
        border-bottom: 1px solid var(--border-card) !important;
    }
    .stTabs [data-baseweb="tab"] {
        background: transparent !important;
        color: var(--text-secondary) !important;
        font-weight: 500 !important;
        border-radius: var(--radius-sm) var(--radius-sm) 0 0 !important;
        padding: 0.6rem 1.2rem !important;
        transition: var(--transition) !important;
    }
    .stTabs [data-baseweb="tab"]:hover {
        color: var(--accent-cyan) !important;
        background: rgba(0, 212, 255, 0.06) !important;
    }
    .stTabs [aria-selected="true"] {
        color: var(--accent-cyan) !important;
        border-bottom: 2px solid var(--accent-cyan) !important;
        font-weight: 600 !important;
    }

    /* ── Dataframe ───────────────────────────────────────── */
    [data-testid="stDataFrame"] {
        border: 1px solid var(--border-card) !important;
        border-radius: var(--radius-md) !important;
        overflow: hidden !important;
    }

    /* ── File uploader ───────────────────────────────────── */
    [data-testid="stFileUploader"] {
        background: var(--bg-card) !important;
        border: 2px dashed var(--border-card) !important;
        border-radius: var(--radius-md) !important;
        padding: 1rem !important;
        transition: var(--transition) !important;
    }
    [data-testid="stFileUploader"]:hover {
        border-color: var(--accent-cyan) !important;
    }

    /* ── Expander ────────────────────────────────────────── */
    .streamlit-expanderHeader {
        background: var(--bg-card) !important;
        border: 1px solid var(--border-card) !important;
        border-radius: var(--radius-sm) !important;
        color: var(--text-primary) !important;
        font-weight: 500 !important;
    }

    /* ── Progress bar ────────────────────────────────────── */
    .stProgress > div > div {
        background: var(--bg-secondary) !important;
        border-radius: 20px !important;
    }
    .stProgress > div > div > div {
        background: linear-gradient(90deg, var(--accent-cyan), var(--accent-blue)) !important;
        border-radius: 20px !important;
    }

    /* ── Dividers ────────────────────────────────────────── */
    hr {
        border-color: var(--border-card) !important;
        opacity: 0.5 !important;
    }

    /* ── Scrollbar ───────────────────────────────────────── */
    ::-webkit-scrollbar { width: 6px; height: 6px; }
    ::-webkit-scrollbar-track { background: var(--bg-primary); }
    ::-webkit-scrollbar-thumb {
        background: var(--text-muted);
        border-radius: 3px;
    }
    ::-webkit-scrollbar-thumb:hover { background: var(--text-secondary); }

    /* ── Custom glass card class ──────────────────────────── */
    .glass-card {
        background: var(--bg-card);
        backdrop-filter: blur(var(--glass-blur));
        -webkit-backdrop-filter: blur(var(--glass-blur));
        border: 1px solid var(--border-card);
        border-radius: var(--radius-lg);
        padding: 1.8rem;
        box-shadow: var(--shadow-glow);
        transition: var(--transition);
        margin-bottom: 1rem;
    }
    .glass-card:hover {
        border-color: var(--border-glow);
        box-shadow: 0 4px 30px rgba(0, 212, 255, 0.1);
    }

    /* ── Gradient text ───────────────────────────────────── */
    .gradient-text {
        background: linear-gradient(135deg, #00d4ff, #3b82f6, #8b5cf6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }

    /* ── Badge styles ────────────────────────────────────── */
    .badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        letter-spacing: 0.03em;
        text-transform: uppercase;
    }
    .badge-danger { background: rgba(255,107,107,0.15); color: #ff6b6b; }
    .badge-warning { background: rgba(245,158,11,0.15); color: #f59e0b; }
    .badge-success { background: rgba(0,200,151,0.15); color: #00c897; }
    .badge-info { background: rgba(0,212,255,0.15); color: #00d4ff; }

    /* ── Risk flag items ─────────────────────────────────── */
    .risk-flag {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        padding: 0.8rem 1.2rem;
        background: var(--bg-card);
        border-left: 3px solid;
        border-radius: 0 var(--radius-sm) var(--radius-sm) 0;
        margin-bottom: 0.5rem;
        transition: var(--transition);
    }
    .risk-flag:hover { transform: translateX(4px); }
    .risk-flag.critical { border-color: #ff6b6b; }
    .risk-flag.warning  { border-color: #f59e0b; }
    .risk-flag.ok       { border-color: #00c897; }

    /* ── Stat highlight ──────────────────────────────────── */
    .stat-value {
        font-size: 2.2rem;
        font-weight: 800;
        line-height: 1;
    }
    .stat-label {
        font-size: 0.8rem;
        color: var(--text-secondary);
        text-transform: uppercase;
        letter-spacing: 0.06em;
        margin-top: 0.3rem;
    }

    /* ── Animate in ──────────────────────────────────────── */
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(20px); }
        to   { opacity: 1; transform: translateY(0); }
    }
    .animate-in {
        animation: fadeInUp 0.6s ease-out forwards;
    }

    /* ── Hide streamlit default ──────────────────────────── */
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    header[data-testid="stHeader"] {
        background: rgba(10, 14, 26, 0.8) !important;
        backdrop-filter: blur(10px) !important;
    }
</style>
""", unsafe_allow_html=True)

# ── Navigation ──────────────────────────────────────────────────────────
overview_page   = st.Page("pages/1_🏠_Overview.py",   title="Overview",       icon="🏠", default=True)
explorer_page   = st.Page("pages/2_📊_Explorer.py",   title="Data Explorer",  icon="📊")
predictor_page  = st.Page("pages/3_🔮_Predictor.py",  title="Predictor",      icon="🔮")
batch_page      = st.Page("pages/4_📋_Batch_Predict.py", title="Batch Predict", icon="📋")
about_page      = st.Page("pages/5_ℹ️_About.py",      title="About",          icon="ℹ️")

pg = st.navigation([overview_page, explorer_page, predictor_page, batch_page, about_page])
pg.run()
