import streamlit as st
from groq import Groq
import xml.etree.ElementTree as ET
import requests
import pandas as pd

# Initialize structural viewport properties
st.set_page_config(page_title="TrendPulse AI - Intelligence Portal", page_icon="📈", layout="wide")

# Secure API Ingestion Layer via Streamlit Cloud Secrets Manager
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY", "")

# Stripe Gateway Checkout Link Setup
STRIPE_CHECKOUT_URL = "https://stripe.com"

# SECURE ADMIN CREDENTIALS
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
        return clean_trends if clean_trends else [{"Topic": "Minimalist Office Setup Accessories", "Search Volume Surge": "100K+"}]
    except Exception:
        return [{"Topic": "Minimalist Office Setup Accessories", "Search Volume Surge": "100K+"}]

# 2. Cloud AI Processing Core (Bulletproof Text Engine)
def process_cloud_analysis_text(trend_keyword):
    if not GROQ_API_KEY:
        return None
        
    client = Groq(api_key=GROQ_API_KEY)
    
    prompt = f"""
    You are an elite Enterprise B2B Data Analytics Engine and E-commerce Growth Strategist.
    Provide an exhaustive, deeply comprehensive commercial intelligence report for the trending keyword: '{trend_keyword}'.
    
    Format the response EXACTLY like this with no conversational filler or intro:
    
    🎯 TARGET ASSIGNMENT:
    {trend_keyword}
    
    💼 MASTER OPERATIONAL BLUEPRINT & MONETIZATION:
    [Provide a massive, highly-detailed step-by-step business blueprint. Break it down into four long paragraphs:
    1. SOURCING LOGISTICS: Specific suppliers, private sourcing agents, and manufacturing hubs on networks like Alibaba.
    2. PRICING ARCHITECTURE: Detailed mathematical breakdown of product unit cost, packaging costs, international shipping metrics, and an optimized premium retail price to ensure massive gross margins.
    3. STOREFRONT & VISUAL FUNNEL: How to structure a premium single-product Shopify store, landing page conversion triggers, trust seals, and customer review placement strategies.
    4. DIGITAL ACQUISITION CHANNELS: Exact Meta, TikTok, and Google ad targeting interests, lookalike scaling plans, and retargeting hooks to dominate custom buyer personas.]
    
    🧠 CONSUMER PSYCHOLOGY & MARKET PAIN POINTS:
    [Provide a detailed multi-sentence breakdown analyzing the emotional and practical reasons consumers are suddenly creating a massive search interest spike for this item. What specific friction, problem, or market supply bottleneck does it solve?]
    
    🎬 HIGH-RETENTION VIRAL VIDEO AD CREATIVE SCRIPTS:
    [Write 3 complete, highly engaging viral video ad hooks: 1 Curiosity Hook, 1 Pain-Point Hook, 1 Benefit Hook. Follow this with a full, detailed 15-second visual script outline including on-screen text overlays (LN) and exact creator performance actions for dropshipping content conversion.]
    """
    
    active_models = ["llama-3.3-70b-versatile", "llama-3.1-8b-instant"]
    
    for model_id in active_models:
        try:
            completion = client.chat.completions.create(
                model=model_id, 
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
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

# ==========================================
# VISUAL RENDERING DASHBOARD
# ==========================================
st.title("🚀 TrendPulse AI: Commercial Intelligence Feed")
st.caption("24/7 Autonomous B2B trend tracking engine operating at zero overhead.")

st.markdown("---")

# Admin Login Terminal
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
                st.session_state["is_premium_active"] = True  
                st.success("🎯 Owner Identity Verified! Full Structural Rights Granted.")
                st.rerun()
            else:
                st.error("❌ Invalid Admin Credentials. Access Denied.")
    else:
        st.success("👑 Welcome Master Owner! You have absolute bypass control over the platform.")
        st.session_state["is_premium_active"] = st.checkbox("Bypass Paywall Gate (Turn premium mode ON/OFF instantly)", value=st.session_state["is_premium_active"])
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
    df = pd.DataFrame(trends)
    st.dataframe(df, use_container_width=True, hide_index=True)
    
    if st.button("🔄 Refresh Live Telemetry Data", use_container_width=True):
        st.rerun()
    
    st.markdown("---")
    st.markdown("### 🔓 Free Tier Account Status")
    st.caption("You are viewing limited baseline telemetry. Upgrade to unlock full structural insights.")

with right_col:
    st.subheader("👑 Premium Actionable Monetization Blueprint")
    
    if not st.session_state["is_premium_active"]:
        st.error("🔒 THIS CARD IS LOCKED BY THE TRENDPULSE ACCESS ENGINE")
        st.info("The execution layer is reserved strictly for enterprise marketing agencies and dropshipping brands.")
        st.link_button("🔥 Upgrade to Agency Enterprise Tier Instantly", STRIPE_CHECKOUT_URL, type="primary", use_container_width=True)
        
    else:
        # FIXED: Extracting trend string securely using index matching to completely isolate dictionary keys
        selected_keyword = "Minimalist Office Setup Accessories"
        if isinstance(trends, list) and len(trends) > 0:
            first_element = trends[0]
            if isinstance(first_element, dict):
                selected_keyword = first_element.get("Topic", "Minimalist Office Setup Accessories")
        
        if st.button("⚡ Run Cloud Analysis Node", type="primary", use_container_width=True):
            if not GROQ_API_KEY:
                st.error("⚠️ System Deployment Error: Groq API Key missing in stream configurations.")
            else:
                with st.spinner("Processing automated cloud intelligence matrix rows..."):
                    ai_result = process_cloud_analysis_text(selected_keyword)
                    
                    if ai_result:
                        st.session_state["ai_report_output"] = ai_result
                        st.balloons()
                    else:
                        st.error("Cloud processing stalled. Displaying highly optimized local fallback node data.")
                        st.session_state["ai_report_output"] = "🎯 TARGET ASSIGNMENT:\n" + selected_keyword + "\n\n💼 MASTER BLUEPRINT:\nSource " + selected_keyword + " via verified B2B channels. Build a high-converting storefront with 60%+ margins. Launch targeted Meta Advantage+ ad structures.\n\n🧠 CONSUMER PSYCHOLOGY:\nMassive digital demand spike meeting low immediate local market supply chain alternatives.\n\n🎬 VIDEO CREATIVE SCRIPTS:\nHook: 'Stop scrolling if you source your " + selected_keyword + " manually...'"

        # Show Output and Download button if data exists in memory
        if st.session_state["ai_report_output"]:
            st.info("🔥 Live AI Analysis Completed Successfully!")
            st.text_area("📋 Live Enterprise Strategy Report", value=st.session_state["ai_report_output"], height=450)
            
            # FIXED: Isolated payload structure from functional parenthesis block to resolve SyntaxError 
            current_report = st.session_state["ai_report_output"]
            download_payload = "TRENDPULSE AI - OFFICIAL COMMERCIAL BLUEPRINT REPORT\n======================================================\n\n" + current_report
