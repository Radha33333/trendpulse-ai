import streamlit as st
from groq import Groq
import xml.etree.ElementTree as ET
import requests
import pandas as pd
import json

# Initialize structural viewport properties
st.set_page_config(page_title="TrendPulse AI - Admin Portal", page_icon="📈", layout="wide")

# Secure API Ingestion Layer via Streamlit Cloud Secrets Manager
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY", "")

# Stripe Gateway Checkout Link Setup
STRIPE_CHECKOUT_URL = "https://stripe.com"

# SECURE ADMIN CREDENTIALS (यहाँ अपनी मनपसंद ID और Password बदल सकते हैं)
ADMIN_USERNAME = "admin123"
ADMIN_PASSWORD = "trendpulse_owner_2026"

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
    primary_trend = trend_data[0]["Topic"] if trend_data else "Minimalist Office Setup Accessories"
    
    if not GROQ_API_KEY:
        return get_fail_safe_local_blueprint(primary_trend)
        
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
    
    active_models = ["llama-3.3-70b-versatile", "llama-3.1-8b-instant"]
    
    for model_id in active_models:
        try:
            completion = client.chat.completions.create(
                model=model_id, 
                messages=[{"role": "user", "content": system_instruction}],
                temperature=0.0, 
                response_format={"type": "json_object"}
            )
            raw_output = completion.choices[0].message.content
            return json.loads(raw_output)
        except Exception:
            continue  
            
    return get_fail_safe_local_blueprint(primary_trend)

def get_fail_safe_local_blueprint(trend_keyword):
    return {
        "target_trend": f"{trend_keyword}",
        "business_pain_point": "High demand surge coupled with lack of specialized suppliers or high local pricing options.",
        "monetization_execution": f"Source unique variations of '{trend_keyword}' via B2B trade networks. Launch a dedicated single-product Shopify store and scale targeted conversion ads directly to relevant marketing channels.",
        "high_retention_hook": f"Stop scrolling if you are still sourcing your '{trend_keyword}' manually. Here is how top brands do it 10x faster..."
    }

# Initialize Session States
if "is_admin_logged_in" not in st.session_state:
    st.session_state["is_admin_logged_in"] = False
if "is_premium_active" not in st.session_state:
    st.session_state["is_premium_active"] = False

# ==========================================
# VISUAL RENDERING DASHBOARD
# ==========================================
st.title("🚀 TrendPulse AI: Commercial Intelligence Feed")
st.caption("24/7 Autonomous B2B trend tracking engine operating at zero overhead.")

st.markdown("---")

# --- SECURE EXPANDABLE ADMIN LOGIN GATEWAY ---
with st.expander("🔑 Owner / Admin Login Terminal", expanded=st.session_state["is_admin_logged_in"]):
    if not st.session_state["is_admin_logged_in"]:
        col1, col2 = st.columns(2)
        with col1:
            input_user = st.text_input("Admin User ID", placeholder="Enter admin username")
        with col2:
            input_pass = st.text_input("Admin Security Password", type="password", placeholder="Enter secret password")
        
        if st.button("🔓 Authenticate Admin Rights", use_container_width=True, type="primary"):
            if input_user == ADMIN_USERNAME and input_pass == ADMIN_PASSWORD:
                st.session_state["is_admin_logged_in"] = True
                st.session_state["is_premium_active"] = True  # Admin gets auto-premium
                st.success("🎯 Owner Identity Verified! Full Structural Rights Granted.")
                st.rerun()
            else:
                st.error("❌ Invalid Admin Credentials. Access Denied.")
    else:
        st.success("👑 Welcome Master Owner! You have absolute bypass control over the platform.")
        
        # Admin Special Rights: Toggle the paywall engine for testing in 1-click
        st.subheader("🛠️ Super-User Command Center")
        st.session_state["is_premium_active"] = st.checkbox("Bypass Paywall Gate (Turn premium mode ON/OFF instantly)", value=st.session_state["is_premium_active"])
        
        if st.button("🔒 Secure Logout from Admin Terminal", type="secondary"):
            st.session_state["is_admin_logged_in"] = False
            st.session_state["is_premium_active"] = False
            st.rerun()

st.markdown("---")

# Main Dashboard Content Split
left_col, right_col = st.columns(2, gap="large")

with left_col:
    st.subheader("📊 Live Telemetry Feeds")
    st.write("Validated commercial traffic acceleration records (India):")
    
    trends = fetch_realtime_commercial_spikes()
    df = pd.DataFrame(trends)
    st.dataframe(df, use_container_width=True, hide_index=True)
    
    if st.button("🔄 Refresh Live Telemetry Data", use_container_width=True):
        st.rerun()
    
    st.markdown("---")
    st.markdown("### 🔓 Free Tier Account Status")
    st.caption("You are viewing limited baseline telemetry. Upgrade to unlock full structural insights.")

with right_col:
    st.subheader("👑 Premium Actionable Monetization Blueprint")
    
    # SYSTEM GATEKEEP CHECK
    if not st.session_state["is_premium_active"]:
        st.error("🔒 THIS CARD IS LOCKED BY THE TRENDPULSE ACCESS ENGINE")
        st.info("The execution layer is reserved strictly for enterprise marketing agencies and dropshipping brands.")
        st.link_button("🔥 Upgrade to Agency Enterprise Tier Instantly", STRIPE_CHECKOUT_URL, type="primary", use_container_width=True)
        
    else:
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
                    
                    # White-label Report Exporter Functionality
                    st.markdown("---")
                    report_txt = (
                        f"TRENDPULSE AI - COMMERCIAL INTELLIGENCE REPORT\n"
                        f"==================================================\n"
                        f"TARGET TREND: {report.get('target_trend')}\n\n"
                        f"MONETIZATION STRATEGY:\n{report.get('monetization_execution')}\n\n"
                        f"CONSUMER PAIN POINT:\n{report.get('business_pain_point')}\n\n"
                        f"VIRAL VIDEO HOOK:\n\"{report.get('high_retention_hook')}\"\n"
                    )
                    
                    st.download_button(
                        label="📥 Download White-Label Executive Report (.txt)",
                        data=report_txt,
                        file_name=f"trendpulse_{report.get('target_trend').lower().replace(' ', '_')}_report.txt",
                        mime="text/plain",
                        use_container_width=True
                    )
        else:
            st.warning("Click the engine execution toggle button above to parse data loops instantly.")
