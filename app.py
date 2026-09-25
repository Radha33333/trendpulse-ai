import io
import json
import urllib.parse
import xml.etree.ElementTree as ET
from groq import Groq
import pandas as pd
import plotly.express as px
import requests
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer
import streamlit as st

# ==========================================
# 1. PAGE CONFIG & GLOBALS
# ==========================================
st.set_page_config(
    page_title="TrendPulse AI - Commercial Signal Intelligence",
    page_icon="⚡",
    layout="wide",
)

GROQ_API_KEY = st.secrets.get("GROQ_API_KEY", "")
STRIPE_CHECKOUT_URL = "https://buy.stripe.com/test_demo"

# ==========================================
# 2. UPDATED CATEGORY ARCHITECTURE & MAPPINGS
# ==========================================
UPDATED_NICHE_CATEGORIES = {
    "🛒 E-Commerce & Viral Shopping": [
        "Predicted Bestsellers",
        "TikTok Shop Products",
        "Upcoming High-Demand Drops",
        "Amazon Hot Movers",
    ],
    "🏛️ Politics, News & Civic Events": [
        "Elections & Rallies",
        "Legislative Assembly & Sabha Debates",
        "Protests & Policy Changes",
        "Politician Speeches",
    ],
    "🛕 Faith, Festivals & Sacred Travel": [
        "Famous Temples",
        "Hidden & Ancient Temples",
        "Religious Festivals",
        "Pilgrimage Circuits",
    ],
    "✈️ Travel, Hotels & Food": [
        "Trending Destinations",
        "Hidden Tourist Places",
        "Restaurants & Stays",
        "Veg & Non-Veg Gourmet",
    ],
    "🌟 Celebrities & Sports Stars": [
        "Cricket & Sports Idols",
        "Movie & OTT Stars",
        "Viral Influencers",
        "Tournament Buzz",
    ],
    "🏢 Real Estate & High-Ticket Props": [
        "Rental Yield Hotspots",
        "PropTech & Smart Homes",
        "Luxury Estates",
        "Commercial Spaces",
    ],
    "💄 Beauty, Skincare & Lifestyle": [
        "UGC Skincare Hacks",
        "Clean Beauty Products",
        "Anti-Aging Devices",
        "Sustainable Fashion",
    ],
    "💻 Digital Products & AI Tools": [
        "Generative AI Software",
        "SaaS & Workflows",
        "Ebooks & Courses",
        "Templates & Prompts",
    ],
}

CATEGORY_SIGNALS_FALLBACK = {
    "🛒 E-Commerce & Viral Shopping": [
        "Next-Gen Ergonomic Desk Accessories",
        "Smart Pet Grooming Hardware",
        "Self-Cleaning Water Bottles",
        "Aesthetic MagSafe Powerbanks",
    ],
    "🏛️ Politics, News & Civic Events": [
        "Assembly Election Rallies & Turnout",
        "Parliament Digital Economy Policy Debates",
        "State Infrastructure Bill & Public Protests",
        "Civic Reform & Election Key Speeches",
    ],
    "🛕 Faith, Festivals & Sacred Travel": [
        "Unexplored Ancient Temples Circuit Travel",
        "Upcoming Festival Handicrafts & Festive Decor",
        "Pilgrimage Eco-Resorts & VIP Pass Trends",
        "Historic Temple Heritage Restoration",
    ],
    "✈️ Travel, Hotels & Food": [
        "Hidden Hill Station Stays & Eco-Resorts",
        "Regional Non-Veg Fusion Food Spots",
        "Fine Dining Cloud Kitchen Collaborations",
        "Offbeat Coastal Escapes & Stays",
    ],
    "🌟 Celebrities & Sports Stars": [
        "World Cup Squad Announcements & Fan Buzz",
        "OTT Blockbuster Movie Trailer Drops",
        "Athlete Fitness Routines & Brand Endorsements",
        "Viral Pop Culture Influencer Moments",
    ],
    "🏢 Real Estate & High-Ticket Props": [
        "High Yield Tier-2 City Commercial Hubs",
        "AI-Integrated PropTech Smart Homes",
        "Luxury Gated Communities & Villas",
        "Co-Living & Flexible Work Spaces",
    ],
    "💄 Beauty, Skincare & Lifestyle": [
        "Micro-Needling & Anti-Aging At-Home Devices",
        "Korean Glass-Skin Serum UGC Campaigns",
        "Sustainable Organic Linen Capsule Wardrobe",
        "Clean Eco-Friendly Cosmetics",
    ],
    "💻 Digital Products & AI Tools": [
        "Automated AI Workflow & Prompt Libraries",
        "Micro-SaaS Invoicing & Booking Plugins",
        "Digital Notion Planners & Finance Dashboards",
        "Generative Video Editing Extensions",
    ],
}

# Dynamic search query keywords mapped to Google Trends RSS search parameters
SEARCH_QUERY_MAP = {
    "🛒 E-Commerce & Viral Shopping": [
        "bestselling products",
        "trending ecommerce items",
        "viral tiktok shop",
    ],
    "🏛️ Politics, News & Civic Events": [
        "election rally updates",
        "political protests news",
        "assembly debate",
    ],
    "🛕 Faith, Festivals & Sacred Travel": [
        "famous temple festival",
        "hidden temples to visit",
        "religious pilgrimage trend",
    ],
    "✈️ Travel, Hotels & Food": [
        "hidden tourist places",
        "best luxury hotels restaurants",
        "viral food places",
    ],
    "🌟 Celebrities & Sports Stars": [
        "sports person trending news",
        "celebrity viral moment",
        "cricket player update",
    ],
    "🏢 Real Estate & High-Ticket Props": [
        "real estate investment trends",
        "proptech smart homes",
        "housing market updates",
    ],
    "💄 Beauty, Skincare & Lifestyle": [
        "trending skincare products",
        "viral beauty hacks",
        "cosmetic product reviews",
    ],
    "💻 Digital Products & AI Tools": [
        "best generative ai tools",
        "micro saas software",
        "digital templates online",
    ],
}

# ==========================================
# 3. TRANSLATIONS / LOCALIZATION
# ==========================================
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
        "sub_category": "🔍 Sub-Niche Focus (Optional):",
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
        "export_pdf_btn": "📄 Download Blueprint PDF",
        "share_wa_btn": "💬 Share to WhatsApp",
        "competitor_insight": "🕵️ Live Competitor Ad Intelligence",
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
        "sub_category": "🔍 सब-नीश फ़ोकस (वैकल्पिक):",
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
        "export_pdf_btn": "📄 ब्लूप्रिंट PDF डाउनलोड करें",
        "share_wa_btn": "💬 व्हाट्सएप पर शेयर करें",
        "competitor_insight": "🕵️ लाइव कॉम्पिटिटर एड इंटेलिजेंस",
    },
}

# ==========================================
# 4. HELPER FUNCTIONS & PDF ENGINE
# ==========================================
def safe_xml_text(text):
    return (
        str(text)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )

def create_pdf_blueprint(
    asset_name, category, role, viral_score, window, result
):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36,
    )
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "TitleStyle",
        parent=styles["Heading1"],
        fontSize=20,
        textColor="#ff4b4b",
        spaceAfter=12,
    )
    heading_style = ParagraphStyle(
        "HeadingStyle",
        parent=styles["Heading2"],
        fontSize=14,
        textColor="#1a1a1a",
        spaceBefore=10,
        spaceAfter=6,
    )
    body_style = ParagraphStyle(
        "BodyStyle",
        parent=styles["Normal"],
        fontSize=10,
        leading=14,
        textColor="#333333",
        spaceAfter=8,
    )

    story = []
    story.append(
        Paragraph("TrendPulse AI - Master Strategy Blueprint", title_style)
    )
    story.append(
        Paragraph(
            f"<b>Asset:</b> {safe_xml_text(asset_name)} | <b>Category:</b>"
            f" {safe_xml_text(category)} | <b>Role:</b> {safe_xml_text(role)}",
            body_style,
        )
    )
    story.append(
        Paragraph(
            f"<b>Predictive Viral Score:</b> {safe_xml_text(viral_score)} |"
            f" <b>Monetization Window:</b> {safe_xml_text(window)}",
            body_style,
        )
    )
    story.append(Spacer(1, 10))

    sections = [
        ("Monetization Model", result.get("profit_model", "")),
        ("Execution Hook & Visual Script", result.get("execution_hook", "")),
        ("Recommended Audio Vibe", result.get("audio_suggestion", "")),
        ("High-ROAS Caption & CTA", result.get("ad_copy", "")),
        ("Action Roadmap", result.get("action_blueprint", "")),
        ("Competitor Ad Intelligence", result.get("competitor_intelligence", "")),
    ]

    for title, text in sections:
        story.append(Paragraph(title, heading_style))
        story.append(Paragraph(safe_xml_text(text), body_style))
        story.append(Spacer(1, 6))

    doc.build(story)
    buffer.seek(0)
    return buffer

# ==========================================
# 5. DATA FETCHING & RSS RADAR PIPELINE
# ==========================================
@st.cache_data(ttl=300)
def fetch_filtered_radar_signals(region, platform_source, category, sub_niche, timeframe):
    url = f"https://trends.google.com/trending/rss?geo={region}"
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

    default_keywords = CATEGORY_SIGNALS_FALLBACK.get(
        category, ["Trending Breakout Asset"]
    )
    
    # Enrich keyword if sub_niche filter is active
    if sub_niche and sub_niche != "All Sub-Niches":
        combined = [
            {"Keyword": f"[{sub_niche}] {kw} [{platform_source}]", "Volume": f"180K+ ({timeframe})"}
            for kw in default_keywords
        ]
    else:
        combined = [
            {"Keyword": f"{kw} [{platform_source}]", "Volume": f"150K+ ({timeframe})"}
            for kw in default_keywords
        ]

    for item in raw_signals:
        combined.append(
            {"Keyword": item["Keyword"], "Volume": item["Volume"]}
        )

    return combined[:5]

# ==========================================
# 6. GROQ LLM BLUEPRINT GENERATOR
# ==========================================
def generate_master_intelligence(
    keyword_asset,
    category,
    sub_niche,
    target_role,
    platform,
    timeframe,
    velocity_score,
    lang,
):
    sub_context = f" | Sub-Niche: '{sub_niche}'" if sub_niche else ""
    
    default_response = {
        "viral_score": f"{velocity_score}%",
        "prediction_window": (
            f"Peak Trend Lifecycle Active ({timeframe} window)"
        ),
        "profit_model": (
            f"• **Strategy:** Direct-to-Consumer Funnel & Automated Growth Model tailored for {target_role}.\n"
            f"• **Execution Model:** Monetize target demand for {keyword_asset} using high-converting landing pages and direct audience triggers."
        ),
        "execution_hook": (
            f"• **0-3s Visual Cue:** High-contrast opening visual highlighting the core issue or opportunity in {category}.\n"
            f"• **Text Overlay:** \"The #1 mistake people are making with {keyword_asset} in 2026 ⚡\"\n"
            f"• **Spoken Script:** \"If you want to capitalize on this trend right now, here is the exact framework...\""
        ),
        "audio_suggestion": "Upbeat Phonk / Fast-Paced Rhythmic Ambient",
        "ad_copy": (
            f"Unlocking maximum impact with {keyword_asset} 🚀📈\n\n"
            "Tested across top channels with unmatched engagement. Drop 'SCALE' below for the exact strategy link directly in your inbox!\n\n"
            "#GrowthStrategy #MarketIntelligence #TrendPulse2026"
        ),
        "action_blueprint": (
            "1. HOUR 1: Create 9:16 high-retention social media creative optimized for platform algorithm.\n"
            "2. HOUR 6: Launch automated keyword DM and comment auto-responder sequence.\n"
            "3. DAY 2: Review early retention metrics and scale ad budgets on highest converting variants."
        ),
        "competitor_intelligence": (
            f"• **Top Competitor Hook Style:** *'Stop ignoring this major update regarding {keyword_asset}...'*\n"
            "• **Optimal Video Duration:** 12 - 18 seconds\n"
            "• **Estimated Engagement Benchmark:** High (4.9% CTR / Rapid comment growth)"
        ),
    }

    if not GROQ_API_KEY:
        return default_response

    try:
        client = Groq(api_key=GROQ_API_KEY)
        prompt = f"""
        You are an elite commercial growth strategist and enterprise trend intelligence consultant.
        Analyze Asset: '{keyword_asset}' | Category: '{category}'{sub_context} | Role: '{target_role}' | Platform: '{platform}' | Timeframe: '{timeframe}' | Velocity: {velocity_score}%
        Language: {lang}
        
        Provide hyper-specific, highly tactical, actionable intelligence tailored precisely to the asset and user role ({target_role}). Avoid generic filler. Create professional-grade strategies ready for immediate commercial deployment.

        Return STRICT JSON format:
        {{
          "viral_score": "{velocity_score}%",
          "prediction_window": "Monetization lifecycle active window with specific timing details",
          "profit_model": "Detailed, specific monetization strategy and conversion steps",
          "execution_hook": "Specific 0-3s visual cue, exact text overlay, and high-retention script",
          "audio_suggestion": "Precise trending audio genre or vibe descriptor",
          "ad_copy": "High-ROAS caption with professional CTA and targeted hashtags",
          "action_blueprint": "Clear 3-step rapid execution roadmap with time markers",
          "competitor_intelligence": "Detailed competitor benchmark data including hook style, video duration, and expected CTR"
        }}
        """

        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            response_format={"type": "json_object"},
        )
        return json.loads(completion.choices[0].message.content)
    except Exception:
        return default_response

# ==========================================
# 7. UI LAYOUT & RENDER
# ==========================================
if "is_premium" not in st.session_state:
    st.session_state["is_premium"] = False

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

st.markdown(f"### {t['config_title']}")

# Filter Form Configuration
with st.form(key="filter_form"):
    f_col1, f_col2, f_col3, f_col4, f_col5 = st.columns(5)

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
            options=list(UPDATED_NICHE_CATEGORIES.keys()),
            index=0
        )

    with f_col4:
        sub_niche_options = UPDATED_NICHE_CATEGORIES.get(selected_category, [])
        selected_sub_niche = st.selectbox(
            t["sub_category"],
            options=["All Sub-Niches"] + sub_niche_options,
            index=0
        )

    with f_col5:
        timeframe = st.selectbox(
            t["velocity"],
            [
                "Realtime Spike (24h)",
                "Short-Term Trend (7 Days)",
                "Viral Surge (3-7 Days)",
                "Macro Trend (30 Days)",
            ],
        )

    apply_filters = st.form_submit_button(t["apply_btn"], use_container_width=True)

st.markdown("---")

left_col, right_col = st.columns([1.3, 0.7], gap="large")

with left_col:
    st.subheader(t["telemetry_title"])
    custom_search = st.text_input(
        t["custom_search"],
        placeholder="e.g. Ergonomic Desk, AI Workflow Tools, Pilgrimage Circuits",
    )

    active_signals = fetch_filtered_radar_signals(
        geo_map[geo_option], 
        platform_source, 
        selected_category, 
        selected_sub_niche, 
        timeframe
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
        forecast = future_forecast_options[
            idx % len(future_forecast_options)
        ]

        table_data.append({
            t["filtered_asset"]: item["Keyword"],
            t["search_volume"]: item["Volume"],
            t["future_forecast"]: forecast,
        })
        signal_scores[item["Keyword"]] = score

    df = pd.DataFrame(table_data)
    sub_title_ctx = f" | Sub: `{selected_sub_niche}`" if selected_sub_niche != "All Sub-Niches" else ""
    st.markdown(
        f"**{t['active_signals_for']}** `{selected_category}`{sub_title_ctx} |"
        f" `{platform_source}` | `{geo_option}`"
    )

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

    st.markdown(f"#### {t['chart_title']}")

    if custom_search.strip():
        chart_keyword = custom_search.strip()
        base_score = 95.0
    else:
        chart_keyword = (
            active_signals[0]["Keyword"] if active_signals else "Asset"
        )
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
        {"Day": days, "Demand Trajectory": velocity_values}
    )
    fig = px.line(
        fig_df,
        x="Day",
        y="Demand Trajectory",
        title=f"7-Day Trend Velocity Curve: {chart_keyword[:35]}...",
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

        first_keyword = (
            active_signals[0]["Keyword"] if active_signals else "Asset"
        )

        st.warning(f"💡 Pro Teaser Preview for: {first_keyword}")
        st.write("🔒 **Predictive Growth Rate:** 85% - 98% Viral Probability")
        st.write("🔒 **Trend Blueprint:** [Locked - Pro Only]")
        st.write(
            '🔒 **Viral Script Hook:** "The ultimate lifestyle upgrade everyone'
            ' is switching to..." [Locked]'
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

        gen_btn_clicked = st.button(t["gen_blueprint"], type="primary", use_container_width=True)

        if gen_btn_clicked:
            with st.spinner("Processing fully synchronized trend matrices..."):
                st.session_state["blueprint_result"] = generate_master_intelligence(
                    target_keyword,
                    selected_category,
                    selected_sub_niche,
                    user_role,
                    platform_source,
                    timeframe,
                    target_score,
                    selected_lang,
                )
                st.session_state["target_keyword"] = target_keyword
                st.session_state["selected_category"] = selected_category
                st.session_state["user_role"] = user_role

        if "blueprint_result" in st.session_state and st.session_state["blueprint_result"]:
            result = st.session_state["blueprint_result"]
            active_target = st.session_state.get("target_keyword", target_keyword)
            active_cat = st.session_state.get("selected_category", selected_category)
            active_role = st.session_state.get("user_role", user_role)

            st.success(
                f"🎯 Signal Strategy Blueprint Generated: **{active_target}**"
            )

            st.markdown("#### 📊 Live Strategy Telemetry")
            col_m1, col_m2 = st.columns(2)
            with col_m1:
                st.metric(
                    label=t["score_label"], value=result.get("viral_score")
                )
            with col_m2:
                st.info(
                    f"**Monetization Window:**\n{result.get('prediction_window')}"
                )

            st.markdown("---")

            with st.expander(t["monetization"], expanded=True):
                st.markdown(result.get("profit_model"))

            with st.expander(t["hook"], expanded=True):
                st.markdown(result.get("execution_hook"))

            with st.expander(t["audio"], expanded=True):
                st.write(
                    f"🔊 **Recommendation:**"
                    f" {result.get('audio_suggestion')}"
                )

            with st.expander(t["caption"], expanded=True):
                st.code(f"{result.get('ad_copy')}", language="text")

            with st.expander(t["plan"], expanded=True):
                st.markdown(result.get("action_blueprint"))

            with st.expander(t["competitor_insight"], expanded=False):
                st.markdown(result.get("competitor_intelligence"))

            pdf_buffer = create_pdf_blueprint(
                active_target,
                active_cat,
                active_role,
                result.get("viral_score"),
                result.get("prediction_window"),
                result,
            )

            wa_text = (
                f"⚡ *TrendPulse AI Blueprint: {active_target}*\n\n🔥 *Viral"
                f" Score:* {result.get('viral_score')}\n🎯 *Hook:*"
                f" {result.get('execution_hook')[:120]}...\n\n📲 *Action Plan:*"
                f" {result.get('action_blueprint')[:150]}..."
            )
            encoded_wa_text = urllib.parse.quote(wa_text)
            wa_share_url = f"https://wa.me/?text={encoded_wa_text}"

            export_col1, export_col2 = st.columns(2)

            with export_col1:
                st.download_button(
                    label=t["export_pdf_btn"],
                    data=pdf_buffer,
                    file_name=(
                        f"blueprint_{active_target.replace(' ', '_')}.pdf"
                    ),
                    mime="application/pdf",
                    use_container_width=True,
                )

            with export_col2:
                st.link_button(
                    t["share_wa_btn"], wa_share_url, use_container_width=True
                )
