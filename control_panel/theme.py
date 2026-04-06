"""Modern theme for the Agentic SDLC Control Panel.

Call apply_theme() at the top of every page for consistent styling.
"""
import streamlit as st


def apply_theme():
    """Apply modern CSS theme to the Streamlit app."""
    st.markdown("""
    <style>
    /* ─── Global ─── */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    .stApp {
        font-family: 'Inter', sans-serif;
    }

    /* ─── Hide default Streamlit branding ─── */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* ─── Sidebar ─── */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%);
    }
    [data-testid="stSidebar"] .stMarkdown p,
    [data-testid="stSidebar"] .stMarkdown h1,
    [data-testid="stSidebar"] .stMarkdown h2,
    [data-testid="stSidebar"] .stMarkdown h3 {
        color: #e2e8f0 !important;
    }
    [data-testid="stSidebar"] .stCaption p {
        color: #94a3b8 !important;
    }

    /* ─── Cards ─── */
    .metric-card {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border: 1px solid #334155;
        border-radius: 16px;
        padding: 24px;
        margin: 8px 0;
        transition: transform 0.2s, box-shadow 0.2s;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(59, 130, 246, 0.15);
    }
    .metric-card h3 {
        color: #94a3b8;
        font-size: 0.85rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin: 0 0 8px 0;
    }
    .metric-card .value {
        color: #f1f5f9;
        font-size: 2rem;
        font-weight: 700;
        margin: 0;
    }
    .metric-card .subtitle {
        color: #64748b;
        font-size: 0.8rem;
        margin-top: 4px;
    }

    /* ─── Gradient Headers ─── */
    .gradient-header {
        background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 50%, #ec4899 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-weight: 800;
        font-size: 2.5rem;
        margin-bottom: 0.5rem;
    }
    .gradient-subheader {
        color: #94a3b8;
        font-size: 1.1rem;
        font-weight: 400;
        margin-bottom: 2rem;
    }

    /* ─── Phase Pills ─── */
    .phase-pill {
        display: inline-block;
        padding: 6px 16px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        margin: 4px;
    }
    .phase-govern { background: #1e3a5f; color: #60a5fa; }
    .phase-design { background: #3b1f5e; color: #a78bfa; }
    .phase-build { background: #1e3b2e; color: #4ade80; }
    .phase-test { background: #3b3b1e; color: #fbbf24; }
    .phase-deploy { background: #3b1e1e; color: #f87171; }
    .phase-operate { background: #1e3b3b; color: #2dd4bf; }
    .phase-oversight { background: #3b2e1e; color: #fb923c; }

    /* ─── Status Badges ─── */
    .status-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    .status-ready { background: #052e16; color: #4ade80; border: 1px solid #166534; }
    .status-running { background: #172554; color: #60a5fa; border: 1px solid #1e40af; }
    .status-hitl { background: #431407; color: #fb923c; border: 1px solid #9a3412; }
    .status-failed { background: #450a0a; color: #f87171; border: 1px solid #991b1b; }
    .status-pending { background: #1e293b; color: #64748b; border: 1px solid #334155; }

    /* ─── Pipeline Step ─── */
    .pipeline-step {
        background: #1e293b;
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 16px 20px;
        margin: 6px 0;
        display: flex;
        align-items: center;
        gap: 16px;
        transition: all 0.2s;
    }
    .pipeline-step:hover {
        border-color: #3b82f6;
        background: #1e293b;
    }
    .pipeline-step .step-num {
        background: #334155;
        color: #94a3b8;
        width: 36px;
        height: 36px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 700;
        font-size: 0.85rem;
        flex-shrink: 0;
    }
    .pipeline-step.completed .step-num {
        background: #166534;
        color: #4ade80;
    }
    .pipeline-step.running .step-num {
        background: #1e40af;
        color: #60a5fa;
        animation: pulse 2s infinite;
    }

    /* ─── HITL Banner ─── */
    .hitl-banner {
        background: linear-gradient(135deg, #431407 0%, #7c2d12 100%);
        border: 1px solid #ea580c;
        border-radius: 12px;
        padding: 16px 24px;
        margin: 16px 0;
    }
    .hitl-banner h4 {
        color: #fdba74;
        margin: 0 0 8px 0;
    }
    .hitl-banner p {
        color: #fed7aa;
        margin: 0;
    }

    /* ─── Cost Gauge ─── */
    .cost-gauge {
        background: #1e293b;
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
    }
    .cost-gauge .amount {
        font-size: 2.5rem;
        font-weight: 800;
        color: #4ade80;
    }
    .cost-gauge .label {
        color: #94a3b8;
        font-size: 0.85rem;
    }

    /* ─── Animations ─── */
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
    @keyframes slideIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .animate-in {
        animation: slideIn 0.5s ease-out;
    }

    /* ─── Agent Card ─── */
    .agent-card {
        background: #1e293b;
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 20px;
        margin: 8px 0;
        transition: all 0.2s;
    }
    .agent-card:hover {
        border-color: #3b82f6;
        box-shadow: 0 4px 15px rgba(59, 130, 246, 0.1);
    }

    /* ─── Progress Bar ─── */
    .progress-container {
        background: #334155;
        border-radius: 10px;
        height: 12px;
        overflow: hidden;
        margin: 8px 0;
    }
    .progress-fill {
        background: linear-gradient(90deg, #3b82f6, #8b5cf6);
        height: 100%;
        border-radius: 10px;
        transition: width 0.5s ease;
    }

    /* ─── Streamlit overrides ─── */
    .stMetric label {
        color: #94a3b8 !important;
    }
    .stMetric [data-testid="stMetricValue"] {
        color: #f1f5f9 !important;
    }
    div[data-testid="stExpander"] {
        border: 1px solid #334155;
        border-radius: 12px;
        overflow: hidden;
    }
    .stButton > button {
        border-radius: 10px;
        font-weight: 600;
        padding: 8px 24px;
        transition: all 0.2s;
    }
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
    }
    .stTextInput > div > div {
        border-radius: 10px;
    }
    .stSelectbox > div > div {
        border-radius: 10px;
    }
    .stDataFrame {
        border-radius: 12px;
        overflow: hidden;
    }
    </style>
    """, unsafe_allow_html=True)


def metric_card(title: str, value: str, subtitle: str = "") -> str:
    """Return HTML for a styled metric card."""
    sub = f'<p class="subtitle">{subtitle}</p>' if subtitle else ""
    return f"""
    <div class="metric-card">
        <h3>{title}</h3>
        <p class="value">{value}</p>
        {sub}
    </div>
    """


def gradient_header(title: str, subtitle: str = "") -> None:
    """Render a gradient header."""
    st.markdown(f'<h1 class="gradient-header">{title}</h1>', unsafe_allow_html=True)
    if subtitle:
        st.markdown(f'<p class="gradient-subheader">{subtitle}</p>', unsafe_allow_html=True)


def phase_pill(phase: str) -> str:
    """Return HTML for a phase pill badge."""
    return f'<span class="phase-pill phase-{phase}">{phase.upper()}</span>'


def status_badge(status: str) -> str:
    """Return HTML for a status badge."""
    return f'<span class="status-badge status-{status}">{status.replace("_", " ").title()}</span>'


def hitl_banner(title: str, description: str) -> None:
    """Render a HITL attention banner."""
    st.markdown(f"""
    <div class="hitl-banner">
        <h4>👤 HUMAN IN THE LOOP — {title}</h4>
        <p>{description}</p>
    </div>
    """, unsafe_allow_html=True)


def progress_bar(percentage: float, label: str = "") -> None:
    """Render a custom gradient progress bar."""
    st.markdown(f"""
    <div style="margin: 4px 0;">
        <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
            <span style="color: #94a3b8; font-size: 0.8rem;">{label}</span>
            <span style="color: #f1f5f9; font-size: 0.8rem; font-weight: 600;">{percentage:.0f}%</span>
        </div>
        <div class="progress-container">
            <div class="progress-fill" style="width: {min(percentage, 100)}%"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)
