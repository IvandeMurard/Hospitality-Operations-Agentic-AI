"""
F&B Operations Agent - Dashboard
Streamlit MVP for prediction visualization
"""

import os
import streamlit as st
import requests
import pandas as pd
from datetime import date, timedelta, datetime
from concurrent.futures import ThreadPoolExecutor
import time
import plotly.graph_objects as go

# Configuration (use API_URL env for local dev, e.g. http://localhost:8000)
API_URL = os.getenv("API_URL", "https://ivandemurard-fb-agent-api.hf.space")

# Initialize session state for prediction persistence
if "prediction_data" not in st.session_state:
    st.session_state.prediction_data = None
if "has_prediction" not in st.session_state:
    st.session_state.has_prediction = False

# Explanatory content (English)
EXPLAINER_CONTENT = {
    "how_it_works": """
### How does this prediction work?

**Data source:**
- 495 historical patterns derived from a hotel dataset (119K reservations, 2015-2017)
- Each pattern captures: day of week, weather, events, holidays, actual covers

**Method:**
1. Your request (date, service) is converted into a numerical "fingerprint" (embedding)
2. Search for the 5 most similar historical patterns (cosine similarity)
3. Weighted average of covers from these patterns = prediction
4. AI generates a natural language explanation

**Current limitations:**
- Derived data (not real hotel data)
- No PMS connection (simulated occupancy)
- Weather and events are simulated
    """,
    
    "reliability_explanation": """
**Estimated Reliability**

Based on MAPE (Mean Absolute Percentage Error) — measures the estimated average gap between prediction and reality.

| Score | Meaning | Recommendation |
|-------|---------|----------------|
| Excellent | < 15% variance | Plan normally |
| Acceptable | 15-25% variance | Consider ±10% buffer |
| Monitor | 25-40% variance | Plan for flexibility |
| Low reliability | > 40% variance | High variance expected |

*Note: Estimated from pattern variance, not backtested on real predictions.*
    """,
    
    "model_diagnostics": """
**Model Diagnostics**

Advanced metrics for technical users:

**Pattern Similarity (Confidence)**
- Measures how well historical patterns match your query context
- High similarity (>90%) = patterns found are very relevant
- Low similarity (<70%) = unusual context, fewer comparable patterns

**Drift Detection**
- If Confidence drops AND MAPE spikes → patterns may be outdated
- Triggers: Confidence < 60% combined with MAPE > 40%
    """
}

# Historical baseline (derived from patterns)
BASELINE_STATS = {
    "weekly_covers_range": (180, 320),
    "breakeven_covers": 35,
    "avg_daily_dinner": 35,
    "avg_daily_lunch": 22,
    "avg_daily_breakfast": 28,
    "patterns_count": 495,
    "data_period": "2015-2017"
}


def get_reliability_score(mape_value):
    """
    Calculate reliability score based on MAPE.
    Returns: (color, emoji, label, advice)
    """
    if mape_value is None:
        return ("gray", "", "Unknown", "Insufficient data for reliability estimate.")
    elif mape_value < 15:
        return ("green", "", "Excellent", "High reliability. Plan staffing normally.")
    elif mape_value < 25:
        return ("yellow", "", "Acceptable", "Good reliability. Consider a ±10% staffing buffer.")
    elif mape_value < 40:
        return ("orange", "", "Monitor", "Moderate variance. Plan for flexibility — have backup staff available.")
    else:
        return ("red", "", "Low reliability", f"High variance expected. Consider a wider staffing range.")

def get_prediction_interval_text(interval, predicted):
    """Format prediction interval for display"""
    if interval:
        low, high = interval
        return f"Expected range: {low} – {high} covers"
    return None

def detect_drift(confidence, mape):
    """
    Detect potential model drift based on combined metrics.
    Returns alert message or None.
    """
    if confidence is None or mape is None:
        return None
    if confidence < 0.60 and mape > 40:
        return "Potential drift detected — patterns may be outdated or context is highly unusual. Manual review recommended."
    elif confidence < 0.70 and mape > 50:
        return "Model uncertainty high — consider manual validation for this prediction."
    return None


def get_factor_breakdown(reasoning: dict, predicted_covers: int) -> list:
    """
    Generate human-readable factor breakdown from reasoning data.
    Returns list of factor dicts with name, impact, icon, description.
    """
    factors = []
    patterns = reasoning.get("similar_patterns", []) or reasoning.get("patterns_used", [])
    context = reasoning.get("context_summary", {})

    # Historical baseline (from patterns)
    if patterns:
        avg_pattern_covers = sum(p.get("actual_covers", 0) for p in patterns) / len(patterns)
        baseline_diff = predicted_covers - avg_pattern_covers
        factors.append({
            "name": "Historical baseline",
            "icon": "📊",
            "value": f"{avg_pattern_covers:.0f} covers",
            "impact": f"{baseline_diff:+.0f}",
            "description": f"Average of {len(patterns)} similar days"
        })

    # Weather (mock for now - will come from real data)
    weather = context.get("weather", {})
    if weather:
        weather_condition = weather.get("condition", "Clear")
        weather_impact = -3 if "rain" in weather_condition.lower() else 0
        if weather_impact != 0:
            factors.append({
                "name": "Weather",
                "icon": "🌧️" if weather_impact < 0 else "☀️",
                "value": weather_condition,
                "impact": f"{weather_impact:+.0f}",
                "description": "Rainy days typically reduce covers by 10%"
            })

    # Events
    events = context.get("events", [])
    if events:
        factors.append({
            "name": "Local events",
            "icon": "🎉",
            "value": events[0] if events else "None",
            "impact": "+2",
            "description": "Events nearby can increase walk-ins"
        })
    else:
        factors.append({
            "name": "Local events",
            "icon": "📅",
            "value": "None detected",
            "impact": "±0",
            "description": "No major events affecting predictions"
        })

    # Day of week pattern
    factors.append({
        "name": "Day pattern",
        "icon": "📆",
        "value": "Typical for this day",
        "impact": "±0",
        "description": "Based on historical patterns for this weekday"
    })

    return factors


def get_similar_day_context(patterns: list) -> dict:
    """
    Get the most similar historical day for human context.
    """
    if not patterns:
        return None

    best = patterns[0]
    day_of_week = best.get("day_of_week") or (best.get("metadata", {}) or {}).get("day_of_week", "")
    return {
        "date": best.get("date", "Unknown"),
        "covers": best.get("actual_covers", 0),
        "similarity": best.get("similarity", 0),
        "day_of_week": day_of_week
    }


def get_contextual_recommendation(predicted: int, range_low: int, range_high: int,
                                   breakeven: int = 35, reliability_label: str = "Monitor") -> str:
    """
    Generate contextual, actionable recommendation (not generic).
    """
    variance = range_high - range_low

    # Below breakeven
    if predicted < breakeven:
        return f"""⚠️ **Below breakeven** ({breakeven} covers)

Expected revenue may not cover costs. Consider:
- Promotional push (social media, hotel guests)
- Minimum staffing configuration
- Evaluate if service should run"""

    # High variance
    if variance > 30:
        return f"""📊 **Wide range expected** ({range_low}-{range_high} covers)

Staffing strategy:
- Schedule for {predicted} covers ({predicted // 20} servers)
- Have 1 server on-call for flex
- Kitchen prep for {range_high} (avoid 86s)"""

    # Good prediction
    if reliability_label == "Excellent":
        return f"""✅ **High confidence prediction**

Plan normally for {predicted} covers:
- {max(2, predicted // 20)} servers
- Standard prep levels
- No special adjustments needed"""

    # Default
    return f"""💡 **Plan for {predicted} covers** (range: {range_low}-{range_high})

Staffing: {max(2, predicted // 20)} servers, {max(1, predicted // 30)} kitchen
Buffer: Consider +1 server on-call if trending up"""


def fetch_prediction(params: dict) -> dict:
    """Fetch a single prediction from API"""
    try:
        response = requests.post(
            f"{API_URL}/predict",
            json=params,
            timeout=30
        )
        response.raise_for_status()
        data = response.json()
        data["_params"] = params  # Keep track of request params
        data["_error"] = None
        return data
    except Exception as e:
        return {
            "_params": params,
            "_error": str(e),
            "predicted_covers": None,
            "confidence": None
        }


def fetch_week_predictions(start_date: date, service_types: list, restaurant_id: str) -> list:
    """Fetch predictions for a week (7 days × service types)"""
    requests_list = []
    
    for day_offset in range(7):
        current_date = start_date + timedelta(days=day_offset)
        for service in service_types:
            requests_list.append({
                "restaurant_id": restaurant_id,
                "service_date": current_date.isoformat(),
                "service_type": service
            })
    
    # Parallel fetch (max 5 concurrent)
    results = []
    with ThreadPoolExecutor(max_workers=5) as executor:
        results = list(executor.map(fetch_prediction, requests_list))
    
    return results


st.set_page_config(
    page_title="F&B Operations Agent",
    page_icon=None,
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .prediction-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 1rem;
        color: white;
        text-align: center;
    }
    .metric-box {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #667eea;
    }
    .confidence-high { color: #28a745; }
    .confidence-medium { color: #ffc107; }
    .confidence-low { color: #dc3545; }
</style>
""", unsafe_allow_html=True)

# Header
st.title("F&B Operations Agent")
st.markdown("*AI-powered demand forecasting for hotel restaurants*")

# How it works (collapsible)
with st.expander("How it works", expanded=False):
    st.markdown(EXPLAINER_CONTENT["how_it_works"])
    
    col_stat1, col_stat2, col_stat3 = st.columns(3)
    with col_stat1:
        st.metric("Historical patterns", BASELINE_STATS["patterns_count"])
    with col_stat2:
        st.metric("Data period", BASELINE_STATS["data_period"])
    with col_stat3:
        st.metric("Avg dinner/day", f"{BASELINE_STATS['avg_daily_dinner']} covers")

st.divider()

# Data timestamp
st.caption(f"📡 Data as of {datetime.now().strftime('%B %d, %Y at %H:%M')} | Patterns: {BASELINE_STATS['patterns_count']} | Period: {BASELINE_STATS['data_period']}")

# Sidebar - Input
with st.sidebar:
    st.header("Prediction Parameters")
    
    # View mode toggle
    view_mode = st.radio(
        "View Mode",
        options=["single", "weekly"],
        format_func=lambda x: "Single Day" if x == "single" else "Weekly Overview",
        horizontal=True
    )
    
    st.divider()
    
    if view_mode == "single":
        service_date = st.date_input(
            "Service Date",
            value=date.today() + timedelta(days=1),
            min_value=date.today(),
            max_value=date.today() + timedelta(days=90)
        )
        
        service_type = st.selectbox(
            "Service Type",
            options=["breakfast", "lunch", "dinner"],
            index=2  # Default: dinner
        )
        service_types = [service_type]
    else:
        # Weekly mode
        week_start = st.date_input(
            "Week Starting",
            value=date.today(),
            min_value=date.today(),
            max_value=date.today() + timedelta(days=90)
        )
        service_date = week_start
        
        service_types = st.multiselect(
            "Service Types",
            options=["breakfast", "lunch", "dinner"],
            default=["dinner"]
        )
        
        if not service_types:
            st.warning("Select at least one service type")
    
    restaurant_id = st.text_input(
        "Restaurant ID",
        value="hotel_main",
        help="Identifier for your restaurant"
    )
    
    button_label = "Get Prediction" if view_mode == "single" else "Get Week Forecast"
    predict_button = st.button(button_label, type="primary", use_container_width=True)

# Main content
if predict_button and view_mode == "single":
    # === SINGLE DAY VIEW: Fetch prediction ===
    with st.spinner("Analyzing patterns..."):
        try:
            response = requests.post(
                f"{API_URL}/predict",
                json={
                    "restaurant_id": restaurant_id,
                    "service_date": service_date.isoformat(),
                    "service_type": service_type
                },
                timeout=30
            )
            if response.status_code == 200:
                data = response.json()
                st.session_state.prediction_data = {
                    "prediction_id": data.get("prediction_id"),
                    "restaurant_id": restaurant_id,
                    "service_date": service_date.isoformat(),
                    "service_type": service_type,
                    "data": data
                }
                st.session_state.has_prediction = True
                st.session_state.last_prediction_params = f"{service_date}_{service_type}_{restaurant_id}"
                # Reset post-service state when new prediction
                st.session_state.post_service_submitted = False
                st.session_state.post_service_result = None
            else:
                st.error(f"Prediction failed: {response.text}")
                st.session_state.has_prediction = False
        except Exception as e:
            st.error(f"Error: {str(e)}")
            st.session_state.has_prediction = False

# Display Single Day results (persists across re-runs for Submit Feedback)
# Clear if params changed (user picked different date/service/restaurant) - only in single mode
if view_mode == "single":
    current_params = f"{service_date}_{service_type}_{restaurant_id}"
    if (st.session_state.get("last_prediction_params") and
        st.session_state.last_prediction_params != current_params):
        st.session_state.has_prediction = False
        st.session_state.prediction_data = None

if view_mode == "single" and st.session_state.has_prediction and st.session_state.prediction_data:
    pred_data = st.session_state.prediction_data
    data = pred_data["data"]
    predicted_covers = data.get("predicted_covers", 0)
    confidence = data.get("confidence", 0)
    reasoning = data.get("reasoning", {})
    staff = data.get("staff_recommendation", {})
    accuracy = data.get("accuracy_metrics", {})
    mape = accuracy.get("estimated_mape")
    interval = accuracy.get("prediction_interval")
    rel_color, rel_emoji, rel_label, rel_advice = get_reliability_score(mape)
    drift_alert = detect_drift(confidence, mape)

    if drift_alert:
        st.warning(drift_alert)

    # Main layout
    col1, col2 = st.columns([2, 1])
    service_date_display = datetime.strptime(pred_data["service_date"], "%Y-%m-%d").date() if isinstance(pred_data.get("service_date"), str) else pred_data.get("service_date", service_date)
    service_type_display = pred_data.get("service_type", service_type)

    with col1:
        st.subheader(f"{service_date_display.strftime('%A, %B %d')} - {service_type_display.capitalize()}")

        # Primary metrics row
        metric_col1, metric_col2 = st.columns(2)

        with metric_col1:
            # Predicted covers with baseline comparison
            baseline = BASELINE_STATS[f"avg_daily_{service_type_display}"]
            delta = predicted_covers - baseline
            st.metric(
                label="Predicted Covers",
                value=f"{predicted_covers}",
                delta=f"{delta:+.0f} vs baseline ({baseline})",
                help=f"Historical baseline for {service_type_display}: {baseline} covers/day"
            )

            # Prediction interval (primary actionable info)
            if interval:
                st.info(f"**Expected range: {interval[0]} – {interval[1]} covers**")

        with metric_col2:
            # Reliability score (single metric replacing Confidence + MAPE)
            st.markdown(f"**Estimated Reliability**")
            st.markdown(f"### {rel_emoji} {rel_label}")
            if mape:
                st.caption(f"±{mape:.0f}% variance")

    with col2:
        # Reliability gauge (based on MAPE, inverted so higher = better)
        reliability_value = max(0, 100 - (mape if mape else 50))
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=reliability_value,
            number={'suffix': '%'},
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Reliability"},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': "#667eea"},
                'steps': [
                    {'range': [0, 60], 'color': "#ffcccc"},
                    {'range': [60, 75], 'color': "#fff3cd"},
                    {'range': [75, 85], 'color': "#d4f5d4"},
                    {'range': [85, 100], 'color': "#28a745"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 2},
                    'thickness': 0.75,
                    'value': 75
                }
            }
        ))
        fig.update_layout(height=250, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig, use_container_width=True)

    # Factor breakdown (Why this prediction?)
    st.divider()
    with st.expander("💭 Why this prediction?", expanded=True):
        factors = get_factor_breakdown(reasoning, predicted_covers)
        for factor in factors:
            col_icon, col_name, col_impact = st.columns([0.5, 3, 1])
            with col_icon:
                st.write(factor["icon"])
            with col_name:
                st.write(f"**{factor['name']}**: {factor['value']}")
                st.caption(factor["description"])
            with col_impact:
                st.write(f"**{factor['impact']}**")

        patterns = reasoning.get("similar_patterns", []) or reasoning.get("patterns_used", [])
        similar_day = get_similar_day_context(patterns)
        if similar_day:
            st.info(f"📆 **Most similar past day:** {similar_day['date']} — {similar_day['covers']} covers ({similar_day['similarity']:.0%} match)")

    # Contextual recommendation
    breakeven = BASELINE_STATS.get("breakeven_covers", 35)
    contextual_reco = get_contextual_recommendation(
        predicted_covers,
        interval[0] if interval else predicted_covers - 10,
        interval[1] if interval else predicted_covers + 10,
        breakeven,
        rel_label
    )
    st.markdown(contextual_reco)

    st.divider()

    # Pre-service validation question
    st.subheader("❓ Does this look right?")
    validation = st.radio(
        "Your assessment:",
        options=["accurate", "higher", "lower"],
        format_func=lambda x: {
            "accurate": f"✓ Yes, {predicted_covers} covers looks accurate",
            "higher": "↑ I expect it to be higher",
            "lower": "↓ I expect it to be lower"
        }[x],
        horizontal=True,
        key="pre_validation"
    )

    selected_reasons = []
    adjusted = None
    if validation in ["higher", "lower"]:
        reason_options = [
            "High booking pace today",
            "Special event/promotion",
            "Weather change expected",
            "Group reservation",
            "Holiday period",
            "Other"
        ]
        selected_reasons = st.multiselect(
            "What makes you think so?",
            options=reason_options,
            key="pre_reasons"
        )
        adjusted = st.number_input(
            "Your estimate:",
            min_value=0,
            max_value=300,
            value=predicted_covers + (10 if validation == "higher" else -10),
            key="adjusted_covers"
        )

    if st.button("Submit Feedback", key="pre_feedback_btn"):
        feedback_payload = {
            "prediction_id": pred_data["prediction_id"],
            "restaurant_id": pred_data["restaurant_id"],
            "feedback_type": "pre_service",
            "pre_validation": validation,
            "pre_reasons": selected_reasons,
            "pre_adjusted_covers": adjusted if validation in ["higher", "lower"] else None
        }
        try:
            feedback_response = requests.post(f"{API_URL}/api/feedback", json=feedback_payload, timeout=10)
            if feedback_response.status_code == 200:
                st.success("✓ Thanks! Your feedback helps improve predictions.")
            else:
                err_text = feedback_response.text
                try:
                    err_detail = feedback_response.json().get("detail", err_text)
                except Exception:
                    err_detail = err_text
                if "Prediction was not stored" in str(err_detail) or "Supabase" in str(err_detail):
                    st.error("La prédiction n'a pas été sauvegardée. Vérifiez que SUPABASE_URL et SUPABASE_KEY sont configurés dans le Space Hugging Face. Relancez une prédiction après configuration.")
                else:
                    st.error(f"Failed to submit feedback: {err_detail}")
        except Exception as e:
            st.error(f"Failed to submit feedback: {str(e)}")

    st.divider()

    # ============================================
    # POST-SERVICE FEEDBACK SECTION
    # ============================================

    if not st.session_state.post_service_submitted:
        st.markdown("### ✅ Post-Service: How did it go?")
        st.caption("Enter actual results after the service to track accuracy. Your feedback feeds a continuous learning loop: the agent compares predictions with actual results to improve over time. Longer-term, a semantic layer will automate this so the system keeps improving with minimal manager input.")

        range_low = interval[0] if interval else predicted_covers - 10
        range_high = interval[1] if interval else predicted_covers + 10

        col_recap, col_input = st.columns([1, 1])
        with col_recap:
            st.markdown("**📊 Prediction Recap**")
            st.markdown(f"- Date: **{service_date_display.strftime('%A, %B %d')}** | Service: **{service_type_display.capitalize()}**")
            st.markdown(f"- Predicted: **{predicted_covers}** covers")
            st.markdown(f"- Expected range: {range_low} – {range_high}")

        with col_input:
            st.markdown("**❓ Actual Results**")
            actual_covers = st.number_input(
                "Actual covers",
                min_value=0,
                max_value=500,
                value=0,
                key="actual_covers_input",
                help="How many covers did you actually serve?"
            )

        st.markdown("**👥 Staff Used** (optional)")
        col_foh, col_boh = st.columns(2)
        with col_foh:
            staff_foh = st.number_input(
                "FOH (servers, hosts)",
                min_value=0,
                max_value=50,
                value=0,
                key="staff_foh_input"
            )
        with col_boh:
            staff_boh = st.number_input(
                "BOH (kitchen)",
                min_value=0,
                max_value=50,
                value=0,
                key="staff_boh_input"
            )

        notes = st.text_area(
            "💬 Notes (optional)",
            placeholder="Any context? Special events, weather issues, no-shows...",
            key="post_service_notes",
            height=80
        )

        if st.button("Submit Post-Service Feedback", key="submit_post_service_btn", type="primary"):
            if actual_covers == 0:
                st.warning("Please enter the actual number of covers")
            else:
                post_feedback_payload = {
                    "prediction_id": pred_data["prediction_id"],
                    "restaurant_id": pred_data["restaurant_id"],
                    "feedback_type": "post_service",
                    "actual_covers": actual_covers,
                    "staff_foh_used": staff_foh if staff_foh > 0 else None,
                    "staff_boh_used": staff_boh if staff_boh > 0 else None,
                    "notes": notes.strip() or None
                }
                try:
                    response = requests.post(
                        f"{API_URL}/api/feedback",
                        json=post_feedback_payload,
                        timeout=10
                    )
                    if response.status_code == 200:
                        error = abs(predicted_covers - actual_covers)
                        accuracy_pct = round((1 - error / actual_covers) * 100, 1) if actual_covers > 0 else 0
                        within_range = range_low <= actual_covers <= range_high
                        st.session_state.post_service_submitted = True
                        st.session_state.post_service_result = {
                            "predicted": predicted_covers,
                            "actual": actual_covers,
                            "accuracy_pct": accuracy_pct,
                            "within_range": within_range
                        }
                        st.rerun()
                    else:
                        st.error(f"Failed to submit: {response.text}")
                except Exception as e:
                    st.error(f"Error: {e}")

    if st.session_state.post_service_submitted and st.session_state.post_service_result:
        result = st.session_state.post_service_result
        st.success("✅ **Thanks! Here's how the prediction performed:**")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Predicted", f"{result['predicted']} covers")
        with col2:
            st.metric("Actual", f"{result['actual']} covers")
        with col3:
            range_icon = "✅" if result["within_range"] else "⚠️"
            st.metric("Accuracy", f"{result['accuracy_pct']}% {range_icon}")
        if result["within_range"]:
            st.info("📊 Within expected range — prediction was reliable!")
        else:
            st.warning("📊 Outside expected range — I'll learn from this difference.")
        st.caption("This feedback helps me improve future predictions!")

    st.divider()

    # Staff Recommendation
    st.subheader("Staff Recommendation")

    if staff and staff.get("recommended_staff"):
        rec_staff = staff.get("recommended_staff", {})
        staff_cols = st.columns(4)
        with staff_cols[0]:
            st.metric("Servers", rec_staff.get("servers", 0))
        with staff_cols[1]:
            st.metric("Hosts", rec_staff.get("hosts", 0))
        with staff_cols[2]:
            st.metric("Bussers", rec_staff.get("bussers", 0))
        with staff_cols[3]:
            st.metric("Kitchen", rec_staff.get("kitchen", 0))
        if staff.get("recommendation"):
            st.caption(f"{staff.get('recommendation')}")
    elif staff:
        servers_data = staff.get("servers", {})
        hosts_data = staff.get("hosts", {})
        kitchen_data = staff.get("kitchen", {})
        staff_cols = st.columns(4)
        with staff_cols[0]:
            rec_servers = servers_data.get("recommended", 0) if isinstance(servers_data, dict) else 0
            st.metric("Servers", rec_servers)
        with staff_cols[1]:
            rec_hosts = hosts_data.get("recommended", 0) if isinstance(hosts_data, dict) else 0
            st.metric("Hosts", rec_hosts)
        with staff_cols[2]:
            st.metric("Bussers", 0)
        with staff_cols[3]:
            rec_kitchen = kitchen_data.get("recommended", 0) if isinstance(kitchen_data, dict) else 0
            st.metric("Kitchen", rec_kitchen)
        if staff.get("rationale"):
            st.caption(f"{staff.get('rationale')}")

    # Expandable sections
    with st.expander("Understand this prediction", expanded=False):
        st.markdown(EXPLAINER_CONTENT["reliability_explanation"])

    with st.expander("🔧 Model Diagnostics", expanded=False):
        st.markdown(EXPLAINER_CONTENT["model_diagnostics"])
        diag_col1, diag_col2, diag_col3 = st.columns(3)
        with diag_col1:
            st.metric("MAPE (estimated)", f"{mape:.1f}%" if mape else "N/A")
        with diag_col2:
            st.metric("Pattern Similarity", f"{confidence:.0%}" if confidence else "N/A")
        with diag_col3:
            st.metric("Patterns Analyzed", accuracy.get("patterns_analyzed", "N/A"))
        if drift_alert:
            st.error(drift_alert)
        else:
            st.success("✅ No drift detected — model operating normally")

    with st.expander("AI Reasoning", expanded=False):
        explanation = reasoning.get("explanation", "") or reasoning.get("summary", "No explanation available")
        st.markdown(f"**Analysis:** {explanation}")
        patterns = reasoning.get("similar_patterns", []) or reasoning.get("patterns_used", [])
        if patterns:
            st.markdown("**Similar Historical Patterns:**")
            for i, pattern in enumerate(patterns[:3], 1):
                if isinstance(pattern, dict):
                    p_date = pattern.get("date", "Unknown")
                    p_covers = pattern.get("actual_covers", "?")
                    p_sim = pattern.get("similarity", 0)
                    st.markdown(f"{i}. {p_date} — {p_covers} covers (similarity: {p_sim:.0%})")

elif predict_button and view_mode != "single":
        # === WEEKLY VIEW ===
        if not service_types:
            st.error("Please select at least one service type")
        else:
            with st.spinner(f"Fetching predictions for 7 days × {len(service_types)} services..."):
                results = fetch_week_predictions(service_date, service_types, restaurant_id)
            
            # Process results into DataFrame
            rows = []
            for r in results:
                params = r.get("_params", {})
                mape = r.get("accuracy_metrics", {}).get("estimated_mape") if r.get("accuracy_metrics") else None
                conf = r.get("confidence")
                
                # Get reliability
                rel_color, rel_emoji, rel_label, _ = get_reliability_score(mape)
                
                rows.append({
                    "Date": params.get("service_date"),
                    "Day": pd.to_datetime(params.get("service_date")).strftime("%a") if params.get("service_date") else "",
                    "Service": params.get("service_type", "").capitalize(),
                    "Covers": r.get("predicted_covers"),
                    "Reliability": f"{rel_emoji} {rel_label}" if mape else "N/A",
                    "Range": f"{r.get('accuracy_metrics', {}).get('prediction_interval', ['-', '-'])[0]}-{r.get('accuracy_metrics', {}).get('prediction_interval', ['-', '-'])[1]}" if r.get("accuracy_metrics", {}).get("prediction_interval") else "N/A",
                    "MAPE": mape,
                    "Confidence": conf,
                    "Error": r.get("_error")
                })
            
            df = pd.DataFrame(rows)
            
            # Header
            st.subheader(f"Week of {service_date.strftime('%B %d, %Y')}")
            
            valid_data = df[df["Covers"].notna()]
            
            if not valid_data.empty:
                total_covers = valid_data['Covers'].sum()
                baseline_low, baseline_high = BASELINE_STATS["weekly_covers_range"]
                
                # Context banner
                if total_covers < baseline_low:
                    st.info(f"Quiet week expected ({total_covers:.0f} covers vs baseline {baseline_low}-{baseline_high})")
                elif total_covers > baseline_high:
                    st.success(f"Busy week expected ({total_covers:.0f} covers vs baseline {baseline_low}-{baseline_high})")
                else:
                    st.info(f"Standard week ({total_covers:.0f} covers, baseline {baseline_low}-{baseline_high})")
                
                # Check for any drift alerts
                drift_days = []
                for _, row in valid_data.iterrows():
                    drift = detect_drift(row.get("Confidence"), row.get("MAPE"))
                    if drift:
                        drift_days.append(f"{row['Day']} {row['Service']}")
                
                if drift_days:
                    st.warning(f"Model uncertainty detected for: {', '.join(drift_days)}. Review these predictions manually.")
                
                # Summary metrics
                summary_cols = st.columns(4)
                
                with summary_cols[0]:
                    delta_vs_baseline = total_covers - ((baseline_low + baseline_high) / 2)
                    st.metric(
                        "Total Covers", 
                        f"{total_covers:.0f}",
                        delta=f"{delta_vs_baseline:+.0f} vs avg.",
                        help=f"Weekly baseline: {baseline_low}-{baseline_high} covers"
                    )
                with summary_cols[1]:
                    st.metric("Avg per Service", f"{valid_data['Covers'].mean():.0f}")
                with summary_cols[2]:
                    st.metric("Peak", f"{valid_data['Covers'].max():.0f}")
                with summary_cols[3]:
                    # Average reliability (inverse of MAPE)
                    avg_mape = valid_data['MAPE'].mean() if 'MAPE' in valid_data else None
                    if avg_mape:
                        avg_reliability = max(0, 100 - avg_mape)
                        st.metric("Avg Reliability", f"{avg_reliability:.0f}%")
                    else:
                        st.metric("Avg Reliability", "N/A")
                
                st.divider()
                
                # Chart
                st.subheader("Weekly Demand Overview")
                
                if len(service_types) > 1:
                    # Heatmap for multiple services
                    pivot_df = valid_data.pivot(index="Service", columns="Day", values="Covers")
                    day_order = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
                    pivot_df = pivot_df.reindex(columns=[d for d in day_order if d in pivot_df.columns])
                    
                    fig = go.Figure(data=go.Heatmap(
                        z=pivot_df.values,
                        x=pivot_df.columns,
                        y=pivot_df.index,
                        colorscale="Blues",
                        text=pivot_df.values,
                        texttemplate="%{text:.0f}",
                        textfont={"size": 14},
                        hovertemplate="Day: %{x}<br>Service: %{y}<br>Covers: %{z}<extra></extra>"
                    ))
                    fig.update_layout(
                        height=200 + (len(service_types) * 50),
                        margin=dict(l=20, r=20, t=20, b=20)
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    # Bar chart for single service
                    fig = go.Figure(data=go.Bar(
                        x=valid_data["Day"],
                        y=valid_data["Covers"],
                        marker_color="#667eea",
                        text=valid_data["Covers"],
                        textposition="outside"
                    ))
                    fig.update_layout(
                        height=300,
                        xaxis_title="Day",
                        yaxis_title="Predicted Covers",
                        margin=dict(l=20, r=20, t=20, b=20)
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                st.divider()
                
                # Detailed table
                st.subheader("Detailed Predictions")
                
                # Prepare display dataframe with better column names
                display_df = valid_data[["Date", "Day", "Service", "Covers", "Range", "Reliability"]].copy()
                display_df = display_df.rename(columns={"Range": "Expected Range"})
                display_df["Covers"] = display_df["Covers"].apply(lambda x: f"{x:.0f}" if pd.notna(x) else "Error")
                
                st.dataframe(
                    display_df,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "Date": st.column_config.TextColumn("Date", help="Service date"),
                        "Day": st.column_config.TextColumn("Day", help="Day of week"),
                        "Service": st.column_config.TextColumn("Service", help="Meal service type"),
                        "Covers": st.column_config.NumberColumn("Covers", help="Predicted number of customers"),
                        "Expected Range": st.column_config.TextColumn("Expected Range", help="Min-max covers based on similar historical patterns"),
                        "Reliability": st.column_config.TextColumn("Reliability", help="Prediction reliability based on MAPE: 🟢 <15% | 🟡 15-25% | 🟠 25-40% | 🔴 >40%")
                    }
                )
                
                # Legend
                st.caption("**Reliability:** Excellent (<15%) | Acceptable (15-25%) | Monitor (25-40%) | Low (>40%)")
                
                # Model diagnostics
                with st.expander("Understand predictions", expanded=False):
                    st.markdown(EXPLAINER_CONTENT["reliability_explanation"])
                
                with st.expander("🔧 Model Diagnostics", expanded=False):
                    st.markdown(EXPLAINER_CONTENT["model_diagnostics"])
                    
                    # Show technical metrics table
                    tech_df = valid_data[["Date", "Day", "Service", "MAPE", "Confidence"]].copy()
                    tech_df["MAPE"] = tech_df["MAPE"].apply(lambda x: f"{x:.1f}%" if pd.notna(x) else "N/A")
                    tech_df["Confidence"] = tech_df["Confidence"].apply(lambda x: f"{x:.0%}" if pd.notna(x) else "N/A")
                    st.dataframe(tech_df, use_container_width=True, hide_index=True)
                
                # Errors
                errors = df[df["Error"].notna()]
                if not errors.empty:
                    with st.expander(f"{len(errors)} Failed Requests", expanded=False):
                        st.dataframe(errors[["Date", "Service", "Error"]], hide_index=True)
            else:
                st.error("All predictions failed. Check API connectivity.")

else:
    # Default state
    st.info("Configure parameters and click **Get Prediction** to see results")
    
    # Demo section
    col_demo1, col_demo2 = st.columns(2)
    
    with col_demo1:
        st.markdown("""
        ### What does this tool do?
        
        Predicts the number of **covers** (customers) for a hotel restaurant service.
        
        **How to use:**
        1. Select a date and service type
        2. Get a prediction with reliability score
        3. Review staffing recommendation
        4. Understand the "why" via AI explanation
        """)
    
    with col_demo2:
        st.markdown("""
        ### Based on what?
        
        | Data | Source |
        |------|--------|
        | Historical patterns | 495 patterns (dataset 2015-2017) |
        | Similarity | Qdrant vector search |
        | Reasoning | Claude AI (Anthropic) |
        | Embeddings | Mistral AI |
        """)
    
    st.divider()
    
    # Quick stats
    st.markdown("### Reference Statistics")
    
    ref_cols = st.columns(4)
    with ref_cols[0]:
        st.metric("Available Patterns", "495")
    with ref_cols[1]:
        st.metric("Avg dinner/day", "35 covers")
    with ref_cols[2]:
        st.metric("Avg lunch/day", "22 covers")
    with ref_cols[3]:
        st.metric("Avg breakfast/day", "28 covers")
    
    st.divider()
    
    # Links
    st.markdown("""
    **Useful links:**
    [API Documentation](https://ivandemurard-fb-agent-api.hf.space/docs) | 
    [GitHub Repository](https://github.com/ivandemurard/fb-agent) |
    [Portfolio](https://ivandemurard.com)
    """)

# Footer
st.divider()
st.caption("Built by Ivan de Murard | F&B Operations Agent v0.3")
