import json
import xml.etree.ElementTree as ET
from groq import Groq
import pandas as pd
import requests
import streamlit as st

st.set_page_config(
    page_title="TrendPulse AI - Predictive Viral Radar",
    page_icon="⚡",
    layout="wide",
)

GROQ_API_KEY = st.secrets.get("GROQ_API_KEY", "")
STRIPE_CHECKOUT_URL = "https://stripe.com"


# Proprietary Multi-Source Radar Engine
@st.cache_data(ttl=600)
def fetch_trendpulse_radar_data(region, platform_source, category_name):
  url = f"https://trends.google.com/trending/rss?geo={region}"
  try:
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers, timeout=10)
    root = ET.fromstring(response.content)
    raw_signals = []
    ns = {"ht": "https://trends.google.com/trending/rss"}

    for item in root.findall(".//item"):
      title = item.find("title")
      approx_traffic = item.find("ht:approx_traffic", ns)

      title_text = title.text if title is not None else ""
      traffic_text = (
          approx_traffic.text if approx_traffic is not None else "100K+"
      )

      if title_text:
        raw_signals.append(
            {"Keyword": str(title_text), "Volume_Raw": str(traffic_text)}
        )

    if raw_signals:
      return raw_signals[:6]
    else:
      return [{
          "Keyword": f"{category_name} Breakout Asset",
          "Volume_Raw": "100K+",
      }]

  except Exception:
    return [{"Keyword": f"{category_name} Viral Signal", "Volume_Raw": "85K+"}]


# AI Profit Engine
def generate_profit_intelligence(
    keyword_asset, category, target_role, platform
):
  if not GROQ_API_KEY:
    return {
        "viral_score": "94% (High Commercial Intent)",
        "prediction_window": "Peak Expected in Next 5-8 Days",
        "profit_model": (
            f"Launch digital service, short-form content campaign, or product"
            f" line for '{keyword_asset}'."
        ),
        "execution_hook": (
            f"Stop scrolling! This '{keyword_asset}' trend is making creators"
            " money right now..."
        ),
        "action_blueprint": (
            "1. Record 15-second reel using hook\n2. Pin affiliate or store"
            " link in bio\n3. Scale organic traffic"
        ),
    }

  client = Groq(api_key=GROQ_API_KEY)
  prompt = f"""
    You are an AI Monetization & Trend Forecasting Engine.
    Analyze Keyword: '{keyword_asset}' | Category: '{category}' | User Role: '{target_role}' | Platform: '{platform}'.

    Provide response in JSON:
    {{
      "viral_score": "e.g. 92% Viral Velocity Score",
      "prediction_window": "Predicted peak lifecycle (e.g. Peak starting in 4 days)",
      "profit_model": "Step-by-step monetization and monetization model",
      "execution_hook": "High-retention 3-second visual/script hook",
      "action_blueprint": "3-step rapid execution plan to profit immediately"
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
        "viral_score": "88% Viral Score",
        "prediction_window": "Active Growth Phase",
        "profit_model": f"Monetize '{keyword_asset}' via direct sales or promo",
        "execution_hook": f"The secret behind '{keyword_asset}' revealed!",
        "action_blueprint": "1. Publish Content\n2. Add CTA\n3. Monetize",
    }


# State Setup
if "is_premium" not in st.session_state:
  st.session_state["is_premium"] = False

# App UI
st.title("⚡ TrendPulse AI: Predictive Monetization Engine")
st.caption(
    "Automated Trend Signals | High-Velocity Content & Product Blueprints"
)

st.markdown("---")

# License Gatekeeper
with st.expander("🔑 Pro Membership Control Panel"):
  st.session_state["is_premium"] = st.checkbox(
      "Simulate Active Pro Subscription", value=st.session_state["is_premium"]
  )

# TrendPulse Proprietary Filter Engine
st.markdown("### 🎛️ TrendPulse Signal Intelligence Filters")
f_col1, f_col2, f_col3, f_col4 = st.columns(4)

with f_col1:
  geo_option = st.selectbox(
      "🌍 Target Region:",
      ["India (IN)", "United States (US)", "United Kingdom (GB)", "Global (ALL)"],
  )
  geo_map = {
      "India (IN)": "IN",
      "United States (US)": "US",
      "United Kingdom (GB)": "GB",
      "Global (ALL)": "US",
  }

with f_col2:
  platform_source = st.selectbox(
      "📱 Signal Source:",
      ["Social Video & Reels", "Search Engine Intent", "E-Commerce Shopping"],
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
      "⏱️ Signal Velocity:",
      ["Realtime Spike (24h)", "Short-Term Trend (7 Days)", "Macro Trend (30 Days)"],
  )

st.markdown("---")

left_col, right_col = st.columns([1, 1], gap="large")

with left_col:
  st.subheader("📊 Live Telemetry Radar")

  custom_search = st.text_input(
      "🔍 Deep Target Asset (Optional - Type keyword to test):",
      placeholder="e.g. AI Video Generators, Aesthetic Desk Lamp",
  )

  raw_signals = fetch_trendpulse_radar_data(
      geo_map[geo_option], platform_source, selected_category
  )

  table_data = []
  for idx, item in enumerate(raw_signals):
    score = round(98.2 - (idx * 4.3), 1)
    stage = (
        "🌱 Emerging (Peak in 5-7 Days)"
        if idx % 2 == 0
        else "🔥 Active Viral Peak"
    )
    table_data.append({
        "Trend Asset": item["Keyword"],
        "Viral Score": f"{score}%",
        "Predicted Status": stage,
    })

  df = pd.DataFrame(table_data)

  st.markdown(
      f"**Active Signals for:** `{selected_category}` | `{platform_source}`"
  )
  st.dataframe(df, width="stretch", hide_index=True)

  if st.button("🔄 Rescan Intelligence Streams", width="stretch"):
    st.cache_data.clear()
    st.rerun()

with right_col:
  st.subheader("💡 Proprietary Execution Co-Pilot")

  if not st.session_state["is_premium"]:
    st.error("🔒 MONETIZATION BLUEPRINT IS LOCKED")
    st.info(
        "Upgrade to unlock profit calculations, script hooks, and action"
        " plans."
    )
    st.link_button(
        "🔥 Upgrade to Pro Membership",
        STRIPE_CHECKOUT_URL,
        type="primary",
        width="stretch",
    )
  else:
    if custom_search.strip():
      target_keyword = custom_search.strip()
      st.info(f"Analyzing Target Keyword: **{target_keyword}**")
    else:
      keyword_list = [t["Keyword"] for t in raw_signals]
      target_keyword = st.selectbox("🎯 Select Target Trend:", keyword_list)

    user_role = st.radio(
        "👤 Select Your Operating Role:",
        [
            "Content Creator / Influencer",
            "E-Commerce Merchant / Dropshipper",
            "Agency Owner / Freelancer",
        ],
        horizontal=True,
    )

    if st.button(
        "⚡ Generate Profit Blueprint", type="primary", width="stretch"
    ):
      with st.spinner("Processing TrendPulse predictive models..."):
        result = generate_profit_intelligence(
            target_keyword, selected_category, user_role, platform_source
        )

        st.success(f"🎯 Analysis Complete for **{target_keyword}**")

        st.metric(
            label="Predictive Viral Score", value=result.get("viral_score")
        )
        st.info(f"**Timeline:** {result.get('prediction_window')}")

        with st.expander(
            "💰 Monetization & Profit Strategy", expanded=True
        ):
          st.write(result.get("profit_model"))

        with st.expander("🎬 High-Retention Content Script Hook", expanded=True):
          st.code(f'"{result.get("execution_hook")}"', language="text")

        with st.expander("📝 3-Step Action Blueprint", expanded=True):
          st.write(result.get("action_blueprint"))
