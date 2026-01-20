"""
F&B Operations Agent - Dashboard
Streamlit MVP for prediction visualization
"""

import streamlit as st
import requests
import pandas as pd
from datetime import date, timedelta
from concurrent.futures import ThreadPoolExecutor
import time
import plotly.graph_objects as go

# Configuration
API_URL = "https://ivandemurard-fb-agent-api.hf.space"


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
    page_icon="🍽️",
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
st.title("🍽️ F&B Operations Agent")
st.markdown("*AI-powered demand forecasting for hotel restaurants*")

st.divider()

# Sidebar - Input
with st.sidebar:
    st.header("📅 Prediction Parameters")
    
    # View mode toggle
    view_mode = st.radio(
        "View Mode",
        options=["single", "weekly"],
        format_func=lambda x: "📍 Single Day" if x == "single" else "📆 Weekly Overview",
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
    
    button_label = "🔮 Get Prediction" if view_mode == "single" else "📆 Get Week Forecast"
    predict_button = st.button(button_label, type="primary", use_container_width=True)

# Main content
if predict_button:
    if view_mode == "single":
        # === SINGLE DAY VIEW (existing logic) ===
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
                response.raise_for_status()
                data = response.json()
                
                predicted_covers = data.get("predicted_covers", 0)
                confidence = data.get("confidence", 0)
                reasoning = data.get("reasoning", {})
                staff = data.get("staff_recommendation", {})
                accuracy = data.get("accuracy_metrics", {})
                
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.subheader(f"📊 {service_date.strftime('%A, %B %d')} - {service_type.capitalize()}")
                    
                    metric_col1, metric_col2, metric_col3 = st.columns(3)
                    
                    with metric_col1:
                        st.metric(label="Predicted Covers", value=f"{predicted_covers}")
                    
                    with metric_col2:
                        st.metric(label="Confidence", value=f"{confidence:.0%}")
                    
                    with metric_col3:
                        mape = accuracy.get("estimated_mape")
                        st.metric(
                            label="Est. MAPE",
                            value=f"{mape:.1f}%" if mape else "N/A",
                            help="Estimated from pattern variance"
                        )
                    
                    interval = accuracy.get("prediction_interval")
                    if interval:
                        st.caption(f"📈 Prediction interval: {interval[0]} - {interval[1]} covers")
                    
                    st.divider()
                    
                    st.subheader("👥 Staff Recommendation")
                    
                    if staff:
                        servers_data = staff.get("servers", {})
                        hosts_data = staff.get("hosts", {})
                        kitchen_data = staff.get("kitchen", {})
                        
                        staff_cols = st.columns(4)
                        
                        with staff_cols[0]:
                            rec_servers = servers_data.get("recommended", 0)
                            st.metric("Servers", rec_servers)
                        with staff_cols[1]:
                            rec_hosts = hosts_data.get("recommended", 0)
                            st.metric("Hosts", rec_hosts)
                        with staff_cols[2]:
                            rec_bussers = 0  # Not in current structure
                            st.metric("Bussers", rec_bussers)
                        with staff_cols[3]:
                            rec_kitchen = kitchen_data.get("recommended", 0)
                            st.metric("Kitchen", rec_kitchen)
                        
                        rationale = staff.get("rationale", "")
                        if rationale:
                            st.caption(f"💡 {rationale}")
                        
                        covers_per_staff = staff.get("covers_per_staff", 0)
                        if covers_per_staff > 0:
                            st.caption(f"📈 Covers per staff: {covers_per_staff:.1f}")
                    else:
                        st.info("No staff recommendation available")
                
                with col2:
                    fig = go.Figure(go.Indicator(
                        mode="gauge+number",
                        value=confidence * 100,
                        domain={'x': [0, 1], 'y': [0, 1]},
                        title={'text': "Confidence"},
                        gauge={
                            'axis': {'range': [0, 100]},
                            'bar': {'color': "#667eea"},
                            'steps': [
                                {'range': [0, 70], 'color': "#ffcccc"},
                                {'range': [70, 85], 'color': "#fff3cd"},
                                {'range': [85, 100], 'color': "#d4edda"}
                            ]
                        }
                    ))
                    fig.update_layout(height=250, margin=dict(l=20, r=20, t=40, b=20))
                    st.plotly_chart(fig, use_container_width=True)
                
                with st.expander("🧠 View AI Reasoning", expanded=False):
                    explanation = reasoning.get("explanation") or reasoning.get("summary", "No explanation available")
                    st.markdown(f"**Analysis:** {explanation}")
                
                with st.expander("🔧 Raw API Response", expanded=False):
                    st.json(data)
                    
            except requests.exceptions.RequestException as e:
                st.error(f"❌ API Error: {str(e)}")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
    
    else:
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
                rows.append({
                    "Date": params.get("service_date"),
                    "Day": pd.to_datetime(params.get("service_date")).strftime("%a") if params.get("service_date") else "",
                    "Service": params.get("service_type", "").capitalize(),
                    "Covers": r.get("predicted_covers"),
                    "Confidence": r.get("confidence"),
                    "MAPE": r.get("accuracy_metrics", {}).get("estimated_mape") if r.get("accuracy_metrics") else None,
                    "Error": r.get("_error")
                })
            
            df = pd.DataFrame(rows)
            
            # Summary metrics
            st.subheader(f"📆 Week of {service_date.strftime('%B %d, %Y')}")
            
            valid_data = df[df["Covers"].notna()]
            
            if not valid_data.empty:
                summary_cols = st.columns(4)
                
                with summary_cols[0]:
                    st.metric("Total Covers", f"{valid_data['Covers'].sum():.0f}")
                with summary_cols[1]:
                    st.metric("Avg per Service", f"{valid_data['Covers'].mean():.0f}")
                with summary_cols[2]:
                    st.metric("Peak", f"{valid_data['Covers'].max():.0f}")
                with summary_cols[3]:
                    avg_conf = valid_data['Confidence'].mean()
                    st.metric("Avg Confidence", f"{avg_conf:.0%}" if avg_conf else "N/A")
                
                st.divider()
                
                # Heatmap / Chart
                st.subheader("📊 Weekly Demand Heatmap")
                
                # Pivot for heatmap
                if len(service_types) > 1:
                    pivot_df = valid_data.pivot(index="Service", columns="Day", values="Covers")
                    # Reorder days
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
                
                # Detail table
                st.subheader("📋 Detailed Predictions")
                
                display_df = valid_data[["Date", "Day", "Service", "Covers", "Confidence", "MAPE"]].copy()
                display_df["Confidence"] = display_df["Confidence"].apply(lambda x: f"{x:.0%}" if pd.notna(x) else "N/A")
                display_df["MAPE"] = display_df["MAPE"].apply(lambda x: f"{x:.1f}%" if pd.notna(x) else "N/A")
                display_df["Covers"] = display_df["Covers"].apply(lambda x: f"{x:.0f}" if pd.notna(x) else "Error")
                
                st.dataframe(
                    display_df,
                    use_container_width=True,
                    hide_index=True
                )
                
                # Errors
                errors = df[df["Error"].notna()]
                if not errors.empty:
                    with st.expander(f"⚠️ {len(errors)} Failed Requests", expanded=False):
                        st.dataframe(errors[["Date", "Service", "Error"]], hide_index=True)
            else:
                st.error("All predictions failed. Check API connectivity.")

else:
    # Default state
    st.info("👈 Configure parameters and click **Get Prediction** to see results")
    
    # Demo card
    st.markdown("""
    ### How it works
    
    1. **Select a date** — Choose the service date you want to predict
    2. **Choose service type** — Lunch, dinner, or brunch
    3. **Get prediction** — Our AI analyzes similar historical patterns
    4. **Review reasoning** — Understand WHY the prediction was made
    
    ---
    
    ### About
    
    This dashboard uses **RAG (Retrieval-Augmented Generation)** to find similar historical patterns 
    and predict demand. The system considers:
    
    - 📅 Day of week & seasonality
    - 🎉 Local events
    - 🌤️ Weather conditions
    - 🏨 Hotel occupancy patterns
    
    [View API Documentation](https://ivandemurard-fb-agent-api.hf.space/docs) | 
    [GitHub Repository](https://github.com/ivandemurard/fb-agent)
    """)

# Footer
st.divider()
st.caption("Built with ❤️ by Ivan de Murard | F&B Operations Agent v0.2")
