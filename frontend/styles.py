# TRACE Design System & Custom CSS for Streamlit

TRACE_CSS = """
<style>
/* Base Dark Theme Overrides */
.stApp {
    background-color: #141414 !important;
    color: #F2EFE9 !important;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

/* Header & Typography */
h1, h2, h3, h4, h5, h6 {
    color: #F2EFE9 !important;
    font-weight: 600;
}

p, span, label {
    color: #D6D2CA !important;
}

/* Workflow Step Progress Banner */
.step-banner {
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: #1C1C1C;
    border: 1px solid #303030;
    border-radius: 10px;
    padding: 10px 16px;
    margin-bottom: 20px;
    gap: 8px;
}

.step-item {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 0.88rem;
    font-weight: 600;
    color: #777777;
}

.step-item.active {
    color: #E5A84B;
}

.step-item.completed {
    color: #56D364;
}

.step-num {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 24px;
    height: 24px;
    border-radius: 50%;
    background: #282828;
    color: #999;
    font-size: 0.78rem;
}

.step-num.active {
    background: #C98A2C;
    color: #121212;
    font-weight: 800;
}

.step-num.completed {
    background: #238636;
    color: #FFFFFF;
}

/* Mode Switcher Pill Banner */
.mode-banner {
    background: #1D1B17;
    border: 1px solid #4A3A22;
    border-radius: 10px;
    padding: 12px 16px;
    margin-bottom: 18px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

/* Primary Accent Buttons */
.stButton > button {
    background: linear-gradient(135deg, #C98A2C 0%, #A66D1B 100%) !important;
    color: #121212 !important;
    font-weight: 700 !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 0.55rem 1.25rem !important;
    transition: all 0.2s ease-in-out !important;
    box-shadow: 0 4px 12px rgba(201, 138, 44, 0.25) !important;
}

.stButton > button:hover {
    background: linear-gradient(135deg, #E09F3E 0%, #C98A2C 100%) !important;
    transform: translateY(-2px);
    box-shadow: 0 6px 18px rgba(201, 138, 44, 0.4) !important;
}

/* Form Inputs & Text Areas */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stSelectbox > div > div > div {
    background-color: #202020 !important;
    color: #F2EFE9 !important;
    border: 1px solid #383838 !important;
    border-radius: 8px !important;
}

.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: #C98A2C !important;
    box-shadow: 0 0 0 1px #C98A2C !important;
}

/* Custom Cards */
.trace-card {
    background-color: #1E1E1E;
    border: 1px solid #333333;
    border-radius: 12px;
    padding: 1.25rem;
    margin-bottom: 1rem;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
}

.trace-card-highlight {
    background: linear-gradient(180deg, #27221A 0%, #1E1B15 100%);
    border: 2px solid #C98A2C;
    border-radius: 12px;
    padding: 1.25rem;
    margin-bottom: 1.25rem;
    box-shadow: 0 8px 24px rgba(201, 138, 44, 0.22);
}

.trace-card-failure {
    background: linear-gradient(180deg, #2A1C1C 0%, #201515 100%);
    border: 2px solid #DA3633;
    border-radius: 12px;
    padding: 1.25rem;
    margin-bottom: 1.25rem;
    box-shadow: 0 8px 24px rgba(218, 54, 51, 0.2);
}

.trace-badge-amber {
    background-color: rgba(201, 138, 44, 0.18);
    color: #E5A84B;
    border: 1px solid #C98A2C;
    padding: 3px 10px;
    border-radius: 6px;
    font-size: 0.85rem;
    font-weight: 600;
    display: inline-block;
}

.trace-badge-green {
    background-color: rgba(46, 160, 67, 0.2);
    color: #56D364;
    border: 1px solid #2EA043;
    padding: 4px 12px;
    border-radius: 6px;
    font-weight: 700;
    display: inline-block;
}

.trace-badge-red {
    background-color: rgba(248, 81, 73, 0.2);
    color: #F85149;
    border: 1px solid #DA3633;
    padding: 4px 12px;
    border-radius: 6px;
    font-weight: 700;
    display: inline-block;
}

.trace-badge-gray {
    background-color: rgba(130, 130, 130, 0.18);
    color: #B0B0B0;
    border: 1px solid #555555;
    padding: 3px 10px;
    border-radius: 6px;
    font-size: 0.85rem;
    font-weight: 600;
    display: inline-block;
}

/* Plain-Language Driver Explanation Banner (Priority 3) */
.driver-banner {
    background: rgba(201, 138, 44, 0.12);
    border: 1px solid #C98A2C;
    border-radius: 8px;
    padding: 10px 14px;
    margin: 10px 0;
    display: flex;
    align-items: center;
    gap: 10px;
}

.driver-text {
    font-size: 0.95rem;
    font-weight: 600;
    color: #E5A84B;
}

/* Score Breakdown Bar */
.score-bar-bg {
    background-color: #2D2D2D;
    border-radius: 6px;
    height: 10px;
    width: 100%;
    margin: 4px 0 10px 0;
    overflow: hidden;
}

.score-bar-fill-amber {
    background: linear-gradient(90deg, #C98A2C, #F4B24B);
    height: 100%;
    border-radius: 6px;
}

.score-bar-fill-blue {
    background: linear-gradient(90deg, #388BFD, #58A6FF);
    height: 100%;
    border-radius: 6px;
}

.score-bar-fill-green {
    background: linear-gradient(90deg, #238636, #3FB950);
    height: 100%;
    border-radius: 6px;
}

.score-bar-fill-purple {
    background: linear-gradient(90deg, #8957E5, #A371F7);
    height: 100%;
    border-radius: 6px;
}

/* Header bar */
.trace-header {
    background: linear-gradient(180deg, #282116 0%, #181818 100%);
    border-bottom: 1px solid #3E321E;
    padding: 1.4rem 1.6rem 1.1rem 1.6rem;
    border-radius: 12px;
    margin-bottom: 1.25rem;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
}

/* Release Audit Certificate Box */
.audit-box {
    background: #18221B;
    border: 1px dashed #2EA043;
    border-radius: 10px;
    padding: 16px;
    margin-top: 14px;
    font-family: monospace;
    font-size: 0.88rem;
    color: #D6D2CA;
}
</style>
"""
