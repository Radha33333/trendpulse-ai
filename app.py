import json
import xml.etree.ElementTree as ET
from groq import Groq
import pandas as pd
import plotly.express as px
import requests
import streamlit as st

# Page Config
st.set_page_config(
    page_title="TrendPulse AI - Commercial Signal Intelligence",
    page_icon="⚡",
    layout="wide",
)

GROQ_API_KEY = st.secrets.get("GROQ_API_KEY", "")
STRIPE_CHECKOUT_URL = "https://buy.stripe.com/test_demo"

# Dynamic Language Dictionary
TEXTS = {
    "English": {
        "title": "⚡ TrendPulse AI: Commercial Signal Intelligence",
        "subtitle": (
            "Predictive Trend Intelligence | Automated Creator & Merchant"
            " Execution"
        ),
        "terminal": "🔑 Enterprise Access Terminal",
        "simulate_pro": "Simulate Pro Subscription Access",
        "config_title": "🎛️ Signal Intelligence Configuration",
        "region": "🌍 Target Region:",
        "platform": "📱 Platform Source:",
        "category": "📁 Niche Category:",
        "velocity": "⏱️ Signal Velocity:",
        "apply_btn": "🚀 Apply Configuration & Update Radar",
        "telemetry_title": "📊 Live Telemetry & Growth Forecast",
        "custom_search": "🔍 Custom Asset Search (Optional):",
        "active_signals_for": "Active Signals for:",
        "filtered_asset": "Filtered Asset",
        "pred_velocity": "Predictive Velocity",
        "status": "Signal Status",
        "chart_title": "📈 Dynamic Velocity Forecast Curve",
        "matrix_title": "💡 Actionable Intelligence Matrix",
        "locked_title": "🔒 PREDICTIVE EXECUTION SUITE IS LOCKED",
        "locked_info": (
            "Unlock full profit blueprints, script hooks, audio vibes, and"
            " 30-sec execution plans."
        ),
        "upgrade_btn": "🔥 Upgrade to Pro Member Tier",
        "analyzing_custom": "Analyzing Custom Asset:",
        "select_asset": "🎯 Select Filtered Asset:",
        "operating_role": "👤 Operating Role:",
        "gen_blueprint": "⚡ Generate Master Blueprint",
        "monetization": "💰 Monetization & Profit Strategy",
        "hook": "🎬 High-Retention Visual Hook (Copy & Use)",
        "audio": "🎵 Recommended Audio Vibe",
        "caption": "📢 Ready-to-Use Caption / Ad Copy",
        "plan": "📝 Rapid Execution Plan",
    },
    "Hindi": {
        "title": "⚡ TrendPulse AI: कमर्शियल सिग्नल इंटेलिजेंस",
        "subtitle": (
            "प्रेडिक्टिव ट्रेंड इंटेलिजेंस | ऑटोमेटेड क्रिएटर और मर्चेंट"
            " एग्जीक्यूशन"
        ),
        "terminal": "🔑 एंटरप्राइज एक्सेस टर्मिनल",
        "simulate_pro": "प्रो सब्सक्रिप्शन एक्सेस सिमुलेट करें",
        "config_title": "🎛️ सिग्नल इंटेलिजेंस कॉन्फ़िगरेशन",
        "region": "🌍 टारगेट रीजन (क्षेत्र):",
        "platform": "📱 प्लेटफॉर्म सोर्स:",
        "category": "📁 नीश कैटेगरी:",
        "velocity": "⏱️ सिग्नल वेलोसिटी:",
        "apply_btn": "🚀 कॉन्फ़िगरेशन लागू करें और रडार अपडेट करें",
        "telemetry_title": "📊 लाइव टेलीमेट्री और ग्रोथ पूर्वानुमान",
        "custom_search": "🔍 कस्टम एसेट सर्च (वैकल्पिक):",
        "active_signals_for": "सक्रिय सिग्नल:",
        "filtered_asset": "फ़िल्टर किया गया एसेट",
        "pred_velocity": "अनुमानित गति (Velocity)",
        "status": "सिग्नल स्थिति",
        "chart_title": "📈 डायनेमिक वेलोसिटी फ़ोरकास्ट कर्व",
        "matrix_title": "💡 एक्शनएबल इंटेलिजेंस मैट्रिक्स",
        "locked_title": "🔒 प्रेडिक्टिव एग्जीक्यूशन सूट लॉक है",
        "locked_info": (
            "पूरे प्रॉफिट ब्लूप्रिंट, स्क्रिप्ट हुक, ऑडियो वाइब्स और 30-सेकंड"
            " प्लान अनलॉक करें।"
        ),
        "upgrade_btn": "🔥 प्रो मेंबर टियर में अपग्रेड करें",
        "analyzing_custom": "कस्टम एसेट का विश्लेषण:",
        "select_asset": "🎯 फ़िल्टर किया गया एसेट चुनें:",
        "operating_role": "👤 आपकी भूमिका (Role):",
        "gen_blueprint": "⚡ मास्टर ब्लूप्रिंट जनरेट करें",
        "monetization": "💰 मोनेटाइजेशन और प्रॉफिट रणनीति",
        "hook": "🎬 हाई-रिटेंशन विजुअल हुक (कॉपी और उपयोग करें)",
        "audio": "🎵 अनुशंसित ऑडियो वाइब",
        "caption": "📢 तैयार कैप्शन / एड कॉपी",
        "plan": "📝 त्वरित निष्पादन योजना (Execution Plan)",
    },
}

# Custom CSS
st.markdown(
    """

""",
    unsafe_allow_html=True,
)


# Fetch Signals Engine
@st.cache_data(ttl=300)
def fetch_filtered_radar_signals(region, platform_source, category, timeframe):
  url = f"https://trends.google.com/trending/rss?geo={region}"

  category_signals = {
      "E-Commerce": [
          "Micro-Fulfillment Logistics",
          "D2C Brand Growth Strategies",
          "Cross-Border Shipping Tech",
          "High-Converting Funnel Builders",
      ],
      "Physical Products": [
          "Ergonomic Desk Setup Gadgets",
          "Aesthetic RGB Light Bars",
          "Minimalist MagSafe Powerbanks",
          "Orthopedic Standing Mats",
      ],
      "Finance": [
          "Tax Planning Hacks 2026",
          "High-Yield Savings & Staking",
          "Personal Budgeting Automations",
          "Index Fund Investment Tips",
      ],
      "Business": [
          "Micro-SaaS Profit Models",
          "Zero-Investment Side Hustles",
          "B2B Lead Generation Automation",
          "Remote Team Operations",
      ],
      "Fitness": [
          "Smart Fitness Ring Trackers",
          "Posture Correction Wearables",
          "Home Gym Compact Equipment",
          "HIIT Workout Analytics",
      ],
      "Health & Lifestyle": [
          "Cold Plunge Therapy Tubs",
          "High Protein Clean Meal Plans",
          "Sleep Optimization Gadgets",
          "Mindfulness & Mental Wellness Apps",
      ],
      "👗 Fashion & Apparel": [
          "Y2K Vintage Streetwear",
          "Minimalist Capsule Wardrobe",
          "Sustainable Eco-Friendly Fabrics",
          "Oversized Aesthetic Hoodies",
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


def generate_master_intelligence(
    keyword_asset,
    category,
    target_role,
    platform,
    timeframe,
    velocity_score,
    lang,
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
    Analyze Keyword Asset: '{keyword_asset}' | Category: '{category}' | Role: '{target_role}' | Platform: '{platform}' | Timeframe: '{timeframe}' | Velocity Score: {velocity_score}%
    Language to respond in: {lang}
    Generate an execution blueprint. Return STRICT JSON:
    {{
      "viral_score": "{velocity_score}%",
      "prediction_window": "Specific lifecycle window based on {timeframe}",
      "profit_model": "Monetization strategy for {target_role}",
      "execution_hook": "High-retention 3-second hook for {platform}",
      "audio_suggestion": "Recommended viral audio vibe",
      "ad_copy": "High-converting caption/ad copy text",
      "action_blueprint": "3-step execution plan"
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

# TOP BAR: Title Header & Clean Language Switcher Positioned at Top Right
head_col1, head_col2 = st.columns([3, 1])

with head_col2:
  selected_lang = st.selectbox(
      "🌐 Language / भाषा:", ["English", "Hindi"], index=0
  )

t = TEXTS[selected_lang]

with head_col1:
  st.title(t["title"])
  st.caption(t["subtitle"])

st.markdown("---")

with st.expander(t["terminal"]):
  st.session_state["is_premium"] = st.checkbox(
      t["simulate_pro"], value=st.session_state["is_premium"]
  )

# Signal Intelligence Configuration Form
st.markdown(f"### {t['config_title']}")

with st.form(key="filter_form"):
  f_col1, f_col2, f_col3, f_col4 = st.columns(4)

  with f_col1:
    geo_option = st.selectbox(
        t["region"],
        [
            "India (IN)",
            "United States (US)",
            "United Kingdom (GB)",
            "Global (ALL)",
        ],
    )
    geo_map = {
        "India (IN)": "IN",
        "United States (US)": "US",
        "United Kingdom (GB)": "GB",
        "Global (ALL)": "US",
    }

  with f_col2:
    platform_source = st.selectbox(
        t["platform"],
        [
            "Social Video & Reels",
            "TikTok & Instagram Reels",
            "Search Engine Intent",
            "E-Commerce Shopping",
        ],
    )

  with f_col3:
    selected_category = st.selectbox(
        t["category"],
        [
            "E-Commerce",
            "Physical Products",
            "Finance",
            "Business",
            "Fitness",
            "Health & Lifestyle",
            "👗 Fashion & Apparel",
            "Tech, AI & Software",
            "Entertainment & Viral Pop Culture",
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
        t["velocity"],
        [
            "Realtime Spike (24h)",
            "Short-Term Trend (7 Days)",
            "Viral Surge (3-7 Days)",
            "Macro Trend (30 Days)",
        ],
    )

  apply_filters = st.form_submit_button(
      t["apply_btn"], use_container_width=True
  )

st.markdown("---")

left_col, right_col = st.columns([1, 1], gap="large")

with left_col:
  st.subheader(t["telemetry_title"])

  custom_search = st.text_input(
      t["custom_search"],
      placeholder="e.g. Ergonomic Keyboard, AI Content Generator",
  )

  # Fetch data based on applied filter inputs
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
        t["filtered_asset"]: item["Keyword"],
        t["pred_velocity"]: f"{score}%",
        t["status"]: stage,
    })
    signal_scores[item["Keyword"]] = score

  df = pd.DataFrame(table_data)
  st.markdown(
      f"**{t['active_signals_for']}** `{selected_category}` |"
      f" `{platform_source}` | `{geo_option}`"
  )
  st.dataframe(df, width="stretch", hide_index=True)

  # Dynamic Chart
  st.markdown(f"#### {t['chart_title']}")

  if custom_search.strip():
    chart_keyword = custom_search.strip()
    base_score = 95.0
  else:
    chart_keyword = active_signals[0]["Keyword"] if active_signals else "Asset"
    base_score = signal_scores.get(chart_keyword, 90.0)

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
      title=f"7-Day Forecast: {chart_keyword[:30]}...",
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

with right_col:
  st.subheader(t["matrix_title"])

  if not st.session_state["is_premium"]:
    st.error(t["locked_title"])
    st.info(t["locked_info"])
    st.link_button(
        t["upgrade_btn"],
        STRIPE_CHECKOUT_URL,
        type="primary",
        width="stretch",
    )
  else:
    if custom_search.strip():
      target_keyword = custom_search.strip()
      target_score = 95.0
      st.info(f"{t['analyzing_custom']} **{target_keyword}**")
    else:
      keyword_list = [t["Keyword"] for t in active_signals]
      target_keyword = st.selectbox(t["select_asset"], keyword_list)
      target_score = signal_scores.get(target_keyword, 92.0)

    user_role = st.radio(
        t["operating_role"],
        [
            "Content Creator / Influencer",
            "E-Commerce Merchant / Dropshipper",
            "Agency Owner / Freelancer",
        ],
        horizontal=True,
    )

    if st.button(t["gen_blueprint"], type="primary", width="stretch"):
      with st.spinner("Processing fully synchronized signal matrices..."):
        result = generate_master_intelligence(
            target_keyword,
            selected_category,
            user_role,
            platform_source,
            timeframe,
            target_score,
            selected_lang,
        )

        st.success(f"🎯 Complete Intelligence Blueprint: **{target_keyword}**")

        col_m1, col_m2 = st.columns(2)
        with col_m1:
          st.metric(
              label="Predictive Viral Score", value=result.get("viral_score")
          )
        with col_m2:
          st.info(f"**Timeline:** {result.get('prediction_window')}")

        with st.expander(t["monetization"], expanded=True):
          st.write(result.get("profit_model"))

        with st.expander(t["hook"], expanded=True):
          st.code(f'"{result.get("execution_hook")}"', language="text")

        with st.expander(t["audio"], expanded=True):
          st.write(f"🔊 **Audio Suggestion:** {result.get('audio_suggestion')}")

        with st.expander(t["caption"], expanded=True):
          st.code(f"{result.get('ad_copy')}", language="text")

        with st.expander(t["plan"], expanded=True):
          st.write(result.get("action_blueprint"))
