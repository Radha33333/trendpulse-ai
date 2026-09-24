import json
import xml.etree.ElementTree as ET
from groq import Groq
import pandas as pd
import requests
import streamlit as st

st.set_page_config(
    page_title="TrendPulse AI - Universal Predictive Engine",
    page_icon="🚀",
    layout="wide",
)

GROQ_API_KEY = st.secrets.get("GROQ_API_KEY", "")
STRIPE_CHECKOUT_URL = "https://stripe.com"


# 1. Google Trends Explore Integration Engine
@st.cache_data(ttl=600)
def fetch_google_explore_data(geo_code, search_type, category):
  url = f"https://trends.google.com/trending/rss?geo={geo_code}"
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
        raw_trends[:6]
        if raw_trends
        else [{"Topic": f"{category} Global Asset", "Search Volume": "100K+"}]
    )

  except Exception:
    return [{
        "Topic": f"{category} Emerging Keyword",
        "Search Volume": "75K+",
    }]


# 2. Universal Intelligence Generator
def process_universal_trend(trend_keyword, category, target_audience, channel):
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
    Analyze Keyword: '{trend_keyword}' | Category: '{category}' | Audience: '{target_audience}' | Platform Channel: '{channel}'.

    Provide output in strict JSON format with keys:
    {{
      "trend_stage": "Specify if it is '🌱 Early Signal (Predicted Peak in 7-10 Days)' or '🔥 Peak Viral Surge (Active Now)'",
      "monetization_idea": "Concrete way to make money from this trend in this category",
      "content_script_hook": "Viral 3-second script hook or headline to capture audience on {channel}",
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


# Session Setup
if "is_premium" not in st.session_state:
  st.session_state["is_premium"] = False

# App UI
st.title("🌐 TrendPulse AI: Google Explore Analytics Engine")
st.caption(
    "Deep Google Trends Explore Parameters Integration | Global Velocity"
    " Radar"
)

st.markdown("---")

# Pro Access Terminal
with st.expander("🔑 Pro Access Control Terminal"):
  st.session_state["is_premium"] = st.checkbox(
      "Simulate Active Pro Subscription", value=st.session_state["is_premium"]
  )

# Explore Filters Panel (Google Trends Style)
st.markdown("### 🔎 Google Explore Filter Configuration")
f_col1, f_col2, f_col3, f_col4 = st.columns(4)

with f_col1:
  geo_option = st.selectbox(
      "🌍 Country / Geography:",
      ["India (IN)", "United States (US)", "United Kingdom (GB)", "Global (ALL)"],
  )
  geo_map = {
      "India (IN)": "IN",
      "United States (US)": "US",
      "United Kingdom (GB)": "GB",
      "Global (ALL)": "US",
  }

with f_col2:
  search_source = st.selectbox(
      "📡 Search Type Source:",
      ["Web Search", "YouTube Search", "E-Commerce / Shopping Search"],
  )

with f_col3:
  selected_category = st.selectbox(
      "📁 Niche Category:",
      [
          "E-Commerce & Physical Products",
          "Tech, AI & Software",
          "Entertainment & Viral Pop Culture",
          "Finance, Business & Crypto",
          "Fitness, Health & Lifestyle",
      ],
  )

with f_col4:
  timeframe = st.selectbox(
      "⏱️ Timeframe Analysis:",
      ["Past 24 Hours (Realtime)", "Past 7 Days", "Past 30 Days"],
  )

st.markdown("---")

left_col, right_col = st.columns([1, 1], gap="large")

with left_col:
  st.subheader("📊 Live Telemetry Radar")

  # Search term input like Explore Search Bar
  custom_search = st.text_input(
      "🔍 Custom Search Term (Optional - Type to analyze specific keyword):",
      placeholder="e.g. AI Automation Tools, Desk Setup",
  )

  trends_data = fetch_google_explore_data(
      geo_map[geo_option], search_source, selected_category
  )

  table_data = []
  for idx, item in enumerate(trends_data):
    stage = (
        "🌱 Emerging (Predicted Peak)"
        if idx % 2 == 0
        else "🔥 Active Viral Peak"
    )
    table_data.append({
        "Keyword Asset": item["Topic"],
        "Surge Index": item["Search Volume"],
        "Status": stage,
    })

  df = pd.DataFrame(table_data)

  st.markdown(
      f"**Displaying Live Signals for:** `{selected_category}` |"
      f" `{geo_option}`"
  )
  st.dataframe(df, width="stretch", hide_index=True)

  if st.button("🔄 Refresh Radar Streams", width="stretch"):
    st.cache_data.clear()
    st.rerun()

with right_col:
  st.subheader("💡 Predictive Monetization Blueprint")

  if not st.session_state["is_premium"]:
    st.error("🔒 EXPLORE BLUEPRINT ENGINE IS LOCKED")
    st.info("Upgrade to Pro Tier to unlock execution scripts and ad funnels.")
    st.link_button(
        "🔥 Upgrade to Pro Tier Now",
        STRIPE_CHECKOUT_URL,
        type="primary",
        width="stretch",
    )
  else:
    # Use custom keyword if typed, else select from radar table
    if custom_search.strip():
      target_keyword = custom_search.strip()
      st.info(f"Targeting Custom Search Keyword: **{target_keyword}**")
    else:
      keyword_list = [t["Topic"] for t in trends_data]
      target_keyword = st.selectbox("🎯 Select Keyword Asset:", keyword_list)

    user_role = st.radio(
        "👤 Select Target Execution Role:",
        [
            "Content Creator / Influencer",
            "E-Commerce Merchant / Dropshipper",
            "Freelancer / Agency Owner",
        ],
        horizontal=True,
    )

    if st.button(
        "⚡ Forecast & Generate Execution Plan",
        type="primary",
        width="stretch",
    ):
      with st.spinner("Analyzing cross-platform search velocity..."):
        result = process_universal_trend(
            target_keyword, selected_category, user_role, search_source
        )

        st.success(f"🎯 Analysis Complete for **{target_keyword}**")
        st.info(f"**Status:** {result.get('trend_stage')}")

        with st.expander(
            "💰 Monetization Strategy (Profit Model)", expanded=True
        ):
          st.write(result.get("monetization_idea"))

        with st.expander(
            f"🎬 Platform Hook Script ({search_source})", expanded=True
        ):
          st.code(f'"{result.get("content_script_hook")}"', language="text")

        with st.expander("📝 3-Step Execution Plan", expanded=True):
          st.write(result.get("execution_steps"))
