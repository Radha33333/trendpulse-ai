import io
import json
import urllib.parse
import xml.etree.ElementTree as ET
from groq import Groq
import pandas as pd
import plotly.express as px
import requests
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer
import streamlit as st

# Page Config
st.set_page_config(
    page_title="TrendPulse AI - Commercial Signal Intelligence",
    page_icon="⚡",
    layout="wide",
)

GROQ_API_KEY = st.secrets.get("GROQ_API_KEY", "")
STRIPE_CHECKOUT_URL = "https://buy.stripe.com/test_demo"

TEXTS = {
    "English": {
        "title": "⚡ TrendPulse AI: Commercial Signal Intelligence",
        "subtitle": (
            "Predictive Trend Intelligence | Automated Creator & Merchant"
            " Signal Engine"
        ),
        "terminal": "🔑 Enterprise Access Terminal",
        "simulate_pro": "Simulate Pro Subscription Access",
        "config_title": "🎛️ Signal Intelligence Configuration",
        "region": "🌍 Target Region:",
        "platform": "📱 Platform Source:",
        "category": "📁 Niche Category:",
        "velocity": "⏱️ Signal Velocity:",
        "apply_btn": "🚀 Apply Configuration & Update Radar",
        "telemetry_title": "📊 Live Telemetry & Growth Forecast",
        "custom_search": "🔍 Custom Asset Search (Optional):",
        "active_signals_for": "Active Signals for:",
        "filtered_asset": "Trending Signal",
        "search_volume": "Search Volume",
        "future_forecast": "Future Trend Forecast",
        "chart_title": "📈 Dynamic Velocity & Demand Forecast Curve",
        "matrix_title": "💡 Actionable Intelligence & Strategy Matrix",
        "locked_title": "🔒 MULTI-CHANNEL BLUEPRINT IS LOCKED",
        "locked_info": (
            "Unlock high-converting scripts, viral hooks, ad copy, and"
            " step-by-step execution plan."
        ),
        "upgrade_btn": "🔥 Upgrade to Pro & Unlock Full Engine",
        "analyzing_custom": "Analyzing Signal Potential for:",
        "select_asset": "🎯 Select Filtered Asset:",
        "operating_role": "👤 Operating Role:",
        "gen_blueprint": "⚡ Generate Master Strategy Blueprint",
        "monetization": "💰 Direct High-ROI Monetization Model",
        "hook": "🎬 Visual Script & High-Retention Hook (Plug & Play)",
        "audio": "🎵 Recommended High-Converting Audio Vibe",
        "caption": "📢 High-ROAS Caption & CTA Framework",
        "plan": "📝 3-Step Rapid Execution Roadmap (Zero to Launch)",
        "score_label": "Predictive Viral Score",
        "export_pdf_btn": "📄 Download Blueprint PDF",
        "share_wa_btn": "💬 Share to WhatsApp",
        "competitor_insight": "🕵️ Live Competitor Ad Intelligence",
    },
    "Hindi": {
        "title": "⚡ TrendPulse AI: कमर्शियल सिग्नल इंटेलिजेंस",
        "subtitle": (
            "प्रेडिक्टिव ट्रेंड इंटेलिजेंस | ऑटोमेटेड क्रिएटर और मर्चेंट"
            " सिग्नल इंजन"
        ),
        "terminal": "🔑 एंटरप्राइज एक्सेस टर्मिनल",
        "simulate_pro": "प्रो सब्सक्रिप्शन एक्सेस सिमुलेट करें",
        "config_title": "🎛️ सिग्नल इंटेलिजेंस कॉन्फ़िगरेशन",
        "region": "🌍 टारगेट रीजन (क्षेत्र):",
        "platform": "📱 प्लेटफॉर्म सोर्स:",
        "category": "📁 नीश कैटेगरी:",
        "velocity": "⏱️ सिग्नल वेलोसिटी:",
        "apply_btn": "🚀 कॉन्फ़िगरेशन लागू करें और रडार अपडेट करें",
        "telemetry_title": "📊 लाइव टेलीमेट्री और ग्रोथ पूर्वानुमान",
        "custom_search": "🔍 कस्टम एसेट सर्च (वैकल्पिक):",
        "active_signals_for": "सक्रिय सिग्नल:",
        "filtered_asset": "ट्रेंडिंग सिग्नल",
        "search_volume": "सर्च वॉल्यूम",
        "future_forecast": "फ्यूचर ट्रेंड फोरकास्ट",
        "chart_title": "📈 डायनेमिक वेलोसिटी और डिमांड फ़ोरकास्ट कर्व",
        "matrix_title": "💡 एक्शनएबल इंटेलिजेंस और स्ट्रैटेजी मैट्रिक्स",
        "locked_title": "🔒 मल्टी-चैनल ब्लूप्रिंट लॉक है",
        "locked_info": (
            "हाई-कन्वर्टिंग स्क्रिप्ट, वायरल हुक, एड कॉपी और एग्जीक्यूशन प्लान"
            " अनलॉक करें।"
        ),
        "upgrade_btn": "🔥 प्रो में अपग्रेड करें और पूरा इंजन अनलॉक करें",
        "analyzing_custom": "सिग्नल क्षमता का विश्लेषण:",
        "select_asset": "🎯 फ़िल्टर किया गया एसेट चुनें:",
        "operating_role": "👤 आपकी भूमिका (Role):",
        "gen_blueprint": "⚡ मास्टर स्ट्रैटेजी ब्लूप्रिंट जनरेट करें",
        "monetization": "💰 डायरेक्ट हाई-ROI मोनेटाइजेशन मॉडल",
        "hook": "🎬 विजुअल स्क्रिप्ट और हाई-रिटेंशन हुक (प्लग एंड प्ले)",
        "audio": "🎵 अनुशंसित हाई-कन्वर्टिंग ऑडियो वाइब",
        "caption": "📢 हाई-ROAS कैप्शन और CTA फ्रेमवर्क",
        "plan": "📝 3-चरणीय त्वरित एग्जीक्यूशन रोडमैप",
        "score_label": "अनुमानित वायरल स्कोर",
        "export_pdf_btn": "📄 ब्लूप्रिंट PDF डाउनलोड करें",
        "share_wa_btn": "💬 व्हाट्सएप पर शेयर करें",
        "competitor_insight": "🕵️ लाइव कॉम्पिटिटर एड इंटेलिजेंस",
    },
}

st.markdown(
    """
    
    """,
    unsafe_allow_html=True,
)


def safe_xml_text(text):
    """Safely sanitize text for ReportLab XML parser."""
    return (
        str(text)
        .replace("&", "&")
        .replace("<", "<")
        .replace(">", ">")
        .replace("\n", "
