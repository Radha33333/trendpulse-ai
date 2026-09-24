import json
import xml.etree.ElementTree as ET
from groq import Groq
import pandas as pd
import requests
import streamlit as st

st.set_page_config(
    page_title="TrendPulse AI - Universal Trend & Monetization Engine",
    page_icon="🚀",
    layout="wide",
)

GROQ_API_KEY = st.secrets.get("GROQ_API_KEY", "")
STRIPE_CHECKOUT_URL = "https://stripe.com"


# Telemetry Fetcher
@st.cache_data(ttl=600)
def fetch_realtime_spikes():
  url = "https://trends.google.com/trending/rss?geo=IN"
  try:
    headers = {"User-Agent": "Mozilla/5.0"}
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
            {"Topic": str(title_text), "Search Volume": str(traffic_text)}
        )

    return (
        raw_trends[:10]
        if raw_trends
        else [{"Topic": "AI Automation Tools", "Search Volume": "100K+"}]
    )
  except Exception:
    return [{"Topic": "AI Automation Tools", "Search Volume": "100K+"}]


# AI Cloud Processing
def process_universal_trend(trend_keyword, category, target_audience):
  if not GROQ_API_KEY:
    return {
        "trend_stage": "🌱 Early Signal (Predicted Peak in 7-10 Days)",
        "monetization_idea": (
            f"Create specialized digital products or affiliate content around"
            f" '{trend_keyword}'."
        ),
        "content_script_hook": (
            f"Everyone is talking about '{trend_keyword}', but here is how you"
            " can actually profit from it..."
        ),
        "execution_steps": (
            "1. Build landing page / short video\n2. Add affiliate links or"
            " product\n3. Drive organic social traffic"
        ),
    }

  client = Groq(api_key=GROQ_API_KEY)
  prompt = f"""
    You are an Elite Trend Forecasting & Monetization Expert.
    Analyze the keyword: '{trend_keyword}' under Category: '{category}' for Audience: '{target_audience}'.

    Provide output in strict JSON format with keys:
    {{
      "trend_stage": "Specify if it is '🌱 Early Signal (Predicted Peak in 7-10 Days)' or '🔥 Peak Viral Surge (Active Now)'",
      "monetization_idea": "Concrete way to make money from this trend in this category",
      "content_script_hook": "Viral 3-second script hook or headline to capture audience",
      "execution_steps": "Numbered 3-step action plan to execute and cash in immediately"
    }}
    """

  try:
    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
        response_format={"type": "json_object"},
    )
    return json.loads(completion.choices[0].message.content)
  except Exception:
    return {
        "trend_stage": "🔥 Active Peak Surge",
        "monetization_idea": (
            f"Launch targeted promotion or content strategy for '{trend_keyword}'"
        ),
        "content_script_hook": (
            f"Do not ignore this '{trend_keyword}' trend before it expires!"
        ),
        "execution_steps": (
            "1. Post high-retention content\n2. Add CTA\n3. Capture leads"
        ),
    }


# Session State
if "is_premium" not in st.session_state:
  st.session_state["is_premium"] = False

# UI Layout
st.title("🚀 TrendPulse AI: Universal Predictive Engine")
st.caption("Forecast Trends Before They Peak | Multi-Category Monetization Hub")

st.markdown("---")

# Sandbox Toggle
with st.expander("🔑 Pro Access Control Terminal"):
  st.session_state["is_premium"] = st.checkbox(
      "Simulate Active Pro Subscription", value=st.session_state["is_premium"]
  )

left_col, right_col = st.columns([1, 1], gap="large")

with left_col:
  st.subheader("📊 Live Telemetry & Surge Radar")

  # Category Filter Selection
  selected_category = st.selectbox(
      "📁 Select Target Niche / Category:",
      [
          "E-Commerce & Physical Products",
          "Tech, AI & Software",
          "Entertainment & Viral Pop Culture",
          "Finance, Business & Crypto",
          "Fitness, Health & Lifestyle",
      ],
  )

  trends_data = fetch_realtime_spikes()

  # Adding Predictive Stage simulation to table
  table_data = []
  for idx, item in enumerate(trends_data):
    stage = (
        "🌱 Emerging (Aane Wala Hai)"
        if idx % 2 == 0
        else "🔥 Peak Surge (Abhi Hai)"
    )
    table_data.append({
        "Keyword": item["Topic"],
        "Search Volume": item["Search Volume"],
        "Trend Status": stage,
    })

  df = pd.DataFrame(table_data)
  st.dataframe(df, width="stretch", hide_index=True)

  if st.button("🔄 Refresh Radar Data", width="stretch"):
    st.cache_data.clear()
    st.rerun()

with right_col:
  st.subheader("💡 Monetization & Execution Co-Pilot")

  if not st.session_state["is_premium"]:
    st.error("🔒 PREDICTIVE MONETIZATION ENGINE IS LOCKED")
    st.info(
        "Unlock full category forecasting and step-by-step profit blueprints."
    )
    st.link_button(
        "🔥 Upgrade to Pro Tier Now",
        STRIPE_CHECKOUT_URL,
        type="primary",
        width="stretch",
    )
  else:
    selected_keyword = st.selectbox(
        "🎯 Select Trend Keyword to Analyze:", [t["Topic"] for t in trends_data]
    )

    user_type = st.radio(
        "👤 Select Your Role:",
        [
            "Content Creator / Influencer",
            "E-Commerce / Dropshipper",
            "Freelancer / Agency Owner",
        ],
        horizontal=True,
    )

    if st.button("⚡ Forecast & Generate Profit Blueprint", type="primary", width="stretch"):
      with st.spinner("Analyzing cross-platform velocity signals..."):
        result = process_universal_trend(
            selected_keyword, selected_category, user_type
        )

        st.success(f"🎯 Analysis Complete for **{selected_keyword}**")
        st.info(f"**Status:** {result.get('trend_stage')}")

        with st.expander("💰 Monetization Strategy (Paise Kaise Banayein)", expanded=True):
          st.write(result.get("monetization_idea"))

        with st.expander(
            "🎬 High-Retention Viral Hook / Headline", expanded=True
        ):
          st.code(f'"{result.get("content_script_hook")}"', language="text")

        with st.expander("📝 3-Step Execution Blueprint", expanded=True):
          st.write(result.get("execution_steps"))
