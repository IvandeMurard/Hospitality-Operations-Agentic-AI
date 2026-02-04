"""Aetherix Header Component"""

import streamlit as st
from datetime import datetime, timedelta
from config import get_text


def _navigate_period(direction: int, view: str) -> None:
    """Navigate to previous/next period"""
    current = st.session_state.selected_date

    if view == "day":
        st.session_state.selected_date = current + timedelta(days=direction)
    elif view == "week":
        st.session_state.selected_date = current + timedelta(weeks=direction)
    else:
        # Month navigation
        if direction > 0:
            next_month = current.replace(day=28) + timedelta(days=4)
            st.session_state.selected_date = next_month.replace(day=1)
        else:
            st.session_state.selected_date = (
                current.replace(day=1) - timedelta(days=1)
            ).replace(day=1)
    
    # Mark that user has requested a forecast
    st.session_state.forecast_requested = True
    st.rerun()


def render_header(lang: str = "en") -> dict:
    """
    Render the page header with view toggle and period selector.

    Returns:
        dict with: {
            "view": "day" | "week" | "month",
            "selected_date": datetime,
            "period_start": datetime,
            "period_end": datetime
        }
    """
    # Initialize session state for date
    if "selected_date" not in st.session_state:
        st.session_state.selected_date = datetime.now()

    col1, col2 = st.columns([1, 2])

    with col1:
        # View toggle - mark forecast requested when view changes
        previous_view = st.session_state.get("previous_view")
        view = st.radio(
            label="View",
            options=["day", "week", "month"],
            format_func=lambda x: get_text(f"header.{x}", lang),
            horizontal=True,
            label_visibility="collapsed",
            key="view_toggle",
        )
        # Check if view changed and mark forecast requested
        if previous_view is not None and previous_view != view:
            st.session_state.forecast_requested = True
        st.session_state.previous_view = view

    with col2:
        # Period selector
        subcol1, subcol2, subcol3, subcol4 = st.columns([1, 3, 1, 1])

        with subcol1:
            if st.button(get_text("header.previous", lang), key="prev_period"):
                _navigate_period(-1, view)

        with subcol2:
            # Display current period
            if view == "day":
                period_label = st.session_state.selected_date.strftime(
                    "%A, %B %d, %Y"
                )
            elif view == "week":
                week_start = st.session_state.selected_date - timedelta(
                    days=st.session_state.selected_date.weekday()
                )
                period_label = f"Week of {week_start.strftime('%B %d, %Y')}"
            else:
                period_label = st.session_state.selected_date.strftime(
                    "%B %Y"
                )

            st.markdown(
                f"""
                <div style="text-align: center; padding: 0.5rem 0;">
                    <span style="font-size: 1.125rem; font-weight: 500; color: #212529;">
                        {period_label}
                    </span>
                </div>
            """,
                unsafe_allow_html=True,
            )

        with subcol3:
            if st.button(get_text("header.next", lang), key="next_period"):
                _navigate_period(1, view)

        with subcol4:
            if st.button(get_text("header.today", lang), key="today_btn"):
                st.session_state.selected_date = datetime.now()
                st.session_state.forecast_requested = True
                st.rerun()

    # Calculate period bounds
    if view == "day":
        period_start = st.session_state.selected_date.replace(
            hour=0, minute=0, second=0
        )
        period_end = period_start + timedelta(days=1)
    elif view == "week":
        period_start = st.session_state.selected_date - timedelta(
            days=st.session_state.selected_date.weekday()
        )
        period_end = period_start + timedelta(days=7)
    else:
        period_start = st.session_state.selected_date.replace(day=1)
        next_month = period_start.replace(day=28) + timedelta(days=4)
        period_end = next_month.replace(day=1)

    return {
        "view": view,
        "selected_date": st.session_state.selected_date,
        "period_start": period_start,
        "period_end": period_end,
    }
