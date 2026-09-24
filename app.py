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
            " Signal Engine"
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
        "filtered_asset": "Trending Signal",
        "search_volume": "Search Volume",
        "future_forecast": "Future Trend Forecast",
        "chart_title": "📈 Dynamic Velocity & Demand Forecast Curve",
        "matrix_title": "💡 Actionable Intelligence & Strategy Matrix",
        "locked_title": "🔒 MULTI-CHANNEL BLUEPRINT IS LOCKED",
        "locked_info": (
            "Unlock high-converting scripts, viral hooks, ad copy, and"
            " step-by-step execution plan."
        ),
        "upgrade_btn": "🔥 Upgrade to Pro & Unlock Full Engine",
        "analyzing_custom": "Analyzing Signal Potential for:",
        "select_asset": "🎯 Select Filtered Asset:",
        "operating_role": "👤 Operating Role:",
        "gen_blueprint": "⚡ Generate Master Strategy Blueprint",
        "monetization": "💰 Direct High-ROI Monetization Model",
        "hook": "🎬 Visual Script & High-Retention Hook (Plug & Play)",
        "audio": "🎵 Recommended High-Converting Audio Vibe",
        "caption": "📢 High-ROAS Caption & CTA Framework",
        "plan": "📝 3-Step Rapid Execution Roadmap (Zero to Launch)",
        "score_label": "Predictive Viral Score",
    },
    "Hindi": {
        "title": "⚡ TrendPulse AI: कमर्शियल सिग्नल इंटेलिजेंस",
        "subtitle": (
            "प्रेडिक्टिव ट्रेंड इंटेलिजेंस | ऑटोमेटेड क्रिएटर और मर्चेंट"
            " सिग्नल इंजन"
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
        "filtered_asset": "ट्रेंडिंग सिग्नल",
        "search_volume": "सर्च वॉल्यूम",
        "future_forecast": "फ्यूचर ट्रेंड फोरकास्ट",
        "chart_title": "📈 डायनेमिक वेलोसिटी और डिमांड फ़ोरकास्ट कर्व",
        "matrix_title": "💡 एक्शनएबल इंटेलिजेंस और स्ट्रैटेजी मैट्रिक्स",
        "locked_title": "🔒 मल्टी-चैनल ब्लूप्रिंट लॉक है",
        "locked_info": (
            "हाई-कन्वर्टिंग स्क्रिप्ट, वायरल हुक, एड कॉपी और एग्जीक्यूशन प्लान"
            " अनलॉक करें।"
        ),
        "upgrade_btn": "🔥 प्रो में अपग्रेड करें और पूरा इंजन अनलॉक करें",
        "analyzing_custom": "सिग्नल क्षमता का विश्लेषण:",
        "select_asset": "🎯 फ़िल्टर किया गया एसेट चुनें:",
        "operating_role": "👤 आपकी भूमिका (Role):",
        "gen_blueprint": "⚡ मास्टर स्ट्रैटेजी ब्लूप्रिंट जनरेट करें",
        "monetization": "💰 डायरेक्ट हाई-ROI मोनेटाइजेशन मॉडल",
        "hook": "🎬 विजुअल स्क्रिप्ट और हाई-रिटेंशन हुक (प्लग एंड प्ले)",
        "audio": "🎵 अनुशंसित हाई-कन्वर्टिंग ऑडियो वाइब",
        "caption": "📢 हाई-ROAS कैप्शन और CTA फ्रेमवर्क",
        "plan": "📝 3-चरणीय त्वरित एग्जीक्यूशन रोडमैप",
        "score_label": "अनुमानित वायरल स्कोर",
    },
}

# Custom CSS styling with Table Overflow Fix
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
                if title is not None and title.text:
                    raw_signals.append({
                        "Keyword": f"{title.text} ({platform_source})",
                        "Volume": (
                            traffic.text
                            if (traffic is not None and traffic.text)
                            else "100K+ Queries"
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
                f"Peak Trend Lifecycle Active ({timeframe} window)"
            ),
            "profit_model": (
                f"**Strategy:** Premium UGC Partnership & Affiliate Funnel.\n**How"
                f" to Cash In:** Showcase the premium aesthetic and comfort of"
                f" {keyword_asset} to partner with top D2C brands for affiliate"
                " commissions or direct brand sponsorship deals ($300–$800/reel)."
            ),
            "execution_hook": (
                f"* **0-3s Visual Cue:** Smooth camera focus highlighting the"
                f" high-quality texture and natural movement of {keyword_asset} in"
                ' aesthetic light.\n* **Text Overlay:** "The ultimate lifestyle'
                ' upgrade everyone is switching to ✨"\n* **Spoken Script:** "If you'
                " love breathable, long-lasting, and skin-friendly quality, you"
                " need to check this out. Here is why this upgrade is trending"
                ' right now..."'
            ),
            "audio_suggestion": (
                "Upbeat Chillhop / Aesthetic Ambient Track (Rising on trends)"
            ),
            "ad_copy": (
                f"Upgrading to 100% natural {keyword_asset} 🌿✨\n\nSuper soft,"
                " highly breathable, and gentle on the skin! Not only feels"
                " incredibly comfortable all day, but also looks effortless and"
                " modern.\n\n👇 Want the direct link + exclusive discount"
                ' code?\nComment "YES" below and I\'ll DM you the details'
                " instantly!\n\n#Trending #LifestyleUpgrade #QualityFirst"
                " #ViralReels"
            ),
            "action_blueprint": (
                "1. **HOUR 1 (Content Production):** Shoot a 15-second visual reel"
                " using the hook above, highlighting asset quality, and add the"
                " direct comment CTA.\n2. **HOUR 6 (Traffic Automation):** Set up"
                ' automated DM keyword response (e.g. reply "YES") to instantly'
                " send the affiliate link to commenters.\n3. **DAY 2 (Scale &"
                " Partner):** Share video performance stats with relevant brands"
                " to pitch long-term paid partnerships."
            ),
        }

    client = Groq(api_key=GROQ_API_KEY)

    prompt = f"""
    Analyze Asset: '{keyword_asset}' | Category: '{category}' | Role: '{target_role}' | Platform: '{platform}' | Timeframe: '{timeframe}' | Velocity: {velocity_score}%
    Language: {lang}
    
    Generate a complete, high-converting revenue blueprint focused on positive highlights, high quality, and actionable execution. Strictly avoid negative framing or criticizing alternatives.
    
    Return STRICT JSON format:
    {{
      "viral_score": "{velocity_score}%",
      "prediction_window": "Monetization lifecycle active window e.g. Peak Trend Lifecycle Active ({timeframe})",
      "profit_model": "**Strategy:** High-converting strategy for {target_role}\\n**How to Cash In:** Step-by-step monetization pathway utilizing {keyword_asset}",
      "execution_hook": "* **0-3s Visual Cue:** Detailed visual setup for {platform}\\n* **Text Overlay:** Aesthetic on-screen text\\n* **Spoken Script:** Engaging spoken audio line focusing on benefits and quality",
      "audio_suggestion": "Specific trending audio genre/style recommendation",
      "ad_copy": "Complete high-converting caption with emojis, clear CTA, and relevant hashtags",
      "action_blueprint": "1. **HOUR 1 (Content Production):** Setup instructions\\n2. **HOUR 6 (Traffic Automation):** Funnel setup instructions\\n3. **DAY 2 (Scale & Partner):** Growth and deal pitching strategy"
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
            "profit_model": (
                f"**Strategy:** Brand Partnership & Direct Funnel for"
                f" {target_role}.\n**How to Cash In:** Monetize {keyword_asset}"
                " through direct audience engagement and affiliate offers."
            ),
            "execution_hook": (
                f"* **0-3s Visual Cue:** Aesthetic product focus.\n* **Text"
                ' Overlay:** "The top upgrade of 2026 ✨"\n* **Spoken Script:** "Here'
                ' is why everyone is loving this..."'
            ),
            "audio_suggestion": "Trending High-Tempo Track",
            "ad_copy": (
                f"Check out {keyword_asset} today for the ultimate quality"
                " upgrade! ✨"
            ),
            "action_blueprint": (
                "1. **HOUR 1:** Record high-quality content using visual hook.\n2."
                " **HOUR 6:** Connect automated link delivery in comments.\n3. **DAY"
                " 2:** Pitch results to brand partners."
            ),
        }


# Session State Initialization
if "is_premium" not in st.session_state:
    st.session_state["is_premium"] = False

# TOP BAR: Header & Language Selector
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

# Layout Column Ratio updated to (1.3, 0.7) to give table more width
left_col, right_col = st.columns([1.3, 0.7], gap="large")

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

    future_forecast_options = [
        "🔥 High Growth (Next 7 Days)",
        "🚀 Viral Peak Expected",
        "📈 Steady Upward Surge",
        "⚡ Breakout Candidate",
        "📊 Emerging Trend",
    ]

    table_data = []
    signal_scores = {}

    for idx, item in enumerate(active_signals):
        score = round(98.8 - (idx * 3.2), 1)
        forecast = future_forecast_options[idx % len(future_forecast_options)]

        table_data.append({
            t["filtered_asset"]: item["Keyword"],
            t["search_volume"]: item["Volume"],
            t["future_forecast"]: forecast,
        })
        signal_scores[item["Keyword"]] = score

    df = pd.DataFrame(table_data)
    st.markdown(
        f"**{t['active_signals_for']}** `{selected_category}` |"
        f" `{platform_source}` | `{geo_option}`"
    )

    # Configured Column Widths to fix Text Cutting
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            t["filtered_asset"]: st.column_config.TextColumn(
                t["filtered_asset"], width="large"
            ),
            t["search_volume"]: st.column_config.TextColumn(
                t["search_volume"], width="small"
            ),
            t["future_forecast"]: st.column_config.TextColumn(
                t["future_forecast"], width="medium"
            ),
        },
    )

    # Dynamic Chart (Live Telemetry Curve)
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

    fig_df = pd.DataFrame({"Day": days, "Demand Trajectory": velocity_values})
    fig = px.line(
        fig_df,
        x="Day",
        y="Demand Trajectory",
        title=f"7-Day Trend Velocity Curve: {chart_keyword[:30]}...",
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

        first_keyword = active_signals[0]["Keyword"] if active_signals else "Asset"

        st.warning(f"💡 Pro Teaser Preview for: {first_keyword}")
        st.write("🔒 **Predictive Growth Rate:** 85% - 98% Viral Probability")
        st.write("🔒 **Trend Blueprint:** [Locked - Pro Only]")
        st.write(
            '🔒 **Viral Script Hook:** "The ultimate lifestyle upgrade everyone is'
            ' switching to..." [Locked]'
        )

        st.link_button(
            t["upgrade_btn"],
            STRIPE_CHECKOUT_URL,
            type="primary",
            use_container_width=True,
        )
    else:
        if custom_search.strip():
            target_keyword = custom_search.strip()
            target_score = 95.0
            st.info(f"{t['analyzing_custom']} **{target_keyword}**")
        else:
            keyword_list = [item["Keyword"] for item in active_signals]
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

        if st.button(t["gen_blueprint"], type="primary", use_container_width=True):
            with st.spinner("Processing fully synchronized trend matrices..."):
                result = generate_master_intelligence(
                    target_keyword,
                    selected_category,
                    user_role,
                    platform_source,
                    timeframe,
                    target_score,
                    selected_lang,
                )

                st.success(
                    f"🎯 Signal Strategy Blueprint Generated: **{target_keyword}**"
                )

                st.markdown("#### 📊 Live Strategy Telemetry")
                col_m1, col_m2 = st.columns(2)
                with col_m1:
                    st.metric(
                        label=t["score_label"], value=result.get("viral_score")
                    )
                with col_m2:
                    st.info(f"**Monetization Window:**\n{result.get('prediction_window')}")

                st.markdown("---")

                with st.expander(t["monetization"], expanded=True):
                    st.markdown(result.get("profit_model"))

                with st.expander(t["hook"], expanded=True):
                    st.markdown(result.get("execution_hook"))

                with st.expander(t["audio"], expanded=True):
                    st.write(f"🔊 **Recommendation:** {result.get('audio_suggestion')}")

                with st.expander(t["caption"], expanded=True):
                    st.code(f"{result.get('ad_copy')}", language="text")

                with st.expander(t["plan"], expanded=True):
                    st.markdown(result.get("action_blueprint"))
