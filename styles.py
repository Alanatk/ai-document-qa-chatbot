import streamlit as st


def load_css():
    """Injects high-end, responsive custom CSS supporting dark & light theme

    adaptability, modern glassmorphism cards, glowing action buttons, pill
    tabs, and polished metric cards.
    """
    st.markdown(
        """
    <style>
    /* Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif !important;
    }

    /* Main Container Padding */
    .block-container {
        max-width: 1280px !important;
        padding-top: 1.25rem !important;
        padding-bottom: 2.5rem !important;
    }

    /* Sidebar Header */
    .sidebar-header {
        background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%) !important;
        padding: 1.2rem !important;
        border-radius: 14px !important;
        text-align: center !important;
        margin-bottom: 1.25rem !important;
        box-shadow: 0 8px 20px rgba(37, 99, 235, 0.3) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
    }

    .sidebar-title {
        font-size: 1.3rem !important;
        font-weight: 800 !important;
        color: #ffffff !important;
        margin: 0 !important;
        letter-spacing: -0.02em !important;
        line-height: 1.3 !important;
    }

    .sidebar-subtitle {
        font-size: 0.8rem !important;
        color: #e0f2fe !important;
        margin-top: 4px !important;
        font-weight: 500 !important;
        opacity: 0.95 !important;
    }

    /* Modern Metric Grid */
    .metric-grid {
        display: grid !important;
        grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)) !important;
        gap: 1.1rem !important;
        margin-top: 0.75rem !important;
        margin-bottom: 1.75rem !important;
    }

    .stat-card {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%) !important;
        padding: 1.25rem 1.4rem !important;
        border-radius: 14px !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-top: 4px solid #3b82f6 !important;
        box-shadow: 0 6px 18px rgba(0, 0, 0, 0.25) !important;
        transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }

    .stat-card:hover {
        transform: translateY(-3px) !important;
        box-shadow: 0 10px 28px rgba(59, 130, 246, 0.3) !important;
        border-top-color: #60a5fa !important;
    }

    .stat-header {
        display: flex !important;
        align-items: center !important;
        gap: 0.5rem !important;
        margin-bottom: 0.4rem !important;
    }

    .stat-icon {
        font-size: 1.1rem !important;
    }

    .stat-label {
        font-size: 0.78rem !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.06em !important;
        color: #94a3b8 !important;
    }

    .stat-value {
        font-size: 2.1rem !important;
        font-weight: 800 !important;
        color: #ffffff !important;
        letter-spacing: -0.03em !important;
    }

    /* Custom Streamlit Tabs Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px !important;
        background: rgba(30, 41, 59, 0.6) !important;
        padding: 6px !important;
        border-radius: 14px !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
    }

    .stTabs [data-baseweb="tab"] {
        height: 44px !important;
        border-radius: 10px !important;
        font-weight: 700 !important;
        font-size: 0.9rem !important;
        color: #94a3b8 !important;
        padding: 0px 18px !important;
        border: none !important;
        transition: all 0.2s ease !important;
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #2563eb 0%, #3b82f6 100%) !important;
        color: #ffffff !important;
        box-shadow: 0 4px 14px rgba(37, 99, 235, 0.4) !important;
    }

    /* Override Streamlit Default Red Primary Buttons to Royal Blue */
    button[kind="primary"], 
    div.stButton > button[kind="primary"],
    .stButton > button:first-child {
        background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%) !important;
        color: #ffffff !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        font-weight: 700 !important;
        border-radius: 10px !important;
        box-shadow: 0 4px 14px rgba(37, 99, 235, 0.3) !important;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }

    button[kind="primary"]:hover,
    div.stButton > button[kind="primary"]:hover,
    .stButton > button:first-child:hover {
        background: linear-gradient(135deg, #1d4ed8 0%, #1e40af 100%) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 22px rgba(37, 99, 235, 0.45) !important;
    }

    div.stButton > button {
        border-radius: 10px !important;
        font-weight: 700 !important;
        padding: 0.6rem 1.2rem !important;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }

    /* File Uploader Container */
    section[data-testid="stFileUploader"] {
        background: rgba(15, 23, 42, 0.8) !important;
        border: 2px dashed #3b82f6 !important;
        border-radius: 14px !important;
        padding: 1.25rem !important;
    }

    /* Quiz Cards */
    .quiz-card {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-left: 4px solid #3b82f6 !important;
        border-radius: 14px !important;
        padding: 1.5rem !important;
        margin-bottom: 1.25rem !important;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2) !important;
    }

    .quiz-question {
        font-size: 1.1rem !important;
        font-weight: 700 !important;
        color: #ffffff !important;
        margin-bottom: 0.5rem !important;
    }

    /* Flashcard UI */
    .flashcard-box {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%) !important;
        border: 2px solid rgba(59, 130, 246, 0.4) !important;
        border-radius: 18px !important;
        padding: 2.5rem !important;
        text-align: center !important;
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.3) !important;
        min-height: 230px !important;
        display: flex !important;
        flex-direction: column !important;
        justify-content: center !important;
        align-items: center !important;
        margin: 1.5rem 0 !important;
    }

    .flashcard-title {
        font-size: 0.85rem !important;
        font-weight: 800 !important;
        color: #60a5fa !important;
        text-transform: uppercase !important;
        letter-spacing: 0.12em !important;
        margin-bottom: 1rem !important;
    }

    .flashcard-content {
        font-size: 1.3rem !important;
        font-weight: 700 !important;
        color: #ffffff !important;
        line-height: 1.6 !important;
    }

    /* Confidence Badges */
    .badge-confidence {
        display: inline-flex !important;
        align-items: center !important;
        gap: 4px !important;
        padding: 4px 12px !important;
        border-radius: 20px !important;
        font-size: 0.78rem !important;
        font-weight: 700 !important;
        margin-top: 6px !important;
        margin-right: 6px !important;
    }

    .badge-high {
        background: rgba(34, 197, 94, 0.15) !important;
        color: #4ade80 !important;
        border: 1px solid rgba(34, 197, 94, 0.3) !important;
    }

    .badge-medium {
        background: rgba(234, 179, 8, 0.15) !important;
        color: #facc15 !important;
        border: 1px solid rgba(234, 179, 8, 0.3) !important;
    }

    .badge-low {
        background: rgba(239, 68, 68, 0.15) !important;
        color: #f87171 !important;
        border: 1px solid rgba(239, 68, 68, 0.3) !important;
    }

    .source-box {
        background: rgba(30, 41, 59, 0.7) !important;
        border-left: 4px solid #3b82f6 !important;
        padding: 12px 16px !important;
        margin-top: 10px !important;
        border-radius: 6px 10px 10px 6px !important;
        font-size: 0.88rem !important;
        color: #e2e8f0 !important;
        border-top: 1px solid rgba(255, 255, 255, 0.05) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.05) !important;
        border-bottom: 1px solid rgba(255, 255, 255, 0.05) !important;
    }

    /* Progress Bar */
    .stProgress > div > div > div > div {
        background-image: linear-gradient(90deg, #2563eb, #60a5fa) !important;
        border-radius: 8px !important;
    }

    /* Footer Text */
    .footer-text {
        text-align: center !important;
        font-size: 0.8rem !important;
        color: #64748b !important;
        margin-top: 2rem !important;
        padding-top: 1rem !important;
        border-top: 1px solid rgba(225, 231, 239, 0.1) !important;
    }
    </style>
    """,
        unsafe_allow_html=True,
    )