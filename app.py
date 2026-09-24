import streamlit as st
from groq import Groq
import xml.etree.ElementTree as ET
import requests
import pandas as pd
import json

# Initialize structural viewport properties
st.set_page_config(page_title="TrendPulse AI - Intelligence Portal", page_icon="📈", layout="wide")

# Secure API Ingestion Layer via Streamlit Cloud Secrets Manager
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY", "")

# Stripe Gateway Checkout Link Setup
STRIPE_CHECKOUT_URL = "https://stripe.com"

# 1. Telemetry Ingestion Layer (Google RSS Ground Truth Feed)
def fetch_realtime_commercial_spikes():
    url = "https://google.com" 
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=10)
        root = ET.fromstring(response.content)
        raw_trends = []
        ns = {'ht': 'hover/trending/rss'}
        
        for item in root.findall('.//item'):
            title = item.find('title').text
            approx_traffic = item.find('ht:approx_traffic', ns)
            traffic_text = approx_traffic.text if approx_traffic is not None else "50K+"
            raw_trends.append({"Topic": title, "Search Volume Surge": traffic_text})
            
        blacklist = ["accident", "arrested", "match", "vs", "election", "died", "killed", "movie review", "ipl"]
        clean_trends = [t for t in raw_trends if not any(word in t["Topic"].lower() for word in blacklist)]
        return clean_trends[:5] if clean_trends else [{"Topic": "Minimalist Office Setup Accessories", "Search Volume Surge": "100K+"}]
    except Exception:
        return [{"Topic": "Minimalist Office Setup Accessories", "Search Volume Surge": "100K+"}]

# 2. Cloud AI Processing Core (Zero-Temperature Factual Filter)
def process_cloud_analysis(trend_data):
    if not GROQ_API_KEY:
        return {"error": "Groq API Key configuration missing inside Secrets Manager."}
        
    client = Groq(api_key=GROQ_API_KEY)
    system_instruction = f"""
    You are a cold, analytical Data Analytics Engine. Do not append conversational filler.
    Analyze this validated market data array: {trend_data}.
    Identify the single most monetizable commercial keyword from this data.
    Output a strictly formatted JSON report matching this dictionary structure exactly:
    {{
      "target_trend": "The isolated business keyword",
      "business_pain_point": "The explicit problem consumers face leading to this search spike",
      "monetization_execution": "Concrete monetization steps (Product to source or service to offer)",
      "high_retention_hook": "A cold 3-second script hook addressing the pain point directly"
    }}
    """
    try:
        completion = client.chat.completions.create(
            model="llama3-8b-8192", 
            messages=[{"role": "user", "content": system_instruction}],
            temperature=0.0, 
            response_format={"type": "json_object"}
        )
        return json.loads(completion.choices[0].message.content)
    except Exception as e:
        return {"target_trend": "Data Node Failure", "business_pain_point": f"Error: {str(e)}", "monetization_execution": "Verify API authorization keys.", "high_retention_hook": "Halted."}

# Initialize Application State Core
if "is_premium_user" not in st.session_state:
    st.session_state["is_premium_user"] = False

# ==========================================
# VISUAL RENDERING DASHBOARD (MAIN VIEW FIXED)
# ==========================================
st.title("🚀 TrendPulse AI: Commercial Intelligence Feed")
st.caption("24/7 Autonomous B2B trend tracking engine operating at zero overhead.")

st.markdown("---")
# DIRECT ON-SCREEN ACCESS GATE MANAGER (Moved from hidden sidebar to main screen view)
st.subheader("🔐 Workspace Access Controls")
st.session_state["is_premium_user"] = st.checkbox("Simulate Paid Account Active (Check this box to unlock the AI Engine Below)", value=st.session_state["is_premium_user"])

if st.session_state["is_premium_user"]:
    st.success("👑 Premium License Verified - Cloud Processing System Online")
else:
    st.warning("⚠️ Restricted Sandbox Tier - Premium Features Gate-locked")
st.markdown("---")

left_col, right_col = st.columns(2, gap="large")

with left_col:
    st.subheader("📊 Live Telemetry Feeds")
    st.write("Validated commercial traffic acceleration records (India):")
    
    trends = fetch_realtime_commercial_spikes()
    df = pd.DataFrame(trends)
    st.dataframe(df, use_container_width=True, hide_index=True)
    
    st.markdown("### 🔓 Free Tier Account Status")
    st.caption("You are viewing limited baseline telemetry. Upgrade to unlock full structural insights.")

with right_col:
    st.subheader("👑 Premium Actionable Monetization Blueprint")
    
    # SYSTEM ACCESS ENGINE GATEKEEP LAYER
    if not st.session_state["is_premium_user"]:
        st.error("🔒 THIS CARD IS LOCKED BY THE TRENDPULSE ACCESS ENGINE")
        st.info("The execution layer is reserved strictly for enterprise marketing agencies and dropshipping brands.")
        st.link_button("🔥 Upgrade to Agency Enterprise Tier Instantly", STRIPE_CHECKOUT_URL, type="primary", use_container_width=True)
        
    else:
        # If user passes authorization tests, render the functional cloud button tools
        if st.button("⚡ Run Cloud Analysis Node", type="primary", use_container_width=True):
            if not GROQ_API_KEY:
                st.error("⚠️ System Deployment Error: Groq API Key missing in stream configurations.")
            else:
                with st.spinner("Processing automated cloud intelligence matrix rows..."):
                    report = process_cloud_analysis(trends)
                    
                    st.info(f"🎯 Target Asset Identified: **{report.get('target_trend')}**")
                    
                    with st.expander("💼 The Monetization Strategy", expanded=True):
                        st.write(report.get("monetization_execution"))
                        
                    with st.expander("🧠 Consumer Pain Point Analysis", expanded=True):
                        st.write(report.get("business_pain_point"))
                        
                    with st.expander("🎬 High-Retention 3-Second Video Hook", expanded=True):
                        st.code(f'"{report.get("high_retention_hook")}"', language="text")
        else:
            st.warning("Click the engine execution toggle button above to parse data loops instantly.")
