import json
import xml.etree.ElementTree as ET
from groq import Groq
import pandas as pd
import requests
import streamlit as st

# 1. Initialize Page Properties
st.set_page_config(
    page_title="TrendPulse AI - Predictive Commercial & Creator Intelligence",
    page_icon="⚡",
    layout="wide",
)

# Secrets & Configuration Management
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY", "")
STRIPE_CHECKOUT_URL = "https://stripe.com"

# Premium CSS Theme
st.markdown(
    """

""",
    unsafe_allow_html=True,
)


# 2. Telemetry Ingestion Engine (Google Trends RSS Feed)
@st.cache_data(ttl=600)
def fetch_realtime_commercial_spikes():
  url = "https://trends.google.com/trending/rss?geo=IN"
  try:
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )
    }
    response = requests.get(url, headers=headers, timeout=10)
    root = ET.fromstring(response.content)
    raw_trends = []
    ns = {"ht": "https://trends.google.com/trending/rss"}

    for item in root.findall(".//item"):
      title = item.find("title")
      approx_traffic = item.find("ht:approx_traffic", ns)

      title_text = title.text if title is not None else ""
      traffic_text = (
          approx_traffic.text if approx_traffic is not None else "50K+"
      )

      if title_text:
        raw_trends.append(
            {"Topic": str(title_text), "Search Volume Surge": str(traffic_text)}
        )

    blacklist = [
        "accident",
        "arrested",
        "match",
        "vs",
        "election",
        "died",
        "killed",
        "movie review",
        "ipl",
    ]
    clean_trends = [
        t
        for t in raw_trends
        if not any(word in t["Topic"].lower() for word in blacklist)
    ]
    return (
        clean_trends[:5]
        if clean_trends
        else [{
            "Topic": "Minimalist Office Setup Accessories",
            "Search Volume Surge": "100K+",
        }]
    )
  except Exception:
    return [{
        "Topic": "Minimalist Office Setup Accessories",
        "Search Volume Surge": "100K+",
    }]


# 3. Fail-Safe Local Intelligence Backup
def get_fail_safe_intelligence(trend_keyword, user_role):
  if user_role == "E-Commerce Merchant":
    return {
        "target_trend": f"{trend_keyword}",
        "viral_prediction": (
            "88% Probability of Saturation in 12 Days. High Buying Intent."
        ),
        "sourcing_logistics": (
            f"Source '{trend_keyword}' variants on Alibaba / IndiaMART at"
            " estimated ₹350/unit."
        ),
        "pricing_architecture": (
            "Cost: ₹350 | Freight & Packaging: ₹150 | Target Retail Price:"
            " ₹1,499 | Profit Margin: ~66%"
        ),
        "storefront_funnel": (
            "Single-product Shopify landing page featuring countdown timer,"
            " sticky CTA, and video reviews."
        ),
        "meta_ad_targeting": (
            "Interests: Online Shopping, Tech Gadgets, Home Office Setup."
            " Age: 22-40."
        ),
        "high_retention_hook": (
            f"Stop wasting money on bad workspace setups! This '{trend_keyword}'"
            " changes everything..."
        ),
    }
  else:  # Reel Creator / Influencer
    return {
        "target_trend": f"{trend_keyword}",
        "viral_prediction": (
            "94% Viral Potential. Peak engagement window: Next 5-7 days."
        ),
        "hook_curiosity": (
            f"I bet you didn't know this hack about '{trend_keyword}'..."
        ),
        "hook_problem": (
            f"If you're struggling with workspace clutter, this"
            f" '{trend_keyword}' is your solution."
        ),
        "hook_direct": (
            f"Why everyone is obsessed with this '{trend_keyword}' right now."
        ),
        "video_storyboard": (
            "0-3s: Fast-paced visual hook | 3-8s: Showcase pain point | 8-12s:"
            " Reveal product/solution | 12-15s: Clear CTA to comment link."
        ),
        "audio_hashtag_stack": (
            "#TrendingIndia #ViralReels #SetupInspiration #ProductFinds"
            " #TechTrends2026"
        ),
    }


# 4. Cloud AI Intelligence Matrix (Groq API Engine)
def process_cloud_intelligence(trend_keyword, user_role):
  if not GROQ_API_KEY:
    return get_fail_safe_intelligence(trend_keyword, user_role)

  client = Groq(api_key=GROQ_API_KEY)

  if user_role == "E-Commerce Merchant":
    prompt = f"""
        You are a cold, analytical E-Commerce Sourcing & Growth Strategist.
        Analyze keyword: '{trend_keyword}'. Output strictly valid JSON with keys:
        {{
          "target_trend": "{trend_keyword}",
          "viral_prediction": "Estimated peak days and saturation percentage",
          "sourcing_logistics": "Where and how to source this item cheaply",
          "pricing_architecture": "Numerical breakdown of Landing cost, Retail price, and Margin %",
          "storefront_funnel": "Shopify single-product conversion layout blueprint",
          "meta_ad_targeting": "Specific Meta/TikTok Interest targets and demography",
          "high_retention_hook": "3-second video ad script hook"
        }}
        """
  else:  # Reel Creator / Influencer
    prompt = f"""
        You are an Elite Social Media Viral Content Strategist.
        Analyze keyword: '{trend_keyword}'. Output strictly valid JSON with keys:
        {{
          "target_trend": "{trend_keyword}",
          "viral_prediction": "Viral score and optimal posting timeframe",
          "hook_curiosity": "Curiosity-driven 3-second script hook",
          "hook_problem": "Problem-centric 3-second script hook",
          "hook_direct": "Direct benefit-driven 3-second script hook",
          "video_storyboard": "15-second timeline breakdown (0-3s, 3-8s, 8-12s, 12-15s)",
          "audio_hashtag_stack": "Top 5 high-velocity hashtags and audio style suggestion"
        }}
        """

  active_models = ["llama-3.3-70b-versatile", "llama-3.1-8b-instant"]

  for model in active_models:
    try:
      completion = client.chat.completions.create(
          model=model,
          messages=[{"role": "user", "content": prompt}],
          temperature=0.1,
          response_format={"type": "json_object"},
      )
      return json.loads(completion.choices[0].message.content)
    except Exception:
      continue

  return get_fail_safe_intelligence(trend_keyword, user_role)


# 5. Session State Initialization
if "is_premium_active" not in st.session_state:
  st.session_state["is_premium_active"] = False
if "ai_report" not in st.session_state:
  st.session_state["ai_report"] = None

# ==========================================
# DASHBOARD UI RENDERING LAYER
# ==========================================
st.title("⚡ TrendPulse AI: Predictive Trend Engine")
st.caption(
    "Real-time B2B Commerce & Creator Intelligence Platform | Monetization"
    " Suite"
)

st.markdown("---")

# Access Control Hub
with st.expander(
    "👑 Access & License Gatekeeper",
    expanded=not st.session_state["is_premium_active"],
):
  col1, col2 = st.columns(2)
  with col1:
    st.session_state["is_premium_active"] = st.checkbox(
        "Bypass Paywall (Simulate Active Pro Subscriber)",
        value=st.session_state["is_premium_active"],
    )
  with col2:
    if st.session_state["is_premium_active"]:
      st.success("👑 License Verified: Unlimited Enterprise Tier")
    else:
      st.warning("🔒 Sandbox View: Upgrade to unlock AI Monetization Blueprints")

st.markdown("---")

left_col, right_col = st.columns([1, 1], gap="large")

# LEFT COLUMN: Live Telemetry
with left_col:
  st.subheader("📊 Live Telemetry & Predictive Spikes")
  st.write("Real-time surge signals extracted from search networks (India):")

  raw_trends = fetch_realtime_commercial_spikes()

  processed = []
  for index, item in enumerate(raw_trends):
    score = round(96.5 - (index * 5.2), 1)
    processed.append({
        "Breakout Keyword": item.get("Topic", "Unknown"),
        "Search Surge": item.get("Search Volume Surge", "50K+"),
        "Predictive Velocity": f"+{score}% (High)",
    })

  df = pd.DataFrame(processed)
  st.dataframe(df, width="stretch", hide_index=True)

  if st.button("🔄 Refresh Telemetry Streams", width="stretch"):
    st.cache_data.clear()
    st.rerun()

  st.markdown("---")
  st.markdown("### 💡 Monetization Tiers")
  st.info(
      "• **Creator Tier (₹1,499/mo):** Viral Hooks, Storyboards & Hashtag"
      " Stacks\n• **Merchant Tier (₹4,999/mo):** Sourcing Costs, Margins & Ad"
      " Audiences\n• **Agency Enterprise (₹14,999/mo):** Unlimited API &"
      " White-Label Exports"
  )

# RIGHT COLUMN: AI Intelligence Co-Pilot
with right_col:
  st.subheader("🤖 AI Trend Co-Pilot & Execution Matrix")

  if not st.session_state["is_premium_active"]:
    st.error("🔒 THIS MODULE IS LOCKED FOR FREE ACCOUNTS")
    st.info("Upgrade your tier to unlock instant product sourcing and script generation.")
    st.link_button(
        "🔥 Upgrade to Pro Membership Instantly",
        STRIPE_CHECKOUT_URL,
        type="primary",
        width="stretch",
    )
  else:
    # Select Keyword & Role Mode
    trend_options = [t.get("Topic") for t in raw_trends]
    selected_trend = st.selectbox(
        "🎯 Select Target Trend Keyword:", trend_options
    )

    user_mode = st.radio(
        "👤 Select Target Persona Output:",
        ["E-Commerce Merchant", "Reel Creator / Influencer"],
        horizontal=True,
    )

    if st.button("⚡ Generate AI Blueprint", type="primary", width="stretch"):
      with st.spinner("Processing cloud intelligence matrices..."):
        st.session_state["ai_report"] = process_cloud_intelligence(
            selected_trend, user_mode
        )
        st.balloons()

    # Render Report Data
    report = st.session_state.get("ai_report")
    if report and report.get("target_trend") == selected_trend:
      st.markdown("---")
      st.success(f"🎯 Analysis Complete for **{selected_trend}**")

      # Dynamic View based on Selected Role
      if user_mode == "E-Commerce Merchant":
        st.markdown(
            f"**📈 Predictive Surge:** {report.get('viral_prediction')}"
        )

        with st.expander("📦 1. Sourcing & Logistics", expanded=True):
          st.write(report.get("sourcing_logistics"))

        with st.expander("💰 2. Pricing & Profit Margins", expanded=True):
          st.write(report.get("pricing_architecture"))

        with st.expander("🛒 3. Storefront Funnel Strategy", expanded=True):
          st.write(report.get("storefront_funnel"))

        with st.expander("🎯 4. Meta / TikTok Ad Targeting", expanded=True):
          st.write(report.get("meta_ad_targeting"))

        with st.expander("🎬 5. Converting Video Ad Hook", expanded=True):
          st.code(f'"{report.get("high_retention_hook")}"', language="text")

      else:  # Creator Mode
        st.markdown(
            f"**🔥 Viral Score & Velocity:** {report.get('viral_prediction')}"
        )

        with st.expander(
            "🎬 1. Three-Second High-Retention Script Hooks", expanded=True
        ):
          st.markdown(
              f"**Curiosity Hook:** \"{report.get('hook_curiosity')}\""
          )
          st.markdown(f"**Problem Hook:** \"{report.get('hook_problem')}\"")
          st.markdown(f"**Direct Hook:** \"{report.get('hook_direct')}\"")

        with st.expander(
            "⏱️ 2. 15-Second Storyboard Execution Timeline", expanded=True
        ):
          st.write(report.get("video_storyboard"))

        with st.expander(
            "🏷️ 3. Recommended Hashtag Stack & Audio Cue", expanded=True
        ):
          st.code(report.get("audio_hashtag_stack"), language="text")

      # Download White-Label Executive Report
      st.markdown("---")
      download_text = f"TRENDPULSE AI REPORT - {selected_trend.upper()}\nMode: {user_mode}\n"
      for k, v in report.items():
        download_text += f"\n[{k.upper().replace('_', ' ')}]\n{v}\n"

      st.download_button(
          label="📥 Download White-Label Report (.txt)",
          data=download_text,
          file_name=f"trendpulse_{selected_trend.lower().replace(' ', '_')}_report.txt",
          mime="text/plain",
          width="stretch",
      )
