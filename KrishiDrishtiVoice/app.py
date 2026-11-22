import html

import streamlit as st

from agriculture_engine import build_guidance, get_answer, parse_question, search
from gnani_service import synthesize_speech, transcribe_audio
from farmer_profile import repository
from farmer_profile import ui as farmer_ui


st.set_page_config(page_title="KrishiDrishti Voice", page_icon="🌾", layout="wide", initial_sidebar_state="expanded")

repository.initialize_database()
st.session_state.setdefault("appearance", "Light")
st.session_state.setdefault("farmer_language", "ಕನ್ನಡ")

IS_DARK = st.session_state.get("appearance") == "Dark"
PALETTE = {
    "ivory": "#111827" if IS_DARK else "#F5F8FC",
    "sage": "#1F2937" if IS_DARK else "#E8EEF4",
    "emerald": "#4ADE80" if IS_DARK else "#16813D",
    "forest": "#F2F5F7" if IS_DARK else "#123A2B",
    "gold": "#D6A75F" if IS_DARK else "#D18A2F",
    "muted": "#C2CDC7" if IS_DARK else "#5D6F64",
}

ROADMAP_PHASES = [
    ("Phase 1", "Language Understanding", "Understand Kannada, dialects, farmer intent, symptoms and context."),
    ("Phase 2", "Agriculture Intelligence + RAG", "Evidence-based agricultural reasoning and verified knowledge retrieval."),
    ("Phase 3", "Image Input + Disease Detection", "Visual crop analysis, disease identification and confidence."),
    ("Phase 4", "Risk Prediction", "Predict relevant agricultural risks using validated conditions and data."),
    ("Phase 5", "Farmer Profile", "Build contextual, personalized farm intelligence."),
    ("Phase 6", "Market Intelligence", "Current local prices, market comparison and harvest-time prediction."),
    ("Phase 7", "Weather Intelligence", "Forecasts, crop-specific risks and proactive notifications."),
]

roadmap_css = """
.roadmap-shell {
    max-width: 1180px;
    min-height: calc(100vh - 4rem);
    margin: -1.2rem auto 0;
    padding: 1.25rem 1.5rem 2.5rem;
    background: var(--app-bg);
    border-radius: 0.35rem;
}
.roadmap-title {
    color: var(--text-strong);
    font-size: 1.28rem;
    font-weight: 750;
    letter-spacing: -0.02em;
    margin: 0 0 1.15rem;
}
.roadmap-list {
    display: flex;
    flex-direction: column;
    gap: 0.95rem;
}
.roadmap-row {
    display: grid;
    grid-template-columns: 5.5rem minmax(0, 1fr);
    gap: 0.15rem;
    align-items: start;
    min-height: 6.25rem;
    padding: 0.85rem 1.1rem 0.9rem;
    border-radius: 0.45rem;
    background: var(--surface);
    border: 1px solid var(--border);
    box-shadow: 0 1px 0 rgba(255,255,255,0.018) inset;
}
.roadmap-phase {
    color: var(--primary);
    font-size: 0.92rem;
    font-weight: 650;
    line-height: 1.25;
    padding-top: 0.22rem;
}
.roadmap-heading {
    color: var(--text-strong);
    font-size: 1.13rem;
    font-weight: 780;
    line-height: 1.25;
    margin: 0 0 0.38rem;
}
.roadmap-description {
    color: var(--text-muted);
    font-size: 0.98rem;
    line-height: 1.42;
    margin: 0;
}
.roadmap-scroll-cue {
    color: var(--text-strong);
    text-align: right;
    font-size: 1.55rem;
    line-height: 1;
    margin-top: 0.85rem;
}
@media (max-width: 640px) {
    .roadmap-row {
        grid-template-columns: 4.5rem minmax(0, 1fr);
        min-height: 7rem;
        padding: 0.8rem;
    }
    .roadmap-heading { font-size: 1.02rem; }
    .roadmap-description { font-size: 0.91rem; }
}
.dashboard-hero {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 1.5rem;
    min-height: 10rem;
    padding: 1.6rem 2rem;
    margin-bottom: 0.35rem;
    border: 1px solid rgba(255,255,255,0.2);
    border-radius: 1rem;
    background: linear-gradient(112deg, #0b5b39 0%, #148444 62%, #35a852 100%);
    color: #ffffff;
    box-shadow: 0 0.5rem 1.5rem rgba(18,58,43,0.12);
}
.dashboard-hero-copy { max-width: 48rem; }
.dashboard-eyebrow {
    color: #c8f3d4;
    font-size: 0.72rem;
    font-weight: 750;
    letter-spacing: 0.13em;
}
.dashboard-hero h1 {
    margin: 0.45rem 0 0.3rem;
    color: #ffffff !important;
    font-size: clamp(1.7rem, 3vw, 2.45rem);
    line-height: 1.15;
}
.dashboard-hero p { margin: 0 0 0.8rem; color: #ecfff1; font-size: 1rem; }
.dashboard-hero-mark {
    display: grid;
    place-items: center;
    width: 5.2rem;
    height: 5.2rem;
    flex: 0 0 5.2rem;
    border: 1px solid rgba(255,255,255,0.35);
    border-radius: 50%;
    background: rgba(255,255,255,0.13);
    color: #ffffff;
    font-size: 2rem;
}
@media (max-width: 640px) {
    .dashboard-hero { min-height: 0; padding: 1.25rem; }
    .dashboard-hero-mark { width: 3.6rem; height: 3.6rem; flex-basis: 3.6rem; }
}
.dashboard-summary-card {
    display: flex;
    align-items: center;
    gap: 0.7rem;
    min-height: 4.1rem;
    padding: 0.65rem 0.75rem;
    border: 1px solid var(--border);
    border-radius: 0.8rem;
    background: var(--surface);
}
.dashboard-summary-icon {
    display: grid;
    place-items: center;
    width: 2.45rem;
    height: 2.45rem;
    flex: 0 0 2.45rem;
    border-radius: 0.7rem;
    background: color-mix(in srgb, var(--primary) 12%, var(--app-bg));
    font-size: 1.25rem;
}
.dashboard-summary-copy { min-width: 0; }
.dashboard-summary-label {
    display: block;
    overflow: hidden;
    color: var(--text-muted);
    font-size: 0.72rem;
    line-height: 1.25;
    text-overflow: ellipsis;
}
.dashboard-summary-value {
    display: block;
    overflow: hidden;
    color: var(--text-strong);
    font-size: 1.12rem;
    font-weight: 750;
    line-height: 1.25;
    text-overflow: ellipsis;
    white-space: nowrap;
}
section.dashboard-hero h1 { color: #ffffff !important; }
@media (max-width: 768px) {
    .block-container { padding: 1.1rem 1rem 3rem; }
}
"""

DARK_OVERRIDES = """
    .stApp, [data-testid="stAppViewContainer"] { background: #111827 !important; color: #F2EBDD !important; }
    [data-testid="stHeader"] { background: #111827 !important; }
    [data-testid="stSidebar"] { background: #0B1220 !important; }
    [data-testid="stSidebar"] * { color: #F2EBDD !important; }
    .block-container { background: #111827 !important; }
    .hero h1, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 { color: #F8FAF7 !important; }
    .hero p { color: #AEBBB4 !important; }
    .panel, .panel-light { background: #1F2937 !important; color: #F2EBDD !important; border-color: #4B6357 !important; }
    .panel-dark { background: #0B1220 !important; color: #F2EBDD !important; }
    .panel-dark h2, .panel-dark h4, .panel-dark p, .panel-dark span { color: #F2EBDD !important; }
    [data-testid="stTextInput"] input, [data-testid="stTextArea"] textarea,
    [data-baseweb="select"] > div, [data-testid="stFileUploader"] section {
        background: #1F2937 !important; color: #F2EBDD !important; border-color: #4B6357 !important;
    }
    [data-testid="stTextInput"] label, [data-testid="stTextArea"] label,
    [data-testid="stSelectbox"] label, [data-testid="stDateInput"] label,
    [data-testid="stNumberInput"] label, [data-testid="stFileUploader"] label,
    [data-testid="stAudioInput"] label { color: #F2EBDD !important; }
    [data-testid="stButton"] button { background: #1F2937 !important; color: #F2EBDD !important; border-color: #4B6357 !important; }
    [data-testid="stButton"] button p, [data-testid="stButton"] button span { color: #F2EBDD !important; }
    [data-testid="stButton"] button[kind="primary"],
    [data-testid="stButton"] button[data-testid="stBaseButton-primary"] {
        background: #16813D !important; color: #FFFFFF !important; border-color: #16813D !important;
    }
    [data-testid="stButton"] button[kind="primary"] *,
    [data-testid="stButton"] button[data-testid="stBaseButton-primary"] * { color: #FFFFFF !important; }
    [data-testid="stTabs"] [role="tab"] { color: #F2EBDD !important; }
    [data-testid="stTabs"] [role="tab"][aria-selected="true"] { background: #1F2937 !important; color: #F8FAF7 !important; }
    [data-testid="stMetric"] { background: #1F2937; }
    [data-testid="stMetric"] label, [data-testid="stMetric"] [data-testid="stMetricValue"] { color: #F2F5F7 !important; }
    .roadmap-shell { background: #111827 !important; }
    .roadmap-row { background: #1F2937 !important; border-color: #344155 !important; }
    [data-testid="stAlert"] [data-testid="stAlertContainer"] { background: #1F2937 !important; }
    [data-testid="stMain"] [data-testid="stExpander"] summary {
        background: #1F2937 !important;
        color: #F2F5F7 !important;
    }
    [data-testid="stMain"] [data-testid="stExpander"] summary [data-testid="stMarkdownContainer"] *,
    [data-testid="stMain"] [data-testid="stExpander"] summary [data-testid="stExpanderIcon"] {
        color: #F2F5F7 !important;
    }
    [data-testid="stMain"] [data-testid="stMarkdownContainer"] *,
    [data-testid="stMain"] [data-testid="stCaptionContainer"],
    [data-testid="stMain"] [data-testid="stCaptionContainer"] *,
    [data-testid="stMain"] label,
    [data-testid="stMain"] [data-testid="stText"] {
        color: #F2F5F7 !important;
    }
    [data-testid="stMain"] [role="radiogroup"][aria-orientation="horizontal"] button[data-variant="segmented_control"] {
        background: #1F2937 !important;
        color: #F2F5F7 !important;
        border-color: #4B6357 !important;
    }
    [data-testid="stMain"] [role="radiogroup"][aria-orientation="horizontal"] button[data-variant="segmented_control"] *,
    [data-testid="stMain"] [role="radiogroup"][aria-orientation="horizontal"] button[data-variant="segmented_control"] [data-testid="stMarkdownContainer"] p {
        color: #F2F5F7 !important;
    }
    [data-testid="stMain"] [role="radiogroup"][aria-orientation="horizontal"] button[data-variant="segmented_control"][aria-checked="true"] {
        background: #16813D !important;
        color: #FFFFFF !important;
    }
    [data-testid="stMain"] [role="radiogroup"][aria-orientation="horizontal"] button[data-variant="segmented_control"][aria-checked="true"] *,
    [data-testid="stMain"] [role="radiogroup"][aria-orientation="horizontal"] button[data-variant="segmented_control"][aria-checked="true"] [data-testid="stMarkdownContainer"] p {
        color: #FFFFFF !important;
    }
    [data-testid="stMain"] button[data-testid="stBaseButton-primary"] [data-testid="stMarkdownContainer"] p {
        color: #FFFFFF !important;
    }
    [data-testid="stMain"] [data-testid="stFileUploader"] button [data-testid="stMarkdownContainer"] * {
        color: #111827 !important;
    }
""" if IS_DARK else ""

st.markdown(
    f"""
    <style>
    {roadmap_css}
    :root {{
        color-scheme: {'dark' if IS_DARK else 'light'};
        --app-bg: {PALETTE['ivory']};
        --surface: {PALETTE['sage']};
        --text-strong: {PALETTE['forest']};
        --text-muted: {PALETTE['muted']};
        --primary: {PALETTE['emerald']};
        --border: {'#344155' if IS_DARK else '#D6E0E8'};
    }}
    .stApp, [data-testid="stAppViewContainer"] {{ background: {PALETTE['ivory']}; color: {PALETTE['forest']}; }}
    [data-testid="stHeader"] {{ background: {PALETTE['ivory']}; }}
    [data-testid="stSidebar"] {{ background: {PALETTE['forest']}; width: 15rem !important; min-width: 15rem !important; }}
    button[aria-label="Collapse sidebar"] {{ display: none !important; }}
    [data-testid="stSidebar"] * {{ color: {PALETTE['ivory']} !important; }}
    [data-testid="stSidebar"] [data-testid="stRadioOption"] * {{ color: #F2EBDD !important; font-weight: 600 !important; }}
    [data-testid="stSidebar"] [role="combobox"],
    [data-testid="stSidebar"] [aria-haspopup="listbox"] {{ color: #102F27 !important; -webkit-text-fill-color: #102F27 !important; }}
    .block-container {{ max-width: 1280px; padding: 2rem 3rem 4rem; }}
    .brand-kicker {{ color: {PALETTE['gold']}; font-size: .78rem; font-weight: 700; letter-spacing: .16em; text-transform: uppercase; }}
    .hero h1, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {{ color: {PALETTE['forest']} !important; }}
    .hero h1 {{ margin: .2rem 0 .25rem; font-size: 2.35rem; }}
    .hero p {{ color: {PALETTE['muted']}; font-size: 1.05rem; margin: 0; }}
    .panel {{ background: {PALETTE['sage']}; border: 1px solid {PALETTE['gold']}; border-radius: 16px; padding: 1rem 1.15rem; color: {PALETTE['forest']}; }}
    .panel-light {{ background: {PALETTE['ivory']}; border: 1px solid {PALETTE['sage']}; border-radius: 16px; padding: 1rem 1.15rem; color: {PALETTE['forest']}; }}
    .panel-dark {{ background: {PALETTE['forest']}; border: 1px solid {PALETTE['gold']}; border-radius: 16px; padding: 1rem 1.15rem; color: {PALETTE['ivory']}; }}
    .panel-dark h4, .panel-dark p, .panel-dark span {{ color: {PALETTE['ivory']}; }}
    .eyebrow {{ color: {PALETTE['gold']}; font-size: .76rem; font-weight: 700; letter-spacing: .1em; text-transform: uppercase; }}
    .status {{ border-left: 4px solid {PALETTE['gold']}; background: {PALETTE['sage']}; color: {PALETTE['forest']}; border-radius: 8px; padding: .65rem .8rem; margin: .35rem 0; }}
    .status strong {{ color: {PALETTE['forest']}; }}
    .muted, [data-testid="stCaptionContainer"] {{ color: {PALETTE['muted']} !important; }}
    .record-card {{ background: {PALETTE['ivory']}; color: {PALETTE['forest']}; border: 1px solid {PALETTE['sage']}; border-radius: 12px; padding: .8rem 1rem; margin: .45rem 0; }}
    .record-card small {{ color: {PALETTE['muted']}; }}
    .source-link {{ color: {PALETTE['emerald']}; word-break: break-word; }}
    /* Farmer Input widget surfaces: explicit selectors prevent inherited dark-theme styles. */
    [data-testid="stAudioInput"] p, [data-testid="stAudioInput"] label,
    [data-testid="stFileUploader"] p, [data-testid="stFileUploader"] label,
    [data-testid="stTextArea"] p, [data-testid="stTextArea"] label,
    [data-testid="stTextArea"] [data-testid="stMarkdownContainer"] {{ color: {PALETTE['forest']} !important; opacity: 1 !important; font-weight: 700 !important; }}
    [data-testid="stAudioInput"], [data-testid="stFileUploader"], [data-testid="stTextArea"] {{ background: {PALETTE['ivory']} !important; color: {PALETTE['forest']} !important; border-radius: 12px; }}
    [data-testid="stTextArea"] textarea {{ background: {PALETTE['ivory']} !important; color: {PALETTE['forest']} !important; -webkit-text-fill-color: {PALETTE['forest']} !important; border: 1px solid {PALETTE['sage']} !important; border-radius: 12px !important; padding: .8rem !important; opacity: 1 !important; box-shadow: none !important; }}
    [data-testid="stTextArea"] textarea:focus {{ border: 2px solid {PALETTE['emerald']} !important; outline: none !important; box-shadow: 0 0 0 1px {PALETTE['emerald']} !important; }}
    [data-testid="stTextArea"] textarea::placeholder {{ color: {PALETTE['muted']} !important; -webkit-text-fill-color: {PALETTE['muted']} !important; opacity: 1 !important; }}
    [data-testid="stFileUploader"] section {{ background: {PALETTE['ivory']} !important; border: 1px solid {PALETTE['sage']} !important; border-radius: 12px !important; color: {PALETTE['forest']} !important; }}
    [data-testid="stFileUploader"] button {{ background: {PALETTE['emerald']} !important; color: {PALETTE['ivory']} !important; border: 1px solid {PALETTE['gold']} !important; border-radius: 8px !important; }}
    [data-testid="stFileUploader"] button p, [data-testid="stFileUploader"] button span {{ color: {PALETTE['ivory']} !important; }}
    [data-testid="stFileUploaderFileName"], [data-testid="stFileUploaderFileName"] *, [data-testid="stFileUploaderFileData"], [data-testid="stFileUploaderFileData"] * {{ color: {PALETTE['forest']} !important; opacity: 1 !important; }}
    [data-testid="stButton"] button {{ min-height: 2.65rem; border-radius: 10px !important; background: {PALETTE['ivory']} !important; color: {PALETTE['forest']} !important; border: 1px solid {PALETTE['sage']} !important; }}
    [data-testid="stButton"] button p, [data-testid="stButton"] button span {{ color: {PALETTE['forest']} !important; opacity: 1 !important; }}
    [data-testid="stButton"] button:hover {{ background: {PALETTE['sage']} !important; color: {PALETTE['forest']} !important; }}
    [data-testid="stButton"] button[kind="primary"], [data-testid="stButton"] button[data-testid="stBaseButton-primary"] {{ background: {PALETTE['emerald']} !important; color: {PALETTE['ivory']} !important; border-color: {PALETTE['gold']} !important; }}
    [data-testid="stButton"] button[kind="primary"] p, [data-testid="stButton"] button[kind="primary"] span, [data-testid="stButton"] button[data-testid="stBaseButton-primary"] p, [data-testid="stButton"] button[data-testid="stBaseButton-primary"] span {{ color: {PALETTE['ivory']} !important; }}
    /* Streamlit tabs: keep every label readable before hover. */
    [data-testid="stTabs"] [role="tab"], [data-baseweb="tab-list"] [role="tab"], [data-baseweb="tab-list"] [data-baseweb="tab"] {{ color: {PALETTE['forest']} !important; background: transparent !important; opacity: 1 !important; font-weight: 700 !important; border-bottom: 3px solid transparent !important; }}
    [data-testid="stTabs"] [role="tab"] *, [data-baseweb="tab-list"] [role="tab"] *, [data-baseweb="tab-list"] [data-baseweb="tab"] * {{ color: {PALETTE['forest']} !important; opacity: 1 !important; }}
    [data-testid="stTabs"] [role="tab"]:hover, [data-baseweb="tab-list"] [role="tab"]:hover, [data-baseweb="tab-list"] [data-baseweb="tab"]:hover {{ color: {PALETTE['emerald']} !important; background: {PALETTE['sage']} !important; }}
    [data-testid="stTabs"] [role="tab"]:focus-visible, [data-baseweb="tab-list"] [role="tab"]:focus-visible {{ outline: 2px solid {PALETTE['gold']} !important; outline-offset: 2px; }}
    [data-testid="stTabs"] [role="tab"][aria-selected="true"], [data-baseweb="tab-list"] [role="tab"][aria-selected="true"], [data-baseweb="tab-list"] [data-baseweb="tab"][aria-selected="true"] {{ color: {PALETTE['forest']} !important; background: {PALETTE['ivory']} !important; border-bottom-color: {PALETTE['emerald']} !important; font-weight: 800 !important; }}
    [data-testid="stTabs"] [role="tab"][aria-selected="true"] *, [data-baseweb="tab-list"] [role="tab"][aria-selected="true"] * {{ color: {PALETTE['forest']} !important; opacity: 1 !important; }}
    [data-testid="stTextInput"] input, [data-testid="stTextArea"] textarea, [data-baseweb="select"] > div, [data-baseweb="select"] input, [data-baseweb="select"] span, [data-baseweb="select"] [role="combobox"], [data-testid="stFileUploader"] section {{ background: {PALETTE['ivory']} !important; color: {PALETTE['forest']} !important; border-color: {PALETTE['sage']} !important; }}
    [data-testid="stTextArea"] textarea:disabled {{ color: {PALETTE['forest']} !important; -webkit-text-fill-color: {PALETTE['forest']} !important; opacity: 1 !important; }}
    input::placeholder, textarea::placeholder {{ color: {PALETTE['muted']} !important; opacity: 1 !important; }}
    [data-testid="stSelectbox"] label, [data-testid="stTextInput"] label, [data-testid="stTextArea"] label, [data-testid="stFileUploader"] label, [data-testid="stAudioInput"] label {{ color: {PALETTE['forest']} !important; }}
    [data-baseweb="select"] button {{ color: {PALETTE['forest']} !important; background: {PALETTE['ivory']} !important; }}
    button[kind="primary"], [data-testid="stBaseButton-primary"], [data-testid="stBaseButton-secondary"] {{ background: {PALETTE['emerald']} !important; color: {PALETTE['ivory']} !important; border: 1px solid {PALETTE['gold']} !important; }}
    button[kind="primary"] p, button[kind="primary"] span, [data-testid="stBaseButton-primary"] p, [data-testid="stBaseButton-primary"] span, [data-testid="stBaseButton-secondary"] p, [data-testid="stBaseButton-secondary"] span {{ color: {PALETTE['ivory']} !important; }}
    button[kind="primary"]:hover, [data-testid="stBaseButton-primary"]:hover, [data-testid="stBaseButton-secondary"]:hover {{ background: {PALETTE['forest']} !important; color: {PALETTE['ivory']} !important; }}
    [data-testid="stAudioInputActionButton"] {{ background: {PALETTE['emerald']} !important; color: {PALETTE['ivory']} !important; border-color: {PALETTE['gold']} !important; }}
    [data-testid="stAudioInputActionButton"] svg {{ fill: {PALETTE['ivory']} !important; color: {PALETTE['ivory']} !important; }}
    [data-testid="stAlert"] {{ background: {PALETTE['sage']} !important; color: {PALETTE['forest']} !important; border-color: {PALETTE['gold']} !important; }}
    [data-testid="stAlert"] p, [data-testid="stAlert"] span, [data-testid="stAlert"] [data-testid="stMarkdownContainer"] {{ color: {PALETTE['forest']} !important; }}
    [data-testid="stSpinner"] {{ color: {PALETTE['emerald']} !important; }}
    {DARK_OVERRIDES}
    </style>
    """,
    unsafe_allow_html=True,
)


LANGUAGES = {
    "ಕನ್ನಡ (Kannada) — Available": ("ಕನ್ನಡ (Kannada)", "Operational: tested Gnani STT + deterministic tomato engine"),
    "English — Available": ("English", "Operational: tested Gnani STT + deterministic tomato engine"),
    "हिन्दी (Hindi) — Planned": ("Hindi", "Planned: Hindi interface and speech processing are not available yet"),
    "తెలుగు (Telugu) — Planned": ("Telugu", "Planned: Telugu interface and speech processing are not available yet"),
    "தமிழ் (Tamil) — Planned": ("Tamil", "Planned: Tamil interface and speech processing are not available yet"),
    "मराठी (Marathi) — Planned": ("Marathi", "Planned: Marathi interface and speech processing are not available yet"),
}

CURRENT_LANGUAGE_LABEL = (
    "ಕನ್ನಡ (Kannada) — Available"
    if st.session_state["farmer_language"] == "ಕನ್ನಡ"
    else "English — Available"
)
st.session_state.setdefault("sidebar_language", CURRENT_LANGUAGE_LABEL)
st.session_state.setdefault("settings_language", st.session_state["farmer_language"])


def status_box(label: str, value: str, tone: str = "neutral") -> None:
    tone_label = {"ready": "READY", "partial": "IN PROGRESS", "planned": "PLANNED", "error": "CHECK"}.get(tone, "INFO")
    st.markdown(f'<div class="status"><strong>{tone_label} · {html.escape(label)}</strong><br>{html.escape(value)}</div>', unsafe_allow_html=True)


def remember_navigation_selection(page_names: list[str], page_labels: list[str], widget_key: str) -> None:
    selected_label = st.session_state[widget_key]
    st.session_state["selected_page_name"] = page_names[page_labels.index(selected_label)]


def reset_session() -> None:
    for key in ("transcript", "question_text", "guidance", "matches", "parse", "conversation", "audio_response"):
        st.session_state.pop(key, None)


def process_text(text: str, language: str) -> None:
    cleaned = text.strip()
    if not cleaned:
        st.session_state["input_error"] = "Enter a question before submitting."
        return
    st.session_state.pop("input_error", None)
    st.session_state["transcript"] = cleaned
    st.session_state["question_text"] = cleaned
    st.session_state["parse"] = parse_question(cleaned)
    st.session_state["matches"] = search(cleaned)
    st.session_state["guidance"] = build_guidance(cleaned, language)
    history = st.session_state.setdefault("conversation", [])
    if not history or history[-1].get("question") != cleaned:
        history.append({"question": cleaned, "answer": get_answer(cleaned, language)})


def tts_response_text(guidance: dict) -> str:
    """Build speech text only from the already validated guidance fields."""
    lines = [guidance.get("understanding", "")]
    causes = guidance.get("possible_explanations", [])
    actions = guidance.get("safe_actions", [])
    questions = guidance.get("follow_up_questions", [])
    if causes:
        lines.append("Possible explanations: " + "; ".join(causes[:4]))
    if actions:
        lines.append("Safe initial actions: " + "; ".join(actions[:3]))
    if questions:
        lines.append("Please check: " + "; ".join(questions[:3]))
    lines.append(guidance.get("referral", "Consult a qualified agricultural expert if the problem continues."))
    return " ".join(line.strip() for line in lines if line and line.strip())


def render_core_roadmap() -> None:
    rows = []
    for phase, heading, description in ROADMAP_PHASES:
        rows.append(
            f"""
            <article class="roadmap-row">
                <div class="roadmap-phase">{html.escape(phase)}</div>
                <div>
                    <h2 class="roadmap-heading">{html.escape(heading)}</h2>
                    <p class="roadmap-description">{html.escape(description)}</p>
                </div>
            </article>
            """
        )
    st.markdown(
        f"""
        <section class="roadmap-shell">
            <h1 class="roadmap-title">KrishiDrishti AI &nbsp;—&nbsp; Core Development Roadmap</h1>
            <div class="roadmap-list">{''.join(rows)}</div>
            <div class="roadmap-scroll-cue" aria-label="Scroll for more">↓</div>
        </section>
        """,
        unsafe_allow_html=True,
    )


with st.sidebar:
    st.markdown("## :material/eco: KrishiDrishti AI")
    interface_language = st.session_state.get("farmer_language", "ಕನ್ನಡ")
    st.caption(farmer_ui.text(interface_language, "Smart farming. Better tomorrow.", "ಸ್ಮಾರ್ಟ್ ಕೃಷಿ. ಉತ್ತಮ ಭವಿಷ್ಯ."))
    is_dark_mode = st.session_state.get("appearance") == "Dark"
    mode_label = farmer_ui.text(interface_language, "Switch to light mode", "ಬೆಳಕು ಮೋಡ್‌ಗೆ ಬದಲಿಸಿ") if is_dark_mode else farmer_ui.text(
        interface_language, "Switch to dark mode", "ಕತ್ತಲೆ ಮೋಡ್‌ಗೆ ಬದಲಿಸಿ"
    )
    mode_icon = ":material/light_mode:" if is_dark_mode else ":material/dark_mode:"
    if st.button(mode_label, icon=mode_icon, key="sidebar_mode_toggle", width="stretch"):
        st.session_state["appearance"] = "Light" if is_dark_mode else "Dark"
        st.rerun()

    language_label = st.selectbox(
        farmer_ui.text(interface_language, "Language", "ಭಾಷೆ"),
        list(LANGUAGES),
        key="sidebar_language",
        on_change=farmer_ui.sync_sidebar_language,
    )
    language, language_note = LANGUAGES[language_label]
    if language in ("ಕನ್ನಡ (Kannada)", "English"):
        st.session_state["farmer_language"] = "ಕನ್ನಡ" if language.startswith("ಕನ್ನಡ") else "English"
    if language == "ಕನ್ನಡ (Kannada)":
        language_note = "ಕಾರ್ಯನಿರ್ವಹಣೆಯಲ್ಲಿದೆ: Gnani STT ಮತ್ತು ಟೊಮೇಟೊ ಮಾರ್ಗದರ್ಶನ."
    elif language == "English":
        language_note = "Operational: tested Gnani STT + deterministic tomato engine"
    else:
        language_note = farmer_ui.text(
            interface_language,
            language_note,
            "ಈ ಭಾಷೆಯ ಇಂಟರ್ಫೇಸ್ ಮತ್ತು ಧ್ವನಿ ಪ್ರಕ್ರಿಯೆ ಇನ್ನೂ ಲಭ್ಯವಿಲ್ಲ.",
        )
    st.caption(language_note)

    labels = farmer_ui.bilingual_labels(st.session_state.get("farmer_language", "ಕನ್ನಡ"))
    page_names = [
        "Home / Dashboard", "Farmer Profile", "My Farms", "My Crops",
        "Ask KrishiDrishti", "Voice Assistant", "Consultation History",
        "Notifications", "Settings", "Help and Support",
        "Farmer experience", "Demonstration dashboard",
    ]
    nav_icons = ["🏠", "👤", "🏡", "🌱", "💬", "🎙️", "🕘", "🔔", "⚙️", "❔", "🧑‍🌾", "🧪"]
    requested = st.session_state.pop("requested_page", None)
    if requested in page_names:
        st.session_state["selected_page_name"] = requested
    default_name = st.session_state.get("selected_page_name", "Home / Dashboard")
    default_index = page_names.index(default_name) if default_name in page_names else 0
    page_labels = [f"{icon} {labels.get(name, name)}" for icon, name in zip(nav_icons, page_names)]
    navigation_key = "sidebar_navigation_kn" if interface_language == "ಕನ್ನಡ" else "sidebar_navigation_en"
    selected_label = st.radio(
        farmer_ui.text(interface_language, "Navigation", "ನ್ಯಾವಿಗೇಶನ್"),
        page_labels,
        index=default_index,
        key=navigation_key,
        on_change=remember_navigation_selection,
        args=(page_names, page_labels, navigation_key),
    )
    view = page_names[page_labels.index(selected_label)]
    st.session_state["selected_page_name"] = view


interface_language = st.session_state.get("farmer_language", "ಕನ್ನಡ")

if view == "Home / Dashboard":
    farmer_ui.dashboard(interface_language)
    st.stop()
elif view == "Farmer Profile":
    farmer_ui.farmer_profile(interface_language)
    st.stop()
elif view == "My Farms":
    farmer_ui.my_farms(interface_language)
    st.stop()
elif view == "My Crops":
    farmer_ui.my_crops(interface_language)
    st.stop()
elif view == "Ask KrishiDrishti":
    farmer_ui.ask_assistant(interface_language)
    st.stop()
elif view == "Voice Assistant":
    farmer_ui.voice_assistant(interface_language)
    st.stop()
elif view == "Consultation History":
    farmer_ui.consultation_history(interface_language)
    st.stop()
elif view == "Notifications":
    farmer_ui.notifications(interface_language)
    st.stop()
elif view == "Settings":
    farmer_ui.settings(interface_language)
    st.stop()
elif view == "Help and Support":
    farmer_ui.help_support(interface_language)
    st.stop()
elif view == "Core development roadmap":
    render_core_roadmap()
    st.stop()
elif view == "Farmer experience":
    st.markdown('<div class="hero"><div class="brand-kicker">KrishiDrishti AI · Development Console</div><h1>🌾 KrishiDrishti Voice</h1><p>Multilingual agricultural voice-assistant testing dashboard</p></div>', unsafe_allow_html=True)
    st.write("")
    st.markdown('<div class="panel-dark"><span class="eyebrow">Farmer experience</span><br><h2 style="color:#F2EBDD">Ask your crop assistant</h2><p>Speak naturally in Kannada or English, preserve your original transcript, and receive source-backed tomato guidance with clear uncertainty warnings.</p></div>', unsafe_allow_html=True)
else:
    st.markdown('<div class="hero"><div class="brand-kicker">KrishiDrishti AI · Development Console</div><h1>🌾 KrishiDrishti Voice</h1><p>Multilingual agricultural voice-assistant testing dashboard</p></div>', unsafe_allow_html=True)
    st.write("")
    st.markdown('<div class="panel-dark"><span class="eyebrow">Demonstration / technical dashboard</span><br><h2 style="color:#F2EBDD">Processing console</h2><p>Inspect the real pipeline from voice input and Gnani transcription through deterministic interpretation, retrieval, safety validation and response.</p></div>', unsafe_allow_html=True)

if language.startswith("Hindi") or language.startswith("Telugu") or language.startswith("Tamil") or language.startswith("Marathi"):
    st.markdown(f'<div class="panel"><span class="eyebrow">Planned language</span><br><strong>{html.escape(language)}</strong><br>This is a UI preview. Speech recognition, translation, and agricultural processing for this language are not operational yet.</div>', unsafe_allow_html=True)

tabs = st.tabs(["Farmer input", "Understanding", "Investigation", "Conversation", "Voice output", "Dev / test"])

with tabs[0]:
    st.subheader("Farmer input")
    st.caption("Use a real recording, upload an audio clip, or test the deterministic engine with text. No mock transcription is generated.")
    left, right = st.columns(2, gap="large")
    with left:
        st.markdown('<div class="eyebrow">Voice capture</div>', unsafe_allow_html=True)
        audio = st.audio_input("Record a question")
        uploaded = st.file_uploader("Upload audio", type=["wav", "mp3", "m4a", "ogg", "flac", "aac"])
        audio_input = audio or uploaded
        if audio_input:
            st.audio(audio_input)
            if st.button("Transcribe with Gnani Prisma", type="primary", use_container_width=True):
                with st.spinner("Sending audio to Gnani Prisma…"):
                    result = transcribe_audio(audio_input, language)
                if result.error:
                    st.session_state["input_error"] = result.error
                else:
                    process_text(result.text or "", language)
                    st.session_state["transcription_status"] = "Verified transcript received from Gnani Prisma."
    with right:
        st.markdown('<div class="eyebrow">Manual text test</div>', unsafe_allow_html=True)
        text_value = st.text_area("Type a question", value=st.session_state.get("question_text", ""), height=150, placeholder="English or Kannada tomato question…")
        submit, clear = st.columns(2)
        with submit:
            if st.button("Submit question", type="primary", use_container_width=True):
                process_text(text_value, language)
        with clear:
            if st.button("Clear session", use_container_width=True):
                reset_session()
                st.rerun()
    if st.session_state.get("input_error"):
        status_box("Input / processing", st.session_state["input_error"], "error")
    if st.session_state.get("transcription_status"):
        status_box("Speech recognition", st.session_state["transcription_status"], "ready")

    st.markdown("### Original-language transcript")
    transcript = st.session_state.get("transcript", "")
    if transcript:
        st.text_area("Preserved transcript", value=transcript, height=120, disabled=True)
    else:
        st.caption("No transcript in the current session.")

with tabs[1]:
    st.subheader("Language understanding")
    parsed = st.session_state.get("parse")
    guidance = st.session_state.get("guidance")
    if parsed:
        st.markdown('<div class="panel-light">', unsafe_allow_html=True)
        st.markdown("**Engine:** Current deterministic parser  ·  **Translation:** Not implemented")
        st.markdown(f"**Crop**  \n{html.escape(str(parsed.get('crop') or 'Unavailable'))}")
        st.markdown(f"**Topic / symptom**  \n{html.escape(str(parsed.get('symptom') or 'Unavailable'))}")
        st.markdown("**Original text**")
        st.text(parsed.get("normalized_text", ""))
        st.markdown("</div>", unsafe_allow_html=True)
        if guidance:
            missing = guidance.get("follow_up_questions", [])
            st.markdown("### Missing information to collect")
            for item in missing:
                st.markdown(f"- {item}")
    else:
        st.caption("Submit a question to inspect crop, symptom, and missing-information extraction.")

with tabs[2]:
    st.subheader("Agricultural investigation")
    matches = st.session_state.get("matches", [])
    guidance = st.session_state.get("guidance")
    if matches and guidance:
        st.markdown("### Retrieved records")
        for match in matches:
            record = match.record
            with st.expander(f"{record['id']} · {record['topic']} · retrieval score {match.score}"):
                st.write(record.get("description_en", "No description available."))
                st.markdown(f"**Possible causes:** {', '.join(record.get('possible_causes', [])) or 'None listed'}")
                st.markdown(f"**Observed distinctions:** {', '.join(record.get('distinguishing_signs', [])) or 'None listed'}")
                st.markdown(f"**Evidence status:** {record.get('evidence_status', 'Unavailable')}")
                source = record.get("source", {})
                st.markdown(f"**Source:** {source.get('title', 'Unavailable')} · {source.get('organization', 'Unavailable')}  \\n+                <span class='source-link'>{html.escape(source.get('url', 'Unavailable'))}</span>", unsafe_allow_html=True)
        st.markdown("### Uncertainty and safety")
        status_box("Safety warning", guidance.get("uncertainty", "Unavailable"), "partial")
        st.markdown("### Why these records?")
        st.caption("Records are ranked by explicit crop and symptom/topic phrase matches in the local deterministic engine. This is not semantic AI or a trained disease recognizer.")
    else:
        st.caption("No agricultural records retrieved yet.")

with tabs[3]:
    st.subheader("Conversational investigation")
    st.markdown('<div class="panel"><span class="eyebrow">Preview state</span><br><strong>Conversation orchestration is not operational yet.</strong><br>The current interface shows where history, follow-up questions, collected answers, and progress will connect once the conversation backend is implemented.</div>', unsafe_allow_html=True)
    history = st.session_state.get("conversation", [])
    if history:
        st.markdown("### Conversation history")
        for turn in history:
            st.markdown(f"**Farmer:** {turn['question']}")
            st.caption("Assistant response is generated by the current deterministic engine.")
        st.markdown("### Current follow-up questions")
        for question in (st.session_state.get("guidance") or {}).get("follow_up_questions", []):
            st.markdown(f"- {question}")
    else:
        st.caption("No conversation turns yet. Repeated-question prevention and voice-response input are planned.")

with tabs[4]:
    st.subheader("Voice output")
    guidance = st.session_state.get("guidance")
    language = LANGUAGES[language_label][0]
    if not guidance:
        st.markdown('<div class="panel"><span class="eyebrow">Waiting for a validated response</span><br><strong>Submit a Kannada question first.</strong><br>Audio is generated only from the existing agricultural guidance engine.</div>', unsafe_allow_html=True)
    elif language != "ಕನ್ನಡ (Kannada)":
        st.markdown('<div class="panel"><span class="eyebrow">Unavailable for this selection</span><br><strong>Kannada Timbre output is the only verified TTS path.</strong><br>No unsupported-language audio is generated.</div>', unsafe_allow_html=True)
    elif guidance.get("safety_category"):
        st.markdown('<div class="panel"><span class="eyebrow">Safety hold</span><br><strong>Audio is not generated for unsafe or unsupported recommendations.</strong></div>', unsafe_allow_html=True)
    else:
        st.caption("The audio below will be generated from the current source-backed, uncertainty-aware agricultural response.")
        if st.button("Generate Kannada response audio", type="primary"):
            with st.spinner("Generating Kannada audio with Gnani Timbre…"):
                speech = synthesize_speech(tts_response_text(guidance), language)
            if speech.error:
                st.session_state["tts_error"] = speech.error
                st.session_state.pop("audio_response", None)
            else:
                st.session_state.pop("tts_error", None)
                st.session_state["audio_response"] = speech.audio
                st.session_state["tts_status"] = {"status_code": speech.status_code, "content_type": speech.content_type, "size": len(speech.audio or b"")}
        if st.session_state.get("tts_error"):
            status_box("TTS processing", st.session_state["tts_error"], "error")
        if st.session_state.get("audio_response"):
            st.audio(st.session_state["audio_response"], format=st.session_state.get("tts_status", {}).get("content_type", "audio/wav"))
            meta = st.session_state.get("tts_status", {})
            status_box("Timbre playback", f"HTTP {meta.get('status_code')} · {meta.get('content_type')} · {meta.get('size')} bytes", "ready")

with tabs[5]:
    st.subheader("Development and testing")
    st.markdown("### Current processing pipeline")
    stages = [
        ("1 · Audio capture / upload", "Operational" if st.session_state.get("transcript") else "Ready"),
        ("2 · Gnani Prisma STT", "Operational for tested English and Kannada"),
        ("3 · Original transcript preservation", "Operational" if st.session_state.get("transcript") else "Waiting"),
        ("4 · Deterministic question parser", "Operational" if st.session_state.get("parse") else "Waiting"),
        ("5 · Local tomato retrieval", "Operational" if st.session_state.get("matches") else "Waiting"),
        ("6 · SLM / translation", "Planned"),
        ("7 · Conversation backend", "Planned"),
        ("8 · Timbre TTS", "Operational for Kannada on request"),
    ]
    for label, value in stages:
        tone = "ready" if value.startswith("Operational") else "planned" if value == "Planned" else "partial"
        status_box(label, value, tone)
    st.markdown("### Validation notes")
    st.caption("Use the manual text input to test English and Kannada without making an API request. Existing automated tests cover deterministic parsing, retrieval, Kannada variants, safety, and offline operation.")
    st.caption("No credentials, environment values, or raw request headers are shown in this panel.")

