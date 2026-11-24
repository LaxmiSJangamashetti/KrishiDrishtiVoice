import hashlib
import html
from datetime import datetime

import streamlit as st

from agriculture_engine import build_guidance, get_answer, parse_question, search
from gnani_service import synthesize_speech, transcribe_audio
from language_understanding import understand
from conversation_manager import new_conversation, process_turn
from farmer_profile import repository as farmer_repository
from farmer_profile import ui as farmer_ui
from agromonitoring_service import AgroMonitoringError, current_weather, weather_forecast, temperature_celsius
from market_service import MarketServiceError, commodities, markets, price_history, prices, states, is_market_query


st.set_page_config(page_title="KrishiDrishti AI", page_icon="🌾", layout="wide", initial_sidebar_state="expanded")
farmer_repository.initialize_database()

PALETTE = {
    "ivory": "#F2EBDD",
    "sage": "#78947F",
    "emerald": "#185844",
    "forest": "#102F27",
    "gold": "#B08A4F",
}

st.markdown(
    f"""
    <style>
    :root {{ color-scheme: light; }}
    .stApp, [data-testid="stAppViewContainer"] {{ background: {PALETTE['ivory']}; color: {PALETTE['forest']}; }}
    [data-testid="stHeader"] {{ background: {PALETTE['ivory']}; }}
    [data-testid="stSidebar"] {{ background: {PALETTE['forest']}; }}
    [data-testid="stSidebar"] * {{ color: {PALETTE['ivory']} !important; }}
    .block-container {{ max-width: 1280px; padding: 2rem 3rem 4rem; }}
    .brand-kicker {{ color: {PALETTE['gold']}; font-size: .78rem; font-weight: 700; letter-spacing: .16em; text-transform: uppercase; }}
    .hero h1, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {{ color: {PALETTE['forest']} !important; }}
    .hero h1 {{ margin: .2rem 0 .25rem; font-size: 2.35rem; }}
    .hero p {{ color: {PALETTE['sage']}; font-size: 1.05rem; margin: 0; }}
    .panel {{ background: {PALETTE['sage']}; border: 1px solid {PALETTE['gold']}; border-radius: 16px; padding: 1rem 1.15rem; color: {PALETTE['forest']}; }}
    .panel-light {{ background: {PALETTE['ivory']}; border: 1px solid {PALETTE['sage']}; border-radius: 16px; padding: 1rem 1.15rem; color: {PALETTE['forest']}; }}
    .panel-dark {{ background: {PALETTE['forest']}; border: 1px solid {PALETTE['gold']}; border-radius: 16px; padding: 1rem 1.15rem; color: {PALETTE['ivory']}; }}
    .panel-dark h4, .panel-dark p, .panel-dark span {{ color: {PALETTE['ivory']}; }}
    .eyebrow {{ color: {PALETTE['gold']}; font-size: .76rem; font-weight: 700; letter-spacing: .1em; text-transform: uppercase; }}
    .status {{ border-left: 4px solid {PALETTE['gold']}; background: {PALETTE['sage']}; color: {PALETTE['forest']}; border-radius: 8px; padding: .65rem .8rem; margin: .35rem 0; }}
    .status strong {{ color: {PALETTE['forest']}; }}
    .muted, [data-testid="stCaptionContainer"] {{ color: {PALETTE['sage']} !important; }}
    .record-card {{ background: {PALETTE['ivory']}; color: {PALETTE['forest']}; border: 1px solid {PALETTE['sage']}; border-radius: 12px; padding: .8rem 1rem; margin: .45rem 0; }}
    .record-card small {{ color: {PALETTE['sage']}; }}
    .source-link {{ color: {PALETTE['emerald']}; word-break: break-word; }}
    /* Farmer Input widget surfaces: explicit selectors prevent inherited dark-theme styles. */
    [data-testid="stAudioInput"] p, [data-testid="stAudioInput"] label,
    [data-testid="stFileUploader"] p, [data-testid="stFileUploader"] label,
    [data-testid="stTextArea"] p, [data-testid="stTextArea"] label,
    [data-testid="stTextArea"] [data-testid="stMarkdownContainer"] {{ color: {PALETTE['forest']} !important; opacity: 1 !important; font-weight: 700 !important; }}
    [data-testid="stAudioInput"], [data-testid="stFileUploader"], [data-testid="stTextArea"] {{ background: {PALETTE['ivory']} !important; color: {PALETTE['forest']} !important; border-radius: 12px; }}
    [data-testid="stTextArea"] textarea {{ background: {PALETTE['ivory']} !important; color: {PALETTE['forest']} !important; -webkit-text-fill-color: {PALETTE['forest']} !important; border: 1px solid {PALETTE['sage']} !important; border-radius: 12px !important; padding: .8rem !important; opacity: 1 !important; box-shadow: none !important; }}
    [data-testid="stTextArea"] textarea:focus {{ border: 2px solid {PALETTE['emerald']} !important; outline: none !important; box-shadow: 0 0 0 1px {PALETTE['emerald']} !important; }}
    [data-testid="stTextArea"] textarea::placeholder {{ color: {PALETTE['sage']} !important; -webkit-text-fill-color: {PALETTE['sage']} !important; opacity: 1 !important; }}
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
    [data-testid="stTabs"] [role="tab"][aria-selected="true"], [data-baseweb="tab-list"] [role="tab"][aria-selected="true"], [data-baseweb="tab-list"] [data-baseweb="tab'][aria-selected="true"] {{ color: {PALETTE['forest']} !important; background: {PALETTE['ivory']} !important; border-bottom-color: {PALETTE['emerald']} !important; font-weight: 800 !important; }}
    [data-testid="stTabs"] [role="tab"][aria-selected="true"] *, [data-baseweb="tab-list"] [role="tab"][aria-selected="true"] * {{ color: {PALETTE['forest']} !important; opacity: 1 !important; }}
    [data-testid="stTextInput"] input, [data-testid="stTextArea"] textarea, [data-baseweb="select"] > div, [data-baseweb="select"] input, [data-baseweb="select"] span, [data-baseweb="select"] [role="combobox"], [data-testid="stFileUploader"] section {{ background: {PALETTE['ivory']} !important; color: {PALETTE['forest']} !important; border-color: {PALETTE['sage']} !important; }}
    [data-testid="stTextArea"] textarea:disabled {{ color: {PALETTE['forest']} !important; -webkit-text-fill-color: {PALETTE['forest']} !important; opacity: 1 !important; }}
    input::placeholder, textarea::placeholder {{ color: {PALETTE['sage']} !important; opacity: 1 !important; }}
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
    /* Farmer-facing dashboard styles, scoped away from the developer console. */
    .dashboard-hero {{ background: linear-gradient(135deg, {PALETTE['forest']}, {PALETTE['emerald']}); border: 1px solid {PALETTE['gold']}; border-radius: 18px; padding: 2.2rem 2rem; display: flex; justify-content: space-between; align-items: center; color: {PALETTE['ivory']}; }}
    .dashboard-hero h1, .dashboard-hero p, .dashboard-hero span {{ color: {PALETTE['ivory']} !important; }}
    .dashboard-hero h1 {{ margin: .45rem 0 .55rem; font-size: clamp(2rem, 4vw, 3.2rem); }}
    .dashboard-hero p {{ max-width: 760px; line-height: 1.55; margin: 0; }}
    .dashboard-eyebrow {{ color: {PALETTE['gold']} !important; font-size: .75rem; font-weight: 800; letter-spacing: .14em; }}
    .dashboard-hero-mark {{ width: 4.5rem; height: 4.5rem; border: 1px solid {PALETTE['sage']}; border-radius: 50%; display: grid; place-items: center; font-size: 2.2rem; background: rgba(120,148,127,.22); }}
    .dashboard-summary-card {{ min-height: 7rem; background: rgba(120,148,127,.16); border: 1px solid {PALETTE['sage']}; border-radius: 14px; padding: 1rem; display: flex; gap: .75rem; align-items: center; color: {PALETTE['forest']}; }}
    .dashboard-summary-icon {{ font-size: 1.45rem; }}
    .dashboard-summary-copy {{ display: flex; flex-direction: column; gap: .3rem; min-width: 0; }}
    .dashboard-summary-label {{ color: {PALETTE['forest']}; font-size: .82rem; overflow-wrap: anywhere; }}
    .dashboard-summary-value {{ color: {PALETTE['forest']}; font-size: 1.2rem; overflow-wrap: anywhere; }}
    @media (max-width: 700px) {{ .block-container {{ padding: 1rem; }} .dashboard-hero {{ padding: 1.35rem; }} .dashboard-hero-mark {{ display: none; }} }}
    </style>
    """,
    unsafe_allow_html=True,
)

# BaseWeb renders selectbox menus in a portal, outside the widget's immediate
# container. Keep these overrides explicit so the sidebar's dark-surface rule
# cannot turn text invisible on the light selectbox field or its popup.
_dark_surface = st.session_state.get("appearance") == "Dark"
_select_bg = PALETTE["forest"] if _dark_surface else PALETTE["ivory"]
_select_fg = PALETTE["ivory"] if _dark_surface else PALETTE["forest"]
st.markdown(
    f"""
    <style>
    [data-testid="stSelectbox"] [data-baseweb="select"] > div {{
        background: {_select_bg} !important;
        color: {_select_fg} !important;
        border: 1px solid {PALETTE['sage']} !important;
        opacity: 1 !important;
    }}
    [data-testid="stSelectbox"] [data-baseweb="select"] [role="combobox"],
    [data-testid="stSelectbox"] [data-baseweb="select"] input,
    [data-testid="stSelectbox"] [data-baseweb="select"] input[aria-autocomplete="list"],
    [data-testid="stSelectbox"] [data-baseweb="select"] span,
    [data-testid="stSelectbox"] [data-baseweb="select"] div {{
        color: {_select_fg} !important;
        -webkit-text-fill-color: {_select_fg} !important;
        opacity: 1 !important;
    }}
    [data-testid="stSidebar"] [data-testid="stSelectbox"] [data-baseweb="select"] input,
    [data-testid="stSidebar"] [data-testid="stSelectbox"] [data-baseweb="select"] span {{
        color: {_select_fg} !important;
        -webkit-text-fill-color: {_select_fg} !important;
        opacity: 1 !important;
    }}
    [data-testid="stSelectbox"] [data-baseweb="select"] svg {{
        fill: {_select_fg} !important;
        color: {_select_fg} !important;
        opacity: 1 !important;
    }}
    [data-baseweb="popover"] [role="listbox"],
    [data-baseweb="popover"] [role="option"] {{
        background: {PALETTE['forest'] if _dark_surface else PALETTE['ivory']} !important;
        color: {PALETTE['ivory'] if _dark_surface else PALETTE['forest']} !important;
        -webkit-text-fill-color: {PALETTE['ivory'] if _dark_surface else PALETTE['forest']} !important;
        opacity: 1 !important;
    }}
    [data-baseweb="popover"] [role="option"]:hover,
    [data-baseweb="popover"] [role="option"][aria-selected="true"] {{
        background: {PALETTE['emerald']} !important;
        color: {PALETTE['ivory']} !important;
        -webkit-text-fill-color: {PALETTE['ivory']} !important;
    }}
    [data-testid="stSelectbox"] [data-baseweb="select"]:focus-within {{
        border-color: {PALETTE['gold']} !important;
        box-shadow: 0 0 0 1px {PALETTE['gold']} !important;
    }}
    [data-testid="stSelectbox"] [data-baseweb="select"][aria-disabled="true"],
    [data-testid="stSelectbox"] [data-baseweb="select"][aria-disabled="true"] * {{
        color: {PALETTE['sage']} !important;
        -webkit-text-fill-color: {PALETTE['sage']} !important;
        opacity: 1 !important;
    }}
    /* Other light-surface controls retain readable Kannada/English text. */
    [data-testid="stTextInput"] input,
    [data-testid="stNumberInput"] input,
    [data-testid="stDateInput"] input,
    [data-testid="stTextArea"] textarea {{
        color: {PALETTE['forest']} !important;
        -webkit-text-fill-color: {PALETTE['forest']} !important;
        opacity: 1 !important;
    }}
    [data-testid="stTextInput"] input::placeholder,
    [data-testid="stNumberInput"] input::placeholder,
    [data-testid="stDateInput"] input::placeholder,
    [data-testid="stTextArea"] textarea::placeholder {{
        color: {PALETTE['sage']} !important;
        -webkit-text-fill-color: {PALETTE['sage']} !important;
        opacity: 1 !important;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)


LANGUAGES = {
    "ಕನ್ನಡ (Kannada) — Available": ("ಕನ್ನಡ (Kannada)", "Operational: tested Gnani STT + deterministic tomato engine"),
    "English — Available": ("English", "Operational: tested Gnani STT + deterministic tomato engine"),
    "हिन्दी (Hindi) — Planned": ("Hindi", "Planned: UI option only; processing is not implemented"),
    "తెలుగు (Telugu) — Planned": ("Telugu", "Planned: UI option only; processing is not implemented"),
    "தமிழ் (Tamil) — Planned": ("Tamil", "Planned: UI option only; processing is not implemented"),
    "मराठी (Marathi) — Planned": ("Marathi", "Planned: UI option only; processing is not implemented"),
}


def status_box(label: str, value: str, tone: str = "neutral") -> None:
    tone_label = {"ready": "READY", "partial": "IN PROGRESS", "planned": "PLANNED", "error": "CHECK"}.get(tone, "INFO")
    st.markdown(f'<div class="status"><strong>{tone_label} · {html.escape(label)}</strong><br>{html.escape(value)}</div>', unsafe_allow_html=True)


def reset_session() -> None:
    for key in ("transcript", "question_text", "guidance", "matches", "parse", "language_understanding", "conversation", "conversation_state", "audio_response", "last_transcribed_audio_fingerprint"):
        st.session_state.pop(key, None)


def process_text(text: str, language: str, input_channel: str = "text") -> str:
    cleaned = text.strip()
    if not cleaned:
        st.session_state["input_error"] = "Enter a question before submitting."
        return ""
    st.session_state.pop("input_error", None)
    st.session_state["transcript"] = cleaned
    st.session_state["question_text"] = cleaned
    if is_market_query(cleaned):
        st.session_state["market_intent_text"] = cleaned
    state = st.session_state.get("conversation_state") or new_conversation()
    profile = farmer_repository.get_profile() or {}
    registered_crops = [crop.get("name") for crop in farmer_repository.list_crops() if crop.get("name")]
    turn = process_turn(
        state,
        cleaned,
        language,
        profile_context={
            "registered_crops": registered_crops,
            "preferred_language": profile.get("preferred_language"),
            "soil_type": profile.get("soil_type"),
            "irrigation_type": profile.get("irrigation_type"),
            "environmental_observations": [
                {"source": "AgroMonitoring", "kind": "weather", "data": st.session_state.get("monitoring_weather")}
            ] if st.session_state.get("monitoring_weather") else [],
        },
    )
    st.session_state["conversation_state"] = state
    st.session_state["language_understanding"] = turn.get("lu", understand(cleaned, input_channel=input_channel))
    st.session_state["parse"] = parse_question(cleaned)
    st.session_state["guidance"] = turn.get("guidance") or build_guidance(cleaned, language, lu_result=st.session_state["language_understanding"])
    st.session_state["matches"] = [] if st.session_state["guidance"].get("safety_category") else search(cleaned, lu_result=st.session_state["language_understanding"])
    st.session_state["conversation"] = state.messages
    return get_answer(cleaned, language)


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


farmer_ui.set_assistant_handler(process_text)


def render_farm_monitoring(language: str) -> None:
    """Show real weather only for a saved farm with explicit coordinates."""
    title = "Farm Monitoring" if language == "English" else "ಜಮೀನು ಮೇಲ್ವಿಚಾರಣೆ"
    st.title(title)
    st.caption("Live AgroMonitoring weather and forecast. No environmental values are estimated locally." if language == "English" else "ನೈಜ AgroMonitoring ಹವಾಮಾನ ಮತ್ತು ಮುನ್ಸೂಚನೆ. ಸ್ಥಳೀಯವಾಗಿ ಯಾವುದೇ ಮೌಲ್ಯ ಅಂದಾಜಿಸಲಾಗುವುದಿಲ್ಲ.")
    farms = farmer_repository.list_farms()
    if not farms:
        st.info("Register a farm first. Coordinates are required for monitoring." if language == "English" else "ಮೊದಲು ಜಮೀನನ್ನು ನೋಂದಾಯಿಸಿ. ಮೇಲ್ವಿಚಾರಣೆಗೆ ನಿರ್ದೇಶಾಂಕಗಳು ಅಗತ್ಯವಿದೆ.")
        return
    choice = st.selectbox("Farm", farms, format_func=lambda farm: farm.get("name", "Unnamed farm"), key="monitoring_farm")
    lat = choice.get("latitude")
    lon = choice.get("longitude")
    if lat is None or lon is None:
        st.warning("This farm has no latitude/longitude saved. Add coordinates before requesting live monitoring data." if language == "English" else "ಈ ಜಮೀನಿಗೆ ಅಕ್ಷಾಂಶ/ರೇಖಾಂಶ ಉಳಿಸಲಾಗಿಲ್ಲ. ನೈಜ ಮೇಲ್ವಿಚಾರಣೆಗೆ ಮೊದಲು ನಿರ್ದೇಶಾಂಕಗಳನ್ನು ಸೇರಿಸಿ.")
        with st.form(f"monitoring_location_{choice['id']}"):
            edit_lat = st.number_input("Latitude", min_value=-90.0, max_value=90.0, value=0.0, format="%.6f")
            edit_lon = st.number_input("Longitude", min_value=-180.0, max_value=180.0, value=0.0, format="%.6f")
            if st.form_submit_button("Save farm location", type="primary"):
                if edit_lat == 0.0 and edit_lon == 0.0:
                    st.error("Enter valid non-zero coordinates.")
                else:
                    farmer_repository.save_farm({"name": choice["name"], "location": choice.get("location"), "area": choice.get("area"), "area_unit": choice.get("area_unit"), "ownership": choice.get("ownership"), "soil_type": choice.get("soil_type"), "irrigation_type": choice.get("irrigation_type"), "water_source": choice.get("water_source"), "notes": choice.get("notes"), "latitude": edit_lat, "longitude": edit_lon}, choice["id"])
                    st.success("Farm location saved.")
                    st.rerun()
        return
    if st.button("Refresh monitoring", type="primary", key="refresh_monitoring"):
        st.session_state.pop("monitoring_weather_error", None)
        st.session_state.pop("monitoring_forecast_error", None)
        with st.spinner("Loading live weather…"):
            try:
                st.session_state["monitoring_weather"] = current_weather(lat=float(lat), lon=float(lon))
                st.session_state["monitoring_last_refresh"] = datetime.now().astimezone().isoformat(timespec="seconds")
            except AgroMonitoringError as exc:
                st.session_state["monitoring_weather_error"] = str(exc)
            try:
                st.session_state["monitoring_forecast"] = weather_forecast(lat=float(lat), lon=float(lon))
            except AgroMonitoringError as exc:
                st.session_state["monitoring_forecast_error"] = str(exc)
    if st.session_state.get("monitoring_weather_error"):
        st.error(st.session_state["monitoring_weather_error"])
    weather = st.session_state.get("monitoring_weather")
    forecast = st.session_state.get("monitoring_forecast")
    if not weather and not forecast:
        st.info("Press Refresh monitoring to request current data." if language == "English" else "ಪ್ರಸ್ತುತ ಮಾಹಿತಿಗಾಗಿ ಮೇಲ್ವಿಚಾರಣೆ ನವೀಕರಿಸಿ ಒತ್ತಿರಿ.")
        return
    if weather:
        main, wind = weather.get("main", {}), weather.get("wind", {})
        condition = (weather.get("weather") or [{}])[0].get("description", "—")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Temperature", f"{temperature_celsius(main.get('temp'))} °C" if temperature_celsius(main.get("temp")) is not None else "—")
        c2.metric("Humidity", f"{main.get('humidity')}%" if main.get("humidity") is not None else "—")
        c3.metric("Condition", condition)
        c4.metric("Wind", f"{wind.get('speed')} m/s" if wind.get("speed") is not None else "—")
        if weather.get("rain", {}).get("3h") is not None:
            st.caption(f"Rainfall (last 3h): {weather['rain']['3h']} mm")
        st.caption(f"Observed: {weather.get('dt', '—')} UTC · Source: AgroMonitoring · Last refresh: {st.session_state.get('monitoring_last_refresh', '—')}")
    if st.session_state.get("monitoring_forecast_error"):
        st.warning(st.session_state["monitoring_forecast_error"])
    if isinstance(forecast, list) and forecast:
        st.subheader("Forecast")
        st.dataframe([{"time": item.get("dt"), "temperature": f"{temperature_celsius(item.get('main', {}).get('temp'))} °C" if temperature_celsius(item.get("main", {}).get("temp")) is not None else "—", "humidity": item.get("main", {}).get("humidity"), "weather": (item.get("weather") or [{}])[0].get("description")} for item in forecast[:8]], use_container_width=True, hide_index=True)


def render_market_prices(language: str) -> None:
    title = "Mandi Market Prices" if language == "English" else "ಮಾರುಕಟ್ಟೆ ಬೆಲೆಗಳು"
    st.title(title)
    st.caption("Actual API observations only; prices are not guaranteed selling prices." if language == "English" else "ನೈಜ API ಮಾಹಿತಿಯಷ್ಟೇ; ಇವು ಖಚಿತ ಮಾರಾಟ ಬೆಲೆಗಳಲ್ಲ.")
    try:
        available_states = states()
    except MarketServiceError as exc:
        st.error(str(exc)); return
    state = st.selectbox("State", available_states, index=available_states.index("Karnataka") if "Karnataka" in available_states else 0)
    try:
        available_commodities = commodities(state=state)
    except MarketServiceError as exc:
        st.error(str(exc)); return
    if not available_commodities:
        st.info("No commodities were returned for this state."); return
    commodity = st.selectbox("Commodity", available_commodities)
    market_list = []
    try:
        market_list = markets(state=state)
    except MarketServiceError as exc:
        st.warning(str(exc))
    districts = sorted({item.get("district") for item in market_list if item.get("district")})
    district = st.selectbox("District (optional)", ["All districts"] + districts)
    market_names = [item.get("market") for item in market_list if item.get("market") and (district == "All districts" or item.get("district") == district)]
    market = st.selectbox("Market (optional)", ["All markets"] + market_names)
    if st.button("Refresh prices", type="primary", key="refresh_market_prices"):
        try:
            st.session_state["market_prices"] = prices(state=state, commodity=commodity, market=None if market == "All markets" else market)
            st.session_state.pop("market_error", None)
        except MarketServiceError as exc:
            st.session_state["market_error"] = str(exc)
    if st.session_state.get("market_error"):
        st.error(st.session_state["market_error"]); return
    payload = st.session_state.get("market_prices")
    if not payload:
        st.info("Press Refresh prices to retrieve current observations."); return
    rows = payload.get("data", []) if isinstance(payload, dict) else []
    if not rows:
        st.info("No price observations were returned for this selection."); return
    if district != "All districts":
        rows = [row for row in rows if row.get("district") == district]
    st.dataframe(rows, use_container_width=True, hide_index=True)
    st.caption(f"API observations returned: {len(rows)}. Arrival dates are retained from the service.")
    if rows:
        values = [row for row in rows if row.get("modal_price") is not None]
        if values:
            st.metric("Latest modal price (INR/quintal)", str(values[-1]["modal_price"]))
        st.caption(f"Freshness: latest arrival date {max(str(row.get('arrival_date', '')) for row in rows)}")
    if st.button("Load historical prices", key="load_market_history"):
        try:
            st.session_state["market_history"] = price_history(state=state, commodity=commodity, market=None if market == "All markets" else market)
            st.session_state.pop("market_history_error", None)
        except MarketServiceError as exc:
            st.session_state["market_history_error"] = str(exc)
    if st.session_state.get("market_history_error"):
        st.error(st.session_state["market_history_error"])
    history = st.session_state.get("market_history", {})
    history_rows = history.get("data", []) if isinstance(history, dict) else []
    chart_rows = [{"date": row.get("arrival_date", row.get("date")), "modal_price": row.get("modal_price")} for row in history_rows if row.get("modal_price") is not None]
    if chart_rows:
        st.line_chart(chart_rows, x="date", y="modal_price")


def render_farmer_application() -> bool:
    """Render the ZIP-derived farmer application as the default shell."""
    farmer_ui.initialize()
    language_label = st.session_state.get("sidebar_language", "English — Available")
    language = "ಕನ್ನಡ" if language_label.startswith("ಕನ್ನಡ") else "English"
    labels = farmer_ui.bilingual_labels(language)
    pages = [
        "Home / Dashboard", "Farmer Profile", "My Farms", "My Crops",
        "Ask KrishiDrishti", "Voice Assistant", "Farm Monitoring", "Mandi Market Prices", "Consultation History",
        "Crop Image Analysis", "Notifications", "Settings", "Help and Support", "Developer tools",
    ]
    with st.sidebar:
        st.markdown('<div class="brand-kicker">KRISHIDRISHTI AI</div><h2 style="color:#F2EBDD">Smart farming. Better tomorrow.</h2>', unsafe_allow_html=True)
        # Radio is intentionally used for the farmer language control: it keeps
        # the selected value and both Kannada/English labels visible even when
        # BaseWeb selectbox portal CSS is altered by a browser/theme extension.
        selected = st.radio(
            "Navigation", [labels.get(page, page) for page in pages[:-1]],
            index=0, key=f"farmer_navigation_{language}",
        )
        selected_page = next((page for page in pages[:-1] if labels.get(page, page) == selected), pages[0])
        st.divider()
        st.session_state["sidebar_language"] = st.radio(
            "Language", ["English — Available", "ಕನ್ನಡ (Kannada) — Available"],
            index=0 if language == "English" else 1, key="farmer_language_selector",
        )
        language = "ಕನ್ನಡ" if st.session_state["sidebar_language"].startswith("ಕನ್ನಡ") else "English"
        st.caption((f"{language} · Five-crop agricultural assistance · Gnani STT: configured" if language == "English" else f"{language} · ಐದು ಬೆಳೆಗಳಿಗೆ ಕೃಷಿ ಮಾಹಿತಿ · Gnani STT: ಸಂರಚಿಸಲಾಗಿದೆ"))
        st.divider()
        if st.button("Developer tools", key="open_developer_tools", width="stretch"):
            st.session_state["developer_tools"] = True
            st.rerun()
    if st.session_state.pop("developer_tools", False):
        return False
    requested = st.session_state.pop("requested_page", None)
    if requested in pages[:-1]:
        selected_page = requested
    renderers = {
        "Home / Dashboard": farmer_ui.dashboard,
        "Farmer Profile": farmer_ui.farmer_profile,
        "My Farms": farmer_ui.my_farms,
        "My Crops": farmer_ui.my_crops,
        "Ask KrishiDrishti": farmer_ui.ask_assistant,
        "Voice Assistant": farmer_ui.voice_assistant,
        "Farm Monitoring": render_farm_monitoring,
        "Mandi Market Prices": render_market_prices,
        "Crop Image Analysis": farmer_ui.crop_image_analysis,
        "Consultation History": farmer_ui.consultation_history,
        "Notifications": farmer_ui.notifications,
        "Settings": farmer_ui.settings,
        "Help and Support": farmer_ui.help_support,
    }
    renderers[selected_page](language)
    return True


if render_farmer_application():
    st.stop()

with st.sidebar:
    st.markdown('<div class="brand-kicker">KrishiDrishti AI</div><h2 style="color:#F2EBDD">Developer tools</h2>', unsafe_allow_html=True)
    view = "Demonstration dashboard"
    language_label = st.selectbox("Language", list(LANGUAGES), key="developer_language")
    language, language_note = LANGUAGES[language_label]
    st.caption(language_note)
    st.divider()
    st.markdown("### Pipeline status")
    status_box("Speech recognition", "Gnani Prisma v2.5 · English and Kannada tested", "ready")
    status_box("Question understanding", "Deterministic parser · tomato-focused", "ready")
    status_box("Translation / SLM", "Not implemented in this milestone", "planned")
    status_box("Conversation orchestration", "Preview state only", "planned")
    status_box("Voice output", "Kannada Timbre v2.5 available on request", "ready")
    st.caption("Credentials are loaded server-side only and are never displayed here.")

st.markdown('<div class="panel-dark"><span class="eyebrow">Developer tools</span><br><h2 style="color:#F2EBDD">Processing console</h2><p>Inspect the real pipeline without exposing internal controls in the farmer-facing application.</p></div>', unsafe_allow_html=True)

if language.startswith("Hindi") or language.startswith("Telugu") or language.startswith("Tamil") or language.startswith("Marathi"):
    st.markdown(f'<div class="panel"><span class="eyebrow">Planned language</span><br><strong>{html.escape(language)}</strong><br>This is a UI preview. Speech recognition, translation, and agricultural processing for this language are not operational yet.</div>', unsafe_allow_html=True)

tabs = st.tabs(["Farmer input", "Understanding", "Investigation", "Conversation", "Voice output", "Dev / test"])

with tabs[0]:
    st.subheader("Farmer input")
    st.caption("Use a real recording, upload an audio clip, or test the deterministic engine with text. No mock transcription is generated.")
    left, right = st.columns(2, gap="large")
    with left:
        st.markdown('<div class="eyebrow">Voice capture</div>', unsafe_allow_html=True)
        generation = st.session_state.setdefault("voice_input_generation", 0)
        audio = st.audio_input("Record a question", key=f"voice_recording_{generation}")
        uploaded = st.file_uploader("Upload audio", type=["wav", "mp3", "m4a", "ogg", "flac", "aac"], key=f"voice_upload_{generation}")
        audio_input = audio or uploaded
        if audio_input:
            st.audio(audio_input)
            if st.button("Transcribe with Gnani Prisma", type="primary", use_container_width=True, key=f"transcribe_voice_{generation}"):
                audio_bytes = audio_input.getvalue() if hasattr(audio_input, "getvalue") else b""
                audio_fingerprint = hashlib.sha256(audio_bytes).hexdigest() if audio_bytes else None
                submission = (generation, audio_fingerprint)
                if audio_fingerprint and submission == st.session_state.get("last_voice_submission"):
                    st.session_state["transcription_status"] = "This recording is already being held for this recorder generation."
                else:
                    try:
                        with st.spinner("Sending audio to Gnani Prisma…"):
                            result = transcribe_audio(audio_input, language)
                        if result.error:
                            st.session_state["input_error"] = result.error
                        else:
                            process_text(result.text or "", language, input_channel="speech_transcript")
                            st.session_state["transcription_status"] = "Verified transcript received from Gnani Prisma."
                        st.session_state["last_voice_submission"] = submission
                    except Exception as exc:
                        st.session_state["input_error"] = f"Voice processing failed: {exc}"
                    finally:
                        st.session_state["voice_input_generation"] = generation + 1
                    st.rerun()
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
    lu = st.session_state.get("language_understanding")
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
        if lu:
            st.markdown("### Contract-shaped extraction")
            st.caption("Deterministic LU layer; confidence remains unset until a documented calibration method exists.")
            st.markdown(f"**Detected language:** `{html.escape(str(lu.get('language', {}).get('primary', 'unknown')))}`")
            if lu.get("observations"):
                for observation in lu["observations"]:
                    evidence = observation.get("evidence", [{}])[0].get("phrase", "")
                    st.markdown(
                        f"- **{html.escape(str(observation.get('kind')))}:** "
                        f"`{html.escape(str(observation.get('normalized_value')) )}` · "
                        f"polarity `{html.escape(str(observation.get('polarity')) )}` · "
                        f"evidence: “{html.escape(str(evidence))}”"
                    )
            if lu.get("missing_information"):
                st.markdown("**Missing information:** " + ", ".join(item.get("field", "unknown") for item in lu["missing_information"]))
            if lu.get("lu_safety_flags"):
                st.warning("Safety review required before providing treatment, dosage, or chemical-mixing guidance.")
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
                if match.reasons:
                    st.caption("Match reasons: " + "; ".join(match.reasons))
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
    if st.button("New Conversation", type="primary", key="new_conversation_button"):
        st.session_state["conversation_state"] = new_conversation()
        for key in ("conversation", "transcript", "question_text", "guidance", "matches", "parse", "language_understanding", "input_error"):
            st.session_state.pop(key, None)
        st.rerun()
    conversation_state = st.session_state.get("conversation_state")
    if conversation_state:
        st.markdown('<div class="panel"><span class="eyebrow">Deterministic conversation engine</span><br><strong>Multi-turn state, follow-up selection, corrections, and safety gating are active.</strong><br>No LLM or external conversation service is used.</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="panel"><span class="eyebrow">Conversation ready</span><br><strong>Submit a farmer message to begin an investigation.</strong></div>', unsafe_allow_html=True)
    history = st.session_state.get("conversation", [])
    if history:
        st.markdown("### Conversation history")
        for turn in history:
            role = "Farmer" if turn.get("role") == "farmer" else "Assistant"
            st.markdown(f"**{role}:** {html.escape(str(turn.get('text', '')))}")
        st.markdown("### Current follow-up questions")
        for question in (st.session_state.get("guidance") or {}).get("follow_up_questions", []):
            st.markdown(f"- {question}")
        if conversation_state and conversation_state.pending_question:
            st.info(conversation_state.pending_question.get("text", "More information is needed."))
        if conversation_state:
            with st.expander("Developer conversation state"):
                st.json({"session_id": conversation_state.session_id, "turn_number": conversation_state.turn_number, "pending_question": conversation_state.pending_question, "asked_questions": conversation_state.asked_questions, "safety_flags": conversation_state.safety_flags, "observations": list(conversation_state.observations.values())})
    else:
        st.caption("No conversation turns yet. Submit text or transcribe audio to begin.")

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

