import html

import streamlit as st

from agriculture_engine import build_guidance, get_answer
from gnani_service import transcribe_audio
from farmer_profile import repository


KANNADA = "ಕನ್ನಡ"
ENGLISH = "English"


def text(language: str, english: str, kannada: str) -> str:
    return kannada if language == KANNADA else english


def initialize() -> None:
    repository.initialize_database()
    st.session_state.setdefault("farmer_language", KANNADA)
    st.session_state.setdefault("appearance", "Dark")


def bilingual_labels(language: str) -> dict[str, str]:
    return {
        "Home / Dashboard": text(language, "Home / Dashboard", "ಮುಖಪುಟ"),
        "Farmer Profile": text(language, "Farmer Profile", "ರೈತ ವಿವರ"),
        "My Farms": text(language, "My Farms", "ನನ್ನ ಜಮೀನುಗಳು"),
        "My Crops": text(language, "My Crops", "ನನ್ನ ಬೆಳೆಗಳು"),
        "Ask KrishiDrishti": text(language, "Ask KrishiDrishti", "ಕೃಷಿದೃಷ್ಟಿಗೆ ಕೇಳಿ"),
        "Voice Assistant": text(language, "Voice Assistant", "ಧ್ವನಿ ಸಹಾಯಕ"),
        "Consultation History": text(language, "Consultation History", "ಸಹಾಯ ಇತಿಹಾಸ"),
        "Notifications": text(language, "Notifications", "ಅಧಿಸೂಚನೆಗಳು"),
        "Settings": text(language, "Settings", "ಸಂಯೋಜನೆಗಳು"),
        "Help and Support": text(language, "Help and Support", "ಸಹಾಯ ಮತ್ತು ಬೆಂಬಲ"),
        "Farmer experience": text(language, "Farmer experience", "ರೈತ ಅನುಭವ"),
        "Demonstration dashboard": text(language, "Demonstration dashboard", "ಪ್ರದರ್ಶನ ಡ್ಯಾಶ್‌ಬೋರ್ಡ್"),
    }


def _reset_navigation_selection() -> None:
    st.session_state.pop("sidebar_navigation_kn", None)
    st.session_state.pop("sidebar_navigation_en", None)


def sync_sidebar_language() -> None:
    language = {
        "ಕನ್ನಡ (Kannada) — Available": KANNADA,
        "English — Available": ENGLISH,
    }.get(st.session_state.get("sidebar_language"))
    if language:
        if st.session_state.get("farmer_language") != language:
            _reset_navigation_selection()
        st.session_state["farmer_language"] = language
        st.session_state["settings_language"] = language


def sync_settings_language() -> None:
    language = st.session_state["settings_language"]
    if st.session_state.get("farmer_language") != language:
        _reset_navigation_selection()
    st.session_state["farmer_language"] = language
    st.session_state["sidebar_language"] = (
        "ಕನ್ನಡ (Kannada) — Available" if language == KANNADA else "English — Available"
    )


def _metric_grid(items: list[tuple[str, str, str]]) -> None:
    icons = ["🏡", "🌿", "🌾", "🍃", "📅", "💬"]
    grid = st.grid("auto", min_column_width=125, gap="small", key="dashboard_metrics")
    for (label, value, _icon), icon in zip(items, icons):
        with grid.cell():
            st.markdown(
                f"""
                <article class="dashboard-summary-card">
                    <span class="dashboard-summary-icon" aria-hidden="true">{icon}</span>
                    <span class="dashboard-summary-copy">
                        <span class="dashboard-summary-label">{html.escape(label)}</span>
                        <strong class="dashboard-summary-value">{html.escape(value)}</strong>
                    </span>
                </article>
                """,
                unsafe_allow_html=True,
            )


def _area_summary(farms: list[dict]) -> str:
    totals: dict[str, float] = {}
    for farm in farms:
        unit = str(farm.get("area_unit") or "acre").lower()
        totals[unit] = totals.get(unit, 0.0) + float(farm.get("area") or 0)
    if not totals:
        return "0 acres"
    names = {"acre": "acres", "hectare": "hectares", "gunta": "guntas"}
    return " · ".join(f"{amount:g} {names.get(unit, unit)}" for unit, amount in totals.items())


def _go_to(page: str, key: str, label: str, icon: str) -> None:
    if st.button(label, key=key, icon=icon, width="stretch"):
        st.session_state["requested_page"] = page
        st.rerun()


def dashboard(language: str) -> None:
    profile = repository.get_profile()
    farms = repository.list_farms()
    crops = repository.list_crops()
    active = [crop for crop in crops if str(crop.get("status", "")).lower() == "active"]
    consultations = repository.list_consultations()
    notifications = repository.list_notifications()
    unread_count = sum(not bool(item.get("is_read")) for item in notifications)
    name = profile.get("name", "").strip() if profile else ""
    greeting = text(language, "Namaskara", "ನಮಸ್ಕಾರ")
    welcome_name = f", {html.escape(name)}" if name else ""
    welcome_text = text(
        language,
        "Your farming workspace at a glance. Manage your fields, track crops, and get help when you need it.",
        "ನಿಮ್ಮ ಕೃಷಿ ವಿವರಗಳನ್ನು ಒಂದೇ ಸ್ಥಳದಲ್ಲಿ ನೋಡಿ. ಜಮೀನುಗಳನ್ನು ನಿರ್ವಹಿಸಿ, ಬೆಳೆಗಳನ್ನು ಗಮನಿಸಿ ಮತ್ತು ಸಹಾಯ ಪಡೆಯಿರಿ.",
    )
    st.markdown(
        f"""
        <section class="dashboard-hero">
            <div class="dashboard-hero-copy">
                <span class="dashboard-eyebrow">KRISHIDRISHTI AI · SMART FARMING</span>
                <h1>{greeting}{welcome_name}!</h1>
                <p>{welcome_text}</p>
            </div>
            <div class="dashboard-hero-mark" aria-hidden="true">🌱</div>
        </section>
        """,
        unsafe_allow_html=True,
    )

    st.space("small")
    _metric_grid([
        (text(language, "Total farms", "ಒಟ್ಟು ಜಮೀನುಗಳು"), str(len(farms)), "home_work"),
        (text(language, "Registered land", "ನೋಂದಾಯಿತ ಭೂಮಿ"), _area_summary(farms), "landscape"),
        (text(language, "Registered crops", "ನೋಂದಾಯಿತ ಬೆಳೆಗಳು"), str(len(crops)), "grass"),
        (text(language, "Active crops", "ಸಕ್ರಿಯ ಬೆಳೆಗಳು"), str(len(active)), "spa"),
        (text(language, "Upcoming activities", "ಮುಂಬರುವ ಚಟುವಟಿಕೆಗಳು"), "0", "calendar_month"),
        (text(language, "Consultations", "ಸಹಾಯಗಳು"), str(len(consultations)), "forum"),
    ])

    st.subheader(text(language, "Quick actions", "ತ್ವರಿತ ಕ್ರಿಯೆಗಳು"), icon=":material/bolt:")
    quick_actions = [
        ("My Farms", text(language, "Add new farm", "ಜಮೀನು ಸೇರಿಸಿ"), "add_home_work"),
        ("My Crops", text(language, "Register crop", "ಬೆಳೆ ನೋಂದಣಿ"), "grass"),
        ("Ask KrishiDrishti", text(language, "Ask a question", "ಪ್ರಶ್ನೆ ಕೇಳಿ"), "chat"),
        ("Voice Assistant", text(language, "Voice assistant", "ಧ್ವನಿ ಸಹಾಯಕ"), "mic"),
        ("My Crops", text(language, "View my crops", "ಬೆಳೆಗಳನ್ನು ನೋಡಿ"), "eco"),
        ("Consultation History", text(language, "View history", "ಇತಿಹಾಸ ನೋಡಿ"), "history"),
    ]
    quick_grid = st.grid("auto", min_column_width=125, gap="small")
    for index, (page, label, icon) in enumerate(quick_actions):
        if quick_grid.button(label, key=f"dashboard_action_{index}", icon=f":material/{icon}:", width="stretch", wrap=True):
            st.session_state["requested_page"] = page
            st.rerun()

    top_sections = st.columns(3, gap="small")
    with top_sections[0]:
        with st.container(border=True):
            st.subheader(text(language, "My farms", "ನನ್ನ ಜಮೀನುಗಳು"), icon=":material/home_work:")
            if not farms:
                st.caption(text(language, "No farms registered yet.", "ಇನ್ನೂ ಜಮೀನು ನೋಂದಣಿ ಆಗಿಲ್ಲ."))
            for farm in farms[:2]:
                st.markdown(f"**{html.escape(str(farm['name']))}**")
                location = farm.get("location") or text(language, "Location not set", "ಸ್ಥಳ ನೀಡಿಲ್ಲ")
                area = farm.get("area")
                area_label = f"{float(area):g} {farm.get('area_unit') or 'acre'}" if area is not None else "—"
                st.caption(f":material/location_on: {html.escape(str(location))} · {area_label}")
            _go_to("My Farms", "dashboard_view_farms", text(language, "View all farms", "ಎಲ್ಲಾ ಜಮೀನುಗಳು"), ":material/arrow_forward:")
    with top_sections[1]:
        with st.container(border=True):
            st.subheader(text(language, "Active crops", "ಸಕ್ರಿಯ ಬೆಳೆಗಳು"), icon=":material/eco:")
            if not active:
                st.caption(text(language, "No active crops registered yet.", "ಸಕ್ರಿಯ ಬೆಳೆಗಳು ಇನ್ನೂ ಇಲ್ಲ."))
            for crop in active[:2]:
                st.markdown(f"**{html.escape(str(crop['name']))}**")
                details = " · ".join(filter(None, [crop.get("farm_name"), crop.get("growth_stage")]))
                st.caption(html.escape(details or text(language, "Crop details not set", "ಬೆಳೆ ವಿವರ ನೀಡಿಲ್ಲ")))
            _go_to("My Crops", "dashboard_view_crops", text(language, "View all crops", "ಎಲ್ಲಾ ಬೆಳೆಗಳು"), ":material/arrow_forward:")
    with top_sections[2]:
        with st.container(border=True):
            st.subheader(text(language, "Recent activity", "ಇತ್ತೀಚಿನ ಚಟುವಟಿಕೆ"), icon=":material/history:")
            activity_items = []
            if consultations:
                latest = consultations[0]
                activity_items.append((
                    latest.get("topic") or text(language, "Consultation saved", "ಸಹಾಯ ಉಳಿಸಲಾಗಿದೆ"),
                    latest.get("created_at") or "",
                ))
            if farms:
                activity_items.append((
                    text(language, "Farm on your profile", "ನಿಮ್ಮ ಪ್ರೊಫೈಲ್‌ನ ಜಮೀನು"),
                    farms[0]["name"],
                ))
            if crops:
                activity_items.append((
                    text(language, "Crop on your profile", "ನಿಮ್ಮ ಪ್ರೊಫೈಲ್‌ನ ಬೆಳೆ"),
                    crops[0]["name"],
                ))
            if not activity_items:
                st.caption(text(language, "Your saved farm, crop, and consultation activity will appear here.",
                                "ಉಳಿಸಿದ ಜಮೀನು, ಬೆಳೆ ಮತ್ತು ಸಹಾಯ ಚಟುವಟಿಕೆಗಳು ಇಲ್ಲಿ ಕಾಣಿಸುತ್ತವೆ."))
            for label, detail in activity_items[:3]:
                st.markdown(f"• **{html.escape(str(label))}**")
                st.caption(html.escape(str(detail)))

    bottom_sections = st.columns(3, gap="small")
    with bottom_sections[0]:
        with st.container(border=True):
            st.subheader(text(language, "Upcoming activities", "ಮುಂಬರುವ ಚಟುವಟಿಕೆಗಳು"), icon=":material/event:")
            st.caption(text(language, "No scheduled activities are saved yet.", "ಯಾವುದೇ ನಿಗದಿತ ಚಟುವಟಿಕೆಗಳನ್ನು ಉಳಿಸಿಲ್ಲ."))
            st.caption(text(language, "Reminders are not scheduled automatically.", "ಜ್ಞಾಪನೆಗಳನ್ನು ಸ್ವಯಂಚಾಲಿತವಾಗಿ ನಿಗದಿಪಡಿಸುವುದಿಲ್ಲ."))
    with bottom_sections[1]:
        with st.container(border=True):
            st.subheader(text(language, "Recent consultations", "ಇತ್ತೀಚಿನ ಸಹಾಯಗಳು"), icon=":material/forum:")
            if not consultations:
                st.caption(text(language, "No saved consultations yet.", "ಇನ್ನೂ ಸಹಾಯ ಇತಿಹಾಸವಿಲ್ಲ."))
            for consultation in consultations[:2]:
                st.markdown(f"**{html.escape(str(consultation.get('topic') or 'Agricultural question'))}**")
                st.caption(f"{consultation.get('created_at') or ''} · {consultation.get('language') or ''}")
            _go_to("Consultation History", "dashboard_view_history", text(language, "View history", "ಇತಿಹಾಸ ನೋಡಿ"), ":material/arrow_forward:")
    with bottom_sections[2]:
        with st.container(border=True):
            st.subheader(text(language, "Important notifications", "ಮುಖ್ಯ ಅಧಿಸೂಚನೆಗಳು"), icon=":material/notifications:")
            if not notifications:
                st.caption(text(language, "No notifications saved.", "ಅಧಿಸೂಚನೆಗಳಿಲ್ಲ."))
            for item in notifications[:2]:
                status_icon = ":material/circle_notifications:" if not item.get("is_read") else ":material/notifications_none:"
                st.markdown(f"{status_icon} **{html.escape(str(item['title']))}**")
                st.caption(html.escape(str(item.get("description") or item.get("created_at") or "")))
            if unread_count:
                st.badge(text(language, f"{unread_count} unread", f"{unread_count} ಓದಿಲ್ಲ"), color="orange")
            _go_to("Notifications", "dashboard_view_notifications", text(language, "View notifications", "ಅಧಿಸೂಚನೆ ನೋಡಿ"), ":material/arrow_forward:")


def farmer_profile(language: str) -> None:
    profile = repository.get_profile() or {}
    st.title(text(language, "Farmer Profile", "ರೈತ ವಿವರ"))
    with st.form("farmer_profile_form"):
        c1, c2 = st.columns(2)
        with c1:
            name = st.text_input(text(language, "Full name", "ಪೂರ್ಣ ಹೆಸರು"), value=profile.get("name", ""))
            mobile = st.text_input(text(language, "Mobile number", "ಮೊಬೈಲ್ ಸಂಖ್ಯೆ"), value=profile.get("mobile", ""))
            email = st.text_input(text(language, "Email address", "ಇಮೇಲ್ ವಿಳಾಸ"), value=profile.get("email", ""))
            age = st.number_input(text(language, "Age", "ವಯಸ್ಸು"), min_value=0, max_value=120, value=int(profile.get("age") or 0), step=1)
            gender = st.selectbox(text(language, "Gender", "ಲಿಂಗ"), ["", "Male", "Female", "Non-binary", "Prefer not to say"], index=0)
        with c2:
            village = st.text_input(text(language, "Village", "ಗ್ರಾಮ"), value=profile.get("village", ""))
            gram_panchayat = st.text_input(text(language, "Gram Panchayat", "ಗ್ರಾಮ ಪಂಚಾಯಿತಿ"), value=profile.get("gram_panchayat", ""))
            taluk = st.text_input(text(language, "Taluk", "ತಾಲೂಕು"), value=profile.get("taluk", ""))
            district = st.text_input(text(language, "District", "ಜಿಲ್ಲೆ"), value=profile.get("district", ""))
            state = st.text_input(text(language, "State", "ರಾಜ್ಯ"), value=profile.get("state", ""))
            pin_code = st.text_input(text(language, "PIN code", "ಪಿನ್ ಕೋಡ್"), value=profile.get("pin_code", ""))

        st.subheader(text(language, "Preferences", "ಆದ್ಯತೆಗಳು"))
        p1, p2, p3 = st.columns(3)
        preferred_language = p1.selectbox(text(language, "Preferred language", "ಆದ್ಯತೆಯ ಭಾಷೆ"), [ENGLISH, KANNADA], index=[ENGLISH, KANNADA].index(profile.get("preferred_language", KANNADA)))
        response_mode = p2.selectbox(text(language, "Response mode", "ಪ್ರತಿಕ್ರಿಯೆ ವಿಧಾನ"), ["Text", "Voice", "Text and Voice"], index=0)
        text_size = p3.selectbox(text(language, "Text size", "ಅಕ್ಷರದ ಗಾತ್ರ"), ["Small", "Medium", "Large"], index=["Small", "Medium", "Large"].index(profile.get("text_size", "Medium")))
        voice_response = st.toggle(text(language, "Enable voice responses", "ಧ್ವನಿ ಪ್ರತಿಕ್ರಿಯೆ ಸಕ್ರಿಯಗೊಳಿಸಿ"), value=bool(profile.get("voice_response")))
        notifications = st.toggle(text(language, "Enable notifications", "ಅಧಿಸೂಚನೆಗಳನ್ನು ಸಕ್ರಿಯಗೊಳಿಸಿ"), value=bool(profile.get("notifications", 1)))
        submitted = st.form_submit_button(text(language, "Save profile", "ರೈತ ವಿವರ ಉಳಿಸಿ"), type="primary", width="stretch")

    if submitted:
        errors = []
        if not name.strip():
            errors.append(text(language, "Name is required.", "ಹೆಸರು ಅಗತ್ಯವಿದೆ."))
        digits = "".join(ch for ch in mobile if ch.isdigit())
        if mobile and len(digits) < 10:
            errors.append(text(language, "Enter a valid 10-digit mobile number.", "ಮಾನ್ಯವಾದ 10 ಅಂಕಿಯ ಮೊಬೈಲ್ ಸಂಖ್ಯೆ ನೀಡಿ."))
        if pin_code and (not pin_code.isdigit() or len(pin_code) != 6):
            errors.append(text(language, "PIN code must contain 6 digits.", "ಪಿನ್ ಕೋಡ್ 6 ಅಂಕಿಗಳನ್ನು ಹೊಂದಿರಬೇಕು."))
        if errors:
            st.error(" ".join(errors))
        else:
            repository.save_profile({
                "name": name.strip(), "mobile": mobile.strip(), "email": email.strip(),
                "age": age or None, "gender": gender or None, "village": village.strip(),
                "gram_panchayat": gram_panchayat.strip(), "taluk": taluk.strip(),
                "district": district.strip(), "state": state.strip(), "pin_code": pin_code.strip(),
                "preferred_language": preferred_language, "response_mode": response_mode,
                "text_size": text_size, "voice_response": int(voice_response),
                "notifications": int(notifications),
            })
            st.session_state["farmer_language"] = preferred_language
            st.success(text(language, "Profile saved successfully.", "ರೈತ ವಿವರ ಯಶಸ್ವಿಯಾಗಿ ಉಳಿಸಲಾಗಿದೆ."))


def _delete_confirm(title: str, action_key: str, callback) -> None:
    if st.button(text(st.session_state["farmer_language"], "Delete", "ಅಳಿಸಿ"), key=action_key, icon=":material/delete:", type="secondary"):
        @st.dialog(title)
        def confirm():
            st.write(text(st.session_state["farmer_language"], "This action cannot be undone.", "ಈ ಕ್ರಿಯೆಯನ್ನು ಹಿಂತೆಗೆದುಕೊಳ್ಳಲು ಸಾಧ್ಯವಿಲ್ಲ."))
            c1, c2 = st.columns(2)
            if c1.button(text(st.session_state["farmer_language"], "Cancel", "ರದ್ದುಮಾಡಿ"), width="stretch"):
                st.rerun()
            if c2.button(text(st.session_state["farmer_language"], "Delete", "ಅಳಿಸಿ"), type="primary", width="stretch"):
                callback()
                st.rerun()
        confirm()


def my_farms(language: str) -> None:
    st.title(text(language, "My Farms", "ನನ್ನ ಜಮೀನುಗಳು"))
    farms = repository.list_farms()
    with st.expander(text(language, "Add new farm", "ಹೊಸ ಜಮೀನು ಸೇರಿಸಿ"), icon=":material/add_home_work:", expanded=False):
        with st.form("farm_form"):
            c1, c2 = st.columns(2)
            name = c1.text_input(text(language, "Farm name", "ಜಮೀನಿನ ಹೆಸರು"))
            location = c2.text_input(text(language, "Village / location", "ಗ್ರಾಮ / ಸ್ಥಳ"))
            area = c1.number_input(text(language, "Land area", "ಭೂಮಿ ವಿಸ್ತೀರ್ಣ"), min_value=0.0, step=0.1)
            area_unit = c2.selectbox(text(language, "Area unit", "ಒಳಗೊಂಡ ಘಟಕ"), ["acre", "hectare", "gunta"])
            ownership = c1.selectbox(text(language, "Ownership", "ಹಕ್ಕು"), ["Owned", "Leased", "Shared", "Other"])
            soil = c2.selectbox(text(language, "Soil type", "ಮಣ್ಣಿನ ಪ್ರಕಾರ"), ["Red soil", "Black soil", "Sandy soil", "Loamy soil", "Clay soil", "Other", "Unknown"])
            irrigation = c1.selectbox(text(language, "Irrigation", "ನೀರಾವರಿ"), ["Rainfed", "Borewell", "Open well", "Canal", "Drip irrigation", "Sprinkler", "Other"])
            water_source = c2.text_input(text(language, "Water source", "ನೀರಿನ ಮೂಲ"))
            notes = st.text_area(text(language, "Additional notes", "ಹೆಚ್ಚಿನ ಟಿಪ್ಪಣಿಗಳು"))
            submitted = st.form_submit_button(text(language, "Save farm", "ಜಮೀನು ಉಳಿಸಿ"), type="primary", width="stretch")
        if submitted:
            if not name.strip():
                st.error(text(language, "Farm name is required.", "ಜಮೀನಿನ ಹೆಸರು ಅಗತ್ಯವಿದೆ."))
            else:
                repository.save_farm({"name": name.strip(), "location": location.strip(), "area": area,
                                      "area_unit": area_unit, "ownership": ownership, "soil_type": soil,
                                      "irrigation_type": irrigation, "water_source": water_source.strip(), "notes": notes.strip()})
                st.success(text(language, "Farm saved.", "ಜಮೀನು ಉಳಿಸಲಾಗಿದೆ."))
                st.rerun()

    if not farms:
        st.info(text(language, "No farms registered.", "ಯಾವುದೇ ಜಮೀನು ನೋಂದಣಿ ಆಗಿಲ್ಲ."))
    for farm in farms:
        with st.container(border=True):
            c1, c2 = st.columns([4, 1])
            c1.markdown(f"### {html.escape(str(farm['name']))}")
            c1.caption(f"{farm.get('location') or '—'} · {farm.get('area') or 0:g} {farm.get('area_unit') or ''}")
            c1.write(f"{text(language, 'Ownership', 'ಹಕ್ಕು')}: {farm.get('ownership') or '—'}")
            c1.write(f"{text(language, 'Soil', 'ಮಣ್ಣು')}: {farm.get('soil_type') or '—'}")
            c1.write(f"{text(language, 'Irrigation', 'ನೀರಾವರಿ')}: {farm.get('irrigation_type') or '—'}")
            with c2:
                if st.button(text(language, "Edit", "ತಿದ್ದಿ"), key=f"edit_farm_{farm['id']}", width="stretch", icon=":material/edit:"):
                    st.session_state["editing_farm"] = farm["id"]
            if st.session_state.get("editing_farm") == farm["id"]:
                with st.form(f"edit_farm_{farm['id']}"):
                    edit_name = st.text_input(text(language, "Farm name", "ಜಮೀನಿನ ಹೆಸರು"), value=farm["name"])
                    edit_location = st.text_input(text(language, "Village / location", "ಗ್ರಾಮ / ಸ್ಥಳ"), value=farm.get("location") or "")
                    edit_area = st.number_input(text(language, "Land area", "ಭೂಮಿ ವಿಸ್ತೀರ್ಣ"), min_value=0.0, value=float(farm.get("area") or 0), step=0.1)
                    edit_unit = st.selectbox(text(language, "Area unit", "ಒಳಗೊಂಡ ಘಟಕ"), ["acre", "hectare", "gunta"], index=["acre", "hectare", "gunta"].index(farm.get("area_unit") or "acre"))
                    edit_notes = st.text_area(text(language, "Additional notes", "ಹೆಚ್ಚಿನ ಟಿಪ್ಪಣಿಗಳು"), value=farm.get("notes") or "")
                    if st.form_submit_button(text(language, "Save changes", "ಬದಲಾವಣೆ ಉಳಿಸಿ"), type="primary", width="stretch"):
                        if not edit_name.strip():
                            st.error(text(language, "Farm name is required.", "ಜಮೀನಿನ ಹೆಸರು ಅಗತ್ಯವಿದೆ."))
                        else:
                            repository.save_farm({"name": edit_name.strip(), "location": edit_location.strip(), "area": edit_area,
                                                  "area_unit": edit_unit, "ownership": farm.get("ownership"),
                                                  "soil_type": farm.get("soil_type"), "irrigation_type": farm.get("irrigation_type"),
                                                  "water_source": farm.get("water_source"), "notes": edit_notes.strip()}, farm["id"])
                            st.session_state.pop("editing_farm", None)
                            st.success(text(language, "Farm updated.", "ಜಮೀನು ನವೀಕರಿಸಲಾಗಿದೆ."))
                            st.rerun()
            _delete_confirm(text(language, "Delete farm", "ಜಮೀನು ಅಳಿಸಿ"), f"delete_farm_{farm['id']}", lambda farm_id=farm["id"]: repository.delete_farm(farm_id))


def my_crops(language: str) -> None:
    st.title(text(language, "My Crops", "ನನ್ನ ಬೆಳೆಗಳು"))
    farms = repository.list_farms()
    crops = repository.list_crops()

    filter_col1, filter_col2 = st.columns(2)
    seasons = sorted({crop["season"] for crop in crops if crop.get("season")})
    statuses = ["All", "Active", "Harvested", "Failed", "Cancelled"]
    season_filter = filter_col1.selectbox(text(language, "Season", "ಋತು"), ["All"] + seasons)
    status_filter = filter_col2.selectbox(text(language, "Status", "ಸ್ಥಿತಿ"), statuses)

    with st.expander(text(language, "Register new crop", "ಹೊಸ ಬೆಳೆ ನೋಂದಣಿ"), icon=":material/grass:", expanded=False):
        if not farms:
            st.warning(text(language, "Register a farm before adding crops.", "ಬೆಳೆ ಸೇರಿಸುವ ಮೊದಲು ಜಮೀನು ನೋಂದಾಯಿಸಿ."))
        else:
            with st.form("crop_form"):
                c1, c2 = st.columns(2)
                name = c1.text_input(text(language, "Crop name", "ಬೆಳೆಯ ಹೆಸರು"))
                farm_id = c2.selectbox(text(language, "Associated farm", "ಸಂಬಂಧಿತ ಜಮೀನು"), [farm["id"] for farm in farms],
                                       format_func=lambda item: next(farm["name"] for farm in farms if farm["id"] == item))
                variety = c1.text_input(text(language, "Crop variety", "ಬೆಳೆ ಪ್ರಭೇದ"))
                season = c2.selectbox(text(language, "Season", "ಋತು"), ["Kharif", "Rabi", "Zaid", "Perennial", "Other"])
                sowing_date = c1.date_input(text(language, "Sowing date", "ಬಿತ್ತನೆ ದಿನಾಂಕ"), value=None)
                cultivated_area = c2.number_input(text(language, "Cultivated area", "ಬೆಳೆ ವಿಸ್ತೀರ್ಣ"), min_value=0.0, step=0.1)
                growth_stage = c1.selectbox(text(language, "Growth stage", "ಬೆಳವಣಿಗೆಯ ಹಂತ"), [
                    "Land preparation", "Sowing", "Germination", "Seedling", "Vegetative growth",
                    "Flowering", "Fruiting", "Maturity", "Harvesting", "Harvested",
                ])
                expected_harvest = c2.date_input(text(language, "Expected harvest date", "ಸಂಪಾದನೆ ದಿನಾಂಕ"), value=None)
                status = c1.selectbox(text(language, "Crop status", "ಬೆಳೆಯ ಸ್ಥಿತಿ"), ["Active", "Harvested", "Failed", "Cancelled"])
                submitted = st.form_submit_button(text(language, "Save crop", "ಬೆಳೆ ಉಳಿಸಿ"), type="primary", width="stretch")
            if submitted:
                if not name.strip():
                    st.error(text(language, "Crop name is required.", "ಬೆಳೆಯ ಹೆಸರು ಅಗತ್ಯವಿದೆ."))
                else:
                    repository.save_crop({
                        "name": name.strip(), "farm_id": int(farm_id), "variety": variety.strip(),
                        "season": season, "sowing_date": sowing_date.isoformat() if sowing_date else None,
                        "cultivated_area": cultivated_area, "growth_stage": growth_stage,
                        "expected_harvest": expected_harvest.isoformat() if expected_harvest else None,
                        "status": status,
                    })
                    st.success(text(language, "Crop saved.", "ಬೆಳೆ ಉಳಿಸಲಾಗಿದೆ."))
                    st.rerun()

    filtered = [crop for crop in crops
                if (season_filter == "All" or crop.get("season") == season_filter)
                and (status_filter == "All" or crop.get("status") == status_filter)]
    if not filtered:
        st.info(text(language, "No crops match these filters.", "ಈ ಫಿಲ್ಟರ್ಗಳಿಗೆ ಬೆಳೆಗಳು ಹೊಂದಿಕೆಯಾಗುವುದಿಲ್ಲ."))
    for crop in filtered:
        with st.container(border=True):
            c1, c2 = st.columns([4, 1])
            c1.markdown(f"### {html.escape(str(crop['name']))}")
            c1.caption(f"{crop.get('farm_name') or '—'} · {crop.get('season') or '—'} · {crop.get('status') or '—'}")
            c1.write(f"{text(language, 'Growth stage', 'ಬೆಳವಣಿಗೆಯ ಹಂತ')}: {crop.get('growth_stage') or '—'}")
            c1.write(f"{text(language, 'Variety', 'ಪ್ರಭೇದ')}: {crop.get('variety') or '—'}")
            c1.write(f"{text(language, 'Sowing date', 'ಬಿತ್ತನೆ ದಿನಾಂಕ')}: {crop.get('sowing_date') or '—'}")
            c1.write(f"{text(language, 'Expected harvest', 'ಸಂಪಾದನೆ')}: {crop.get('expected_harvest') or '—'}")
            with c2:
                if st.button(text(language, "Edit", "ತಿದ್ದಿ"), key=f"edit_crop_{crop['id']}", width="stretch", icon=":material/edit:"):
                    st.session_state["editing_crop"] = crop["id"]
            if st.session_state.get("editing_crop") == crop["id"]:
                with st.form(f"edit_crop_{crop['id']}"):
                    stage = st.selectbox(text(language, "Growth stage", "ಬೆಳವಣಿಗೆಯ ಹಂತ"), [
                        "Land preparation", "Sowing", "Germination", "Seedling", "Vegetative growth",
                        "Flowering", "Fruiting", "Maturity", "Harvesting", "Harvested",
                    ], index=0)
                    status = st.selectbox(text(language, "Crop status", "ಬೆಳೆಯ ಸ್ಥಿತಿ"), ["Active", "Harvested", "Failed", "Cancelled"],
                                          index=["Active", "Harvested", "Failed", "Cancelled"].index(crop.get("status") or "Active"))
                    if st.form_submit_button(text(language, "Save changes", "ಬದಲಾವಣೆ ಉಳಿಸಿ"), type="primary", width="stretch"):
                        repository.save_crop({"name": crop["name"], "farm_id": crop.get("farm_id"),
                                              "variety": crop.get("variety"), "season": crop.get("season"),
                                              "sowing_date": crop.get("sowing_date"), "cultivated_area": crop.get("cultivated_area"),
                                              "growth_stage": stage, "expected_harvest": crop.get("expected_harvest"),
                                              "status": status}, crop["id"])
                        st.session_state.pop("editing_crop", None)
                        st.success(text(language, "Crop updated.", "ಬೆಳೆ ನವೀಕರಿಸಲಾಗಿದೆ."))
                        st.rerun()
            _delete_confirm(text(language, "Delete crop", "ಬೆಳೆ ಅಳಿಸಿ"), f"delete_crop_{crop['id']}", lambda crop_id=crop["id"]: repository.delete_crop(crop_id))


def ask_assistant(language: str) -> None:
    st.title(text(language, "Ask KrishiDrishti", "ಕೃಷಿದೃಷ್ಟಿಗೆ ಕೇಳಿ"))
    farms = repository.list_farms()
    crops = repository.list_crops()
    farm_id = None
    crop_id = None
    c1, c2 = st.columns(2)
    farm_choice = c1.selectbox(text(language, "Farm", "ಜಮೀನು"), ["General question"] + [farm["name"] for farm in farms])
    if farm_choice != "General question":
        farm_id = next(farm["id"] for farm in farms if farm["name"] == farm_choice)
    matching_crops = [crop for crop in crops if farm_id is None or crop.get("farm_id") == farm_id]
    crop_choice = c2.selectbox(text(language, "Crop", "ಬೆಳೆ"), ["No crop selected"] + [crop["name"] for crop in matching_crops])
    if crop_choice != "No crop selected":
        crop_id = next(crop["id"] for crop in matching_crops if crop["name"] == crop_choice)

    st.caption(text(language, "Quick questions", "ತ್ವರಿತ ಪ್ರಶ್ನೆಗಳು"))
    suggestions = [
        "How should I manage my tomato crop?",
        "What should I do about yellow leaves?",
        "How can I identify common pests?",
    ]
    suggestion_row = st.container(horizontal=True)
    for index, suggestion in enumerate(suggestions):
        if suggestion_row.button(suggestion, key=f"quick_question_{index}"):
            st.session_state["chat_pending"] = suggestion
            st.rerun()

    history = st.session_state.setdefault("chat_history", [])
    for message in history:
        with st.chat_message(message["role"], avatar=":material/person:" if message["role"] == "user" else ":material/eco:"):
            st.markdown(message["content"])

    prompt = st.session_state.pop("chat_pending", None) or st.chat_input(
        text(language, "Ask in Kannada or English", "ಕನ್ನಡ ಅಥವಾ ಇಂಗ್ಲಿಷ್ನಲ್ಲಿ ಕೇಳಿ")
    )
    if prompt:
        history.append({"role": "user", "content": prompt})
        guidance = build_guidance(prompt, language)
        answer = get_answer(prompt, language)
        history.append({"role": "assistant", "content": answer})
        repository.save_consultation(
            guidance.get("understanding") or "Agricultural question",
            prompt,
            answer,
            farm_id,
            crop_id,
            language,
        )
        st.rerun()

    if st.button(text(language, "Clear conversation", "ಸಂಭಾಷಣೆ ತೆರವುಗೊಳಿಸಿ"), icon=":material/delete_sweep:"):
        st.session_state["chat_history"] = []
        st.rerun()


def voice_assistant(language: str) -> None:
    st.title(text(language, "Voice Assistant", "ಧ್ವನಿ ಸಹಾಯಕ"))
    st.caption(text(language, "Ready", "ತಯಾರಾಗಿದೆ"))
    audio = st.audio_input(text(language, "Record a question", "ಪ್ರಶ್ನೆಯನ್ನು ರೆಕಾರ್ಡ್ ಮಾಡಿ"))
    uploaded = st.file_uploader(text(language, "Or upload audio", "ಅಥವಾ ಧ್ವನಿ ಅಪ್ಲೋಡ್ ಮಾಡಿ"), type=["wav", "mp3", "m4a", "ogg", "flac", "aac"])
    selected = audio or uploaded
    if selected:
        st.audio(selected)
        if st.button(text(language, "Submit recording", "ರೆಕಾರ್ಡಿಂಗ್ ಸಲ್ಲಿಸಿ"), type="primary", icon=":material/send:", width="stretch"):
            with st.spinner(text(language, "Processing recording", "ರೆಕಾರ್ಡಿಂಗ್ ಪ್ರಕ್ರಿಯೆಯಲ್ಲಿದೆ")):
                result = transcribe_audio(selected, language)
            if result.error:
                st.error(result.error)
            else:
                st.success(text(language, "Transcription completed", "ಧ್ವನಿ ಪಠ್ಯ ಪೂರ್ಣಗೊಂಡಿದೆ"))
                st.text_area(text(language, "Recognized text", "ಗುರುತಿಸಿದ ಪಠ್ಯ"), value=result.text or "", height=120)


def consultation_history(language: str) -> None:
    st.title(text(language, "Consultation History", "ಸಹಾಯ ಇತಿಹಾಸ"))
    consultations = repository.list_consultations()
    search_text = st.text_input(text(language, "Search history", "ಇತಿಹಾಸ ಹುಡುಕಿ"), label_visibility="collapsed", placeholder=text(language, "Search consultations", "ಸಹಾಯ ಹುಡುಕಿ"))
    if search_text:
        needle = search_text.lower()
        consultations = [item for item in consultations if needle in str(item.get("question") or "").lower()
                         or needle in str(item.get("topic") or "").lower()]
    if not consultations:
        st.info(text(language, "No saved consultations.", "ನೋಂದಾಯಿತ ಸಹಾಯಗಳಿಲ್ಲ."))
    for item in consultations:
        with st.expander(f"{item.get('topic') or 'Agricultural question'} · {item.get('created_at') or ''}",
                         icon=":material/history:", expanded=False):
            st.caption(f"{item.get('farm_name') or 'General'} · {item.get('crop_name') or 'No crop'} · {item.get('language') or '—'}")
            st.markdown(f"**{text(language, 'Question', 'ಪ್ರಶ್ನೆ')}**")
            st.write(item.get("question") or "")
            st.markdown(f"**{text(language, 'Response', 'ಪ್ರತಿಕ್ರಿಯೆ')}**")
            st.write(item.get("answer") or "")
            if st.button(text(language, "Delete consultation", "ಸಹಾಯ ಅಳಿಸಿ"), key=f"delete_consultation_{item['id']}",
                         icon=":material/delete:", type="secondary"):
                repository.delete_consultation(item["id"])
                st.success(text(language, "Consultation deleted.", "ಸಹಾಯ ಅಳಿಸಲಾಗಿದೆ."))
                st.rerun()


def notifications(language: str) -> None:
    st.title(text(language, "Notifications", "ಅಧಿಸೂಚನೆಗಳು"))
    items = repository.list_notifications()
    c1, c2 = st.columns([1, 1])
    if c1.button(text(language, "Mark all as read", "ಎಲ್ಲವನ್ನೂ ಓದಿದೆ ಎಂದು ಗುರುತು"), icon=":material/done_all:", width="stretch"):
        repository.mark_all_notifications_read()
        st.rerun()
    if c2.button(text(language, "Refresh", "ನವೀಕರಿಸಿ"), icon=":material/refresh:", width="stretch"):
        st.rerun()

    if not items:
        st.info(text(language, "No notifications are currently saved.", "ಈ ಸಮಯದಲ್ಲಿ ಯಾವುದೇ ಅಧಿಸೂಚನೆಗಳಿಲ್ಲ."))
        return
    for item in items:
        with st.container(border=True):
            if item.get("is_read"):
                st.badge(text(language, "Read", "ಓದಲಾಗಿದೆ"), color="gray")
            else:
                st.badge(text(language, "Unread", "ಓದಿಲ್ಲ"), color="green")
            st.markdown(f"**{html.escape(str(item['title']))}**")
            st.caption(str(item.get("created_at") or ""))
            if item.get("description"):
                st.write(item["description"])
            c1, c2 = st.columns(2)
            if not item.get("is_read") and c1.button(text(language, "Mark as read", "ಓದಿದೆ ಎಂದು ಗುರುತು"),
                                                       key=f"read_notification_{item['id']}", width="stretch"):
                repository.mark_notification_read(item["id"])
                st.rerun()
            if c2.button(text(language, "Delete", "ಅಳಿಸಿ"), key=f"delete_notification_{item['id']}",
                          icon=":material/delete:", width="stretch"):
                repository.delete_notification(item["id"])
                st.rerun()


def settings(language: str) -> None:
    st.title(text(language, "Settings", "ಸಂಯೋಜನೆಗಳು"))
    st.subheader(text(language, "Language", "ಭಾಷೆ"))
    language_choice = st.segmented_control(
        text(language, "Interface language", "ಇಂಟರ್ಫೇಸ್ ಭಾಷೆ"),
        [ENGLISH, KANNADA],
        selection_mode="single",
        default=language,
        key="settings_language",
        on_change=sync_settings_language,
    )
    if language_choice:
        st.session_state["farmer_language"] = language_choice

    st.subheader(text(language, "Accessibility", "ಸುಲಭ ಪ್ರವೇಶ"))
    text_size = st.segmented_control(text(language, "Text size", "ಅಕ್ಷರದ ಗಾತ್ರ"),
                                     ["Small", "Medium", "Large"], selection_mode="single", default="Medium")
    st.session_state["text_size"] = text_size or "Medium"

    st.subheader(text(language, "Appearance", "ದೃಶ್ಯ"))
    dark_mode = st.session_state.get("appearance") == "Dark"
    mode_label = text(language, "Switch to light mode", "ಬೆಳಕು ಮೋಡ್‌ಗೆ ಬದಲಿಸಿ") if dark_mode else text(
        language, "Switch to dark mode", "ಕತ್ತಲೆ ಮೋಡ್‌ಗೆ ಬದಲಿಸಿ"
    )
    mode_icon = ":material/light_mode:" if dark_mode else ":material/dark_mode:"
    if st.button(mode_label, icon=mode_icon, key="settings_mode_toggle", width="stretch"):
        st.session_state["appearance"] = "Light" if dark_mode else "Dark"
        st.rerun()

    st.subheader(text(language, "Voice", "ಧ್ವನಿ"))
    voice_response = st.toggle(text(language, "Enable voice responses", "ಧ್ವನಿ ಪ್ರತಿಕ್ರಿಯೆ ಸಕ್ರಿಯಗೊಳಿಸಿ"),
                               value=st.session_state.setdefault("voice_response", True))
    st.session_state["voice_response"] = voice_response
    preferred_voice_language = st.selectbox(text(language, "Speech language", "ಧ್ವನಿ ಭಾಷೆ"),
                                            [ENGLISH, KANNADA])
    st.session_state["voice_language"] = preferred_voice_language

    if st.button(text(language, "Save settings", "ಸಂಯೋಜನೆಗಳನ್ನು ಉಳಿಸಿ"), type="primary", icon=":material/save:", width="stretch"):
        profile = repository.get_profile()
        if profile:
            repository.save_profile({
                "preferred_language": language_choice or language,
                "text_size": text_size or "Medium",
                "voice_response": int(voice_response),
            })
        st.success(text(language, "Settings saved.", "ಸಂಯೋಜನೆಗಳನ್ನು ಉಳಿಸಲಾಗಿದೆ."))


def help_support(language: str) -> None:
    st.title(text(language, "Help and Support", "ಸಹಾಯ ಮತ್ತು ಬೆಂಬಲ"))
    st.caption(text(language, "Choose a topic to learn how to use KrishiDrishti AI.",
                   "ಕೃಷಿದೃಷ್ಟಿ AI ಬಳಸುವುದು ಹೇಗೆಂದು ತಿಳಿಯಲು ವಿಷಯವನ್ನು ಆರಿಸಿ."))
    topics = [
        ("Create a farmer profile", "Open Farmer Profile and enter the required personal and location information."),
        ("Add a farm", "Open My Farms, expand Add new farm, and save all available farm details."),
        ("Register a crop", "Open My Crops and associate the crop with an existing farm."),
        ("Ask an agricultural question", "Open Ask KrishiDrishti. Optionally select a farm and crop, then send your question."),
        ("Use voice interaction", "Open Voice Assistant, record or upload audio, and submit it for transcription."),
    ]
    for title, description in topics:
        with st.expander(title, icon=":material/help:", expanded=False):
            st.write(description)
    st.subheader(text(language, "Supported languages", "ಬೆಂಬಲಿತ ಭಾಷೆಗಳು"))
    st.write("Kannada (ಕನ್ನಡ) · English")
    st.subheader(text(language, "Frequently asked questions", "ಪದೇ ಪದೇ ಕೇಳುವ ಪ್ರಶ್ನೆಗಳು"))
    with st.expander(text(language, "Where is my profile stored?", "ನನ್ನ ವಿವರ ಎಲ್ಲಿ ಉಳಿಯುತ್ತದೆ?"), expanded=False):
        st.write(text(language, "Profile and farm records are stored locally in the application database.",
                       "ರೈತ ಮತ್ತು ಜಮೀನು ವಿವರಗಳನ್ನು ಸ್ಥಳೀಯ ಅಪ್ಲಿಕೇಶನ್ ಡೇಟಾಬೇಸ್‌ನಲ್ಲಿ ಉಳಿಸಲಾಗುತ್ತದೆ."))
