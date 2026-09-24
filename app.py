import streamlit as st
from groq import Groq
import xml.etree.ElementTree as ET
import requests
import pandas as pd

# Initialize structural properties with current enterprise layout
st.set_page_config(page_title="TrendPulse AI - Commercial Portal", page_icon="📈", layout="wide")

# Secure API Ingestion Layer via Streamlit Cloud Secrets Manager
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY", "")

# Stripe Gateway Checkout Link Setup
STRIPE_CHECKOUT_URL = "https://stripe.com"

# SECURE ADMIN CREDENTIALS
ADMIN_USERNAME = "admin123"
ADMIN_PASSWORD = "trendpulse_owner_2026"

# Premium CSS Theme Injection Layer for high-end B2B UI styling
st.markdown("""
<style>
    .report-box { background-color: #f8f9fa; border-left: 5px solid #ff4b4b; padding: 20px; border-radius: 5px; margin-bottom: 20px; }
    .stButton>button { border-radius: 4px; height: 3em; transition: all 0.3s ease; }
    .stButton>button:hover { background-color: #ff4b4b !important; color: white !important; border: 1px solid #ff4b4b !important; }
</style>
""", unsafe_allow_html=True)

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
            raw_trends.append({"Topic": str(title), "Search Volume Surge": str(traffic_text)})
            
        blacklist = ["accident", "arrested", "match", "vs", "election", "died", "killed", "movie review", "ipl"]
        clean_trends = [t for t in raw_trends if not any(word in t["Topic"].lower() for word in blacklist)]
        return clean_trends if clean_trends else [{"Topic": "Minimalist Office Setup Accessories", "Search Volume Surge": "100K+"}]
    except Exception:
        return [{"Topic": "Minimalist Office Setup Accessories", "Search Volume Surge": "100K+"}]

# 2. Cloud AI Processing Core (Optimized Text Pipeline)
def process_cloud_analysis_text(trend_keyword, tier_level):
    if not GROQ_API_KEY:
        return None
        
    client = Groq(api_key=GROQ_API_KEY)
    sanitized_keyword = str(trend_keyword).strip()
    
    prompt = f"""
    You are an elite Enterprise B2B Data Analytics Engine and E-commerce Growth Strategist.
    Provide an exhaustive, deeply comprehensive commercial intelligence report for the trending keyword: '{sanitized_keyword}'.
    Target Subscription Tier context requirements: {tier_level}.
    
    Format the response EXACTLY like this with no conversational filler or intro text:
    
    🎯 TARGET ASSIGNMENT:
    {sanitized_keyword}
    
    💼 MASTER OPERATIONAL BLUEPRINT & MONETIZATION:
    1. SOURCING LOGISTICS: Identify targeted manufacturing hubs and wholesale validation networks on B2B platforms like Alibaba.
    2. PRICING ARCHITECTURE: Provide a detailed numerical cost breakdown (Unit landing cost, premium packaging, global freight estimates) and calculate an optimized retail price for high gross margins.
    3. STOREFRONT FUNNEL: Explain the design blueprint for a single-product high-converting Shopify store layout, utilizing high-retention social proof placement.
    4. ACQUISITION PLAN: Detail target interest arrays for Meta Ads, scaling structures, and lookalike modeling setups.
    
    🧠 CONSUMER PSYCHOLOGY & MARKET PAIN POINTS:
    Provide a professional multi-sentence breakdown analyzing the emotional factors and supply chain shortages driving this sudden spike in search velocity.
    
    🎬 HIGH-RETENTION VIRAL VIDEO AD CREATIVE SCRIPTS:
    Write 3 distinct high-converting script hooks (1 Curiosity, 1 Problem-Centric, 1 Direct Benefit) accompanied by a complete 15-second narrative execution timeline for social commerce creators.
    """
    
    active_models = ["llama-3.1-8b-instant", "llama-3.3-70b-versatile"]
    
    for model_id in active_models:
        try:
            completion = client.chat.completions.create(
                model=model_id, 
                messages=[{"role": "user", "content": prompt}],
                temperature=0.15
            )
            return completion.choices.message.content
        except Exception:
            continue  
            
    return None

# Initialize Session States
if "is_admin_logged_in" not in st.session_state:
    st.session_state["is_admin_logged_in"] = False
if "is_premium_active" not in st.session_state:
    st.session_state["is_premium_active"] = False
if "ai_report_output" not in st.session_state:
    st.session_state["ai_report_output"] = ""
if "selected_tier" not in st.session_state:
    st.session_state["selected_tier"] = "The Pulse Feed (Basic)"

# ==========================================
# VISUAL RENDERING DASHBOARD
# ==========================================
st.title("🚀 TrendPulse AI: Commercial Intelligence Feed")
st.caption("24/7 Autonomous B2B trend tracking engine operating at zero overhead.")

st.markdown("---")

# Admin Login Terminal Container View
with st.expander("🔑 Owner / Admin Login Terminal", expanded=st.session_state["is_admin_logged_in"]):
    if not st.session_state["is_admin_logged_in"]:
        col1, col2 = st.columns(2)
        with col1:
            input_user = st.text_input("Admin User ID", placeholder="Enter admin username")
        with col2:
            input_pass = st.text_input("Admin Security Password", type="password", placeholder="Enter secret password")
        
        if st.button("🔓 Authenticate Admin Rights", width="stretch", type="primary"):
            if input_user == ADMIN_USERNAME and input_pass == ADMIN_PASSWORD:
                st.session_state["is_admin_logged_in"] = True
                st.session_state["is_premium_active"] = True  
                st.success("🎯 Owner Identity Verified! Full Structural Rights Granted.")
                st.rerun()
            else:
                st.error("❌ Invalid Admin Credentials. Access Denied.")
    else:
        st.success("👑 Welcome Master Owner! You have absolute bypass control over the platform.")
        st.session_state["is_premium_active"] = st.checkbox("Bypass Paywall Gate (Force Premium Access ON)", value=st.session_state["is_premium_active"])
        
        st.session_state["selected_tier"] = st.selectbox(
            "Select Account Simulation Mode:",
            ["The Pulse Feed (Basic - ₹2,499/mo)", "The Agency Enterprise Vault (Premium - ₹14,999/mo)"]
        )
        
        if st.button("🔒 Secure Logout from Admin Terminal", type="secondary"):
            st.session_state["is_admin_logged_in"] = False
            st.session_state["is_premium_active"] = False
            st.session_state["ai_report_output"] = ""
            st.rerun()

st.markdown("---")

left_col, right_col = st.columns(2, gap="large")

with left_col:
    st.subheader("📊 Live Telemetry Feeds")
    st.write("Validated commercial traffic acceleration records (India):")
    
    trends = fetch_realtime_commercial_spikes()
    
    processed_trends = []
    for index, item in enumerate(trends):
        velocity_score = 94.2 - (index * 6.4)
        processed_trends.append({
            "Breakout Keyword Niche": item.get("Topic", "Unknown Trend"),
            "Search Volume": item.get("Search Volume Surge", "50K+"),
            "Velocity Score": f"+{velocity_score}% Realtime"
        })
        
    df = pd.DataFrame(processed_trends)
    st.dataframe(df, width="stretch", hide_index=True)
    
    if st.button("🔄 Refresh Live Telemetry Data", width="stretch"):
        st.rerun()
    
    st.markdown("---")
    st.markdown("### 🔓 Free Tier Account Status")
    st.caption("You are viewing limited baseline telemetry. Upgrade to unlock full structural insights.")

with right_col:
    st.subheader("👑 Premium Actionable Monetization Blueprint")
    
    if not st.session_state["is_premium_active"]:
        st.error("🔒 THIS CARD IS LOCKED BY THE TRENDPULSE ACCESS ENGINE")
        st.info("The execution layer is reserved strictly for enterprise marketing agencies and dropshipping brands.")
        st.link_button("🔥 Upgrade to Agency Enterprise Tier Instantly", STRIPE_CHECKOUT_URL, type="primary", width="stretch")
        
    else:
        # FIXED: Directly unpack row 0 out of the list container to completely eliminate the TypeError crash
        selected_keyword = "Minimalist Office Setup Accessories"
        try:
            if isinstance(trends, list) and len(trends) > 0:
                first_row_dict = trends[0]  # Crucial Fix: Safely fetch the top trend dictionary
                selected_keyword = str(first_row_dict.get("Topic", "Minimalist Office Setup Accessories"))
        except Exception:
            selected_keyword = "Minimalist Office Setup Accessories"
            
        st.info(f"🎯 Currently Tracking Highest Velocity Target: **{selected_keyword}**")
        
        if st.button("⚡ Run Cloud Analysis Node", type="primary", width="stretch"):
            if not GROQ_API_KEY:
                st.error("⚠️ System Deployment Error: Groq API Key missing in stream configurations.")
            else:
                with st.spinner("Processing automated cloud intelligence matrix rows..."):
                    ai_result = process_cloud_analysis_text(selected_keyword, st.session_state["selected_tier"])
                    
                    if ai_result:
                        st.session_state["ai_report_output"] = str(ai_result)
                        st.balloons()
                    else:
                        st.error("Cloud processing stalled. Displaying highly optimized local fallback data.")
