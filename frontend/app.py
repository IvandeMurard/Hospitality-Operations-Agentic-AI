"""Aetherix - Intelligence layer for hotel F&B operations"""

import streamlit as st

# Page config must be first Streamlit command
st.set_page_config(
    page_title="Aetherix",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Import after page config
from config import AETHERIX_CSS, get_text
from components.sidebar import render_sidebar
from components.header import render_header

# Initialize session state for prediction persistence (Phase 2)
if "prediction_data" not in st.session_state:
    st.session_state.prediction_data = None
if "has_prediction" not in st.session_state:
    st.session_state.has_prediction = False

# Inject custom CSS
st.markdown(AETHERIX_CSS, unsafe_allow_html=True)

# Get language from session state (set by sidebar selectbox)
lang = st.session_state.get("lang_select", "en")

# Render sidebar and get context
context = render_sidebar(lang=lang)

# Main content area
if context["page"] == "forecast":
    # Render header
    header = render_header(lang=context["language"])

    st.markdown("<br>", unsafe_allow_html=True)

    # Placeholder KPI cards (Phase 2)
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label=get_text("kpi.covers", lang).upper(),
            value="127",
            delta="+12%",
        )
    with col2:
        st.metric(
            label=get_text("kpi.range", lang).upper(),
            value="108 – 146",
        )
    with col3:
        st.metric(
            label=get_text("kpi.staff", lang).upper(),
            value="8 servers",
        )
    with col4:
        st.metric(
            label=get_text("kpi.confidence", lang).upper(),
            value=get_text("confidence.high", lang),
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # Placeholder for chart (Phase 2)
    st.info("Timeline chart will be implemented in Phase 2")

    # Placeholder for panels (Phase 3)
    col1, col2 = st.columns(2)
    with col1:
        st.info("Factors panel will be implemented in Phase 3")
    with col2:
        st.info("Feedback panel will be implemented in Phase 3")

elif context["page"] == "history":
    st.title("History")
    st.info("History page will be implemented in Phase 5")

elif context["page"] == "settings":
    st.title("Settings")
    st.info("Settings page will be implemented in Phase 6")
