"""Factors Panel Component — Display reasoning and contextual factors."""

import streamlit as st
from typing import Optional

from config import get_text


def render_factors_panel(prediction: Optional[dict], view: str, lang: str = "en") -> None:
    """
    Render factors panel with real prediction reasoning.

    Shows: events, weather, historical baseline, most similar day, confidence factors.
    Uses data from prediction.reasoning and prediction context when available.
    """
    if view != "day":
        with st.expander(get_text("factors.title", lang), expanded=False):
            st.info(get_text("factors.no_data", lang))
        return

    if not prediction:
        with st.expander(get_text("factors.title", lang), expanded=False):
            st.info(get_text("factors.no_data", lang))
        return

    reasoning = prediction.get("reasoning") or {}
    if isinstance(reasoning, str):
        reasoning = {"summary": reasoning}
    patterns = reasoning.get("patterns_used") or []
    confidence_factors = reasoning.get("confidence_factors") or []

    with st.expander(get_text("factors.title", lang), expanded=False):
        col1, col2 = st.columns(2)

        with col1:
            st.markdown(f"**{get_text('factors.events', lang)}**")
            events = (
                prediction.get("events")
                or (reasoning.get("events") if isinstance(reasoning.get("events"), list) else None)
            )
            if events and len(events) > 0:
                for ev in events[:3]:
                    if isinstance(ev, dict):
                        name = ev.get("name", ev.get("event_type", "Event"))
                        impact = ev.get("impact", "")
                        st.markdown(f"- {name}" + (f" ({impact})" if impact else ""))
                    else:
                        st.markdown(f"- {ev}")
            else:
                st.caption(get_text("factors.no_events", lang))

            st.markdown("---")
            st.markdown(f"**{get_text('factors.weather', lang)}**")
            weather = prediction.get("weather") or reasoning.get("weather")
            if weather:
                if isinstance(weather, dict):
                    condition = weather.get("condition", weather.get("description", "—"))
                    temp = weather.get("temperature", weather.get("temp", "—"))
                    st.markdown(f"- {condition}" + (f", {temp}°C" if temp != "—" else ""))
                else:
                    st.write(weather)
            else:
                st.caption(get_text("factors.no_weather", lang))

        with col2:
            st.markdown(f"**{get_text('factors.baseline', lang)}**")
            if patterns:
                valid_covers = [p.get("actual_covers", p.get("covers", 0)) for p in patterns]
                avg = (
                    sum(valid_covers) / len(valid_covers)
                    if valid_covers
                    else 0
                )
                st.markdown(
                    f"- {get_text('factors.avg_similar', lang)}: {int(avg)} covers"
                )
                st.markdown(
                    f"- {get_text('factors.patterns_count', lang)}: {len(patterns)}"
                )
            else:
                accuracy_metrics = prediction.get("accuracy_metrics") or {}
                baseline = accuracy_metrics.get("historical_avg", "—")
                st.caption(
                    f"{get_text('factors.historical_avg', lang)}: {baseline}"
                )

            st.markdown("---")
            st.markdown(f"**{get_text('factors.similar_day', lang)}**")
            if patterns and len(patterns) > 0:
                best = patterns[0]
                date_val = best.get("date", "—")
                covers = best.get("actual_covers", best.get("covers", "—"))
                sim = best.get("similarity", 0)
                sim_pct = int(sim * 100) if isinstance(sim, (int, float)) else "—"
                day_type = best.get("event_type", best.get("metadata", {}).get("day_of_week", ""))
                st.markdown(f"- {date_val}" + (f" ({day_type})" if day_type else ""))
                st.markdown(f"- {covers} covers, {sim_pct}% similar")
            else:
                st.caption(get_text("factors.no_similar", lang))

        if confidence_factors:
            st.markdown("---")
            st.markdown(f"**{get_text('factors.confidence', lang)}**")
            for factor in confidence_factors[:5]:
                if isinstance(factor, str):
                    st.markdown(f"- {factor}")
                else:
                    st.markdown(f"- {factor}")
