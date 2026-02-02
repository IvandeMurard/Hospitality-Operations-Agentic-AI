"""Aetherix Sidebar Component"""

import streamlit as st
from config import BRAND_NAME, get_text


def render_sidebar(lang: str = "en") -> dict:
    """
    Render the Aetherix sidebar.

    Returns:
        dict with selected values: {
            "page": str,
            "restaurant": str,
            "service": str,
            "language": str
        }
    """
    with st.sidebar:
        # Brand
        st.markdown(
            f"""
            <div style="margin-bottom: 2rem;">
                <h1 style="color: white; font-size: 1.5rem; font-weight: 700; margin: 0;">
                    {BRAND_NAME}
                </h1>
            </div>
        """,
            unsafe_allow_html=True,
        )

        # Navigation
        st.markdown(
            '<p class="section-header">Navigation</p>', unsafe_allow_html=True
        )

        page = st.radio(
            label="nav",
            options=["forecast", "history", "settings"],
            format_func=lambda x: get_text(f"nav.{x}", lang),
            label_visibility="collapsed",
            key="nav_radio",
        )

        st.divider()

        # Context
        st.markdown(
            '<p class="section-header">Context</p>', unsafe_allow_html=True
        )

        restaurant = st.selectbox(
            label=get_text("sidebar.restaurant", lang),
            options=["Main Restaurant", "Pool Bar", "Room Service"],
            key="restaurant_select",
        )

        service = st.selectbox(
            label=get_text("sidebar.service", lang),
            options=["Breakfast", "Lunch", "Dinner"],
            index=2,  # Default to Dinner
            key="service_select",
        )

        st.divider()

        # Data status
        st.markdown(
            '<p class="section-header">Data</p>', unsafe_allow_html=True
        )

        st.markdown(
            """
            <div style="color: rgba(255,255,255,0.8); font-size: 0.875rem;">
                <div style="margin-bottom: 0.5rem;">
                    <span style="color: rgba(255,255,255,0.5);">Patterns:</span> 495
                </div>
                <div style="margin-bottom: 0.5rem;">
                    <span style="color: rgba(255,255,255,0.5);">Period:</span> 2015-2017
                </div>
                <div>
                    <span style="color: rgba(255,255,255,0.5);">Updated:</span> 2h ago
                </div>
            </div>
        """,
            unsafe_allow_html=True,
        )

        st.divider()

        # Coming Soon
        st.markdown(
            '<p class="section-header">Coming Soon</p>',
            unsafe_allow_html=True,
        )

        st.markdown(
            """
            <div class="coming-soon" style="font-size: 0.875rem; line-height: 1.8;">
                ◇ PMS Integration<br>
                ◇ Staff Planner<br>
                ◇ Inventory<br>
                ◇ Alerts
            </div>
        """,
            unsafe_allow_html=True,
        )

        st.divider()

        # Footer
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(
                """
                <a href="#" style="color: rgba(255,255,255,0.7); text-decoration: none; font-size: 0.875rem;">
                    ? Help
                </a>
            """,
                unsafe_allow_html=True,
            )

        with col2:
            language = st.selectbox(
                label="Language",
                options=["en", "fr"],
                format_func=lambda x: "EN" if x == "en" else "FR",
                label_visibility="collapsed",
                key="lang_select",
            )

    return {
        "page": page,
        "restaurant": restaurant,
        "service": service,
        "language": language,
    }
