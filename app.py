import json
import xml.etree.ElementTree as ET
from groq import Groq
import pandas as pd
import requests
import streamlit as st

st.set_page_config(
    page_title="TrendPulse AI - Commercial & GenZ Signal Intelligence",
    page_icon="⚡",
    layout="wide",
)

GROQ_API_KEY = st.secrets.get("GROQ_API_KEY", "")
STRIPE_CHECKOUT_URL = "https://buy.stripe.com/test_demo"

# Custom Styling for GenZ Dark Vibe & Clean UI
st.markdown(
    """

""",
    unsafe_allow_html=True,
)


# Filter-linked Dynamic Intelligence Engine
@st.cache_data(ttl=300)
def fetch_filtered_radar_signals(region, platform_source, category):
  url = f"https://trends.google.com/trending/rss?geo={region}"

  category_signals = {
      "🤖 Generative AI & Automation Tools": [
          "Custom GPT Workflow Agents",
          "Open-Source AI Video Generator",
          "Voice Cloning CapCut Template",
          "Local Privacy LLM Setup",
      ],
      "🛍️ TikTok Made Me Buy It (Viral Products)": [
          "Aesthetic RGB Desk Light Bar",
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
          "Micro-Saas Starter Kit",
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
      for item in root.findall(".//item")[:3]:
        title = item.find("title")
        traffic = item.find("ht:approx_traffic", ns)
        if title is not None:
          raw_signals.append({
              "Keyword": f"{title.text} ({platform_source})",
              "Volume": (
                  traffic.text if traffic is not None else "100K+"
              ),
          })
  except Exception:
    pass

  default_keywords = category_signals.get(
      category, ["Viral Breakout Asset"]
  )
  combined = []

  for kw in default_keywords:
    combined.append({
        "Keyword": f"{kw} [{platform_source}]",
        "Volume": "250K+ GenZ Surge",
    })

  for item in raw_signals:
    combined.append({"Keyword": item["Keyword"], "Volume": item["Volume"]})

  return combined[:5]


def generate_master_intelligence(
    keyword_asset, category, target_role, platform
):
  if not GROQ_API_KEY:
    return {
        "viral_score": "98.2% (High GenZ Retention)",
        "prediction_window": f"Peak active on {platform} in Next 48 Hours",
        "profit_model": (
            f"Launch quick organic campaign for '{keyword_asset}' under"
            f" {category}. Monetize via bio link or affiliate."
        ),
        "execution_hook": (
            f"Stop scrolling! If you are not using '{keyword_asset}' on"
            f" {platform}, you are missing out..."
        ),
        "audio_suggestion": "Trending Slowed + Reverb Lo-Fi Beats",
        "ad_copy": (
            f"Get instant access to '{keyword_asset}'. Tap the link below before"
            " it goes out of stock!"
        ),
        "action_blueprint": (
            "1. Record 7-sec short video using hook\n2. Add suggested trending"
            " audio\n3. Pin affiliate link in bio"
        ),
    }

  client = Groq(api_key=GROQ_API_KEY)
  prompt = f"""
    Analyze Keyword: '{keyword_asset}' | Category: '{category}' | Role: '{target_role}' | Platform: '{platform}'.
    Provide response tailored for GenZ Creators & Dropshippers. Output strict JSON with keys:
    {{
      "viral_score": "e.g. 97.5%",
      "prediction_window": "Short lifecycle window e.g. Peak in Next 48-72 Hours",
      "profit_model": "Instant monetization strategy",
      "execution_hook": "High-retention 3-second hook for Short Video/Reels",
      "audio_suggestion": "Recommended trending audio genre or style",
      "ad_copy": "Direct converting caption/ad text",
      "action_blueprint": "3-step 30-second execution plan"
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
        "viral_score": "92.0%",
        "prediction_window": "Active GenZ Surge Phase",
        "profit_model": f"Monetize '{keyword_asset}' immediately.",
        "execution_hook": f"The secret hack behind '{keyword_asset}'!",
        "audio_suggestion": "Popular High-Tempo Phonk Track",
        "ad_copy": f"Check out '{keyword_asset}' now!",
        "action_blueprint": "1. Post Short Reel\n2. Add CTA\n3. Monetize Link",
    }


# Initialize Session State for Premium Access
if "is_premium" not in st.session_state:
  st.session_state["is_premium"] = False

# App UI Header
st.title("⚡ TrendPulse AI: Viral Radar & Rapid Execution")
st.caption(
    "Automated Trend Signals | 30-Second Creator & E-Commerce Execution Engine"
)

st.markdown("---")

# Pro Control Panel Gatekeeper
with st.expander("🔑 Pro & Creator Access Terminal"):
  st.session_state["is_premium"] = st.checkbox(
      "Simulate Active Subscription Access",
      value=st.session_state["is_premium"],
  )

# Extended GenZ & High-Converting Signal Configuration
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
          "TikTok & Instagram Reels",
          "YouTube Shorts Velocity",
          "E-Commerce & Social Shopping",
      ],
  )

with f_col3:
  selected_category = st.selectbox(
      "📁 Viral Niche Category:",
      [
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
      "⏱️ Velocity Window:",
      ["Realtime Spike (24h)", "Viral Surge (3-7 Days)", "Macro Trend (30 Days)"],
  )

st.markdown("---")

left_col, right_col = st.columns([1, 1], gap="large")

with left_col:
  st.subheader("📊 Live Telemetry & Growth Projection")

  custom_search = st.text_input(
      "🔍 Deep Target Asset (Optional):",
      placeholder="e.g. CapCut AI Template, Mini Projector",
  )

  # Fetch data based on active filter selections
  active_signals = fetch_filtered_radar_signals(
      geo_map[geo_option], platform_source, selected_category
  )

  table_data = []
  for idx, item in enumerate(active_signals):
    score = round(99.1 - (idx * 2.8), 1)
    stage = (
        "🌱 Emerging (Peak Pending)"
        if idx % 2 == 0
        else "🔥 Active Viral Surge"
    )
    table_data.append({
        "Asset Target": item["Keyword"],
        "Predictive Velocity": f"{score}%",
        "Status": stage,
    })

  df = pd.DataFrame(table_data)
  st.markdown(
      f"**Active Signals:** `{selected_category}` | `{platform_source}`"
  )
  st.dataframe(df, width="stretch", hide_index=True)

  st.markdown("#### 📈 Projected 7-Day Growth Curve")
  chart_data = pd.DataFrame({
      "Day": ["Day 1", "Day 2", "Day 3", "Day 4", "Day 5", "Day 6", "Day 7"],
      "Virality Score": [35, 55, 88, 100, 95, 80, 65],
  }).set_index("Day")

  st.line_chart(chart_data)

  if st.button("🔄 Rescan Intelligence Streams", width="stretch"):
    st.cache_data.clear()
    st.rerun()

with right_col:
  st.subheader("💡 30-Second Execution Co-Pilot")

  if not st.session_state["is_premium"]:
    st.error("🔒 PREDICTIVE SUITE IS LOCKED")
    st.info(
        "Unlock full profit blueprints, script hooks, ad copies, and 30-sec"
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
      st.info(f"Analyzing Target Keyword: **{target_keyword}**")
    else:
      keyword_list = [t["Keyword"] for t in active_signals]
      target_keyword = st.selectbox("🎯 Select Target Keyword:", keyword_list)

    user_role = st.radio(
        "👤 Operating Role:",
        [
            "GenZ Content Creator",
            "E-Commerce / Dropshipper",
            "Agency Owner / Freelancer",
        ],
        horizontal=True,
    )

    if st.button(
        "⚡ Generate 30-Sec Action Blueprint", type="primary", width="stretch"
    ):
      with st.spinner("Processing viral execution matrix..."):
        result = generate_master_intelligence(
            target_keyword, selected_category, user_role, platform_source
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
            "💰 Monetization & Profit Blueprint", expanded=True
        ):
          st.write(result.get("profit_model"))

        with st.expander(
            "🎬 High-Retention Script Hook (Copy & Use)", expanded=True
        ):
          st.code(f'"{result.get("execution_hook")}"', language="text")

        with st.expander("🎵 Recommended Audio Vibe", expanded=True):
          st.write(f"🔊 **Audio Suggestion:** {result.get('audio_suggestion')}")

        with st.expander("📢 Ready-to-Use Caption / Ad Copy", expanded=True):
          st.code(f"{result.get('ad_copy')}", language="text")

        with st.expander("📝 30-Second Rapid Execution Plan", expanded=True):
          st.write(result.get("action_blueprint"))
