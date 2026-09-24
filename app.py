import json
import xml.etree.ElementTree as ET
from groq import Groq
import numpy as np
import pandas as pd
import plotly.express as px
import requests
import streamlit as st

# 1. Page & Layout Configuration
st.set_page_config(
    page_title="TrendPulse AI - Commercial Signal Intelligence",
    page_icon="⚡",
    layout="wide",
)

# Secrets & Constants
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY", "")
STRIPE_CHECKOUT_URL = "https://buy.stripe.com/test_demo"

# Custom Styling
st.markdown(
    """

""",
    unsafe_allow_html=True,
)


# 2. Dynamic Signal Radar Engine
@st.cache_data(ttl=300)
def fetch_filtered_radar_signals(region, platform_source, category, timeframe):
  """Fetches live trends combined with comprehensive category keywords."""
  url = f"https://trends.google.com/trending/rss?geo={region}"

  category_signals = {
      "E-Commerce & Physical Products": [
          "Ergonomic Desk Setup Gadgets",
          "Aesthetic RGB Light Bars",
          "Minimalist MagSafe Powerbanks",
          "Orthopedic Standing Mats",
      ],
      "Tech, AI & Software": [
          "Open Source AI Video Generators",
          "Automated Workflow Agents",
          "Local Privacy LLM Models",
          "Developer Productivity Extension",
      ],
      "Entertainment & Viral Pop Culture": [
          "Trending Cinematic Reel Audio",
          "Viral Meme Reaction Formats",
          "Short-Form Anime Breakdown",
          "Celebrity Style Breakdown",
      ],
      "Finance, Business & Crypto": [
          "Tax Planning Hacks 2026",
          "Micro-SaaS Profit Models",
          "High-Yield Crypto Staking",
          "Zero-Investment Side Hustles",
      ],
      "Fitness, Health & Lifestyle": [
          "Cold Plunge Therapy Tubs",
          "High Protein Clean Meal Plans",
          "Smart Fitness Ring Trackers",
          "Posture Correction Wearables",
      ],
      "🤖 Generative AI & Automation Tools": [
          "Custom GPT Workflow Agents",
          "Voice Cloning CapCut Template",
          "Open-Source Video Generators",
          "Autonomous Coding Bots",
      ],
      "🛍️ TikTok Made Me Buy It (Viral Products)": [
          "Aesthetic RGB Light Bar",
          "Compact MagSafe Powerbank",
          "Orthopedic Standing Mat",
          "Viral Cold Plunge Tub",
      ],
      "🎮 Gaming, Esports & Streaming Culture": [
          "In-Game Asset Marketplace",
          "Stream Setup Micro-Gadgets",
          "Viral Gaming Clip Overlay",
          "Handheld Retro Console",
      ],
      "💼 Micro-SaaS & Solopreneurship": [
          "Notion Aesthetic Planner Template",
          "Framer Portfolio Kit",
          "Zero-Code Automation Pipeline",
          "Micro-SaaS Starter Kit",
      ],
      "🌱 Biohacking, Wellness & Longevity": [
          "Smart Fitness Ring Tracker",
          "Red Light Therapy Panel",
          "Clean Protein Meal Plan",
          "Posture Correction Wearable",
      ],
      "🎨 Digital Assets, UGC & Templates": [
          "Lightroom Cinematic Presets",
          "CapCut Viral Audio Transition",
          "Aesthetic Reel Cover Pack",
          "AI Avatar Asset Pack",
      ],
      "🐕 Pet Tech & Premium Care": [
          "GPS Pet Tracker Collar",
          "Automatic Smart Pet Feeder",
          "Viral Pet Bath Attachment",
          "Specialty Organic Dog Treats",
      ],
  }

  raw_signals = []
  try:
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers, timeout=5)
    if response.status_code == 200:
      root = ET.fromstring(response.content)
      ns = {"ht": "https://trends.google.com/trending/rss"}
      for item in root.findall(".//item")[:4]:
        title = item.find("title")
        traffic = item.find("ht:approx_traffic", ns)
        if title is not None:
          raw_signals.append({
              "Keyword": f"{title.text} ({platform_source})",
              "Volume": (
                  traffic.text if traffic is not None else "100K+ Queries"
              ),
          })
  except Exception:
    pass

  default_keywords = category_signals.get(
      category, ["Trending Breakout Asset"]
  )
  combined = []

  for kw in default_keywords:
    combined.append({
        "Keyword": f"{kw} [{platform_source}]",
        "Volume": f"150K+ ({timeframe})",
    })

  for item in raw_signals:
    combined.append({"Keyword": item["Keyword"], "Volume": item["Volume"]})

  return combined[:5]


# 3. Synchronized AI Intelligence Engine
def generate_master_intelligence(
    keyword_asset, category, target_role, platform, timeframe, velocity_score
):
  if not GROQ_API_KEY:
    return {
        "viral_score": f"{velocity_score}%",
        "prediction_window": (
            f"Peak active on {platform} over {timeframe} window"
        ),
        "profit_model": (
            f"Capitalize on '{keyword_asset}' under {category} using targeted"
            f" {target_role} monetization workflows."
        ),
        "execution_hook": (
            f"Stop scrolling! Here is how '{keyword_asset}' is trending on"
            f" {platform}..."
        ),
        "audio_suggestion": "Trending Low-Fi Beats / High-Energy Phonk Track",
        "ad_copy": (
            f"Get instant access to top-rated '{keyword_asset}' solutions"
            " today!"
        ),
        "action_blueprint": (
            "1. Launch targeted content using keyword hook\n2. Integrate"
            " recommended audio vibe\n3. Direct audience to monetized CTA"
        ),
  }

  client = Groq(api_key=GROQ_API_KEY)
  prompt = f"""
    Analyze Keyword Asset: '{keyword_asset}'
    Category: '{category}'
    Target Operating Role: '{target_role}'
    Platform Source: '{platform}'
    Timeframe Horizon: '{timeframe}'
    Current Mathematical Velocity Score: {velocity_score}%

    Generate an execution blueprint. Return STRICT JSON with these keys:
    {{
      "viral_score": "{velocity_score}%",
      "prediction_window": "Specific lifecycle window based on {timeframe}",
      "profit_model": "Tailored monetization strategy for {target_role}",
      "execution_hook": "High-retention 3-second hook for {platform}",
      "audio_suggestion": "Recommended viral audio vibe or genre",
      "ad_copy": "High-converting caption or ad copy text",
      "action_blueprint": "Clear 3-step action plan"
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
        "viral_score": f"{velocity_score}%",
        "prediction_window": f"Active Growth Phase ({timeframe})",
        "profit_model": f"Monetize '{keyword_asset}' immediately.",
        "execution_hook": f"Secret strategy for '{keyword_asset}'!",
        "audio_suggestion": "Trending High-Tempo Track",
        "ad_copy": f"Check out '{keyword_asset}' now!",
        "action_blueprint": "1. Post Content\n2. Add CTA\n3. Monetize",
    }


# Session State Initialization
if "is_premium" not in st.session_state:
  st.session_state["is_premium"] = False

# Application Header
st.title("⚡ TrendPulse AI: Commercial Signal Intelligence")
st.caption(
    "Predictive Trend Intelligence | Automated Creator & Merchant Execution"
)

st.markdown("---")

with st.expander("🔑 Enterprise Access Terminal"):
  st.session_state["is_premium"] = st.checkbox(
      "Simulate Pro Subscription Access", value=st.session_state["is_premium"]
  )

# Signal Intelligence Filters Setup
st.markdown("### 🎛️ Signal Intelligence Configuration")
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
      "📱 Platform Source:",
      [
          "Social Video & Reels",
          "TikTok & Instagram Reels",
          "Search Engine Intent",
          "E-Commerce Shopping",
      ],
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
          "🤖 Generative AI & Automation Tools",
          "🛍️ TikTok Made Me Buy It (Viral Products)",
          "🎮 Gaming, Esports & Streaming Culture",
          "💼 Micro-SaaS & Solopreneurship",
          "🌱 Biohacking, Wellness & Longevity",
          "🎨 Digital Assets, UGC & Templates",
          "🐕 Pet Tech & Premium Care",
      ],
  )

with f_col4:
  timeframe = st.selectbox(
      "⏱️ Signal Velocity:",
      [
          "Realtime Spike (24h)",
          "Short-Term Trend (7 Days)",
          "Viral Surge (3-7 Days)",
          "Macro Trend (30 Days)",
      ],
  )

st.markdown("---")

left_col, right_col = st.columns([1, 1], gap="large")

# Left Column: Telemetry & Dynamic Visualization
with left_col:
  st.subheader("📊 Live Telemetry & Growth Forecast")

  custom_search = st.text_input(
      "🔍 Custom Asset Search (Optional):",
      placeholder="e.g. Ergonomic Keyboard, AI Content Generator",
  )

  # Fetch Signals with all filters included
  active_signals = fetch_filtered_radar_signals(
      geo_map[geo_option], platform_source, selected_category, timeframe
  )

  table_data = []
  signal_scores = {}
  for idx, item in enumerate(active_signals):
    score = round(98.8 - (idx * 3.2), 1)
    stage = (
        "🌱 Emerging (Peak Pending)"
        if idx % 2 == 0
        else "🔥 Active Viral Peak"
    )
    table_data.append({
        "Filtered Asset": item["Keyword"],
        "Predictive Velocity": f"{score}%",
        "Signal Status": stage,
    })
    signal_scores[item["Keyword"]] = score

  df = pd.DataFrame(table_data)
  st.markdown(
      f"**Active Signals for:** `{selected_category}` | `{platform_source}` |"
      f" `{geo_option}`"
  )
  st.dataframe(df, width="stretch", hide_index=True)

  # Dynamic Chart Generation Linked directly to Asset
  st.markdown("#### 📈 Dynamic Velocity Forecast Curve")

  if custom_search.strip():
    chart_keyword = custom_search.strip()
    base_score = 95.0
  else:
    chart_keyword = active_signals[0]["Keyword"] if active_signals else "Asset"
    base_score = signal_scores.get(chart_keyword, 90.0)

  # Generate synchronized trend curve based on calculated velocity score
  days = ["Day 1", "Day 2", "Day 3", "Day 4", "Day 5", "Day 6", "Day 7"]
  multiplier = base_score / 100.0
  velocity_values = [
      int(20 * multiplier),
      int(45 * multiplier),
      int(75 * multiplier),
      int(100 * multiplier),
      int(92 * multiplier),
      int(80 * multiplier),
      int(65 * multiplier),
  ]

  fig_df = pd.DataFrame({"Day": days, "Search Velocity": velocity_values})
  fig = px.line(
      fig_df,
      x="Day",
      y="Search Velocity",
      title=f"7-Day Forecast Horizon: {chart_keyword[:30]}...",
      markers=True,
  )
  fig.update_traces(line_color="#ff4b4b", line_width=3)
  fig.update_layout(
      margin=dict(l=20, r=20, t=40, b=20),
      height=280,
      paper_bgcolor="rgba(0,0,0,0)",
      plot_bgcolor="rgba(0,0,0,0)",
      font=dict(color="white"),
  )
  st.plotly_chart(fig, use_container_width=True)

  if st.button("🔄 Rescan Intelligence Streams", width="stretch"):
    st.cache_data.clear()
    st.rerun()

# Right Column: Actionable Intelligence Matrix
with right_col:
  st.subheader("💡 Actionable Intelligence Matrix")

  if not st.session_state["is_premium"]:
    st.error("🔒 PREDICTIVE EXECUTION SUITE IS LOCKED")
    st.info(
        "Unlock full profit blueprints, script hooks, audio vibes, and 30-sec"
        " execution plans."
    )
    st.link_button(
        "🔥 Upgrade to Pro Member Tier",
        STRIPE_CHECKOUT_URL,
        type="primary",
        width="stretch",
    )
  else:
    if custom_search.strip():
      target_keyword = custom_search.strip()
      target_score = 95.0
      st.info(f"Analyzing Custom Asset: **{target_keyword}**")
    else:
      keyword_list = [t["Keyword"] for t in active_signals]
      target_keyword = st.selectbox("🎯 Select Filtered Asset:", keyword_list)
      target_score = signal_scores.get(target_keyword, 92.0)

    user_role = st.radio(
        "👤 Operating Role:",
        [
            "Content Creator / Influencer",
            "E-Commerce Merchant / Dropshipper",
            "Agency Owner / Freelancer",
        ],
        horizontal=True,
    )

    if st.button(
        "⚡ Generate Master Blueprint", type="primary", width="stretch"
    ):
      with st.spinner("Processing fully synchronized signal matrices..."):
        result = generate_master_intelligence(
            target_keyword,
            selected_category,
            user_role,
            platform_source,
            timeframe,
            target_score,
        )

        st.success(f"🎯 Complete Intelligence Blueprint: **{target_keyword}**")

        col_m1, col_m2 = st.columns(2)
        with col_m1:
          st.metric(
              label="Predictive Viral Score", value=result.get("viral_score")
          )
        with col_m2:
          st.info(f"**Timeline:** {result.get('prediction_window')}")

        with st.expander(
            "💰 Monetization & Profit Strategy", expanded=True
        ):
          st.write(result.get("profit_model"))

        with st.expander(
            "🎬 High-Retention Visual Hook (Copy & Use)", expanded=True
        ):
          st.code(f'"{result.get("execution_hook")}"', language="text")

        with st.expander("🎵 Recommended Audio Vibe", expanded=True):
          st.write(f"🔊 **Audio Suggestion:** {result.get('audio_suggestion')}")

        with st.expander("📢 Ready-to-Use Caption / Ad Copy", expanded=True):
          st.code(f"{result.get('ad_copy')}", language="text")

        with st.expander("📝 Rapid Execution Plan", expanded=True):
          st.write(result.get("action_blueprint"))
