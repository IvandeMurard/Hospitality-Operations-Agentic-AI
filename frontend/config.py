"""Aetherix Design System Configuration"""

import os
from pathlib import Path

# API
API_BASE = os.environ.get("AETHERIX_API_BASE", "http://localhost:8000")

# Brand
BRAND_NAME = "Aetherix"
BRAND_TAGLINE = "Intelligence layer for hotel F&B operations"

# Colors
COLORS = {
    # Primary (Green)
    "primary_900": "#081C15",
    "primary_800": "#1B4332",  # Sidebar background
    "primary_700": "#2D6A4F",  # Buttons, accents
    "primary_600": "#40916C",  # Hover, success
    "primary_100": "#D8F3DC",  # Light backgrounds
    # Neutral
    "white": "#FFFFFF",
    "gray_50": "#F8F9FA",  # Page background
    "gray_100": "#E9ECEF",  # Card borders
    "gray_200": "#DEE2E6",  # Dividers
    "gray_400": "#ADB5BD",  # Disabled
    "gray_500": "#6C757D",  # Secondary text
    "gray_700": "#495057",  # Body text
    "gray_900": "#212529",  # Headings
    # Semantic
    "success": "#40916C",
    "warning": "#E9C46A",
    "error": "#E76F51",
    "info": "#457B9D",
}

# Custom CSS
AETHERIX_CSS = """
<style>
    /* Import Inter font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    /* Global */
    .stApp {
        background-color: #F8F9FA;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #1B4332;
        padding-top: 2rem;
    }
    
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] span,
    [data-testid="stSidebar"] label {
        color: white !important;
    }
    
    [data-testid="stSidebar"] .stSelectbox label {
        color: rgba(255,255,255,0.7) !important;
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    /* Sidebar dividers */
    [data-testid="stSidebar"] hr {
        border-color: rgba(255,255,255,0.2);
        margin: 1.5rem 0;
    }
    
    /* Cards */
    div[data-testid="stMetric"] {
        background-color: white;
        padding: 1rem 1.25rem;
        border-radius: 8px;
        border: 1px solid #E9ECEF;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
    }
    
    div[data-testid="stMetric"] label {
        color: #6C757D !important;
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    div[data-testid="stMetric"] [data-testid="stMetricValue"] {
        color: #212529;
        font-size: 2rem;
        font-weight: 600;
    }
    
    /* Buttons */
    .stButton > button {
        background-color: #2D6A4F;
        color: white;
        border: none;
        border-radius: 6px;
        padding: 0.5rem 1rem;
        font-weight: 500;
    }
    
    .stButton > button:hover {
        background-color: #1B4332;
        border: none;
    }
    
    /* Radio buttons (for toggle) */
    div[data-testid="stRadio"] > div {
        flex-direction: row;
        gap: 0;
    }
    
    div[data-testid="stRadio"] > div > label {
        background-color: white;
        border: 1px solid #DEE2E6;
        padding: 0.5rem 1rem;
        margin: 0;
        cursor: pointer;
    }
    
    div[data-testid="stRadio"] > div > label:first-child {
        border-radius: 6px 0 0 6px;
    }
    
    div[data-testid="stRadio"] > div > label:last-child {
        border-radius: 0 6px 6px 0;
    }
    
    div[data-testid="stRadio"] > div > label[data-checked="true"] {
        background-color: #2D6A4F;
        color: white;
        border-color: #2D6A4F;
    }
    
    /* Section headers */
    .section-header {
        color: rgba(255,255,255,0.5);
        font-size: 0.7rem;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        margin-bottom: 0.75rem;
    }
    
    /* Coming soon items */
    .coming-soon {
        color: rgba(255,255,255,0.4) !important;
        font-style: italic;
    }
</style>
"""


def get_text(key: str, lang: str = "en") -> str:
    """Get translated text by key"""
    import json

    locale_file = Path(__file__).parent / "locales" / f"{lang}.json"
    if locale_file.exists():
        with open(locale_file, "r", encoding="utf-8") as f:
            translations = json.load(f)
            keys = key.split(".")
            value = translations
            for k in keys:
                value = value.get(k, key)
            return value if isinstance(value, str) else key
    return key
