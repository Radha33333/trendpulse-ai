import json
import xml.etree.ElementTree as ET
from groq import Groq
import pandas as pd
import plotly.express as px
import requests
import streamlit as st

# Page Config
st.set_page_config(
    page_title="TrendPulse AI - Revenue Signal Intelligence",
    page_icon="⚡",
    layout="wide",
)

GROQ_API_KEY = st.secrets.get("GROQ_API_KEY", "")
STRIPE_CHECKOUT_URL = "https://buy.stripe.com/test_demo"

# Dynamic Language Dictionary with Income & ROI Terminology
TEXTS = {
    "English": {
        "title": "⚡ TrendPulse AI: Commercial Signal Intelligence",
        "subtitle": (
            "Predictive Trend Intelligence | Automated Creator & Merchant"
            " Revenue Multiplier"
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
        "filtered_asset": "Filtered Trend Asset",
        "est_revenue": "Est. Revenue Opportunity",
        "saturation": "Saturation Window",
        "status": "Signal Status",
        "chart_title": "📈 Dynamic Velocity & Demand Forecast Curve",
        "matrix_title": "💡 Actionable Intelligence & Income Blueprint Matrix",
        "locked_title": "🔒 MULTI-CHANNEL REVENUE BLUEPRINT IS LOCKED",
        "locked_info": (
            "Unlock high-converting scripts, viral hooks, monetized ad copy,"
            " and step-by-step 10x ROI execution plan."
        ),
        "upgrade_btn": "🔥 Upgrade to Pro & Unlock Revenue Engine",
        "analyzing_custom": "Analyzing Revenue Potential for:",
        "select_asset": "🎯 Select Filtered Asset:",
        "operating_role": "👤 Operating Role:",
        "gen_blueprint": "⚡ Generate High-ROI Master Blueprint",
        "monetization": "💰 Income Strategy & Profit Model",
        "hook": "🎬 High-Retention Viral Hook (Copy & Use)",
        "audio": "🎵 Recommended High-Converting Audio Vibe",
        "caption": "📢 High-ROAS Caption / Commercial Ad Copy",
        "plan": "📝 3-Step Rapid Revenue Execution Plan",
        "roi_label": "Predicted Revenue Multiplier",
        "roi_value": "8.4x Average Boost",
    },
    "Hindi": {
        "title": "⚡ TrendPulse AI: कमर्शियल सिग्नल इंटेलिजेंस",
        "subtitle": (
            "प्रेडिक्टिव ट्रेंड इंटेलिजेंस | ऑटोमेटेड क्रिएटर और मर्चेंट"
            " रेवेन्यू मल्टिफ्लायर"
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
        "est_revenue": "अनुमानित आय का अवसर (Revenue)",
        "saturation": "सैचुरेशन विंडो (मांग)",
        "status": "सिग्नल स्थिति",
        "chart_title": "📈 डायनेमिक वेलोसिटी और डिमांड फ़ोरकास्ट कर्व",
        "matrix_title": "💡 एक्शनएबल इंटेलिजेंस और इनकम ब्लूप्रिंट मैट्रिक्स",
        "locked_title": "🔒 मल्टी-चैनल रेवेन्यू ब्लूप्रिंट लॉक है",
        "locked_info": (
            "हाई-कन्वर्टिंग स्क्रिप्ट, वायरल हुक, मोनेटाइज्ड एड कॉपी और 10x ROI"
            " एग्जीक्यूशन प्लान अनलॉक करें।"
        ),
        "upgrade_btn": "🔥 प्रो में अपग्रेड करें और रेवेन्यू इंजन अनलॉक करें",
        "analyzing_custom": "आय क्षमता का विश्लेषण:",
        "select_asset": "🎯 फ़िल्टर किया गया एसेट चुनें:",
        "operating_role": "👤 आपकी भूमिका (Role):",
        "gen_blueprint": "⚡ हाई-ROI मास्टर ब्लूप्रिंट जनरेट करें",
        "monetization": "💰 इनकम रणनीति और प्रॉफिट मॉडल",
        "hook": "🎬 हाई-रिटेंशन विजुअल हुक (कॉपी और उपयोग करें)",
        "audio": "🎵 अनुशंसित ऑडियो वाइब",
        "caption": "📢 तैयार हाई-ROAS एड कॉपी / कैप्शन",
        "plan": "📝 3-चरणीय त्वरित रेवेन्यू प्लान",
        "roi_label": "अनुमानित आय मल्टीप्लायर",
        "roi_value": "8.4x औसत वृद्धि",
    },
}

# Custom CSS styling
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
        "roi_multiplier": "6.8x - 12.4x Potential",
        "prediction_window": (
            f"Peak Monetization Active on {platform} over {timeframe} window"
        ),
        "profit_model": (
            f"Capitalize on '{keyword_asset}' under {category} using targeted"
            f" {target_role} monetization workflows to generate recurring"
            " sales."
        ),
        "execution_hook": (
            f"Stop scrolling! Here is how '{keyword_asset}' is printing revenue"
            f" on {platform}..."
        ),
        "audio_suggestion": "Trending Low-Fi Beats / High-Energy Phonk Track",
        "ad_copy": (
            f"Unlock instant revenue using top-rated '{keyword_asset}'"
            " strategies today!"
        ),
        "action_blueprint": (
            "1. Launch targeted high-converting reel using keyword hook\n2."
            " Integrate recommended viral audio vibe\n3. Direct audience to"
            " high-ticket CTA funnel"
        ),
    }

  client = Groq(api_key=GROQ_API_KEY)
  prompt = f"""
    Analyze Keyword Asset: '{keyword_asset}' | Category: '{category}' | Role: '{target_role}' | Platform: '{platform}' | Timeframe: '{timeframe}' | Velocity Score: {velocity_score}%
    Language to respond in: {lang}
    Generate an income execution blueprint. Return STRICT JSON:
    {{
      "viral_score": "{velocity_score}%",
      "roi_multiplier": "e.g., 5.5x - 11.2x Revenue Potential",
      "prediction_window": "Specific monetization lifecycle window based on {timeframe}",
      "profit_model": "Actionable monetization strategy focused on increasing income for {target_role}",
      "execution_hook": "High-retention 3-second hook designed for conversions on {platform}",
      "audio_suggestion": "Recommended viral audio vibe",
      "ad_copy": "High-converting ad copy text designed to multiply revenue",
      "action_blueprint": "3-step rapid execution plan"
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
        "roi_multiplier": "7.2x Revenue Potential",
        "prediction_window": f"Active Growth & High Revenue Phase ({timeframe})",
        "profit_model": f"Monetize '{keyword_asset}' immediately using high-converting funnels.",
        "execution_hook": f"Secret monetization strategy for '{keyword_asset}'!",
        "audio_suggestion": "Trending High-Tempo Track",
        "ad_copy": f"Check out '{keyword_asset}' and multiply your income now!",
        "action_blueprint": "1. Post High-Converting Content\n2. Add Direct CTA\n3. Scaled Sales Monetization",
    }


# Session State Initialization
if "is_premium" not in st.session_state:
  st.session_state["is_premium"] = False

# TOP BAR: Title Header & Clean Language Switcher
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

  revenue_tiers = [
      "$18,500/mo",
      "$14,200/mo",
      "$9,800/mo",
      "$7,500/mo",
      "$5,100/mo",
  ]
  table_data = []
  signal_scores = {}
  for idx, item in enumerate(active_signals):
    score = round(98.8 - (idx * 3.2), 1)
    sat_val = 12 + (idx * 8)
    sat_status = f"{sat_val}% (High ROI Window)"
    table_data.append({
        t["filtered_asset"]: item["Keyword"],
        t["est_revenue"]: revenue_tiers[idx % len(revenue_tiers)],
        t["saturation"]: sat_status,
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
      int(25 * multiplier),
      int(50 * multiplier),
      int(85 * multiplier),
      int(100 * multiplier),
      int(94 * multiplier),
      int(82 * multiplier),
      int(70 * multiplier),
  ]

  fig_df = pd.DataFrame(
      {"Day": days, "Demand & Revenue Trajectory": velocity_values}
  )
  fig = px.line(
      fig_df,
      x="Day",
      y="Demand & Revenue Trajectory",
      title=f"7-Day Profit Potential Curve: {chart_keyword[:30]}...",
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

    # Teaser Box without unterminated string syntax errors
    first_keyword = active_signals[0]["Keyword"] if active_signals else "Asset"
    st.markdown(
        '
